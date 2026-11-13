# 11 — 輔助執行工具規格：Git-native Operating Kit

**文件狀態：** 設計規格 v0.3 · 2026-11-13 · **尚未實作**
**讀者：** 實作者（Opus／工程師）與審查者。流程見 [09](09-execution-playbook.md)，領域規範見 [10](10-domain-profiles-sw-fw-hw.md)，開發工單見 [13](13-opus-handoff.md)。
**規格用語：** 「必須」為驗收必要條件；「建議」可由實作者調整並在 PR 說明理由。外部產品的功能名稱與設定以其官方文件為準，實作前須核對。

## 1. 目標與非目標

**目標：** 讓 09 的流程可被**操作**（一行指令完成一步）與**強制**（違規會被機器擋下），且不需要後端服務。

| 設計目標 | 說明 |
|---|---|
| 確定性骨幹 | CLI 不呼叫 LLM；同樣輸入得到同樣輸出。LLM 只在 Agent 層產生文字，且不是事實來源 |
| 檔案即資料庫 | 所有狀態是 repo 內的 YAML／Markdown，可 diff、可審、可搬到任何 Git 平台 |
| 強制在伺服端 | 真正的關卡是 forge 分支保護 + CI 檢查，不是 Agent 的自律或前端顯示 |
| 可替換 | Forge（GitHub 先）、Agent 執行環境（Claude Code 先）、領域包都以薄介面隔開 |
| 離線可測 | 單元測試不需網路；forge 以假實作替身測試 |

**非目標（MVP 不做）：** 後端服務與資料庫、即時多人編輯、CLI 內建模型推論、設備或儀器控制、G0 自動合併、取代機構的 PLM／ELN／安全 SOP。

## 2. 組成總覽

```text
                 人類（Primary / Backup / Reviewer）
                    │ PR review・留言指令・看板
                    ▼
┌──────────── Forge（GitHub：PR、分支保護、CODEOWNERS、Actions）────────────┐
│   ⑤ Forge 整合包：workflow（verify / gate / board / cadence）、PR 樣板   │
└───────────────▲──────────────────────────────▲───────────────────────────┘
                │ 讀寫分支與 PR                 │ 在 CI 內執行
┌───────────────┴──────────────┐    ┌──────────┴────────────────────────────┐
│ ④ Agent 整合包（Claude Code）│    │ ① aitw CLI（Python，確定性）          │
│   技能・子代理・防護 hook    │───▶│   lint・evidence・verify・packet・gate │
└──────────────────────────────┘    │   board・digest・trace・metrics        │
                                    └──────────┬────────────────────────────┘
                                               │ 讀寫
        ┌──────────────────────────────────────┼─────────────────────────────┐
        ▼                                      ▼                             ▼
 ② 檔案契約（schema + 樣板）          ③ 領域包（sw / fw / hw）        ⑥ 看板（靜態 HTML）
   mission / wp / evidence / packet     policy 預設・檢查表・驗證配方     Mission Control Lite
```

| # | 組件 | 交付形式 | 位置（本 repo） |
|---|---|---|---|
| ① | `aitw` CLI | Python 套件 | `packages/aitw/` |
| ② | 檔案契約 | JSON Schema + 樣板 | `packages/aitw/schemas/`、`kit/templates/` |
| ③ | 領域包 | YAML + Markdown | `kit/packs/{sw,fw,hw}/`、`kit/checklists/` |
| ④ | Agent 整合包 | 技能、子代理、hook 設定 | `kit/agent/claude-code/` |
| ⑤ | Forge 整合包 | workflow、PR 樣板、設定指南 | `kit/forge/github/` |
| ⑥ | 看板 | 靜態 HTML + JSON | 由 `aitw board build` 產生 |
| ⑦ | 範例專案 | 虛構、可在 CI 跑通 | `examples/bms-ntc-demo/` |

## 3. 目錄配置

`aitw init` 在**專案 repo** 建立下列結構（本 repo 的 `examples/bms-ntc-demo/` 為其範例）：

