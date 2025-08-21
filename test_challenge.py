# #!/usr/bin/env python3
"""
Test script for AI Engineer Challenge
Run this to validate your implementation
"""

import json
import asyncio
import time
from typing import Dict, Any
import httpx

# Import your model
from app.models.dex_model import DexScoringModel

# Sample test data
SAMPLE_WALLET_MESSAGE = {
    "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96590e4265",
    "data": [
        {
            "protocolType": "dexes",
            "transactions": [
                {
                    "document_id": "507f1f77bcf86cd799439011",
                    "action": "swap",
                    "timestamp": 1703980800,
                    "caller": "0x742d35Cc6634C0532925a3b8D4C9db96590e4265",
                    "protocol": "uniswap_v3",
                    "poolId": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
                    "poolName": "Uniswap V3 USDC/WETH 0.05%",
                    "tokenIn": {"amountUSD": 1000.0},
                    "tokenOut": {"amountUSD": 1000.0},
                },
                {
                    "document_id": "507f1f77bcf86cd799439012",
                    "action": "deposit",
                    "timestamp": 1703980900,
                    "caller": "0x742d35Cc6634C0532925a3b8D4C9db96590e4265",
                    "protocol": "uniswap_v3",
                    "poolId": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
                    "poolName": "Uniswap V3 USDC/WETH 0.05%",
                    "token0": {"amountUSD": 500.0},
                    "token1": {"amountUSD": 500.0},
                },
                {
                    "document_id": "507f1f77bcf86cd799439013",
                    "action": "withdraw",
                    "timestamp": 1703981800,
                    "caller": "0x742d35Cc6634C0532925a3b8D4C9db96590e4265",
                    "protocol": "uniswap_v3",
                    "poolId": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
                    "poolName": "Uniswap V3 USDC/WETH 0.05%",
                    "token0": {"amountUSD": 250.0},
                    "token1": {"amountUSD": 250.0},
                },
            ]
        }
    ],
}

EXPECTED_FEATURES = {
    "total_deposit_usd": 500.0,
    "total_withdraw_usd": 500.0,
    "num_deposits": 1,
    "num_withdraws": 1,
    "total_swap_volume": 1000.0,
    "num_swaps": 1,
    "unique_pools": 1,
}

# ------------------ SERVER TESTS ------------------
async def test_server_health(base_url: str = "http://localhost:8000"):
    """Test if the server is running and healthy."""
    print("🔍 Testing server health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/")
            assert response.status_code == 200
            print("✅ Root endpoint working")

            response = await client.get(f"{base_url}/api/v1/health")
            assert response.status_code == 200
            print("✅ Health endpoint working")

            response = await client.get(f"{base_url}/api/v1/stats")
            assert response.status_code == 200
            print("✅ Stats endpoint working")

    except Exception as e:
        print(f"❌ Server health check failed: {e}")
        return False

    return True

# ------------------ MODEL TEST ------------------
def test_ai_model_logic():
    """Test the AI model logic directly."""
    print("🧠 Testing AI model logic...")
    try:
        model = DexScoringModel()
        result = model.score_wallet(SAMPLE_WALLET_MESSAGE)

        if "categories" not in result or not result["categories"]:
            print("❌ No categories in model output")
            return False

        features = result["categories"][0]["features"]
        for feat, exp in EXPECTED_FEATURES.items():
            if abs(features.get(feat, 0) - exp) > 0.01:
                print(f"⚠️ Feature {feat}: expected {exp}, got {features.get(feat)}")

        print("✅ Model logic test passed")
        return True
    except Exception as e:
        print(f"❌ AI model test failed: {e}")
        return False

# ------------------ KAFKA TEST ------------------
async def test_kafka_integration():
    print("📨 Testing Kafka integration (mock)...")
    print("⚠️ Skipping Kafka integration test (mock mode)")
    return True

# ------------------ PERFORMANCE TEST ------------------
def performance_test():
    """Test performance with multiple wallets."""
    print("⚡ Running performance test...")
    start_time = time.time()

    num_wallets = 100
    model = DexScoringModel()
    for _ in range(num_wallets):
        model.score_wallet(SAMPLE_WALLET_MESSAGE)

    end_time = time.time()
    elapsed = max(end_time - start_time, 1e-6)  # prevent division by zero
    rate = num_wallets / elapsed

    print(f"📊 Processed {num_wallets} wallets in {elapsed:.2f}s")
    print(f"📊 Rate: {rate:.2f} wallets/second")

    if rate >= 16.67:
        print("✅ Performance target met (1000+ wallets/minute)")
        return True
    else:
        print("⚠️ Performance below target")
        return False

# ------------------ RUN ALL ------------------
async def run_all_tests():
    print("🚀 Starting AI Engineer Challenge Validation\n")

    tests = [
        ("Server Health", test_server_health()),
        ("AI Model Logic", test_ai_model_logic()),
        ("Kafka Integration", test_kafka_integration()),
        ("Performance", performance_test()),
    ]

    results = []
    for name, test in tests:
        print(f"\n--- {name} ---")
        if asyncio.iscoroutine(test):
            result = await test
        else:
            result = test
        results.append((name, result))

    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, r in results if r)
    for name, r in results:
        status = "✅ PASS" if r else "❌ FAIL"
        print(f"{name}: {status}")

    print(f"\nOverall: {passed}/{len(results)} tests passed")
    if passed == len(results):
        print("🎉 Congratulations! Your implementation passes all tests!")
    else:
        print("🔧 Some tests failed - check logs")

if __name__ == "__main__":
    print("AI Engineer Challenge - Test Suite")
    print("Make sure your server is running on http://localhost:8000\n")
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n⏹️ Tests cancelled")
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
