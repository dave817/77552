# Phase 2 完成報告

## ✅ 已實現功能

### 1. 數據庫持久化系統

**文件**: `backend/database.py`

實現了完整的數據庫模型和 ORM 映射：

#### 數據表結構

**Users 表** - 用戶管理
```python
- user_id (主鍵)
- username (唯一，索引)
- created_at
- last_active
```

**Characters 表** - AI 角色
```python
- character_id (主鍵)
- user_id (外鍵)
- name, gender, identity, nickname
- detail_setting, other_setting (JSON)
- created_at
```

**Messages 表** - 對話記錄
```python
- message_id (主鍵)
- user_id, character_id (外鍵)
- speaker_name, message_content
- timestamp (索引)
- favorability_level (當時的好感度)
```

**FavorabilityTracking 表** - 好感度追蹤
```python
- tracking_id (主鍵)
- user_id, character_id (外鍵，唯一)
- current_level (1-3)
- message_count
- last_updated
```

**UserPreference 表** - 用戶偏好
```python
- preference_id (主鍵)
- user_id (外鍵)
- category, content (JSON)
- created_at
```

#### 關鍵特性

✅ **自動初始化**: 應用啟動時自動創建數據表
✅ **關係映射**: SQLAlchemy ORM 完整關係定義
✅ **級聯刪除**: 刪除用戶時自動清理相關數據
✅ **時間戳記**: 自動記錄創建和更新時間

---

### 2. 對話管理系統

**文件**: `backend/conversation_manager.py`

#### ConversationManager 類

核心功能實現：

1. **用戶管理**
   ```python
   get_or_create_user(username) # 獲取或創建用戶
   ```

2. **角色管理**
   ```python
   save_character(user_id, character_data) # 保存角色
   get_character(character_id) # 獲取角色
   get_user_characters(user_id) # 獲取用戶的所有角色
   ```

3. **對話歷史**
   ```python
   save_message(...) # 保存訊息
   get_conversation_history(character_id, limit) # 獲取歷史
   format_messages_for_api(messages) # 格式化給 API
   ```

4. **好感度系統**
   ```python
   get_favorability(character_id) # 獲取好感度
   update_favorability(character_id) # 更新並檢查升級
   ```

5. **完整對話流程**
   ```python
   send_message(user_id, character_id, user_message)
   # 1. 保存用戶訊息
   # 2. 獲取歷史（最多100條）
   # 3. 調用 API（帶歷史和當前好感度）
   # 4. 保存角色回應
   # 5. 更新好感度
   # 6. 返回結果
   ```

#### 好感度升級邏輯

```python
LEVEL_1_THRESHOLD = 0   # 0-19 訊息
LEVEL_2_THRESHOLD = 20  # 20-49 訊息
LEVEL_3_THRESHOLD = 50  # 50+ 訊息
```

- **Level 1** (陌生期): 0-19 條訊息，禮貌保留
- **Level 2** (熟悉期): 20-49 條訊息，更親近友好
- **Level 3** (親密期): 50+ 條訊息，深度情感連結

升級時自動通知前端！

---

### 3. API 端點 (Phase 2)

#### POST /api/v2/create-character
創建角色並保存到數據庫

**請求**:
```json
{
  "user_name": "用戶名",
  "dream_type": {...},
  "custom_memory": {...}
}
```

**回應**:
```json
{
  "success": true,
  "user_id": 1,
  "character_id": 1,
  "character": {...},
  "initial_message": "嗨！我是...",
  "favorability_level": 1
}
```

#### POST /api/v2/send-message
發送訊息（帶完整歷史和好感度）

**請求**:
```json
{
  "user_id": 1,
  "character_id": 1,
  "message": "你好！"
}
```

**回應**:
```json
{
  "success": true,
  "reply": "你好！很高興見到你...",
  "favorability_level": 1,
  "level_increased": false,
  "message_count": 5,
  "usage": {...}
}
```

#### GET /api/v2/conversation-history/{character_id}
獲取對話歷史

**查詢參數**: `limit` (默認50)

**回應**:
```json
{
  "success": true,
  "character_id": 1,
  "message_count": 10,
  "messages": [
    {
      "message_id": 1,
      "speaker_name": "小雨",
      "content": "你好！",
      "timestamp": "2025-10-22T...",
      "favorability_level": 1
    },
    ...
  ]
}
```

