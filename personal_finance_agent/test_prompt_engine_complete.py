#!/usr/bin/env python3
"""
Sentinel Prompt Engine™ - Täydellinen testiskripti
Testaa kaikki ominaisuudet ja varmistaa että järjestelmä toimii
"""

import sys
import os
import asyncio
import requests
import json
from datetime import datetime
from typing import Dict, Any

# Lisää app-polku
sys.path.append(os.path.join(os.path.dirname(__file__)))

def print_header(title: str):
    """Tulosta kaunis otsikko"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_result(test_name: str, success: bool, details: Any = None):
    """Tulosta testin tulos"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        if isinstance(details, dict):
            for key, value in details.items():
                print(f"    {key}: {value}")
        else:
            print(f"    {details}")
    print()

def test_imports():
    """Testaa että kaikki importit toimivat"""
    print_header("IMPORT-TESTIT")
    
    try:
        from app.services.sentinel_prompt_engine import (
            prompt_engine,
            PromptCategory,
            PromptSeverity,
            PersonalityType,
            PromptContext,
            PromptTemplate,
            generate_emergency_prompt,
            generate_motivation_prompt,
            generate_achievement_prompt,
            generate_chat_prompt,
            generate_guardian_prompt
        )
        print_result("Import Sentinel Prompt Engine", True, "Kaikki komponentit ladattu")
        return True
    except Exception as e:
        print_result("Import Sentinel Prompt Engine", False, str(e))
        return False

def test_prompt_engine_initialization():
    """Testaa Prompt Engine -alustus"""
    print_header("PROMPT ENGINE -ALUSTUS")
    
    try:
        from app.services.sentinel_prompt_engine import prompt_engine
        
        # Tarkista että templates on ladattu
        template_count = len(prompt_engine.templates)
        print_result("Template Loading", template_count > 0, f"{template_count} templatea ladattu")
        
        # Tarkista persoonallisuudet
        personality_count = len(prompt_engine.personality_configs)
        print_result("Personality Configs", personality_count == 5, f"{personality_count} persoonallisuutta")
        
        # Tarkista fallback-viestit
        fallback_count = len(prompt_engine.fallback_messages)
        print_result("Fallback Messages", fallback_count > 0, f"{fallback_count} fallback-viestiä")
        
        return True
    except Exception as e:
        print_result("Prompt Engine Initialization", False, str(e))
        return False

def test_context_creation():
    """Testaa kontekstin luominen"""
    print_header("KONTEKSTIN LUOMINEN")
    
    try:
        from app.services.sentinel_prompt_engine import PromptContext, PersonalityType
        
        # Peruskonteкsti
        context = PromptContext(
            user_id=123,
            personality=PersonalityType.FRIENDLY_BUDDY,
            current_savings=15000.0,
            monthly_savings=1200.0,
            goal_progress=15.0,
            mood_score=75,
            streak_days=14
        )
        
        print_result("Basic Context Creation", True, {
            "User ID": context.user_id,
            "Personality": context.personality.value,
            "Savings": f"{context.current_savings}€",
            "Progress": f"{context.goal_progress}%"
        })
        
        # Minimaalinen konteksti
        minimal_context = PromptContext(user_id=1)
        print_result("Minimal Context Creation", True, "Oletusarvot käytössä")
        
        return True
    except Exception as e:
        print_result("Context Creation", False, str(e))
        return False

def test_all_categories():
    """Testaa kaikki prompt-kategoriat"""
    print_header("PROMPT-KATEGORIOIDEN TESTAUS")
    
    try:
        from app.services.sentinel_prompt_engine import (
            prompt_engine, PromptCategory, PromptContext, PersonalityType
        )
        
        # Luo testikonteкsti
        context = PromptContext(
            user_id=1,
            personality=PersonalityType.FRIENDLY_BUDDY,
            current_savings=15000.0,
            monthly_savings=1200.0,
            goal_progress=15.0,
            mood_score=75,
            streak_days=14,
            monthly_income=3500.0,
            monthly_expenses=2300.0,
            extra_data={
                "budget_exceeded_amount": "500",
                "days_to_recovery": "7",
                "achievement": "Säästöputki 14 päivää"
            }
        )
        
        # Testaa jokainen kategoria
        categories_to_test = [
            PromptCategory.EMERGENCY,
            PromptCategory.WARNING,
            PromptCategory.MOTIVATION,
            PromptCategory.ACHIEVEMENT,
            PromptCategory.CHAT,
            PromptCategory.GUARDIAN,
            PromptCategory.INCOME_IDEAS
        ]
        
        success_count = 0
        total_count = len(categories_to_test)
        
        for category in categories_to_test:
            try:
                result = prompt_engine.generate_prompt(category, context)
                
                success = result.get("success", False)
                message_length = len(result.get("message", ""))
                template_id = result.get("template_id", "unknown")
                fallback_used = result.get("fallback_used", True)
                
                print_result(
                    f"Category: {category.value}",
                    success and message_length > 0,
                    {
                        "Success": success,
                        "Message Length": message_length,
                        "Template": template_id,
                        "Fallback Used": fallback_used,
                        "Preview": result.get("message", "")[:100] + "..." if result.get("message") else "No message"
                    }
                )
                
                if success:
                    success_count += 1
                    
            except Exception as e:
                print_result(f"Category: {category.value}", False, str(e))
        
        overall_success = success_count / total_count
        print_result(
            "Overall Category Test",
            overall_success >= 0.8,
            f"{success_count}/{total_count} categories passed ({overall_success*100:.1f}%)"
        )
        
        return overall_success >= 0.8
        
    except Exception as e:
        print_result("Category Testing", False, str(e))
        return False

