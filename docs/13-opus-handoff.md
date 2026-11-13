# 13 — 開發交付包：Operating Kit 實作工單（給 Opus）

**文件狀態：** 交付規格 v0.3 · 2026-11-13
**分工：** 規劃與範例設計已完成（09–12）；本文把它拆成可逐一交付、逐一審查的工單。
**給人類（Primary）：** 核准包含本文的 PR = 核准這份計畫與各工單的驗收條件（對應 09 的步驟 3）。第 6 節是需要你確認的事項。

## 1. 實作者須知

### 1.1 閱讀順序

1. [`AGENTS.md`](../AGENTS.md)（共同規範，全部適用）
2. [09 執行流程](09-execution-playbook.md) → [10 領域規範](10-domain-profiles-sw-fw-hw.md) → [11 工具規格](11-toolkit-spec.md)（**主要規格**）→ [12 操作範例](12-operating-examples.md)（**端對端驗收情境**）
3. [14 GitLab 執行方式](14-gitlab-profile.md)（單位實際使用的平台；K2b 的規格）
4. [`kit/templates/`](../kit/templates/)、[`kit/checklists/`](../kit/checklists/)（檔案契約的起點）
5. 01–08 為背景；與 09–14 衝突時以 09–14 為準，並在 PR 指出衝突處。

### 1.2 不可違反的不變量

實作的任何便利性都不得破壞以下任一條；每條都必須有自動化測試：

| # | 不變量 |
|---|---|
| I1 | CLI 不呼叫任何模型；相同輸入產生相同輸出 |
| I2 | Agent 產生的證據標籤最高為 OBSERVED；VERIFIED 只能來自 CI 重跑或人類簽認 |
| I3 | Gate Check 使用的工具、policy、config、驗收定義取自基底分支 |
| I4 | Agent 身份與 PR 作者的核准不計入；核准只認針對 head commit 的人類 review |
| I5 | 驗收定義變更、範圍外變更、人類專屬路徑變更，沒有人類授權就失敗 |
| I6 | 證據只增不改；失敗的執行也留存 |
| I7 | 工具不含、也不產生任何燒錄、儀器或設備控制指令 |
| I8 | 所有範例與測試資料皆為虛構並如此標示；不含 secret、真實量測或內部資訊 |
| I9 | 看板與報告的每個數字可由檔案重算；不接受模型填寫的數值 |
| I10 | HALT 存在時，開工類指令與 Gate 一律失敗 |

### 1.3 技術約束

- Python 3.11 以上；套件放 `packages/aitw/`（`src` 佈局、`pyproject.toml`）；測試用 pytest。
- 相依最小化：YAML 解析、JSON Schema 驗證、指令列框架各一個成熟函式庫即可；新增其他相依需在 PR 說明必要性（AGENTS.md 規則 9）。
- 單元測試不得連網；forge 互動一律經 `ForgeAdapter`，測試使用 `FakeForge`。
- 使用者可見訊息與文件用繁體中文；程式、欄位名、指令用英文。
- Claude Code、GitHub 與 GitLab 的功能、檔案格式、設定名稱**先查官方文件再實作**；與本規格描述不符時以官方為準並回報。
- 範例專案只用主機端工具鏈可建置的內容（例：以主機編譯器建置的 C 測試、Python 腳本）；不要求模擬器或 EDA 軟體即可跑通 CI。需要外部工具的驗證配方標為「選用」。

### 1.4 工作方式（本專案即第一個試點）

工具開發本身依 09 §12 的**手動模式**進行：

- 一張工單一個（或數個更小的）PR；分支 `wp/WP-NNN-<slug>`。
- 每個 PR 依 [PR 樣板](../.github/pull_request_template.md) 附共讀包：主張表、必看清單、未驗證範圍、實際執行的指令與輸出。
- **從未執行的測試不得宣稱通過**；無法執行的項目標 NOT RUN 與原因。
- 規格不清或有誤時：不要默默偏離。在 PR 以「決策請求」列出選項與建議，可先做不相依的部分。
- 不擴大範圍：發現規格外的好點子，記入 PR 的「後續建議」，不要順手實作。

