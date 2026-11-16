---
# 虛構範例資料（fictional）；對應 docs/12 §4、§8
id: WP-004
mission: M-001
title: 上位機 SOH 低溫補償改用新溫度資料
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G1
review_tier: R2
scope:
  paths: ["sw/**"]
satisfies: [REQ-003]
depends_on: [WP-003]
acceptance:
  - id: AC1
    text: 補償函式的單元測試通過
    verify: {kind: test_run, runner: ci, command: "python -m pytest sw", ladder: V2}
  - id: AC2
    text: 解碼端與 protocol.yaml 的契約測試通過
    verify: {kind: test_run, runner: ci, command: "python -m pytest sw/test_contract.py", ladder: V3}
budget: {max_iterations: 3, max_agent_minutes: 180}
start_approval: not_required
---

## 背景與目的

純軟體、可完全自動驗證的快速通道（docs/12 §8）。

## 執行日誌（只增不改）

- 2026-11-16 agent:orchestrator 由 Plan 建立（虛構）
