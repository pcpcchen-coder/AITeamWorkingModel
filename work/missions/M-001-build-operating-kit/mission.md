---
id: M-001
title: 建置 Git-native Operating Kit，讓 AI 開發 × 人類共讀共推的流程可操作、可強制
owner: <repo owner：請填入你的 forge 帳號>
backup: none                  # 目前為 Solo；見 docs/13 §6 的 D3
status: PROPOSED              # 包含本檔的 PR 經 owner 合併後即為核准
success:
  - id: S1
    text: 以 aitw 指令在範例專案完成「建立工作包 → 留證 → 共讀包 → Gate → 看板」一輪（里程碑 M1）
    ladder_required: V3
  - id: S2
    text: docs/12 的黃金路徑與例外情境以端對端測試離線重現（里程碑 M3）
    ladder_required: V3
  - id: S3
    text: docs/13 §1.2 的不變量 I1–I10 各有自動化測試
    ladder_required: V2
out_of_scope:
  - 後端服務、資料庫、RAG、本地模型推論介面（docs/07 的 T01–T03、T11）
  - 任何設備、儀器、燒錄的控制功能
  - G0 自動合併
human_only:
  - 核准與合併 PR
  - 修改分支保護與 repo 設定
  - 領域檢查表內容的專業確認
risk_boundaries:
  - 公開 repo：只可使用虛構資料
  - 工具不得降低 docs/05 的安全要求
budget:
  max_wp: 12
  review_minutes_per_week: 90   # 試行假設，依實際量測調整
deadline: null
---

## 背景

01–08 完成了原則與目標平台的設計，但尚無可操作的流程與工具。v0.3 規劃（09–13）提出先以版控檔案 + PR + CI + CLI 運作的 Operating Kit。

## 成功定義的說明

S1–S3 皆可由 CI 與端對端測試驗證；不涉及實體設備。真實專案的適用性需另以試點驗證（docs/13 §6 的 D7），不在本 Mission 的成功定義內。

## AI 可自主進行的範圍

依 docs/13 的工單 K0–K8 實作、測試、撰寫文件；每張工單以 PR 送審。規格不清或有誤時提出決策請求。

## 計畫

工單、驗收條件與相依見 [docs/13](../../../docs/13-opus-handoff.md)。K0 的第一步會把各工單轉成本目錄下的 `wp/` 工作包檔，另開 Plan PR 供核准。

## 待人類確認

見 docs/13 §6（D1–D8）。
