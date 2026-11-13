# AI Team Working Model — AI-Driven R&D

> **Status:** Architecture & operating-model proposal (v0.4, 2026-11-13). This repository is **not** a deployed AI platform；v0.3 規劃的 `aitw` 工具尚未實作。
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
| [09 執行流程 Playbook](docs/09-execution-playbook.md) | **v0.3** 九步流程、共讀協定、共推協定、節奏、RACI、手動模式 |
| [10 軟／韌／硬領域規範](docs/10-domain-profiles-sw-fw-hw.md) | **v0.3** 各領域的 AI 自主度、驗證階梯、證據、Gate、介面契約、人類任務 |
| [11 輔助工具規格](docs/11-toolkit-spec.md) | **v0.3** Git-native Operating Kit：檔案契約、`aitw` CLI、Gate、Agent／Forge 整合、看板 |
| [12 操作範例](docs/12-operating-examples.md) | **v0.3** 一個橫跨軟韌硬的虛構 Mission 從頭走到尾 |
| [13 開發交付包](docs/13-opus-handoff.md) | **v0.3** 實作工單 K0–K8、不變量、啟動指令、待確認事項 |
| [14 GitLab 執行方式](docs/14-gitlab-profile.md) | **v0.4** AI 開發 × GitLab 共同 review：平台對照、依授權等級的強制方式、漸進導入階梯 |
| [Kit 樣板與檢查表](kit/README.md) | 現在就能用的手動模式樣板 |
| [Agent 工作契約](prompts/agent-contracts.md) | Orchestrator / Research / Engineer / Validator / Handover |
| [協作規範](AGENTS.md) | 對人類與 Coding Agent 的共同規範 |
| [互動 Demo：Mission Control](demo/mission-control.html) | 單檔 HTML、模擬資料、離線可用 |
| [互動 Demo：工作流程案例示範](demo/workflow-walkthrough.html) | **v0.4** 一步步播放虛構案例：三方接力、看板變化、Gate 模擬器；可切換 GitLab／GitHub 用語 |

## v0.3：先讓流程能操作（Git-native Operating Kit）

01–08 定義原則與目標平台；v0.3 補上「明天就能照做」的一層——**流程先以版控檔案 + PR + CI + CLI 運作，Mission Control 平台之後只是讀同一份資料的檢視層。**

- **檔案是狀態、PR 是共讀面、CI 是關卡**；人類在 forge 上的已驗證行為是核准正本。
- **AI 不能自己把結果標成 VERIFIED**；只有 CI 重跑或人類依原始資料簽認可以。
- **軟／韌／硬採不同的自主度與驗證階梯**；燒錄、上電、量測、送板一律由人執行，AI 準備與分析。
- **共推進度**：決策佇列與時限、人類任務接力、方向指示、WIP 上限保護人類注意力。

- **GitLab 與 GitHub 皆可**：單位既有的「AI 開發、GitLab 上 review」案例是首個試點候選，可從 MR 樣板開始漸進導入（[14](docs/14-gitlab-profile.md)）。

從 [09](docs/09-execution-playbook.md) 開始讀；想直接看實例讀 [12](docs/12-operating-examples.md) 或開啟 [工作流程案例示範](demo/workflow-walkthrough.html)。實作優先序調整見 [07](docs/07-engineering-backlog.md) 開頭與 [13](docs/13-opus-handoff.md)。

## MVP 優先交付（平台層，v0.2 規劃）

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
4. 交給 AI Coding Agent 前，先讓它閱讀 [AGENTS.md](AGENTS.md) 和 [開發交付包](docs/13-opus-handoff.md)（Operating Kit 工單）；平台層工單見 [工程 Backlog](docs/07-engineering-backlog.md)。
5. 不等工具：依 [kit/README.md](kit/README.md) 的手動模式，用樣板先跑一輪。

**邊界：** 第一階段 AI 僅能在可控的資料、程式與沙盒環境中執行。正式設備控制、正式部署、具安全影響的研究結論與重要技術決策均需要人類核准。

## 版本與來源

本版是 2026-11-13 前的設計討論整理：從「單人專案 → Primary/Backup」延伸至「AI Shadow → AI-Driven R&D + Human Co-Review」，v0.3 再加入可操作的執行流程、軟韌硬領域規範與輔助工具規格。文內時間、投入比例與成功目標都是**試行假設**，不是部署現況或已驗證績效。
