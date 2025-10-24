"""
Conversation Manager - Manages conversation history and favorability
Phase 2: Complete conversation flow with persistence
"""
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import json

from backend.database import User, Character, Message, FavorabilityTracking, UserPreference
from backend.api_client import SenseChatClient


class ConversationManager:
    """Manages conversations, history, and favorability tracking"""

    # Favorability level thresholds
    LEVEL_1_THRESHOLD = 0  # 0-19 messages
    LEVEL_2_THRESHOLD = 20  # 20-49 messages
    LEVEL_3_THRESHOLD = 50  # 50+ messages

    MAX_HISTORY_MESSAGES = 100  # Maximum messages to send to API

    def __init__(self, db: Session, api_client: SenseChatClient):
        """
        Initialize conversation manager

        Args:
            db: Database session
            api_client: SenseChat API client
        """
        self.db = db
        self.api_client = api_client

    def get_or_create_user(self, username: str) -> User:
        """
        Get existing user or create new one

        Args:
            username: User's name

        Returns:
            User object
        """
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            user = User(username=username)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user

    def save_character(
        self,
        user_id: int,
        character_data: Dict
    ) -> Character:
        """
        Save generated character to database

        Args:
            user_id: User ID
            character_data: Character settings dictionary

        Returns:
            Character object
        """
        character = Character(
            user_id=user_id,
            name=character_data["name"],
            gender=character_data["gender"],
            identity=character_data.get("identity"),
            nickname=character_data.get("nickname"),
            detail_setting=character_data.get("detail_setting"),
            other_setting=json.loads(character_data["other_setting"]) if isinstance(
                character_data.get("other_setting"), str
            ) else character_data.get("other_setting")
        )

        self.db.add(character)
        self.db.commit()
        self.db.refresh(character)

        # Initialize favorability tracking
        favorability = FavorabilityTracking(
            user_id=user_id,
            character_id=character.character_id,
            current_level=1,
            message_count=0
        )
        self.db.add(favorability)
        self.db.commit()

        return character

    def get_character(self, character_id: int) -> Optional[Character]:
        """Get character by ID"""
        return self.db.query(Character).filter(
            Character.character_id == character_id
        ).first()

    def get_user_characters(self, user_id: int) -> List[Character]:
        """Get all characters for a user"""
        return self.db.query(Character).filter(
            Character.user_id == user_id
        ).order_by(Character.created_at.desc()).all()

    def save_message(
        self,
        user_id: int,
        character_id: int,
        speaker_name: str,
        content: str,
        favorability_level: int
    ) -> Message:
        """
        Save a message to database

        Args:
            user_id: User ID
            character_id: Character ID
            speaker_name: Who said the message
            content: Message content
            favorability_level: Current favorability level

        Returns:
            Message object
        """
        message = Message(
            user_id=user_id,
            character_id=character_id,
            speaker_name=speaker_name,
            message_content=content,
            favorability_level=favorability_level
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_conversation_history(
        self,
        character_id: int,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        Get conversation history for a character

        Args:
            character_id: Character ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of Message objects in chronological order
        """
        query = self.db.query(Message).filter(
            Message.character_id == character_id
        ).order_by(Message.timestamp.asc())

        if limit:
            # Get the most recent N messages
            total = query.count()
            if total > limit:
                query = query.offset(total - limit)

        return query.all()

    def get_favorability(self, character_id: int) -> Optional[FavorabilityTracking]:
        """Get favorability tracking for a character"""
        return self.db.query(FavorabilityTracking).filter(
            FavorabilityTracking.character_id == character_id
        ).first()

    def update_favorability(self, character_id: int) -> Tuple[int, bool]:
        """
        Update favorability level based on message count

        Args:
            character_id: Character ID

        Returns:
            Tuple of (current_level, level_increased)
        """
        favorability = self.get_favorability(character_id)
        if not favorability:
            return 1, False

        # Increment message count
        favorability.message_count += 1
        old_level = favorability.current_level

        # Determine new level based on message count
        if favorability.message_count >= self.LEVEL_3_THRESHOLD:
            favorability.current_level = 3
        elif favorability.message_count >= self.LEVEL_2_THRESHOLD:
            favorability.current_level = 2
        else:
            favorability.current_level = 1

        level_increased = favorability.current_level > old_level
        self.db.commit()

        return favorability.current_level, level_increased

    def format_messages_for_api(self, messages: List[Message]) -> List[Dict]:
        """
        Format database messages for API request

        Args:
            messages: List of Message objects

        Returns:
            List of message dictionaries for API
        """
        return [
            {
                "name": msg.speaker_name,
                "content": msg.message_content
            }
            for msg in messages
        ]

    def send_message(
        self,
        user_id: int,
        character_id: int,
        user_message: str
    ) -> Dict:
        """
        Send a message and get character's response

        Args:
            user_id: User ID
            character_id: Character ID
            user_message: User's message

        Returns:
            Dictionary with character's response and metadata
        """
        # Get character and user
        character = self.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")

        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Get favorability
        favorability = self.get_favorability(character_id)
        current_level = favorability.current_level if favorability else 1

        # Save user's message
        self.save_message(
            user_id=user_id,
            character_id=character_id,
            speaker_name=user.username,
            content=user_message,
            favorability_level=current_level
        )

        # Get conversation history (limited)
        history = self.get_conversation_history(
            character_id=character_id,
            limit=self.MAX_HISTORY_MESSAGES
        )

        # Format messages for API
        api_messages = self.format_messages_for_api(history)

        # Prepare character settings with current favorability
        character_settings_list = [
            {
                "name": user.username,
                "gender": "男",  # Default, can be customized
                "detail_setting": "用戶"
            },
            {
                "name": character.name,
                "gender": character.gender,
                "identity": character.identity,
                "nickname": character.nickname,
                "detail_setting": character.detail_setting,
                "other_setting": json.dumps(character.other_setting, ensure_ascii=False) if isinstance(
                    character.other_setting, dict
                ) else character.other_setting,
                "feeling_toward": [
                    {
                        "name": user.username,
                        "level": current_level
                    }
                ]
            }
        ]

        # Role setting
        role_setting = {
            "user_name": user.username,
            "primary_bot_name": character.name
        }

        # Call API
        try:
            response = self.api_client.create_character_chat(
                character_settings=character_settings_list,
                role_setting=role_setting,
                messages=api_messages,
                max_new_tokens=1024
            )

            character_reply = response["data"]["reply"]

            # Save character's response
            self.save_message(
                user_id=user_id,
                character_id=character_id,
                speaker_name=character.name,
                content=character_reply,
                favorability_level=current_level
            )

            # Update favorability
            new_level, level_increased = self.update_favorability(character_id)

            # Get updated favorability for accurate message count
            updated_favorability = self.get_favorability(character_id)
            current_message_count = updated_favorability.message_count if updated_favorability else 0

            # Check for milestone achievements (50, 100, 200, 500 messages)
            milestone_reached = False
            milestone_number = 0
            milestones = [50, 100, 200, 500, 1000]
            for milestone in milestones:
                if current_message_count == milestone:
                    milestone_reached = True
                    milestone_number = milestone
                    break

            # Check for conversation anniversary (days since first message)
            anniversary_reached = False
            anniversary_days = 0
            first_message = self.db.query(Message).filter(
                Message.character_id == character_id
            ).order_by(Message.timestamp.asc()).first()

            if first_message:
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc)
                first_date = first_message.timestamp
                if first_date.tzinfo is None:
                    from datetime import timezone
                    first_date = first_date.replace(tzinfo=timezone.utc)
                days_since_first = (now - first_date).days

                # Check for anniversary milestones (7, 30, 100, 365 days)
                anniversary_milestones = [7, 30, 100, 365]
                for anniversary in anniversary_milestones:
                    if days_since_first == anniversary:
                        anniversary_reached = True
                        anniversary_days = anniversary
                        break

            return {
                "success": True,
                "reply": character_reply,
                "favorability_level": new_level,
                "level_increased": level_increased,
                "message_count": current_message_count,
                "milestone_reached": milestone_reached,
                "milestone_number": milestone_number,
                "anniversary_reached": anniversary_reached,
                "anniversary_days": anniversary_days,
                "usage": response["data"].get("usage", {})
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in send_message: {error_details}")
            return {
                "success": False,
                "error": str(e),
                "error_details": error_details
            }

    def delete_character(self, character_id: int) -> bool:
        """Delete a character and all associated data"""
        character = self.get_character(character_id)
        if not character:
            return False

        self.db.delete(character)
        self.db.commit()
        return True

    def get_conversation_summary(self, character_id: int) -> Dict:
        """Get conversation statistics and summary"""
        favorability = self.get_favorability(character_id)
        message_count = self.db.query(Message).filter(
            Message.character_id == character_id
        ).count()

        return {
            "character_id": character_id,
            "message_count": message_count,
            "favorability_level": favorability.current_level if favorability else 1,
            "last_updated": favorability.last_updated if favorability else None
        }
