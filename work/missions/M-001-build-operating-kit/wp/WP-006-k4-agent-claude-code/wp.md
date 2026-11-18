---
id: WP-006
mission: M-001
title: K4 — Agent 整合包（Claude Code）
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G2                      # docs/13 §3 K4 宣告值
review_tier: R2
scope:
  paths:
    - "kit/agent/claude-code/**"
    - "packages/aitw/**"              # 拒絕清單比對邏輯若放在 CLI 內
    - "examples/bms-ntc-demo/**"      # 技能操作紀錄（標示為示範）
    - "AGENTS.md"
    - "docs/11-toolkit-spec.md"
satisfies: [S3]
depends_on: [WP-005]
acceptance:
  # 來源：docs/13 §3 K4「驗收」原文
  - id: AC1
    text: "拒絕清單以樣本工具呼叫做單元測試：每一類至少三個應攔截與兩個不應誤攔的案例。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp006_ac1"
      ladder: V2
  - id: AC2
    text: "Validator 子代理的設定不允許寫入產品程式與測試。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m wp006_ac2"
      ladder: V2
  - id: AC3
    text: "每個技能有一份在範例專案上的操作紀錄（實際執行的對話與產出，放 `examples/` 並標示為示範）。"
    verify:
      kind: doc
      runner: human            # 存在性可由測試檢查；內容是否為實際執行需人類審閱
      ladder: V3
  - id: AC4
    text: "文件明寫：hook 是輔助防線，安全邊界在 forge 與執行環境權限。"
    verify:
      kind: doc
      runner: human
      ladder: V1
  # 來源：docs/13 §1.2
  - id: AC5
    text: "I7（Agent 層）：防護 hook 攔截燒錄、除錯器、串列埠與儀器控制類工具呼叫；整合包本身不產生此類指令。"
    verify:
      kind: test_run
      runner: ci
      command: "python -m pytest -m inv_i7"
      ladder: V2
budget:
  max_iterations: 3
  max_agent_minutes: 480        # 規模 M；試行假設
start_approval: not_required
---

## 背景與目的

把 `prompts/agent-contracts.md` 的契約落成 Claude Code 可用的技能、子代理與防護 hook（docs/11 §8），讓人類可「用技能驅動 Agent」（里程碑 M2）。

## 作法

- 先查證 Claude Code 官方文件中技能（skills）、子代理（subagents）、hooks 的檔案格式與事件名稱，再實作；與 docs/11 §8 不符處以官方為準並在 PR 回報。
- 預計 2 個 PR：`wp/WP-006-hooks-denylist`（hook 與拒絕清單 + 測試）、`wp/WP-006-skills-agents`（技能、子代理、安裝說明、操作紀錄、AGENTS.md 更新）。
- Agent 執行環境除 Claude Code 外是否同時支援本地模型，依 docs/13 §6 的 D8（預設先 Claude Code）。

## 只能在更高驗證階確認的項目

- hook 在實際長時間 Agent 工作中的誤攔率（需試點）。

## 人類必看（docs/13 原文）

- 拒絕清單樣式。
- 各技能的提示內容（是否有替人決定、替人核准的傾向）。

## 完成定義（docs/13 §4）

- [ ] 驗收條件逐條對應到測試或標示的人工驗證
- [ ] PR 附實際執行的指令與輸出；未執行者標 NOT RUN
- [ ] 不變量 I1–I10 無一被破壞
- [ ] 相關文件已同步（11、12 與實作一致）
- [ ] 範例與測試資料皆為虛構
- [ ] 共讀包列出未驗證範圍與後續建議
- [ ] 經人類核准後合併

## 執行日誌（只增不改）

- 2026-11-13 agent:engineer-sw 由 docs/13 §3 K4 轉寫本 WP。