```text
<project-repo>/
├── .aiteam/
│   ├── config.yaml          # 專案、人員與角色、Agent 身份、節奏、WIP 上限
│   ├── policy.yaml          # 路徑→領域／Gate、各 Gate 的核准規則（人類專屬）
│   ├── packs/               # 已啟用領域包的檢查表與驗證配方
│   └── HALT                 # 存在即緊急停止（平時不存在）
├── work/missions/M-001-<slug>/
│   ├── mission.md
│   ├── steering.md
│   └── wp/WP-003-<slug>/
│       ├── wp.md
│       ├── evidence/manifest.yaml  (+ 各證據輸出檔)
│       ├── review/packet-r1.md、verification-r1.md
│       └── decisions/DR-001.md
├── knowledge/
│   ├── memory.md            # 研究記憶：已驗證事實／假設／未知／已否決（皆附來源）
│   ├── adr/                 # 設計決策
│   ├── interfaces/          # ICD（見 10 §6）
│   └── requirements.yaml
├── cadence/{digests,sync}/
├── takeover/TKO-<yyyy-mm>/
├── STATUS.md                # 產生檔：人類可讀的現況總表
└── （專案本身的 sw/ fw/ hw/ docs/ …）
```

命名規則（必須）：Mission `M-NNN`、WP `WP-NNN`（repo 內唯一遞增）、證據 `EV-<WP號>-NN`、決策請求 `DR-NNN`、分支 `wp/WP-NNN-<slug>`、commit 尾註 `WP: WP-NNN` 與 `Agent: <role>`。

## 4. 檔案契約

每種檔案以 YAML front matter 承載機器欄位、Markdown 本文承載給人讀的內容。完整樣板見 [`kit/templates/`](../kit/templates/)；以下列出**必填欄位**與規則。

### 4.1 `wp.md`

| 欄位 | 型別 | 規則 |
|---|---|---|
| `id`、`mission`、`title` | 字串 | id 唯一 |
| `domain` | `sw｜fw｜hw｜sys｜research` | |
| `executor` | `ai｜human｜pair` | `human` 即人類任務（10 §8） |
| `autonomy` | `A0–A3` | 需與 executor、gate 相容（09 §3） |
| `gate` | `G0–G3` | 宣告值；實際值由 Gate Check 取較高者 |
| `review_tier` | `R1–R3` | 不得低於該 Gate 的預設 |
| `scope.paths` | 路徑樣式清單 | 變更超出即 Gate 失敗 |
| `acceptance[]` | `id`、`text`、`verify` | 每條都要有 `verify` |
| `acceptance[].verify` | `kind`、`runner`（`ci｜agent｜human`）、`command`（ci／agent 必填）、`ladder`（V1–V5） | 合併 Plan 後凍結 |
| `satisfies[]`、`depends_on[]` | 編號清單 | 必須存在 |
| `budget` | `max_iterations`、`max_agent_minutes` | 超出轉 BLOCKED |
| `start_approval` | `not_required｜required` | G3 必為 `required` |
| `blocked` | `reason`、`next_action`、`owner` | 存在即 BLOCKED |

本文區段：背景、作法、執行日誌（只增不改）。

### 4.2 `evidence/manifest.yaml`

每筆證據（必須）：`id`、`ac`（對應驗收條件）、`kind`、`produced_by`（`agent:<role>｜ci:<run-id>｜human:<handle>`）、`git_sha`、`worktree_dirty`、`started_at`、`duration_s`、`command` 與 `exit_code`（若為指令）、`outputs[]`（`path` 或 `uri` + `sha256`）、`ladder`、`label`、`verified_by`、`conditions`（量測／HIL 必填，欄位見 10 §4、§5）。

`kind` 列舉：`test_run｜build｜static_analysis｜size_report｜sim｜calc｜erc_drc｜bom_check｜datasheet｜measurement｜hil_run｜checklist｜benchmark｜doc`。

**標籤規則（由 lint 強制）：**

