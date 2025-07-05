#!/usr/bin/env python3
"""
Testi dynaamiselle statussysteemille
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'personal_finance_agent'))

from app.services.sentinel_learning_engine import SentinelLearningEngine, SentinelStatusSystem
from datetime import datetime, timedelta
import json

def test_status_system():
    """Testaa dynaamisen statussysteemin"""
    
    print("🧠 TESTING SENTINEL STATUS SYSTEM™")
    print("=" * 50)
    
    # Luo learning engine
    learning_engine = SentinelLearningEngine()
    
    # Testaa statussysteemiä ilman tietokantaa (mock data)
    print("\n📊 TESTING STATUS CALCULATIONS:")
    
    # Testaa säästämisdiscipliinin analyysiä
    print("\n1. 💰 SÄÄSTÄMISDISCIPLIINI:")
    for score in [0, 15, 35, 60, 85]:
        status = learning_engine.status_system._get_savings_status(score)
        print(f"   {score}% -> {status['title']} (Taso {status['level']})")
    
    # Testaa tulokasvun analyysiä
    print("\n2. 💼 TULOKASVU:")
    for score in [0, 15, 35, 60, 85]:
        status = learning_engine.status_system._get_income_status(score)
        print(f"   {score}% -> {status['title']} (Taso {status['level']})")
    
    # Testaa tavoiteorientaation analyysiä
    print("\n3. 🎯 TAVOITEORIENTAATIO:")
    for score in [0, 15, 35, 60, 85]:
        status = learning_engine.status_system._get_goal_status(score)
        print(f"   {score}% -> {status['title']} (Taso {status['level']})")
    
    # Testaa talouslukutaidon analyysiä
    print("\n4. 🧮 TALOUSLUKUTAITO:")
    for score in [0, 15, 35, 60, 85]:
        status = learning_engine.status_system._get_literacy_status(score)
        print(f"   {score}% -> {status['title']} (Taso {status['level']})")
    
    # Testaa käyttäytymismuutoksen analyysiä
    print("\n5. 🔄 KÄYTTÄYTYMISMUUTOS:")
    for score in [0, 15, 35, 60, 85]:
        status = learning_engine.status_system._get_behavior_status(score)
        print(f"   {score}% -> {status['title']} (Taso {status['level']})")
    
    # Testaa yhteisstatuksen analyysiä
    print("\n6. 🏆 YHTEISSTATUS:")
    for score in [0, 25, 45, 70, 90]:
        status = learning_engine.status_system._get_overall_status(score)
        print(f"   {score}% -> {status['title']} (Taso {status['level']})")
    
    # Testaa kontekstuaalisia statuksia
    print("\n7. 🎯 KONTEKSTUAALISET STATUKSET:")
    
    # Alkoholi-ongelma
    alcohol_profiles = [
        {"alcohol_issue": True, "alcohol_spending": 400},
        {"alcohol_issue": True, "alcohol_spending": 200},
        {"alcohol_issue": True, "alcohol_spending": 50}
    ]
    
    for profile in alcohol_profiles:
        status = learning_engine.get_contextual_status(profile)
        print(f"   Alkoholi {profile['alcohol_spending']}€ -> {status}")
    
    # Laiskuus
    laziness_profiles = [
        {"laziness_level": 9},
        {"laziness_level": 6},
        {"laziness_level": 2}
    ]
    
    for profile in laziness_profiles:
        status = learning_engine.get_contextual_status(profile)
        print(f"   Laiskuus {profile['laziness_level']}/10 -> {status}")
    
    # Talousstress
    stress_profiles = [
        {"financial_stress": 9},
        {"financial_stress": 6},
        {"financial_stress": 2}
    ]
    
    for profile in stress_profiles:
        status = learning_engine.get_contextual_status(profile)
        print(f"   Stress {profile['financial_stress']}/10 -> {status}")
    
    # Testaa parannusalueet ja milestonet
    print("\n8. 📈 PARANNUSALUEET JA MILESTONET:")
    
    # Simuloi huono status
    poor_statuses = {
        'savings_status': {'level': 1},
        'income_status': {'level': 2},
        'goal_status': {'level': 1},
        'literacy_status': {'level': 2},
        'behavior_status': {'level': 1}
    }
    
    improvement_areas = learning_engine.status_system._get_improvement_areas(poor_statuses)
    next_milestones = learning_engine.status_system._get_next_milestones(poor_statuses)
    
    print("   Parannusalueet:")
    for area in improvement_areas:
        print(f"   • {area}")
    
    print("   Seuraavat milestonet:")
    for milestone in next_milestones:
        print(f"   • {milestone}")
    
    # Testaa hyvä status
    good_statuses = {
        'savings_status': {'level': 4},
        'income_status': {'level': 3},
        'goal_status': {'level': 4},
        'literacy_status': {'level': 3},
        'behavior_status': {'level': 4}
    }
    
    improvement_areas = learning_engine.status_system._get_improvement_areas(good_statuses)
    next_milestones = learning_engine.status_system._get_next_milestones(good_statuses)
    
    print("\n   Hyvän statuksen parannusalueet:")
    for area in improvement_areas:
        print(f"   • {area}")
    
    print("   Hyvän statuksen milestonet:")
    for milestone in next_milestones:
        print(f"   • {milestone}")
    
    print("\n✅ SENTINEL STATUS SYSTEM™ TESTI VALMIS!")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_status_system() 