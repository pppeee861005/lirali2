#!/usr/bin/env python3
"""
測試增強版記憶管理功能的範例腳本
"""
from pathlib import Path
import json
from agent_enhanced import JSONMemoryStore

def demo_enhanced_features():
    """展示新功能的使用範例"""
    
    # 使用測試記憶檔案
    test_memory_path = Path("test_memory.json")
    store = JSONMemoryStore(test_memory_path)
    
    print("=" * 60)
    print("🎯 利娜莉管家系統 v2.0 - 功能演示")
    print("=" * 60)
    print()
    
    # 1. 建立一些測試記憶
    print("📝 步驟 1: 建立測試記憶...")
    print("-" * 60)
    
    store.write(
        topic="工作",
        title="專案 A 重要事項",
        content="deadline 是 11/15,需要準備客戶簡報,聯絡人是李經理",
        tags=["#專案", "#deadline", "#客戶"]
    )
    
    store.write(
        topic="工作",
        title="週會時間",
        content="每週一上午 10:00 團隊會議,記得準備進度報告",
        tags=["#會議", "#固定行程"]
    )
    
    store.write(
        topic="生活",
        title="咖啡喜好",
        content="喜歡拿鐵,不加糖,少冰",
        tags=["#飲食", "#咖啡", "#偏好"]
    )
    
    store.write(
        topic="生活",
        title="運動計畫",
        content="每週三、六晚上 7:00 去健身房,主要練有氧和重訓",
        tags=["#運動", "#健康", "#固定行程"]
    )
    
    store.write(
        topic="想法",
        title="部落格靈感",
        content="寫一篇關於 AI 工具如何提升生產力的文章",
        tags=["#寫作", "#靈感", "#AI"]
    )
    
    print("✅ 已建立 5 筆測試記憶")
    print()
    
    # 2. 列出所有主題
    print("📋 步驟 2: 列出所有主題")
    print("-" * 60)
    
    topics_result = store.list_topics()
    print(f"總主題數: {topics_result['total_topics']}\n")
    
    for topic_info in topics_result['topics']:
        print(f"📁 {topic_info['topic']}")
        print(f"   記憶數: {topic_info['count']} 筆")
        print(f"   標籤: {', '.join(topic_info['tags'])}")
        print(f"   最近活動: {topic_info['latest_activity']}")
        print()
    
    # 3. 查看統計資訊
    print("📊 步驟 3: 統計資訊")
    print("-" * 60)
    
    stats = store.get_statistics()
    print(f"總記憶數: {stats['total_memories']} 筆")
    print(f"總主題數: {stats['total_topics']} 個\n")
    
    print("🏷 熱門標籤:")
    for i, tag_info in enumerate(stats['top_tags'][:5], 1):
        print(f"   {i}. {tag_info['tag']} ({tag_info['count']}次)")
    print()
    
    # 4. 按標籤查詢
    print("🔍 步驟 4: 按標籤查詢 (查詢 #固定行程)")
    print("-" * 60)
    
    tagged_result = store.read(tags=["#固定行程"])
    print(f"找到 {tagged_result['count']} 筆記憶:\n")
    
    for entry in tagged_result['results']:
        print(f"• {entry['title']} ({entry['topic']})")
        print(f"  {entry['content'][:50]}...")
        print()
    
    # 5. 更新記憶
    print("✏️ 步驟 5: 更新記憶 (修改咖啡喜好)")
    print("-" * 60)
    
    update_result = store.update(
        topic="生活",
        title="咖啡喜好",
        new_content="改喝美式咖啡,不加糖,去冰",
        new_tags=["#飲食", "#咖啡", "#偏好", "#美式"]
    )
    print(f"更新狀態: {update_result['status']}")
    print(f"訊息: {update_result['message']}")
    print()
    
    # 6. 讀取更新後的記憶
    print("👀 步驟 6: 驗證更新結果")
    print("-" * 60)
    
    read_result = store.read(topic="生活", title="咖啡喜好")
    if read_result['results']:
        entry = read_result['results'][0]
        print(f"標題: {entry['title']}")
        print(f"內容: {entry['content']}")
        print(f"標籤: {', '.join(entry['tags'])}")
        print(f"更新時間: {entry.get('updated_at', '未更新')}")
    print()
    
    # 7. 主題摘要
    print("📄 步驟 7: 生成主題摘要 (工作主題)")
    print("-" * 60)
    
    summary_result = store.summarize_topic("工作")
    if summary_result['status'] == 'ok':
        summary_data = summary_result['summary_data']
        print(f"主題: {summary_data['topic']}")
        print(f"記憶數: {summary_data['total_entries']} 筆\n")
        
        print("內容列表:")
        for i, entry in enumerate(summary_data['entries'], 1):
            print(f"{i}. {entry['title']}")
            print(f"   內容: {entry['content'][:50]}...")
            print(f"   標籤: {', '.join(entry['tags'])}")
            print()
    
    # 8. 刪除記憶
    print("🗑️ 步驟 8: 刪除記憶 (刪除部落格靈感)")
    print("-" * 60)
    
    delete_result = store.delete(topic="想法", title="部落格靈感")
    print(f"刪除狀態: {delete_result['status']}")
    print(f"訊息: {delete_result['message']}")
    print()
    
    # 9. 最終統計
    print("📊 步驟 9: 最終統計")
    print("-" * 60)
    
    final_stats = store.get_statistics()
    print(f"剩餘記憶數: {final_stats['total_memories']} 筆")
    print(f"主題數: {final_stats['total_topics']} 個")
    print()
    
    print("=" * 60)
    print("✨ 演示完成!")
    print("=" * 60)
    print()
    print(f"測試記憶已儲存至: {test_memory_path.absolute()}")
    print("您可以查看該檔案了解資料結構")
    print()
    
    # 可選:清理測試檔案
    cleanup = input("是否刪除測試記憶檔案? (y/n): ").strip().lower()
    if cleanup == 'y':
        test_memory_path.unlink()
        print("✅ 測試檔案已刪除")
    else:
        print("💾 測試檔案已保留")


if __name__ == "__main__":
    try:
        demo_enhanced_features()
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
