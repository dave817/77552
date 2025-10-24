"""
Test script for Phase 2 - Persistent Conversations
Tests database persistence, conversation history, and favorability tracking
"""
import sys
import os
import io

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal, init_db, User, Character, Message, FavorabilityTracking
from backend.conversation_manager import ConversationManager
from backend.character_generator import CharacterGenerator
from backend.api_client import SenseChatClient
from backend.models import UserProfile, DreamType, CustomMemory


def test_database_setup():
    """Test database initialization"""
    print("=" * 60)
    print("測試資料庫初始化...")
    print("=" * 60)

    try:
        init_db()
        print("✅ 資料庫初始化成功！")
        return True
    except Exception as e:
        print(f"❌ 資料庫初始化失敗: {e}")
        return False


def test_character_creation_and_persistence():
    """Test creating and saving a character"""
    print("\n" + "=" * 60)
    print("測試角色創建和保存...")
    print("=" * 60)

    db = SessionLocal()

    try:
        # Initialize services
        api_client = SenseChatClient()
        character_generator = CharacterGenerator(api_client=api_client)
        conv_manager = ConversationManager(db, api_client)

        # Create user profile
        user_profile = UserProfile(
            user_name="測試用戶",
            dream_type=DreamType(
                personality_traits=["溫柔", "體貼"],
                talking_style="溫柔體貼",
                interests=["音樂", "閱讀"],
                age_range="22-25",
                occupation="學生"
            ),
            custom_memory=CustomMemory(
                likes={"food": ["咖啡"]},
                dislikes={},
                habits={},
                personal_background={}
            )
        )

        # Get or create user
        user = conv_manager.get_or_create_user(user_profile.user_name)
        print(f"✅ 用戶已創建: {user.username} (ID: {user.user_id})")

        # Generate character
        print("正在生成角色...")
        character_settings = character_generator.generate_character(user_profile)

        # Save character
        character = conv_manager.save_character(user.user_id, character_settings)
        print(f"✅ 角色已保存: {character.name} (ID: {character.character_id})")
        print(f"   暱稱: {character.nickname}")
        print(f"   身份: {character.identity}")

        # Check favorability tracking
        favorability = conv_manager.get_favorability(character.character_id)
        print(f"✅ 好感度追蹤已初始化: Level {favorability.current_level}, 訊息數: {favorability.message_count}")

        db.close()
        return character.character_id

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        db.close()
        return None


def test_conversation_flow(character_id):
    """Test conversation with history and favorability"""
    print("\n" + "=" * 60)
    print("測試對話流程和好感度系統...")
    print("=" * 60)

    if not character_id:
        print("❌ 沒有角色 ID，跳過測試")
        return

    db = SessionLocal()

    try:
        # Initialize services
        api_client = SenseChatClient()
        conv_manager = ConversationManager(db, api_client)

        # Get character and user
        character = conv_manager.get_character(character_id)
        user = db.query(User).filter(User.username == "測試用戶").first()

        print(f"開始與 {character.name} 對話...")
        print(f"初始好感度: Level {conv_manager.get_favorability(character_id).current_level}")

        # Test messages
        test_messages = [
            "你好！很高興認識你",
            "你喜歡做什麼呢？",
            "今天天氣真好",
            "我們來聊聊音樂吧",
            "你最喜歡什麼類型的音樂？"
        ]

        for i, msg in enumerate(test_messages, 1):
            print(f"\n--- 訊息 {i}/{len(test_messages)} ---")
            print(f"👤 {user.username}: {msg}")

            # Send message
            result = conv_manager.send_message(
                user_id=user.user_id,
                character_id=character_id,
                user_message=msg
            )

            if result["success"]:
                print(f"💕 {character.name}: {result['reply']}")
                print(f"   好感度: Level {result['favorability_level']} | 訊息數: {result['message_count']}")

                if result['level_increased']:
                    print(f"   🎉 好感度提升！")
            else:
                print(f"❌ 發送失敗: {result.get('error')}")

        # Check final favorability
        final_favorability = conv_manager.get_favorability(character_id)
        print(f"\n✅ 對話完成！")
        print(f"   最終好感度: Level {final_favorability.current_level}")
        print(f"   總訊息數: {final_favorability.message_count}")

        # Get conversation history
        history = conv_manager.get_conversation_history(character_id)
        print(f"   歷史記錄: {len(history)} 條訊息已保存")

        db.close()
        return True

    except Exception as e:
        print(f"❌ 對話測試失敗: {e}")
        import traceback
        traceback.print_exc()
        db.close()
        return False


