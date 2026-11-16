---
# 虛構範例資料（fictional）；對應 docs/12 §4、§6
id: WP-003
mission: M-001
title: 韌體改用由介面契約產生的查表內插換算溫度
domain: fw
executor: ai
agent: engineer-fw
autonomy: A2
gate: G1
review_tier: R2
scope:
  paths: ["fw/src/**", "fw/include/**", "fw/tests/**", "fw/tools/**"]
satisfies: [REQ-002]
depends_on: [WP-002]
acceptance:
  - id: AC1
    text: 主機端單元測試通過，全量程換算誤差在表格內插誤差內
    verify: {kind: test_run, runner: ci, command: "make -C fw test", ladder: V2}
  - id: AC2
    text: 程式大小在預算內（主機端大小報告；目標板用量為選用配方）
    verify: {kind: size_report, runner: ci, command: "make -C fw size", ladder: V2}
  - id: AC3
    text: 表格端點與超出範圍的行為有測試（Plan 審查時 primary-a 要求加入）
    verify: {kind: test_run, runner: ci, command: "make -C fw test", ladder: V2}
budget: {max_iterations: 3, max_agent_minutes: 240}
start_approval: not_required
---

## 背景與目的

以 analog.yaml 產生查表，取代現行換算。

## 只能在更高驗證階確認的項目

- ADC 取樣雜訊與濾波效果、實際轉換時間（需實機，WP-005）。

## 執行日誌（只增不改）

- 2026-11-16 agent:orchestrator 由 Plan 建立（虛構）
