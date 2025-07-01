#!/usr/bin/env python3
"""
Mock GPT Testi - Testaa kaikki AI-ominaisuudet ilman oikeaa OpenAI API:a
"""
import requests
import json
import time
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Test data
TEST_USER = {
    "email": "test@example.com", 
    "password": "testpass123",
    "name": "Test User"
}

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_result(test_name: str, success: bool, data: Any = None):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if data and success:
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                print(f"   {key}: {value}")
        else:
            print(f"   Response: {data}")
    elif not success:
        print(f"   Error: {data}")
    print()

def register_and_login() -> str:
    """Register test user and get JWT token"""
    try:
        # Try to register
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json=TEST_USER
        )
        
        # Login to get token - use email instead of username
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": TEST_USER["email"],
                "password": TEST_USER["password"]
            }
        )
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            return token_data["access_token"]
        else:
            print(f"Login failed: {login_response.text}")
            return None
            
    except Exception as e:
        print(f"Auth error: {e}")
        return None

def test_mock_gpt_health():
    """Test Mock GPT health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/mock-gpt/health")
        if response.status_code == 200:
            data = response.json()
            print_result("Mock GPT Health Check", True, {
                "Status": data.get("status"),
                "Service": data.get("service"),
                "Response Time": data.get("response_time")
            })
            return True
        else:
            print_result("Mock GPT Health Check", False, response.text)
            return False
    except Exception as e:
        print_result("Mock GPT Health Check", False, str(e))
        return False

def test_mock_gpt_stats():
    """Test Mock GPT stats endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/mock-gpt/stats")
        if response.status_code == 200:
            data = response.json()
            print_result("Mock GPT Stats", True, {
                "Model": data.get("model"),
                "Available": data.get("available"),
                "Features": len(data.get("features", [])),
                "Cost": data.get("cost")
            })
            return True
        else:
            print_result("Mock GPT Stats", False, response.text)
            return False
    except Exception as e:
        print_result("Mock GPT Stats", False, str(e))
        return False

