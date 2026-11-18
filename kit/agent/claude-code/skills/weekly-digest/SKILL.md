---
name: weekly-digest
description: 給一個任務的備援的週摘要（10 分鐘讀完）：本週最重要的三到五項變化、仍是假設或未知的事、一題挑戰題。沒有重大變化就直說，不湊數。依 kit/templates/weekly-digest.md。由人以 /weekly-digest 啟動，在節奏助理的分離脈絡中執行。
argument-hint: "<任務編號> <週次，例如 2026-W47> [備援的代號]"
disable-model-invocation: true
context: fork
agent: cadence-reporter
---

# 技能：weekly-digest（備援週摘要）

> 來源：`prompts/handoff-prompts.md` §6.2；改寫為通用版本。執行於 `cadence-reporter`。

**本次參數：** $ARGUMENTS

## 內容

依 `kit/templates/weekly-digest.md`：

- **本週最重要的三到五項變化**：各說明改了什麼、影響什麼、需不需要備援行動，並附來源連結。排序依關卡等級、介面契約變更、風險。**本週沒有重大變化就寫「本週無重大變更」，不要湊數。**
- **仍是假設或未知的事**：附標籤與來源。
- **一題挑戰題**：檢驗備援是否理解本週最關鍵的變化。**先不要給答案。**
- 結尾提醒：「讀完摘要不代表能接手。」

## 資料來源

repo 內本週的提交、已合併的工作包、共讀包、驗證報告、決策請求；平台資料若無法取得，寫「平台資料未取得」。記錄產生時的 commit（`generated_from_sha`）。

## 寫入

寫到 `cadence/digests/<週次>-<任務編號>.md`（新檔），或人指定的檔案。不修改其他檔案。

## 規則

只列事實並附來源；不寫進度百分比；不評價個人。

## 回報

依 `cadence-reporter` 的回報格式。
