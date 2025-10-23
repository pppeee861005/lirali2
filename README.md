# Linali 個人管家（CLI）

一個會話式「個人管家/助理」專案。助理以「利娜莉 Linali」角色與你互動，並透過本地 JSON 記憶庫讀寫你的偏好、代辦與重點資訊。支援寫入、查詢、更新、刪除、主題總覽、統計、與主題彙整等功能。

## 功能特色
- 記憶庫操作：寫入/查詢/更新/刪除（含主題、標籤、關鍵字）
- 主題總覽：各主題的數量、常見標籤與最近活動時間
- 統計資訊：總記憶數、主題數、熱門標籤
- 主題彙整：輸出結構化資料，便於後續 LLM 摘要
- 互動對話：模型會自動呼叫工具來操作記憶

## 專案結構
- `agent_enhanced.py`：互動式助理主程式（需要 `OPENAI_API_KEY`）
- `test_features.py`：離線功能示範（不需連網/金鑰）
- `memory_store.json`：預設記憶資料庫（互動模式使用）
- `QUICK_START.md`, `UPDATE_NOTES.md`：快速開始與更新說明

## 環境需求
- Python 3.8+（本機驗證於 Python 3.13）
- 套件：`openai`, `python-dotenv`

安裝依賴：
```bash
pip install openai python-dotenv
```

## 設定 API 金鑰（互動模式需要）
可先複製範本檔為 `.env`：
```bash
# macOS/Linux
cp .env.example .env
# Windows (PowerShell)
Copy-Item .env.example .env
```

建立 `.env` 檔：
```bash
OPENAI_API_KEY=你的API金鑰
```

## 使用方式
### 1) 離線功能示範（不需 API 金鑰/連網）
```bash
python test_features.py
```
會建立 `test_memory.json`，示範寫入/查詢/更新/刪除、主題總覽、統計與主題彙整。程式尾端會詢問是否刪除檔案。

### 2) 互動式助理（需要 API 金鑰與連網）
```bash
python agent_enhanced.py
```
- 對話中，助理會根據你的指令自動呼叫工具（如 `write_memory`, `read_memory` 等）操作 `memory_store.json`。
- 預設稱呼已調整為「主人」。若需自訂稱呼或語氣，可修改 `agent_enhanced.py` 內的 system prompt。

## 記憶工具一覽（對話中自動使用）
- `write_memory(topic, title, content, tags=[])`：寫入記憶。
- `read_memory(topic=None, title=None, query=None, tags=None)`：查詢記憶（可依主題/標題/關鍵字/標籤）。
- `update_memory(topic, title, new_content=None, new_tags=None)`：更新記憶內容或標籤。
- `delete_memory(topic, title=None)`：刪除單筆或整個主題。
- `list_topics()`：列出主題、數量、標籤、最近活動時間。
- `get_statistics()`：輸出總記憶數、主題數、熱門標籤。
- `summarize_topic(topic)`：輸出主題內各條目的結構化摘要資料。

## 常見問題
- 看不到互動回覆？請確認 `.env` 內 `OPENAI_API_KEY` 是否有效，並確保主機可連網。
- 文字顯示亂碼？請確保終端與檔案使用 UTF-8（建議編輯器設定為 UTF-8）。
- 要更換稱呼/語氣？修改 `agent_enhanced.py` 中的 system prompt 內容。

## 開發與測試
- 建議先跑 `test_features.py` 確認本地記憶功能無虞。
- 若要調整資料位置，可在 `agent_enhanced.py` 修改 `MEMORY_PATH`。

---

