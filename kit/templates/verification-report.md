---
wp: WP-000
revision: 1
head_sha: "<commit>"
validator: "agent:validator"
independent_context: true      # 是否使用與 Engineer 不同的模型或全新上下文
verdict: PASS                  # PASS | FAIL | BLOCKED
criteria:
  AC1: PASS
findings:                      # 包含驗收條件沒涵蓋到的風險
  - id: F1
    severity: risk             # blocker | risk | note
    text: <發現>
    in_acceptance_scope: false
    suggestion: <建議；由人類決定是否處理>
disagreements: []              # 與 Engineer 結論不一致之處（會列入必看清單）
only_verifiable_on_hardware: []
---

# 驗證報告 · WP-000 · r1

## 我實際做了什麼

<重跑了哪些指令、檢查了哪些證據的來源與條件；附證據編號>

## 逐條驗收結果

| 驗收條件 | 結果 | 依據 |
|---|---|---|
| AC1 | | |

## 沒有驗證的部分

<明列未測邊界與原因>

> Validator 不是人類審查的替代品；本報告不構成核准。
