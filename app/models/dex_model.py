# app/models/dex_model.py
from __future__ import annotations
from typing import Dict, Any, List, Tuple, DefaultDict
from collections import defaultdict
import time
from decimal import Decimal, ROUND_DOWN

from app.utils.types import WalletMessage, CategoryFeatures, CategoryScore, SuccessMessage, FailureMessage

class DexScoringModel:
    """
    Minimal but production-friendly scorer:
    - Extracts DEX features (deposits/withdrawals/swaps, volumes, unique pools)
    - Estimates avg hold time (pairing deposits->withdraws by pool where possible)
    - Builds LP + Swap sub-scores and combines into 0..1000 'zscore'
    """

    def _safe(self, x, default=0.0):
        return float(x) if isinstance(x, (int, float)) else default

    def _extract_features(self, pd: Dict[str, Any]) -> Tuple[CategoryFeatures, int]:
        txs = pd.get("transactions", [])
        pools_seen = set()

        total_deposit_usd = 0.0
        total_withdraw_usd = 0.0
        total_swap_volume = 0.0
        num_deposits = num_withdraws = num_swaps = 0

        # hold time estimation: deposit times per pool, withdraw times per pool
        deposits_by_pool: DefaultDict[str, List[int]] = defaultdict(list)
        withdraws_by_pool: DefaultDict[str, List[int]] = defaultdict(list)

        for t in txs:
            action = (t.get("action") or "").lower()
            pool_id = t.get("poolId") or ""
            ts = int(t.get("timestamp") or 0)
            if pool_id:
                pools_seen.add(pool_id)

            if action == "swap":
                num_swaps += 1
                vin = self._safe(t.get("tokenIn", {}).get("amountUSD"))
                vout = self._safe(t.get("tokenOut", {}).get("amountUSD"))
                # count volume as average of legs if both present, else either
                volume = vout if vin == 0 and vout > 0 else vin if vout == 0 and vin > 0 else (vin + vout) / 2.0
                total_swap_volume += volume

            elif action == "deposit":
                num_deposits += 1
                usd0 = self._safe(t.get("token0", {}).get("amountUSD"))
                usd1 = self._safe(t.get("token1", {}).get("amountUSD"))
                total_deposit_usd += (usd0 + usd1)
                if pool_id and ts:
                    deposits_by_pool[pool_id].append(ts)

            elif action == "withdraw":
                num_withdraws += 1
                usd0 = self._safe(t.get("token0", {}).get("amountUSD"))
                usd1 = self._safe(t.get("token1", {}).get("amountUSD"))
                total_withdraw_usd += (usd0 + usd1)
                if pool_id and ts:
                    withdraws_by_pool[pool_id].append(ts)

        # avg hold time: greedily pair earliest deposit with next withdraw per pool
        hold_days_list: List[float] = []
        for pool, dlist in deposits_by_pool.items():
            dlist = sorted(dlist)
            wlist = sorted(withdraws_by_pool.get(pool, []))
            i = j = 0
            while i < len(dlist) and j < len(wlist):
                if wlist[j] >= dlist[i]:
                    delta_days = (wlist[j] - dlist[i]) / 86400.0
                    hold_days_list.append(delta_days)
                    i += 1
                    j += 1
                else:
                    j += 1
        avg_hold_days = sum(hold_days_list) / len(hold_days_list) if hold_days_list else 0.0

        features = CategoryFeatures(
            total_deposit_usd=round(total_deposit_usd, 6),
            total_withdraw_usd=round(total_withdraw_usd, 6),
            total_swap_volume=round(total_swap_volume, 6),
            num_deposits=num_deposits,
            num_withdraws=num_withdraws,
            num_swaps=num_swaps,
            avg_hold_time_days=round(avg_hold_days, 6),
            unique_pools=len(pools_seen),
        )
        return features, len(txs)

    def _score_lp(self, f: CategoryFeatures) -> float:
        # simple heuristics
        base = 0.0
        base += min(f.total_deposit_usd / 1000.0, 1.0) * 500  # up to 500
        base += min(f.avg_hold_time_days / 30.0, 1.0) * 300  # up to 300
        # withdraw penalty if churny
        churn = 0.0 if f.total_deposit_usd == 0 else min(f.total_withdraw_usd / max(f.total_deposit_usd, 1.0), 1.0)
        base += (1.0 - churn) * 200  # retainers score higher
        return max(0.0, min(1000.0, base))

    def _score_swap(self, f: CategoryFeatures) -> float:
        base = 0.0
        base += min(f.total_swap_volume / 2000.0, 1.0) * 700  # up to 700
        base += min(f.num_swaps / 10.0, 1.0) * 200           # up to 200
        base += min(f.unique_pools / 3.0, 1.0) * 100         # up to 100
        return max(0.0, min(1000.0, base))

    def _to_zstr(self, val: float) -> str:
        # 18 decimal places as string
        return str(Decimal(val).quantize(Decimal("0.000000000000000001"), rounding=ROUND_DOWN))

    def score_wallet(self, wallet_json: Dict[str, Any]) -> Dict[str, Any]:
        t0 = time.time()
        wallet = WalletMessage(**wallet_json)
        out_categories: List[CategoryScore] = []

        for block in wallet.data:
            if block.protocolType.lower() != "dexes":
                # skip unsupported categories for now
                continue

            features, tx_count = self._extract_features(block.dict())
            # combine LP and Swap
            lp = self._score_lp(features)
            sw = self._score_swap(features)
            combined = (0.5 * lp + 0.5 * sw)  # equal weights

            out_categories.append(
                CategoryScore(
                    category="dexes",
                    score=round(combined, 6),
                    transaction_count=tx_count,
                    features=features
                )
            )

        final = sum(c.score for c in out_categories) / len(out_categories) if out_categories else 0.0

        resp = SuccessMessage(
            wallet_address=wallet.wallet_address,
            zscore=self._to_zstr(final),
            timestamp=int(time.time()),
            processing_time_ms=int((time.time() - t0) * 1000),
            categories=out_categories
        ).dict()

        # ensure plain JSON types
        return resp
