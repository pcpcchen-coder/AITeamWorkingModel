# 12 — 操作範例：一個橫跨軟／韌／硬的 Mission 從頭走到尾

**文件狀態：** 設計範例 v0.3 · 2026-11-13

> **讀前必看**
> - 專案、人員、數值、板號、指令輸出**全部虛構**，用來示範流程，不是實驗結果，也不是工具的實際輸出（`aitw` 尚未實作）。
> - 本文同時是範例專案 `examples/bms-ntc-demo/` 與端對端測試的**規格**（見 [13](13-opus-handoff.md) 的 K0、K8）。
> - 流程定義見 [09](09-execution-playbook.md)，領域規則見 [10](10-domain-profiles-sw-fw-hw.md)，指令見 [11](11-toolkit-spec.md)。

## 1. 情境

一個電池模組的溫度量測鏈：

```text
NTC 熱敏電阻 ──▶ 上拉電阻分壓 ──▶ MCU ADC ──▶ 韌體換算溫度 ──▶ 通訊訊框 ──▶ 上位機 SOH 估算
   （硬體）          （硬體）       （硬體/韌體）    （韌體）        （介面契約）       （軟體）
```

問題（虛構）：低溫段溫度誤差偏大，連帶使低溫 SOH 估算不準。

## 2. 人員與設定

| 身份 | Forge 帳號（虛構） | 角色 |
|---|---|---|
| 人員甲 | `primary-a` | Primary；硬體與韌體 owner |
| 人員乙 | `backup-b` | Backup；軟體 owner |
| 人員丙 | `reviewer-c` | Reviewer；具實驗室操作資格 |
| AI | `aiteam-bot` | 所有 Agent 共用的機器身份（核准一律不計） |

```yaml
# .aiteam/config.yaml（節錄）
project: bms-ntc-demo
people:
  - {handle: primary-a,  roles: [primary],  domains: [hw, fw]}
  - {handle: backup-b,   roles: [backup],   domains: [sw]}
  - {handle: reviewer-c, roles: [reviewer], domains: [hw, fw], qualifications: [bench_low_voltage, thermal_chamber]}
agents:
  identities: [aiteam-bot]
wip:
  max_in_review_per_person: 3
  max_open_decisions: 5
  max_rework: 3
```

## 3. 第 0 天：Mission Intake（人類 20 分鐘）

人員甲執行 `/mission-intake`。AI 只問問題、不替人決定目標：

```text
AI：這個 Mission 完成時，什麼可量測的結果算成功？
甲：-20°C 到 60°C 的溫度量測誤差在 ±1°C 內，用樣板實測確認。
AI：哪些事情明確不做？
甲：不換 MCU、不改 PCB 佈局；只允許改被動元件值和韌體。
AI：哪些動作必須由人執行？
甲：改板、燒錄、溫箱量測。釋出改版 BOM 要我和丙都簽。
AI：我可以自主進行到哪？
甲：分析、計算、模擬、韌體與軟體的主機端測試可以直接做，做完給我審。
```

產出 `work/missions/M-001-low-temp-accuracy/mission.md`（節錄）：

```yaml
id: M-001
title: 改善低溫段溫度量測準確度
owner: primary-a
success:
  - id: S1
    text: 樣板實測 -20~60°C 溫度誤差 ≤ ±1°C
    ladder_required: V4
out_of_scope: [更換 MCU, 變更 PCB 佈局]
human_only: [改板, 燒錄, 溫箱量測, BOM 釋出]
budget: {max_wp: 10, review_minutes_per_week: 90}
```

Mission PR 由 `aiteam-bot` 開出，甲核准合併；乙留 `/read`。

## 4. 第 1 天：規劃（AI 起草，人類 15 分鐘審）

`/wp-plan M-001` 產生 Plan PR，內含六個工作包：

| WP | 內容 | 領域 | 執行者 | 自主度 | Gate | 審查 | 最高驗證階 | 相依 |
|---|---|---|---|---|---|---|---|---|
| WP-001 | 量測鏈誤差預算分析 | research | ai | A3 | G0 | R1 | V2 | — |
| WP-002 | 上拉電阻值的最壞情況計算與模擬；更新類比介面契約 | hw | ai | A2 | G2 | R2 | V3 | WP-001 |
| WP-003 | 韌體改用查表內插換算溫度 | fw | ai | A2 | G1 | R2 | V2 | WP-002 |
| WP-004 | 上位機 SOH 低溫補償改用新溫度資料 | sw | ai | A2 | G1 | R2 | V3 | WP-003 |
| WP-005 | 樣板改裝與三點溫度量測 | hw | **human** | A1 | G3 | R3 | V4 | WP-002、WP-003 |
| WP-006 | 改版 BOM 釋出 | hw | pair | A0 | G3 | R3 | — | WP-005 |