## 2. Mission 與里程碑

Mission 檔：[`work/missions/M-001-build-operating-kit/mission.md`](../work/missions/M-001-build-operating-kit/mission.md)

| 里程碑 | 包含工單 | 人類可以做到什麼 |
|---|---|---|
| **M1 可操作** | K0、K1、K2a、K2b、K3 | 用指令建立 WP、留證、產生共讀包、過 Gate、看看板（Agent 部分仍用一般提示） |
| **M2 可交給 AI** | K4–K5 | 用技能驅動 Agent；韌體／硬體領域包與人類任務可用 |
| **M3 可持續** | K6–K8 | 週摘要、會議議程、指標、接手演練、完整教學 |

相依：`K0 → K1 → K2a → K3`；**K2b（GitLab）在 K2a 之後，可與 K3 平行，須在首個 GitLab 試點前完成**；K4 與 K5 在 K3 之後可平行；K6、K7 在 K3 之後；K8 最後。

## 3. 工單

每張工單：目標、範圍、驗收（全部需自動化測試，除非註明）、人類必看、規模（S／M／L 為相對值）。

### K0 — 契約與骨架　·　G1　·　規模 M

**目標：** 先把檔案契約定成可驗證的 schema，並建立範例專案骨架，後續工單都以此為測試資料。

**範圍：**
- 把本文 K0–K8 轉成 `work/missions/M-001-build-operating-kit/wp/` 下的 `wp.md`（Plan PR，供人類核准）。
- `packages/aitw/` 骨架、CI（lint + pytest）。
- 11 §4 各檔案的 JSON Schema；`kit/templates/` 全部樣板通過 schema。
- `aitw lint`（僅 schema 與交叉引用）。
- `examples/bms-ntc-demo/`：依 12 的情境建立虛構專案（`sw/`、`fw/`、`hw/calc/`、`knowledge/interfaces/`、`.aiteam/`、一個 Mission 與六個 WP 檔）。

**驗收：**
- `aitw lint` 對範例專案通過。
- 至少 8 個刻意寫壞的 fixture（缺必填欄位、編號重複、引用不存在的 WP、未知列舉值、驗收條件缺 `verify`、相依成環等）各自失敗，訊息含檔案、欄位、原因、修正方式。
- 範例專案的 `make -C fw test`、軟體測試、硬體計算腳本可在 CI 執行。

**人類必看：** schema 的必填欄位清單是否符合 11 §4；範例專案確認為虛構。

### K1 — 工作包生命週期與證據　·　G1　·　規模 M

**範圍：** `init`、`mission new|list|show`、`wp new|start|block|unblock|status`（LocalForge）、`evidence run|add|check`、標籤規則 L1–L6、`halt`。

**驗收：**
- `evidence run` 記錄 11 §7.1 的全部欄位；指令失敗仍留證且結束碼為 1；重跑產生新編號、舊紀錄不變（I6）。
- 無法以參數把 `produced_by` 指定為 `ci` 或 `human`（I2）。
- L1–L6 每條規則各有通過與失敗案例。
- 證據之後修改 `scope.paths` 內檔案 → `evidence check` 報告過期。
- `wp start` 在下列情況拒絕並說明：相依未接受、需啟動核准而未核准、HALT 存在（I10）、預算用盡。
- `init` 不覆寫既有檔案；重複執行結果相同。

**人類必看：** 證據執行器的實作（指令執行、限時、輸出保存）；標籤規則測試。

### K2a — Gate 核心、CI 驗證與 GitHub 整合　·　G2　·　規模 L

**範圍：** `verify`、`gate check`（11 §5.3 全部 14 步）、`decision request|list|resolve`、`doctor`、`ForgeAdapter` 與 `GitHubForge`／`FakeForge`、`kit/forge/github/`（workflow、CODEOWNERS 產生、設定指南）。

