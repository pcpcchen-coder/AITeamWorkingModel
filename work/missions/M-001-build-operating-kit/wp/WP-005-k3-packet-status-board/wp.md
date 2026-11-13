---
id: WP-005
mission: M-001
title: K3 — 共讀包、狀態與看板
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G1                      # docs/13 §3 K3 宣告值
review_tier: R2
scope:
  paths:
    - "packages/aitw/**"
    - "examples/bms-ntc-demo/**"
    - "docs/11-toolkit-spec.md"
satisfies: [S1, S3]
depends_on: [WP-003]
acceptance:
  # 來源：docs/13 §3 K3「驗收」原文
  - id: AC1
    text: "必看清單規則（09 §6.2）逐條有 fixture：安全關鍵路徑、介面契約、測試刪除／跳過、驗收變更、Validator 異議、HYPOTHESIS 主張。Agent 提供的額外項目可增加、不可使規則項目消失。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp005_ac1"
      ladder: V2
  - id: AC2
    text: "共讀包敘述空格未填 → lint 失敗；敘述引用不存在的證據編號 → lint 失敗。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp005_ac2"
      ladder: V2
  - id: AC3
    text: "狀態推導涵蓋 09 §5 每一列。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp005_ac3"
      ladder: V2
  - id: AC4
    text: "待審數達上限時 `wp submit` 拒絕並指出是誰、幾件。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp005_ac4"
      ladder: V2
  - id: AC5
    text: "看板：數字與由檔案重算的結果一致（I9）；輸入含 HTML／腳本字元時輸出已跳脫；離線可開；每個數字有來源連結；顯示產生時的 commit。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp005_ac5"
      ladder: V2
  # 來源：docs/11 §13 第 1 點
  - id: AC6
    text: "`packet build`、`brief`、`STATUS.md` 產生各有單元測試，輸出為確定性（I1）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp005_ac6"
      ladder: V2
  # 來源：docs/13 §1.2
  - id: AC7
    text: "I9：看板與報告的每個數字可由檔案重算；不接受模型填寫的數值。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i9"
      ladder: V2
  # 來源：Mission M-001 的 S3 與 docs/13 §1.2（M1 結束時 I1–I10 必須全部有測試）
  - id: AC8
    text: "不變量覆蓋檢查：標記 inv_i1 至 inv_i10 每個至少收集到 1 個測試，且全部通過。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp005_ac8"
      ladder: V2
budget:
  max_iterations: 3
  max_agent_minutes: 480        # 規模 M；試行假設
start_approval: not_required
---

## 背景與目的

讓人類用最少時間讀懂一個 WP（共讀包 + 必看清單），並用由事實推導的狀態與看板掌握全局。完成後達成里程碑 M1（Mission S1）。

## 作法

預計 2 個 PR：

1. `wp/WP-005-packet-submit`：`packet build`（確定性骨架 + 必看規則）、`wp submit`（WIP 上限）、`wp status`（forge 推導）。
2. `wp/WP-005-board`：`board build`（單檔離線 HTML + `data.json`）、`brief`、`STATUS.md`；附看板截圖（以 Playwright 產生，僅供人類審閱）。

- 看板不載入任何外部資源；所有文字經跳脫；每個數字附來源檔案或 PR 連結。

## 只能在更高驗證階確認的項目

- 看板是否真的讓人類更快做決定（需試點量測，09 §13）。

## 人類必看（docs/13 原文）

- 必看清單的規則實作。
- 看板實際畫面（附截圖）。

## 完成定義（docs/13 §4）

- [ ] 驗收條件逐條對應到測試或標示的人工驗證
- [ ] PR 附實際執行的指令與輸出；未執行者標 NOT RUN
- [ ] 不變量 I1–I10 無一被破壞
- [ ] 相關文件已同步（11、12 與實作一致）
- [ ] 範例與測試資料皆為虛構
- [ ] 共讀包列出未驗證範圍與後續建議
- [ ] 經人類核准後合併

## 執行日誌（只增不改）

- 2026-11-13 agent:engineer-sw 由 docs/13 §3 K3 轉寫本 WP。
