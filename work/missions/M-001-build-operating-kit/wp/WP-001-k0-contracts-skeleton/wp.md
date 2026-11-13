---
id: WP-001
mission: M-001
title: K0 — 契約與骨架（schema、aitw lint、範例專案、CI）
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G1                      # docs/13 §3 K0 宣告值
review_tier: R2
scope:
  paths:
    - "packages/aitw/**"
    - "examples/bms-ntc-demo/**"
    - "work/missions/M-001-build-operating-kit/wp/**"
    - "pytest.ini"                    # repo 根的測試設定（見 wp/README.md「驗證指令慣例」）
    - ".github/workflows/ci.yml"      # 人類專屬路徑：見 Plan PR 的決策請求 DR-P2
    - "kit/templates/**"              # 僅限使樣板通過 schema 的必要修正：見決策請求 DR-P3
    - "docs/11-toolkit-spec.md"       # 僅同步 schema 位置等與實作不一致之處
    - "kit/README.md"
    - "README.md"
satisfies: [S1, S3]
depends_on: []
acceptance:
  # 來源：docs/13 §3 K0「驗收」原文
  - id: AC1
    text: "`aitw lint` 對範例專案通過。"
    verify:
      kind: static_analysis
      runner: ci
      command: "aitw --repo examples/bms-ntc-demo lint"
      ladder: V1
  - id: AC2
    text: "至少 8 個刻意寫壞的 fixture（缺必填欄位、編號重複、引用不存在的 WP、未知列舉值、驗收條件缺 `verify`、相依成環等）各自失敗，訊息含檔案、欄位、原因、修正方式。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp001_ac2"
      ladder: V2
  - id: AC3
    text: "範例專案的 `make -C fw test` 可在 CI 執行。"
    verify:
      kind: test_run
      runner: ci
      command: "make -C examples/bms-ntc-demo/fw test"
      ladder: V2
  - id: AC4
    text: "範例專案的軟體測試可在 CI 執行。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest examples/bms-ntc-demo/sw"
      ladder: V2
  - id: AC5
    text: "範例專案的硬體計算腳本可在 CI 執行。"
    verify:
      kind: calc
      runner: ci
      command: "python examples/bms-ntc-demo/hw/calc/ntc_divider_worstcase.py --candidates 10k,22k,33k"
      ladder: V2
  # 來源：docs/13 §3 K0「範圍」中可檢驗的交付項
  - id: AC6
    text: "11 §4 各檔案的 JSON Schema 存在；`kit/templates/` 全部樣板通過 schema。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp001_ac6"
      ladder: V2
  - id: AC7
    text: "CI（lint + pytest）在 PR 上執行並綠燈。"
    verify:
      kind: test_run
      runner: human            # owner 在 PR 頁面確認 CI 工作實際執行與結果
      ladder: V2
  # 來源：docs/13 §1.2（不變量每條都必須有自動化測試）
  - id: AC8
    text: "I1：`aitw lint` 對同一輸入重複執行，輸出（含 --json）逐位元組相同；套件相依不含任何模型 SDK，且測試期間禁止網路連線。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i1"
      ladder: V2
  - id: AC9
    text: "I7：`packages/aitw/`、`kit/`、`examples/` 不含、CLI 輸出不產生任何燒錄、除錯器、儀器或設備控制指令（以樣式掃描測試；K4 拒絕清單資料檔另行處理，見決策請求 DR-P6）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i7"
      ladder: V2
  - id: AC10
    text: "I8：`examples/` 與測試 fixture 每個檔案（或其所在目錄的說明檔）標示為虛構；掃描不到 secret 樣式（金鑰、權杖、私鑰標頭）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i8"
      ladder: V2
budget:
  max_iterations: 3
  max_agent_minutes: 480        # 規模 M；試行假設
start_approval: not_required
---

## 背景與目的

先把 docs/11 §4 的檔案契約定成可驗證的 JSON Schema，並建立範例專案 `examples/bms-ntc-demo/` 作為後續所有工單的測試資料。對應 Mission 成功定義 S1（M1 的基礎）與 S3（I1、I7、I8 的測試）。

## 作法

本工單預計切成 **3 個 PR**（皆在本 WP 範圍內）：

1. **Plan PR**（本 PR，分支 `wp/WP-001-plan`）：K0–K8 的 wp.md。不含程式。
2. **骨架與契約 PR**（分支 `wp/WP-001-schemas-lint`）：`packages/aitw/`（src 佈局、`pyproject.toml`）、JSON Schema、`aitw lint`（schema + 交叉引用）、壞 fixture、CI、I1／I7／I8 測試。
3. **範例專案 PR**（分支 `wp/WP-001-example-project`）：`examples/bms-ntc-demo/`（`sw/`、`fw/`、`hw/calc/`、`knowledge/interfaces/`、`.aiteam/`、M-001 與 WP-001～006），並在 CI 加入 AC1、AC3–AC5。

- Schema 位置：建議 `packages/aitw/src/aitw/schemas/`（作為套件資料隨 wheel 發佈），docs/11 §2 寫的是 `packages/aitw/schemas/`——見決策請求 DR-P4。
- 範例專案的 C 測試以主機 `cc` + `make` 建置；硬體計算為純 Python 腳本；不需模擬器或 EDA（docs/13 §1.3）。

## 只能在更高驗證階確認的項目

- 無實體項目。範例專案的「數值」皆為虛構，不代表任何真實元件或量測。

## 人類必看（docs/13 原文）

- schema 的必填欄位清單是否符合 11 §4。
- 範例專案確認為虛構。

## 完成定義（docs/13 §4）

- [ ] 驗收條件逐條對應到測試或標示的人工驗證
- [ ] PR 附實際執行的指令與輸出；未執行者標 NOT RUN
- [ ] 不變量 I1–I10 無一被破壞
- [ ] 相關文件已同步（11、12 與實作一致）
- [ ] 範例與測試資料皆為虛構
- [ ] 共讀包列出未驗證範圍與後續建議
- [ ] 經人類核准後合併

## 執行日誌（只增不改）

- 2026-11-13 agent:engineer-sw 由 docs/13 §3 K0 轉寫本 WP；開 Plan PR。
