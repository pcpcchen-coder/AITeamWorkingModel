---
# 虛構範例資料（fictional）；對應 docs/12 §3
id: M-001
title: 改善低溫段溫度量測準確度
owner: primary-a
backup: backup-b
status: ACTIVE
success:
  - id: S1
    text: 樣板實測 -20~60°C 溫度誤差 ≤ ±1°C
    ladder_required: V4
out_of_scope: [更換 MCU, 變更 PCB 佈局]
human_only: [改板, 燒錄, 溫箱量測, BOM 釋出]
risk_boundaries:
  - 只允許改被動元件值與韌體
  - 實體動作依機構實驗室 SOP，本流程不取代 SOP
budget: {max_wp: 10, review_minutes_per_week: 90}
deadline: null
---

## 背景

（虛構）低溫段溫度誤差偏大，連帶使低溫 SOH 估算不準。量測鏈：NTC → 上拉分壓 → MCU ADC → 韌體換算 → 通訊訊框 → 上位機。

## 成功定義的說明

S1 需要樣板實測（V4），由人類任務 WP-005 取得；AI 只能做到分析、計算、模擬與主機端測試（V2–V3）。

## AI 可自主進行的範圍

分析、計算、模擬、韌體與軟體的主機端測試可直接做，做完送審（docs/12 §3 的訪談結果）。

## 相關資料

- 介面契約：`knowledge/interfaces/analog.yaml`、`knowledge/interfaces/protocol.yaml`
- 需求：`knowledge/requirements.yaml`
