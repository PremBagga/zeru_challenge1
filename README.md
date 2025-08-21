# 🚀 AI Scoring Server – DeFi Wallet Reputation (DEX)

A **production-ready FastAPI microservice** for **DeFi wallet reputation scoring**.
This service consumes wallet transaction data (DEX activity), extracts meaningful features, computes a **risk/reputation z-score (0–1000)**, and returns results in the required JSON format.

Built as part of the **AI Engineer Challenge**.

---

## 📖 Project Card

| **Category**           | **Details**                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------ |
| **Project Name**       | AI Scoring Server – DeFi Reputation (DEX)                                            |
| **Tech Stack**         | Python 3.11+, FastAPI, Pydantic, Pandas, NumPy, Kafka , MongoDB                      |
| **Core Features**      | FastAPI microservice, AI scoring model, DEX feature engineering, Mock Kafka mode     |
| **Input Format**       | Wallet JSON (transactions with swap/deposit/withdraw)                                |
| **Output Format**      | JSON success (score + features) or failure (error message)                           |
| **Score Range**        | 0 – 1000 (string, normalized)                                                        |
| **Kafka Support**      | ✅ Real Kafka integration (if enabled) / Mock mode (local dev)                       |
| **Environment Config** | `.env` file with Kafka/Mongo settings                                                |
| **Tests Provided**     | Local model test, Kafka mock test, End-to-end challenge validation script            |
| **Status**             | ✅ Completed for AI Engineer Challenge                                               |

---

## 📂 Project Structure

```
ai-scoring-server/
├─ app/
│  ├─ main.py                      # FastAPI entrypoint + endpoints
│  ├─ models/
│  │  └─ dex_model.py              # DEX scoring logic (features + zscore)
│  ├─ services/
│  │  └─ kafka_service.py          # Kafka (real or mock) wrapper
│  ├─ utils/
│  │  ├─ __init__.py
│  │  └─ types.py                  # Pydantic models, serializers
│  └─ __init__.py
├─ test_model_local.py             # Direct model test (no server)
├─ test_kafka_mock.py              # Kafka service test (mock mode)
├─ test_challenge.py               # End-to-end validation script
├─ requirements.txt
├─ .env.example                    # Env template
└─ README.md
```

---

## ⚡ Setup & Quickstart (Local Mode – No Kafka Required)

> Works on **Windows / macOS / Linux**. Requires **Python 3.11+**.

### 1️⃣ Create & activate virtual environment

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Copy environment file

```bash
cp .env.example .env
```

➡️ Ensure `KAFKA_ENABLED=false`

### 4️⃣ Run the FastAPI server

```bash
uvicorn app.main:app --reload --port 8000
```

### 5️⃣ Open API Docs

Go to 👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
You will see:

* `/api/v1/health` → Health check
* `/api/v1/score` → Scoring endpoint
* `/api/v1/stats` → Stats

---

## 🔌 API Endpoints

### Root

**GET /**

```json
{ "service": "AI Scoring Server", "version": "1.0.0" }
```

### Health Check

**GET /api/v1/health**

```json
{ "status": "ok", "kafka_enabled": false }
```

### Score Wallet

**POST /api/v1/score**
📥 Input:

```json
{
  "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96590e4265",
  "data": [
    {
      "protocolType": "dexes",
      "transactions": [
        {
          "action": "swap",
          "timestamp": 1703980800,
          "tokenIn": { "amountUSD": 1000.0 },
          "tokenOut": { "amountUSD": 1000.0 }
        },
        {
          "action": "deposit",
          "timestamp": 1703980900,
          "token0": { "amountUSD": 500.0 },
          "token1": { "amountUSD": 500.0 }
        }
      ]
    }
  ]
}
```

📤 Output:

```json
{
  "wallet_address": "0x742d35Cc6634C0532925a3b8D4C9db96590e4265",
  "zscore": "732.0",
  "timestamp": 1703980800,
  "processing_time_ms": 52,
  "categories": [
    {
      "category": "dexes",
      "score": 732,
      "transaction_count": 2,
      "features": {
        "total_deposit_usd": 1000,
        "total_swap_volume": 1000,
        "num_deposits": 1,
        "num_swaps": 1,
        "avg_hold_time_days": 0,
        "unique_pools": 1
      }
    }
  ]
}
```

---

## 🧠 Scoring Logic

**Feature Engineering:**

* Total deposits (USD)
* Total withdraws (USD)
* Swap volume (USD)
* Transaction counts: deposits, withdraws, swaps
* Pool diversity (`unique_pools`)
* Holding time (stubbed as `0` in local mode)

**Scoring Algorithm:**

1. Compute **LP score** (deposits/withdraws).
2. Compute **Swap score** (volume + frequency).
3. Weighted aggregation → final z-score (0–1000).
4. Output normalized **string** zscore.

---

## 🧪 Testing

### Local model

```bash
python test_model_local.py
```

### Kafka mock

```bash
python test_kafka_mock.py
```

### End-to-end challenge validation

Start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

Run tests:

```bash
python test_challenge.py
```

---

## 📝 Deliverables

✅ AI scoring FastAPI server
✅ Local dev mode (no Kafka required)
✅ Feature extraction + zscore (0–1000)
✅ JSON success/failure outputs
✅ End-to-end test validation

---

