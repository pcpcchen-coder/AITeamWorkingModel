---
# 虛構範例資料（fictional）；對應 docs/12 §4、§7。本工作包是人類任務：AI 只準備程序與分析資料。
id: WP-005
mission: M-001
title: 樣板改裝與三點溫度量測
domain: hw
executor: human
autonomy: A1
gate: G3
review_tier: R3
scope:
  paths: ["work/missions/M-001-low-temp-accuracy/wp/WP-005-bench-measurement/**"]
satisfies: [REQ-001, S1]
depends_on: [WP-002, WP-003]
acceptance:
  - id: AC1
    text: 樣板在低溫、常溫、高溫三點的量測誤差，附待測物、儀器校正編號、執行者與原始資料雜湊
    verify: {kind: measurement, runner: human, ladder: V4}
budget: {max_iterations: 2, max_agent_minutes: 60}
start_approval: required
---

## 背景與目的

驗證 S1。三點（低／常溫／高）是最小集合；是否加中間點由 primary-a 決定（docs/12 §4）。

## 只能在更高驗證階確認的項目

- 本工作包即 V4；長時間與環境測試（V5）不在本 Mission 範圍。

## 執行日誌（只增不改）

- 2026-11-16 agent:orchestrator 由 Plan 建立（虛構）
