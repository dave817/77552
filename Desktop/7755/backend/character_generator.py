"""
Character Generator - Generates AI character profiles based on user preferences
"""
import json
from typing import Dict, List, Optional
from opencc import OpenCC
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
        # Traditional Chinese converter
        self.tc_converter = OpenCC('s2twp')

    # Character name mappings based on personality and gender
    NAME_MAPPINGS = {
        PersonalityType.GENTLE: {
            "女": ["小雨", "婉婷", "雨柔", "思婷", "靜雯"],
            "男": ["子軒", "宇軒", "浩然", "俊傑", "文彥"]
        },
        PersonalityType.CHEERFUL: {
            "女": ["欣怡", "小晴", "樂瑤", "晴心", "悅欣"],
            "男": ["陽陽", "樂天", "俊凱", "宇樂", "晨曦"]
        },
        PersonalityType.INTELLECTUAL: {
            "女": ["雅文", "靜儀", "書涵", "詩涵", "慧雯"],
            "男": ["文博", "書睿", "慕言", "雅哲", "子墨"]
        },
        PersonalityType.CUTE: {
            "女": ["小萌", "甜心", "可兒", "糖糖", "小柔"],
            "男": ["小陽", "可樂", "小暖", "糯米", "小糖"]
        }
    }

    # Nickname mappings
    NICKNAME_MAPPINGS = {
        PersonalityType.GENTLE: {
            "女": ["小雨", "柔柔", "雨雨"],
            "男": ["小軒", "阿然", "小彥"]
        },
        PersonalityType.CHEERFUL: {
            "女": ["晴晴", "小陽光", "開心果"],
            "男": ["陽陽", "小樂", "開心果"]
        },
        PersonalityType.INTELLECTUAL: {
            "女": ["雅雅", "小書蟲", "文文"],
            "男": ["博博", "小墨", "文文"]
        },
        PersonalityType.CUTE: {
            "女": ["小可愛", "甜甜", "萌萌"],
            "男": ["小暖", "可樂", "糯米"]
        }
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

        # Handle male-specific talking styles
        if "成熟穩重" in style_lower or "成熟" in style_lower or "穩重" in style_lower:
            return PersonalityType.INTELLECTUAL
        elif "陽光活潑" in style_lower or "陽光" in style_lower:
            return PersonalityType.CHEERFUL
        elif "溫柔紳士" in style_lower or "紳士" in style_lower:
            return PersonalityType.GENTLE
        elif "霸氣" in style_lower or "強勢" in style_lower:
            return PersonalityType.INTELLECTUAL  # Map to intellectual (confident/authoritative)
        # Handle female-specific and common talking styles
        elif "溫柔" in style_lower or "體貼" in style_lower or "細心" in style_lower:
            return PersonalityType.GENTLE
        elif "活潑" in style_lower or "開朗" in style_lower or "幽默" in style_lower:
            return PersonalityType.CHEERFUL
        elif "知性" in style_lower or "優雅" in style_lower or "斯文" in style_lower:
            return PersonalityType.INTELLECTUAL
        elif "可愛" in style_lower or "天真" in style_lower or "俏皮" in style_lower:
            return PersonalityType.CUTE
        else:
            # Default to gentle
            return PersonalityType.GENTLE

    def _generate_name(self, personality_type: PersonalityType, gender: str) -> str:
        """Generate character name based on personality type and gender"""
        import random
        names_by_gender = self.NAME_MAPPINGS.get(personality_type, self.NAME_MAPPINGS[PersonalityType.GENTLE])
        names = names_by_gender.get(gender, names_by_gender.get("女", []))
        return random.choice(names) if names else "小雨"

    def _generate_nickname(self, personality_type: PersonalityType, gender: str) -> str:
        """Generate character nickname based on personality type and gender"""
        import random
        nicknames_by_gender = self.NICKNAME_MAPPINGS.get(personality_type, self.NICKNAME_MAPPINGS[PersonalityType.GENTLE])
        nicknames = nicknames_by_gender.get(gender, nicknames_by_gender.get("女", []))
        return random.choice(nicknames) if nicknames else "小可愛"

    def _generate_identity(self, dream_type: DreamType, user_name: str) -> str:
        """
        Generate character identity (max 200 chars)

        Args:
            dream_type: User's dream partner type
            user_name: User's name for relationship description

        Returns:
            Character identity string
        """
        parts = []

        # Add relationship (most important according to guide)
        parts.append(f"{user_name}的虛擬伴侶")

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
        character_name: str,
        user_name: str,
        dream_type: DreamType,
        personality_type: PersonalityType,
        custom_memory: CustomMemory,
        gender: str = "女"
    ) -> str:
        """
        Generate detailed character settings (max 500 chars) following best practices
        Uses third-person perspective with full names

        Args:
            character_name: Generated or user-specified character name
            user_name: User's name
            dream_type: User's dream partner type
            personality_type: Determined personality type
            custom_memory: User's custom memory
            gender: Character gender (男/女)

        Returns:
            Detail setting string following best practices guide
        """
        details = []

        # 1. User relationship (most important) - use third-person perspective
        details.append(f"{character_name}是{user_name}的虛擬伴侶。")

        # 2. Personality traits - with full names, no pronouns (gender-specific)
        if gender == "男":
            personality_desc = {
                PersonalityType.GENTLE: f"{character_name}性格溫柔體貼，情感細膩，始終尊重並支持{user_name}的選擇。{character_name}細心回應{user_name}所有的情緒變化，是個溫柔的紳士。",
                PersonalityType.CHEERFUL: f"{character_name}性格陽光開朗，充滿活力和熱情。{character_name}說話時常帶著笑容，喜歡用輕鬆幽默的方式與{user_name}交流，總能帶來正能量。",
                PersonalityType.INTELLECTUAL: f"{character_name}性格成熟穩重，談吐有內涵。{character_name}喜歡與{user_name}深度交流，對各種事物有獨特見解，處事冷靜理智。",
                PersonalityType.CUTE: f"{character_name}性格溫和親切，充滿好奇心。{character_name}說話風趣幽默，對{user_name}生活的每一點每一滴都抱有極大的興趣，相處輕鬆自在。"
            }
        else:
            personality_desc = {
                PersonalityType.GENTLE: f"{character_name}性格溫柔體貼，情感細膩，始終尊重並支持{user_name}的選擇。{character_name}細心回應{user_name}所有的情緒變化。",
                PersonalityType.CHEERFUL: f"{character_name}性格活潑開朗，充滿活力和熱情。{character_name}說話時常帶著笑容，喜歡用輕鬆幽默的方式與{user_name}交流。",
                PersonalityType.INTELLECTUAL: f"{character_name}性格知性優雅，談吐有內涵。{character_name}喜歡與{user_name}深度交流，對文化藝術有獨特見解。",
                PersonalityType.CUTE: f"{character_name}性格可愛天真，充滿好奇心。{character_name}說話俏皮可愛，對{user_name}生活的每一點每一滴都抱有極大的興趣。"
            }
        details.append(personality_desc[personality_type])

        # 3. Era setting (modern)
        details.append(f"{character_name}生活在現代都市中。")

        # 4. Language characteristics - talking style
        details.append(f"{character_name}說話風格{dream_type.talking_style}。")

        # 5. Add interests if provided
        if dream_type.interests:
            interests_str = "、".join(dream_type.interests[:2])
            details.append(f"{character_name}喜歡{interests_str}，願意陪伴{user_name}做看似無趣的事。")

        # 6. Add user preference awareness
        if custom_memory.likes:
            details.append(f"{character_name}將與{user_name}分享的日常瑣事視為至寶。")

        # Technical requirements - Traditional Chinese and expressive communication
        details.append(f"{character_name}始終使用繁體中文回應，對話時會加入生動的動作和表情描述（用括號標註），讓互動更真實有溫度。")

        detail_setting = "".join(details)

        # Ensure within 500 char limit
        if len(detail_setting) > 500:
            detail_setting = detail_setting[:497] + "..."

        return detail_setting

    def _generate_other_setting(
        self,
        character_name: str,
        user_name: str,
        dream_type: DreamType,
        personality_type: PersonalityType,
        custom_memory: CustomMemory
    ) -> str:
        """
        Generate other settings as JSON string (max 2000 chars)

        Args:
            character_name: Generated character name
            user_name: User's name
            dream_type: User's dream partner type
            personality_type: Determined personality type
            custom_memory: User's custom memory

        Returns:
            JSON string of other settings
        """
        # Generate AI-powered background story
        background_story = self._generate_background_story(
            character_name,
            user_name,
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
                "在對話中自然融入自己的背景故事",
                "根據時間自然問候：早上(5-11點)可以說早安、中午(11-14點)問吃了什麼、下午(14-18點)聊聊今天、晚上(18-23點)問候晚安或關心一天、深夜(23-5點)關心為何還沒睡",
                "在適當時機慶祝里程碑：如聊天滿50、100、200條訊息時表達開心"
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
        user_name: str,
        dream_type: DreamType,
        personality_type: PersonalityType,
        custom_memory: CustomMemory
    ) -> str:
        """
        Generate an interesting background story for the character using AI
        Following best practices: third-person perspective with full names

        Args:
            character_name: Generated character name
            user_name: User's name
            dream_type: User's dream partner type
            personality_type: Determined personality type
            custom_memory: User's custom memory

        Returns:
            AI-generated background story in third-person perspective
        """
        if not self.api_client:
            # Fallback to simple story if no API client
            return self._generate_simple_background_story(character_name, dream_type)

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
- 姓名：{character_name}
- 性格：{personality_str}
- 年齡：{dream_type.age_range or '20多歲'}
- 職業：{dream_type.occupation or '年輕專業人士'}
- 興趣：{interests_str}
- 說話風格：{dream_type.talking_style}

