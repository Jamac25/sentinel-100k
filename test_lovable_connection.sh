#!/bin/bash

echo "🧪 Testing Lovable ↔ Sentinel Backend Connection"
echo "================================================"

# Test backend health
echo "1. 🔍 Testing backend health..."
health_response=$(curl -s http://localhost:8000/health)
if [[ $? -eq 0 ]]; then
    echo "✅ Backend is running on port 8000"
else
    echo "❌ Backend not responding on port 8000"
    exit 1
fi

# Test dashboard endpoint
echo ""
echo "2. 📊 Testing dashboard endpoint..."
dashboard_response=$(curl -s http://localhost:8000/api/v1/dashboard/summary)
if [[ $? -eq 0 ]]; then
    echo "✅ Dashboard endpoint responding"
    echo "   Income: $(echo $dashboard_response | jq -r '.total_income')€"
    echo "   Expenses: $(echo $dashboard_response | jq -r '.total_expenses')€" 
    echo "   Balance: $(echo $dashboard_response | jq -r '.net_amount')€"
else
    echo "❌ Dashboard endpoint not working"
    exit 1
fi

# Test transactions endpoint
echo ""
echo "3. 💳 Testing transactions endpoint..."
transactions_response=$(curl -s http://localhost:8000/api/v1/transactions)
transaction_count=$(echo $transactions_response | jq '. | length')
if [[ $transaction_count -gt 0 ]]; then
    echo "✅ Transactions endpoint working ($transaction_count transactions)"
else
    echo "❌ No transactions found"
fi

# Test goals endpoint
echo ""
echo "4. 🎯 Testing goals endpoint..."
goals_response=$(curl -s http://localhost:8000/api/v1/dashboard/goals/progress)
goal_count=$(echo $goals_response | jq '. | length')
if [[ $goal_count -gt 0 ]]; then
    echo "✅ Goals endpoint working ($goal_count goals)"
    main_goal=$(echo $goals_response | jq -r '.[0].goal_name')
    progress=$(echo $goals_response | jq -r '.[0].progress_percent')
    echo "   Main goal: $main_goal ($progress%)"
else
    echo "❌ No goals found"
fi

# Test categories endpoint
echo ""
echo "5. 📂 Testing categories endpoint..."
categories_response=$(curl -s http://localhost:8000/api/v1/categories)
category_count=$(echo $categories_response | jq '. | length')
if [[ $category_count -gt 0 ]]; then
    echo "✅ Categories endpoint working ($category_count categories)"
else
    echo "❌ No categories found"
fi

# Test AI chat endpoint
echo ""
echo "6. 🤖 Testing AI chat endpoint..."
chat_response=$(curl -s -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Miten säästän enemmän?"}')
if [[ $? -eq 0 ]]; then
    echo "✅ AI chat endpoint working"
    ai_response=$(echo $chat_response | jq -r '.response')
    echo "   AI response: ${ai_response:0:60}..."
else
    echo "❌ AI chat endpoint not working"
fi

echo ""
echo "🎉 Connection Test Complete!"
echo "==============================================="
echo "📍 Backend URL: http://localhost:8000"
echo "📍 Frontend URL: http://localhost:8080"
echo ""
echo "🔗 For Lovable frontend, use these endpoints:"
echo "   Dashboard: http://localhost:8000/api/v1/dashboard/summary"
echo "   Transactions: http://localhost:8000/api/v1/transactions"
echo "   Goals: http://localhost:8000/api/v1/dashboard/goals/progress"
echo "   AI Chat: http://localhost:8000/api/v1/chat"
echo ""
echo "✅ All endpoints should work with your Lovable frontend!" 