**驗收：**
- 14 步每一步至少一個通過與一個失敗案例（FakeForge）。
- 安全案例必須失敗：PR 內修改 policy／工具／workflow；PR 內放寬驗證指令而無授權 DR；核准者是 Agent 身份；核准者是 PR 作者；核准針對舊 commit；DR 的 `ref` 指向不存在或非授權人類的留言；變更超出 scope。
- `verify` 執行的是基底分支上的指令（以「PR 把指令改成恆真」的 fixture 證明）。
- Gate 報告每個失敗項都有「下一步該誰做什麼」。
- Workflow：PR 觸發的工作不使用 secret、權杖唯讀；Gate 工作使用基底／已釋出版本的工具（以設定檢查測試或文件化的人工驗證步驟證明，後者標示 NOT AUTOMATED）。
- `GitHubForge` 以錄製的回應做契約測試；真實 API 的手動驗證步驟寫入文件。

**人類必看：** Gate 演算法實作全文；workflow 的觸發條件與權限；安全案例測試清單。

### K2b — GitLab adapter 與整合包　·　G2　·　規模 M

**目標：** 讓 Kit 在單位實際使用的 GitLab 上運作（規格見 [14](14-gitlab-profile.md)）。

**範圍：** `GitLabForge`；`kit/forge/gitlab/`（CI 範本含 `aitw-verify`、`aitw-gate` job、MR 樣板、設定指南）；`doctor` 的 GitLab 檢查項；可設定的留言指令前綴；Free 與 Premium 兩種強制方式的設定指南。

**驗收：**
- K2a 的全部 Gate 案例（含安全案例）以 GitLab 形式的固定資料再跑一次並通過——同一組案例、兩個 adapter。
- Free 版情境：平台核准為選用時，未達核准條件 Gate 仍失敗；bot 與 MR 作者的核准不計；早於最新版本的核准不計。
- 以 `aitw:` 前綴的留言指令可被辨識；GitLab 原生 quick action 不被誤判為 Kit 指令。
- `doctor` 能指出：主幹未保護、未開啟「Pipelines must succeed」、CI 設定檔仍在專案內（AI 可改）、bot 角色過高。
- 14 §5 的六個要點各有測試或文件化的人工驗證步驟（後者標示 NOT AUTOMATED）；14 列為 UNKNOWN 的項目需以實際 GitLab 驗證並回寫文件。
- 「核准後重新評估 Gate」的作法經實測選定，並在 PR 以決策請求說明取捨。

**人類必看：** CI 範本的 job 定義與變數使用；設定指南（需對照單位的 GitLab 版本與等級）。

### K3 — 共讀包、狀態與看板　·　G1　·　規模 M

**範圍：** `packet build`（確定性骨架 + 必看清單規則）、`wp submit`（含 WIP 上限）、`wp status`（forge 推導）、`board build`、`brief`、`STATUS.md`。

**驗收：**
- 必看清單規則（09 §6.2）逐條有 fixture：安全關鍵路徑、介面契約、測試刪除／跳過、驗收變更、Validator 異議、HYPOTHESIS 主張。Agent 提供的額外項目可增加、不可使規則項目消失。
- 共讀包敘述空格未填 → lint 失敗；敘述引用不存在的證據編號 → lint 失敗。
- 狀態推導涵蓋 09 §5 每一列。
- 待審數達上限時 `wp submit` 拒絕並指出是誰、幾件。
- 看板：數字與由檔案重算的結果一致（I9）；輸入含 HTML／腳本字元時輸出已跳脫；離線可開；每個數字有來源連結；顯示產生時的 commit。

**人類必看：** 必看清單的規則實作；看板實際畫面（附截圖）。

### K4 — Agent 整合包（Claude Code）　·　G2　·　規模 M

**範圍：** `kit/agent/claude-code/`：11 §8.1 的技能、§8.2 的子代理、§8.3 的防護 hook；安裝說明；`AGENTS.md` 的對應更新。

