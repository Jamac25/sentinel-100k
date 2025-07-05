#!/usr/bin/env python3
"""
🚀 SENTINEL 100K - ENTERPRISE MAIN APPLICATION (SECURITY FIXED)
Golden Standard Security Implementation - Production Ready
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn

# Import our fixed security systems
from enterprise_security_fixed import get_security_system, SecurityConfig, ThreatLevel
from enterprise_database_fixed import get_database, DatabaseConfig, DatabaseSecurityLevel

# Configure secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security configuration
SECURITY_CONFIG = SecurityConfig(
    jwt_expiry_minutes=15,
    session_timeout_minutes=15,
    max_failed_attempts=3,
    lockout_duration_minutes=30,
    password_min_length=12,
    require_mfa=True,
    max_session_per_user=3
)

# Database configuration
DATABASE_CONFIG = DatabaseConfig(
    database_url=os.getenv('DATABASE_URL', 'postgresql://sentinel_user:${DB_PASSWORD}@localhost:5432/sentinel_100k'),
    security_level=DatabaseSecurityLevel.PRODUCTION,
    require_ssl=True
)

# Initialize security and database systems
security_system = None
database = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global security_system, database
    
    # Startup
    logger.info("🚀 Starting Sentinel 100K Enterprise (Security FIXED)")
    
    # Initialize security system
    security_system = get_security_system()
    
    # Initialize database
    database = get_database()
    
    # Setup demo user with MFA
    try:
        mfa_setup = security_system.register_user_mfa("user_1")
        logger.info(f"✅ Demo user MFA setup complete. Secret: {mfa_setup['secret'][:8]}...")
    except Exception as e:
        logger.warning(f"Demo user MFA setup failed: {e}")
    
    logger.info("✅ All systems initialized securely")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Sentinel 100K Enterprise")

# Create FastAPI app with security
app = FastAPI(
    title="Sentinel 100K Enterprise (Security FIXED)",
    description="Enterprise-grade personal finance system with comprehensive security",
    version="1.0.0-security-fixed",
    lifespan=lifespan,
    docs_url="/api/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/api/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Security middleware
security = HTTPBearer()

# FIXED: Comprehensive security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.sentinel100k.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:8501", "https://127.0.0.1:8501"],  # FIXED: Only allow HTTPS
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=600  # FIXED: Cache preflight requests
)

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """FIXED: Comprehensive security middleware"""
    start_time = datetime.utcnow()
    
    # Extract client information
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # FIXED: Security headers
    response = await call_next(request)
    
    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # Log request
    duration = (datetime.utcnow() - start_time).total_seconds()
    logger.info(f"Request: {request.method} {request.url.path} from {client_ip} - {response.status_code} ({duration:.3f}s)")
    
    return response

# Dependency to get current user
async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """FIXED: Secure user authentication"""
    
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Validate JWT token
    payload = security_system.validate_jwt_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Validate session
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session_validation = security_system.validate_session(session_id, client_ip, user_agent)
    if not session_validation["valid"]:
        raise HTTPException(status_code=401, detail=session_validation["error"])
    
    return {
        "user_id": payload["sub"],
        "session_id": session_id,
        "session_info": session_validation["session_info"]
    }

# FIXED: Secure health check endpoint
@app.get("/health")
async def health_check():
    """Secure health check endpoint"""
    try:
        # Check security system
        security_status = security_system.get_security_status()
        
        # Check database
        database_status = database.get_database_status()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0-security-fixed",
            "security": {
                "threat_level": security_status["threat_level"],
                "active_sessions": security_status["active_sessions"],
                "blocked_ips": security_status["blocked_ips"]
            },
            "database": {
                "status": database_status["status"],
                "ssl_enabled": database_status["ssl_enabled"]
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": "Service unavailable"}
        )

# FIXED: Secure authentication endpoint
@app.post("/auth/login")
async def login(request: Request, login_data: Dict[str, Any]):
    """FIXED: Secure login with MFA"""
    
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Validate input
    if not all(key in login_data for key in ["email", "password"]):
        raise HTTPException(status_code=400, detail="Email and password required")
    
    # Check for MFA token
    mfa_token = login_data.get("mfa_token")
    
    try:
        # Authenticate user
        result = security_system.authenticate_user(
            email=login_data["email"],
            password=login_data["password"],
            source_ip=client_ip,
            user_agent=user_agent,
            mfa_token=mfa_token
        )
        
        if not result["success"]:
            status_code = 429 if "retry_after" in result else 401
            raise HTTPException(status_code=status_code, detail=result["error"])
        
        return {
            "access_token": result["token"],
            "token_type": "bearer",
            "expires_at": result["expires_at"],
            "user_id": result["user_id"],
            "mfa_verified": result["mfa_verified"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

# FIXED: Secure user registration endpoint
@app.post("/auth/register")
async def register(request: Request, user_data: Dict[str, Any]):
    """FIXED: Secure user registration"""
    
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    try:
        # Validate required fields
        required_fields = ["email", "name", "password"]
        if not all(field in user_data for field in required_fields):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Create user in database
        user = database.create_user_secure(user_data)
        
        # Setup MFA for new user
        mfa_setup = security_system.register_user_mfa(user["id"])
        
        return {
            "user_id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "mfa_setup": {
                "secret": mfa_setup["secret"],
                "qr_url": mfa_setup["qr_url"],
                "backup_codes": mfa_setup["backup_codes"]
            },
            "message": "User registered successfully. Please setup MFA before first login."
        }
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# FIXED: Secure user profile endpoint
@app.get("/api/user/profile")
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user profile securely"""
    
    try:
        user = database.get_user_secure(current_user["user_id"])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user": user,
            "session_info": current_user["session_info"]
        }
        
    except Exception as e:
        logger.error(f"Profile lookup error: {e}")
        raise HTTPException(status_code=500, detail="Profile lookup failed")

