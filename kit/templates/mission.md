---
id: M-000
title: <一句話的任務目標>
owner: <primary 的 forge 帳號>
backup: <backup 的 forge 帳號，或 none>
status: PROPOSED
success:                      # 可量測、可驗證的成功定義
  - id: S1
    text: <什麼結果算成功>
    ladder_required: V2       # 需要驗證到哪一階（V1–V5，見 docs/10 §2）
out_of_scope:
  - <明確不做的事>
human_only:                   # 必須由人執行的動作
  - <例：燒錄、量測、送板>
risk_boundaries:
  - <不可碰的東西、安全限制>
budget:
  max_wp: 10
  review_minutes_per_week: 90
deadline: null
---

## 背景

<為什麼要做；目前已知的事實（附來源）與未知>

## 成功定義的說明

<S1… 各自如何驗證；需要哪些人類任務>

## AI 可自主進行的範圍

<例：分析、計算、模擬、主機端測試可直接做，完成後送審>

## 相關資料

<repo 路徑、既有決策、介面契約；不可貼入機密內容>
