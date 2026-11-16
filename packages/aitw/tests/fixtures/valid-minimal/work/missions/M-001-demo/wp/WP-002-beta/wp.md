---
# 虛構測試資料（fictional test data）
id: WP-002
mission: M-001
title: 虛構工作包：呼叫端整合
domain: sw
executor: ai
agent: engineer-sw
autonomy: A2
gate: G1
review_tier: R2
scope:
  paths: ["sw/app/**"]
satisfies: [S1]
depends_on: [WP-001]
acceptance:
  - id: AC1
    text: 整合測試通過
    verify: {kind: test_run, runner: ci, command: "python -m pytest sw/app", ladder: V3}
budget: {max_iterations: 3, max_agent_minutes: 120}
start_approval: not_required
---

## 背景與目的

虛構測試資料。