| 規則 | 內容 |
|---|---|
| L1 | `produced_by: agent:*` 的證據，`label` 最高為 OBSERVED |
| L2 | `label: VERIFIED` 必須有 `verified_by: ci:<run-id>` 或 `human:<handle>`，且該人類不是 Agent 身份 |
| L3 | `kind: sim` 最高為 OBSERVED |
| L4 | `kind: measurement｜hil_run` 必須 `produced_by: human:*`（MVP）且 `conditions` 完整 |
| L5 | `kind: datasheet` 必須有文件名、版次、頁碼 |
| L6 | `worktree_dirty: true` 的證據不可支持 VERIFIED |

### 4.3 `review/packet-rN.md`

Front matter（機器欄位）：`wp`、`revision`、`head_sha`、`effective_gate`、`review_tier`、`claims[]`（`id`、`text`、`label`、`evidence[]`、`ladder`、`scope_limits`）、`must_read[]`（`path`、`lines`、`reason`、`est_minutes`）、`questions[]`（連到 DR）、`challenge_question`、`unverified[]`、`rollback`。

本文依 09 §6.1 的八段呈現。**主張規則（lint）：** VERIFIED 需引用符合 L2 的證據；HYPOTHESIS 需有驗證計畫；UNKNOWN 需說明缺口；本文敘述中引用的證據編號必須存在。

### 4.4 `decisions/DR-NNN.md`

必填：`id`、`wp`、`kind`（`choice｜start_approval｜scope_change｜acceptance_change`）、`question`、`options[]`（`id`、`summary`、`impact`、`reversible`）、`recommendation`、`needed_by`、`blocks[]`、`request_sha`；決議欄位 `resolution`：`outcome`、`option`、`decided_by`、`decided_at`、`ref`（forge 上人類留言或 review 的網址）、`dissent[]`。

**規則：** `resolution` 的效力來自 `ref` 指向的人類已驗證行為；Gate Check 會回查該留言確實存在、作者為具權限的人類、內容與紀錄一致。檔案內容本身不構成核准。

### 4.5 其他

`mission.md`（目標、成功定義、不做什麼、風險邊界、預算、核准者）、`human-task-record.md`（10 §8）、`config.yaml`、`policy.yaml`、週摘要、會議議程、接手包：見樣板。

## 5. Policy 與 Gate Check

### 5.1 Policy 是人類專屬

`.aiteam/**`、CODEOWNERS、CI workflow 屬於 `human_only` 路徑：Agent 身份的 commit 觸及這些路徑時 Gate 必須失敗。修改需由人類提交並經管理者核准。

### 5.2 核准規則（policy 預設，可調嚴）

| Gate | 最少人類核准 | 角色要求 | 其他 |
|---|---|---|---|
| G0 | 1 | primary／backup／reviewer 任一 | 可當日批次送審（R1） |
| G1 | 1 | primary 或 reviewer | |
| G2 | 1 | 必含 primary；policy 指定的加簽角色 | Backup 共讀紀錄（預設不擋合併，逾期升級） |
| G3 | 2 | 必含 primary + 一位合格 reviewer | 檢查表全項填寫；啟動核准紀錄；R3 會議紀錄 |

Solo 模式無法滿足 G3 的兩人要求——這是刻意的：不可逆動作需要第二位合格人類。

### 5.3 Gate Check 演算法（`aitw gate check`）

輸入：PR 編號（或本地 WP）。**工具本體、policy、config、WP 的驗收定義一律取自基底分支（base）**；PR 分支的內容只當資料讀。

