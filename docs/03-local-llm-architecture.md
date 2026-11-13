# 03 — 本地 LLM 與 AI 研發平台技術架構

**定位：** 可部署方案候選（不是硬體已驗證、工具已安裝或服務已上線的聲明）。

## 1. 系統分層

~~~text
[Browser: Mission Control / Co-Review / Takeover]
     | SSO session + project-scoped authorization
     v
[API Gateway / FastAPI / Policy Engine]
     |                     |                  |
     |                     +--> PostgreSQL (task, review, run, audit)
     |                     +--> Object Store (evidence, raw manifest)
     |                     +--> Job Queue / Workers
     |                                |
     |                      [Event Collectors]
     |                      Git / PR / CI / experiment / docs
     |
     +--> [Agent Orchestrator]
            |-- Planner / Research / Engineering / Validator / Handover
            |-- model routing via OpenAI-compatible adapter
            |-- tool execution via sandbox and explicit policy
            |
            +--> [Evidence-aware Retrieval]
                   | RBAC/ABAC filter FIRST
                   +--> keyword + vector retrieval + reranker
                   +--> Qdrant index + canonical source references
            |
            +--> [Inference Servers]
                   Ollama (pilot) / llama.cpp / vLLM (scale)
                   [Optional] LiteLLM gateway for routing and quota
~~~

**Source of Truth**：Git/設計決策、版控實驗 manifest、原始量測與測試證據。RAG 索引、LLM 回答、對話歷史都只是衍生資料，可重建。

## 2. P0 / P1 / P2 技術選型

| 層 | P0（先實作） | P1/P2（達到需求再導入） |
|---|---|---|
| UI | React + TypeScript，搭配單檔 demo 供討論 | 更完整可視化、對註解的即時同步 |
| API | FastAPI、OpenAPI 規格 | 多租戶 API gateway |
| Auth | 現有 AD/SSO/OIDC 整合，DEV 使用 fake data | 細粒度 ABAC、資料分級 |
| DB | PostgreSQL | 分割、稽核封存 |
| Vector | Qdrant | Hybrid search、rerank、品質評測 |
| Events | Git webhook + queue workers | 文件系統、實驗管理系統 connector |
| Inference | Ollama local + adapter | vLLM（GPU 多人併發），LiteLLM routing |
| Chat | Open WebUI 選配 | 與專用 Mission Control 整合 |
| Coding | Continue / CLI Agent 在授權沙盒 | 多 agent 協作與測試排程 |
| Observability | request id、工具呼叫與原始事件 log | Langfuse 或同等 trace/eval |

**不要一次部署所有產品**；先證明資料擷取、引用、共讀與接手可行。

## 3. 本地模型選型與驗證

模型不與系統核心耦合，每種用途建 ModelProfile：id、provider、base_url、quantization、context_limit、allowed_tasks、data_classification、latency_threshold、cost_estimate、eval_version。

候選（需查核可用版本、開源授權、推論速度）：
- 低延遲中文摘要／分類：小型通用指令模型（例如 Qwen3.5 9B 類級）。
- 較複雜研究推論：較大型指令／推理模型。
- Coding agent：可良好支援工具呼叫與長程程式任務的 coding 模型。
- Retrieval：中文/英文 embedding + reranker；對專有名詞採 hybrid retrieval。
- 安全及指令遵循：須在研究資料集上另外評測。

初期單機 32GB 統一記憶體可測試小型量化模型，但**可容納權重不表示多使用者、長上下文或工具呼叫有足夠效能**；須量測吞吐、TTFT、VRAM/RAM、KV cache、同時請求、溫度與穩定度。不可僅依模型檔案大小規劃伺服器。

### 模型評測集（公開 repo 不附內部資料）

- 至少 50–100 個經授權的真實研發 QA / 搜尋 / 版本追溯問題。
- 各選 10–20 個：跨文件推理、中文技術歧義、來源不足時拒答、程式修復與測試、接手環境還原。
- 每題保存 ground-truth / 參考證據；評測引用正確、回答正確、誤導率、工具成功率、時間與資源消耗。
- 測試資料集版本、模型版本、prompt 版本與每次結果可追溯，避免在相同資料上過度調參。

## 4. Evidence-aware RAG

流程：
1. Source connector 讀取 **使用者或服務帳戶有權存取** 的資料，建立不可變版本標籤。
2. 去除可疑或敏感區段，標記 tenant/project/ACL/classification、資料來源、revision、有效時間。
3. 根據文檔段落、程式符號、測試 run 與實驗階層分段索引；保存 canonical source uri。
4. 查詢時**先**依當前使用者與專案權限縮小檢索範圍，再作 keyword + vector retrieval + rerank。
5. 回答必須給可點回原始資料的版本化引用；來源不足輸出 UNKNOWN。
6. 結果留存 model/prompt/index version；索引可被來源事件觸發增量更新或重建。

**限制：** Qdrant payload filter 不是完整身份驗證；認證授權仍由伺服器層負責。不能把未信任文件的內容當成新的 system prompt 或工具指令。

## 5. Event pipeline 的可靠性

Webhook → 驗證簽章 → 去重（source + event id）→ queue → normalize → evidence link → summarizer → review artifact → 通知。

- 至少一次事件投遞（at-least-once）與 idempotency key。
- 事件可能延遲、重排、重複；不把 receipt time 當 experiment time。
- 失敗進 dead-letter queue，提供人工重跑、重放與診斷。
- 大型實驗資料只登錄 manifest、checksum、版本與安全存取位置；禁止直接複製到公開 repo。
- 摘要更新是**衍生快取**，不能覆蓋原始紀錄。

## 6. Agent 執行隔離

- 每個 Agent 有固定可用工具的 allowlist（例如 repo read、issue read、sandbox code execution）。
- 工具執行在容器/沙盒，限制 CPU、GPU、記憶體、時間、網路、檔案掛載、憑證及可寫路徑。
- 寫入用分支 + PR + test，不能默默覆蓋預設分支；外部影響操作由人類批准。
- 限制每個任務最大輪數、token、失敗重試和資源額度，防止失控迴圈。
- 不以 AI 自我回覆「核准」取代人類授權。

## 7. 第一版最小部署拓樸

~~~text
R&D LAN / controlled environment
  browser
    |
  reverse proxy + HTTPS + OIDC
    |
  FastAPI ---- PostgreSQL
    |           |
  worker ---- event queue
    |
  Ollama (local inference)
    |
  Qdrant ---- approved file store
    |
  Git integration / experiment manifests
~~~

正式部署至少需資料分類、受控網路、備份、監控、災難復原、日誌保留與權限稽核。模型可用並不代表整套系統已符合機構規範。

## 8. 核心非功能性要求

- **可靠性：** 接收重複事件不得產生重複任務或發送重複重要通知。
- **可觀測性：** 每項 AI 產出可查輸入來源、模型、prompt、工具呼叫及驗證。
- **安全：** 跨專案資料不得互相出現在檢索結果；模型不可直接讀到未授權秘密。
- **可替換：** 更換本地 LLM 不需改動主要 UI 與研發資料 schema。
- **復原：** DB/manifest 及授權文件備份，RAG 向量可重建。
- **可用性：** 網路中斷或模型不可用時，仍可瀏覽先前核准的狀態與原始證據。