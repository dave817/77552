"""
Character Generator - Generates AI character profiles based on user preferences
"""
import json
from typing import Dict, List, Optional
from backend.models import UserProfile, DreamType, CustomMemory, PersonalityType


class CharacterGenerator:
    """Generates character settings based on user's dream type and custom memory"""

    def __init__(self, api_client=None):
        """
        Initialize character generator

        Args:
            api_client: Optional SenseChatClient for AI-generated backgrounds
        """
        self.api_client = api_client

    # Character name mappings based on personality
    NAME_MAPPINGS = {
        PersonalityType.GENTLE: ["小雨", "婉婷", "雨柔", "思婷", "靜雯"],
        PersonalityType.CHEERFUL: ["欣怡", "小晴", "樂瑤", "晴心", "悅欣"],
        PersonalityType.INTELLECTUAL: ["雅文", "靜儀", "書涵", "詩涵", "慧雯"],
        PersonalityType.CUTE: ["小萌", "甜心", "可兒", "糖糖", "小柔"]
    }

    # Nickname mappings
    NICKNAME_MAPPINGS = {
        PersonalityType.GENTLE: ["小雨", "柔柔", "雨雨"],
        PersonalityType.CHEERFUL: ["晴晴", "小陽光", "開心果"],
        PersonalityType.INTELLECTUAL: ["雅雅", "小書蟲", "文文"],
        PersonalityType.CUTE: ["小可愛", "甜甜", "萌萌"]
    }


    def _determine_personality_type(self, dream_type: DreamType) -> PersonalityType:
        """
        Determine the personality type based on talking style and traits

        Args:
            dream_type: User's dream partner type

        Returns:
            PersonalityType enum
        """
        style_lower = dream_type.talking_style.lower()

        if "溫柔" in style_lower or "體貼" in style_lower or "細心" in style_lower:
            return PersonalityType.GENTLE
        elif "活潑" in style_lower or "開朗" in style_lower or "幽默" in style_lower:
            return PersonalityType.CHEERFUL
        elif "知性" in style_lower or "優雅" in style_lower or "成熟" in style_lower:
            return PersonalityType.INTELLECTUAL
        elif "可愛" in style_lower or "天真" in style_lower or "俏皮" in style_lower:
            return PersonalityType.CUTE
        else:
            # Default to gentle
            return PersonalityType.GENTLE

    def _generate_name(self, personality_type: PersonalityType, gender: str) -> str:
        """Generate character name based on personality type"""
        import random
        names = self.NAME_MAPPINGS.get(personality_type, self.NAME_MAPPINGS[PersonalityType.GENTLE])
        return random.choice(names)

    def _generate_nickname(self, personality_type: PersonalityType) -> str:
        """Generate character nickname based on personality type"""
        import random
        nicknames = self.NICKNAME_MAPPINGS.get(personality_type, self.NICKNAME_MAPPINGS[PersonalityType.GENTLE])
        return random.choice(nicknames)

    def _generate_identity(self, dream_type: DreamType) -> str:
        """
        Generate character identity (max 200 chars)

        Args:
            dream_type: User's dream partner type

        Returns:
            Character identity string
        """
        parts = []

        # Add age
        if dream_type.age_range:
            parts.append(f"{dream_type.age_range}歲")

        # Add occupation
        if dream_type.occupation:
            parts.append(dream_type.occupation)

        # Add brief description
        if dream_type.physical_description:
            parts.append(dream_type.physical_description)

        # Add main interest
        if dream_type.interests:
            parts.append(f"喜歡{dream_type.interests[0]}")

        identity = "，".join(parts)

        # Ensure within 200 char limit
        if len(identity) > 200:
            identity = identity[:197] + "..."

        return identity

    def _generate_detail_setting(
        self,
        dream_type: DreamType,
        personality_type: PersonalityType,
        custom_memory: CustomMemory
    ) -> str:
        """
        Generate detailed character settings (max 500 chars)

        Args:
            dream_type: User's dream partner type
            personality_type: Determined personality type
            custom_memory: User's custom memory

        Returns:
            Detail setting string
        """
        details = []

        # Add personality description
        personality_desc = {
            PersonalityType.GENTLE: "性格溫柔體貼，說話輕聲細語，總是關心對方的感受。喜歡用溫暖的話語鼓勵人，細心觀察對方的需要。",
            PersonalityType.CHEERFUL: "性格活潑開朗，充滿活力和熱情。說話時常帶著笑容，喜歡用輕鬆幽默的方式交流。",
            PersonalityType.INTELLECTUAL: "性格知性優雅，談吐有內涵。喜歡深度交流，對文化藝術有獨特見解，說話條理清晰。",
            PersonalityType.CUTE: "性格可愛天真，充滿好奇心。說話俏皮可愛，常常用天真的角度看世界，讓人感到溫暖。"
        }
        details.append(personality_desc[personality_type])

        # Add talking style
        details.append(f"說話風格：{dream_type.talking_style}。")

        # Add interests
        if dream_type.interests:
            interests_str = "、".join(dream_type.interests[:3])
            details.append(f"興趣愛好包括{interests_str}。")

        # Add reference to user's preferences if available
        if custom_memory.likes:
            details.append("會主動關心對方的喜好，並嘗試參與。")

        # Add emphasis on Traditional Chinese and expressive communication
        details.append("【必須使用繁體中文】對話時會加入生動的動作和表情描述(用括號標註)，讓互動更真實有溫度。")

        detail_setting = "".join(details)

        # Ensure within 500 char limit
        if len(detail_setting) > 500:
            detail_setting = detail_setting[:497] + "..."

        return detail_setting

    def _generate_other_setting(
        self,
        character_name: str,
        dream_type: DreamType,
        personality_type: PersonalityType,
        custom_memory: CustomMemory
    ) -> str:
        """
        Generate other settings as JSON string (max 2000 chars)

        Args:
            character_name: Generated character name
            dream_type: User's dream partner type
            personality_type: Determined personality type
            custom_memory: User's custom memory

        Returns:
            JSON string of other settings
        """
        # Generate AI-powered background story
        background_story = self._generate_background_story(
            character_name,
            dream_type,
            personality_type,
            custom_memory
        )

        other_settings = {
            "interests": dream_type.interests,
            "background_story": background_story,
            "values": self._extract_values(dream_type),
            "communication_style": dream_type.talking_style,
            "relationship_goals": "建立深厚的情感連結，互相理解和支持",
            "user_preferences_awareness": {
                "likes": custom_memory.likes,
                "dislikes": custom_memory.dislikes,
                "habits": custom_memory.habits
            },
            "response_guidelines": [
                "【重要】必須使用繁體中文回應，絕對不可使用簡體中文",
                "在回應中加入生動的動作和表情描述，使用括號標註，例如：(噗嗤一笑，眼里闪烁着狡黠的光芒)、(靠近你的耳边，轻声细语)、(先是一愣，随即露出俏皮的笑容)、(轻轻捏了捏你的脸颊)、(眼神中流露出一丝受伤，但很快又恢复了平静)、(轻轻握住你的手)",
                "讓回應更有人情味和生命力，表現出真實的情感和反應",
                "自然地提及用戶的喜好和習慣",
                "保持人設一致性",
                "根據好感度調整親密程度和互動方式",
                "記住之前的對話內容，展現連貫性",
                "在對話中自然融入自己的背景故事"
            ]
        }

        json_str = json.dumps(other_settings, ensure_ascii=False)

        # Ensure within 2000 char limit
        if len(json_str) > 2000:
            # Reduce background story if too long
            other_settings["background_story"] = other_settings["background_story"][:100] + "..."
            json_str = json.dumps(other_settings, ensure_ascii=False)

        return json_str

    def _generate_background_story(
        self,
        character_name: str,
        dream_type: DreamType,
        personality_type: PersonalityType,
        custom_memory: CustomMemory
    ) -> str:
        """
        Generate an interesting background story for the character using AI

        Args:
            character_name: Generated character name
            dream_type: User's dream partner type
            personality_type: Determined personality type
            custom_memory: User's custom memory

        Returns:
            AI-generated background story
        """
        if not self.api_client:
            # Fallback to simple story if no API client
            return self._generate_simple_background_story(dream_type)

        try:
            # Create a prompt for generating background story
            personality_map = {
                PersonalityType.GENTLE: "溫柔體貼",
                PersonalityType.CHEERFUL: "活潑開朗",
                PersonalityType.INTELLECTUAL: "知性優雅",
                PersonalityType.CUTE: "可愛天真"
            }

            interests_str = "、".join(dream_type.interests) if dream_type.interests else "閱讀和音樂"
            personality_str = personality_map[personality_type]

            prompt = f"""請為一位名叫{character_name}的角色創作一個簡短但有趣的背景故事（150字以內，繁體中文）。

角色設定：
- 性格：{personality_str}
- 年齡：{dream_type.age_range or '20多歲'}
- 職業：{dream_type.occupation or '年輕專業人士'}
- 興趣：{interests_str}
- 說話風格：{dream_type.talking_style}

要求：
1. 故事要有趣且有個性，不要太平淡
2. 包含一些生活細節和小故事
3. 展現角色的性格特點
4. 讓人感覺這是一個真實、立體的人
5. 以第一人稱（我）的方式敘述
6. 不要超過150字

請直接輸出背景故事，不需要其他說明。"""

            # Use API to generate story
            story_character = [
                {
                    "name": "系統",
                    "gender": "中性",
                    "detail_setting": "專業的故事創作助手"
                },
                {
                    "name": "創作者",
                    "gender": "中性",
                    "detail_setting": "擅長創作有趣的角色背景故事"
                }
            ]

            role_setting = {
                "user_name": "系統",
                "primary_bot_name": "創作者"
            }

            messages = [{
                "name": "系統",
                "content": prompt
            }]

            response = self.api_client.create_character_chat(
                character_settings=story_character,
                role_setting=role_setting,
                messages=messages,
                max_new_tokens=300
            )

            story = response["data"]["reply"].strip()

            # Ensure within reasonable length
            if len(story) > 200:
                story = story[:197] + "..."

            return story

        except Exception as e:
            print(f"Failed to generate AI background story: {e}")
            # Fallback to simple story
            return self._generate_simple_background_story(dream_type)

    def _generate_simple_background_story(self, dream_type: DreamType) -> str:
        """Generate a simple fallback background story"""
        story_parts = []

        if dream_type.occupation:
            story_parts.append(f"目前從事{dream_type.occupation}的工作")

        if dream_type.interests:
            story_parts.append(f"平時喜歡{dream_type.interests[0]}")

        story_parts.append("希望能遇到一個真心相待的人")

        return "，".join(story_parts) + "。"

    def _extract_values(self, dream_type: DreamType) -> List[str]:
        """Extract values based on personality traits"""
        values = ["真誠", "善良", "互相尊重"]

        if "溫柔" in dream_type.talking_style:
            values.append("關懷")
        if "活潑" in dream_type.talking_style:
            values.append("樂觀")
        if "知性" in dream_type.talking_style:
            values.append("智慧")

        return values

    def _determine_gender(self, dream_type: DreamType) -> str:
        """Determine gender from dream type (can be extended)"""
        # For now, default to female, but this can be customized
        # based on user input or preferences
        return "女"

    def generate_character(self, user_profile: UserProfile) -> Dict:
        """
        Generate complete character settings from user profile

        Args:
            user_profile: User's complete profile

        Returns:
            Dictionary with character settings ready for API
        """
        personality_type = self._determine_personality_type(user_profile.dream_type)
        gender = self._determine_gender(user_profile.dream_type)
        name = self._generate_name(personality_type, gender)
        nickname = self._generate_nickname(personality_type)

        character_settings = {
            "name": name,
            "gender": gender,
            "identity": self._generate_identity(user_profile.dream_type),
            "nickname": nickname,
            "detail_setting": self._generate_detail_setting(
                user_profile.dream_type,
                personality_type,
                user_profile.custom_memory
            ),
            "other_setting": self._generate_other_setting(
                name,  # Pass character name
                user_profile.dream_type,
                personality_type,  # Pass personality type
                user_profile.custom_memory
            ),
            "feeling_toward": [
                {
                    "name": user_profile.user_name,
                    "level": 1  # Start at level 1
                }
            ]
        }

        return character_settings

    def create_initial_message(
        self,
        character_name: str,
        user_profile: UserProfile
    ) -> str:
        """
        Create the character's first message to the user

        Args:
            character_name: Generated character name
            user_profile: User's profile

        Returns:
            Initial greeting message
        """
        greetings = []

        # Basic greeting
        greetings.append(f"嗨！我是{character_name}。")

        # Reference user's interests if available
        if user_profile.dream_type.interests:
            interest = user_profile.dream_type.interests[0]
            greetings.append(f"聽說你喜歡{interest}？我也很喜歡呢！")

        # Reference user's likes if available
        if user_profile.custom_memory.likes:
            for category, items in user_profile.custom_memory.likes.items():
                if items:
                    greetings.append(f"我注意到你喜歡{items[0]}，真巧！")
                    break

        # Warm opening question
        greetings.append("很高興認識你，今天過得怎麼樣？")

        return "".join(greetings)
