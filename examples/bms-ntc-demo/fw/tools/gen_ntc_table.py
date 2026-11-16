#!/usr/bin/env python3
"""由 knowledge/interfaces/analog.yaml 產生 fw/include/ntc_table_data.h — 虛構範例（fictional）。

用法（repo 根目錄）：python examples/bms-ntc-demo/fw/tools/gen_ntc_table.py
產生檔已提交；介面契約變更後須重新產生（一致性檢查見工單 K5）。輸出為確定性。
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parents[2]
ANALOG = PROJECT / "knowledge" / "interfaces" / "analog.yaml"
OUT = PROJECT / "fw" / "include" / "ntc_table_data.h"
STEP_C = 5


def main() -> int:
    p = yaml.safe_load(ANALOG.read_text(encoding="utf-8"))
    r25, beta = float(p["ntc"]["r25_ohm"]), float(p["ntc"]["beta_k"])
    pullup, full = float(p["divider"]["pullup_ohm"]), 2 ** int(p["adc"]["bits"]) - 1
    lo, hi = int(p["range_degc"]["min"]), int(p["range_degc"]["max"])
    rows = []
    for t in range(lo, hi + 1, STEP_C):
        r = r25 * math.exp(beta * (1.0 / (t + 273.15) - 1.0 / 298.15))
        rows.append((round(full * r / (r + pullup)), t * 10))
    body = "\n".join(f"    {{{adc:4d}, {decic:5d}}}," for adc, decic in rows)
    OUT.write_text(f"""/* 產生檔，請勿手改 — 虛構範例資料（fictional）。
 * 來源：knowledge/interfaces/analog.yaml version {p['version']}
 * 產生：python examples/bms-ntc-demo/fw/tools/gen_ntc_table.py
 * 上拉 {pullup:g} Ω、R25 {r25:g} Ω、Beta {beta:g} K、ADC {p['adc']['bits']} bit；每 {STEP_C}°C 一點。
 * ADC 讀值隨溫度上升而遞減（NTC 接地端）。
 */
#ifndef NTC_TABLE_DATA_H
#define NTC_TABLE_DATA_H

#define NTC_TABLE_LEN {len(rows)}

static const ntc_point_t NTC_TABLE[NTC_TABLE_LEN] = {{
{body}
}};

#endif /* NTC_TABLE_DATA_H */
""", encoding="utf-8")
    print(f"已產生 {OUT.relative_to(PROJECT).as_posix()}（{len(rows)} 點）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
