# kit/agent/claude-code — 四個協作 Agent 與技能（Claude Code）

**狀態：** v0.1 初版 · 2026-11-16 · 依 [docs/19](../../../docs/19-agent-roles.md) 建置。每個 Agent 在一個虛構小例子上試跑過一次（見 [trials/](trials/README.md)）；**尚未在真實專案上試用**。試跑由 AI 執行，結果標籤最高為 OBSERVED。
**運作方式：** 手動模式。不依賴 `aitw` 指令列工具；登錄證據、產生共讀包等步驟用 [`kit/templates/`](../../templates/) 的樣板與白話步驟完成。
**對象工具：** Claude Code。立場與權限的設計與工具無關；換工具時只需改寫檔案格式。

## 1. 內容

```
kit/agent/claude-code/
├── agents/                       # 子代理定義（每個 Agent 一個 .md）
│   ├── mission-executor.md       # 執行者
│   ├── independent-validator.md  # 驗證者
│   ├── coread-guide.md           # 共讀助理
│   └── cadence-reporter.md       # 節奏助理
├── skills/<技能名>/SKILL.md      # 21 個技能
└── trials/                       # 虛構示範的試跑紀錄
```

| Agent | 為誰工作 | 技能 | 工具（由定義檔強制） |
|---|---|---|---|
| `mission-executor` 執行者 | 任務主責 | `mission-intake`、`wp-plan`、`wp-run`、`decision-request`、`review-packet`、`rework`、`human-task`、`takeover-pack`；領域技能 `domain-sw`、`domain-fw`、`domain-hw` | Read, Grep, Glob, Edit, Write, Bash, Skill |
| `independent-validator` 驗證者 | 審查流程（不為作者） | `verify-wp`、`critique-plan`、`premerge-check` | Read, Grep, Glob, Bash, Write（**無 Edit**） |
| `coread-guide` 共讀助理 | 個別審查者 | `coread`、`shadow-compare`、`tutor` | Read, Grep, Glob（**無寫入、無執行指令**） |
| `cadence-reporter` 節奏助理 | 整個團隊 | `daily-brief`、`weekly-digest`、`sync-agenda`、`case-review` | Read, Grep, Glob, Bash, Write（**無 Edit**） |

每個 Agent 定義檔都包含 docs/19 §4 的七項：什麼時候用與不該用、立場、工具與寫入範圍、絕不做的事與理由、停下來問的條件、回報格式、模型建議。

### 技能如何綁到 Agent

| 技能類別 | 綁定方式 | 效果 |
|---|---|---|
| 驗證者的三個技能、節奏助理的四個技能 | `context: fork` + `agent: <Agent 名>`，且 `disable-model-invocation: true` | 不論在哪個對話輸入 `/verify-wp` 等，都會**另開一個該 Agent 的子代理**執行：帶該 Agent 的工具限制、**不帶呼叫者的對話脈絡**；只能由人輸入啟動，模型不會自己叫用 |
| 共讀助理的三個技能 | 不分叉（需要多輪對話）；`disallowed-tools: Edit, Write, NotebookEdit, Bash`；`disable-model-invocation: true` | 技能啟用期間移除寫入與執行指令的工具；建議在 `coread-guide` 的對話中使用 |
| 執行者的技能 | 不分叉（需要訪談與延續規劃的脈絡） | 請在 `mission-executor` 的對話中使用；在一般對話中使用時，工具不受執行者定義限制 |

## 2. 安裝到一個專案 repo（GitLab 與 GitHub 相同）

Claude Code 讀的是 repo 內的檔案，與平台無關。以下步驟在 GitLab 與 GitHub 上都一樣；差別只在第 5 步的平台設定。

1. **複製檔案**到專案 repo 的根目錄：
   ```bash
   # 在專案 repo 根目錄執行；<kit> 是本 repo 的 kit/ 路徑
   mkdir -p .claude
   cp -r <kit>/agent/claude-code/agents  .claude/agents
   cp -r <kit>/agent/claude-code/skills  .claude/skills
   ```
   結果應為 `.claude/agents/*.md` 與 `.claude/skills/<技能名>/SKILL.md`。
