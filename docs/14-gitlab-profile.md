# 14 — GitLab 執行方式：AI 開發 × 在 GitLab 上共同 Review

**文件狀態：** 設計提案 v0.4 · 2026-11-13
**緣由：** 單位內已有開發案例採用「開發工作由 AI 執行、同仁在 GitLab 上進行 review」。這個做法與 09 的流程方向一致，且已有人實際在用，因此納為**第一優先的落地方式**，並作為首個真實試點的候選。
**查證說明：** 第 3–5 節的 GitLab 功能名稱與授權等級查自 GitLab 官方文件（2026-11-13 讀取，文末列出網址）。GitLab 功能與等級會變動，且自架版本可能較舊；實作前請以單位實際版本再確認。標示 **UNKNOWN** 者為未能由文件確認的項目。
**公開 repo 注意：** 本文不記錄該案例的專案名稱、人員或內容；只描述做法的型態。

## 1. 既有做法的定位：保留什麼、補什麼

目前已知的只有三件事：使用 GitLab、開發由 AI 執行、大家在 GitLab 上 review。細節待訪談（§8）。以這個型態為起點：

| 面向 | 既有做法（已知） | 值得保留 | Kit 要補上的 |
|---|---|---|---|
| 協作平台 | GitLab | 同仁已熟悉 Merge Request（MR）、留言、pipeline；自架 GitLab 適合機密研發資料 | 不換平台；Kit 以 GitLab 為一等公民 |
| 執行者 | AI 執行開發 | 人類時間集中在審查與決策 | 明確的自主度邊界（10）、範圍限制、人類任務接力 |
| 審查 | 大家在 GitLab 上 review | 討論與決定留在 MR 上，可追溯 | 共讀包與必看清單（看什麼、看多深）、挑戰題、審查分級 |
| 證據 | 待確認 | — | 證據清單、標籤規則（AI 不能自標 VERIFIED）、CI 重跑 |
| 核准強制 | 待確認 | — | Gate：誰必須核准、核准是否針對最新版本、AI 身份不計 |
| 進度 | 待確認 | — | 四欄看板、決策佇列與時限、WIP 上限 |
| 接手 | 待確認 | — | 週摘要、接手包與演練 |

**原則：不要求該團隊改變現有習慣才能開始。** 採漸進導入（§6），每一級都能獨立帶來好處。

## 2. 同一套流程、兩種平台

09–13 的流程與檔案契約與平台無關；只有「共讀面」與「關卡」的實作不同。全文的「PR」在 GitLab 上讀作「MR」。

| 流程概念（09、11） | GitHub | GitLab |
|---|---|---|
| 共讀面 | Pull Request | Merge Request（MR） |
| 逐行留言與討論 | Review comment | Thread（可設定必須全部 resolve 才能合併） |
| 人類核准 | PR review：Approve | MR approval（`/approve` 或按鈕） |
| 要求修改 | Request changes | 留下未解決的 thread；不核准 |
| 主幹保護 | Branch protection／Rulesets | Protected branches／Branch rules |
| 領域 owner 加簽 | CODEOWNERS | CODEOWNERS（Premium 以上） |
| CI | GitHub Actions | GitLab CI/CD pipeline |
| 必過檢查 | Required status checks | Merge check：「Pipelines must succeed」 |
| AI 的機器身份 | 機器帳號或 App | Project access token 的 bot user，或 service account |
| MR／PR 樣板 | `.github/pull_request_template.md` | `.gitlab/merge_request_templates/Default.md` |
| 看板發佈 | Pages（公開 repo 即公開） | GitLab Pages，可限專案成員存取 |
| 任務與看板 | Issues、Projects | Issues、Issue boards、Milestones、Labels |

## 3. GitLab 上的九步流程

