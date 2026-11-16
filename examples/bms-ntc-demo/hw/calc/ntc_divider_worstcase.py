#!/usr/bin/env python3
"""NTC 上拉分壓的最壞情況分析 — 虛構範例（fictional）。

參數取自 knowledge/interfaces/analog.yaml（介面契約正本）；只有上拉電阻值可由
--candidates 覆寫，用來比較候選值。所有數值皆為虛構，不是任何真實元件的規格。

對每個候選上拉電阻、每個溫度點：
  * 靈敏度：每 °C 對應的 ADC 讀值變化（counts/°C）；
  * 最壞情況誤差：上拉容差、R25 容差、Beta 容差、ADC 誤差四者的全部極值組合（16 組），
    以「標稱參數」把受擾動的讀值反推回溫度，取與真實溫度的最大偏差。
ADC 為比例式量測（參考電壓與分壓電源同源），參考電壓誤差相消，故不列入。

輸出為確定性文字（相同輸入 → 相同輸出），結束碼：0 正常、2 參數錯誤。
"""

from __future__ import annotations

import argparse
import itertools
import math
import sys
from pathlib import Path

import yaml

T0_K = 273.15
T25_K = 298.15
PROJECT = Path(__file__).resolve().parents[2]
ANALOG = PROJECT / "knowledge" / "interfaces" / "analog.yaml"
REPORT_TEMPS = (-20, -10, 0, 10, 25, 40, 60)


def r_ntc(t_c: float, r25: float, beta: float) -> float:
    return r25 * math.exp(beta * (1.0 / (t_c + T0_K) - 1.0 / T25_K))


def adc_counts(t_c: float, pullup: float, r25: float, beta: float, full: int) -> float:
    r = r_ntc(t_c, r25, beta)
    return full * r / (r + pullup)


def counts_to_temp(counts: float, pullup: float, r25: float, beta: float, full: int) -> float:
    ratio = min(max(counts / full, 1e-9), 1 - 1e-9)
    r = pullup * ratio / (1.0 - ratio)
    return 1.0 / (1.0 / T25_K + math.log(r / r25) / beta) - T0_K


def parse_ohms(text: str) -> float:
    t = text.strip().lower()
    mult = 1.0
    if t.endswith("k"):
        mult, t = 1e3, t[:-1]
    elif t.endswith("m"):
        mult, t = 1e6, t[:-1]
    value = float(t) * mult
    if value <= 0:
        raise ValueError(text)
    return value


def analyse(pullup: float, p: dict) -> list[tuple[int, float, float]]:
    ntc, div, adc = p["ntc"], p["divider"], p["adc"]
    r25, beta = float(ntc["r25_ohm"]), float(ntc["beta_k"])
    full = 2 ** int(adc["bits"]) - 1
    tol = (div["pullup_tolerance_pct"] / 100, ntc["r25_tolerance_pct"] / 100, ntc["beta_tolerance_pct"] / 100)
    lsb = float(adc["error_lsb"])
    rows = []
    for t in REPORT_TEMPS:
        sens = abs(adc_counts(t + 0.5, pullup, r25, beta, full) - adc_counts(t - 0.5, pullup, r25, beta, full))
        worst = 0.0
        for sp, sr, sb, se in itertools.product((-1, 1), repeat=4):
            c = adc_counts(t, pullup * (1 + sp * tol[0]), r25 * (1 + sr * tol[1]), beta * (1 + sb * tol[2]), full)
            est = counts_to_temp(c + se * lsb, pullup, r25, beta, full)
            worst = max(worst, abs(est - t))
        rows.append((t, sens, worst))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="NTC 上拉分壓最壞情況分析（虛構範例）")
    ap.add_argument("--candidates", default=None, help="候選上拉電阻，逗號分隔，例：10k,22k,33k（預設：analog.yaml 的值）")
    args = ap.parse_args(argv)
    params = yaml.safe_load(ANALOG.read_text(encoding="utf-8"))
    try:
        cands = ([parse_ohms(c) for c in args.candidates.split(",")] if args.candidates
                 else [float(params["divider"]["pullup_ohm"])])
    except ValueError as exc:
        print(f"參數錯誤：無法解析電阻值 {exc}；修正：使用如 10k、22000 的格式", file=sys.stderr)
        return 2

    print("NTC 上拉分壓最壞情況分析（虛構範例資料；不是量測結果）")
    print(f"來源參數：{ANALOG.relative_to(PROJECT).as_posix()}（version {params['version']}）")
    print("誤差組合：上拉、R25、Beta 容差與 ADC 誤差的全部極值（16 組）；比例式 ADC，參考電壓誤差相消")
    for pullup in cands:
        print(f"\n上拉 {pullup / 1000:g}k")
        print(f"{'溫度°C':>7} {'counts/°C':>10} {'最壞誤差°C':>11}")
        for t, sens, worst in analyse(pullup, params):
            print(f"{t:>7d} {sens:>10.2f} {worst:>11.3f}")
        low = [w for t, _, w in analyse(pullup, params) if -20 <= t <= 60]
        print(f"-20～60°C 範圍最大誤差：{max(low):.3f} °C")
    return 0


if __name__ == "__main__":
    sys.exit(main())
