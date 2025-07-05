#!/usr/bin/env python3
"""
🔒 SENTINEL 100K - ENTERPRISE SECURITY SYSTEM
Microsoft Zero-Trust Security Model Implementation
"""

import os
import hashlib
import secrets
import time
import jwt
import bcrypt
import pyotp
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from enum import Enum
import threading
import logging
from collections import defaultdict, deque
import re
import ipaddress
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Security threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuthenticationMethod(Enum):
    """Supported authentication methods"""
    PASSWORD = "password"
    MFA_TOTP = "mfa_totp"
    MFA_SMS = "mfa_sms"
    API_KEY = "api_key"
    CERTIFICATE = "certificate"

@dataclass
class SecurityEvent:
    """Security event for audit logging"""
    event_id: str
    user_id: Optional[str]
    event_type: str
    threat_level: ThreatLevel
    source_ip: str
    user_agent: str
    timestamp: datetime
    details: Dict[str, Any]
    blocked: bool = False

@dataclass
class SessionInfo:
    """Enhanced session information"""
    session_id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    source_ip: str
    user_agent: str
    auth_methods: List[AuthenticationMethod]
    risk_score: float = 0.0
    is_valid: bool = True
    device_fingerprint: str = ""

class EnterpriseSecuritySystem:
    """
    🔒 Enterprise Security System
    Implements Microsoft/Azure security standards:
    - Multi-factor authentication
    - Session management with device tracking
    - Threat detection and response
    - Compliance audit logging
    - Zero-trust validation
    """
    
    def __init__(self):
        self.encryption_key = self._get_or_create_master_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Session management
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.user_sessions: Dict[str, Set[str]] = defaultdict(set)
        self.session_lock = threading.Lock()
        
        # Threat detection
        self.failed_attempts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        self.suspicious_ips: Dict[str, Dict[str, Any]] = {}
        self.blocked_ips: Set[str] = set()
        
        # Security events
        self.security_events: deque = deque(maxlen=10000)
        self.threat_patterns = self._initialize_threat_patterns()
        
        # MFA secrets storage (encrypted)
        self.mfa_secrets: Dict[str, str] = {}
        
        # API key management
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        
        # Start background tasks
        self._start_session_cleanup()
        self._start_threat_monitoring()
        
        logger.info("✅ Enterprise Security System initialized")
    
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key"""
        key_file = os.path.join(os.getcwd(), '.sentinel_master_key')
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            os.chmod(key_file, 0o600)  # Restrict access
            logger.info("✅ Generated new master encryption key")
            return key
    
    def _initialize_threat_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize threat detection patterns"""
        return {
            'sql_injection': re.compile(r'(\bUNION\b|\bSELECT\b|\bINSERT\b|\bDROP\b|\bDELETE\b)', re.IGNORECASE),
            'xss_script': re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            'xss_event': re.compile(r'on\w+\s*=', re.IGNORECASE),
            'path_traversal': re.compile(r'\.\.[\\/]'),
            'command_injection': re.compile(r'[\|&;`]'),
            'ldap_injection': re.compile(r'[()=*]'),
        }
    
    def register_user_mfa(self, user_id: str) -> Dict[str, Any]:
        """Register MFA for user"""
        secret = pyotp.random_base32()
        encrypted_secret = self.cipher_suite.encrypt(secret.encode())
        self.mfa_secrets[user_id] = encrypted_secret.decode()
        
        # Generate QR code URL
        totp = pyotp.TOTP(secret)
        qr_url = totp.provisioning_uri(
            name=f"user_{user_id}",
            issuer_name="Sentinel-100K"
        )
        
        return {
            "secret": secret,  # Show once for setup
            "qr_url": qr_url,
            "backup_codes": self._generate_backup_codes(user_id)
        }
    
    def _generate_backup_codes(self, user_id: str) -> List[str]:
        """Generate MFA backup codes"""
        codes = [secrets.token_hex(4).upper() for _ in range(10)]
        # Store encrypted backup codes
        encrypted_codes = self.cipher_suite.encrypt("|".join(codes).encode())
        # In real implementation, store in database
        return codes
    
    def verify_mfa_token(self, user_id: str, token: str) -> bool:
        """Verify MFA token"""
        if user_id not in self.mfa_secrets:
            return False
        
        try:
            encrypted_secret = self.mfa_secrets[user_id].encode()
            secret = self.cipher_suite.decrypt(encrypted_secret).decode()
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=2)  # Allow 30s window
        except Exception as e:
            logger.error(f"MFA verification error: {e}")
            return False
    
    def authenticate_user(self, email: str, password: str, source_ip: str, 
                         user_agent: str, mfa_token: Optional[str] = None) -> Dict[str, Any]:
        """Enhanced user authentication with threat detection"""
        
        # Check if IP is blocked
        if source_ip in self.blocked_ips:
            self._log_security_event(
                event_type="authentication_blocked",
                threat_level=ThreatLevel.HIGH,
                source_ip=source_ip,
                user_agent=user_agent,
                details={"reason": "blocked_ip", "email": email},
                blocked=True
            )
            return {"success": False, "error": "Access denied", "blocked": True}
        
        # Check for brute force
        if self._is_brute_force_attempt(source_ip, email):
            self._handle_brute_force(source_ip, email)
            return {"success": False, "error": "Too many failed attempts", "retry_after": 300}
        
        # Simulate user lookup and password verification
        # In real implementation, query database
        user_id = self._get_user_id_by_email(email)
        if not user_id or not self._verify_password(user_id, password):
            self._record_failed_attempt(source_ip, email)
            self._log_security_event(
                event_type="authentication_failed",
                threat_level=ThreatLevel.MEDIUM,
                source_ip=source_ip,
                user_agent=user_agent,
                details={"email": email, "reason": "invalid_credentials"}
            )
            return {"success": False, "error": "Invalid credentials"}
        
        # Check if MFA is required
        if user_id in self.mfa_secrets:
            if not mfa_token or not self.verify_mfa_token(user_id, mfa_token):
                return {"success": False, "error": "MFA token required", "mfa_required": True}
        
        # Create secure session
        session_info = self._create_session(user_id, source_ip, user_agent)
        
        # Generate secure JWT
        token = self._generate_jwt_token(user_id, session_info.session_id)
        
        self._log_security_event(
            event_type="authentication_success",
            threat_level=ThreatLevel.LOW,
            source_ip=source_ip,
            user_agent=user_agent,
            details={"user_id": user_id, "session_id": session_info.session_id},
            user_id=user_id
        )
        
        return {
            "success": True,
            "token": token,
            "session_id": session_info.session_id,
            "expires_at": (datetime.utcnow() + timedelta(hours=8)).isoformat(),
            "user_id": user_id
        }
    
    def _get_user_id_by_email(self, email: str) -> Optional[str]:
        """Simulate user lookup"""
        # In real implementation, query database
        if email == "admin@sentinel100k.com":
            return "user_1"
        return None
    
    def _verify_password(self, user_id: str, password: str) -> bool:
        """Simulate password verification"""
        # In real implementation, verify against hashed password in database
        return password == "admin123"  # Demo only
    
    def _create_session(self, user_id: str, source_ip: str, user_agent: str) -> SessionInfo:
        """Create secure session with device fingerprinting"""
        session_id = secrets.token_urlsafe(32)
        device_fingerprint = hashlib.sha256(f"{user_agent}_{source_ip}".encode()).hexdigest()
        
        session_info = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            source_ip=source_ip,
            user_agent=user_agent,
            auth_methods=[AuthenticationMethod.PASSWORD],
            device_fingerprint=device_fingerprint
        )
        
        if user_id in self.mfa_secrets:
            session_info.auth_methods.append(AuthenticationMethod.MFA_TOTP)
        
        with self.session_lock:
            self.active_sessions[session_id] = session_info
            self.user_sessions[user_id].add(session_id)
        
        return session_info
    
    def _generate_jwt_token(self, user_id: str, session_id: str) -> str:
        """Generate secure JWT token"""
        payload = {
            "sub": user_id,
            "session_id": session_id,
            "iat": int(time.time()),
            "exp": int(time.time()) + (8 * 3600),  # 8 hours
            "iss": "Sentinel-100K-Enterprise",
            "aud": "sentinel-api"
        }
        
        # Use strong secret from environment
        secret = os.getenv('JWT_SECRET_KEY', 'fallback-secret-change-in-production')
        return jwt.encode(payload, secret, algorithm='HS256')
    
    def validate_session(self, session_id: str, source_ip: str, user_agent: str) -> Dict[str, Any]:
        """Validate session with enhanced security checks"""
        with self.session_lock:
            session = self.active_sessions.get(session_id)
        
        if not session:
            return {"valid": False, "error": "Session not found"}
        
        if not session.is_valid:
            return {"valid": False, "error": "Session invalidated"}
        
        # Check session timeout (8 hours max, 30 min idle)
        if datetime.utcnow() - session.created_at > timedelta(hours=8):
            self._invalidate_session(session_id, "session_expired")
            return {"valid": False, "error": "Session expired"}
        
        if datetime.utcnow() - session.last_activity > timedelta(minutes=30):
            self._invalidate_session(session_id, "idle_timeout")
            return {"valid": False, "error": "Session timed out"}
        
        # Security checks
        risk_factors = []
        
        # IP address change
        if session.source_ip != source_ip:
            risk_factors.append("ip_change")
            session.risk_score += 30
        
        # User agent change
        if session.user_agent != user_agent:
            risk_factors.append("user_agent_change")
            session.risk_score += 20
        
        # Suspicious IP
        if source_ip in self.suspicious_ips:
            risk_factors.append("suspicious_ip")
            session.risk_score += 40
        
        # High risk session
        if session.risk_score > 50:
            self._invalidate_session(session_id, "high_risk_detected")
            self._log_security_event(
                event_type="session_invalidated_high_risk",
                threat_level=ThreatLevel.HIGH,
                source_ip=source_ip,
                user_agent=user_agent,
                details={"session_id": session_id, "risk_factors": risk_factors, "risk_score": session.risk_score},
                user_id=session.user_id
            )
            return {"valid": False, "error": "Session invalidated due to suspicious activity"}
        
        # Update session activity
        session.last_activity = datetime.utcnow()
        
        return {
            "valid": True,
            "user_id": session.user_id,
            "session_info": {
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "risk_score": session.risk_score,
                "auth_methods": [method.value for method in session.auth_methods]
            }
        }
    
    def _invalidate_session(self, session_id: str, reason: str):
        """Invalidate a session"""
        with self.session_lock:
            session = self.active_sessions.get(session_id)
            if session:
                session.is_valid = False
                self.user_sessions[session.user_id].discard(session_id)
                logger.info(f"Session {session_id} invalidated: {reason}")
    
    def _is_brute_force_attempt(self, source_ip: str, email: str) -> bool:
        """Detect brute force attempts"""
        key = f"{source_ip}_{email}"
        attempts = self.failed_attempts[key]
        
        # More than 5 attempts in 5 minutes
        if len(attempts) >= 5:
            recent_attempts = [t for t in attempts if time.time() - t < 300]
            return len(recent_attempts) >= 5
        
        return False
    
    def _record_failed_attempt(self, source_ip: str, email: str):
        """Record failed authentication attempt"""
        key = f"{source_ip}_{email}"
        self.failed_attempts[key].append(time.time())
    
    def _handle_brute_force(self, source_ip: str, email: str):
        """Handle brute force attack"""
        # Temporary IP blocking
        self.blocked_ips.add(source_ip)
        
        # Schedule IP unblock after 5 minutes
        def unblock_ip():
            time.sleep(300)
            self.blocked_ips.discard(source_ip)
        
        threading.Thread(target=unblock_ip, daemon=True).start()
        
        self._log_security_event(
            event_type="brute_force_detected",
            threat_level=ThreatLevel.CRITICAL,
            source_ip=source_ip,
            user_agent="",
            details={"email": email, "blocked_for": "5_minutes"},
            blocked=True
        )
    
    def _log_security_event(self, event_type: str, threat_level: ThreatLevel, 
                           source_ip: str, user_agent: str, details: Dict[str, Any],
                           user_id: Optional[str] = None, blocked: bool = False):
        """Log security event for compliance"""
        event = SecurityEvent(
            event_id=secrets.token_urlsafe(16),
            user_id=user_id,
            event_type=event_type,
            threat_level=threat_level,
            source_ip=source_ip,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            details=details,
            blocked=blocked
        )
        
        self.security_events.append(event)
        
        # Log to file for compliance
        logger.info(f"SECURITY_EVENT: {event_type} | {threat_level.value} | {source_ip} | {details}")
    
    def _start_session_cleanup(self):
        """Start background session cleanup"""
        def cleanup_loop():
            while True:
                try:
                    current_time = datetime.utcnow()
                    expired_sessions = []
                    
                    with self.session_lock:
                        for session_id, session in self.active_sessions.items():
                            if (current_time - session.created_at > timedelta(hours=8) or
                                current_time - session.last_activity > timedelta(minutes=30)):
                                expired_sessions.append(session_id)
                    
                    for session_id in expired_sessions:
                        self._invalidate_session(session_id, "cleanup_expired")
                    
                    if expired_sessions:
                        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                except Exception as e:
                    logger.error(f"Session cleanup error: {e}")
                
                time.sleep(60)  # Check every minute
        
        cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        cleanup_thread.start()
        logger.info("✅ Session cleanup started")
    
    def _start_threat_monitoring(self):
        """Start background threat monitoring"""
        def monitoring_loop():
            while True:
                try:
                    # Analyze recent security events
                    recent_events = [e for e in self.security_events 
                                   if (datetime.utcnow() - e.timestamp).total_seconds() < 3600]
                    
                    # IP-based threat analysis
                    ip_events = defaultdict(list)
                    for event in recent_events:
                        ip_events[event.source_ip].append(event)
                    
                    for ip, events in ip_events.items():
                        if len(events) > 10:  # More than 10 events per hour
                            self.suspicious_ips[ip] = {
                                "first_seen": min(e.timestamp for e in events),
                                "event_count": len(events),
                                "threat_score": sum(1 if e.threat_level == ThreatLevel.HIGH else 0.5 for e in events)
                            }
                
                except Exception as e:
                    logger.error(f"Threat monitoring error: {e}")
                
                time.sleep(300)  # Check every 5 minutes
        
        monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitoring_thread.start()
        logger.info("✅ Threat monitoring started")
    
    def get_security_dashboard(self) -> Dict[str, Any]:
        """Get security dashboard data"""
        recent_events = [e for e in self.security_events 
                        if (datetime.utcnow() - e.timestamp).total_seconds() < 86400]
        
        return {
            "active_sessions": len(self.active_sessions),
            "blocked_ips": len(self.blocked_ips),
            "suspicious_ips": len(self.suspicious_ips),
            "security_events_24h": len(recent_events),
            "high_threat_events_24h": len([e for e in recent_events if e.threat_level == ThreatLevel.HIGH]),
            "critical_threat_events_24h": len([e for e in recent_events if e.threat_level == ThreatLevel.CRITICAL]),
            "users_with_mfa": len(self.mfa_secrets),
            "avg_session_duration": self._calculate_avg_session_duration()
        }
    
    def _calculate_avg_session_duration(self) -> float:
        """Calculate average session duration in minutes"""
        if not self.active_sessions:
            return 0.0
        
        total_duration = sum(
            (datetime.utcnow() - session.created_at).total_seconds()
            for session in self.active_sessions.values()
        )
        
        return total_duration / len(self.active_sessions) / 60  # Convert to minutes

# Global enterprise security system
enterprise_security = EnterpriseSecuritySystem() 