1. **停止檢查：** base 有 `.aiteam/HALT` → 失敗（exit 4）。
2. **辨識類型：** 由分支名與標籤判定 PR 種類：`plan｜wp｜decision｜cadence｜takeover｜human`（人類直接提交）。以下為 `wp` 類的步驟。
3. **範圍：** 變更檔案都落在 WP 的 `scope.paths` 或該 WP 自己的工作目錄內；否則失敗。
4. **人類專屬路徑：** 見 5.1。
5. **實際 Gate：** `max(wp.gate, 各變更路徑的 min_gate)`；收集加簽角色與跨領域 owner。
6. **驗收定義凍結：** 比對 PR 內 `wp.md` 的 `acceptance` 與 base；有差異則需要一筆已決議的 `acceptance_change` DR，且實際 Gate 至少 G2。
7. **證據完整：** 每條驗收條件至少一筆符合其 `verify.runner` 的證據；輸出檔雜湊相符。
8. **證據新鮮：** `runner: ci` 的條件必須有**針對目前 head commit** 的 CI 驗證結果；agent／human 證據的 `git_sha` 之後，`scope.paths` 內不得再有變更，否則視為過期。
9. **標籤與主張：** 執行 4.2、4.3 的 lint 規則。
10. **決策：** 該 WP 所有 `blocks` 到合併的 DR 都已決議，且 `ref` 回查通過。
11. **啟動核准：** `start_approval: required` 者必須有已合併的核准紀錄，且時間早於第一筆執行證據。
12. **人類核准：** 透過 forge 讀取針對 head commit 的 review；排除 Agent 身份與 PR 作者；依 5.2 檢查人數與角色。
13. **檢查表：** G3 或 `safety_critical` 路徑需要對應檢查表且每項有結果與依據。
14. **輸出：** 人類可讀報告（逐項通過／失敗與原因、下一步該誰做什麼）+ JSON。全部通過 exit 0，否則 exit 1。

## 6. `aitw` CLI 指令參考

通用：`aitw [--repo PATH] [--json] <群組> <指令>`。
結束碼：`0` 成功 · `1` 檢查未通過 · `2` 用法或檔案格式錯誤 · `3` 外部相依不可用（CI 中視為失敗）· `4` HALT 生效。
錯誤訊息必須指出**檔案、欄位、原因與修正方式**。

| 指令 | 用途 | 主要行為 |
|---|---|---|
| `init [--packs sw,fw,hw] [--forge github\|none]` | 安裝 Kit 到專案 | 建目錄、複製樣板與領域包、產生 CODEOWNERS 與 workflow 草稿（不覆寫既有檔） |
| `doctor` | 健檢 | 檢查 schema、人員與 Agent 身份、分支保護設定、HALT；列出缺口 |
| `mission new\|list\|show` | 管理 Mission | 由樣板建立並配號 |
| `wp new --mission M --domain D --title T [--executor human]` | 建立 WP | 配號、套用領域包預設的 Gate 與驗證配方 |
| `wp start WP` | 開工 | 檢查狀態、啟動核准、相依、HALT、預算；建分支；寫執行日誌 |
| `wp block\|unblock WP` | 標記阻擋 | 必填原因、下一步、負責人 |
| `wp submit WP` | 送審 | 跑 lint 與證據檢查；檢查審查者 WIP 上限（觸頂則拒絕並說明）；產生共讀包骨架；PR 轉 ready |
| `wp status [WP]` | 現況 | 依 §7.2 推導實際狀態；列出「下一步該誰做」 |
| `evidence run WP --ac AC --kind K -- <指令…>` | 執行並留證 | 見 §7.1 |
| `evidence add WP --ac AC --kind K --file F --by human:<handle>` | 登錄人類或外部證據 | 計算雜湊；要求 `conditions` |
| `evidence check WP` | 檢查證據 | 雜湊、過期、標籤規則 |
| `verify WP` | CI 重跑驗收 | 取 **base** 的 `verify.command`，在乾淨工作區針對 head 執行，產生 `ci:` 證據與摘要 |
| `lint` | 全庫檢查 | schema、交叉引用、標籤與主張規則、樣板空格未填 |
| `packet build WP` | 產生共讀包 | 確定性地填入主張表、證據表、必看清單、驗證階；留下敘述空格給 Agent 填，lint 會檢查是否填完 |
| `gate check [--pr N\|--wp WP]` | 關卡 | §5.3 |
| `decision request\|list\|resolve` | 決策請求 | `resolve` 只登錄 `ref`，並回查該人類行為 |
| `board build [--out DIR]` | 看板 | 產生 `data.json`、單檔 HTML、`STATUS.md` |
| `brief [--for ROLE]` | 每日簡報 | 等你決定／等你動手／昨日完成／接下來 |
| `digest build --week W` | 週摘要骨架 | 依 Gate、介面變更、風險排序選 3–5 項；無重大變更則如實輸出「無」 |
| `sync agenda [--date D]` | 會議議程 | 依 09 §8 的五段產生 |
| `trace` | 追溯矩陣 | 需求 ↔ WP ↔ 證據 ↔ 驗證階 |
| `metrics [--since D]` | 指標 | 09 §13 的各項，附計算來源 |
| `takeover pack\|start\|submit\|grade` | 接手演練 | 產生接手包、計時、收證據、登錄 Reviewer 評級 |
| `halt --reason R` | 緊急停止 | 建立 HALT 檔；解除只能經人類核准的 PR |

