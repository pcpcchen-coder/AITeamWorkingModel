---
id: WP-000
mission: M-000
title: <工作包標題>
domain: sw                    # sw | fw | hw | sys | research
executor: ai                  # ai | human | pair
agent: engineer-sw            # executor 為 ai / pair 時填
autonomy: A2                  # A0–A3（docs/09 §3）
gate: G1                      # 宣告值；實際值由 Gate Check 取較高者
review_tier: R2
scope:
  paths:                      # 允許變更的路徑；超出即 Gate 失敗
    - "sw/example/**"
satisfies: []                 # 需求編號
depends_on: []                # 其他 WP
acceptance:                   # 合併 Plan 後凍結；變更需人類決議
  - id: AC1
    text: <可檢驗的驗收條件>
    verify:
      kind: test_run          # 見 docs/11 §4.2 的 kind 列舉
      runner: ci              # ci | agent | human
      command: "<驗證指令>"
      ladder: V2
budget:
  max_iterations: 3
  max_agent_minutes: 240
start_approval: not_required  # G3 必為 required
# blocked:                    # 存在即 BLOCKED
#   reason: <原因>
#   next_action: <下一步>
#   owner: <誰>
---

## 背景與目的

<這個工作包解決什麼；與 Mission 成功定義的關係>

## 作法

<預計怎麼做；會動到哪些檔案；有哪些替代方案>

## 只能在更高驗證階確認的項目

<例：實機時序、量測；對應的人類任務 WP>

## 執行日誌（只增不改）

- <時間> <誰/哪個 Agent> <做了什麼>