甲在 Plan PR 的審查留言：

```text
CHANGE: WP-003 的驗收條件只寫「全量程誤差」，請加上表格端點與超出範圍的行為。
Q: WP-005 為什麼只量三點？
```

AI 回覆並修正：WP-003 增加 AC3（端點）；說明三點（低／常溫／高）是驗證 S1 的最小集合，並把「增加中間點」列為可選項讓甲決定。甲核准合併 → **六個 WP 的驗收條件與驗證指令自此凍結**。WP-005、WP-006 標示 `start_approval: required`。

## 5. 範例 A — 硬體分析（WP-002）：計算、模擬、決策請求、跨領域介面

### 5.1 AI 執行並留證

```text
$ aitw wp start WP-002
✔ HALT：未啟用
✔ 相依：WP-001 已 ACCEPTED
✔ Gate：G2（免個別啟動核准）
→ 已建立分支 wp/WP-002-pullup-analysis

$ aitw evidence run WP-002 --ac AC1 --kind calc -- python hw/calc/ntc_divider_worstcase.py --candidates 10k,22k,33k
✔ EV-002-01 已記錄 · 結束碼 0 · commit 1c7e0d4（工作區乾淨）
  輸出  evidence/EV-002-01.log  sha256:9a30…
  標籤  OBSERVED（agent 產生）

$ aitw evidence run WP-002 --ac AC2 --kind sim -- make -C hw/sim run
✔ EV-002-02 已記錄 · kind=sim → 標籤上限 OBSERVED（規則 L3）
```

規格書參數以 `datasheet` 證據登錄；找不到的照實標示：

```yaml
- id: EV-002-03
  kind: datasheet
  source: {document: "NTC-10K-EXAMPLE 規格書（虛構）", revision: "C", page: 4}
  value: {parameter: "R25 容差", text: "±1%"}
  label: OBSERVED
- id: EV-002-04
  kind: datasheet
  label: UNKNOWN
  gap: "規格書未提供 -20°C 以下的電阻容差表；低溫段容差為外推假設"
```

### 5.2 AI 提出決策請求（不自己選）

```yaml
# decisions/DR-001.md（節錄）
id: DR-001
wp: WP-002
kind: choice
question: 上拉電阻由 10k 改為 22k 或 33k？
options:
  - id: A
    summary: 22k
    impact: 低溫段解析度改善（中）；高溫段解析度略降
    reversible: true
  - id: B
    summary: 33k
    impact: 低溫段解析度改善（大）；高溫段解析度降幅較大，接近 60°C 時餘裕變小
    reversible: true
recommendation: {option: A, reason: "兩端解析度較平衡；B 的高溫餘裕依賴 EV-002-04 的外推假設"}
needed_by: 2026-11-18
blocks: [WP-003, WP-005]
```

### 5.3 人類共讀（R2，約 20 分鐘）

共讀包 `packet-r1.md` 的主張表（節錄）：

| # | 主張 | 標籤 | 證據 | 驗證階 | 範圍限制 |
|---|---|---|---|---|---|
| C1 | 現行 10k 上拉在低溫段每 °C 對應的 ADC 變化量過小，是主要誤差來源 | OBSERVED | EV-002-01 | V2 | 計算模型，未經實測 |
| C2 | 改為 22k 後，全量程最壞情況誤差可落在目標內 | HYPOTHESIS | EV-002-01、02 | V3 | 低溫容差為外推（EV-002-04）；需 WP-005 實測 |
| C3 | 建議樣板先以 22k 驗證 | RECOMMENDATION | DR-001 | — | 僅適用樣板，不代表可釋出 |

必看清單（由 policy 產生）：

| 項目 | 原因 | 預估 |
|---|---|---|
| `knowledge/interfaces/analog.yaml` 第 12–15 行 | **介面契約變更（跨領域）** | 3 分 |
| `hw/calc/ntc_divider_worstcase.py` 第 40–88 行 | 最壞情況的假設組合 | 10 分 |
| 主張 C2 | AI 標示 HYPOTHESIS | 3 分 |
| EV-002-04 | UNKNOWN 缺口 | 2 分 |

人員乙（Backup）執行 `/coread WP-002`，AI 依必看清單帶讀並出挑戰題：