2. **放入樣板**：把 `kit/templates/`（以及需要的 `kit/checklists/`、`kit/team/`）複製到專案的 `kit/` 下。技能用 `kit/templates/<樣板>` 這個路徑引用它們；放在別處時，請一併修改技能內的路徑。
3. **寫常駐規則**：專案根目錄的 `AGENTS.md` 加入 [`prompts/handoff-prompts.md` §2](../../../prompts/handoff-prompts.md) 的「與人類協作的規則」，以及專案涉及的領域補充規則（[docs/18](../../../docs/18-domain-handoffs.md) §1.1、§2.1、§3.1）。依專案調整路徑。
   - **UNKNOWN：Claude Code 是否自動讀取 `AGENTS.md`。** 官方子代理文件明寫會載入 `CLAUDE.md`；`AGENTS.md` 在本次查證中未取得逐字說明。保險的作法：在專案根目錄放一個 `CLAUDE.md`，內容只有一行 `@AGENTS.md`（以匯入方式引用；匯入語法請以官方文件為準），或直接把規則放進 `CLAUDE.md`。
4. **建立角色矩陣**：依 `kit/team/role-matrix.md` 寫出誰是各任務的主責、備援與各領域負責人。執行者與節奏助理會讀它。
5. **平台設定（真正的保證）**：Agent 用獨立的機器身份提交，**沒有合併與核准權限**；主幹受保護，必須經 MR／PR 與人類核准，新提交使舊核准失效。GitLab 的作法見 [docs/14](../../../docs/14-gitlab-profile.md)，GitHub 見 [docs/11 §9](../../../docs/11-toolkit-spec.md)。Agent 定義檔裡的「不合併」只是提醒，不是保證。
6. **提交並送 MR／PR**：`.claude/agents/`、`.claude/skills/` 屬於專案設定，請經人類審查後合併。
7. **確認載入**：在 repo 根目錄啟動 Claude Code，輸入 `/` 應看到 `wp-run`、`verify-wp`、`coread` 等技能。新建的 `.claude/agents/` 目錄若在啟動時不存在，需要重新啟動 Claude Code 才會被偵測（官方文件說明）。

**不需要也沒有安裝：** hook、`settings.json` 的權限規則、相依套件。

## 3. 每個 Agent 什麼時候用、怎麼叫用

叫用方式（官方文件確認的兩種）：

- **以 Agent 身分開整個對話**：`claude --agent <Agent 名>`。整個對話都使用該 Agent 的系統提示與工具限制（試跑時以 `-p` 模式確認工具清單確實被限制，見 trials）。**建議的主要用法**：每個人依當下的角色開對應的對話。
- **在一般對話中委派**：直接說「請用 independent-validator 驗證 WP-002」，或輸入綁定該 Agent 的技能（例如 `/verify-wp WP-002`）。

| 情境 | 誰 | 怎麼做 |
|---|---|---|
| 開新任務 | 主責 | `claude --agent mission-executor`，輸入 `/mission-intake <一兩句背景>`，回答問題 |
| 拆工作包 | 主責 | 同一類對話，`/wp-plan M-001` |
| 核准計畫前挑毛病 | 主責 | **開新對話**，`/critique-plan M-001 <Plan MR／PR>`（自動在驗證者中執行） |
| 執行工作包 | 主責交付 | `claude --agent mission-executor`，`/wp-run WP-003 <目的與特有要求>` |
| AI 開了決策請求 | 主責 | 在平台留言決定，再於執行者對話 `/decision-request resolved DR-001 <決定與理由>` |
| 獨立驗證 | 主責或審查者 | **開新對話**（建議用不同模型，見第 4 節），`/verify-wp WP-003` |
| 寫共讀包 | 主責交付 | 執行者對話，`/review-packet WP-003` |
| 審查者帶讀 | 審查者本人 | `claude --agent coread-guide`，`/coread WP-003 備援 20` |
| 合併前自查（選用） | 合併者 | `/premerge-check <MR／PR> WP-003 <平台上的核准與 CI 狀態>` |
| 返工 | 主責交付 | 執行者對話，`/rework WP-003 1 <要改的事>` |
| 人類任務 | 主責、合格執行者 | 執行者對話，`/human-task prepare WP-005 ...`；人填完紀錄後 `/human-task analyze WP-005` |
| 主責缺席、對話太長 | 代理主責、主責 | 執行者對話，`/takeover-pack package M-001 <交接紀錄連結>` 或 `/takeover-pack handoff WP-003` |
| 每日簡報、週摘要 | 個人、備援 | `/daily-brief <代號>`、`/weekly-digest M-001 2026-W47 <備援>` |
| 每週團隊會 | 協調人 | `/sync-agenda agenda <日期> 45`；會後 `/sync-agenda minutes <日期> <結論全文>` |
| 每月案例回顧 | 協調人 | `/case-review 2026-11` |
| 見習審查、學習型工作包 | 見習者、學習者 | `claude --agent coread-guide`，`/shadow-compare ...`、`/tutor ...` |

