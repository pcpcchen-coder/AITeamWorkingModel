# 07 — 工程實作 Backlog（給 Claude Code / Codex）

這是**規格與工單拆解**，不是宣稱程式已實作。請依優先順序建立 PR、測試與驗收證據。

> **v0.3 優先序調整（提案）：** 先實作 **Git-native Operating Kit**（工單 K0–K8，見 [13](13-opus-handoff.md)），再做本文的平台層工單。理由：Git 本身已是事件庫，流程可先用檔案 + PR + CI 運作並取得真實使用數據，再決定平台要蓋多大。
> T04–T10 的需求由 K 系列以檔案形式先行滿足；T01、T02、T03、T11、T12 延後，屆時沿用 Kit 的檔案契約。對照表見 [11 §12](11-toolkit-spec.md)。

## 0. 預計 Repo 結構（尚未全部建立）

~~~text
AITeamWorkingModel/
├── README.md
├── AGENTS.md
├── docs/                   # 制度、工作流、架構、API、治理、KPI
├── prompts/                # Agent contracts
├── demo/                   # 可離線開啟的假資料互動頁
# 之後由實作任務新增：
├── apps/web/               # React + TypeScript UI
├── services/api/           # FastAPI + authz + models
├── services/worker/        # ingestion/normalization/digest jobs
├── services/agents/        # orchestration, adapters, tool policies
├── packages/schemas/       # OpenAPI/JSON Schema/Pydantic contracts
├── infra/compose/          # local deploy templates
├── tests/                  # unit/integration/security/eval
└── examples/               # 僅限虛構與可公開測試資料
~~~

## P0：先證實關鍵價值

### T01 — Event ingestion
- GitHub webhook 接收 commit/PR/Issue/CI 事件；驗簽、idempotency、重試與 dead letter。
- 原始事件及 source revision 保存，去重不丟失資料。
- **驗收：** 同一 webhook 重送三次，僅有一個標準化事件；異常可重放。

### T02 — Evidence-aware retrieval
- PostgreSQL + Qdrant + 實驗 manifest schema，並接權限預過濾。
- 回答需有 canonical source link、revision、evidence status；不足為 UNKNOWN。
- **驗收：** 各種超出權限的查詢、prompt injection 測試不能越權或無依據斷言。

### T03 — Local inference adapter
- 提供 OpenAI-compatible adapter，model profile、timeout、retry/circuit breaker。
- 本地部署 Ollama 設定範本（不存儲密鑰）。
- **驗收：** 替換模型只改 config；timeout/離線錯誤返回可解釋結果。

### T04 — Task/approval state machine
- mission、task、artifact、decision、audit log schema。
- 不符合 approval gate 的操作在 API 端拒絕。
- **驗收：** HIGH_RISK 未核准時不能 RUNNING；已有 approval 與 artifact revision 綁定。

### T05 — Co-Review UI
- Mission board、review artifact、來源查看、Primary/Backup 留言、批准/退回。
- **驗收：** 雙人能在同一版本 artifact 留存審查；更新後舊批准不會延續。

## P1：讓備援投入最小化

### T06 — Backup weekly digest
- 每週 3–5 項重要異動；內容包括進度、來源、風險、未決議題。
- **驗收：** 無重大變化不杜撰；摘要每條可追溯。

### T07 — Takeover package generator
- 根據版本化資料組合 snapshot、runbook、依賴、任務與證據來源。
- **驗收：** Backup 可獨立取得可用接手包；缺少的資料標 UNKNOWN 而不是補造。

### T08 — Sandbox takeover runner
- 演練任務與結果收集，紀錄驗證、操作時間與失敗原因。
- **驗收：** 不詢問 Primary 也能完成已指定的可重現案例；權限不足正確被阻止。

### T09 — Portfolio / KPI
- 支援能力矩陣、風險、演練紀錄、工時與驗證證據。
- **驗收：** 看板統計與底層事件一致，不能由 LLM 任意填數值。

## P2：擴展與優化

### T10 — Multi-agent orchestration
- Planner、Research、Engineer、Validator、Handover Agent contracts。
- **驗收：** 每個輸出保留來源、工具紀錄和 approval chain；超限自動 BLOCKED。

### T11 — Observability & model evaluation
- Trace、模型指標、引用正確性、工具成功率、回歸評測。
- **驗收：** 模型更新前後能重跑相同 eval suite，產生差異報告。

### T12 — 研究設備 connector（需另行資安審核）
- 先唯讀／離線模擬，明確簽核後才討論設備操作。
- **驗收：** 未授權狀態絕不會發出寫入／控制命令。

## 工程規範

- 每項任務走獨立分支／PR；附變更目的、風險、測試與回退方式。
- 禁止用示範假資料作為已連接真實 Git/實驗系統的證據。
- 所有模型版本、授權及模型本地推論需求在實機 benchmark 後再確定。
- 每次提交都更新相關 docs、API schema 及可重現測試。
- 交付目標為「可以讓另一位 Agent 或工程師接手」，而非只在作者機器跑通。

## 可以直接交給 Coding Agent 的啟動指令

~~~text
請閱讀 README.md、AGENTS.md、docs/01–07 與 prompts/agent-contracts.md。
本 repo 目前主要是架構與流程規格；不得宣稱已部署真實 AI 研發服務。
請先提出 T01–T05 的 MVP 分支實作計畫與驗收案例，
分別標出資料權限、人工核准、安全風險及測試依賴。
先交付 T01（事件去重 + 測試）與 T04（狀態機 + approval gate），
在 PR 中附完整測試證據；沒有機構設備/密鑰時使用假資料與 mock。
禁止直接向實體設備發命令；不要提交研究機密或 API secrets。
~~~