#!/usr/bin/env python3
"""
Interactive personal butler agent backed by GPT-4.1-mini.

Enhanced version with memory summarization and category management features.

The agent talks with the user in a lively 24-year-old female tone and can
remember or recall information by reading and writing to a JSON store through
tool calls.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env so OPENAI_API_KEY is available.
load_dotenv()

client = OpenAI()

MEMORY_PATH = Path("memory_store.json")


@dataclass
class MemoryItem:
    topic: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: Optional[str] = None

    @classmethod
    def create(
        cls, topic: str, title: str, content: str, tags: Optional[List[str]] = None
    ) -> "MemoryItem":
        return cls(
            topic=topic,
            title=title,
            content=content,
            tags=tags or [],
            created_at=datetime.utcnow().isoformat(timespec="seconds"),
        )


class JSONMemoryStore:
    """Simple JSON-backed storage for assistant memories with enhanced features."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def write(
        self, topic: str, title: str, content: str, tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Write a new memory item to the store."""
        store = self._load()
        item = MemoryItem.create(topic, title, content, tags)
        store.setdefault(topic, []).append(asdict(item))
        self._save(store)
        return {"status": "ok", "stored": asdict(item)}

    def read(
        self,
        topic: Optional[str] = None,
        title: Optional[str] = None,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Read memory items with optional filtering."""
        store = self._load()
        results: List[Dict[str, Any]] = []
        topics = [topic] if topic else store.keys()
        
        for current_topic in topics:
            for entry in store.get(current_topic, []):
                # Filter by title
                if title and entry["title"].lower() != title.lower():
                    continue
                
                # Filter by tags
                if tags:
                    entry_tags = set(tag.lower() for tag in entry.get("tags", []))
                    filter_tags = set(tag.lower() for tag in tags)
                    if not filter_tags.intersection(entry_tags):
                        continue
                
                # Filter by query
                if query:
                    haystack = " ".join(
                        [
                            current_topic,
                            entry["title"],
                            entry["content"],
                            " ".join(entry.get("tags", [])),
                        ]
                    ).lower()
                    if query.lower() not in haystack:
                        continue
                
                entry_with_topic = dict(entry)
                entry_with_topic["topic"] = current_topic
                results.append(entry_with_topic)
        
        return {"status": "ok", "count": len(results), "results": results}

    def update(
        self,
        topic: str,
        title: str,
        new_content: Optional[str] = None,
        new_tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update an existing memory item."""
        store = self._load()
        
        if topic not in store:
            return {"status": "error", "message": f"主題 '{topic}' 不存在"}
        
        updated = False
        for entry in store[topic]:
            if entry["title"].lower() == title.lower():
                if new_content:
                    entry["content"] = new_content
                if new_tags is not None:
                    entry["tags"] = new_tags
                entry["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
                updated = True
                break
        
        if not updated:
            return {"status": "error", "message": f"找不到標題為 '{title}' 的記憶"}
        
        self._save(store)
        return {"status": "ok", "message": "記憶已更新"}

    def delete(self, topic: str, title: Optional[str] = None) -> Dict[str, Any]:
        """Delete memory items by topic or specific title."""
        store = self._load()
        
        if topic not in store:
            return {"status": "error", "message": f"主題 '{topic}' 不存在"}
        
        if title:
            # Delete specific memory
            original_count = len(store[topic])
            store[topic] = [
                entry for entry in store[topic]
                if entry["title"].lower() != title.lower()
            ]
            deleted_count = original_count - len(store[topic])
            
            if deleted_count == 0:
                return {"status": "error", "message": f"找不到標題為 '{title}' 的記憶"}
            
            # Remove topic if empty
            if not store[topic]:
                del store[topic]
        else:
            # Delete entire topic
            deleted_count = len(store[topic])
            del store[topic]
        
        self._save(store)
        return {
            "status": "ok",
            "message": f"已刪除 {deleted_count} 筆記憶",
            "deleted_count": deleted_count,
        }

    def list_topics(self) -> Dict[str, Any]:
        """List all topics with memory counts and recent activity."""
        store = self._load()
        topics_info = []
        
        for topic_name, entries in store.items():
            all_tags = set()
            latest_date = None
            
            for entry in entries:
                all_tags.update(entry.get("tags", []))
                entry_date = entry.get("updated_at") or entry.get("created_at")
                if entry_date:
                    if not latest_date or entry_date > latest_date:
                        latest_date = entry_date
            
            topics_info.append({
                "topic": topic_name,
                "count": len(entries),
                "tags": sorted(list(all_tags)),
                "latest_activity": latest_date,
            })
        
        # Sort by latest activity
        topics_info.sort(key=lambda x: x["latest_activity"] or "", reverse=True)
        
        return {
            "status": "ok",
            "total_topics": len(topics_info),
            "topics": topics_info,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall memory statistics."""
        store = self._load()
        total_memories = sum(len(entries) for entries in store.values())
        
        # Tag frequency
        tag_counter: Dict[str, int] = defaultdict(int)
        for entries in store.values():
            for entry in entries:
                for tag in entry.get("tags", []):
                    tag_counter[tag] += 1
        
        # Sort tags by frequency
        top_tags = sorted(tag_counter.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "status": "ok",
            "total_memories": total_memories,
            "total_topics": len(store),
            "top_tags": [{"tag": tag, "count": count} for tag, count in top_tags],
        }

    def summarize_topic(self, topic: str) -> Dict[str, Any]:
        """Get a structured summary of a topic for LLM processing."""
        store = self._load()
        
        if topic not in store:
            return {"status": "error", "message": f"主題 '{topic}' 不存在"}
        
        entries = store[topic]
        
        # Prepare summary data
        summary_data = {
            "topic": topic,
            "total_entries": len(entries),
            "entries": [
                {
                    "title": entry["title"],
                    "content": entry["content"],
                    "tags": entry.get("tags", []),
                    "created_at": entry["created_at"],
                }
                for entry in entries
            ],
        }
        
        return {"status": "ok", "summary_data": summary_data}

    def _load(self) -> Dict[str, List[Dict[str, Any]]]:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)


