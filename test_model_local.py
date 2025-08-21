from app.models.dex_model import DexScoringModel

# Sample wallet JSON (from the challenge doc)
wallet_json = {
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
                    "tokenIn": {"amount": 1000000000, "amountUSD": 1000.0, "address": "0xa0b8...", "symbol": "USDC"},
                    "tokenOut": {"amount": 500000000000000000, "amountUSD": 1000.0, "address": "0xc02a...", "symbol": "WETH"}
                },
                {
                    "document_id": "507f1f77bcf86cd799439012",
                    "action": "deposit",
                    "timestamp": 1703980900,
                    "caller": "0x742d35Cc6634C0532925a3b8D4C9db96590e4265",
                    "protocol": "uniswap_v3",
                    "poolId": "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640",
                    "poolName": "Uniswap V3 USDC/WETH 0.05%",
                    "token0": {"amount": 500000000, "amountUSD": 500.0, "address": "0xa0b8...", "symbol": "USDC"},
                    "token1": {"amount": 250000000000000000, "amountUSD": 500.0, "address": "0xc02a...", "symbol": "WETH"}
                }
            ]
        }
    ]
}

model = DexScoringModel()
result = model.score_wallet(wallet_json)

print("✅ Model Output:")
print(result)
