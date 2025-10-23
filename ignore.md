# 不版控文件清單（建議加入 .gitignore）

本檔列出本專案中建議「不納入版控」的檔案與目錄，便於在團隊中統一規範。若你使用 Git，請將下列項目加入 `.gitignore`。

## 建議忽略項目
- 機密與設定
  - `.env`
  - `.env.*`
- 本地資料/範例輸出
  - `memory_store.json`
  - `test_memory.json`
- Python 產物
  - `__pycache__/`
  - `*.py[cod]`
  - `*.pyo`
  - `*.egg-info/`
- 日誌與快取
  - `*.log`
  - `.cache/`
- 作業系統產生檔
  - `.DS_Store`
  - `Thumbs.db`

## `.gitignore` 範例
將以下內容貼到專案根目錄的 `.gitignore`：

```
# Secrets
.env
.env.*

# App data
memory_store.json
test_memory.json

# Python
__pycache__/
*.py[cod]
*.pyo
*.egg-info/

# Logs & cache
*.log
.cache/

# OS
.DS_Store
Thumbs.db
```

> 提醒：`ignore.md` 為說明文件，本身可納入版控；實際忽略規則仍需加入 `.gitignore` 才會生效。
