---
id: DR-000
wp: WP-000
kind: choice                   # choice | start_approval | scope_change | acceptance_change
question: <需要人類決定的問題>
options:
  - id: A
    summary: <選項>
    impact: <對範圍、時程、風險、其他 WP 的影響>
    reversible: true
  - id: B
    summary: <選項>
    impact: <影響>
    reversible: true
recommendation:
  option: A
  reason: <AI 的建議與依據（附證據編號）>
needed_by: 2026-01-01
blocks: []                     # 不決定的話哪些 WP 會停
request_sha: "<提出時的 commit>"
resolution:                    # 效力來自 ref 指向的人類已驗證行為；Gate 會回查
  outcome: null                # APPROVE | REJECT | DEFER
  option: null
  decided_by: null
  decided_at: null
  ref: null                    # forge 上人類留言或 review 的網址
  dissent: []                  # 異議必須保留
---

## 背景

<為什麼會走到這個岔路；相關證據>

## 各選項說明

<必要時補充圖表或計算>

## 如何回覆

在 PR 留言：`/decide DR-000 <選項> [理由]`
