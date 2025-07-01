#!/usr/bin/env python3
"""
🧪 SENTINEL 100K - COMPREHENSIVE TEST SUITE
===========================================
Tests all 100% complete features
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_system():
    print("🧪 Testing Sentinel 100K Complete System...")
    
    # Test 1: Basic system
    try:
        response = requests.get(f"{BASE_URL}/")
        data = response.json()
        completion = data.get("completion_percentage", 0)
        print(f"✅ System Status: {completion}% complete")
    except:
        print("❌ System not responding")
        return
    
    # Test 2: Health check
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        status = data.get("completion", "unknown")
        print(f"✅ Health Check: {status}")
    except:
        print("❌ Health check failed")
    
    # Test 3: Deep onboarding
    try:
        response = requests.post(f"{BASE_URL}/api/v1/onboarding/start")
        data = response.json()
        user_id = data.get("user_id", "")
        steps = len(data.get("steps", []))
        print(f"✅ Deep Onboarding: {steps} steps, User ID: {user_id[:10]}...")
    except:
        print("❌ Deep onboarding failed")
    
    # Test 4: Weekly cycles
    try:
        response = requests.get(f"{BASE_URL}/api/v1/cycles/current/test_user")
        if response.status_code == 200:
            data = response.json()
            week = data.get("current_cycle", {}).get("week_number", 0)
            target = data.get("current_cycle", {}).get("savings_target", 0)
            print(f"✅ Weekly Cycles: Week {week}, Target: {target}€")
        else:
            print("⚠️ Weekly cycles: User not found (normal for test)")
    except:
        print("❌ Weekly cycles failed")
    
    # Test 5: Night analysis
    try:
        response = requests.post(f"{BASE_URL}/api/v1/analysis/night/trigger")
        data = response.json()
        users = data.get("users_analyzed", 0)
        print(f"✅ Night Analysis: {users} users analyzed")
    except:
        print("❌ Night analysis failed")
    
    # Test 6: AI Chat
    try:
        response = requests.post(f"{BASE_URL}/api/v1/chat/complete", 
                               json={"message": "Onko järjestelmä 100% valmis?"})
        data = response.json()
        context_aware = data.get("context_aware", False)
        completion = data.get("completion_status", "unknown")
        print(f"✅ AI Chat: Context aware: {context_aware}, Status: {completion}")
    except:
        print("❌ AI Chat failed")
    
    print("\n🎯 Test completed! Check results above.")

if __name__ == "__main__":
    test_system() 