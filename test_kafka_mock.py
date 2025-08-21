# from app.services.kafka_service import KafkaScoringService


# wallet_json = {
#     "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96590e4265",
#     "data": [
#         {
#             "protocolType": "dexes",
#             "transactions": [
#                 {
#                     "action": "swap",
#                     "tokenIn": {"amountUSD": 1000.0},
#                     "tokenOut": {"amountUSD": 1000.0}
#                 },
#                 {
#                     "action": "deposit",
#                     "token0": {"amountUSD": 500.0},
#                     "token1": {"amountUSD": 500.0}
#                 }
#             ]
#         }
#     ]
# }

# # Run in mock mode (no Kafka)
# service = KafkaScoringService(use_kafka=False)
# status, result = service.process_message(wallet_json)

# print(f"Status: {status}")
# print("Result:", result)

# test_kafka_mock.py
import time
from app.services.kafka_service import KafkaScoringService

# ✅ Sample input JSON (taken from challenge statement)
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
                    "tokenIn": {
                        "amount": 1000000000,
                        "amountUSD": 1000.0,
                        "address": "0xa0b86a33e6c3d4c3e6c3d4c3e6c3d4c3e6c3d4c3",
                        "symbol": "USDC"
                    },
                    "tokenOut": {
                        "amount": 500000000000000000,
                        "amountUSD": 1000.0,
                        "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                        "symbol": "WETH"
                    }
                },
                {
                    "document_id": "507f1f77bcf86cd799439012",
                    "action": "deposit",
                    "timestamp": 1703980900,
                    "caller": "0x742d35Cc6634C0532925a3b8D4C9db96590e4265",
                    "protocol": "uniswap_v3",
                    "poolId": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
                    "poolName": "Uniswap V3 USDC/WETH 0.05%",
                    "token0": {
                        "amount": 500000000,
                        "amountUSD": 500.0,
                        "address": "0xa0b86a33e6c3d4c3e6c3d4c3e6c3d4c3e6c3d4c3",
                        "symbol": "USDC"
                    },
                    "token1": {
                        "amount": 250000000000000000,
                        "amountUSD": 500.0,
                        "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
                        "symbol": "WETH"
                    }
                }
            ]
        }
    ]
}

if __name__ == "__main__":
    # ✅ Initialize service in MOCK MODE (no Kafka required)
    service = KafkaScoringService(use_kafka=False)

    start = time.time()
    result = service.process_message(SAMPLE_WALLET_MESSAGE)
    end = time.time()

    print("Status:", result["status"])
    print("Processing Time:", round((end - start) * 1000, 2), "ms")
    print("Result:", result["result"])
