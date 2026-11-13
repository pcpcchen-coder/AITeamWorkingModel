# 04 — AI Mission Control / Human Co-Review UI 與 API 規格

**產品目標：** 人類不是盯著 AI 的逐 token 回覆，而是用共享介面檢視 AI 的任務、產出、推論、證據、風險與待決策事項。

## 1. UI 資訊架構

~~~text
Mission Control
├── Portfolio（主管）：專案風險與備援能力總覽
├── Project（所有授權成員）：AI 任務進度 / 決策 / 風險
│   ├── AI task graph + status
│   ├── Evidence feed：source, version, artifact type, risk
│   ├── Review workspace：同一成果上的多人評論/決策
│   ├── Research memory：已驗證事實 / 假設 / 未知
│   └── Activity timeline：可稽核事件
├── Backup（備援）：每週重要差異 + 1 題挑戰
├── Takeover：獨立接手任務、接手包、驗證步驟、結果
└── Admin：模型、權限、工具政策、資料連線、評測
~~~

第一版建議將 UI 稱為 **AI R&D Mission Control**；「Backup Dashboard」只是其中一個角色工作區。

## 2. 主要頁面與使用行為

### A. Project Mission Board
- 頂部：研究目標、當前階段、Primary/Backup、AI 執行狀態、資料最新同步時間。
- 中區：任務列表，顯示 PROPOSED / RUNNING / VERIFYING / IN_REVIEW / ACCEPTED / BLOCKED。
- 右區：需要人類決策的優先清單、風險、資源配額。
- 點進任務顯示：可重現輸出、來源、測試 run、模型版本、阻擋原因。
- **不以 AI 自估百分比偽裝真進度。** 進度可由驗收通過的明確任務加權計算。

### B. Human-AI Co-Review
- 每份成果是 versioned artifact（文獻比較、設計 ADR、PR、模型圖、波形、測試報告）。
- Primary/Backup 在固定 artifact 版本的段落、圖表、程式行或整份成果上加註評論。
- AI 可提出修改建議，但**不會自動替人類按批准**。
- 人類決策：APPROVE / REQUEST_CHANGES / REJECT / DEFER。
- 顯示「此結論的原始證據」「未驗證假設」「先前版本與異動」。

### C. Backup Weekly Digest
- 只顯示 3–5 條重大變更，附摘要、差異、影響、原始連結、是否需要行動。
- 清楚區分「已讀」、「已理解」、「能接手」；已讀不影響 L2/L3 評級。
- 若本週無重要變更，顯示「無重大異動」，不要為了填滿產生虛假進度。

### D. Takeover Mode
- 快照接手包、環境還原清單、真實且可驗證的任務、步驟進度。
- 啟用演練時記錄開始時間、證據、權限失敗與求助紀錄。
- Primary 不介入；Reviewer 依測試證據評級。
- AI 可作導師，但每條操作建議必須可追溯到實際版本和安全 SOP。

### E. Portfolio / Manager
- 專案列表、Primary、Backup、備援 L0–L3、上次演練、風險趨勢。
- 呈現未驗證覆蓋範圍與過期知識。
- 能看「誰離開會導致哪個專案停止」，但權限仍限制原始技術細節。

## 3. 建議的 API（MVP）

| Method | Endpoint | 用途 |
|---|---|---|
| GET | /api/projects | 取得授權專案 |
| GET | /api/projects/{id}/missions | 專案 AI 任務與狀態 |
| POST | /api/projects/{id}/missions | 建立任務／目標（核准後才執行） |
| GET | /api/projects/{id}/events | 可追溯事件流 |
| GET | /api/projects/{id}/artifacts | 版本化 AI 產物 |
| GET | /api/artifacts/{id} | 內容、來源、證據與 review |
| POST | /api/artifacts/{id}/comments | 新增共讀註解 |
| POST | /api/artifacts/{id}/decisions | 人類核准、駁回、變更要求 |
| GET | /api/projects/{id}/backup-digest | 每週備援摘要 |
| POST | /api/projects/{id}/takeover-sessions | 產生接手演練（須授權） |
| POST | /api/takeover-sessions/{id}/submissions | 提交測試證據 |
| GET | /api/portfolio/risk | 主管風險與備援分級 |
| GET | /api/evidence/{id} | 取回授權範圍內來源與 hash |

API 應支援 cursor pagination、request_id、idempotency_key、審計事件與一致錯誤碼；不能僅靠前端角色顯示來實作權限。

## 4. 最小資料表（抽象）

~~~text
projects (id, classification, primary_user_id, backup_user_id, status)
project_memberships (project_id, user_id, role, scopes)
missions (id, project_id, objective, state, risk_class, policy_version)
tasks (id, mission_id, state, assigned_agent, acceptance_criteria, budget)
events (id, source, external_id, source_revision, occurred_at, received_at)
artifacts (id, task_id, type, revision, content_uri, evidence_state)
artifact_evidence (artifact_id, source_uri, source_revision, checksum)
reviews (id, artifact_id, artifact_revision, author_id, anchor, comment)
decisions (id, artifact_id, version, actor_id, outcome, timestamp)
takeover_sessions (id, project_id, backup_id, snapshot, state, started_at)
takeover_results (session_id, verifier_id, evidence_uri, level, completed_at)
model_runs (id, model_profile, prompt_version, tools, tokens, latency_ms, trace_id)
audit_log (id, actor_id, action, object_ref, policy_decision, timestamp)
~~~

重要 invariant：
- 只有授權的人類身份可以使 HIGH_RISK 任務越過 AWAITING_APPROVAL。
- artifact revision 一旦審查不可悄悄改寫；新內容必須新 revision 與新審查。
- Backup L2/L3 必須引用 takeover_results 的驗證證據，不能由聊天摘要欄位直接更新。
- 來源被撤銷授權或刪除後，索引和快取也要清除或失效。

## 5. Event / Review 前端資料契約（示意）

~~~json
{
  "artifact_id": "demo-a01",
  "revision": 3,
  "title": "低溫 SOH 誤差評估（示意）",
  "status": "IN_REVIEW",
  "evidence_state": "HYPOTHESIS",
  "sources": [
    {"uri": "repo://demo/experiments/run-001", "revision": "v1", "verified": false}
  ],
  "required_approver_role": "primary",
  "comments": [
    {"author_role": "backup", "anchor": "conclusion-1", "body": "如何排除倍率影響？"}
  ]
}
~~~

## 6. Demo 與正式版差異

[demo/mission-control.html](../demo/mission-control.html) 為**單檔離線概念驗證**；預設使用虛構資料，沒有真實後端、權限、持久化、模型推論或 Git 存取。可展示工作流，但不可把 demo 的「批准」當作正式的審核紀錄。

正式版應由 FastAPI + DB 提供跨人員一致的事件與審查；再串本地 LLM、Git webhook、RAG、測試 runner。