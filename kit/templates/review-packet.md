---
wp: WP-000
revision: 1
head_sha: "<送審時的 commit>"
effective_gate: G1
review_tier: R2
claims:
  - id: C1
    text: <一句可被檢驗的主張>
    label: OBSERVED            # VERIFIED | OBSERVED | HYPOTHESIS | RECOMMENDATION | UNKNOWN | REJECTED
    evidence: [EV-000-01]
    ladder: V2
    scope_limits: <這個結論不適用於哪些情況>
must_read:                     # 規則項目由工具產生；Agent 可加不可減
  - path: "<檔案>"
    lines: "<行號範圍>"
    reason: <為什麼必看>
    est_minutes: 5
questions: []                  # 連到 DR 編號
challenge_question: <一題檢驗理解的問題>
unverified:
  - <未驗證範圍或已知失敗>
rollback: <如何回退>
---

# 共讀包 · WP-000 · r1

## 1. 三行摘要

- **改了什麼：**
- **為什麼：**
- **影響誰：**

## 2. 主張與證據

| # | 主張 | 標籤 | 證據 | 驗證階 | 範圍限制 |
|---|---|---|---|---|---|
| C1 | | | | | |

## 3. 必看清單（合計約 __ 分鐘）

| 項目 | 原因 | 預估 |
|---|---|---|
| | | |

## 4. 可略讀

<機械性變更、產生檔>

## 5. 未驗證範圍與已知失敗

<包含：只能在更高驗證階確認的項目>

## 6. 需要你決定的事

<DR 編號、選項、建議；沒有則寫「無」>

## 7. 挑戰題

<問題>（請以 `/understood <答案>` 回覆）

## 8. 回退方式

<指令或步驟>
