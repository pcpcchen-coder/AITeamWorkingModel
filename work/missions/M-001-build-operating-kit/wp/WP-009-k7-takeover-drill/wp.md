---
id: WP-009
mission: M-001
title: K7 — 接手演練（takeover pack|start|submit|grade）
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G1                      # docs/13 §3 K7 宣告值
review_tier: R2
scope:
  paths:
    - "packages/aitw/**"
    - "examples/bms-ntc-demo/**"
    - "kit/templates/takeover-package.md"
    - "docs/11-toolkit-spec.md"
satisfies: [S2]
depends_on: [WP-005]
acceptance:
  # 來源：docs/13 §3 K7「驗收」原文（一句拆成四條，內容未增減）
  - id: AC1
    text: "接手包含 02 §6 的七項，缺少者標 UNKNOWN。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp009_ac1"
      ladder: V2
  - id: AC2
    text: "計時與求助紀錄可查。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp009_ac2"
      ladder: V2
  - id: AC3
    text: "評級只能由 config 中的 reviewer 登錄、不可為受測者本人。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp009_ac3"
      ladder: V2
  - id: AC4
    text: "L2／L3 必須引用演練證據。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp009_ac4"
      ladder: V2
budget:
  max_iterations: 3
  max_agent_minutes: 240        # 規模 S；試行假設
start_approval: not_required
---

## 背景與目的

讓接手能力以演練證據評定（docs/02 §6、docs/09 §6.3），而不是以「已讀」代替。

## 作法

- 1 個 PR：`wp/WP-009-takeover`。
- 評級登錄同樣受 I4 精神約束：評級的效力來自 forge 上 reviewer 的已驗證行為（`ref` 回查），檔案內容本身不構成評級。

## 只能在更高驗證階確認的項目

- 演練實際耗時與接手包是否足夠（需真實演練）。

## 人類必看

- docs/13 K7 未列人類必看項目；建議審閱評級登錄的身份檢查。

## 完成定義（docs/13 §4）

- [ ] 驗收條件逐條對應到測試或標示的人工驗證
- [ ] PR 附實際執行的指令與輸出；未執行者標 NOT RUN
- [ ] 不變量 I1–I10 無一被破壞
- [ ] 相關文件已同步（11、12 與實作一致）
- [ ] 範例與測試資料皆為虛構
- [ ] 共讀包列出未驗證範圍與後續建議
- [ ] 經人類核准後合併

## 執行日誌（只增不改）

- 2026-11-13 agent:engineer-sw 由 docs/13 §3 K7 轉寫本 WP。