**不要做：** 在執行者的同一個對話裡請它驗證自己；用共讀助理改分支；用節奏助理評價個人。

## 4. 模型設定（驗證者建議與執行者不同）

四個定義檔都寫 `model: inherit`（跟隨啟動它的對話），**沒有寫死模型名稱**。要讓驗證者用不同的模型，任選一種：

| 作法 | 怎麼做 | 範圍 |
|---|---|---|
| 啟動時指定 | `claude --agent independent-validator --model <別名或完整模型 ID>` | 這一次對話 |
| 改定義檔 | 把 `independent-validator.md` 的 `model: inherit` 改成別名或完整模型 ID | 專案所有人 |
| 環境變數 | `CLAUDE_CODE_SUBAGENT_MODEL=<模型>`（官方文件列出；優先序低於定義檔的 `model` 欄位） | 該環境所有子代理 |

官方文件列出 `model` 可接受：別名 `sonnet`、`opus`、`haiku`、`fable`，完整模型 ID，或 `inherit`。哪些模型可用取決於你的帳號與組織設定。

**注意：** 從一般對話用 `/verify-wp` 分叉時，若定義檔是 `inherit`，驗證者會用**與該對話相同**的模型；要不同的模型，請用上表前兩種作法。做不到不同模型時，至少是**全新的對話**（分叉技能本身就不帶呼叫者的對話脈絡）。

## 5. 靠自律、未被工具強制的限制

Agent 定義檔的 `tools` 欄位只能決定「有哪些工具」，**不能限制寫到哪個路徑、能執行哪些指令**（官方文件的 `tools` 只接受工具名稱；路徑與指令層級的規則屬於 `settings.json` 的權限設定，本次不在範圍）。以下限制只寫在定義與技能的文字裡，**靠模型遵守，沒有被工具強制**：

| # | 限制 | 哪個 Agent | 為什麼工具擋不住 |
|---|---|---|---|
| 1 | 只修改工作包 `scope.paths` 內的檔案 | 執行者 | 有 Edit／Write／Bash，可寫任何路徑 |
| 2 | 不修改 `.aiteam/`、CI、負責人設定、驗收條件、人填的紀錄 | 執行者 | 同上 |
| 3 | 不合併、不核准、不改分支保護 | 執行者、驗證者、節奏助理 | 有 Bash 就可能呼叫平台 CLI；**真正的保證是機器身份沒有這些權限** |
| 4 | 不執行、不產生設備控制指令 | 執行者、驗證者、節奏助理 | 有 Bash；**真正的保證是執行環境沒有接設備** |
| 5 | 只寫驗證報告，不改產品程式與測試 | 驗證者 | 沒有 Edit，但 Write 可以覆寫任何檔案，Bash 也能改檔 |
| 6 | 不提交、不推送、不切換作者的分支 | 驗證者 | 有 Bash |
| 7 | 只寫節奏類檔案、只用唯讀查詢 | 節奏助理 | 有 Write 與 Bash |
| 8 | 不評價個人、不編造進度 | 節奏助理 | 內容層面，任何工具都擋不住 |
| 9 | 不給核准、不先給挑戰題答案、不淡化漏看 | 驗證者、共讀助理 | 內容層面 |
| 10 | 驗證者與執行者用不同模型 | 驗證者 | 定義檔是 `inherit`；要靠人設定 |
| 11 | 執行者技能只在執行者對話中使用 | 執行者 | 執行者技能沒有綁定 Agent；在一般對話中使用時，工具是該對話的工具 |

**被工具強制的部分：** 共讀助理只有讀取與搜尋（不能寫檔、不能執行指令）；驗證者與節奏助理沒有 Edit；驗證者、共讀助理、節奏助理沒有 Skill 與派生子代理的工具；驗證者與節奏助理的技能一律在各自的 Agent 中分叉執行；共讀技能啟用期間移除寫入與執行指令的工具（**這一項試跑時未被觀察到**：模型在嘗試編輯前就拒絕了，見 trials/t3）。以上各項的試跑觀察見 trials。

**防護 hook 不在本次範圍**（docs/13 的 K4）。若要把第 1、3、4、5 項變成強制，有兩條路，都需要 owner 決定：(a) 專案 `.claude/settings.json` 的 `permissions.deny` 規則（可限制路徑與指令樣式）；(b) K4 的防護 hook。兩者都需要列出指令樣式，必須與 PR #3 的設備指令掃描協調。