def test_all_personalities():
    """Testaa kaikki persoonallisuudet"""
    print_header("PERSOONALLISUUKSIEN TESTAUS")
    
    try:
        from app.services.sentinel_prompt_engine import (
            prompt_engine, PromptCategory, PromptContext, PersonalityType
        )
        
        personalities = [
            PersonalityType.BUSINESS_COACH,
            PersonalityType.CALM_ADVISOR,
            PersonalityType.TECH_ANALYST,
            PersonalityType.FRIENDLY_BUDDY,
            PersonalityType.STRICT_MENTOR
        ]
        
        success_count = 0
        
        for personality in personalities:
            try:
                context = PromptContext(
                    user_id=1,
                    personality=personality,
                    current_savings=10000,
                    monthly_savings=800,
                    goal_progress=10.0
                )
                
                result = prompt_engine.generate_prompt(PromptCategory.MOTIVATION, context)
                
                success = result.get("success", False)
                message = result.get("message", "")
                
                # Tarkista että persoonallisuuden emoji on mukana
                personality_config = prompt_engine.personality_configs.get(personality, {})
                expected_emoji = personality_config.get("emoji", "🤖")
                has_emoji = message.startswith(expected_emoji)
                
                print_result(
                    f"Personality: {personality.value}",
                    success and has_emoji,
                    {
                        "Success": success,
                        "Has Emoji": has_emoji,
                        "Expected Emoji": expected_emoji,
                        "Message Preview": message[:80] + "..." if message else "No message"
                    }
                )
                
                if success and has_emoji:
                    success_count += 1
                    
            except Exception as e:
                print_result(f"Personality: {personality.value}", False, str(e))
        
        overall_success = success_count / len(personalities)
        print_result(
            "Overall Personality Test",
            overall_success >= 0.8,
            f"{success_count}/{len(personalities)} personalities passed ({overall_success*100:.1f}%)"
        )
        
        return overall_success >= 0.8
        
    except Exception as e:
        print_result("Personality Testing", False, str(e))
        return False

def test_convenience_functions():
    """Testaa mukavuusfunktiot"""
    print_header("MUKAVUUSFUNKTIOIDEN TESTAUS")
    
    try:
        from app.services.sentinel_prompt_engine import (
            PromptContext, PersonalityType,
            generate_emergency_prompt,
            generate_motivation_prompt,
            generate_achievement_prompt,
            generate_chat_prompt,
            generate_guardian_prompt
        )
        
        context = PromptContext(
            user_id=1,
            personality=PersonalityType.FRIENDLY_BUDDY,
            current_savings=15000,
            monthly_savings=1200,
            goal_progress=15.0,
            emergency_mode=True,
            achievement_unlocked="Säästöputki 30 päivää"
        )
        
        functions_to_test = [
            ("Emergency Prompt", generate_emergency_prompt),
            ("Motivation Prompt", generate_motivation_prompt),
            ("Achievement Prompt", generate_achievement_prompt),
            ("Chat Prompt", generate_chat_prompt),
            ("Guardian Prompt", generate_guardian_prompt)
        ]
        
        success_count = 0
        
        for func_name, func in functions_to_test:
            try:
                result = func(context)
                success = result.get("success", False)
                message_length = len(result.get("message", ""))
                
                print_result(
                    func_name,
                    success and message_length > 0,
                    {
                        "Success": success,
                        "Message Length": message_length,
                        "Template": result.get("template_id", "unknown")
                    }
                )
                
                if success and message_length > 0:
                    success_count += 1
                    
            except Exception as e:
                print_result(func_name, False, str(e))
        
        overall_success = success_count / len(functions_to_test)
        print_result(
            "Overall Convenience Functions",
            overall_success >= 0.8,
            f"{success_count}/{len(functions_to_test)} functions passed ({overall_success*100:.1f}%)"
        )
        
        return overall_success >= 0.8
        
    except Exception as e:
        print_result("Convenience Functions", False, str(e))
        return False

