---
# 虛構範例資料（fictional）；對應 docs/12 §4、§5
id: WP-002
mission: M-001
title: 上拉電阻值的最壞情況計算與模擬；更新類比介面契約
domain: hw
executor: ai
agent: engineer-hw
autonomy: A2
gate: G2
review_tier: R2
scope:
  paths: ["hw/calc/**", "hw/sim/**", "knowledge/interfaces/analog.yaml"]
satisfies: [REQ-001]
depends_on: [WP-001]
acceptance:
  - id: AC1
    text: 候選上拉電阻 10k／22k／33k 的最壞情況誤差與每 °C 解析度，以可重跑的腳本計算
    verify: {kind: calc, runner: ci, command: "python hw/calc/ntc_divider_worstcase.py --candidates 10k,22k,33k", ladder: V2}
  - id: AC2
    text: 選定候選值的分壓電路模擬（選用配方：需外部電路模擬器；本範例尚未提供 hw/sim）
    verify: {kind: sim, runner: agent, command: "make -C hw/sim run", ladder: V3}
  - id: AC3
    text: analog.yaml 更新後由 hw、fw、sw owner 審查（跨領域介面變更）
    verify: {kind: doc, runner: human, ladder: V1}
budget: {max_iterations: 3, max_agent_minutes: 240}
start_approval: not_required
---

## 背景與目的

依 WP-001 的結論比較上拉電阻候選值；選值以決策請求交由人類決定（docs/12 §5.2）。

## 只能在更高驗證階確認的項目

- 低溫段 NTC 容差為外推假設；需 WP-005 實測。

## 執行日誌（只增不改）

- 2026-11-16 agent:orchestrator 由 Plan 建立（虛構）
