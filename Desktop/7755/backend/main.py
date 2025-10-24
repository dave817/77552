"""
FastAPI backend for Dating Chatbot
Phase 1: User Onboarding & Character Generation
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional

from backend.models import UserProfile, DreamType, CustomMemory
from backend.character_generator import CharacterGenerator
from backend.api_client import SenseChatClient
from backend.database import get_db, init_db
from backend.conversation_manager import ConversationManager
from sqlalchemy.orm import Session
from fastapi import Depends

app = FastAPI(title="Dating Chatbot API", version="1.0.0")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
api_client = SenseChatClient()
character_generator = CharacterGenerator(api_client=api_client)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    init_db()
    print("Database initialized successfully")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - shows welcome page"""
    return """
    <html>
        <head>
            <title>戀愛聊天機器人</title>
            <meta charset="UTF-8">
        </head>
        <body>
            <h1>歡迎使用戀愛聊天機器人</h1>
            <p>API 文檔: <a href="/docs">/docs</a></p>
            <p>前端界面: <a href="/ui">使用界面</a></p>
        </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "dating-chatbot"}


@app.post("/api/generate-character")
async def generate_character(user_profile: UserProfile) -> Dict:
    """
    Generate AI character based on user's dream type and custom memory

    Args:
        user_profile: User's complete profile

    Returns:
        Character settings and initial greeting
    """
    try:
        # Generate character settings
        character_settings = character_generator.generate_character(user_profile)

        # Generate initial message
        initial_message = character_generator.create_initial_message(
            character_settings["name"],
            user_profile
        )

        return {
            "success": True,
            "character": character_settings,
            "initial_message": initial_message,
            "message": "角色生成成功！"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"角色生成失敗: {str(e)}")


@app.post("/api/test-chat")
async def test_chat(
    character_settings: Dict,
    user_name: str,
    user_message: str
) -> Dict:
    """
    Test chat with generated character

    Args:
        character_settings: Generated character settings
        user_name: User's name
        user_message: User's message

    Returns:
        Character's response
    """
    try:
        # Prepare role setting
        role_setting = {
            "user_name": user_name,
            "primary_bot_name": character_settings["name"]
        }

        # Prepare messages
        messages = [
            {
                "name": user_name,
                "content": user_message
            }
        ]

        # Need both user and character in character_settings for API
        user_character = {
            "name": user_name,
            "gender": "男",  # Default, can be customized
            "detail_setting": "普通用戶"
        }

        api_character_settings = [user_character, character_settings]

        # Call API
        response = api_client.create_character_chat(
            character_settings=api_character_settings,
            role_setting=role_setting,
            messages=messages,
            max_new_tokens=1024
        )

        return {
            "success": True,
            "reply": response["data"]["reply"],
            "full_response": response["data"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天失敗: {str(e)}")


@app.get("/api/test-connection")
async def test_connection():
    """Test API connection to SenseChat"""
    try:
        is_connected = api_client.test_connection()
        return {
            "success": is_connected,
            "message": "API 連接成功" if is_connected else "API 連接失敗"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"連接測試失敗: {str(e)}")


# ==================== Phase 2: Persistent Conversation Endpoints ====================

@app.post("/api/v2/create-character")
async def create_character_v2(user_profile: UserProfile, db: Session = Depends(get_db)) -> Dict:
    """
    Phase 2: Create character and save to database

    Args:
        user_profile: User's complete profile
        db: Database session

    Returns:
        Character with character_id for persistent conversations
    """
    try:
        # Initialize conversation manager
        conv_manager = ConversationManager(db, api_client)

        # Get or create user
        user = conv_manager.get_or_create_user(user_profile.user_name)

        # Generate character
        character_settings = character_generator.generate_character(user_profile)

        # Save character to database
        character = conv_manager.save_character(user.user_id, character_settings)

        # Generate initial message
        initial_message = character_generator.create_initial_message(
            character_settings["name"],
            user_profile
        )

        # Save initial message
        conv_manager.save_message(
            user_id=user.user_id,
            character_id=character.character_id,
            speaker_name=character.name,
            content=initial_message,
            favorability_level=1
        )

        return {
            "success": True,
            "user_id": user.user_id,
            "character_id": character.character_id,
            "character": {
                "name": character.name,
                "nickname": character.nickname,
                "gender": character.gender,
                "identity": character.identity,
                "detail_setting": character.detail_setting,
                "other_setting": character.other_setting
            },
            "initial_message": initial_message,
            "favorability_level": 1,
            "message": "角色已創建並保存！"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"角色創建失敗: {str(e)}")


class SendMessageRequest(BaseModel):
    user_id: int
    character_id: int
    message: str


@app.post("/api/v2/send-message")
async def send_message_v2(
    request: SendMessageRequest,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Phase 2: Send message with conversation history and favorability tracking

    Args:
        request: Request body with user_id, character_id, and message
        db: Database session

    Returns:
        Character's response with favorability info
    """
    try:
        # Initialize conversation manager
        conv_manager = ConversationManager(db, api_client)

        # Send message and get response
        result = conv_manager.send_message(
            user_id=request.user_id,
            character_id=request.character_id,
            user_message=request.message
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"發送訊息失敗: {str(e)}")


