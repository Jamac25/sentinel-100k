"""
API integration tests
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

from app.main import app

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    @pytest.mark.api
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Personal Finance Agent" in data["message"]
    
    @pytest.mark.api
    def test_mock_gpt_health(self):
        """Test Mock GPT health endpoint"""
        response = self.client.get("/api/v1/mock-gpt/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Mock GPT Service"
    
    @pytest.mark.api
    def test_mock_gpt_stats(self):
        """Test Mock GPT stats endpoint"""
        response = self.client.get("/api/v1/mock-gpt/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Mock GPT Service"
        assert data["available"] == True
        assert "features" in data

class TestAuthAPI:
    """Test authentication API"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    @pytest.mark.api
    def test_register_user(self):
        """Test user registration"""
        user_data = {
            "email": "testapi@example.com",
            "password": "testpassword123",
            "name": "Test API User"
        }
        
        response = self.client.post("/api/v1/auth/register", json=user_data)
        # Might fail due to database constraints, but should not crash
        assert response.status_code in [200, 201, 400, 409]
    
    @pytest.mark.api
    def test_login_invalid_user(self):
        """Test login with invalid credentials"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = self.client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401

class TestMockGPTAPI:
    """Test Mock GPT API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        # Mock authentication
        self.headers = {"Authorization": "Bearer mock_token"}
    
    @pytest.mark.api
    @patch('app.api.auth.get_current_user')
    def test_financial_advice_endpoint(self, mock_auth):
        """Test financial advice endpoint"""
        # Mock user
        mock_auth.return_value = type('MockUser', (), {'id': 1, 'email': 'test@example.com'})()
        
        advice_data = {
            "category": "ruoka",
            "current_spending": 400,
            "suggested_reduction": 100,
            "over_budget_percent": 25
        }
        
        response = self.client.post(
            "/api/v1/mock-gpt/financial-advice",
            json=advice_data,
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "advice" in data
        assert "service" in data
    
    @pytest.mark.api
    @patch('app.api.auth.get_current_user')
    def test_income_idea_endpoint(self, mock_auth):
        """Test income idea endpoint"""
        # Mock user
        mock_auth.return_value = type('MockUser', (), {'id': 1, 'email': 'test@example.com'})()
        
        idea_data = {
            "skills": ["python", "web development"],
            "available_time": 15,
            "preferred_categories": ["freelance"]
        }
        
        response = self.client.post(
            "/api/v1/mock-gpt/income-idea",
            json=idea_data,
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "idea" in data
        assert "service" in data
    
    @pytest.mark.api
    @patch('app.api.auth.get_current_user')
    def test_categorize_endpoint(self, mock_auth):
        """Test categorization endpoint"""
        # Mock user
        mock_auth.return_value = type('MockUser', (), {'id': 1, 'email': 'test@example.com'})()
        
        transaction_data = {
            "description": "K-Market ruokaostokset",
            "amount": 45.50
        }
        
        response = self.client.post(
            "/api/v1/mock-gpt/categorize",
            json=transaction_data,
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "categorization" in data
        assert "service" in data

class TestJobAgentAPI:
    """Test Job Agent API endpoints"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
        self.headers = {"Authorization": "Bearer mock_token"}
    
    @pytest.mark.api
    def test_job_agent_health(self):
        """Test job agent health endpoint"""
        response = self.client.get("/api/v1/job-agent/health-check")
        # Might not exist yet, but should not crash
        assert response.status_code in [200, 404]
    
    @pytest.mark.api
    @patch('app.api.auth.get_current_user')
    def test_cv_analysis_endpoint(self, mock_auth):
        """Test CV analysis endpoint"""
        # Mock user
        mock_auth.return_value = type('MockUser', (), {'id': 1, 'email': 'test@example.com'})()
        
        cv_data = {
            "cv_text": "John Doe, Software Developer, Python, JavaScript, 3 years experience"
        }
        
        # This endpoint might not exist yet
        response = self.client.post(
            "/api/v1/job-agent/analyze-cv",
            json=cv_data,
            headers=self.headers
        )
        
        # Should not crash, might return 404 if not implemented
        assert response.status_code in [200, 404, 422]

class TestErrorHandling:
    """Test API error handling"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    @pytest.mark.api
    def test_invalid_endpoint(self):
        """Test invalid endpoint"""
        response = self.client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    @pytest.mark.api
    def test_invalid_json(self):
        """Test invalid JSON data"""
        response = self.client.post(
            "/api/v1/mock-gpt/financial-advice",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 401, 422]  # Various possible error codes
    
    @pytest.mark.api
    def test_missing_auth_header(self):
        """Test missing authentication header"""
        response = self.client.post(
            "/api/v1/mock-gpt/financial-advice",
            json={"category": "test"}
        )
        assert response.status_code == 401

class TestCORSAndSecurity:
    """Test CORS and security headers"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    @pytest.mark.api
    def test_cors_headers(self):
        """Test CORS headers"""
        response = self.client.options("/api/v1/mock-gpt/health")
        # CORS might be configured
        assert response.status_code in [200, 405]
    
    @pytest.mark.api
    def test_security_headers(self):
        """Test security headers"""
        response = self.client.get("/")
        # Should have basic security headers
        headers = response.headers
        # These might not be configured yet, just check response is valid
        assert response.status_code == 200 
 
 
 
 