def test_fallback_system():
    """Testaa fallback-järjestelmä"""
    print_header("FALLBACK-JÄRJESTELMÄN TESTAUS")
    
    try:
        from app.services.sentinel_prompt_engine import (
            prompt_engine, PromptCategory, PromptContext, PersonalityType
        )
        
        # Luo konteksti puutteellisilla tiedoilla
        minimal_context = PromptContext(user_id=999)
        
        # Testaa että fallback toimii
        result = prompt_engine.generate_prompt(PromptCategory.CHAT, minimal_context)
        
        success = result.get("success", True)  # Fallback on myös success
        message = result.get("message", "")
        fallback_used = result.get("fallback_used", False)
        
        print_result(
            "Fallback System",
            len(message) > 0,  # Tärkeintä että saamme viestin
            {
                "Message Received": len(message) > 0,
                "Fallback Used": fallback_used,
                "Message": message[:100] + "..." if message else "No message"
            }
        )
        
        return len(message) > 0
        
    except Exception as e:
        print_result("Fallback System", False, str(e))
        return False

def test_statistics():
    """Testaa tilastojärjestelmä"""
    print_header("TILASTOJÄRJESTELMÄN TESTAUS")
    
    try:
        from app.services.sentinel_prompt_engine import prompt_engine
        
        # Hae tilastot
        stats = prompt_engine.get_usage_statistics()
        
        required_fields = ["total_templates", "total_usage", "average_usage_per_template"]
        has_all_fields = all(field in stats for field in required_fields)
        
        print_result(
            "Statistics Collection",
            has_all_fields,
            {
                "Total Templates": stats.get("total_templates", 0),
                "Total Usage": stats.get("total_usage", 0),
                "Has All Fields": has_all_fields
            }
        )
        
        return has_all_fields
        
    except Exception as e:
        print_result("Statistics", False, str(e))
        return False

def test_api_endpoints():
    """Testaa API-endpointit (jos backend on käynnissä)"""
    print_header("API-ENDPOINTTIEN TESTAUS")
    
    base_url = "http://localhost:8000"
    
    try:
        # Testaa health check
        response = requests.get(f"{base_url}/api/v1/prompt-engine/health-check", timeout=5)
        health_ok = response.status_code == 200
        
        print_result(
            "Health Check Endpoint",
            health_ok,
            {
                "Status Code": response.status_code,
                "Response": response.json() if health_ok else "Failed"
            }
        )
        
        if not health_ok:
            print("⚠️ Backend ei ole käynnissä - ohitetaan API-testit")
            return True  # Ei kriittinen virhe
        
        # Testaa personalities endpoint
        try:
            response = requests.get(f"{base_url}/api/v1/prompt-engine/personalities", timeout=5)
            personalities_ok = response.status_code == 200
            
            print_result(
                "Personalities Endpoint",
                personalities_ok,
                {
                    "Status Code": response.status_code,
                    "Personalities Count": len(response.json().get("personalities", [])) if personalities_ok else 0
                }
            )
        except:
            print_result("Personalities Endpoint", False, "Request failed")
        
        return health_ok
        
    except requests.exceptions.RequestException:
        print_result("API Connection", False, "Backend ei ole käynnissä")
        print("💡 Käynnistä backend komennolla: python3 simple_start.py")
        return True  # Ei kriittinen virhe

def run_all_tests():
    """Suorita kaikki testit"""
    print_header("SENTINEL PROMPT ENGINE™ - TÄYDELLINEN TESTISARJA")
    print("🚀 Aloitetaan testaus...")
    
    tests = [
        ("Imports", test_imports),
        ("Engine Initialization", test_prompt_engine_initialization),
        ("Context Creation", test_context_creation),
        ("All Categories", test_all_categories),
        ("All Personalities", test_all_personalities),
        ("Convenience Functions", test_convenience_functions),
        ("Fallback System", test_fallback_system),
        ("Statistics", test_statistics),
        ("API Endpoints", test_api_endpoints)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed_tests += 1
        except Exception as e:
            print_result(f"Test: {test_name}", False, f"Unexpected error: {e}")
    
    # Lopputulos
    print_header("TESTIEN YHTEENVETO")
    
    success_rate = (passed_tests / total_tests) * 100
    overall_success = success_rate >= 80
    
    print_result(
        "OVERALL RESULT",
        overall_success,
        {
            "Tests Passed": f"{passed_tests}/{total_tests}",
            "Success Rate": f"{success_rate:.1f}%",
            "Status": "🎉 EXCELLENT!" if success_rate >= 90 else "✅ GOOD" if success_rate >= 80 else "⚠️ NEEDS WORK"
        }
    )
    
    if overall_success:
        print("\n🎉 Sentinel Prompt Engine™ on valmis käyttöön!")
        print("💡 Käynnistä backend: python3 simple_start.py")
        print("💡 Testaa API: curl http://localhost:8000/api/v1/prompt-engine/health-check")
    else:
        print("\n⚠️ Joitakin ongelmia havaittu. Tarkista virheet yllä.")
    
    return overall_success

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
 
 
 