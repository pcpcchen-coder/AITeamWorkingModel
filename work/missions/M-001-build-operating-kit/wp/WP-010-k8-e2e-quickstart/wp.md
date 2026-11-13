---
id: WP-010
mission: M-001
title: K8 — 黃金路徑端對端與教學（e2e、docs/15-quickstart.md、文件同步）
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G1                      # docs/13 §3 K8 宣告值
review_tier: R2
scope:
  paths:
    - "packages/aitw/**"
    - "examples/bms-ntc-demo/**"
    - "docs/09-execution-playbook.md"
    - "docs/10-domain-profiles-sw-fw-hw.md"
    - "docs/11-toolkit-spec.md"
    - "docs/12-operating-examples.md"
    - "docs/13-opus-handoff.md"
    - "docs/14-gitlab-profile.md"
    - "docs/15-quickstart.md"
    - "README.md"
    - "kit/README.md"
satisfies: [S2]
depends_on: [WP-004, WP-006, WP-007, WP-008, WP-009]
acceptance:
  # 來源：docs/13 §3 K8「驗收」原文
  - id: AC1
    text: "端對端測試在 CI 離線通過，涵蓋 12 的 §5–§8 與 §12 的每個例外情境。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp010_ac1"
      ladder: V3
  - id: AC2
    text: "一位未參與開發的人依 quickstart 可在範例專案完成一輪（人工驗證，結果寫入 PR）。"
    verify:
      kind: test_run
      runner: human            # 執行者人選見決策請求 DR-P12
      ladder: V3
  # 來源：docs/13 §3 K8 範圍、§4 完成定義「相關文件已同步」
  - id: AC3
    text: "09–14 與實作的差異已核對並同步；quickstart 含 GitHub 與 GitLab 兩版步驟。"
    verify:
      kind: doc
      runner: human
      ladder: V1
budget:
  max_iterations: 3
  max_agent_minutes: 480        # 規模 M；試行假設
start_approval: not_required
---

## 背景與目的

以 docs/12 的全流程為端對端測試（FakeForge），並提供從 `aitw init` 到第一個 WP 合併的教學，達成里程碑 M3（Mission S2）。

## 作法

- 預計 2 個 PR：`wp/WP-010-e2e`（端對端測試）、`wp/WP-010-quickstart`（docs/15 與文件同步）。
- 端對端測試以 FakeForge 驅動 GitHub 與 GitLab 兩組固定資料。

## 只能在更高驗證階確認的項目

- 真實團隊依 quickstart 導入的阻力（需試點，docs/13 §6 的 D7）。

## 人類必看

- docs/13 K8 未列人類必看項目；AC2 本身即為人工驗證。

## 完成定義（docs/13 §4）

- [ ] 驗收條件逐條對應到測試或標示的人工驗證
- [ ] PR 附實際執行的指令與輸出；未執行者標 NOT RUN
- [ ] 不變量 I1–I10 無一被破壞
- [ ] 相關文件已同步（09–15 與實作一致）
- [ ] 範例與測試資料皆為虛構
- [ ] 共讀包列出未驗證範圍與後續建議
- [ ] 經人類核准後合併

## 執行日誌（只增不改）

- 2026-11-13 agent:engineer-sw 由 docs/13 §3 K8 轉寫本 WP。