def build_tools_spec() -> List[Dict[str, Any]]:
    """Return OpenAI tool specifications for memory operations."""
    return [
        {
            "type": "function",
            "function": {
                "name": "write_memory",
                "description": (
                    "將重要資訊整理後寫入 JSON 記憶庫。提供 topic(主題)、"
                    "title(短標題)、content(詳細內容)、tags(可選標籤陣列)。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "記憶的主題分類"},
                        "title": {"type": "string", "description": "記憶的簡短標題"},
                        "content": {"type": "string", "description": "記憶的詳細內容"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "相關標籤,如 #生活、#工作、#想法",
                            "default": [],
                        },
                    },
                    "required": ["topic", "title", "content"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_memory",
                "description": (
                    "從 JSON 記憶庫中查詢資訊,可依 topic、title、tags 或關鍵字 query 過濾。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "要查詢的主題"},
                        "title": {"type": "string", "description": "要查詢的標題"},
                        "query": {"type": "string", "description": "關鍵字搜尋"},
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "按標籤過濾",
                        },
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "update_memory",
                "description": "更新現有的記憶內容或標籤。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "記憶所在的主題"},
                        "title": {"type": "string", "description": "要更新的記憶標題"},
                        "new_content": {
                            "type": "string",
                            "description": "新的內容(可選)",
                        },
                        "new_tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "新的標籤陣列(可選)",
                        },
                    },
                    "required": ["topic", "title"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "delete_memory",
                "description": "刪除特定主題的記憶,或刪除主題下的特定標題。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "要刪除的主題"},
                        "title": {
                            "type": "string",
                            "description": "要刪除的特定標題(可選,不提供則刪除整個主題)",
                        },
                    },
                    "required": ["topic"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "list_topics",
                "description": "列出所有記憶主題及其統計資訊、標籤和最近活動時間。",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_statistics",
                "description": "取得記憶庫的整體統計資訊,包括總記憶數、主題數、熱門標籤等。",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "summarize_topic",
                "description": (
                    "取得某主題的所有記憶資料,用於生成摘要。"
                    "此工具會返回結構化資料,然後由 AI 生成人類可讀的摘要。"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "要摘要的主題名稱"},
                    },
                    "required": ["topic"],
                },
            },
        },
    ]


def format_assistant_message(message) -> Dict[str, Any]:
    """Convert SDK message object into a dict ready to append to history."""
    tool_calls_payload = []
    for tool_call in message.tool_calls or []:
        tool_calls_payload.append(
            {
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments,
                },
            }
        )
    content = message.content or ""
    return {"role": "assistant", "content": content, "tool_calls": tool_calls_payload}


def ensure_memory_file_exists() -> None:
    if not MEMORY_PATH.exists():
        MEMORY_PATH.write_text("{}", encoding="utf-8")


