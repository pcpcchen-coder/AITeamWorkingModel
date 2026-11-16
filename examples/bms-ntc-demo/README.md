# bms-ntc-demo — 虛構範例專案

> **全部虛構。** 專案、人員、元件、數值、板號皆為示範用的虛構資料，不是實驗結果，也不對應任何真實產品、人員或量測。
> 規格：[docs/12 操作範例](../../docs/12-operating-examples.md)；工單：[docs/13 K0](../../docs/13-opus-handoff.md)。

一個電池模組溫度量測鏈的示範專案：NTC 熱敏電阻 → 上拉分壓 → MCU ADC → 韌體換算 → 通訊訊框 → 上位機 SOH 估算。
本專案停在 docs/12 §4「Plan 剛核准」的時點：六個工作包已規劃、尚未開工。後續工單（K1–K8）以它重現 docs/12 的流程。

## 目錄

| 路徑 | 內容 |
|---|---|
| `.aiteam/` | 專案設定（docs/12 §2 的虛構身份）與路徑政策（docs/10 §7） |
| `knowledge/interfaces/` | 介面契約正本：`analog.yaml`（類比鏈）、`protocol.yaml`（通訊訊框） |
| `knowledge/requirements.yaml` | 虛構需求 |
| `hw/calc/` | 上拉電阻最壞情況計算腳本 |
| `fw/` | 韌體：查表內插換算（主機端 C 單元測試） |
| `sw/` | 上位機：訊框解碼、低溫 SOH 補償、對介面契約的契約測試 |
| `work/missions/M-001-low-temp-accuracy/` | Mission 與 WP-001～WP-006 |

## 在 repo 根目錄執行

```bash
make -C examples/bms-ntc-demo/fw test                    # 韌體主機端單元測試（需 C 編譯器與 make）
python -m pytest examples/bms-ntc-demo/sw                # 軟體測試
python examples/bms-ntc-demo/hw/calc/ntc_divider_worstcase.py --candidates 10k,22k,33k
aitw --repo examples/bms-ntc-demo lint                   # 檔案契約檢查
```

不需要模擬器、EDA 或任何實體設備；所有實體動作（改板、燒錄、量測）在本專案中都是**人類任務**，只以工作包描述。