## 7. 證據執行器與狀態推導

### 7.1 `evidence run` 的語意

1. 記錄開始時間、目前 commit、工作區是否乾淨、工具版本指紋（由領域包指定要記哪些）。
2. 以限時與資源上限執行指令；完整保存 stdout／stderr 到輸出檔。
3. 記錄結束碼與耗時；計算輸出檔 sha256。
4. 於 manifest 追加一筆（**只增不改**；重跑產生新編號，舊的保留）。
5. `produced_by` 取自執行環境（Agent 角色或 CI run），不接受指令列任意指定為 `human` 或 `ci`。
6. 指令失敗時仍留證（失敗也是證據），結束碼回傳 1。

### 7.2 狀態推導（`wp status`）

依 09 §5 的對照表，由「base 上的 WP 檔 + 分支與 PR 的 forge 狀態」計算。Forge 透過介面存取：

```text
ForgeAdapter（介面）
  get_pr(wp_or_number) -> {number, draft, head_sha, base_ref, author, labels, merged}
  list_reviews(pr)     -> [{user, state, commit_sha, submitted_at}]
  list_comments(pr)    -> [{user, body, url, created_at}]
  get_check_runs(sha)  -> [{name, conclusion, run_id}]
  identity_kind(user)  -> human | bot
  branch_protection(ref) -> {...}
實作：GitHubForge（REST）、LocalForge（僅 git，無核准資訊）、FakeForge（測試用，讀固定資料）
```

## 8. Agent 整合包（Claude Code 先行）

Agent 的行為契約沿用 [`prompts/agent-contracts.md`](../prompts/agent-contracts.md)；本包把契約落成可用的技能、子代理與防護設定。**技能、子代理、hook 的檔案格式與事件名稱以 Claude Code 官方文件為準，實作前必須查證。** 其他 Agent 執行環境（Codex、本地模型的 CLI Agent）以相同的 CLI 與 `AGENTS.md` 契約接入。

### 8.1 技能（人類的操作入口）

| 技能 | 誰用 | 做什麼 | 呼叫的 CLI |
|---|---|---|---|
| `/mission-intake` | Primary | 訪談式提問 → 起草 `mission.md` → 開 PR | `mission new`、`lint` |
| `/wp-plan M-001` | Primary 觸發 | 拆 WP、寫驗收與驗證、估 Gate → 開 Plan PR | `wp new`、`lint` |
| `/wp-run WP-003` | Primary 觸發或排程 | 依領域切換工程子代理，執行並留證 | `wp start`、`evidence run` |
| `/wp-verify WP-003` | 自動 | 啟動 Validator 子代理，寫驗證報告 | `evidence check` |
| `/review-packet WP-003` | 自動 | 填共讀包的敘述段落 | `packet build`、`wp submit` |
| `/coread WP-003` | Primary／Backup | 帶讀：依必看清單逐項說明、回答問題並附來源、出挑戰題；把未解問題整理成留言草稿，**由人送出** | 唯讀 |
| `/decide` | 人類 | 列出待決 DR 與各選項影響；人類在 forge 留言決定 | `decision list` |
| `/human-task WP-005` | 執行者 | 顯示程序書；引導填紀錄表；登錄原始資料雜湊 | `evidence add` |
| `/sync-agenda`、`/digest` | 排程 | 產生議程與週摘要的敘述 | `sync agenda`、`digest build` |
| `/takeover-pack`、`/takeover-coach` | Reviewer／Backup | 產生接手包；演練時當導師（不洩漏答案、每步附來源） | `takeover *` |

