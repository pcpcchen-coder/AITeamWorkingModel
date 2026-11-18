---
id: WP-007
mission: M-001
title: K5 — 韌體／硬體領域包與人類任務
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G2                      # docs/13 §3 K5 宣告值
review_tier: R2
scope:
  paths:
    - "kit/packs/**"
    - "kit/checklists/**"
    - "packages/aitw/**"
    - "examples/bms-ntc-demo/**"
    - "docs/10-domain-profiles-sw-fw-hw.md"
    - "docs/11-toolkit-spec.md"
satisfies: [S3]
depends_on: [WP-005]
acceptance:
  # 來源：docs/13 §3 K5「驗收」原文
  - id: AC1
    text: "範例專案中：修改 `knowledge/interfaces/analog.yaml` 而未同步韌體常數 → 一致性檢查失敗。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp007_ac1"
      ladder: V2
  - id: AC2
    text: "`measurement`／`hil_run` 證據缺少待測物、儀器校正編號、執行者或原始資料雜湊 → 失敗。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp007_ac2"
      ladder: V2
  - id: AC3
    text: "人類任務在啟動核准前登錄執行證據 → Gate 失敗（11 §5.3 步驟 11）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp007_ac3"
      ladder: V2
  - id: AC4
    text: "`trace` 輸出每個需求的最高驗證階；只到模擬的需求被標示。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp007_ac4"
      ladder: V2
  - id: AC5
    text: "檢查表項目缺結果或依據 → Gate 失敗。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp007_ac5"
      ladder: V2
  # 來源：docs/13 §3 K5 範圍（人類任務流程：偏離自動列入必看）
  - id: AC6
    text: "人類任務紀錄含偏離時，共讀包必看清單自動列入該偏離。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp007_ac6"
      ladder: V2
budget:
  max_iterations: 3
  max_agent_minutes: 480        # 規模 M；試行假設
start_approval: not_required
---

## 背景與目的

提供 `sw／fw／hw` 領域包（policy 預設、驗證配方、證據欄位要求、必看規則樣式），補齊檢查表，並讓「AI → 人 → AI」的人類任務接力可被檢查（docs/10）。

## 作法

- 預計 2 個 PR：`wp/WP-007-packs-checklists`（領域包、檢查表草稿）、`wp/WP-007-human-task-trace`（`evidence add` 的 `conditions` 驗證、偏離列入必看、介面一致性檢查、`trace`）。
- 新增檢查表：軟體安全、電路圖審查、佈局審查、上電程序——**僅為起始草稿**，內容須由領域專家確認。
- 韌體／硬體的實際工具鏈與 EDA 依 docs/13 §6 的 D4、D5；未決前領域包保持工具鏈中立，驗證配方需外部工具者標「選用」。
- 本工單不產生任何燒錄、儀器或設備控制指令（I7）；程序書只描述由人執行的步驟。

## 只能在更高驗證階確認的項目

- 檢查表內容的專業正確性（需領域專家，規劃者與 Agent 均無法保證）。
- 實際 EDA 檔案格式的可處理程度（D4）。

## 人類必看（docs/13 原文）

- 各檢查表內容（需領域專家確認，這是規劃者無法代為保證的部分）。
- policy 預設值。

## 完成定義（docs/13 §4）

- [ ] 驗收條件逐條對應到測試或標示的人工驗證
- [ ] PR 附實際執行的指令與輸出；未執行者標 NOT RUN
- [ ] 不變量 I1–I10 無一被破壞
- [ ] 相關文件已同步（10、11、12 與實作一致）
- [ ] 範例與測試資料皆為虛構
- [ ] 共讀包列出未驗證範圍與後續建議
- [ ] 經人類核准後合併

## 執行日誌（只增不改）

- 2026-11-13 agent:engineer-sw 由 docs/13 §3 K5 轉寫本 WP。