```text
挑戰題：為什麼模擬通過還不能把 C2 標成 VERIFIED？
乙（/understood）：模擬只到 V3，而且低溫容差是外推值；要等樣板量測。
```

人員甲在週會上決定（留言即正本）：

```text
/decide DR-001 A 同意建議；高溫餘裕優先。
```

### 5.4 Gate

因變更了 `knowledge/interfaces/**`，policy 要求**硬體、韌體、軟體 owner 都核准**：

```text
$ aitw gate check --pr 9
Gate 報告 · WP-002 · head 1c7e0d4 · 實際 Gate：G2（跨領域：hw, fw, sw）
 ✔ 範圍・驗收定義・證據完整・證據新鮮・標籤與主張
 ✔ 決策          DR-001 = A（primary-a；留言已回查）
 ✘ 人類核准      已有 primary-a（hw, fw）；尚缺 sw owner（backup-b）
結果：未通過
下一步：請 backup-b 審查介面契約變更（必看 1 項，約 3 分鐘）
```

乙核准後通過、合併。結論留在知識庫時仍是「22k 為**樣板驗證用的建議值**」，不是已驗證的設計。

## 6. 範例 B — 韌體（WP-003）：驗證、返工、範圍變更

### 6.1 執行

AI 由 `analog.yaml` 產生查表、實作內插與主機端測試：

```text
$ aitw evidence run WP-003 --ac AC1 --kind test_run -- make -C fw test
✔ EV-003-01 已記錄 · 結束碼 0 · 耗時 4.2s · commit 3f9c2ab（工作區乾淨）
  標籤  OBSERVED（agent 產生；需 CI 重跑才能成為 VERIFIED）

$ aitw evidence run WP-003 --ac AC2 --kind size_report -- make -C fw size
✔ EV-003-02 已記錄 · Flash +412 bytes（預算內）

$ aitw wp submit WP-003
✔ lint 通過 · 證據完整 · 審查者 WIP：primary-a 1/3
→ 共讀包骨架已產生，PR #14 轉為 ready
```

### 6.2 CI 重跑與 Validator

CI 依**基底分支上凍結的**指令重跑通過。Validator 的驗證報告（節錄）：

```yaml
verdict: PASS
criteria: {AC1: PASS, AC2: PASS, AC3: PASS}
findings:
  - id: F1
    severity: risk
    text: ADC 讀值超出表格上限（對應 NTC 斷線）時，函式回傳表格端點溫度且不報錯
    in_acceptance_scope: false
    suggestion: 請人類判斷是否屬於本 WP 範圍
only_verifiable_on_hardware:
  - ADC 取樣雜訊與濾波效果
  - 實際轉換時間
```

驗收條件都過了，但 Validator 把「驗收條件沒涵蓋到的風險」攤開給人看，不替人決定。

### 6.3 共讀：挑戰題抓到問題

```text
挑戰題：NTC 斷線時，韌體回報什麼溫度？上位機分得出來嗎？
乙（/understood）：回傳表格端點的低溫值，沒有錯誤旗標；上位機會當成真的很冷。
甲（REQUEST_CHANGES）：
  CHANGE: 斷線與短路必須回報故障，不可回傳看似合理的溫度。
```

→ WP-003 進入 **REWORK**（第 1 次）。

### 6.4 返工觸及範圍外 → 決策請求

這次返工有兩件事 AI 不能自己決定：(1) 要新增驗收條件（驗收定義已凍結）；(2) 回報故障需要在通訊訊框加旗標，會動到 `knowledge/interfaces/protocol.yaml`，超出 WP-003 的 `scope.paths`。AI 把兩件事合成一個決策請求：

```yaml
# DR-002（節錄）
kind: acceptance_change
question: 新增驗收條件 AC4「斷線／短路必須回報故障」；故障旗標涉及的通訊介面變更如何處理？
options:
  - {id: A, summary: "新增 AC4，並擴大 WP-003 範圍納入介面變更", impact: "WP-003 成為 G2 跨領域；審查範圍變大"}
  - {id: B, summary: "新增 AC4，WP-003 只做韌體內部的故障偵測與錯誤碼；另開 WP-007 處理介面與上位機", impact: "WP-003 變更較小；WP-004 需等 WP-007"}
recommendation: {option: B, reason: 變更較小、各自可獨立驗證}
```

```text
甲：/decide DR-002 B
```

AI 依決議新增 AC4、斷線／短路偵測與測試，重新留證、CI 重跑、產生 `packet-r2.md`。

### 6.5 Gate 通過

