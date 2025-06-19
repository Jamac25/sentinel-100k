"""
Authentication API routes for user registration, login, and token management.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from app.schemas import UserCreate, UserLogin, Token, UserResponse, PasswordChange, PasswordReset
from app.services.auth_service import auth_service, security
from app.db.init_db import get_db
from app.models import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


def get_current_user(credentials=Depends(security), db=Depends(get_db)):
    """
    Get current authenticated user from JWT token.
    This dependency can be used in protected routes.
    """
    token = credentials.credentials
    return auth_service.get_current_user(db, token)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data, db=Depends(get_db)):
    """
    Register a new user account.
    
    Creates a new user with the provided email, name, and password.
    Automatically sets up the user's financial profile and agent state.
    """
    try:
        # Register user
        user = auth_service.register_user(db, user_data)
        
        # Initialize user's financial profile (this would typically be done in a service)
        # For now, we'll create the basic user response
        
        logger.info(f"User registered successfully: {user.email}")
        
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except Exception as e:
        logger.error(f"Registration failed: {e}")
        raise


@router.post("/login", response_model=None)
async def login(login_data, db=Depends(get_db)):
    """
    Authenticate user and return access token.
    
    Validates email and password, then returns a JWT token for subsequent requests.
    """
    try:
        login_result = auth_service.login_user(db, login_data)
        
        return Token(
            access_token=login_result["access_token"],
            token_type=login_result["token_type"],
            expires_in=login_result["expires_in"],
            user=login_result["user"]
        )
        
    except Exception as e:
        logger.error(f"Login failed for {login_data.email}: {e}")
        raise


@router.post("/refresh", response_model=None)
async def refresh_token(
    current_user = Depends(get_current_user),
    db = Depends(get_db)
) -> None:
    """
    Refresh the access token for the current user.
    
    Generates a new JWT token with extended expiration time.
    """
    try:
        refresh_result = auth_service.refresh_token(db, current_user)
        
        logger.info(f"Token refreshed for user: {current_user.email}")
        return refresh_result
        
    except Exception as e:
        logger.error(f"Token refresh failed for user {current_user.email}: {e}")
        raise


@router.get("/me", response_model=None)
async def get_current_user_info(current_user=Depends(get_current_user)):
    """
    Get current user information.
    
    Returns the profile information of the currently authenticated user.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )


@router.post("/change-password", response_model=None)
async def change_password(password_data, current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Change the current user's password.
    
    Requires the current password for verification and a new password.
    """
    try:
        success = auth_service.change_password(
            db, current_user, password_data.old_password, password_data.new_password
        )
        
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to change password"
            )
            
    except Exception as e:
        logger.error(f"Password change failed for user {current_user.email}: {e}")
        raise


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
async def request_password_reset(
    email: str,
    db = Depends(get_db)
) -> None:
    """
    Request a password reset token.
    
    Generates a password reset token and would typically send it via email.
    For now, returns the token directly (for development).
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if user exists or not for security
            return {"message": "If the email exists, a reset token has been sent"}
        
        # Generate reset token
        reset_token = auth_service.generate_password_reset_token(user)
        
        # In production, this would be sent via email
        # For development, we return it directly
        logger.info(f"Password reset requested for user: {email}")
        
        return {
            "message": "Password reset token generated",
            "reset_token": reset_token  # Remove this in production
        }
        
    except Exception as e:
        logger.error(f"Password reset request failed for {email}: {e}")
        return {"message": "If the email exists, a reset token has been sent"}


@router.post("/reset-password", response_model=None)
async def reset_password(password_data, db=Depends(get_db)):
    """
    Reset password using a reset token.
    
    Uses the token from the password reset request to set a new password.
    """
    try:
        success = auth_service.reset_password(db, password_data.token, password_data.new_password)
        
        if success:
            return {"message": "Password reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reset password"
            )
            
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user = Depends(get_current_user)
) -> None:
    """
    Logout the current user.
    
    In a stateless JWT system, logout is handled client-side by discarding the token.
    This endpoint is provided for consistency and potential future token blacklisting.
    """
    logger.info(f"User logged out: {current_user.email}")
    
    return {"message": "Logged out successfully"}


@router.delete("/deactivate", status_code=status.HTTP_200_OK)
async def deactivate_account(current_user=Depends(get_current_user), db=Depends(get_db)):
    """
    Deactivate the current user's account.
    
    Marks the user account as inactive, preventing further logins.
    """
    try:
        success = auth_service.deactivate_user(db, current_user)
        
        if success:
            return {"message": "Account deactivated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to deactivate account"
            )
            
    except Exception as e:
        logger.error(f"Account deactivation failed for user {current_user.email}: {e}")
        raise 