def test_financial_advice(token: str):
    """Test financial advice generation"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "category": "ruoka",
            "current_spending": 400,
            "suggested_reduction": 100,
            "over_budget_percent": 25
        }
        
        response = requests.post(
            f"{BASE_URL}/mock-gpt/financial-advice",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result("Financial Advice Generation", True, {
                "Status": result.get("status"),
                "Advice": result.get("advice"),
                "Service": result.get("service")
            })
            return True
        else:
            print_result("Financial Advice Generation", False, response.text)
            return False
    except Exception as e:
        print_result("Financial Advice Generation", False, str(e))
        return False

def test_income_idea(token: str):
    """Test income idea generation"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "skills": ["tietokone", "valokuvaus", "kirjoittaminen"],
            "available_time": 15,
            "preferred_categories": ["freelance", "gig_economy"]
        }
        
        response = requests.post(
            f"{BASE_URL}/mock-gpt/income-idea",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            idea = result.get("idea", {})
            print_result("Income Idea Generation", True, {
                "Type": idea.get("type"),
                "Description": idea.get("description"),
                "Estimated Income": f"{idea.get('estimated_income')}€",
                "Time Required": idea.get("time_required")
            })
            return True
        else:
            print_result("Income Idea Generation", False, response.text)
            return False
    except Exception as e:
        print_result("Income Idea Generation", False, str(e))
        return False

def test_motivation_message(token: str):
    """Test motivation message generation"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "monthly_savings": 600,
            "current_month_savings": 320,
            "streak_days": 12,
            "mood": "great"
        }
        
        response = requests.post(
            f"{BASE_URL}/mock-gpt/motivation",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result("Motivation Message Generation", True, {
                "Message": result.get("message"),
                "Service": result.get("service")
            })
            return True
        else:
            print_result("Motivation Message Generation", False, response.text)
            return False
    except Exception as e:
        print_result("Motivation Message Generation", False, str(e))
        return False

def test_transaction_categorization(token: str):
    """Test transaction categorization"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "description": "K-Market ruokaostokset",
            "amount": 45.50
        }
        
        response = requests.post(
            f"{BASE_URL}/mock-gpt/categorize",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            categorization = result.get("categorization", {})
            print_result("Transaction Categorization", True, {
                "Category": categorization.get("category"),
                "Confidence": f"{categorization.get('confidence', 0)*100:.1f}%",
                "Reasoning": categorization.get("reasoning")
            })
            return True
        else:
            print_result("Transaction Categorization", False, response.text)
            return False
    except Exception as e:
        print_result("Transaction Categorization", False, str(e))
        return False

def test_spending_analysis(token: str):
    """Test spending pattern analysis"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "transactions": [
                {"description": "K-Market", "amount": 45.50, "category": "ruoka"},
                {"description": "Shell bensa", "amount": 60.00, "category": "liikenne"},
                {"description": "Ravintola", "amount": 35.00, "category": "ravintolat"},
                {"description": "Apteekki", "amount": 25.00, "category": "terveys"},
                {"description": "Vaatekauppa", "amount": 80.00, "category": "vaatteet"}
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/mock-gpt/analyze-spending",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get("analysis", {})
            print_result("Spending Pattern Analysis", True, {
                "Total Analyzed": analysis.get("total_analyzed"),
                "Total Amount": f"{analysis.get('total_amount')}€",
                "Average Transaction": f"{analysis.get('average_transaction', 0):.2f}€",
                "Insights": len(analysis.get("insights", [])),
                "Recommendations": len(analysis.get("recommendations", []))
            })
            return True
        else:
            print_result("Spending Pattern Analysis", False, response.text)
            return False
    except Exception as e:
        print_result("Spending Pattern Analysis", False, str(e))
        return False

def test_all_features(token: str):
    """Test all features at once"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.post(
            f"{BASE_URL}/mock-gpt/test-all-features",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result("All Features Test", True, {
                "Status": result.get("status"),
                "Message": result.get("message"),
                "Features Tested": result.get("total_features_tested")
            })
            
            # Show details of each test
            test_results = result.get("test_results", {})
            for feature, data in test_results.items():
                if feature == "service_stats":
                    print(f"   📊 Service Stats: {data.get('total_requests')} requests")
                elif isinstance(data, dict) and "category" in data:
                    print(f"   🏷️ Categorization: {data.get('category')} ({data.get('confidence', 0)*100:.0f}%)")
                elif isinstance(data, dict) and "type" in data:
                    print(f"   💡 Income Idea: {data.get('type')} - {data.get('estimated_income')}€")
                elif isinstance(data, str):
                    print(f"   💬 {feature}: {data[:50]}...")
            
            return True
        else:
            print_result("All Features Test", False, response.text)
            return False
    except Exception as e:
        print_result("All Features Test", False, str(e))
        return False

def main():
    """Main test function"""
    print_section("MOCK GPT API TESTAUS")
    print("🎯 Testaa kaikki AI-ominaisuudet ilman oikeaa OpenAI API:a")
    
    # Test basic endpoints first (no auth required)
    print_section("BASIC ENDPOINTS")
    health_ok = test_mock_gpt_health()
    stats_ok = test_mock_gpt_stats()
    
    if not health_ok:
        print("❌ Mock GPT service ei ole käytettävissä. Tarkista API server.")
        return
    
    # Get authentication token
    print_section("AUTHENTICATION")
    print("🔐 Kirjaudutaan sisään...")
    token = register_and_login()
    
    if not token:
        print("❌ Kirjautuminen epäonnistui. Tarkista auth service.")
        return
    
    print_result("Authentication", True, {"Token": f"{token[:20]}..."})
    
    # Test all AI features
    print_section("AI FEATURES")
    
    tests = [
        ("Financial Advice", lambda: test_financial_advice(token)),
        ("Income Ideas", lambda: test_income_idea(token)),
        ("Motivation Messages", lambda: test_motivation_message(token)),
        ("Transaction Categorization", lambda: test_transaction_categorization(token)),
        ("Spending Analysis", lambda: test_spending_analysis(token))
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🧪 Testing {test_name}...")
        success = test_func()
        results.append((test_name, success))
        time.sleep(0.5)  # Small delay between tests
    
    # Test all features at once
    print_section("COMPREHENSIVE TEST")
    all_features_ok = test_all_features(token)
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"🎯 Individual Tests: {passed}/{total} passed")
    print(f"🔄 Comprehensive Test: {'✅ PASS' if all_features_ok else '❌ FAIL'}")
    print(f"📊 Basic Endpoints: {'✅ PASS' if health_ok and stats_ok else '❌ FAIL'}")
    
    if passed == total and all_features_ok:
        print("\n🎉 KAIKKI TESTIT ONNISTUIVAT!")
        print("✨ Mock GPT API on valmis käyttöön!")
        print("🚀 Voit nyt siirtyä aitoon OpenAI API:in kun olet valmis.")
    else:
        print(f"\n⚠️  {total - passed} testiä epäonnistui.")
        print("🔧 Tarkista virheloki ja korjaa ongelmat.")

if __name__ == "__main__":
    main() 
 
 
 
 