### 8.2 子代理

| 子代理 | 可寫範圍 | 可用工具 | 限制 |
|---|---|---|---|
| orchestrator | `work/**` 的計畫與 DR | 讀全庫、CLI | 不改產品程式 |
| researcher | WP 工作目錄、`knowledge/`（經 PR） | 讀、允許清單內的資料來源 | 無來源不下結論 |
| engineer-sw／fw／hw | WP 的 `scope.paths` | 讀寫、沙盒內建置與測試 | 受 §8.3 拒絕清單限制 |
| validator | 僅 `review/verification-rN.md` | 讀、重跑測試 | **不可修改產品程式與測試**；建議使用與 Engineer 不同的模型或至少全新上下文 |
| handover | `takeover/`、`knowledge/memory.md`（經 PR） | 讀、CLI | 缺口標 UNKNOWN |

同一模型的兩個人格不是獨立驗證（01 §3）；獨立性主要來自 **CI 重跑**與**人類審查**，Validator 是輔助。

### 8.3 防護 hook 與拒絕清單

工具呼叫前攔截（必須涵蓋，樣式由領域包提供並可擴充）：

| 類別 | 攔截對象 |
|---|---|
| 實體目標 | 燒錄與除錯連線工具、串列埠與儀器匯流排存取、任何設備控制指令 |
| 核准與合併 | 以 CLI 或 API 核准、合併 PR；修改分支保護；強制推送；直接推主幹 |
| 人類專屬路徑 | 寫入 `.aiteam/**`、CODEOWNERS、CI workflow |
| 範圍 | 寫入目前 WP `scope.paths` 以外的產品檔案（警告並要求改開新 WP） |
| 停止 | 存在 `.aiteam/HALT` 時拒絕開新工作 |

**Hook 是輔助防線，不是安全邊界。** 真正的保證來自：Agent 的執行環境根本沒有燒錄器與儀器的存取權、Agent 身份沒有合併與核准權限、CI Gate 取自基底分支。

## 9. Forge 整合包（GitHub 先行）

### 9.1 必要設定（`aitw doctor` 檢查；名稱以 GitHub 官方文件為準）

- 主幹必須經 PR；必須通過 `aitw-verify` 與 `aitw-gate` 兩項檢查。
- 至少一位核准；**新 commit 使舊核准失效**；要求 CODEOWNERS 審查；禁止強制推送；管理者不得繞過。
- **Agent 使用獨立的機器身份**（機器帳號或 App）發 PR。原因：PR 作者不能核准自己的 PR；若 Agent 用 Primary 的帳號發 PR，Primary 就無法審查。
- 禁止自動化身份核准 PR。

### 9.2 Workflow

| Workflow | 觸發 | 內容 | 權限 |
|---|---|---|---|
| `aitw-verify` | PR 更新 | 於容器內執行 `aitw verify`；上傳完整 log | 唯讀；**不提供任何 secret** |
| `aitw-gate` | PR 更新、review 提交、留言 | 以**基底分支／已釋出版本**的工具執行 `gate check`；輸出報告 | 讀 PR 與 review |
| `aitw-board` | 主幹更新 | `board build`；更新 `STATUS.md` | 寫入產生檔 |
| `aitw-cadence` | 排程（每日、每週） | 產生簡報、週摘要骨架、議程 PR | 開 PR |

### 9.3 人類留言指令（Gate 以 API 回查，MVP 不需寫入型機器人）

`/read` · `/understood <答案>` · `/decide DR-NNN <選項> [理由]` · `/steer <內容>` · `/time <分鐘>`。只有 config 內登錄的人類身份有效。

### 9.4 PR 樣板

PR 說明採共讀包的精簡版（見 [`.github/pull_request_template.md`](../.github/pull_request_template.md)）；完整共讀包以檔案形式存在 repo，因為 PR 說明可被事後修改、不具版本。

