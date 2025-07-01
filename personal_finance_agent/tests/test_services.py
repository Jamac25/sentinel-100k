"""
Unit tests for core services
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Import services to test
from app.services.mock_gpt_service import MockGPTService
from app.services.auth_service import AuthService

class TestMockGPTService:
    """Test Mock GPT Service"""
    
    def setup_method(self):
        """Setup test"""
        self.service = MockGPTService()
    
    @pytest.mark.unit
    def test_health_check(self):
        """Test health check"""
        result = self.service.health_check()
        
        assert result["status"] == "healthy"
        assert result["service"] == "Mock GPT Service"
        assert "uptime" in result
        assert "response_time" in result
    
    @pytest.mark.unit
    def test_get_stats(self):
        """Test get stats"""
        result = self.service.get_stats()
        
        assert result["service"] == "Mock GPT Service"
        assert result["available"] == True
        assert "features" in result
        assert len(result["features"]) > 0
        assert result["cost"] == 0.0
    
    @pytest.mark.unit
    def test_generate_financial_advice(self):
        """Test financial advice generation"""
        test_data = {
            "category": "ruoka",
            "current_spending": 400,
            "suggested_reduction": 100,
            "over_budget_percent": 25
        }
        
        result = self.service.generate_financial_advice(test_data)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "ruoka" in result.lower()
    
    @pytest.mark.unit
    def test_categorize_transaction(self):
        """Test transaction categorization"""
        result = self.service.categorize_transaction("K-Market ruokaostokset", 45.50)
        
        assert isinstance(result, dict)
        assert "category" in result
        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1
        assert "reasoning" in result

class TestAuthService:
    """Test Authentication Service"""
    
    def setup_method(self):
        """Setup test"""
        self.service = AuthService()
    
    @pytest.mark.unit
    def test_get_password_hash(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = self.service.get_password_hash(password)
        
        assert hashed != password
        assert len(hashed) > 50  # bcrypt hash length
        assert hashed.startswith("$2b$")
    
    @pytest.mark.unit
    def test_verify_password(self):
        """Test password verification"""
        password = "testpassword123"
        hashed = self.service.get_password_hash(password)
        
        # Test correct password
        assert self.service.verify_password(password, hashed) == True
        
        # Test incorrect password
        assert self.service.verify_password("wrongpassword", hashed) == False
    
    @pytest.mark.unit
    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = self.service.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50
        assert "." in token  # JWT has dots

 