"""
Authentication service for JWT token management and user verification.
Handles login, registration, and token-based authentication.
"""
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate, UserLogin, Token
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token security
security = HTTPBearer()


class AuthService:
    """
    Authentication service handling user registration, login, and JWT token management.
    Implements secure password hashing and token-based authentication.
    """
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Payload data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"Token verification failed: {e}")
            return None
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            logger.info(f"Authentication failed: user not found for email {email}")
            return None
        
        if not user.is_active:
            logger.info(f"Authentication failed: user {email} is inactive")
            return None
        
        if not self.verify_password(password, user.password_hash):
            logger.info(f"Authentication failed: invalid password for user {email}")
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"User {email} authenticated successfully")
        return user
    
    def register_user(self, db: Session, user_data: UserCreate) -> User:
        """
        Register a new user.
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            Created user object
            
        Raises:
            HTTPException: If user already exists or validation fails
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Validate password strength
        if not self._is_password_strong(user_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long and contain uppercase, lowercase, and numbers"
            )
        
        # Create new user
        password_hash = self.get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            password_hash=password_hash,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"New user registered: {user_data.email}")
        return db_user
    
    def login_user(self, db: Session, login_data: UserLogin) -> Dict[str, Any]:
        """
        Login user and return access token.
        
        Args:
            db: Database session
            login_data: Login credentials
            
        Returns:
            Dictionary containing access token and user info
            
        Raises:
            HTTPException: If authentication fails
        """
        user = self.authenticate_user(db, login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "is_active": user.is_active
            }
        }
    
    def get_current_user(self, db: Session, token: str) -> User:
        """
        Get current user from JWT token.
        
        Args:
            db: Database session
            token: JWT token
            
        Returns:
            Current user object
            
        Raises:
            HTTPException: If token is invalid or user not found
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        payload = self.verify_token(token)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        try:
            user_id = int(user_id)
        except ValueError:
            raise credentials_exception
        
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        return user
    
    def refresh_token(self, db: Session, current_user: User) -> Dict[str, Any]:
        """
        Refresh access token for current user.
        
        Args:
            db: Database session
            current_user: Current authenticated user
            
        Returns:
            New access token data
        """
        access_token_expires = timedelta(minutes=self.access_token_expire_minutes)
        access_token = self.create_access_token(
            data={"sub": str(current_user.id), "email": current_user.email},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def change_password(self, db: Session, user: User, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            db: Database session
            user: User object
            old_password: Current password
            new_password: New password
            
        Returns:
            Success status
            
        Raises:
            HTTPException: If old password is incorrect or new password is weak
        """
        # Verify old password
        if not self.verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        if not self._is_password_strong(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 8 characters long and contain uppercase, lowercase, and numbers"
            )
        
        # Update password
        user.password_hash = self.get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Password changed for user {user.email}")
        return True
    
    def deactivate_user(self, db: Session, user: User) -> bool:
        """
        Deactivate user account.
        
        Args:
            db: Database session
            user: User to deactivate
            
        Returns:
            Success status
        """
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"User account deactivated: {user.email}")
        return True
    
    def _is_password_strong(self, password: str) -> bool:
        """
        Check if password meets strength requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            True if password is strong enough
        """
        if len(password) < 8:
            return False
        
        has_uppercase = any(c.isupper() for c in password)
        has_lowercase = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        return has_uppercase and has_lowercase and has_digit
    
    def generate_password_reset_token(self, user: User) -> str:
        """
        Generate password reset token.
        
        Args:
            user: User requesting password reset
            
        Returns:
            Password reset token
        """
        expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        to_encode = {
            "sub": str(user.id),
            "email": user.email,
            "type": "password_reset",
            "exp": expire
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify password reset token.
        
        Args:
            token: Reset token to verify
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") == "password_reset":
                return payload
        except JWTError:
            pass
        
        return None
    
    def reset_password(self, db: Session, token: str, new_password: str) -> bool:
        """
        Reset user password using reset token.
        
        Args:
            db: Database session
            token: Password reset token
            new_password: New password
            
        Returns:
            Success status
            
        Raises:
            HTTPException: If token is invalid or password is weak
        """
        payload = self.verify_password_reset_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Validate new password
        if not self._is_password_strong(new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long and contain uppercase, lowercase, and numbers"
            )
        
        # Update password
        user.password_hash = self.get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Password reset completed for user {user.email}")
        return True


# Global auth service instance
auth_service = AuthService()

def get_current_user(db: Session, token: str) -> User:
    """Dependency to get the current user from JWT token."""
    payload = auth_service.verify_token(token)
    if not payload or 'sub' not in payload:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user_id = int(payload['sub'])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user 