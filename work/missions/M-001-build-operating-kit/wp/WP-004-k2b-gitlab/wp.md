---
id: WP-004
mission: M-001
title: K2b — GitLab adapter 與整合包
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G2                      # docs/13 §3 K2b 宣告值
review_tier: R2
scope:
  paths:
    - "packages/aitw/**"
    - "kit/forge/gitlab/**"
    - "docs/14-gitlab-profile.md"     # 回寫實測結果（UNKNOWN 項目）
    - "docs/11-toolkit-spec.md"
satisfies: [S1, S3]
depends_on: [WP-003]
acceptance:
  # 來源：docs/13 §3 K2b「驗收」原文
  - id: AC1
    text: "K2a 的全部 Gate 案例（含安全案例）以 GitLab 形式的固定資料再跑一次並通過——同一組案例、兩個 adapter。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp004_ac1"
      ladder: V2
  - id: AC2
    text: "Free 版情境：平台核准為選用時，未達核准條件 Gate 仍失敗；bot 與 MR 作者的核准不計；早於最新版本的核准不計。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp004_ac2"
      ladder: V2
  - id: AC3
    text: "以 `aitw:` 前綴的留言指令可被辨識；GitLab 原生 quick action 不被誤判為 Kit 指令。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp004_ac3"
      ladder: V2
  - id: AC4
    text: "`doctor` 能指出：主幹未保護、未開啟「Pipelines must succeed」、CI 設定檔仍在專案內（AI 可改）、bot 角色過高。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp004_ac4"
      ladder: V2
  - id: AC5
    text: "14 §5 的六個要點各有測試或文件化的人工驗證步驟（後者標示 NOT AUTOMATED）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp004_ac5"
      ladder: V2
  - id: AC6
    text: "14 列為 UNKNOWN 的項目以實際 GitLab 驗證並回寫文件。"
    verify:
      kind: test_run
      runner: human            # 需要實際 GitLab 環境與權杖，見決策請求 DR-P11
      ladder: V4
  - id: AC7
    text: "「核准後重新評估 Gate」的作法經實測選定，並在 PR 以決策請求說明取捨。"
    verify:
      kind: test_run
      runner: human            # 需要實際 GitLab 環境，見決策請求 DR-P11
      ladder: V4
  # 來源：docs/13 §1.2
  - id: AC8
    text: "I4（GitLab）：bot、MR 作者、早於最新版本的核准一律不計（與 AC2 共用 fixture，以 inv_i4 標記納入不變量測試集）。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i4"
      ladder: V2
budget:
  max_iterations: 3
  max_agent_minutes: 480        # 規模 M；試行假設
start_approval: not_required
---

## 背景與目的

讓 Kit 在單位實際使用的 GitLab 上運作（規格：docs/14）。須在首個 GitLab 試點前完成；可與 K3 平行。

## 作法

預計 2 個 PR：

1. `wp/WP-004-gitlab-adapter`：`GitLabForge`（REST；以錄製回應測試）、留言指令前綴設定、Gate 案例重跑（AC1–AC4）。
2. `wp/WP-004-gitlab-kit`：`kit/forge/gitlab/`（CI 範本含 `aitw-verify`、`aitw-gate` job、MR 樣板、Free／Premium 設定指南）、`doctor` 的 GitLab 檢查項、14 §5 六要點的測試與人工步驟；實測結果回寫 docs/14。

- AC6、AC7 需要一個可用的 GitLab 測試專案（gitlab.com 的虛構專案或單位自架環境）與權杖；離線單元測試不受影響。見 DR-P11 與 docs/13 §6 的 D1。

## 只能在更高驗證階確認的項目

- 真實 GitLab 的核准 API 欄位、bot 能否核准、外部 status check 等級（V4，AC6）。
- 單位 GitLab 的實際版本與授權等級（D1）。

## 人類必看（docs/13 原文）

- CI 範本的 job 定義與變數使用。
- 設定指南（需對照單位的 GitLab 版本與等級）。

## 完成定義（docs/13 §4）

- [ ] 驗收條件逐條對應到測試或標示的人工驗證
- [ ] PR 附實際執行的指令與輸出；未執行者標 NOT RUN
- [ ] 不變量 I1–I10 無一被破壞
- [ ] 相關文件已同步（11、12、14 與實作一致）
- [ ] 範例與測試資料皆為虛構
- [ ] 共讀包列出未驗證範圍與後續建議
- [ ] 經人類核准後合併

## 執行日誌（只增不改）

- 2026-11-13 agent:engineer-sw 由 docs/13 §3 K2b 轉寫本 WP。
