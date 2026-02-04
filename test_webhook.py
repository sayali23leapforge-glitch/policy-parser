#!/usr/bin/env python3
"""
Quick test script to verify webhook implementation
Run this to test the webhook endpoint and lead fetching
"""

import requests
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
META_WEBHOOK_VERIFY_TOKEN = os.getenv('META_WEBHOOK_VERIFY_TOKEN', 'test_token')

print("=" * 60)
print("🧪 WEBHOOK IMPLEMENTATION TEST SUITE")
print("=" * 60)
print(f"\n📍 Backend URL: {BACKEND_URL}")
print(f"🔐 Webhook Verify Token: {META_WEBHOOK_VERIFY_TOKEN}")

# Test 1: Webhook Verification (GET request)
print("\n\n1️⃣  Testing Webhook Verification (GET /webhook)...")
print("-" * 60)

try:
    response = requests.get(
        f'{BACKEND_URL}/webhook',
        params={
            'hub.challenge': 'test_challenge_123',
            'hub.verify_token': META_WEBHOOK_VERIFY_TOKEN
        }
    )
    
    if response.status_code == 200 and response.text == 'test_challenge_123':
        print("✅ PASS: Webhook verification works correctly")
        print(f"   Response: {response.text}")
    else:
        print(f"❌ FAIL: Expected 'test_challenge_123', got '{response.text}'")
        print(f"   Status: {response.status_code}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

# Test 2: Webhook Verification Failure (wrong token)
print("\n\n2️⃣  Testing Webhook Verification Failure (invalid token)...")
print("-" * 60)

try:
    response = requests.get(
        f'{BACKEND_URL}/webhook',
        params={
            'hub.challenge': 'test_challenge_123',
            'hub.verify_token': 'wrong_token_12345'
        }
    )
    
    if response.status_code == 403:
        print("✅ PASS: Webhook correctly rejects invalid token")
        print(f"   Status: {response.status_code} (Forbidden)")
    else:
        print(f"❌ FAIL: Expected status 403, got {response.status_code}")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

# Test 3: Check API endpoints exist
print("\n\n3️⃣  Testing API Endpoints...")
print("-" * 60)

endpoints = [
    ('/api/leads', 'GET'),
    ('/api/leads/sync', 'POST'),
    ('/webhook', 'GET'),
]

for endpoint, method in endpoints:
    try:
        if method == 'GET':
            response = requests.get(f'{BACKEND_URL}{endpoint}', timeout=5)
        else:
            response = requests.post(f'{BACKEND_URL}{endpoint}', json={}, timeout=5)
        
        print(f"✅ {method} {endpoint}: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"⚠️  {method} {endpoint}: Connection refused (backend not running?)")
    except Exception as e:
        print(f"⚠️  {method} {endpoint}: {type(e).__name__}")

# Test 4: Simulation of webhook payload
print("\n\n4️⃣  Simulating Webhook Payload (for manual testing)...")
print("-" * 60)

webhook_payload = {
    "object": "page",
    "entry": [
        {
            "id": "page_id_123456",
            "time": int(datetime.now().timestamp()),
            "changes": [
                {
                    "value": {
                        "leadgen_id": "lead_id_test_123456"
                    },
                    "field": "leadgen"
                }
            ]
        }
    ]
}

print("📤 Sample webhook payload (use for testing):")
print(json.dumps(webhook_payload, indent=2))

print("\n\n" + "=" * 60)
print("✅ TEST SUITE COMPLETE")
print("=" * 60)

print("\n📋 NEXT STEPS:")
print("1. Ensure backend is running: python backend/app.py")
print("2. Configure webhook in Facebook App Settings")
print("3. Set webhook URL to: https://your-domain.com/webhook")
print("4. Create a test lead on Facebook")
print("5. Check dashboard for instant lead appearance")
print("6. Monitor logs: tail -f flask_log.txt | grep 'leadgen'")

print("\n💡 DEBUGGING:")
print("- Check browser console for: '✅ Real-time webhook listener active'")
print("- Check server logs for: '📝 New leadgen event'")
print("- Verify HTTPS is working (required for production)")
print("- Test with ngrok for local HTTPS: ngrok http 5000")

print("\n" + "=" * 60)