```text
$ aitw gate check --pr 14
Gate 報告 · WP-003 · head 8a41c07 · 實際 Gate：G2（原 G1；驗收定義變更 → 至少 G2）
 ✔ 範圍            7 個檔案皆在 scope 內
 ✔ 驗收定義        AC4 新增；已由 DR-002 授權
 ✔ 證據完整        AC1–AC4
 ✔ 證據新鮮        CI 驗證針對 8a41c07（run 1024）
 ✔ 標籤與主張      5 條主張
 ✔ 決策            DR-002 = B（primary-a；留言已回查）
 ✔ 人類核准        primary-a 針對 8a41c07 核准
結果：通過
```

共讀包 r2 的「未驗證範圍」明列：**僅主機端（V2）驗證；實機行為待 WP-005**，並自動帶出交給人燒錄的檔案資訊（CI 產物與 sha256）。

## 7. 範例 C — 人類任務（WP-005）：AI 準備、人動手、AI 分析、人簽認

### 7.1 AI 準備程序書，人類啟動核准（G3）

AI 產生程序書與空白紀錄表（樣板：[`kit/templates/human-task-record.md`](../kit/templates/human-task-record.md)），並開啟啟動核准 DR-003。程序書節錄：

```text
目的        驗證 S1：樣板在三個溫度點的量測誤差
待測物      樣板 P-07（虛構），硬體版本 A1，改裝：上拉電阻 10k → 22k
韌體        CI run 1024 產物 fw-demo.hex，sha256:c41f…（由已核准 commit 8a41c07 重建）
設備        溫箱、參考溫度計（需填校正編號）
步驟        1 改裝並拍照 → 2 燒錄並確認版本字串 → 3 -20°C 穩定 20 分鐘後記錄 10 筆 → 4 25°C → 5 60°C
預期        各點誤差 ≤ ±1°C
中止條件    任何異常發熱、電流超過限值、溫箱告警 → 立即斷電並記錄
安全        依機構實驗室 SOP；本程序不取代 SOP
```

丙（合格執行者）與甲審閱後，兩人核准 DR-003。

### 7.2 人執行並照實記錄

丙依程序操作，執行 `/human-task WP-005` 逐欄填寫。**偏離照實記**：

```yaml
executor: reviewer-c
dut: {id: P-07, hw_rev: A1, rework: "R12 10k→22k", fw_sha256: "c41f…"}
instruments:
  - {type: 溫箱, cal_id: "CAL-EX-001"}
  - {type: 參考溫度計, cal_id: "CAL-EX-002"}
deviations:
  - "溫箱最低只穩定在 -18°C，未達程序要求的 -20°C"
raw_data:
  - {uri: "lab-store://demo/WP-005/run1.csv", sha256: "77be…"}
```

```text
$ aitw evidence add WP-005 --ac AC1 --kind measurement --file run1.csv --by human:reviewer-c
✔ EV-005-01 已記錄 · produced_by=human:reviewer-c · 條件欄位完整
  注意：紀錄含 1 項偏離，共讀包將自動列入必看清單
```

### 7.3 AI 分析，人簽認

AI 的共讀包主張：

| # | 主張 | 標籤 | 證據 | 範圍限制 |
|---|---|---|---|---|
| C1 | 樣板 P-07 在 -18°C、25°C、60°C 三點誤差皆在 ±1°C 內 | OBSERVED | EV-005-01 | 單一樣板；低溫點為 -18°C 而非 -20°C |
| C2 | S1（-20~60°C）已達成 | **UNKNOWN** | — | -20°C 未量到；不外推 |

AI 沒有把「-18°C 過了」說成「-20°C 過了」。R3 審查會上，甲（非執行者）依原始資料簽認 C1 → VERIFIED（範圍照寫），並決定：開 WP-008 借用可達 -20°C 的溫箱補量，WP-006（BOM 釋出）維持 BLOCKED。

## 8. 範例 D — 軟體（WP-004）：快速通道

純軟體、G1、可完全自動驗證，是最短路徑：

1. AI 實作 + 單元測試 + 與 `protocol.yaml` 的契約測試；`evidence run` 留證。
2. CI 重跑通過 → 共讀包必看清單只有一項（溫度換算函式，8 分鐘）。
3. 乙（軟體 owner）審查並核准 → Gate 通過 → 合併。

人類總投入約 10 分鐘。這條通道快，是因為風險低且可驗證，不是因為省略了檢查。

## 9. 每日簡報（人員甲早上看到的）