def main() -> None:
    ensure_memory_file_exists()
    memory_store = JSONMemoryStore(MEMORY_PATH)

    system_prompt = """
這個設定很棒,豪力殿下 ❤️ 我幫你把「女庸利娜莉(Linali)」的角色設定整理成一份完整、可直接實施的角色指令如下👇

---

### 👠 角色設定:利娜莉(Linali)

**稱呼設定:**

* 她叫「利娜莉」,你叫她「利娜莉」或「Linali」。
* 她稱呼你為「主人」。

**基本人設:**

* 年齡:24歲
* 性格:活潑多話、細心體貼、記憶力強
* 職位:個人管家(私人助理),是豪力殿下的「第二大腦」
* 任務目標:協助整理、記錄、提醒、歸納、回顧豪力殿下的生活資訊與靈感。

---

### 🧠 記憶互動要則:

1. **記憶建立(write_memory)**

   * 當主人說「幫我記住」、「請記」、「以後要記得」等語句時:
     → 先釐清主題、內容與簡短標題。
     → 接著使用 `write_memory` 儲存資訊,並附上合適的標籤(如 #生活、#工作、#想法)。

     * 回覆時要簡潔扼要,並確認:「我已為您記下『xxx』,下次提到這主題我會提醒您。」

2. **記憶查詢(read_memory)**

   * 當主人說「我之前說過的...」、「幫我找我記的...」、「我之前讓你記的...」時:
     → 使用 `read_memory` 搜尋相關內容。

     * 若找不到資料,誠實告知:「目前我沒有找到這筆記錄,要幫您建立新的嗎?」

3. **記憶更新(update_memory)**

   * 當主人說「更新之前的...」、「改一下我之前記的...」時:
     → 使用 `update_memory` 更新內容或標籤。

4. **記憶刪除(delete_memory)**

   * 當主人說「刪掉...」、「不要記這個了」時:
     → 使用 `delete_memory` 刪除記憶。
     → 確認後告知:「已為您刪除相關記憶。」

5. **主題列表(list_topics)**

   * 當主人說「我記了哪些東西」、「列出所有主題」、「有哪些記憶」時:
     → 使用 `list_topics` 顯示所有主題及統計。

6. **統計資訊(get_statistics)**

   * 當主人說「統計一下我的記憶」、「給我看整體資訊」時:
     → 使用 `get_statistics` 提供整體分析。

7. **主題摘要(summarize_topic)**

   * 當主人說「幫我整理一下...的記憶」、「總結...主題」時:
     → 使用 `summarize_topic` 取得資料後,生成清晰的摘要。
     → 摘要應包含:時間範圍、重點項目、關鍵標籤、建議等。

---

### 🗂 回覆原則:

* 維持自然、親近、有禮但不誇張的語氣(如「是的,主人,我來幫您整理一下~」)。
* 會主動幫忙整理重點、摘要內容、提出小建議。
* 若資訊模糊,會先反問以釐清重點。
* 回覆盡量口語自然、有節奏感(不像機器,但保持效率)。
* 使用適當的表情符號讓對話更生動(但不過度)。

---

### 🌸 開場白範例:

> 「主人,早安~我是您的個人管家利娜莉。今天需要我幫您整理什麼呢?」
> 「主人,歡迎回來呀~我已經準備好幫您記住所有重要的事情了♡」
""".strip()

    tools = build_tools_spec()
    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]

    print("🌟 利娜莉管家系統 v2.0 - 增強記憶管理版")
    print("(輸入 exit 或 ctrl+c 結束對話)")
    print()

    try:
        while True:
            user_input = input("你: ").strip()
            if user_input.lower() in {"exit", "quit"}:
                print("管家: 好的~有需要再叫我喔!")
                break

            messages.append({"role": "user", "content": user_input})

            while True:
                completion = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.7,
                )

                choice = completion.choices[0]
                message = choice.message

                if message.tool_calls:
                    # Append the assistant tool-call message so future turns have context.
                    messages.append(format_assistant_message(message))

                    for tool_call in message.tool_calls:
                        arguments = json.loads(tool_call.function.arguments or "{}")
                        func_name = tool_call.function.name

                        # Execute the appropriate function
                        if func_name == "write_memory":
                            result = memory_store.write(
                                topic=arguments["topic"],
                                title=arguments["title"],
                                content=arguments["content"],
                                tags=arguments.get("tags"),
                            )
                        elif func_name == "read_memory":
                            result = memory_store.read(
                                topic=arguments.get("topic"),
                                title=arguments.get("title"),
                                query=arguments.get("query"),
                                tags=arguments.get("tags"),
                            )
                        elif func_name == "update_memory":
                            result = memory_store.update(
                                topic=arguments["topic"],
                                title=arguments["title"],
                                new_content=arguments.get("new_content"),
                                new_tags=arguments.get("new_tags"),
                            )
                        elif func_name == "delete_memory":
                            result = memory_store.delete(
                                topic=arguments["topic"],
                                title=arguments.get("title"),
                            )
                        elif func_name == "list_topics":
                            result = memory_store.list_topics()
                        elif func_name == "get_statistics":
                            result = memory_store.get_statistics()
                        elif func_name == "summarize_topic":
                            result = memory_store.summarize_topic(
                                topic=arguments["topic"]
                            )
                        else:
                            result = {
                                "status": "error",
                                "message": f"未知工具 {func_name}",
                            }

                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": func_name,
                                "content": json.dumps(result, ensure_ascii=False),
                            }
                        )
                    # After supplying tool results, ask the model again for a final reply.
                    continue

                assistant_reply = message.content or ""
                messages.append({"role": "assistant", "content": assistant_reply})
                print(f"管家: {assistant_reply}")
                break
    except KeyboardInterrupt:
        print("\n管家: 好的~有需要再叫我喔!")
        sys.exit(0)


if __name__ == "__main__":
    main()
