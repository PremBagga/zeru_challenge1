# # app/services/kafka_service.py
# import os
# import json
# import threading
# import time
# from typing import Dict, Any, Optional

# from app.models.dex_model import DexScoringModel
# from app.utils.types import FailureMessage, FailureCategory, to_serializable
# from dotenv import load_dotenv
# load_dotenv()

# KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "false").lower() == "true"

# if KAFKA_ENABLED:
#     from kafka import KafkaConsumer, KafkaProducer

# from app.models.dex_model import DexScoringModel

# class KafkaScoringService:
#     def __init__(self, use_kafka: bool = True):
#         self.model = DexScoringModel()
#         self.use_kafka = use_kafka

#         if self.use_kafka:
#             from kafka import KafkaConsumer, KafkaProducer
#             import os
#             self.consumer = KafkaConsumer(
#                 os.getenv("KAFKA_INPUT_TOPIC", "wallet-transactions"),
#                 bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
#                 group_id=os.getenv("KAFKA_CONSUMER_GROUP", "ai-scoring-service")
#             )
#             self.producer = KafkaProducer(
#                 bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
#             )
#         else:
#             # No Kafka → mock mode
#             self.consumer = None
#             self.producer = None

#     def process_message(self, wallet_json: dict):
#         """Process one wallet JSON message and return success/failure result."""
#         try:
#             result = self.model.score_wallet(wallet_json)
#             return {"status": "success", "result": result}
#         except Exception as e:
#             return {
#                 "status": "failure",
#                 "result": {
#                     "wallet_address": wallet_json.get("wallet_address", "unknown"),
#                     "error": str(e),
#                     "timestamp": 0,
#                     "processing_time_ms": 0,
#                     "categories": [{"category": "dexes", "error": str(e), "transaction_count": 0}]
#                 }
#             }
# app/services/kafka_service.py
import os
from queue import Queue
from app.models.dex_model import DexScoringModel

# Load Kafka flag from env
KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "false").lower() == "true"

if KAFKA_ENABLED:
    from kafka import KafkaConsumer, KafkaProducer


class KafkaScoringService:
    def __init__(self):
        self.model = DexScoringModel()
        self.real_mode = KAFKA_ENABLED  # Track if real Kafka is enabled

        if self.real_mode:
            # Real Kafka mode
            self.consumer = KafkaConsumer(
                os.getenv("KAFKA_INPUT_TOPIC", "wallet-transactions"),
                bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
                group_id=os.getenv("KAFKA_CONSUMER_GROUP", "ai-scoring-service"),
            )
            self.producer = KafkaProducer(
                bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
            )
        else:
            # Mock mode with queue
            self.queue = Queue()
            self.consumer = None
            self.producer = None

    def process_message(self, wallet_json: dict):
        """Process one wallet JSON message and return success/failure result."""
        try:
            result = self.model.score_wallet(wallet_json)
            return {"status": "success", "result": result}
        except Exception as e:
            return {
                "status": "failure",
                "result": {
                    "wallet_address": wallet_json.get("wallet_address", "unknown"),
                    "error": str(e),
                    "timestamp": 0,
                    "processing_time_ms": 0,
                    "categories": [
                        {"category": "dexes", "error": str(e), "transaction_count": 0}
                    ],
                },
            }

    # ---------------- MOCK Helpers ----------------
    def mock_send(self, message: dict):
        if not self.real_mode:
            self.queue.put(message)

    def mock_drain(self):
        if not self.real_mode:
            drained = []
            while not self.queue.empty():
                drained.append(self.queue.get())
            return drained
        return []


