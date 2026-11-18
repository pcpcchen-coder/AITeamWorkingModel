# M-001 工作包索引（Plan）

**狀態：** Plan PR 草案，待 owner 核准。合併後各 `wp.md` 的 `acceptance`（含驗證指令）即凍結；之後變更需人類決議（`acceptance_change` 決策請求）。
**來源：** 驗收條件逐字轉寫自 [docs/13 §3](../../../../docs/13-opus-handoff.md)；為讓每條可被單獨驗證，部分句子拆成多條（內容未增減）。另外加入的條目都註明來源（docs/13 §1.2 不變量、docs/11 §13 驗收總則、Mission S3），只會更嚴、不會放寬。

## 1. 工單 ↔ 工作包

| WP | 工單 | 里程碑 | 宣告 Gate | 規模 | 相依 | 預計 PR 數 |
|---|---|---|---|---|---|---|
| [WP-001](WP-001-k0-contracts-skeleton/wp.md) | K0 契約與骨架 | M1 | G1 | M | — | 3（含本 Plan PR） |
| [WP-002](WP-002-k1-lifecycle-evidence/wp.md) | K1 生命週期與證據 | M1 | G1 | M | WP-001 | 2 |
| [WP-003](WP-003-k2a-gate-github/wp.md) | K2a Gate 核心與 GitHub | M1 | G2 | L | WP-002 | 3 |
| [WP-004](WP-004-k2b-gitlab/wp.md) | K2b GitLab | M1 | G2 | M | WP-003 | 2 |
| [WP-005](WP-005-k3-packet-status-board/wp.md) | K3 共讀包、狀態、看板 | M1 | G1 | M | WP-003 | 2 |
| [WP-006](WP-006-k4-agent-claude-code/wp.md) | K4 Agent 整合包 | M2 | G2 | M | WP-005 | 2 |
| [WP-007](WP-007-k5-fw-hw-packs/wp.md) | K5 韌硬體領域包與人類任務 | M2 | G2 | M | WP-005 | 2 |
| [WP-008](WP-008-k6-cadence-metrics/wp.md) | K6 節奏與指標 | M3 | G1 | S | WP-005 | 1 |
| [WP-009](WP-009-k7-takeover-drill/wp.md) | K7 接手演練 | M3 | G1 | S | WP-005 | 1 |
| [WP-010](WP-010-k8-e2e-quickstart/wp.md) | K8 端對端與教學 | M3 | G1 | M | WP-004、006–009 | 2 |

相依依 docs/13 §2：`K0 → K1 → K2a → K3`；K2b 在 K2a 之後、可與 K3 平行；K4、K5、K6、K7 在 K3 之後；K8 最後。共 10 個 WP（Mission 預算 `max_wp: 12`）。

## 2. 驗證指令慣例（請一併核准）

- 所有 `runner: ci` 的測試以 **pytest marker** 選取，從 repo 根目錄執行：`python -m pytest -m wpNNN_acN`；不變量測試用 `inv_i1`～`inv_i10`。
- repo 根的 `pytest.ini` 定義 `testpaths` 與全部 marker（`--strict-markers`），由 WP-001 建立。
- 選不到任何測試時 pytest 結束碼為 5 → 視為失敗，避免「空測試也算過」。
- 範例專案的建置與計算指令以 repo 根為基準（例：`make -C examples/bms-ntc-demo/fw test`）。
- 這些指令是在程式尚未存在時預先凍結的；若實作時發現必須改指令，會以決策請求提出，不會自行修改。

## 3. 不變量 ↔ 工作包

| 不變量 | 主要測試所在 | 補強 |
|---|---|---|
| I1 確定性、不呼叫模型 | WP-001 AC8 | WP-002 AC11、WP-005 AC6 |
| I2 Agent 證據最高 OBSERVED | WP-002 AC2、AC8 | WP-003（Gate 步驟 9） |
| I3 Gate 取自基底分支 | WP-003 AC3、AC9 | WP-004 AC1 |
| I4 只認 head commit 的人類核准 | WP-003 AC10 | WP-004 AC2、AC8 |
| I5 驗收／範圍／人類專屬路徑需人類授權 | WP-003 AC11 | WP-004 AC1 |
| I6 證據只增不改 | WP-002 AC1、AC9 | — |
| I7 無燒錄／儀器／設備控制指令 | WP-001 AC9 | WP-006 AC5、WP-007 |
| I8 範例與測試資料虛構 | WP-001 AC10 | 之後每個 PR 的 fixture 皆受同一測試約束 |
| I9 數字可由檔案重算 | WP-005 AC5、AC7 | WP-008 AC3 |
| I10 HALT 使開工與 Gate 失敗 | WP-002 AC10 | WP-003 AC12 |

