---
id: WP-008
mission: M-001
title: K6 — 節奏與指標（digest、sync agenda、metrics、aitw-cadence）
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G1                      # docs/13 §3 K6 宣告值
review_tier: R2
scope:
  paths:
    - "packages/aitw/**"
    - "kit/forge/github/**"           # aitw-cadence workflow 範本
    - "kit/forge/gitlab/**"           # 對應的排程 pipeline 範本
    - "examples/bms-ntc-demo/**"
    - "docs/11-toolkit-spec.md"
satisfies: [S2]
depends_on: [WP-005]
acceptance:
  # 來源：docs/13 §3 K6「驗收」原文（一句拆成四條，內容未增減）
  - id: AC1
    text: "無重大變更時週摘要輸出「無」而非湊數。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp008_ac1"
      ladder: V2
  - id: AC2
    text: "摘要每條附來源。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp008_ac2"
      ladder: V2
  - id: AC3
    text: "09 §13 的每個指標有計算測試。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp008_ac3"
      ladder: V2
  - id: AC4
    text: "議程五段齊全。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp008_ac4"
      ladder: V2
budget:
  max_iterations: 3
  max_agent_minutes: 240        # 規模 S；試行假設
start_approval: not_required
---

## 背景與目的

讓 Backup 以低負擔跟上（週摘要）、讓每週共讀共推會有確定性的議程，並以事實計算 09 §13 的指標（I9）。

## 作法

- 1 個 PR：`wp/WP-008-cadence`。
- 指標全部由 git／forge 事實計算，每項輸出附計算來源；不接受模型填寫的數值。
- `aitw-cadence` 範本只產生骨架並開 PR；排程權限以最小權限設計。

## 只能在更高驗證階確認的項目

- 摘要選項排序是否符合人類直覺（需試點）。

## 人類必看

- docs/13 K6 未列人類必看項目；建議審閱指標定義與計算來源。

## 完成定義（docs/13 §4）

- [ ] 驗收條件逐條對應到測試或標示的人工驗證
- [ ] PR 附實際執行的指令與輸出；未執行者標 NOT RUN
- [ ] 不變量 I1–I10 無一被破壞
- [ ] 相關文件已同步（11、12 與實作一致）
- [ ] 範例與測試資料皆為虛構
- [ ] 共讀包列出未驗證範圍與後續建議
- [ ] 經人類核准後合併

## 執行日誌（只增不改）

- 2026-11-13 agent:engineer-sw 由 docs/13 §3 K6 轉寫本 WP。