**驗收：**
- 拒絕清單以樣本工具呼叫做單元測試：每一類至少三個應攔截與兩個不應誤攔的案例。
- Validator 子代理的設定不允許寫入產品程式與測試。
- 每個技能有一份在範例專案上的操作紀錄（實際執行的對話與產出，放 `examples/` 並標示為示範）。
- 文件明寫：hook 是輔助防線，安全邊界在 forge 與執行環境權限。

**人類必看：** 拒絕清單樣式；各技能的提示內容（是否有替人決定、替人核准的傾向）。

### K5 — 韌體／硬體領域包與人類任務　·　G2　·　規模 M

**範圍：** `kit/packs/{sw,fw,hw}/`（policy 預設、驗證配方、證據欄位要求、必看規則樣式）、補齊 `kit/checklists/`（軟體安全、電路圖審查、佈局審查、上電程序）、人類任務流程（`evidence add` 的 `conditions` 驗證、偏離自動列入必看）、介面契約一致性檢查、`trace`。

**驗收：**
- 範例專案中：修改 `knowledge/interfaces/analog.yaml` 而未同步韌體常數 → 一致性檢查失敗。
- `measurement`／`hil_run` 證據缺少待測物、儀器校正編號、執行者或原始資料雜湊 → 失敗。
- 人類任務在啟動核准前登錄執行證據 → Gate 失敗（11 §5.3 步驟 11）。
- `trace` 輸出每個需求的最高驗證階；只到模擬的需求被標示。
- 檢查表項目缺結果或依據 → Gate 失敗。

**人類必看：** 各檢查表內容（需領域專家確認，這是規劃者無法代為保證的部分）；policy 預設值。

### K6 — 節奏與指標　·　G1　·　規模 S

**範圍：** `digest build`、`sync agenda`、`metrics`、`aitw-cadence` workflow。

**驗收：** 無重大變更時週摘要輸出「無」而非湊數；摘要每條附來源；09 §13 的每個指標有計算測試；議程五段齊全。

### K7 — 接手演練　·　G1　·　規模 S

**範圍：** `takeover pack|start|submit|grade`。

**驗收：** 接手包含 02 §6 的七項，缺少者標 UNKNOWN；計時與求助紀錄可查；評級只能由 config 中的 reviewer 登錄、不可為受測者本人；L2／L3 必須引用演練證據。

### K8 — 黃金路徑端對端與教學　·　G1　·　規模 M

**範圍：** 把 12 的全流程寫成可重跑的端對端測試（FakeForge）；`docs/15-quickstart.md`（從 `aitw init` 到第一個 WP 合併，含 GitHub 與 GitLab 兩版步驟）；核對 09–14 與實作的差異並同步。

**驗收：** 端對端測試在 CI 離線通過，涵蓋 12 的 §5–§8 與 §12 的每個例外情境；一位未參與開發的人依 quickstart 可在範例專案完成一輪（人工驗證，結果寫入 PR）。

## 4. 每張工單的完成定義

- [ ] 驗收條件逐條對應到測試或標示的人工驗證
- [ ] PR 附實際執行的指令與輸出；未執行者標 NOT RUN
- [ ] 不變量 I1–I10 無一被破壞
- [ ] 相關文件已同步（11、12 與實作一致）
- [ ] 範例與測試資料皆為虛構
- [ ] 共讀包列出未驗證範圍與後續建議
- [ ] 經人類核准後合併

## 5. 給 Opus 的啟動指令