## 10. 看板：Mission Control Lite

`aitw board build` 產生**單檔離線 HTML** + `data.json`，視覺沿用 [`demo/mission-control.html`](../demo/mission-control.html)，但資料來自真實檔案。

| 分頁 | 內容 | 資料來源 |
|---|---|---|
| 今日 | 09 §7.1 的四欄：等我決定／等我動手／AI 進行中／卡住 | WP 狀態、DR、人類任務 |
| Mission | 每個 Mission 的 WP 清單、狀態、Gate、驗證階；進度 = 已接受 WP 數／總數 | `work/**` |
| 共讀 | 待審共讀包、必看清單時間合計、Backup 共讀狀態 | `review/**`、forge |
| 追溯 | 需求 ↔ WP ↔ 證據 ↔ 驗證階矩陣 | `trace` |
| 備援 | 週摘要、已讀／已理解、L 級與最近演練日 | `cadence/**`、`takeover/**` |
| 指標 | 09 §13 | `metrics` |

規則（必須）：每個數字可點回來源檔案或 PR；頁首顯示產生時的 commit 與時間；純唯讀——所有動作連回 forge 進行；輸出時對所有文字做跳脫。**真實專案的看板不可發佈到公開網站**。

日後的後端平台（04）讀同一份 `data.json` schema，不另立資料模型。

## 11. 工具自身的安全設計

| 威脅 | 對策 |
|---|---|
| AI 在 PR 內修改工具、policy 或驗收條件讓自己過關 | Gate 與 verify 的工具、policy、驗收定義取自基底分支；驗收變更需人類決議 |
| AI 偽造測試輸出 | VERIFIED 只認 CI 重跑或人類簽認（規則 L1、L2） |
| AI 弱化測試 | 測試刪改一律列入必看清單（09 §6.2） |
| PR 內容夾帶惡意指令（提示注入） | 工具把 PR、Issue、文件內容當資料，不執行；Agent 依契約視為不可信輸入 |
| CI 執行 AI 寫的程式 | PR 的 CI 不給 secret、唯讀權杖、容器隔離、限時限資源、盡可能斷網 |
| 冒用人類核准 | 核准來自 forge 的已驗證身份；Agent 身份與 PR 作者的核准不計；檔案內的決議需回查 `ref` |
| 舊核准套用到新內容 | 新 commit 使核准失效；Gate 只認針對 head commit 的 review |
| 看板注入 | 所有輸出文字跳脫；不載入外部資源 |
| 管理者繞過保護 | 關閉繞過；`doctor` 定期檢查並列入指標 |

本設計**不能**防範有管理權限者的惡意行為，也不取代機構的資安與安全審核（05）。

## 12. 與既有 Backlog（07 的 T 系列）的關係

| T 系列 | 在 Kit 中的對應 | 說明 |
|---|---|---|
| T04 狀態機與核准關卡 | K1、K2 | 以檔案 + forge 實現，不需資料庫 |
| T05 Co-Review UI | K3（共讀包 + PR + 看板） | PR 即共讀面 |
| T06 Backup 週摘要 | K6 | |
| T07、T08 接手包與演練 | K7 | |
| T09 Portfolio／KPI | K3、K6 | 單專案先行；跨專案彙整為後續 |
| T10 多 Agent 編排 | K4 | 以技能與子代理實現 |
| T01 事件擷取、T02 RAG、T03 本地推論介面、T11 觀測、T12 設備連接 | **延後** | Git 本身已是事件庫；規模或機密需求出現時再建，並沿用 Kit 的檔案契約 |

## 13. 驗收總則

1. 每個指令有單元測試；Gate Check 的每一步至少一個通過案例與一個失敗案例。
2. 範例專案的「黃金路徑」端對端測試可在 CI 離線跑通（forge 用假實作）。
3. 所有失敗訊息指出該由誰做什麼。
4. 文件（本文與 12 的操作範例）與實作不一致時，以 PR 同步修正其中之一，並說明原因。
