# app/utils/types.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
import numpy as np
from decimal import Decimal

# -------- Input models --------
class TokenAmount(BaseModel):
    amount: Optional[float] = None
    amountUSD: Optional[float] = None
    address: Optional[str] = None
    symbol: Optional[str] = None

class Transaction(BaseModel):
    document_id: Optional[str]
    action: str
    timestamp: int
    caller: Optional[str]
    protocol: Optional[str]
    poolId: Optional[str] = None
    poolName: Optional[str] = None

    # swap fields
    tokenIn: Optional[TokenAmount] = None
    tokenOut: Optional[TokenAmount] = None

    # lp fields
    token0: Optional[TokenAmount] = None
    token1: Optional[TokenAmount] = None

class ProtocolData(BaseModel):
    protocolType: str
    transactions: List[Transaction] = Field(default_factory=list)

class WalletMessage(BaseModel):
    wallet_address: str
    data: List[ProtocolData]

# -------- Output models --------
class CategoryFeatures(BaseModel):
    total_deposit_usd: float = 0.0
    total_withdraw_usd: float = 0.0
    total_swap_volume: float = 0.0
    num_deposits: int = 0
    num_withdraws: int = 0
    num_swaps: int = 0
    avg_hold_time_days: float = 0.0
    unique_pools: int = 0

class CategoryScore(BaseModel):
    category: str
    score: float
    transaction_count: int
    features: CategoryFeatures

class SuccessMessage(BaseModel):
    wallet_address: str
    zscore: str  # string with decimals
    timestamp: int
    processing_time_ms: int
    categories: List[CategoryScore]

class FailureCategory(BaseModel):
    category: str
    error: str
    transaction_count: int = 0

class FailureMessage(BaseModel):
    wallet_address: str
    error: str
    timestamp: int
    processing_time_ms: int
    categories: List[FailureCategory] = Field(default_factory=list)

# -------- utils --------
def to_serializable(obj: Any):
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_serializable(v) for v in obj]
    return obj