## 6. 官方格式查證

查證日期 2026-11-16，對照的官方頁面：

- 子代理：https://code.claude.com/docs/en/sub-agents
- 技能：https://code.claude.com/docs/en/skills
- 權限規則語法：https://code.claude.com/docs/en/permissions
- 設定：https://code.claude.com/docs/en/settings

試跑環境的 Claude Code 版本：2.1.326。

| 項目 | 官方說法（摘要） | 本實作 |
|---|---|---|
| 子代理位置 | 專案 `.claude/agents/`，使用者 `~/.claude/agents/`；必填 `name`、`description` | 照做 |
| `tools` | 逗號分隔字串或 YAML 清單；省略則繼承全部 | 四個都明列 |
| `model` | `sonnet`／`opus`／`haiku`／`fable`、完整模型 ID 或 `inherit`；省略時同啟動它的對話 | 一律 `inherit` |
| 技能位置 | `.claude/skills/<名稱>/SKILL.md`；所有欄位選填 | 照做 |
| `allowed-tools` | **只預先核准，不限制**可用工具 | 不使用（避免誤以為是限制） |
| `disallowed-tools` | 技能啟用期間從可用工具中移除 | 用於共讀技能 |
| `context: fork` + `agent` | 技能在指定類型的子代理中執行，不帶對話歷史 | 用於驗證者與節奏助理的技能 |
| `disable-model-invocation` | `true` 時只能由人以 `/名稱` 啟動 | 用於驗證者、共讀助理、節奏助理的技能 |
| 參數 | `$ARGUMENTS` 代換 | 每個技能使用 |

**UNKNOWN（文件沒寫清楚或本次未取得逐字內容）：**
- 子代理 `tools` 欄位能否寫路徑或指令層級的規則（例如限制只寫某目錄）：未見說明；本實作不依賴它。
- 子代理是否自動載入 `AGENTS.md`：子代理文件的逐字內容只提到 `CLAUDE.md`。
- 子代理可否再派生子代理的確切規則：只取得摘要；本實作的四個 Agent 都沒有派生工具。
- Claude Code 是否自動讀取 `AGENTS.md`：試跑中各 Agent 都有引用虛構專案的 `AGENTS.md`，但無法分辨是自動載入還是自己讀檔，仍列 UNKNOWN。

**試跑中觀察到、文件未明寫的行為（OBSERVED，2.1.326，見 trials/README 第 3 節）：**
- 以 `--agent independent-validator` 開的主對話（沒有派生子代理的工具）輸入 `/verify-wp`，仍會分叉成驗證者子代理。
- 在試跑環境中，有 Bash 的 Agent 工具清單沒有 Grep 與 Glob（一般對話的預設清單也沒有），搜尋改以 Bash 進行；沒有 Bash 的共讀助理則有 Grep 與 Glob。這看起來是環境或版本差異，請在自己的環境確認。

## 7. 與 docs/19、docs/11 §8 的差異

| 項目 | 規格 | 實作 | 原因 |
|---|---|---|---|
| 技能名稱 | docs/11 §8.1 寫 `/wp-verify`、`/digest`、`/takeover-coach` | 依 docs/19 §3：`verify-wp`、`weekly-digest`；`takeover-coach` 未做 | docs/19 為準；takeover-coach 不在 docs/19 §3 |
| 子代理 | docs/11 §8.2 有 orchestrator、researcher、engineer-sw／fw／hw、validator、handover | 四個 Agent；領域差異改為技能 | docs/19 §2 的決定 |
| 驗證者寫入範圍 | 「只有驗證報告」 | 驗證報告與旁邊的重跑輸出目錄 | 重跑輸出需要留存才能被核對；不覆寫作者的證據 |
| 技能呼叫 CLI | docs/11 §8.1 每個技能呼叫 `aitw` | 全部改為手動步驟 | `aitw` 尚未完成 |
| 共讀助理「只產生留言草稿」 | docs/19 §2 | 留言草稿只輸出在對話中，不寫檔 | 共讀助理沒有寫入工具；這讓「不寫入 repo」被工具強制 |

## 8. 已知限制

- 只在虛構小例子上各試跑一次；不同模型與版本的反應會不同。
- 官方格式會變動；升級 Claude Code 後請重新對照第 6 節。
- 執行者涵蓋的事很多；若實際使用時脈絡過長，可能需要把規劃拆出去（docs/19 §8）。
- 技能文字是 prompt，不是保證；不可逆的限制要靠平台權限與執行環境（docs/19 §5）。
