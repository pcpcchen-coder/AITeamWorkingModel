---
# 虛構範例資料（fictional）；對應 docs/12 §4
id: WP-001
mission: M-001
title: 量測鏈誤差預算分析
domain: research
executor: ai
agent: researcher
autonomy: A3
gate: G0
review_tier: R1
scope:
  paths: ["hw/calc/**", "knowledge/memory.md"]
satisfies: [REQ-001]
depends_on: []
acceptance:
  - id: AC1
    text: 列出量測鏈各誤差來源（電阻容差、NTC 參數、ADC）及其在 -20～60°C 的貢獻，附可重跑的計算
    verify: {kind: calc, runner: agent, command: "python hw/calc/ntc_divider_worstcase.py", ladder: V2}
budget: {max_iterations: 2, max_agent_minutes: 120}
start_approval: not_required
---

## 背景與目的

找出低溫誤差的主要來源，作為 WP-002 的依據。

## 只能在更高驗證階確認的項目

- 實際誤差需樣板量測（WP-005）。

## 執行日誌（只增不改）

- 2026-11-16 agent:orchestrator 由 Plan 建立（虛構）
