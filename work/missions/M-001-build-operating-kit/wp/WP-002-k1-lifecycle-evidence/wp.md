---
id: WP-002
mission: M-001
title: K1 — 工作包生命週期與證據（init、mission、wp、evidence、標籤規則、halt）
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G1                      # docs/13 §3 K1 宣告值
review_tier: R2
scope:
  paths:
    - "packages/aitw/**"
    - "examples/bms-ntc-demo/**"
    - "docs/11-toolkit-spec.md"
satisfies: [S1, S3]
depends_on: [WP-001]
acceptance:
  # 來源：docs/13 §3 K1「驗收」原文
  - id: AC1
    text: "`evidence run` 記錄 11 §7.1 的全部欄位；指令失敗仍留證且結束碼為 1；重跑產生新編號、舊紀錄不變（I6）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp002_ac1"
      ladder: V2
  - id: AC2
    text: "無法以參數把 `produced_by` 指定為 `ci` 或 `human`（I2）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp002_ac2"
      ladder: V2
  - id: AC3
    text: "L1–L6 每條規則各有通過與失敗案例。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp002_ac3"
      ladder: V2
  - id: AC4
    text: "證據之後修改 `scope.paths` 內檔案 → `evidence check` 報告過期。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp002_ac4"
      ladder: V2
  - id: AC5
    text: "`wp start` 在下列情況拒絕並說明：相依未接受、需啟動核准而未核准、HALT 存在（I10）、預算用盡。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp002_ac5"
      ladder: V2
  - id: AC6
    text: "`init` 不覆寫既有檔案；重複執行結果相同。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp002_ac6"
      ladder: V2
  # 來源：docs/11 §13 第 1 點（每個指令有單元測試）、§6（錯誤訊息須含檔案、欄位、原因、修正方式）
  - id: AC7
    text: "本工單範圍內每個指令（init、mission new|list|show、wp new|start|block|unblock|status、evidence run|add|check、halt）各有單元測試，涵蓋結束碼 0／1／2／4 中適用者；錯誤訊息含檔案、欄位、原因與修正方式。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp002_ac7"
      ladder: V2
  # 來源：docs/13 §1.2
  - id: AC8
    text: "I2：Agent 產生的證據標籤最高為 OBSERVED；VERIFIED 只能來自 CI 或人類簽認（含 evidence add 的人類身份不可由 Agent 環境冒用，見決策請求 DR-P7）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i2"
      ladder: V2
  - id: AC9
    text: "I6：證據只增不改；失敗的執行也留存（manifest 既有項目在任何指令後位元組不變）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i6"
      ladder: V2
  - id: AC10
    text: "I10（開工類指令部分）：HALT 存在時 `wp start` 與其他開工類指令失敗，結束碼 4。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i10"
      ladder: V2
  - id: AC11
    text: "I1（本工單指令）：相同輸入產生相同輸出（時間與 commit 以可注入的時鐘／git 替身固定後比對）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i1"
      ladder: V2
budget:
  max_iterations: 3
  max_agent_minutes: 480        # 規模 M；試行假設
start_approval: not_required
---

## 背景與目的

讓 WP 可以被建立、開工、阻擋、留證與檢查證據，全部在本地（LocalForge，只用 git）完成。這是「有證據」（docs/14 §6 第 3 級）的核心。

## 作法

預計 2 個 PR：

1. `wp/WP-002-init-mission-wp`：`init`、`mission *`、`wp new|start|block|unblock|status`（LocalForge）、`halt`。
2. `wp/WP-002-evidence`：`evidence run|add|check`、L1–L6、過期偵測。

- 指令執行器：`subprocess`、限時（預設值可設定）、stdout／stderr 完整存檔、sha256；不經 shell 解譯參數（`--` 之後的參數清單直接傳入）。
- `produced_by` 由執行環境決定（例：`AITW_AGENT_ROLE` → `agent:<role>`）；**不提供**任何指定 `produced_by` 的參數。CI 身份只由 K2a 的 `aitw verify` 產生。
- 待決事項：`wp start` 的啟動核准判定（DR-P8）、預算的計量方式（DR-P9）、`evidence add --by human:` 與 I2 的關係（DR-P7）。

## 只能在更高驗證階確認的項目

- 無實體項目。

## 人類必看（docs/13 原文）

- 證據執行器的實作（指令執行、限時、輸出保存）。
- 標籤規則測試。

## 完成定義（docs/13 §4）

- [ ] 驗收條件逐條對應到測試或標示的人工驗證
- [ ] PR 附實際執行的指令與輸出；未執行者標 NOT RUN
- [ ] 不變量 I1–I10 無一被破壞
- [ ] 相關文件已同步（11、12 與實作一致）
- [ ] 範例與測試資料皆為虛構
- [ ] 共讀包列出未驗證範圍與後續建議
- [ ] 經人類核准後合併

## 執行日誌（只增不改）

- 2026-11-13 agent:engineer-sw 由 docs/13 §3 K1 轉寫本 WP。
