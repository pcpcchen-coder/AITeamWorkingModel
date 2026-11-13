# kit/ — Git-native Operating Kit（樣板與檢查表）

**狀態：** v0.3 設計階段。此目錄目前只有**樣板與檢查表**；`aitw` CLI、領域包、Agent 與 Forge 整合包尚未實作（見 [docs/13](../docs/13-opus-handoff.md)）。

| 路徑 | 內容 | 規格 |
|---|---|---|
| `templates/` | Mission、工作包、證據清單、共讀包、驗證報告、決策請求、人類任務紀錄、週摘要、會議議程、接手包、設定與政策 | [docs/11 §4](../docs/11-toolkit-spec.md) |
| `checklists/` | 韌體安全關鍵審查、硬體釋出（G3）——起始草稿，需領域專家補充 | [docs/10 §9](../docs/10-domain-profiles-sw-fw-hw.md) |
| `packs/`、`agent/`、`forge/` | （待實作）領域包、Claude Code 整合、GitHub 整合 | docs/11 §8–§9 |

## 現在就能用：手動模式

不必等工具。流程見 [docs/09 §12](../docs/09-execution-playbook.md)：

1. 複製 `templates/mission.md`、`templates/wp.md` 到專案 repo，請 AI 依樣板填寫，開 PR 由人類核准。
2. AI 在 `wp/WP-NNN-<slug>` 分支工作；每個驗證指令的完整輸出存檔，依 `templates/evidence-manifest.yaml` 登錄（含 commit 與 sha256）。
3. AI 依 `templates/review-packet.md` 產生共讀包；人類依「必看清單」審查並以 PR review 決定。
4. 主幹開啟分支保護：必須經 PR、必須有人類核准、新 commit 使舊核准失效。

**GitLab 專案：** 把 [`.github/pull_request_template.md`](../.github/pull_request_template.md) 的內容複製為 `.gitlab/merge_request_templates/Default.md`，並建立四個看板 label（等我決定、等我動手、AI 進行中、卡住）。平台對照與各授權等級可強制的範圍見 [docs/14](../docs/14-gitlab-profile.md)。

手動模式缺少自動強制（Gate、證據過期、WIP 上限）——這是工具要補的。

## 注意

- 樣板中的帳號、專案名皆為虛構範例。
- 本 repo 為公開；真實專案請在私有 repo 使用，不要把真實研發資料放進來。