```text
$ aitw brief --for primary-a
【等你決定】2
  DR-001  上拉電阻 22k 或 33k？        需求日 11/18   卡住：WP-003、WP-005
  PR #14  WP-003 共讀包 r2（必看 3 項，約 18 分鐘）
【等你動手】0
【昨日完成】
  WP-001 已接受 · WP-002 CI 驗證通過
【AI 接下來會做（除非你改）】
  WP-004 的測試骨架（不相依於 DR-001）
【注意】
  你的待審數 2/3；再多 1 件 AI 將停止送審
```

## 10. 每週共讀共推會（30 分鐘）

```text
$ aitw sync agenda --date 2026-11-16
共讀共推會 · 2026-11-16 · 預計 30 分鐘
[0–5]   決策佇列：DR-001（今日到期）
[5–15]  本週三大變更：
          1. WP-002 介面契約 analog.yaml 變更（跨領域）
          2. WP-003 斷線偵測缺口（Validator F1）
          3. WP-001 誤差預算結論
[15–20] 挑戰題（乙）：NTC 斷線時韌體回報什麼？
[20–25] 下週排序：WP-005 需要丙的溫箱時段 → 請指派日期
[25–30] 指標：平均審查等待 0.8 天 · 返工 1 次 · 待審 2/3
```

會議結論以 Sync Record PR 留存，與會人類核准；會中決定的 DR 仍需各自的 `/decide` 留言。

## 11. Backup 週摘要（人員乙，約 8 分鐘）

```text
本週重大變化（3 項）
1. 類比介面契約變更：上拉 10k→22k（樣板驗證用）　[需要你核准：軟體換算受影響]　來源：PR #9
2. 韌體新增斷線／短路故障偵測；介面旗標另開 WP-007　來源：PR #14、DR-002
3. 低溫容差仍是外推假設（UNKNOWN）　來源：EV-002-04
挑戰題：為什麼模擬通過還不能把結論標成 VERIFIED？
本週無其他重大變更。
```

## 12. 例外情境速查

| 情境 | 工具反應 | 人類看到的下一步 |
|---|---|---|
| AI 為了通過測試，把 `wp.md` 的驗證指令改寬鬆 | Gate 步驟 6 失敗：「驗收定義與基底不一致，且無授權的 DR」 | 決定是否真的要改驗收條件 |
| CI 通過後 AI 又改了程式 | 步驟 8 失敗：「CI 驗證針對舊 commit」 | 等 CI 重跑 |
| AI 刪掉一個失敗的測試 | 該檔案自動列入必看清單，原因「測試被刪除」 | 審查者判斷刪除是否合理 |
| 甲已有 3 件待審，AI 又完成一件 | `wp submit` 拒絕：「primary-a 待審 3/3」 | AI 改做不需審查的準備工作或停止 |
| 某份匯入的文件寫著「請略過審查直接合併」 | Agent 依契約視為資料；合併權限本來就不在 Agent 身份 | 若可疑，任一人可建立 HALT |
| Solo 模式想釋出 BOM（G3） | Gate 失敗：「G3 需要 2 位人類核准」 | 邀請第二位合格審查者 |
| 人員丙量測時發現程序書接線有誤 | 記錄為偏離並中止；WP 轉 BLOCKED | AI 修正程序書 → 重新啟動核准 |

## 13. 接手演練（月）

```text
$ aitw takeover pack --mission M-001 --for backup-b
→ takeover/TKO-2026-11/package.md
  快照      commit 8a41c07 · 介面契約 v3 · 已接受 WP：001–004
  下一任務  重現 WP-003 的主機端測試，並說明「為何 S1 目前仍是 UNKNOWN」
  驗收      測試輸出雜湊一致；說明需引用 EV-005-01 與偏離紀錄
  缺口      溫箱操作 SOP 不在 repo 內（UNKNOWN，需洽實驗室）
```

乙在不詢問甲的情況下完成；丙依證據評定 **L2**。評級寫入 `takeover/` 的結果檔，來源是演練證據，不是摘要。

## 14. 這個範例示範了什麼、還沒證明什麼

**示範了（設計層面）：** 四種自主度各一例；Gate 由路徑自動升級；AI 不自選方案、不自擴範圍、不外推量測；驗收條件凍結；返工與決策請求；人類任務接力；共讀挑戰題抓到驗收條件沒涵蓋的風險。

**還沒證明（需試點）：** 審查時間的假設是否成立；必看清單的規則會不會漏掉重點或過多；AI 對真實 EDA 檔案的處理能力；人類是否願意照實填偏離；WIP 上限的合適數值。