WP-005 AC8 會檢查 `inv_i1`～`inv_i10` 每個 marker 至少有一個測試且全部通過（對應 Mission S3，在 M1 結束時達成）。

## 4. Plan 階段的決策請求

以下為實作者在規格中發現的矛盾、缺漏或疑問。每項附選項、影響與建議；owner 可在 Plan PR 留言回覆（例：`DR-P3: A`）。未回覆的項目，會依「建議」先做不相依的部分，並在相關 PR 再次提出。

| # | 問題 | 選項 | 建議 | 影響的 WP |
|---|---|---|---|---|
| DR-P1 | `mission.md` 的 `owner` 尚未填寫（屬人類決定） | owner 自行填入 forge 帳號 | 由 owner 另開 commit／PR 填寫；Agent 不代填 | WP-001 AC1（本 repo 的 lint 在填寫前會指出此缺口） |
| DR-P2 | K0 需要 CI，但 `.github/**` 在 policy 樣板中是 `human_only`（11 §5.1） | A：Agent 在 PR 中提交 `.github/workflows/ci.yml`，列入必看清單，owner 審閱並合併即為授權；B：Agent 只在 `kit/forge/github/` 放草稿，由 owner 自行複製啟用 | **A**（本 repo 尚未安裝 `.aiteam/policy.yaml`，手動模式下 owner 審閱即為人類授權；之後所有 workflow 變更同樣列為必看） | WP-001 |
| DR-P3 | 樣板與 schema 的矛盾：11 §4.2 說每筆證據的執行欄位（`git_sha`、`started_at`、`command`…）皆必填，但樣板中的 `datasheet`／`measurement` 範例與 12 §5.1 的 `EV-002-04` 都沒有；樣板含 `<…>` 佔位字，但 11 §6 的 lint 要檢查「樣板空格未填」 | A：schema 依 `kind` 分必填集合（共同欄位 + 指令類才要求執行欄位；`datasheet` 要求 `source`；`measurement`／`hil_run` 要求 `conditions` 與 `outputs`）；佔位字檢查是獨立的 lint 規則、不套用在 `kit/templates/`；同步修正 11 §4.2；B：照 11 §4.2 字面全部必填，修改樣板與 12 補齊欄位 | **A**（符合 12 的情境且較不易誤報；會在 PR 列出完整必填清單供審） | WP-001、WP-002 |
| DR-P4 | 11 §2 寫 schema 放 `packages/aitw/schemas/`，但 src 佈局下需放在套件內才會隨 wheel 發佈 | A：`packages/aitw/src/aitw/schemas/` 並更新 11 §2；B：維持原路徑，另寫打包設定 | **A** | WP-001 |
| DR-P5 | 驗收指令在程式存在前就被凍結 | A：採用本文 §2 的 marker 慣例；B：改為「指令於實作 PR 中確定，屆時以 acceptance_change 核准」 | **A** | 全部 |
| DR-P6 | I7 要求工具「不含」燒錄／儀器指令，但 K4 的拒絕清單本身必須列出這些工具名稱作為攔截樣式 | A：I7 掃描排除明確列名的拒絕清單資料檔（路徑寫死在測試中，變更即列入必看）；B：拒絕清單以雜湊或編碼儲存 | **A**（可讀性較好，審查者看得懂攔了什麼） | WP-001、WP-006 |
| DR-P7 | 11 §6 定義 `evidence add --by human:<handle>`，與 K1 驗收「無法以參數把 `produced_by` 指定為 `human`」直接矛盾；Agent 也可能冒用人類身份 | A：保留 `--by`，但 (1) 偵測到 Agent 環境時拒絕、(2) handle 必須是 config 中的人類且不在 `agents.identities`、(3) 該證據在 Gate 中須經 forge 回查（新增該證據的 commit 由該人類推送，或有該人類的 review 引用）才算人類證據；K1 驗收的那句解讀為適用 `evidence run`；B：移除 `--by`，人類身份只由 forge 驗證取得（K1 離線無法做到）；C：K1 只支援 Agent 證據，`evidence add` 延到 K5 | **A**；第 (1) 點只是輔助，不是安全邊界，真正保證在 Gate 回查 | WP-002、WP-003、WP-007 |
| DR-P8 | K1 的 `wp start` 要檢查「需啟動核准而未核准」，但 LocalForge 無法回查 forge 上的人類行為（11 §4.4：檔案內容本身不構成核准） | A：K1 只檢查基底分支上存在已決議的 `start_approval` DR（必要條件），`ref` 回查由 K2a 的 Gate 步驟 11 負責；B：K1 的 `wp start` 一律要求 forge | **A**（`wp start` 不是安全邊界，Gate 才是） | WP-002 |
| DR-P9 | `wp start` 的「預算用盡」未定義如何計量（`max_iterations`、`max_agent_minutes`） | A：iterations = 執行日誌中 `wp start` 紀錄數；agent minutes = Agent 證據 `duration_s` 加總（下限估計，報告中標示）；執行日誌採固定行格式寫在 `wp.md` 本文；B：另設 `log.yaml` 機器檔 | **A**，但若 owner 希望機器檔與人讀日誌分離則選 B | WP-002 |
| DR-P10 | Gate 步驟 2 依分支名辨識 PR 種類，但 11 只定義了 `wp/WP-NNN-<slug>` | 提案：`plan/M-NNN-<slug>`、`decision/DR-NNN`、`cadence/<日期>`、`takeover/TKO-<yyyy-mm>`；人類直接提交的 PR 依作者身份判定 | 採用提案並寫入 11 §3。本 Plan PR 依你的指示用 `wp/WP-001-plan` | WP-003 |
| DR-P11 | K2b 的 AC6、AC7 需要實際 GitLab 環境；單位的版本與等級仍未知（13 §6 D1） | A：建立 gitlab.com 上的虛構測試專案（Free），owner 做設定、Agent 經權杖做 API 驗證；B：使用單位自架 GitLab（不可把內部資訊寫回公開 repo）；C：先做離線部分，AC6、AC7 標 NOT RUN 等試點 | **A** 先驗證 Free 行為，再以 B 對照單位版本 | WP-004 |
| DR-P12 | 本 repo 的 PR 目前由 owner 的帳號（`pcpcchen-coder`，經 GitHub 整合）開出，owner 在 GitHub 上無法正式 Approve 自己的 PR；09 §11 的 Solo 模式要求 Agent 用獨立機器身份（13 §6 D2） | A：手動模式期間接受「owner 審閱後自行合併」為核准紀錄，於 PR 留言記錄審查結論；B：建立機器帳號或 GitHub App 給 Agent 使用 | 短期 **A**；K2a 合併前決定是否改 B（否則 Gate 的人類核准在本 repo 無法成立） | 全部；WP-003 前必須決定 |
| DR-P13 | K8 AC2 需要「一位未參與開發的人」；目前人類只有 owner | A：owner 視為未參與（未寫程式）；B：另邀一人 | **B** 較符合原意；若不可行則 A 並在 PR 註明限制 | WP-010 |
| DR-P14 | 本 repo 沒有 `knowledge/requirements.yaml`，但 `satisfies` 必須引用存在的編號 | A：lint 在沒有 requirements 檔時允許引用 Mission 的 `success` 編號（本 Plan 即如此使用 S1–S3）；B：在本 repo 建立 requirements 檔 | **A** | WP-001 |

### 與 01–08 的衝突（依規定以 09–14 為準，僅記錄）

- 05 §4 的 G3 寫「MVP 預設拒絕」；09 §3、11 §5.2 允許 G3 在兩位人類核准下進行。依 09–14 為準；Kit 工具本身不執行任何 G3 動作（Mission out_of_scope）。
- 07 §（Backlog）以後端平台 T01–T12 為主；11 §12 已說明延後項目，無需處理。
