"""低溫 SOH 補償 — 虛構範例（fictional）。係數為示範用虛構值，不是任何電池的特性。"""

from __future__ import annotations

REFERENCE_C = 25.0
LOW_TEMP_KNEE_C = 10.0
COEFF_PER_C = 0.004       # 虛構：膝點以下每 °C 修正 0.4 %


def compensate_soh(raw_soh: float, temp_c: float) -> float:
    """把在 temp_c 下估得的 SOH（0–1）修正回參考溫度；膝點以上不修正。"""
    if not 0.0 <= raw_soh <= 1.0:
        raise ValueError(f"raw_soh 必須在 0～1 之間，收到 {raw_soh}")
    if temp_c >= LOW_TEMP_KNEE_C:
        return raw_soh
    factor = 1.0 + COEFF_PER_C * (LOW_TEMP_KNEE_C - temp_c)
    return min(1.0, raw_soh * factor)
