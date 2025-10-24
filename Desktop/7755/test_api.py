"""
Test script for SenseChat-Character-Pro API
Tests connection and character generation
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

from backend.api_client import SenseChatClient
from backend.character_generator import CharacterGenerator
from backend.models import UserProfile, DreamType, CustomMemory


def test_api_connection():
    """Test basic API connection"""
    print("=" * 60)
    print("測試 API 連接...")
    print("=" * 60)

    client = SenseChatClient()

    try:
        is_connected = client.test_connection()
        if is_connected:
            print("✅ API 連接成功！")
            return True
        else:
            print("❌ API 連接失敗")
            return False
    except Exception as e:
        print(f"❌ 連接測試錯誤: {e}")
        return False


def test_character_generation():
    """Test character generation"""
    print("\n" + "=" * 60)
    print("測試角色生成...")
    print("=" * 60)

    # Create sample user profile
    user_profile = UserProfile(
        user_name="小明",
        dream_type=DreamType(
            personality_traits=["溫柔", "體貼", "善良"],
            physical_description="甜美可愛",
            age_range="22-25",
            interests=["音樂", "閱讀", "旅行"],
            occupation="學生",
            talking_style="溫柔體貼"
        ),
        custom_memory=CustomMemory(
            likes={"food": ["咖啡", "甜點"], "activities": ["看電影", "散步"]},
            dislikes={"general": ["吵鬧的環境", "熬夜"]},
            habits={"daily_routine": "早睡早起", "communication_style": "喜歡深度交流"},
            personal_background={"occupation": "軟體工程師", "hobbies": "寫程式"}
        )
    )

    # Initialize with API client for AI-generated backgrounds
    client = SenseChatClient()
    generator = CharacterGenerator(api_client=client)

    try:
        # Generate character with AI-powered background story
        print("正在生成AI背景故事...")
        character = generator.generate_character(user_profile)

        print(f"\n角色名稱: {character['name']}")
        print(f"暱稱: {character['nickname']}")
        print(f"性別: {character['gender']}")
        print(f"身份: {character['identity']}")
        print(f"\n詳細設定:\n{character['detail_setting']}")

        # Parse and show background story
        import json
        other_setting = json.loads(character['other_setting'])
        print(f"\n✨ AI生成的背景故事:\n{other_setting.get('background_story', 'N/A')}")

        print(f"\n其他設定:\n{character['other_setting'][:200]}...")
        print(f"\n好感度設定: {character['feeling_toward']}")

        # Generate initial message
        initial_msg = generator.create_initial_message(character['name'], user_profile)
        print(f"\n初次見面訊息:\n{initial_msg}")

        print("\n✅ 角色生成成功！")
        return character, user_profile

    except Exception as e:
        print(f"❌ 角色生成錯誤: {e}")
        return None, None


def test_chat_with_character(character, user_profile):
    """Test actual chat with generated character"""
    print("\n" + "=" * 60)
    print("測試與角色對話...")
    print("=" * 60)

    if not character:
        print("❌ 沒有角色可以測試")
        return

    client = SenseChatClient()

    # Create user character settings
    user_character = {
        "name": user_profile.user_name,
        "gender": "男",
        "detail_setting": "普通用戶"
    }

    # Prepare character settings for API (needs both user and AI character)
    character_settings = [user_character, character]

    # Role settings
    role_setting = {
        "user_name": user_profile.user_name,
        "primary_bot_name": character["name"]
    }

    # Test messages
    test_messages = [
        "你好！很高興認識你",
        "你喜歡做什麼呢？",
        "我今天有點累"
    ]

    conversation_history = []

    for user_msg in test_messages:
        print(f"\n👤 {user_profile.user_name}: {user_msg}")

        # Add user message to history
        conversation_history.append({
            "name": user_profile.user_name,
            "content": user_msg
        })

        try:
            # Call API
            response = client.create_character_chat(
                character_settings=character_settings,
                role_setting=role_setting,
                messages=conversation_history,
                max_new_tokens=1024
            )

            # Get reply
            reply = response["data"]["reply"]
            print(f"💕 {character['name']}: {reply}")

            # Add character response to history
            conversation_history.append({
                "name": character["name"],
                "content": reply
            })

            # Show token usage
            usage = response["data"]["usage"]
            print(f"   (Token 使用: {usage['total_tokens']} total)")

        except Exception as e:
            print(f"❌ 對話錯誤: {e}")
            break

    print("\n✅ 對話測試完成！")


def main():
    """Run all tests"""
    print("\n🚀 開始測試 Dating Chatbot - Phase 1\n")

    # Test 1: API Connection
    if not test_api_connection():
        print("\n⚠️  API 連接失敗，請檢查憑證設定")
        return

    # Test 2: Character Generation
    character, user_profile = test_character_generation()

    if not character:
        print("\n⚠️  角色生成失敗")
        return

    # Test 3: Chat with Character
    test_chat_with_character(character, user_profile)

    print("\n" + "=" * 60)
    print("✅ 所有測試完成！")
    print("=" * 60)
    print("\n接下來可以啟動 Web 應用:")
    print("  python -m uvicorn backend.main:app --reload")
    print("\n然後訪問: http://localhost:8000/ui")
    print("=" * 60)


if __name__ == "__main__":
    main()
