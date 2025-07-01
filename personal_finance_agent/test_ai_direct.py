#!/usr/bin/env python3
"""
Suora AI-testaus - Testaa Mock GPT servicea suoraan ilman API:a
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.mock_gpt_service import mock_gpt_service
import json

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_result(test_name: str, success: bool, data: any = None):
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

def test_service_health():
    """Test service health"""
    try:
        health = mock_gpt_service.health_check()
        print_result("Service Health Check", True, {
            "Status": health.get("status"),
            "Service": health.get("service"),
            "Response Time": health.get("response_time")
        })
        return True
    except Exception as e:
        print_result("Service Health Check", False, str(e))
        return False

def test_service_stats():
    """Test service stats"""
    try:
        stats = mock_gpt_service.get_stats()
        print_result("Service Stats", True, {
            "Model": stats.get("model"),
            "Available": stats.get("available"),
            "Features": len(stats.get("features", [])),
            "Total Requests": stats.get("total_requests")
        })
        return True
    except Exception as e:
        print_result("Service Stats", False, str(e))
        return False

def test_financial_advice():
    """Test financial advice generation"""
    try:
        test_data = {
            "category": "ruoka",
            "current_spending": 400,
            "suggested_reduction": 100,
            "over_budget_percent": 25
        }
        
        advice = mock_gpt_service.generate_financial_advice(test_data)
        print_result("Financial Advice Generation", True, {
            "Advice": advice
        })
        return True
    except Exception as e:
        print_result("Financial Advice Generation", False, str(e))
        return False

def test_income_ideas():
    """Test income idea generation"""
    try:
        test_profile = {
            "skills": ["tietokone", "valokuvaus", "kirjoittaminen"],
            "available_time": 15
        }
        
        idea = mock_gpt_service.generate_income_idea(test_profile)
        print_result("Income Idea Generation", True, {
            "Type": idea.get("type"),
            "Description": idea.get("description"),
            "Estimated Income": f"{idea.get('estimated_income')}€",
            "Time Required": idea.get("time_required"),
            "Difficulty": idea.get("difficulty")
        })
        return True
    except Exception as e:
        print_result("Income Idea Generation", False, str(e))
        return False

def test_motivation_messages():
    """Test motivation message generation"""
    try:
        test_progress = {
            "monthly_savings": 600,
            "current_month_savings": 320,
            "streak_days": 12,
            "mood": "great"
        }
        
        message = mock_gpt_service.generate_motivation_message(test_progress)
        print_result("Motivation Message Generation", True, {
            "Message": message
        })
        return True
    except Exception as e:
        print_result("Motivation Message Generation", False, str(e))
        return False

def test_transaction_categorization():
    """Test transaction categorization"""
    try:
        test_cases = [
            ("K-Market ruokaostokset", 45.50),
            ("Shell bensa-asema", 60.00),
            ("Ravintola Fazer", 35.00),
            ("Apteekki lääkkeet", 25.00),
            ("H&M vaatteet", 80.00)
        ]
        
        results = []
        for description, amount in test_cases:
            result = mock_gpt_service.categorize_transaction(description, amount)
            results.append({
                "Description": description,
                "Amount": f"{amount}€",
                "Category": result.get("category"),
                "Confidence": f"{result.get('confidence', 0)*100:.1f}%"
            })
        
        print_result("Transaction Categorization", True, {
            "Test Cases": len(test_cases),
            "Results": json.dumps(results, indent=2, ensure_ascii=False)
        })
        return True
    except Exception as e:
        print_result("Transaction Categorization", False, str(e))
        return False

def test_spending_analysis():
    """Test spending pattern analysis"""
    try:
        test_transactions = [
            {"description": "K-Market", "amount": 45.50, "category": "ruoka"},
            {"description": "Shell bensa", "amount": 60.00, "category": "liikenne"},
            {"description": "Ravintola", "amount": 35.00, "category": "ravintolat"},
            {"description": "Apteekki", "amount": 25.00, "category": "terveys"},
            {"description": "Vaatekauppa", "amount": 80.00, "category": "vaatteet"},
            {"description": "Elisa lasku", "amount": 45.00, "category": "tietoliikenne"},
            {"description": "Spotify", "amount": 9.99, "category": "viihde"}
        ]
        
        analysis = mock_gpt_service.analyze_spending_pattern(test_transactions)
        print_result("Spending Pattern Analysis", True, {
            "Total Analyzed": analysis.get("total_analyzed"),
            "Total Amount": f"{analysis.get('total_amount')}€",
            "Average Transaction": f"{analysis.get('average_transaction', 0):.2f}€",
            "Insights Count": len(analysis.get("insights", [])),
            "Recommendations Count": len(analysis.get("recommendations", [])),
            "Confidence": f"{analysis.get('confidence', 0)*100:.1f}%"
        })
        
        # Show insights
        insights = analysis.get("insights", [])
        if insights:
            print("   📊 Key Insights:")
            for i, insight in enumerate(insights[:3], 1):
                print(f"      {i}. {insight}")
        
        return True
    except Exception as e:
        print_result("Spending Pattern Analysis", False, str(e))
        return False

def test_performance():
    """Test service performance"""
    try:
        import time
        
        # Test multiple requests
        start_time = time.time()
        
        for i in range(10):
            mock_gpt_service.categorize_transaction(f"Test transaction {i}", 50.0)
            mock_gpt_service.generate_motivation_message({"mood": "good"})
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 20  # 20 requests total
        
        print_result("Performance Test", True, {
            "Total Requests": 20,
            "Total Time": f"{total_time:.2f}s",
            "Average Response Time": f"{avg_time*1000:.1f}ms",
            "Requests per Second": f"{20/total_time:.1f}"
        })
        return True
    except Exception as e:
        print_result("Performance Test", False, str(e))
        return False

def main():
    """Main test function"""
    print_section("SUORA AI-TESTAUS")
    print("🎯 Testaa Mock GPT servicea suoraan ilman FastAPI:a")
    
    # Test basic functionality
    print_section("BASIC FUNCTIONALITY")
    health_ok = test_service_health()
    stats_ok = test_service_stats()
    
    if not health_ok:
        print("❌ Mock GPT service ei ole käytettävissä.")
        return
    
    # Test AI features
    print_section("AI FEATURES")
    
    tests = [
        ("Financial Advice", test_financial_advice),
        ("Income Ideas", test_income_ideas),
        ("Motivation Messages", test_motivation_messages),
        ("Transaction Categorization", test_transaction_categorization),
        ("Spending Analysis", test_spending_analysis)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"🧪 Testing {test_name}...")
        success = test_func()
        results.append((test_name, success))
    
    # Test performance
    print_section("PERFORMANCE")
    perf_ok = test_performance()
    
    # Final stats
    final_stats = mock_gpt_service.get_stats()
    print_section("FINAL STATS")
    print(f"📊 Total Requests Made: {final_stats.get('total_requests')}")
    print(f"💰 Total Cost: {final_stats.get('cost')}€ (Mock service is free!)")
    print(f"🎯 All Features Available: {final_stats.get('available')}")
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"🎯 AI Feature Tests: {passed}/{total} passed")
    print(f"📊 Basic Tests: {'✅ PASS' if health_ok and stats_ok else '❌ FAIL'}")
    print(f"⚡ Performance Test: {'✅ PASS' if perf_ok else '❌ FAIL'}")
    
    if passed == total and health_ok and stats_ok and perf_ok:
        print("\n🎉 KAIKKI TESTIT ONNISTUIVAT!")
        print("✨ Mock GPT AI-palvelu toimii täydellisesti!")
        print("🚀 Valmis siirtymään aitoon OpenAI API:in!")
        print("\n🔥 AI-OMINAISUUDET TESTATTU:")
        print("   💡 Talousneuvonta")
        print("   💰 Ansaintaideat")  
        print("   🎯 Motivaatioviestit")
        print("   🏷️ Transaktioiden kategorisointi")
        print("   📊 Kulutuskuvioiden analyysi")
    else:
        print(f"\n⚠️  {total + 3 - passed - (1 if health_ok else 0) - (1 if stats_ok else 0) - (1 if perf_ok else 0)} testiä epäonnistui.")
        print("🔧 Tarkista virheet ja korjaa ongelmat.")

if __name__ == "__main__":
    main() 
 
 
 
 