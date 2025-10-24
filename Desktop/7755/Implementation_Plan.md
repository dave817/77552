# Dating Chatbot Implementation Plan
## Using SenseChat-Character-Pro API

---

## Table of Contents
1. [Phase 1: User Onboarding & Character Generation](#phase-1-user-onboarding--character-generation)
2. [Phase 2: Conversation Flow Architecture](#phase-2-conversation-flow-architecture)
3. [Phase 3: Advanced Features](#phase-3-advanced-features)
4. [Phase 4: Technical Architecture](#phase-4-technical-architecture)
5. [Phase 5: Frontend Components](#phase-5-frontend-components)
6. [Phase 6: Advanced Enhancements](#phase-6-advanced-enhancements)
7. [Phase 7: Testing & Quality Assurance](#phase-7-testing--quality-assurance)
8. [Phase 8: Deployment Considerations](#phase-8-deployment-considerations)
9. [Implementation Priority Order](#implementation-priority-order)
10. [Technical Stack Recommendation](#technical-stack-recommendation)

---

## Phase 1: User Onboarding & Character Generation

### 1.1 User Input Collection (Traditional Chinese Interface)

#### Step 1: Dream Type Collection (理想型收集)
- **Question**: "請描述你的理想伴侶類型"
- **Input Fields**:
  - Personality traits (性格特質): e.g., 溫柔、活潑、成熟、可愛
  - Physical description (外貌描述): e.g., 高挑、甜美、運動型
  - Age range (年齡範圍): e.g., 20-25歲
  - Interests/hobbies (興趣愛好): e.g., 喜歡音樂、運動、閱讀
  - Occupation/background (職業背景): e.g., 學生、上班族、藝術家
  - Talking style preference (說話風格): e.g., 溫柔體貼、活潑幽默、知性優雅

#### Step 2: Custom Memory Collection (個人記憶收集)
- **Question**: "告訴我關於你自己的事"
- **Input Categories**:
  - **Likes (喜好)**:
    - Food preferences (飲食偏好)
    - Activities (活動)
    - Topics of interest (感興趣的話題)
  - **Dislikes (不喜歡)**:
    - Pet peeves (討厭的事)
    - Topics to avoid (避免的話題)
  - **Habits (習慣)**:
    - Daily routine (日常作息)
    - Communication style (溝通方式)
    - Special dates/events (特殊日期)
  - **Personal Background (個人背景)**:
    - Occupation (職業)
    - Hobbies (愛好)
    - Life goals (人生目標)

### 1.2 Character Profile Generation Logic

#### Mapping User Input → Character Settings:

```json
{
  "character_settings": {
    "name": "[Generated based on personality, e.g., '小雨' for gentle type]",
    "gender": "[Based on user's dream type]",
    "identity": "[Occupation + age + basic background, max 200 chars]",
    "nickname": "[Sweet nickname, max 50 chars]",
    "detail_setting": "[Core personality traits, talking style, behavioral patterns, emotional characteristics - max 500 chars]",
    "other_setting": {
      "interests": ["..."],
      "background_story": "...",
      "values": ["..."],
      "communication_style": "...",
      "relationship_goals": "..."
    },
    "feeling_toward": [
      {
        "name": "[User's name]",
        "level": 1
      }
    ]
  }
}
```

**Character Name Generation Strategy**:
- Traditional Chinese names based on personality
- Examples:
  - 溫柔型 → 小雨/婉婷
  - 活潑型 → 欣怡/小晴
  - 成熟型 → 雅文/靜儀

---

## Phase 2: Conversation Flow Architecture

### 2.1 Initial Conversation Setup

#### First Message Strategy:
1. Character introduces herself naturally
2. References some aspect of user's preferences (from custom memory)
3. Opens with a warm, engaging question

#### Example Flow:
```
User completes profile →
Character generated →
System creates initial context →
Character: "嗨！我是小雨,聽說你喜歡音樂？我最近在聽一首很好聽的歌..." →
Conversation begins
```

### 2.2 Message History Management

#### Structure:
```json
{
  "messages": [
    {
      "name": "[Character name]",
      "content": "[Character's previous message]"
    },
    {
      "name": "[User name]",
      "content": "[User's response]"
    }
  ]
}
```

#### Memory Management:
- Store full conversation history in database
- Send last 50-100 messages to API (within 32K token limit)
- Older messages stored for reference but not sent to API
- Implement token counting to stay within limits

### 2.3 Role Setting Configuration

#### For each API call:
```json
{
  "role_setting": {
    "user_name": "[User's name/ID]",
    "primary_bot_name": "[Character's name]"
  }
}
```

---

## Phase 3: Advanced Features

### 3.1 Favorability System Implementation

#### Favorability Progression Logic:

**Level 1** (陌生期 - Stranger Phase):
- Initial 10-20 messages
- Polite, curious, getting-to-know-you tone
- Character responses are friendly but reserved

**Level 2** (熟悉期 - Familiar Phase):
- After 20-50 messages
- More personal conversations
- Character shares more about herself
- Shows more interest in user's life

**Level 3** (親密期 - Intimate Phase):
- After 50+ messages or specific milestones
- Deep emotional connection
- Character expresses affection
- Remembers important details consistently

#### Trigger Conditions for Level Increase:
- Number of messages exchanged
- Quality of conversation (positive sentiment)
- User engagement frequency
- Shared personal information

### 3.2 Knowledge Base Integration (Optional Enhancement)

#### Purpose: Store character-specific knowledge
- Background story details
- Shared memories with user
- Important dates/events
- User's preferences (from custom memory)

#### Implementation:
```json
{
  "qa_lst": [
    {
      "std_q": "你記得我喜歡什麼嗎？",
      "simi_qs": ["我的喜好是什麼", "我喜歡什麼"],
      "answer": "[Retrieved from user's custom memory]"
    }
  ],
  "text_lst": [
    "[Character background story]",
    "[Shared experience #1]",
    "[Important user preferences]"
  ]
}
```

#### API Integration:
- Upload knowledge base files
- Pass `know_ids` in chat completion requests
- Character can reference stored memories naturally

### 3.3 Conversation Context Enhancement

#### System Prompting Strategy (via `detail_setting` and `other_setting`):
- Always respond in Traditional Chinese
- Reference user's custom memory naturally
- Maintain consistent personality
- Show emotional growth based on favorability level
- Remember previous conversations

---

## Phase 4: Technical Architecture

### 4.1 Backend Components

#### Component 1: Character Generator Service
- **Input**: User's dream type + custom memory
- **Output**: Complete `character_settings` object
- Uses template-based generation with variations
- Validates character limits (50/200/500/2000 chars)

#### Component 2: Conversation Manager
- Manages message history
- Tracks conversation state
- Implements favorability level logic
- Handles API calls to SenseChat-Character-Pro

#### Component 3: API Client
- JWT token generation (using AccessKey ID/Secret)
- HTTP request handling
- Response parsing
- Error handling (rate limits, API errors)

#### Component 4: Database Layer
- User profiles
- Character profiles (generated)
- Conversation history
- Favorability tracking
- Session management

### 4.2 Database Schema

#### Users Table:
```sql
- user_id (primary key)
- username
- created_at
- last_active
```

#### Characters Table:
```sql
- character_id (primary key)
- user_id (foreign key)
- name
- gender
- identity
- nickname
- detail_setting
- other_setting (JSON)
- created_at
```

#### Conversations Table:
```sql
- message_id (primary key)
- user_id (foreign key)
- character_id (foreign key)
- speaker_name
- message_content
- timestamp
- favorability_level (at time of message)
```

#### User_Preferences Table (Custom Memory):
```sql
- preference_id (primary key)
- user_id (foreign key)
- category (likes/dislikes/habits)
- content (JSON)
- created_at
```

#### Favorability_Tracking Table:
```sql
- tracking_id (primary key)
- user_id (foreign key)
- character_id (foreign key)
- current_level (1-3)
- message_count
- last_updated
```

### 4.3 API Request Flow

#### For each user message:
1. Retrieve character settings from database
2. Retrieve last N messages from conversation history
3. Get current favorability level
4. Update `feeling_toward` in character settings
5. Construct API request:
   ```json
   {
     "method": "POST",
     "url": "https://api.sensenova.cn/v1/llm/character/chat-completions",
     "headers": {
       "Authorization": "Bearer [JWT_TOKEN]"
     },
     "body": {
       "model": "SenseChat-Character-Pro",
       "character_settings": [...],
       "role_setting": {...},
       "messages": [...],
       "max_new_tokens": 1024,
       "n": 1
     }
   }
   ```
6. Receive response with character's reply
7. Save message to database
8. Update conversation statistics
9. Check if favorability level should increase
10. Return response to frontend

### 4.4 Authentication & Token Management

#### JWT Token Generation:
```python
# Implementation using PyJWT:
# Header: {"alg": "HS256", "typ": "JWT"}
# Payload: {
#   "iss": AccessKey_ID,
#   "exp": current_time + 1800 seconds,
#   "nbf": current_time - 5 seconds
# }
# Signature: sign with AccessKey_Secret
```

#### Token Refresh Strategy:
- Tokens expire in 30 minutes
- Generate new token every 25 minutes proactively
- Handle token expiration errors gracefully

### 4.5 Rate Limiting

**API Rate Limit**: 60 RPM
- Implement request queue
- Track requests per minute
- Add delays if approaching limit
- Return user-friendly messages during rate limiting

---

## Phase 5: Frontend Components

### 5.1 User Interface Screens (Traditional Chinese)

#### Screen 1: Welcome / Onboarding
- Title: "歡迎使用戀愛聊天機器人"
- Brief introduction
- Start button → Go to Dream Type Input

#### Screen 2: Dream Type Input
- Form fields for ideal partner description
- Dropdowns/checkboxes for personality traits
- Text areas for detailed descriptions
- "下一步" (Next) button

#### Screen 3: Custom Memory Input
- Sections for likes/dislikes/habits
- Free-text input areas
- "完成" (Complete) button

#### Screen 4: Character Generation Loading
- "正在生成你的專屬伴侶..."
- Loading animation
- Character preview appears when ready

#### Screen 5: Chat Interface
- Character avatar/profile card
- Favorability level indicator (♥♥♥)
- Message history (scrollable)
- Input box for user messages
- Send button
- Settings/menu button

#### Screen 6: Character Profile View
- Full character details
- Favorability progress
- Conversation statistics
- Option to regenerate character (warning: loses history)

### 5.2 UI/UX Features

#### Real-time Features:
- Typing indicator when character is "thinking"
- Message delivery animations
- Favorability level up notifications

#### Visual Feedback:
- Level 1: Grey/neutral heart color
- Level 2: Pink heart color
- Level 3: Red/glowing heart color

#### Responsive Design:
- Mobile-first approach
- Works on desktop and mobile browsers

---

## Phase 6: Advanced Enhancements

### 6.1 Character Personality Variations

#### Template Categories:

**1. 溫柔體貼型 (Gentle & Caring)**
- Soft language, caring questions
- Uses terms like "要注意身體哦", "有好好吃飯嗎"

**2. 活潑開朗型 (Cheerful & Lively)**
- Exclamation marks, emojis (if allowed by user preference)
- Energetic language, "哈哈", "太好了！"

**3. 知性優雅型 (Intellectual & Elegant)**
- Sophisticated vocabulary
- Cultural references, book/art discussions

**4. 可愛天真型 (Cute & Innocent)**
- Simplified expressions
- Curious questions, playful tone

### 6.2 Conversation Quality Enhancement

#### Natural Language Patterns:
- Character occasionally initiates new topics
- References earlier conversations
- Asks follow-up questions
- Shows emotional reactions
- Maintains consistent speech patterns

#### Memory Integration:
- Character naturally mentions user's preferences
- Example: User likes coffee → Character: "今天想喝咖啡嗎？我記得你喜歡拿鐵"

### 6.3 Special Events/Features

#### Time-based Interactions:
- Morning greetings (早安)
- Evening check-ins (晚安)
- Weekend plans discussions

#### Milestone Celebrations:
- First conversation anniversary
- 100 message milestone
- Favorability level increases

#### Optional Future Features:
- Multiple character support (user can create different characters)
- Character customization (change appearance, personality tweaks)
- Export conversation history
- Voice message support (if API supports TTS)

---

## Phase 7: Testing & Quality Assurance

### 7.1 Test Scenarios

#### Character Generation Testing:
- Various dream type inputs
- Edge cases (minimal input, maximum input)
- Special characters in custom memory
- Different personality combinations

#### Conversation Flow Testing:
- Short conversations (5-10 messages)
- Medium conversations (20-50 messages)
- Long conversations (100+ messages)
- Favorability progression accuracy

#### API Integration Testing:
- Token expiration handling
- Rate limit scenarios
- Network errors
- Invalid responses

### 7.2 Quality Checks

#### Character Consistency:
- Personality remains stable across conversations
- No contradictions in character responses
- Appropriate favorability level tone

#### Language Quality:
- Proper Traditional Chinese usage
- Natural conversation flow
- No awkward translations

#### Memory Accuracy:
- Character correctly recalls user preferences
- References custom memory appropriately

---

## Phase 8: Deployment Considerations

### 8.1 Environment Setup

#### Development:
- Local Python environment
- Test database (SQLite)
- Mock API responses for testing

#### Production:
- Hosted backend (e.g., Railway, Render, AWS)
- Production database (PostgreSQL/MySQL)
- Real SenseChat API integration

### 8.2 Security

#### API Key Protection:
- Never expose AccessKey ID/Secret in frontend
- Use environment variables
- Backend-only API calls

#### User Data Privacy:
- Encrypt sensitive user information
- Secure database connections
- HTTPS for all communications

### 8.3 Monitoring

#### Metrics to Track:
- API usage (stay within 60 RPM)
- Average conversation length
- User retention rates
- Favorability progression patterns
- Error rates

---

## Implementation Priority Order

### Priority 1 (MVP - Minimum Viable Product):
1. User input collection (dream type + custom memory)
2. Basic character generation (name, personality, detail_setting)
3. Simple chat interface
4. API integration with message history
5. Database for storing conversations

### Priority 2 (Enhanced Features):
6. Favorability system implementation
7. Character profile view
8. Improved UI/UX
9. Advanced character customization (other_setting)
10. Memory enhancement (knowledge base integration)

### Priority 3 (Polish & Advanced):
11. Special events/milestones
12. Multiple conversation templates
13. Analytics dashboard
14. Export features
15. Advanced personalization

---

## Technical Stack Recommendation

### Backend:
- **Framework**: FastAPI (async, modern, fast)
- **Database**: PostgreSQL (production) / SQLite (development)
- **ORM**: SQLAlchemy
- **Authentication**: JWT (for API token generation)
- **API Client**: `sensenova` Python SDK or direct HTTP requests

### Frontend:
- **Framework**: React or Vue.js
- **Language**: TypeScript (type safety)
- **UI Library**: Ant Design / Material-UI (supports Traditional Chinese)
- **State Management**: Redux/Vuex or React Context
- **HTTP Client**: Axios

### Deployment:
- **Backend**: Railway, Render, or AWS Lambda
- **Frontend**: Vercel, Netlify
- **Database**: Supabase, Railway PostgreSQL, or AWS RDS

---

## Key Strengths of SenseChat-Character-Pro

✅ **Built-in character roleplay capabilities**
✅ **32K context window for long conversations (100+ messages)**
✅ **Native Traditional Chinese support**
✅ **Favorability system for relationship progression**
✅ **Flexible character customization (up to 2000 chars in other_setting)**
✅ **60 RPM rate limit (sufficient for personal projects)**
✅ **Official Python SDK available**

---

## API Credentials Reference

**Model**: SenseChat-Character-Pro
**API Key**: sk-KwTRyijO6ByCWjrjm3vf5bwgGktAKOYQ
**AccessKey ID**: 019A0A2BD9067A46B8DD59CBD56F2A9C
**AccessKey Secret**: 019A0A2BD9067A3689A95F2111B79929
**Endpoint**: https://api.sensenova.cn/v1/llm/character/chat-completions
**Rate Limit**: 60 RPM
**Context Length**: 32K tokens
**Max Response**: 4096 tokens (default 500)

---

## Next Steps

1. Review and approve this implementation plan
2. Set up development environment
3. Start with Priority 1 (MVP) implementation
4. Iteratively add Priority 2 and 3 features
5. Test thoroughly before deployment
6. Deploy and monitor performance

---

*Document created: 2025-10-22*
*Last updated: 2025-10-22*