@app.get("/api/v2/conversation-history/{character_id}")
async def get_conversation_history(
    character_id: int,
    limit: Optional[int] = 50,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get conversation history for a character

    Args:
        character_id: Character ID
        limit: Maximum number of messages to return
        db: Database session

    Returns:
        List of messages
    """
    try:
        conv_manager = ConversationManager(db, api_client)
        messages = conv_manager.get_conversation_history(character_id, limit)

        return {
            "success": True,
            "character_id": character_id,
            "message_count": len(messages),
            "messages": [
                {
                    "message_id": msg.message_id,
                    "speaker_name": msg.speaker_name,
                    "content": msg.message_content,
                    "timestamp": msg.timestamp.isoformat(),
                    "favorability_level": msg.favorability_level
                }
                for msg in messages
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取歷史失敗: {str(e)}")


@app.get("/api/v2/user-characters/{user_id}")
async def get_user_characters(user_id: int, db: Session = Depends(get_db)) -> Dict:
    """
    Get all characters for a user

    Args:
        user_id: User ID
        db: Database session

    Returns:
        List of characters
    """
    try:
        conv_manager = ConversationManager(db, api_client)
        characters = conv_manager.get_user_characters(user_id)

        return {
            "success": True,
            "user_id": user_id,
            "character_count": len(characters),
            "characters": [
                {
                    "character_id": char.character_id,
                    "name": char.name,
                    "nickname": char.nickname,
                    "created_at": char.created_at.isoformat(),
                    "favorability": conv_manager.get_favorability(char.character_id).current_level
                    if conv_manager.get_favorability(char.character_id) else 1
                }
                for char in characters
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取角色列表失敗: {str(e)}")


@app.get("/api/v2/favorability/{character_id}")
async def get_favorability_status(character_id: int, db: Session = Depends(get_db)) -> Dict:
    """
    Get favorability status for a character

    Args:
        character_id: Character ID
        db: Database session

    Returns:
        Favorability information
    """
    try:
        conv_manager = ConversationManager(db, api_client)
        favorability = conv_manager.get_favorability(character_id)

        if not favorability:
            raise HTTPException(status_code=404, detail="好感度記錄不存在")

        return {
            "success": True,
            "character_id": character_id,
            "current_level": favorability.current_level,
            "message_count": favorability.message_count,
            "last_updated": favorability.last_updated.isoformat(),
            "progress": {
                "level_1_threshold": ConversationManager.LEVEL_1_THRESHOLD,
                "level_2_threshold": ConversationManager.LEVEL_2_THRESHOLD,
                "level_3_threshold": ConversationManager.LEVEL_3_THRESHOLD
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"獲取好感度失敗: {str(e)}")


@app.get("/ui2")
async def ui2():
    """Phase 2 UI - User input and character generation with full persistence"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <title>戀愛聊天機器人 - 建立你的專屬伴侶 v2</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: "Microsoft YaHei", "微軟正黑體", sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }
            h1 {
                color: #667eea;
                text-align: center;
                margin-bottom: 10px;
                font-size: 32px;
            }
            .subtitle {
                text-align: center;
                color: #666;
                margin-bottom: 30px;
                font-size: 16px;
            }
            .step {
                display: none;
            }
            .step.active {
                display: block;
                animation: fadeIn 0.5s;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: bold;
            }
            input[type="text"],
            textarea,
            select {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus,
            textarea:focus,
            select:focus {
                outline: none;
                border-color: #667eea;
            }
            textarea {
                resize: vertical;
                min-height: 80px;
            }
            .checkbox-group {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .checkbox-item {
                flex: 0 0 calc(50% - 5px);
            }
            .checkbox-item input {
                margin-right: 5px;
            }
            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 16px;
                cursor: pointer;
                transition: transform 0.2s;
                margin-top: 10px;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }
            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            .button-group {
                display: flex;
                gap: 10px;
                justify-content: space-between;
                margin-top: 20px;
            }
            .character-result {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 12px;
                margin-top: 20px;
            }
            .character-name {
                font-size: 24px;
                color: #667eea;
                margin-bottom: 10px;
            }
            .character-detail {
                margin: 10px 0;
                line-height: 1.6;
            }
            .chat-test {
                margin-top: 20px;
                padding: 20px;
                background: #fff;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
            }
            .message {
                padding: 10px;
                margin: 10px 0;
                border-radius: 8px;
            }
            .message.user {
                background: #e3f2fd;
                text-align: right;
            }
            .message.character {
                background: #f3e5f5;
            }
            .loading {
                text-align: center;
                color: #667eea;
                font-size: 18px;
                padding: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>💕 戀愛聊天機器人 [Phase 2]</h1>
            <p class="subtitle">建立你的專屬AI伴侶 - 完整持久化版本</p>

            <!-- Step 1: Basic Info -->
            <div id="step1" class="step active">
                <h2>第一步：基本資料</h2>
                <div class="form-group">
                    <label>你的名字：</label>
                    <input type="text" id="userName" placeholder="請輸入你的名字">
                </div>
                <div class="button-group">
                    <div></div>
                    <button onclick="nextStep(2)">下一步</button>
                </div>
            </div>

            <!-- Step 2: Dream Type -->
            <div id="step2" class="step">
                <h2>第二步：描述你的理想伴侶</h2>

                <div class="form-group">
                    <label>說話風格：</label>
                    <select id="talkingStyle">
                        <option value="溫柔體貼">溫柔體貼</option>
                        <option value="活潑開朗">活潑開朗</option>
                        <option value="知性優雅">知性優雅</option>
                        <option value="可愛俏皮">可愛俏皮</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>性格特質（可多選）：</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" id="trait1" value="溫柔">
                            <label for="trait1" style="display:inline">溫柔</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="trait2" value="活潑">
                            <label for="trait2" style="display:inline">活潑</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="trait3" value="體貼">
                            <label for="trait3" style="display:inline">體貼</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="trait4" value="幽默">
                            <label for="trait4" style="display:inline">幽默</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="trait5" value="知性">
                            <label for="trait5" style="display:inline">知性</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" id="trait6" value="可愛">
                            <label for="trait6" style="display:inline">可愛</label>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label>興趣愛好（用逗號分隔）：</label>
                    <input type="text" id="interests" placeholder="例如：音樂、電影、旅行">
                </div>

                <div class="form-group">
                    <label>年齡範圍：</label>
                    <input type="text" id="ageRange" placeholder="例如：20-25">
                </div>

                <div class="form-group">
                    <label>職業背景：</label>
                    <input type="text" id="occupation" placeholder="例如：學生、上班族">
                </div>

                <div class="button-group">
                    <button onclick="prevStep(1)">上一步</button>
                    <button onclick="nextStep(3)">下一步</button>
                </div>
            </div>

            <!-- Step 3: Custom Memory -->
            <div id="step3" class="step">
                <h2>第三步：告訴我關於你自己</h2>

                <div class="form-group">
                    <label>你喜歡的事物：</label>
                    <textarea id="likes" placeholder="例如：喜歡喝咖啡、喜歡看電影、喜歡運動..."></textarea>
                </div>

                <div class="form-group">
                    <label>你不喜歡的事物：</label>
                    <textarea id="dislikes" placeholder="例如：不喜歡吵鬧的環境、不喜歡熬夜..."></textarea>
                </div>

                <div class="form-group">
                    <label>你的生活習慣：</label>
                    <textarea id="habits" placeholder="例如：早睡早起、喜歡規律作息..."></textarea>
                </div>

                <div class="form-group">
                    <label>你的職業/愛好：</label>
                    <textarea id="background" placeholder="例如：我是軟體工程師，平時喜歡寫程式..."></textarea>
                </div>

                <div class="button-group">
                    <button onclick="prevStep(2)">上一步</button>
                    <button onclick="generateCharacter()">生成我的專屬伴侶</button>
                </div>
            </div>

            <!-- Step 4: Character Result -->
            <div id="step4" class="step">
                <h2>你的專屬AI伴侶</h2>
                <div id="characterResult" class="character-result"></div>

                <div class="chat-test">
                    <h3>試著和她聊聊天吧！</h3>
                    <div id="chatMessages"></div>
                    <div class="form-group" style="margin-top: 15px;">
                        <input type="text" id="userMessage" placeholder="輸入你想說的話..." onkeypress="if(event.key==='Enter') sendMessage()">
                        <button onclick="sendMessage()" style="width: 100%; margin-top: 10px;">發送</button>
                    </div>
                </div>

                <div class="button-group" style="margin-top: 20px;">
                    <button onclick="location.reload()">重新開始</button>
                </div>
            </div>
        </div>

        <script>
            let currentStep = 1;
            let generatedCharacter = null;
            let userId = null;
            let characterId = null;
            let favorabilityLevel = 1;
            let messageCount = 0;

            function nextStep(step) {
                // Validate current step
                if (step === 2 && !document.getElementById('userName').value) {
                    alert('請輸入你的名字');
                    return;
                }

                document.getElementById('step' + currentStep).classList.remove('active');
                document.getElementById('step' + step).classList.add('active');
                currentStep = step;
            }

            function prevStep(step) {
                document.getElementById('step' + currentStep).classList.remove('active');
                document.getElementById('step' + step).classList.add('active');
                currentStep = step;
            }

            function getSelectedTraits() {
                const traits = [];
                for (let i = 1; i <= 6; i++) {
                    const checkbox = document.getElementById('trait' + i);
                    if (checkbox.checked) {
                        traits.push(checkbox.value);
                    }
                }
                return traits;
            }

            async function generateCharacter() {
                const userName = document.getElementById('userName').value;
                const talkingStyle = document.getElementById('talkingStyle').value;
                const traits = getSelectedTraits();
                const interests = document.getElementById('interests').value.split('、').map(s => s.trim()).filter(s => s);
                const ageRange = document.getElementById('ageRange').value;
                const occupation = document.getElementById('occupation').value;
                const likes = document.getElementById('likes').value;
                const dislikes = document.getElementById('dislikes').value;
                const habits = document.getElementById('habits').value;
                const background = document.getElementById('background').value;

                if (traits.length === 0) {
                    alert('請至少選擇一個性格特質');
                    return;
                }

                const userProfile = {
                    user_name: userName,
                    dream_type: {
                        personality_traits: traits,
                        physical_description: '',
                        age_range: ageRange,
                        interests: interests,
                        occupation: occupation,
                        talking_style: talkingStyle
                    },
                    custom_memory: {
                        likes: { general: likes.split('、').map(s => s.trim()).filter(s => s) },
                        dislikes: { general: dislikes.split('、').map(s => s.trim()).filter(s => s) },
                        habits: { general: habits },
                        personal_background: { general: background }
                    }
                };

                // Show loading
                document.getElementById('characterResult').innerHTML = '<div class="loading">正在生成你的專屬伴侶...</div>';
                nextStep(4);

                try {
                    const response = await fetch('/api/v2/create-character', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(userProfile)
                    });

                    const data = await response.json();

                    if (data.success) {
                        // Save Phase 2 data
                        userId = data.user_id;
                        characterId = data.character_id;
                        generatedCharacter = data.character;
                        favorabilityLevel = data.favorability_level;
                        messageCount = 0;

                        displayCharacter(data.character, data.initial_message);
                    } else {
                        alert('生成失敗：' + data.message);
                    }
                } catch (error) {
                    alert('發生錯誤：' + error.message);
                }
            }

            function displayCharacter(character, initialMessage) {
                // Parse other_setting to get background story
                let backgroundStory = '';
                try {
                    const otherSetting = typeof character.other_setting === 'string'
                        ? JSON.parse(character.other_setting)
                        : character.other_setting;
                    backgroundStory = otherSetting.background_story || '';
                } catch (e) {
                    console.error('Failed to parse other_setting:', e);
                }

                // Favorability level display
                const favorabilityText = favorabilityLevel === 1 ? '陌生期 (Level 1)' :
                                        favorabilityLevel === 2 ? '熟悉期 (Level 2)' :
                                        '親密期 (Level 3)';
                const favorabilityColor = favorabilityLevel === 1 ? '#9e9e9e' :
                                         favorabilityLevel === 2 ? '#ff9800' :
                                         '#e91e63';

                const html = `
                    <div class="character-name">💕 ${character.name} (${character.nickname})</div>
                    <div class="character-detail"><strong>身份：</strong>${character.identity || '神秘'}</div>
                    <div class="character-detail"><strong>性格：</strong>${character.detail_setting}</div>
                    <div class="character-detail" style="background: ${favorabilityColor}15; padding: 10px; border-radius: 8px; border-left: 4px solid ${favorabilityColor};"><strong>💗 好感度：</strong><span style="color: ${favorabilityColor}; font-weight: bold;">${favorabilityText}</span> <span style="font-size: 12px; color: #666;">(訊息數: ${messageCount})</span></div>
                    ${backgroundStory ? `<div class="character-detail" style="background: #fff3e0; padding: 15px; border-radius: 8px; margin-top: 15px;"><strong>✨ 她的故事：</strong><br/><div style="margin-top: 8px; line-height: 1.8;">${backgroundStory}</div></div>` : ''}
                    <div class="character-detail" style="margin-top: 15px;"><strong>初次見面：</strong>${initialMessage}</div>
                `;
                document.getElementById('characterResult').innerHTML = html;

                // Display initial message in chat
                displayMessage(character.name, initialMessage, 'character');
            }

            function displayMessage(sender, content, type) {
                const chatMessages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + type;
                messageDiv.innerHTML = `<strong>${sender}：</strong>${content}`;
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            async function sendMessage() {
                const input = document.getElementById('userMessage');
                const message = input.value.trim();

                if (!message) return;

                const userName = document.getElementById('userName').value;
                displayMessage(userName, message, 'user');
                input.value = '';

                // Show loading indicator
                const loadingDiv = document.createElement('div');
                loadingDiv.id = 'loading-indicator';
                loadingDiv.className = 'message character';
                loadingDiv.innerHTML = '<em>正在輸入...</em>';
                document.getElementById('chatMessages').appendChild(loadingDiv);

                try {
                    const response = await fetch('/api/v2/send-message', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            user_id: userId,
                            character_id: characterId,
                            message: message
                        })
                    });

                    const data = await response.json();

                    // Remove loading indicator
                    const loading = document.getElementById('loading-indicator');
                    if (loading) loading.remove();

                    if (data.success) {
                        displayMessage(generatedCharacter.name, data.reply, 'character');

                        // Update favorability info
                        favorabilityLevel = data.favorability_level;
                        messageCount = data.message_count;

                        // Show level up notification
                        if (data.level_increased) {
                            const levelUpText = favorabilityLevel === 2 ? '你們的關係變得更熟悉了！ 💛' :
                                               favorabilityLevel === 3 ? '你們的關係變得親密了！ 💖' : '';
                            const notification = document.createElement('div');
                            notification.className = 'message';
                            notification.style = 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; font-weight: bold;';
                            notification.innerHTML = `🎉 好感度提升！${levelUpText}`;
                            document.getElementById('chatMessages').appendChild(notification);
                        }

                        // Update favorability display
                        updateFavorabilityDisplay();
                    } else {
                        alert('發送失敗');
                    }
                } catch (error) {
                    // Remove loading indicator if error occurs
                    const loading = document.getElementById('loading-indicator');
                    if (loading) loading.remove();
                    alert('發生錯誤：' + error.message);
                }
            }

            function updateFavorabilityDisplay() {
                // Update the favorability display in character result
                const favorabilityText = favorabilityLevel === 1 ? '陌生期 (Level 1)' :
                                        favorabilityLevel === 2 ? '熟悉期 (Level 2)' :
                                        '親密期 (Level 3)';
                const favorabilityColor = favorabilityLevel === 1 ? '#9e9e9e' :
                                         favorabilityLevel === 2 ? '#ff9800' :
                                         '#e91e63';

                // Re-render character with updated favorability
                displayCharacter(generatedCharacter, '');
            }
        </script>
    </body>
    </html>
    """

    return HTMLResponse(
        content=html_content,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
