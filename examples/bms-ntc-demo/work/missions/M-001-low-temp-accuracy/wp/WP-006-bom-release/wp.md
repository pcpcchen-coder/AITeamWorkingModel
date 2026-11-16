---
# 虛構範例資料（fictional）；對應 docs/12 §4。不可逆動作：R3 會議審查、兩位人類核准。
id: WP-006
mission: M-001
title: 改版 BOM 釋出
domain: hw
executor: pair
agent: engineer-hw
autonomy: A0
gate: G3
review_tier: R3
scope:
  paths: ["hw/release/**"]
satisfies: [REQ-001]
depends_on: [WP-005]
acceptance:
  - id: AC1
    text: 硬體釋出檢查表（hw-release-g3）全項填寫結果與依據，兩位人類核准
    verify: {kind: checklist, runner: human, ladder: V4}
budget: {max_iterations: 2, max_agent_minutes: 60}
start_approval: required
---

## 背景與目的

在 WP-005 量測確認後釋出改版 BOM。

## 執行日誌（只增不改）

- 2026-11-16 agent:orchestrator 由 Plan 建立（虛構）