| # | 步驟（09 §4） | 在 GitLab 上怎麼做 |
|---|---|---|
| 1 | Mission Intake | 建 Issue（或 Epic）描述目標；AI 起草 `mission.md` 開 MR；Primary 核准合併 |
| 2 | Plan | AI 開 Plan MR，內含各 `wp.md`；每個 WP 可對應一張 Issue 方便在看板上拖拉 |
| 3 | Plan Approval | Primary 在 Plan MR 上以 thread 提修改、核准後合併 → 驗收條件凍結 |
| 4 | Execute | AI 以 bot 身份在 `wp/WP-NNN-<slug>` 分支工作，開 Draft MR；證據檔隨 commit 進分支 |
| 5 | Verify | MR pipeline 的 `aitw-verify` job 在乾淨 runner 重跑驗收；Validator 報告寫入分支 |
| 6 | Packet | 共讀包存為 repo 檔案，並摘要到 MR 說明（依 MR 樣板）；MR 取消 Draft |
| 7 | Co-Review | Primary／Backup 在 MR 上開 thread、回答挑戰題、核准；決策以留言指令記錄 |
| 8 | Gate & Merge | `aitw-gate` job 檢查證據與核准；「Pipelines must succeed」擋住未通過者；由人類合併 |
| 9 | Update | 主幹 pipeline 產生看板與 `STATUS.md`；看板可發佈到限成員存取的 GitLab Pages |

**GitLab 原生功能可直接當「共推」工具：**

- **Labels + Issue board** 即四欄看板的人工版：`等我決定`、`等我動手`、`AI 進行中`、`卡住`。工具完成前就能用。
- **Milestone** 對應 Mission；**Assignee／Reviewer** 對應「下一步該誰」。
- **Thread 必須 resolve** 天然對應「要求修改必須被回應」。
- **To-Do 清單與通知** 即每日「等我決定」的入口。

## 4. 依授權等級的強制方式

這是 GitLab 與 GitHub 最大的差異，直接決定 Gate 怎麼做。

| 需要強制的事 | GitLab Free | Premium／Ultimate |
|---|---|---|
| AI 不能直接推主幹、不能合併 | **可以**：主幹設為保護分支，「Allowed to merge」限 Maintainers，「Allowed to push and merge」設為無人；bot 給 Developer 角色 | 同左，並可指定到個別使用者或群組 |
| 合併前 pipeline 必須通過 | **可以**：Merge check「Pipelines must succeed」 | 同左 |
| 合併前**必須**有人類核准 | **平台本身不能強制**：Free 的核准是選用的，不擋合併 → 改由 `aitw-gate` job 讀取核准紀錄，未達條件就讓 pipeline 失敗 | 可用 approval rules 設定必要核准人數與指定核准者；`aitw-gate` 仍做角色與版本檢查 |
| MR 作者／提交者不得核准 | 由 `aitw-gate` 排除 bot 身份與 MR 作者 | 「Prevent approval by merge request creator」「Prevent approvals by users who add commits」 |
| 新 commit 使舊核准失效 | 由 `aitw-gate` 比對核准時間與最新版本 | 「Remove all approvals」（推送新 commit 時） |
| 領域 owner 加簽 | 由 `aitw-gate` 依 policy 與 config 的領域 owner 檢查 | CODEOWNERS + 保護分支的「Require approval from code owners」 |
| 專案維護者無法自行放寬規則 | 無（靠制度與稽核） | Ultimate：merge request approval policies 可覆寫專案設定 |

**結論：**

1. **即使是 Free 版，09 的 Gate 也能成立**——強制點是「保護分支 + Pipelines must succeed + `aitw-gate` job」，核准紀錄由 job 透過 API 回查。這與 11 §5 的設計一致，不需要改模式。
2. Premium 以上可把一部分檢查交給平台原生功能，`aitw-gate` 變成第二道防線與統一報告。
3. 單位使用哪個等級、哪個版本，是 K2b 前必須確認的事（§8）。

## 5. 在 GitLab 實作 Gate 的六個要點