# FIXED: Secure data endpoint
@app.get("/api/data/secure")
async def get_secure_data(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get secure data with full protection"""
    
    try:
        # Execute secure database query
        query = "SELECT id, name, created_at FROM user_data WHERE user_id = $1"
        parameters = {"user_id": current_user["user_id"]}
        
        data = database.execute_secure_query(query, parameters, read_only=True)
        
        return {
            "data": data,
            "retrieved_at": datetime.utcnow().isoformat(),
            "user_id": current_user["user_id"]
        }
        
    except Exception as e:
        logger.error(f"Secure data query error: {e}")
        raise HTTPException(status_code=500, detail="Data retrieval failed")

# FIXED: Security status endpoint
@app.get("/api/security/status")
async def get_security_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get security system status"""
    
    try:
        security_status = security_system.get_security_status()
        database_status = database.get_database_status()
        
        return {
            "security": security_status,
            "database": database_status,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Security status error: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")

# FIXED: Logout endpoint
@app.post("/auth/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Secure logout"""
    
    try:
        # Invalidate session
        security_system._invalidate_session(current_user["session_id"], "user_logout")
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """FIXED: Secure error handling"""
    
    # Log security-relevant errors
    if exc.status_code in [401, 403, 429]:
        logger.warning(f"Security error {exc.status_code}: {exc.detail} from {request.client.host}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """FIXED: Secure general exception handling"""
    
    logger.error(f"Unhandled exception: {exc} from {request.client.host}")
    
    # FIXED: Don't expose internal error details
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )

if __name__ == "__main__":
    # FIXED: Secure server configuration
    uvicorn.run(
        "main_security_fixed:app",
        host="127.0.0.1",  # FIXED: Only bind to localhost
        port=8000,
        log_level="info",
        access_log=True,
        server_header=False,  # FIXED: Don't expose server info
        date_header=False,    # FIXED: Don't expose date
        reload=False,         # FIXED: Disable reload in production
        ssl_keyfile=os.getenv("SSL_KEYFILE"),
        ssl_certfile=os.getenv("SSL_CERTFILE"),
    ) 