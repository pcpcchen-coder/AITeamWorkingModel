---
# 虛構測試資料（fictional test data）
id: WP-001
mission: M-001
title: 虛構工作包：換算函式
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G1
review_tier: R2
scope:
  paths: ["sw/convert/**"]
satisfies: [REQ-001]
depends_on: []
acceptance:
  - id: AC1
    text: 換算函式的單元測試通過
    verify: {kind: test_run, runner: ci, command: "python -m pytest sw/convert", ladder: V2}
  - id: AC2
    text: 人類確認輸出格式
    verify: {kind: doc, runner: human, ladder: V1}
budget: {max_iterations: 3, max_agent_minutes: 120}
start_approval: not_required
---

## 背景與目的

虛構測試資料。

## 執行日誌（只增不改）

- 2026-01-01 agent:engineer-sw 虛構紀錄