| # | 要點 | 原因 | 作法 |
|---|---|---|---|
| 1 | **CI 設定檔不放在 AI 改得到的地方** | MR pipeline 使用**來源分支**的 `.gitlab-ci.yml`；AI 可在自己的分支改掉 pipeline 讓 Gate 消失 | 專案設定「CI/CD configuration file」指向**另一個專案**的檔案（例：`aitw.gitlab-ci.yml@group/ci-config`，Free 可用）；該專案只有人類可寫。Ultimate 可改用 pipeline execution policies |
| 2 | **Gate 用的工具與 policy 取自主幹** | 與 11 §5.3 相同（不變量 I3） | job 內另外取出目標分支的 `.aiteam/` 與已釋出版本的 `aitw`；MR 分支內容只當資料 |
| 3 | **核准後要重新評估 Gate** | 核准本身不會觸發新的 pipeline | 候選作法（需實測擇一）：核准者重試 `aitw-gate` job；以 webhook 觸發 pipeline；外部 status check（等級 UNKNOWN）。合併者按鈕前看到的必須是核准後的 Gate 結果 |
| 4 | **核准要綁定版本** | Free 不會自動在新 commit 時移除核准 | `aitw-gate` 只承認時間晚於最新 MR 版本的核准；核准 API 可帶 `sha`，不符會被拒絕。取得「最新版本時間」的 API 欄位需實作時確認 |
| 5 | **留言指令的前綴要避開 quick actions** | GitLab 會把 `/` 開頭的已知指令當 quick action 執行並從留言內容移除 | 指令前綴設為可設定；GitLab 預設改用 `aitw:`（例：`aitw: decide DR-001 A 理由`、`aitw: read`、`aitw: understood …`）。`/approve` 仍用 GitLab 原生 |
| 6 | **MR pipeline 不給機密** | pipeline 會執行 AI 寫的程式 | 機密設為 protected variables；未保護的來源分支預設取不到。runner 以容器隔離、限時限資源，盡量斷網 |

**AI 身份：** 自架 GitLab 任何授權都能建立 project access token，系統會自動產生 bot user（帳號樣式 `project_{id}_bot_{隨機字串}`）；也可用 service account。給 Developer 角色即可開分支與 MR、但不能合併到保護分支。bot 能否按核准，文件未明確說明（**UNKNOWN**）——無論如何 `aitw-gate` 一律不計 Agent 身份的核准。

**看板：** GitLab Pages 的存取控制可把站台限制為專案成員（需管理員先啟用功能），因此真實專案的看板可放在 Pages；公開專案仍不可放真實資料。

## 6. 漸進導入階梯（從既有做法出發）

每一級只加一樣東西，隨時可停在某一級。

| 級 | 加入什麼 | 需要的工具 | 團隊得到什麼 |
|---|---|---|---|
| **0 現況** | AI 開發、MR review | 無 | 已在運作 |
| **1 看得懂** | MR 樣板（共讀包精簡版：主張與標籤、必看清單、實際執行的驗證、未驗證範圍）；四個看板 label | 只需樣板與 label，今天可做 | 審查者知道該看哪裡、哪些結論只是假設 |
| **2 有邊界** | `mission.md`、`wp.md`（範圍、驗收條件、Gate、執行者）；AI 改用 bot 身份；主幹保護 | 樣板（手動模式，09 §12） | AI 不會越做越大；驗收條件先講清楚；人類任務有紀錄 |
| **3 有證據** | 證據清單與標籤規則；pipeline 重跑驗收 | `aitw` K0–K1 + CI | 「測試通過」由 CI 證明，不靠 AI 自述 |
| **4 有關卡** | `aitw-gate`；CI 設定移到獨立專案；決策請求與留言指令 | `aitw` K2（GitLab adapter） | 核准的人、版本、範圍被機器檢查 |
| **5 可持續** | 看板、每日簡報、週摘要、共讀共推會議程、接手演練 | `aitw` K3、K6、K7 | Backup 低負擔跟上；人員異動時可接手 |

建議該案例先做第 1 級（成本最低、回饋最快），並同時量測 09 §13 的基準數字，作為後續調整的依據。

## 7. 對規格與工單的影響

