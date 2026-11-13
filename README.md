# AI Team Working Model — AI-Driven R&D

> **Status:** Architecture & operating-model proposal (v0.2, 2026-11-13). This repository is **not** a deployed AI platform.
>
> **Language:** 繁體中文為主；code / API / schema 保留英文名稱。
>
> **Public repository notice:** 使用虛構範例。請勿提交內部研究結果、未公開專利、客戶資料、帳密、設備控制憑證或未授權資料。

## 願景

**AI 主導研發任務執行，人類共同閱讀 AI 的進度、成果、推論和建議；Primary 負責研究方向與決策，Backup 以最小日常負擔維持可驗證的接手能力。**

不是「增加第二位全職開發者」，也不是「把研發判斷全部交給 LLM」；而是建立可追溯、可審查、可接手的 **AI-Native R&D Operating Model**。

```text
Human Primary ── goals / approvals ──┐
                                     ├─> Mission Control / Co-Review UI
Human Backup ── challenges / takeover┘             │
                                                   ▼
                                    AI Orchestrator / Policy Engine
                                                   │
                      ┌────────────────────────────┼───────────────────────┐
                      ▼                            ▼                       ▼
                 Research Agent              Engineer Agent          Validator Agent
                      └────────────────────────────┼───────────────────────┘
                                                   ▼
                                    Evidence / Git / Experiments
                                                   ▲
                                    Local LLM + RAG + Access Control
```

## 三項核心能力

| 能力 | 操作方式 | 成功證據 |
| --- | --- | --- |
| **AI R&D Execution** | AI 在已授權範圍內規劃、分析、實作、測試、回報 | 任務紀錄、程式差異、可重現測試 |
| **Human–AI Co-Review** | Primary / Backup 對同一份 AI 產物共同審閱、評論、挑戰假設 | 有來源、審查紀錄、決策狀態 |
| **R&D Continuity** | Backup 只看重大差異；必要時啟動 Takeover Mode | 獨立接手演練、環境重建與驗證證據 |

## 文件導覽

| 文件 | 用途 |
| --- | --- |
| [01 願景與角色制度](docs/01-operating-model.md) | Primary、Backup、Reviewer、AI；L0–L3 |
| [02 任務執行與共讀流程](docs/02-workflow-and-takeover.md) | AI 事件工作流、審核門檻、接手演練 |
| [03 本地 LLM 技術架構](docs/03-local-llm-architecture.md) | 本地模型、RAG、部署、資料流 |
| [04 UI / API 規格](docs/04-mission-control-spec.md) | Mission Control、資料結構、介面與 API |
| [05 安全與治理](docs/05-security-and-governance.md) | 權限、機密、Agent 工具防護、審計 |
| [06 導入路線圖與 KPI](docs/06-rollout-and-kpi.md) | 90 天分階段導入、驗收標準 |
| [07 工程實作 Backlog](docs/07-engineering-backlog.md) | 可交給 Claude Code / Codex 的任務拆解 |
| [08 討論整合與決策](docs/08-decision-log.md) | 原始問題 → 目標模式、ADR 草案、待確認條件 |
| [Agent 工作契約](prompts/agent-contracts.md) | Orchestrator / Research / Engineer / Validator / Handover |
| [協作規範](AGENTS.md) | 對人類與 Coding Agent 的共同規範 |
| [互動 Demo](demo/mission-control.html) | 單檔 HTML、模擬資料、離線可用 |

## MVP 優先交付

1. **事件擷取：** Git / PR / Issue / CI / 實驗 manifest → 有來源的事件庫。
2. **AI 工作摘要：** 自動歸納「完成、進行中、風險、待決策」，標示證據／未知。
3. **雙人共讀：** Primary / Backup 同看 AI 產出並提出討論，決策可追溯。
4. **Takeover Mode：** 產生接手包，由 Backup 獨立完成沙盒任務。
5. **主管看板：** 備援分級、接手演練成果與風險，而非單看 AI 自報進度。

## 技術選型（候選，需實測）

- **Frontend:** React + TypeScript；通用對話入口可使用 Open WebUI。
- **Backend:** FastAPI + PostgreSQL + background worker。
- **Retrieval:** Qdrant + hybrid retrieval + reranker；資料先經授權過濾。
- **Inference:** Ollama（單機試點）→ 規模化再考慮 vLLM / LiteLLM；採 OpenAI-compatible adapter。
- **Source of truth:** Git / issue / design decision / experiment manifest / evidence；**LLM 摘要不是事實來源**。
- **Observability:** 測試紀錄、模型與 prompt 版本、工具調用與審查紀錄；量大後考慮 Langfuse。

模型名稱與 GPU 需求不在此硬寫為最終選擇；需以資料安全規範、授權、中文與工程任務 benchmark 決定。

## 快速開始

1. 先讀 [01 願景與角色制度](docs/01-operating-model.md) 和 [02 工作流程](docs/02-workflow-and-takeover.md)。
2. 直接用瀏覽器開啟 [離線 Demo](demo/mission-control.html)，體驗共讀、任務審核與接手。
3. 依 [90 天導入計畫](docs/06-rollout-and-kpi.md) 選 2–3 個不同性質的試點。
4. 交給 AI Coding Agent 前，先讓它閱讀 [AGENTS.md](AGENTS.md) 和 [工程 Backlog](docs/07-engineering-backlog.md)。

**邊界：** 第一階段 AI 僅能在可控的資料、程式與沙盒環境中執行。正式設備控制、正式部署、具安全影響的研究結論與重要技術決策均需要人類核准。

## 版本與來源

本版是 2026-11-13 前的設計討論整理：從「單人專案 → Primary/Backup」延伸至「AI Shadow → AI-Driven R&D + Human Co-Review」。文內時間、投入比例與成功目標都是**試行假設**，不是部署現況或已驗證績效。
