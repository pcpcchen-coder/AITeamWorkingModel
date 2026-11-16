# aitw — Git-native Operating Kit CLI

**狀態：** 開發中（工單 K0）。規格見 [docs/11](../../docs/11-toolkit-spec.md)，工單見 [docs/13](../../docs/13-opus-handoff.md)。

確定性工具：不呼叫任何模型，相同輸入產生相同輸出（不變量 I1）。

```bash
pip install -e "packages/aitw[dev]"
aitw --repo examples/bms-ntc-demo lint     # 檢查檔案契約（schema 與交叉引用）
aitw --repo . --json lint                  # JSON 輸出
python -m pytest                           # 從 repo 根目錄執行全部測試
```

| 結束碼 | 意義 |
|---|---|
| 0 | 通過 |
| 1 | 檢查未通過 |
| 2 | 用法或檔案格式錯誤（YAML 語法、front matter、重複鍵） |
| 3 | 外部相依不可用（後續工單） |
| 4 | HALT 生效（後續工單） |

Schema 位於 `src/aitw/schemas/`（隨套件發佈；DR-P4）。
