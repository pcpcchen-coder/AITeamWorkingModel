---
# 虛構測試資料（fictional test data）
wp: WP-001
revision: 1
head_sha: "0000000000000000000000000000000000000001"
effective_gate: G1
review_tier: R2
claims:
  - {id: C1, text: 換算函式在量程內正確（虛構）, label: OBSERVED, evidence: [EV-001-01], ladder: V2, scope_limits: 僅主機端}
must_read:
  - {path: sw/convert/convert.py, lines: "1-20", reason: 換算邏輯, est_minutes: 5}
questions: [DR-001]
challenge_question: 超出量程時回傳什麼？
unverified: [實機行為]
rollback: revert 該 merge commit
---

# 共讀包 · WP-001 · r1（虛構）
