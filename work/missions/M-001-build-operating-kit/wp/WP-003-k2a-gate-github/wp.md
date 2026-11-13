---
id: WP-003
mission: M-001
title: K2a — Gate 核心、CI 驗證與 GitHub 整合
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G2                      # docs/13 §3 K2a 宣告值
review_tier: R2
scope:
  paths:
    - "packages/aitw/**"
    - "kit/forge/github/**"
    - "examples/bms-ntc-demo/**"
    - "docs/11-toolkit-spec.md"
satisfies: [S1, S3]
depends_on: [WP-002]
acceptance:
  # 來源：docs/13 §3 K2a「驗收」原文
  - id: AC1
    text: "14 步每一步至少一個通過與一個失敗案例（FakeForge）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp003_ac1"
      ladder: V2
  - id: AC2
    text: "安全案例必須失敗：PR 內修改 policy／工具／workflow；PR 內放寬驗證指令而無授權 DR；核准者是 Agent 身份；核准者是 PR 作者；核准針對舊 commit；DR 的 `ref` 指向不存在或非授權人類的留言；變更超出 scope。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp003_ac2"
      ladder: V2
  - id: AC3
    text: "`verify` 執行的是基底分支上的指令（以「PR 把指令改成恆真」的 fixture 證明）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp003_ac3"
      ladder: V2
  - id: AC4
    text: "Gate 報告每個失敗項都有「下一步該誰做什麼」。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp003_ac4"
      ladder: V2
  - id: AC5
    text: "Workflow：PR 觸發的工作不使用 secret、權杖唯讀；Gate 工作使用基底／已釋出版本的工具（以設定檢查測試證明；無法自動化的部分以文件化的人工驗證步驟證明，並標示 NOT AUTOMATED）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp003_ac5"
      ladder: V2
  - id: AC6
    text: "`GitHubForge` 以錄製的回應做契約測試。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp003_ac6"
      ladder: V3
  - id: AC7
    text: "`GitHubForge` 對真實 API 的手動驗證步驟寫入文件（`kit/forge/github/`），並在 PR 記錄是否實際執行。"
    verify:
      kind: doc
      runner: human
      ladder: V4
  # 來源：docs/11 §13 第 1 點
  - id: AC8
    text: "`decision request|list|resolve` 與 `doctor`（GitHub 檢查項）各有單元測試；`resolve` 只登錄 `ref` 並回查該人類行為。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp003_ac8"
      ladder: V2
  # 來源：docs/13 §1.2
  - id: AC9
    text: "I3：Gate Check 使用的工具、policy、config、驗收定義取自基底分支。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i3"
      ladder: V2
  - id: AC10
    text: "I4：Agent 身份與 PR 作者的核准不計入；核准只認針對 head commit 的人類 review。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i4"
      ladder: V2
  - id: AC11
    text: "I5：驗收定義變更、範圍外變更、人類專屬路徑變更，沒有人類授權就失敗。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i5"
      ladder: V2
  - id: AC12
    text: "I10（Gate 部分）：基底有 HALT 時 `gate check` 失敗，結束碼 4。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i10"
      ladder: V2
budget:
  max_iterations: 3
  max_agent_minutes: 900        # 規模 L；試行假設
start_approval: not_required
---

## 背景與目的

把 docs/11 §5.3 的 14 步 Gate 實作為確定性演算法，經 `ForgeAdapter` 存取平台；先以 `FakeForge` 與 `GitHubForge` 落地（本 repo 自身在 GitHub）。這是「有關卡」（docs/14 §6 第 4 級）。

## 作法

預計 3 個 PR：

1. `wp/WP-003-forge-adapter`：`ForgeAdapter` 介面、`FakeForge`（讀固定資料）、`LocalForge` 擴充。
2. `wp/WP-003-gate-verify`：`gate check` 14 步、`verify`、`decision *`、報告（文字 + JSON）。
3. `wp/WP-003-github`：`GitHubForge`（REST，錄製回應契約測試）、`doctor`、`kit/forge/github/`（workflow、CODEOWNERS 產生、設定指南）。

- 共用 Gate 測試案例以「平台中立的情境描述 + 各 adapter 的固定資料」組織，供 K2b 直接重跑。
- `kit/forge/github/` 的 workflow 只是**範本**（給專案 `aitw init` 複製），不會啟用在本 repo；本 repo 的 workflow 變更屬人類專屬路徑（DR-P2）。
- PR 種類辨識需要 plan／decision／cadence／takeover PR 的分支命名規則，docs/11 未定義——見 DR-P10。

## 只能在更高驗證階確認的項目

- 真實 GitHub API 的行為（V4，手動驗證步驟，AC7）。

## 人類必看（docs/13 原文）

- Gate 演算法實作全文。
- workflow 的觸發條件與權限。
- 安全案例測試清單。

## 完成定義（docs/13 §4）

- [ ] 驗收條件逐條對應到測試或標示的人工驗證
- [ ] PR 附實際執行的指令與輸出；未執行者標 NOT RUN
- [ ] 不變量 I1–I10 無一被破壞
- [ ] 相關文件已同步（11、12 與實作一致）
- [ ] 範例與測試資料皆為虛構
- [ ] 共讀包列出未驗證範圍與後續建議
- [ ] 經人類核准後合併

## 執行日誌（只增不改）

- 2026-11-13 agent:engineer-sw 由 docs/13 §3 K2a 轉寫本 WP。
