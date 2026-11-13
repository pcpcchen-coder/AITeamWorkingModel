# 02 — AI 任務執行、Human Co-Review 與接手流程

**狀態：** 設計提案 v0.2

## 1. 事件驅動的標準循環

~~~mermaid
flowchart TD
 A[人類設定研究目標與邊界] --> B[AI 分解任務與驗證計畫]
 B --> C{需人類核准?}
 C -- 是 --> D[Primary / Reviewer 審核]
 D -->|批准| E[AI 在沙盒中執行]
 C -- 否 --> E
 E --> F[研究與程式產物 + 原始證據]
 F --> G[獨立驗證與證據核對]
 G --> H{達到門檻?}
 H -- 否 --> I[修正或要求人類決策]
 I --> B
 H -- 是 --> J[Human Co-Review]
 J --> K{是否重大決策/實體風險?}
 K -- 是 --> D
 K -- 否 --> L[更新狀態 / 知識 / 接手包]
 L --> M[下一個已授權任務]
 M --> B
~~~

每一步保留任務 ID、負責 Agent、模型/Prompt 版本、輸入來源、輸出雜湊與審查紀錄。**AI 的進度百分比僅反映已驗證的工作單位；不是 LLM 猜測值。**

## 2. 工作狀態機

~~~text
PROPOSED -> PLANNED -> AWAITING_APPROVAL -> APPROVED
         -> RUNNING -> VERIFYING -> IN_REVIEW -> ACCEPTED
                        |              |           |
                        v              v           v
                       BLOCKED ------> REWORK     ARCHIVED
~~~

- 不需事先核准的低風險任務，可從 PLANNED 進 RUNNING，但需留下授權 policy id。
- 高風險、對外發布、設備操作、正式環境寫入，不能繞過 AWAITING_APPROVAL。
- BLOCKED 必須有原因、下一個人類或系統動作、重試策略。

## 3. 資料與證據分層

| 類型 | 例子 | 呈現 |
|---|---|---|
| VERIFIED | 經版本化測試證實結果 | 呈現測試、run id、commit、判定者 |
| OBSERVED | 原始量測或 log | 指向不可變原始紀錄與條件 |
| HYPOTHESIS | 原理推測、待驗證關聯 | 顯示待測假設與驗證方法 |
| RECOMMENDATION | AI 下一步建議 | 益處、成本、風險、前提 |
| UNKNOWN | 檢索不到或權限不足 | 明確不推論、不杜撰 |
| REJECTED | 人類否決或測試失敗 | 記錄否決原因與可追溯證據 |

凡 AI 提供結論，前端一定要能「查看來源」。引用必須指向人類授權可讀的文件版本／資料集／測試。

## 4. Primary / Backup 的每日、每週、每月節奏

**即時：** AI 收到 Git commit、PR、Issue、CI、實驗 manifest 等事件 → 偵測影響 → 背景更新知識索引 → 高風險事件通知。
**每日：** AI 自動同步工作進展；無需 Primary 手工做日報。
**每週：** Backup 只收到本週 3–5 個最重要的變化、風險、未決事項；可直接在成果上註解。
**每月：** Backup 獨立執行一次接手任務；審查者核對實際測試證據。

共讀介面不是一對一 Chat，而是共同的 **review artifact**：同一份研究假設、波形、程式 diff 或測試報告，讓多人針對特定段落/圖表/結論留言。討論與決策附在 artifact 與 version 上。

## 5. 什麼情況必須暫停 AI、交給人類？

- 研究方向、需求或驗證標準有重大變化。
- 變更涉及安全、隱私、資安、智慧財產、外部溝通或法規。
- 需要控制實驗儀器、改動正式設備、執行破壞性操作。
- 重要研究結論證據不足、模型彼此矛盾或與物理常識衝突。
- 權限、資源使用或模型推論成本超出既定額度。
- Agent 重複失敗、工具輸出不可信、出現 prompt injection 疑慮。

## 6. Takeover Mode — 一鍵產生可操作接手包

觸發方式：排程演練、Primary 缺席、主管核准正式交接。

交接包至少包含：
1. **Snapshot：** Repo commit/tag、資料集版本、實驗 run IDs、模型與 prompt 版本。
2. **Objective：** 研究目標、成功定義、未完成假設與風險。
3. **Environment：** 必要環境、容器或設備配置、權限與操作限制。
4. **Known state：** 最近完成／失敗工作與重現方式。
5. **Next task：** 單一可驗證的真實小任務與驗收條件。
6. **Evidence links：** 原始程式、決策、測試、實驗資料來源。
7. **Unresolved gaps：** 缺失資料、未知資訊及權限阻礙。

### Shadow Takeover 演練規則

- Backup 可使用已核准的本地 AI、正式文件、沙盒工具。
- 不可詢問 Primary 或使用其個人帳號。
- 計時從取得接手包到能完成明確的工作產出；記錄無效等待與阻礙。
- Reviewer 核對結果可重現、未逾越權限；只對完成證據評級。
- 演練失敗後優先修復資料與環境缺口，重新演練。

## 7. 接手能力驗收範例（虛構）

題目：「重現一個指定測試條件下的 SOH 演算法分析，說明與前次結果差異，修改一個已知計算錯誤。」
- L1：找到指定演算法版本、資料集、執行腳本與依賴。
- L2：不靠主責執行、記錄同樣結果、能解釋不一致處。
- L3：實作修正、提交 PR，經獨立測試與審查接受。
- 若測試需要設備授權：先在記錄或模擬資料上做；實體操作仍須由有資格且經授權的人員執行。

## 8. 追蹤事件範例

~~~json
{
  "event_id": "evt-demo-001",
  "project_id": "soh-demo",
  "source_type": "git_commit",
  "source_uri": "repo://soh-demo/commit/example-sha",
  "source_revision": "example-sha",
  "risk_level": "medium",
  "change_summary": "調整低溫誤差處理方式",
  "evidence_status": "HYPOTHESIS",
  "human_approval": "pending",
  "occurred_at": "2026-11-13T01:00:00Z"
}
~~~

此範例是 schema 示意，非真實量測資料或 Git commit。

## 9. Definition of Done

任務只有在**有可定位的產出、核准要求已符合、驗證證據可重現、失敗/未驗證範圍已揭露**的情況下才可標記為 ACCEPTED。知識庫摘要與 Backup 接手包應依該版本同步更新。