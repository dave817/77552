"""
Knowledge Base Management for SenseChat API
Handles creation and management of knowledge bases for characters
"""
import json
import io
from typing import Dict, List, Optional
from backend.api_client import SenseChatClient


class KnowledgeBaseManager:
    """Manages knowledge base operations for SenseChat API"""

    def __init__(self, api_client: SenseChatClient):
        """
        Initialize knowledge base manager

        Args:
            api_client: SenseChat API client instance
        """
        self.api_client = api_client

    def create_character_knowledge(
        self,
        character_name: str,
        user_preferences: Dict,
        background_info: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a knowledge base for a character

        Args:
            character_name: Character's name
            user_preferences: User's custom memory and preferences
            background_info: Additional background information

        Returns:
            Knowledge base ID if successful, None otherwise
        """
        try:
            # Build knowledge base content
            knowledge_content = self._build_knowledge_content(
                character_name,
                user_preferences,
                background_info
            )

            # Create file with knowledge content
            file_id = self._create_knowledge_file(knowledge_content)
            if not file_id:
                return None

            # Create knowledge base with the file
            knowledge_base_id = self._create_knowledge_base(
                file_id=file_id,
                description=f"知識庫 - {character_name}"
            )

            return knowledge_base_id

        except Exception as e:
            print(f"Error creating knowledge base: {e}")
            import traceback
            traceback.print_exc()
            return None

    def update_character_knowledge(
        self,
        knowledge_base_id: str,
        character_name: str,
        user_preferences: Dict,
        background_info: Optional[str] = None
    ) -> bool:
        """
        Update an existing knowledge base

        Args:
            knowledge_base_id: Existing knowledge base ID
            character_name: Character's name
            user_preferences: Updated user preferences
            background_info: Updated background information

        Returns:
            True if successful, False otherwise
        """
        try:
            # Build updated knowledge content
            knowledge_content = self._build_knowledge_content(
                character_name,
                user_preferences,
                background_info
            )

            # Create new file
            file_id = self._create_knowledge_file(knowledge_content)
            if not file_id:
                return False

            # Update knowledge base
            return self._update_knowledge_base(
                knowledge_base_id=knowledge_base_id,
                file_id=file_id
            )

        except Exception as e:
            print(f"Error updating knowledge base: {e}")
            return False

    def _build_knowledge_content(
        self,
        character_name: str,
        user_preferences: Dict,
        background_info: Optional[str] = None
    ) -> Dict:
        """
        Build knowledge base content from user preferences

        Args:
            character_name: Character's name
            user_preferences: User's custom memory
            background_info: Background information

        Returns:
            Knowledge base content dictionary
        """
        qa_lst = []
        text_lst = []

        # Extract user preferences if available
        if user_preferences:
            # Add Q&A pairs for user preferences
            if "likes" in user_preferences and user_preferences["likes"]:
                likes_text = ", ".join([
                    f"{k}: {', '.join(v)}"
                    for k, v in user_preferences["likes"].items()
                    if v
                ])
                if likes_text:
                    qa_lst.append({
                        "std_q": "用戶喜歡什麼？",
                        "simi_qs": ["我喜歡什麼", "我的喜好", "我喜歡的東西"],
                        "answer": f"你喜歡: {likes_text}"
                    })
                    text_lst.append(f"用戶喜好: {likes_text}")

            if "dislikes" in user_preferences and user_preferences["dislikes"]:
                dislikes_text = ", ".join([
                    f"{k}: {', '.join(v)}"
                    for k, v in user_preferences["dislikes"].items()
                    if v
                ])
                if dislikes_text:
                    qa_lst.append({
                        "std_q": "用戶不喜歡什麼？",
                        "simi_qs": ["我不喜歡什麼", "我討厭什麼"],
                        "answer": f"你不太喜歡: {dislikes_text}"
                    })
                    text_lst.append(f"用戶不喜歡: {dislikes_text}")

            if "habits" in user_preferences and user_preferences["habits"]:
                for habit_type, habit_value in user_preferences["habits"].items():
                    if habit_value:
                        text_lst.append(f"用戶習慣 - {habit_type}: {habit_value}")

            if "personal_background" in user_preferences and user_preferences["personal_background"]:
                for bg_type, bg_value in user_preferences["personal_background"].items():
                    if bg_value:
                        text_lst.append(f"用戶背景 - {bg_type}: {bg_value}")

                        # Add Q&A for occupation
                        if bg_type == "occupation":
                            qa_lst.append({
                                "std_q": "用戶是做什麼工作的？",
                                "simi_qs": ["我的職業", "我是做什麼的", "我的工作"],
                                "answer": f"你的職業是: {bg_value}"
                            })

        # Add background information
        if background_info:
            text_lst.append(f"{character_name}的背景: {background_info}")

        # If no content, add a default entry
        if not qa_lst and not text_lst:
            text_lst.append(f"這是{character_name}的知識庫")

        return {
            "qa_lst": qa_lst,
            "text_lst": text_lst
        }

    def _create_knowledge_file(self, content: Dict) -> Optional[str]:
        """
        Create and upload a knowledge base file

        Args:
            content: Knowledge base content

        Returns:
            File ID if successful, None otherwise
        """
        try:
            # Convert content to JSON string
            json_content = json.dumps(content, ensure_ascii=False, indent=2)

            # Create file object
            file_obj = io.StringIO(json_content)

            # Upload file using API client
            response = self.api_client.create_knowledge_file(
                file=file_obj,
                description="Character knowledge base"
            )

            if response.get("success") and "file_id" in response:
                return response["file_id"]

            return None

        except Exception as e:
            print(f"Error creating knowledge file: {e}")
            return None

    def _create_knowledge_base(
        self,
        file_id: str,
        description: str
    ) -> Optional[str]:
        """
        Create a knowledge base with uploaded file

        Args:
            file_id: Uploaded file ID
            description: Knowledge base description

        Returns:
            Knowledge base ID if successful, None otherwise
        """
        try:
            response = self.api_client.create_knowledge_base(
                file_ids=[file_id],
                description=description
            )

            if response.get("success") and "knowledge_base_id" in response:
                return response["knowledge_base_id"]

            return None

        except Exception as e:
            print(f"Error creating knowledge base: {e}")
            return None

    def _update_knowledge_base(
        self,
        knowledge_base_id: str,
        file_id: str
    ) -> bool:
        """
        Update an existing knowledge base

        Args:
            knowledge_base_id: Knowledge base ID
            file_id: New file ID

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.api_client.update_knowledge_base(
                knowledge_base_id=knowledge_base_id,
                file_ids=[file_id]
            )

            return response.get("success", False)

        except Exception as e:
            print(f"Error updating knowledge base: {e}")
            return False