#### GET /api/v2/user-characters/{user_id}
獲取用戶的所有角色

**回應**:
```json
{
  "success": true,
  "user_id": 1,
  "character_count": 2,
  "characters": [
    {
      "character_id": 1,
      "name": "小雨",
      "nickname": "雨雨",
      "created_at": "2025-10-22T...",
      "favorability": 2
    },
    ...
  ]
}
```

#### GET /api/v2/favorability/{character_id}
獲取好感度狀態

**回應**:
```json
{
  "success": true,
  "character_id": 1,
  "current_level": 2,
  "message_count": 25,
  "last_updated": "2025-10-22T...",
  "progress": {
    "level_1_threshold": 0,
    "level_2_threshold": 20,
    "level_3_threshold": 50
  }
}
```

---

### 4. 技術改進

#### 數據庫連接管理

使用 FastAPI 的依賴注入：
```python
@app.post("/api/v2/send-message")
async def send_message_v2(
    user_id: int,
    character_id: int,
    message: str,
    db: Session = Depends(get_db)  # 自動管理連接
) -> Dict:
    ...
```

#### 應用啟動時初始化

```python
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized")
```

#### 歷史訊息優化

- 只發送最近 100 條訊息給 API
- 避免超過 32K token 限制
- 更早的訊息保存在數據庫中可查詢

#### 好感度與對話整合

角色的 `feeling_toward` 參數動態更新：
```python
"feeling_toward": [
    {
        "name": user.username,
        "level": current_level  # 1, 2, or 3
    }
]
```

AI 會根據好感度調整回應風格！

---

### 5. 測試腳本

**文件**: `test_phase2.py`

完整測試套件：

1. ✅ **數據庫初始化測試**
2. ✅ **角色創建和保存測試**
3. ✅ **對話流程測試** (5輪對話)
4. ✅ **好感度升級測試** (55輪對話，測試3個等級)

運行測試：
```bash
python test_phase2.py
```

---

### 6. Phase 1 vs Phase 2 對比

| 功能 | Phase 1 | Phase 2 |
|------|---------|---------|
| 角色創建 | ✅ 臨時生成 | ✅ 保存到數據庫 |
| 對話歷史 | ❌ 無持久化 | ✅ 完整保存 |
| 好感度追蹤 | ❌ 無 | ✅ 自動追蹤升級 |
| 多角色支持 | ❌ 單次會話 | ✅ 支持多個角色 |
| 會話恢復 | ❌ 無法恢復 | ✅ 隨時恢復 |
| 歷史查詢 | ❌ 無 | ✅ 完整API |
| 數據持久化 | ❌ 無 | ✅ SQLite 數據庫 |

---

### 7. 數據流程

#### 創建角色流程

```
用戶提交表單
  → POST /api/v2/create-character
    → 獲取或創建用戶
    → 生成角色（AI背景故事）
    → 保存角色到數據庫
    → 初始化好感度追蹤（Level 1）
    → 生成初始訊息
    → 保存初始訊息
  → 返回 user_id 和 character_id
```

#### 發送訊息流程

```
用戶發送訊息
  → POST /api/v2/send-message
    → 保存用戶訊息到數據庫
    → 獲取對話歷史（最多100條）
    → 獲取當前好感度
    → 構建 API 請求（包含歷史和好感度）
    → 調用 SenseChat API
    → 保存 AI 回應到數據庫
    → 更新好感度計數
    → 檢查是否升級
  → 返回回應和好感度信息
```

---

### 8. 數據庫文件

數據庫文件位置：`./dating_chatbot.db`

可以使用 SQLite 工具查看：
```bash
sqlite3 dating_chatbot.db
.tables  # 查看所有表
SELECT * FROM users;  # 查看用戶
SELECT * FROM characters;  # 查看角色
SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10;  # 最近10條訊息
SELECT * FROM favorability_tracking;  # 好感度狀態
```

---

### 9. 性能考慮

#### Token 管理

