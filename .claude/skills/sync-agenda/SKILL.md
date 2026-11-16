---
name: sync-agenda
description: 每週團隊會的兩個階段：(1) agenda：依 repo 與 MR／PR 的事實準備議程（逾期與卡住、跨任務碰撞、共用資源、審查負荷、調整一條規則）；(2) minutes：會後只依人提供的結論起草紀錄，列出每個決定要在哪裡留言才生效。依 kit/templates/sync-agenda.md。由人以 /sync-agenda 啟動，在節奏助理的分離脈絡中執行。
argument-hint: "[agenda|minutes] <日期> [會議長度分鐘] [minutes 時：會議結論全文]"
disable-model-invocation: true
context: fork
agent: cadence-reporter
---

# 技能：sync-agenda（議程與會議紀錄）

> 來源：`docs/17` 第 13 站、`docs/16` §9；改寫為通用版本。執行於 `cadence-reporter`。

**本次參數：** $ARGUMENTS

第一項是 `agenda` 或 `minutes`；不清楚時判為無法產生並說明需要哪一種。

## A. 議程（agenda）

依 `kit/templates/sync-agenda.md`，會議長度與分段依參數（未指定時用 `docs/16` §9 的團隊會五段）：逾期與卡住、跨任務碰撞、共用資源、審查負荷、調整一條規則。

資料**只用 repo 與 MR／PR 上的事實**：
- 逾期或本週到期的決策請求。
- 被阻擋的工作包與原因。
- 範圍重疊、跨任務相依、介面契約的變更。
- 人類任務佇列與需要的設備、人員。
- 每個人的待審件數與等待最久的一件（需要平台資料；取得不到就寫「平台資料未取得」）。

每一項附連結或檔案路徑。**沒有資料的段落寫「無」，不要湊內容。** 不寫任何進度百分比；進度只列「已接受的工作包數／總數」。另外列出本週前三大變更，各用兩句話說明主張與證據，供會上共讀。

寫到 `cadence/sync/<日期>-agenda.md`（新檔），或人指定的檔案。

## B. 會議紀錄（minutes）

參數中必須有人提供的**會議結論**；沒有就停下來請人提供，不要自己推測會議內容。

- 依 `kit/templates/sync-agenda.md` 起草，寫到 `cadence/sync/<日期>-minutes.md`（新檔）。
- **只記錄人給你的結論**，不要自行補充或推測沒談到的事。結論不清楚或互相矛盾時，列為「待確認」。
- 會中做的決定，逐一列出「**誰需要在哪個 MR／PR 留言才生效**」。
- 列出指派出去的人類任務、執行者與日期（只列人給的）。
- 依專案約定，紀錄由與會者以 MR／PR 核准；你不提交、不開 MR／PR，交給人處理。

## 規則

不評價個人；不寫進度百分比；不修改節奏類以外的檔案。

## 回報

依 `cadence-reporter` 的回報格式。