def test_favorability_progression():
    """Test favorability level progression"""
    print("\n" + "=" * 60)
    print("測試好感度升級系統...")
    print("=" * 60)

    db = SessionLocal()

    try:
        api_client = SenseChatClient()
        character_generator = CharacterGenerator(api_client=api_client)
        conv_manager = ConversationManager(db, api_client)

        # Create new user and character
        user_profile = UserProfile(
            user_name="好感度測試",
            dream_type=DreamType(
                personality_traits=["活潑"],
                talking_style="活潑開朗",
                interests=["運動"],
                age_range="20-25",
                occupation="學生"
            ),
            custom_memory=CustomMemory()
        )

        user = conv_manager.get_or_create_user(user_profile.user_name)
        character_settings = character_generator.generate_character(user_profile)
        character = conv_manager.save_character(user.user_id, character_settings)

        print(f"測試角色: {character.name}")
        print(f"\n好感度閾值:")
        print(f"  Level 1: 0-{ConversationManager.LEVEL_2_THRESHOLD-1} 訊息")
        print(f"  Level 2: {ConversationManager.LEVEL_2_THRESHOLD}-{ConversationManager.LEVEL_3_THRESHOLD-1} 訊息")
        print(f"  Level 3: {ConversationManager.LEVEL_3_THRESHOLD}+ 訊息")

        # Simulate conversations to reach each level
        levels_reached = []

        for i in range(55):  # Enough to reach Level 3
            result = conv_manager.send_message(
                user_id=user.user_id,
                character_id=character.character_id,
                user_message=f"測試訊息 {i+1}"
            )

            if result.get('level_increased'):
                levels_reached.append(result['favorability_level'])
                print(f"🎉 訊息 {i+1}: 好感度提升至 Level {result['favorability_level']}！")

        final_fav = conv_manager.get_favorability(character.character_id)
        print(f"\n✅ 好感度測試完成！")
        print(f"   最終好感度: Level {final_fav.current_level}")
        print(f"   總訊息數: {final_fav.message_count}")
        print(f"   升級次數: {len(levels_reached)}")

        db.close()
        return True

    except Exception as e:
        print(f"❌ 好感度測試失敗: {e}")
        import traceback
        traceback.print_exc()
        db.close()
        return False


def main():
    """Run all Phase 2 tests"""
    print("\n🚀 開始測試 Dating Chatbot - Phase 2\n")

    # Test 1: Database setup
    if not test_database_setup():
        print("\n⚠️  資料庫初始化失敗，停止測試")
        return

    # Test 2: Character creation and persistence
    character_id = test_character_creation_and_persistence()

    if not character_id:
        print("\n⚠️  角色創建失敗")
        return

    # Test 3: Conversation flow
    if not test_conversation_flow(character_id):
        print("\n⚠️  對話測試失敗")
        return

    # Test 4: Favorability progression
    if not test_favorability_progression():
        print("\n⚠️  好感度測試失敗")
        return

    print("\n" + "=" * 60)
    print("✅ Phase 2 所有測試完成！")
    print("=" * 60)
    print("\n新功能:")
    print("  ✅ 資料庫持久化")
    print("  ✅ 對話歷史保存")
    print("  ✅ 好感度追蹤系統")
    print("  ✅ 多輪對話管理")
    print("\nAPI 端點:")
    print("  POST /api/v2/create-character - 創建並保存角色")
    print("  POST /api/v2/send-message - 發送訊息（帶歷史）")
    print("  GET  /api/v2/conversation-history/{character_id} - 獲取歷史")
    print("  GET  /api/v2/user-characters/{user_id} - 獲取用戶角色")
    print("  GET  /api/v2/favorability/{character_id} - 獲取好感度")
    print("\n伺服器: http://localhost:8000")
    print("API 文檔: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    main()