- 限制歷史訊息數量（100條）
- 估計不會超過 32K token 限制
- 每條訊息平均 ~100 tokens
- 100 條訊息 ≈ 10K tokens
- 加上角色設定 ≈ 12K tokens
- 安全範圍內

#### 數據庫性能

- 索引關鍵欄位 (timestamp, character_id, user_id)
- SQLite 適合小型應用（<1000 用戶）
- 可升級到 PostgreSQL/MySQL

#### API 速率限制

- 60 RPM 限制
- 平均每次對話 1-2 個請求
- 足夠支持 30-60 個並發對話

---

### 10. 升級路徑

#### 從 Phase 1 升級到 Phase 2

**Phase 1 端點仍然可用**:
- `/api/generate-character` - 臨時生成（無數據庫）
- `/api/test-chat` - 臨時對話（無歷史）

**Phase 2 新端點**:
- `/api/v2/*` - 完整功能（帶數據庫）

**建議**:
- 新應用使用 v2 端點
- 舊代碼保持兼容
- 逐步遷移

---

### 11. 未來增強

已為以下功能預留空間：

1. **知識庫整合** (Phase 3)
   - 在 `ConversationManager` 中添加知識庫支持
   - API 已支持 `know_ids` 參數

2. **多用戶身份**
   - User 表已設計完整
   - 可添加認證系統

3. **角色多樣化**
   - 支持一個用戶創建多個角色
   - 每個角色獨立的對話和好感度

4. **統計分析**
   - 數據庫結構支持統計查詢
   - 可添加分析端點

---

### 12. 關鍵文件清單

```
backend/
├── database.py                 # 數據庫模型 ⭐
├── conversation_manager.py     # 對話管理器 ⭐
├── main.py                     # API 端點（含 v2）⭐
├── character_generator.py      # 角色生成器
├── api_client.py              # API 客戶端
├── models.py                  # Pydantic 模型
└── config.py                  # 配置

test_phase2.py                 # Phase 2 測試 ⭐
dating_chatbot.db              # SQLite 數據庫文件 ⭐
```

---

### 13. 驗收標準

| 功能 | 狀態 | 備註 |
|------|------|------|
| 數據庫自動初始化 | ✅ | 啟動時創建表 |
| 用戶創建和管理 | ✅ | 自動去重 |
| 角色保存到數據庫 | ✅ | 完整字段 |
| 對話歷史保存 | ✅ | 每條訊息 |
| 對話歷史查詢 | ✅ | API 端點 |
| 好感度初始化 | ✅ | Level 1 |
| 好感度自動更新 | ✅ | 每次對話 |
| 好感度升級檢測 | ✅ | 20/50 閾值 |
| 多輪對話上下文 | ✅ | 最多100條 |
| API 錯誤處理 | ✅ | 完整異常 |

---

### 14. 已知限制

1. **數據庫**:
   - 目前使用 SQLite（單文件）
   - 適合開發和小型部署
   - 生產環境建議 PostgreSQL

2. **Token 計數**:
   - 目前按訊息數量限制（100條）
   - 未實現精確 token 計數
   - 未來可添加 tiktoken

3. **並發**:
   - SQLite 不適合高並發
   - 需要時可升級數據庫

4. **緩存**:
   - 未實現查詢緩存
   - 每次都查數據庫

---

## 🎉 Phase 2 總結

### ✅ 核心成就

1. **完整的數據持久化** - 所有數據保存到數據庫
2. **對話歷史管理** - 完整記錄和查詢
3. **好感度追蹤系統** - 自動升級，3個等級
4. **多輪對話支持** - 帶上下文的真實對話
5. **RESTful API** - 完整的 v2 端點

### 📊 代碼統計

- **新增文件**: 3 個核心文件
- **數據表**: 5 個表
- **API 端點**: 5 個 v2 端點
- **代碼行數**: ~800+ 行新代碼
- **測試覆蓋**: 4 個完整測試

### 🚀 下一步

Phase 2 已完成！可以：

1. **測試 API** - 訪問 `/docs` 查看所有端點
2. **運行測試** - `python test_phase2.py`
3. **開發 Phase 3** - 知識庫整合（可選）
4. **改進前端** - 整合 v2 API

---

**完成日期**: 2025-10-22
**狀態**: ✅ 完成並測試
**版本**: 2.0.0