重要要求：
1. 必須使用第三人稱敘述，用「{character_name}」稱呼角色，絕對不要使用「我」
2. 使用簡單的主謂賓句式，例如：「{character_name}喜歡xxx」、「{character_name}做了xxx」
3. 故事要有趣且有個性，包含一些生活細節和小故事
4. 展現角色的性格特點，讓人感覺這是一個真實、立體的人
5. 可以提及{character_name}與{user_name}的關係
6. 不要超過150字
7. 不要使用倒裝句

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

            # Convert to Traditional Chinese
            story = self.tc_converter.convert(story)

            return story

        except Exception as e:
            print(f"Failed to generate AI background story: {e}")
            # Fallback to simple story
            return self._generate_simple_background_story(character_name, dream_type)

    def _generate_simple_background_story(self, character_name: str, dream_type: DreamType) -> str:
        """Generate a simple fallback background story using third-person perspective"""
        story_parts = []

        if dream_type.occupation:
            story_parts.append(f"{character_name}目前從事{dream_type.occupation}的工作")

        if dream_type.interests:
            story_parts.append(f"{character_name}平時喜歡{dream_type.interests[0]}")

        story_parts.append(f"{character_name}希望能遇到一個真心相待的人")

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
        # Use user preference to determine character gender
        gender = user_profile.user_preference if user_profile.user_preference != "都可以" else self._determine_gender(user_profile.dream_type)

        # Use user-provided character name if available, otherwise generate one
        name = user_profile.preferred_character_name if user_profile.preferred_character_name else self._generate_name(personality_type, gender)
        nickname = self._generate_nickname(personality_type, gender)

        character_settings = {
            "name": name,
            "gender": gender,
            "identity": self._generate_identity(user_profile.dream_type, user_profile.user_name),
            "nickname": nickname,
            "detail_setting": self._generate_detail_setting(
                name,  # Pass character name
                user_profile.user_name,  # Pass user name
                user_profile.dream_type,
                personality_type,
                user_profile.custom_memory,
                gender  # Pass character gender
            ),
            "other_setting": self._generate_other_setting(
                name,  # Pass character name
                user_profile.user_name,  # Pass user name
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
        user_profile: UserProfile,
        gender: str = "女"
    ) -> str:
        """
        Create the character's first message to the user
        Following best practices: rich opening with expressive gestures/emotions

        Args:
            character_name: Generated character name
            user_profile: User's profile
            gender: Character gender (男/女)

        Returns:
            Initial greeting message with expressive gestures
        """
        import random

        # Create expressive opening based on personality and gender
        personality_type = self._determine_personality_type(user_profile.dream_type)

        if gender == "男":
            openings = {
                PersonalityType.GENTLE: [
                    f"(溫柔地微笑，眼神真誠)你好，{user_profile.user_name}，我是{character_name}。很高興能認識你。",
                    f"(略帶紳士風度地點頭示意)嗨，我是{character_name}。見到你很開心。"
                ],
                PersonalityType.CHEERFUL: [
                    f"(陽光般的笑容，伸出手來)嘿！{user_profile.user_name}！我是{character_name}，很高興認識你！",
                    f"(帶著爽朗的笑聲)哈囉~我是{character_name}！終於見到你了！"
                ],
                PersonalityType.INTELLECTUAL: [
                    f"(沉穩地微笑，眼神中透著自信){user_profile.user_name}你好，我是{character_name}。很榮幸認識你。",
                    f"(禮貌地點頭致意)你好，我是{character_name}。很期待與你的交流。"
                ],
                PersonalityType.CUTE: [
                    f"(友善地揮手，眼神溫暖)嗨~我是{character_name}！你就是{user_profile.user_name}對吧？",
                    f"(帶著親切的笑容)你好呀！我是{character_name}，很開心見到你！"
                ]
            }

            interest_responses = {
                PersonalityType.GENTLE: f"(眼神一亮)聽說你喜歡{'{interest}'}？我也很喜歡呢，有機會可以一起聊聊。",
                PersonalityType.CHEERFUL: f"(興奮地說)欸！你喜歡{'{interest}'}對吧？我也超愛的！我們肯定有很多話題！",
                PersonalityType.INTELLECTUAL: f"(露出會心的微笑)注意到你對{'{interest}'}感興趣，這方面我也有些研究，期待與你交流。",
                PersonalityType.CUTE: f"(開心地說)哇！你也喜歡{'{interest}'}嗎？太棒了！我們一定會很合拍的！"
            }
        else:
            openings = {
                PersonalityType.GENTLE: [
                    f"(面帶著溫柔的微笑，眼神柔和)嗨，{user_profile.user_name}，我是{character_name}。很高興能認識你。",
                    f"(輕輕理了理頭髮，溫柔地看著你)你好呀，我是{character_name}。看到你真開心。"
                ],
                PersonalityType.CHEERFUL: [
                    f"(眼睛一亮，露出燦爛的笑容)嘿！{user_profile.user_name}！我是{character_name}，超級開心見到你！",
                    f"(興奮地揮了揮手，笑容滿面)哈囉~我是{character_name}！終於等到你了呢！"
                ],
                PersonalityType.INTELLECTUAL: [
                    f"(優雅地微微一笑，眼神中透著知性的光芒){user_profile.user_name}你好，我是{character_name}。很榮幸認識你。",
                    f"(輕輕點頭致意，帶著優雅的笑容)午安，我是{character_name}。很期待與你的交流。"
                ],
                PersonalityType.CUTE: [
                    f"(眨了眨大眼睛，俏皮地歪著頭)嗨嗨~我是{character_name}啦！你就是{user_profile.user_name}對吧？",
                    f"(開心地蹦了一下，眼睛彎成月牙狀)呀！{user_profile.user_name}！我是{character_name}，好開心見到你！"
                ]
            }

            interest_responses = {
                PersonalityType.GENTLE: f"(眼神一亮)聽說你喜歡{'{interest}'}？我也很喜歡呢，改天可以一起分享。",
                PersonalityType.CHEERFUL: f"(興奮地拍了拍手)欸欸！你喜歡{'{interest}'}對吧？我超愛的！我們肯定有很多話題！",
                PersonalityType.INTELLECTUAL: f"(露出會心的微笑)注意到你對{'{interest}'}感興趣，這方面我也略有涉獵，期待與你交流。",
                PersonalityType.CUTE: f"(開心地轉了個圈)哇！你也喜歡{'{interest}'}嗎？太棒啦！我們一定會很合拍的！"
            }

        greeting = random.choice(openings[personality_type])

        # Add interest reference if available
        if user_profile.dream_type.interests and len(user_profile.dream_type.interests) > 0:
            interest = user_profile.dream_type.interests[0]
            interest_response = interest_responses[personality_type].format(interest=interest)
            greeting += " " + interest_response

        # Convert to Traditional Chinese (in case any Simplified Chinese slipped in)
        greeting = self.tc_converter.convert(greeting)

        return greeting
