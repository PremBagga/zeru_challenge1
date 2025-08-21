# app/main.py
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models.dex_model import DexScoringModel
from app.utils.types import WalletMessage, to_serializable
from app.services.kafka_service import KafkaScoringService, KAFKA_ENABLED

app = FastAPI(title="AI Scoring Server", version="1.0.0")

# Allow CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Model + stats
model = DexScoringModel()
stats = {"processed": 0, "success": 0, "failure": 0, "avg_ms": 0.0}

# Kafka service (lazy init)
kafka: KafkaScoringService | None = None


@app.on_event("startup")
def on_startup():
    """
    Start Kafka service only if enabled.
    """
    global kafka
    kafka = KafkaScoringService()
    if kafka.real_mode:   # Only start threads if real Kafka mode
        kafka.start()


@app.on_event("shutdown")
def on_shutdown():
    """
    Stop Kafka service cleanly.
    """
    global kafka
    if kafka:
        kafka.stop()


@app.get("/")
def root():
    return {"service": "AI Scoring Server", "version": "1.0.0"}


@app.get("/api/v1/health")
def health():
    """
    Health check.
    """
    return {"status": "ok", "kafka_enabled": KAFKA_ENABLED}


@app.get("/api/v1/stats")
def get_stats():
    """
    Return processing statistics.
    """
    return stats


@app.post("/api/v1/score")
def score_wallet(payload: WalletMessage):
    """
    Score a wallet request directly via API.
    """
    t0 = time.time()
    try:
        result = model.score_wallet(payload.dict())
        ms = int((time.time() - t0) * 1000)
        result["processing_time_ms"] = ms

        # update stats
        stats["processed"] += 1
        stats["success"] += 1
        n = stats["success"] + stats["failure"]
        stats["avg_ms"] = (stats["avg_ms"] * (n - 1) + ms) / max(n, 1)

        return to_serializable(result)
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        stats["processed"] += 1
        stats["failure"] += 1
        raise HTTPException(status_code=400, detail=str(e))


# ---------------- MOCK KAFKA CONTROL ---------------- #

@app.post("/api/v1/kafka/publish")
def kafka_publish(payload: WalletMessage):
    """
    Queue a message into the mock Kafka service.
    Only works if Kafka is disabled (mock mode).
    """
    if not kafka or kafka.real_mode:
        raise HTTPException(status_code=400, detail="Kafka mock publish only available in MOCK mode")
    kafka.mock_send(payload.dict())
    return {"status": "queued"}


@app.get("/api/v1/kafka/drain")
def kafka_drain():
    """
    Drain all queued mock Kafka messages.
    Only works if Kafka is disabled (mock mode).
    """
    if not kafka or kafka.real_mode:
        raise HTTPException(status_code=400, detail="Kafka mock drain only available in MOCK mode")
    return kafka.mock_drain()


# Run locally:
# uvicorn app.main:app --reload --port 8000
# Docs: http://127.0.0.1:8000/docs