| 文件 | 調整 |
|---|---|
| 11 §7.2 | `ForgeAdapter` 的實作增加 `GitLabForge`；介面不變（`get_pr` 等方法對應 MR） |
| 11 §9 | Forge 整合包分為 `kit/forge/github/` 與 `kit/forge/gitlab/`（CI 範本、MR 樣板、設定指南、`doctor` 檢查項） |
| 11 §9.3 | 留言指令前綴可設定（GitHub 預設 `/`，GitLab 預設 `aitw:`） |
| 13 K2 | 拆為 **K2a**（Gate 核心 + FakeForge + GitHub，用於本 repo 自身開發）與 **K2b**（GitLab adapter 與整合包，用於單位試點）；兩者共用同一組 Gate 測試案例 |
| 13 §6 | D1 更新：單位使用 GitLab；本 repo 留在 GitHub；兩個 adapter 都做，GitLab 為真實試點的優先 |
| 13 K8 | 快速上手文件編號順延為 `docs/15-quickstart.md`，並含 GitLab 版步驟 |
| 08 | 新增 ADR-014 |

`aitw doctor` 在 GitLab 上需檢查：保護分支設定、「Pipelines must succeed」是否開啟、CI 設定檔是否指向外部專案、bot 的角色、（Premium 以上）approval settings 是否符合 §4。

## 8. 需要向該案例團隊確認的事（訪談清單）

請勿把答案中的內部名稱寫進本公開 repo；只需回報型態。

1. GitLab 是自架或 GitLab.com？版本與授權等級（Free／Premium／Ultimate）？
2. AI 以什麼方式執行（哪一種 Agent 工具、在誰的機器或 runner 上）？以誰的帳號提交與開 MR？
3. 現在的 review 規則：誰一定要看、幾個人核准才合併、誰按合併？是否有保護分支？
4. 是否已有 CI pipeline？測試由 AI 本機跑還是 pipeline 跑？
5. 任務從哪裡來（Issue、口頭、文件）？AI 的工作範圍如何界定？
6. 開發內容屬於軟體、韌體或硬體？是否涉及實機燒錄或量測？這些步驟現在由誰做、如何記錄？
7. 審查者目前最花時間或最不放心的是什麼？有沒有發生過「合併後才發現 AI 做錯」的情況？
8. 是否願意作為首個試點，從 §6 的第 1 級開始？

## 9. 參考來源（GitLab 官方文件，2026-11-13 讀取）

- 核准設定：<https://docs.gitlab.com/user/project/merge_requests/approvals/settings/>
- 核准規則與 Free 版行為：<https://docs.gitlab.com/user/project/merge_requests/approvals/>、<https://docs.gitlab.com/user/project/merge_requests/approvals/rules/>
- Code Owners：<https://docs.gitlab.com/user/project/codeowners/>
- 保護分支：<https://docs.gitlab.com/user/project/repository/branches/protected/>
- Project access tokens、service accounts：<https://docs.gitlab.com/user/project/settings/project_access_tokens/>、<https://docs.gitlab.com/user/profile/service_accounts/>
- CI 設定檔位置與 MR pipeline：<https://docs.gitlab.com/ci/pipelines/settings/>、<https://docs.gitlab.com/ci/pipelines/merge_request_pipelines/>
- Merge checks：<https://docs.gitlab.com/user/project/merge_requests/auto_merge/>
- Quick actions、Notes API、核准 API：<https://docs.gitlab.com/user/project/quick_actions/>、<https://docs.gitlab.com/api/notes/>、<https://docs.gitlab.com/api/merge_request_approvals/>
- Pages 存取控制：<https://docs.gitlab.com/user/project/pages/pages_access_control/>
- Approval policies（Ultimate）：<https://docs.gitlab.com/user/application_security/policies/merge_request_approval_policies/>

**未能確認（UNKNOWN）：** bot user／service account 能否核准 MR；「所有 thread 必須 resolve」設定的確切名稱與等級；外部 status checks 的等級；核准時間與 MR 最新版本比對所需的 API 欄位。