```text
你要在 AITeamWorkingModel repo 實作「Git-native Operating Kit」。

先讀：AGENTS.md → docs/09 → docs/10 → docs/11（主要規格）→ docs/12（端對端情境）
→ docs/13（工單與不變量）→ docs/14（GitLab）→ kit/templates/、kit/checklists/。

規則：
1. 依 docs/13 的工單順序進行，從 K0 開始；一張工單一個（或更小的）PR，
   分支命名 wp/WP-NNN-<slug>。
2. K0 的第一步：把 K0–K8 轉成 work/missions/M-001-build-operating-kit/wp/ 下的
   wp.md，開 Plan PR 等人類核准，核准後才開始寫程式。
3. 每個 PR 依 .github/pull_request_template.md 附共讀包：主張表（含標籤）、
   必看清單、未驗證範圍、實際執行的指令與輸出。沒執行過的測試不得說通過。
4. docs/13 §1.2 的不變量 I1–I10 每條都要有測試，不可為了方便而放寬。
5. 規格不清、有誤、或與官方文件（Claude Code、GitHub、GitLab）不符時：不要默默偏離；
   在 PR 以決策請求列出選項與建議，先做不相依的部分。
6. 不擴大範圍；額外想法寫入「後續建議」。
7. 所有範例資料必須虛構並標示；不可加入 secret 或真實研發資料。
8. 不可核准或合併自己的 PR。

現在請先回報：你對 K0 的實作計畫、打算使用的相依套件與理由、
以及你在規格中發現的任何矛盾或疑問。
```

## 6. 需要人類確認的事項（已先採預設值，不擋 K0–K1）

| # | 問題 | 目前預設 | 影響 | 最晚需決定 |
|---|---|---|---|---|
| D1 | Forge 平台 | **已確認：單位使用 GitLab**；本 repo 留在 GitHub。兩個 adapter 都做（K2a、K2b） | 尚需確認 GitLab 為自架或雲端、版本與授權等級（Free 不能由平台強制核准，見 14 §4） | K2b 前 |
| D2 | Agent 用什麼身份發 PR／MR？ | 獨立機器身份（GitLab：project access token 的 bot 或 service account） | 若 Agent 以人的帳號提交，該人的核准不應計入，Gate 的人類核准將無法成立 | K2a 前 |
| D3 | 目前的人力配置 | 單位案例已有多人在 GitLab 上 review → 以 Pair／Team 為主要情境；Solo 仍可運作 | WIP 上限、G3 的兩人要求、共讀流程 | K3 前 |
| D4 | 硬體設計使用哪種 EDA？檔案是否為文字格式、可否匯出網表／BOM？ | 未知；領域包先以「匯出檔進版控」設計 | 硬體領域包的驗證配方與圖像差異 | K5 前 |
| D5 | 韌體的目標平台與工具鏈？是否已有主機端測試或模擬器？ | 未知；工具鏈中立，範例只用主機端 | 韌體領域包的驗證配方 | K5 前 |
| D6 | 真實專案放在哪？（本 repo 為公開） | Kit 在本 repo 開發；真實專案用私有 repo 並以 `aitw init` 安裝 | 資料分級、看板發佈方式 | 首個真實試點前 |
| D7 | 第一個真實試點要選哪個題目？ | **建議以單位既有的 GitLab 案例為首個試點**，從 14 §6 的第 1 級（MR 樣板與看板 label）開始，不必等工具 | 驗證 12 的假設；訪談清單見 14 §8 | 現在即可開始 |
| D8 | Agent 執行環境除 Claude Code 外，是否需同時支援本地模型？ | 先 Claude Code；契約保持中立 | K4 範圍 | K4 前 |

## 7. 已知風險（規劃者的提醒）

| 風險 | 說明 | 緩解 |
|---|---|---|
| 流程負擔過重 | 檔案與欄位多，小任務可能覺得繁瑣 | G0／G1 走快速通道；欄位由工具與 Agent 填；以指標檢視後精簡 |
| 審查流於形式 | 人類習慣性按核准 | 必看清單 + 挑戰題；定期抽查；量測錯誤採納率 |
| 證據形式化 | 有 log 不代表驗證了對的事 | 驗收條件在規劃時由人審；Validator 提出驗收範圍外的風險 |
| 硬體能力高估 | AI 對圖面的理解未經驗證 | 硬體採保守自主度；以試點調整（10 §10） |
| 規格本身的錯誤 | 09–12 未經實作檢驗 | 工單 1.4 的決策請求機制；K8 統一核對 |
| 防護被誤認為安全邊界 | hook 可被繞過 | 文件明示；真正的強制在 forge 與執行環境 |
