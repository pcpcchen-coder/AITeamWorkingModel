"""cell_temperature 訊框解碼 — 虛構範例（fictional）。

欄位定義的正本是 knowledge/interfaces/protocol.yaml；test_contract.py 檢查兩者一致。
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

FRAME_ID = 0x310
FRAME_LENGTH = 3
TEMP_OFFSET = 0
TEMP_SCALE = 0.1          # temp_decic × 0.1 = °C
STATUS_OFFSET = 2
STATUS_OK = 0


class FrameError(ValueError):
    """訊框長度或內容不符合介面契約。"""


@dataclass(frozen=True)
class CellTemperature:
    temp_c: float
    status: int


def decode_cell_temperature(payload: bytes) -> CellTemperature:
    if len(payload) != FRAME_LENGTH:
        raise FrameError(f"cell_temperature 長度應為 {FRAME_LENGTH} bytes，收到 {len(payload)}")
    (decic,) = struct.unpack_from("<h", payload, TEMP_OFFSET)
    status = payload[STATUS_OFFSET]
    return CellTemperature(temp_c=round(decic * TEMP_SCALE, 1), status=status)
