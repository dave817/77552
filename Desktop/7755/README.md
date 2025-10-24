# 戀愛聊天機器人 (Dating Chatbot)

使用 SenseChat-Character-Pro API 打造的個性化 AI 戀愛聊天機器人

## 📋 專案概述

這是一個基於 SenseChat-Character-Pro 的戀愛聊天機器人，能夠根據用戶的理想型和個人偏好，生成專屬的 AI 伴侶角色。

### 當前進度：Phase 1 - 用戶引導與角色生成 ✅

- ✅ 用戶輸入收集（繁體中文介面）
- ✅ 理想型設定（夢想伴侶類型）
- ✅ 個人記憶收集（喜好/習慣）
- ✅ AI 角色生成邏輯
- ✅ JWT 認證 API 客戶端
- ✅ 簡易網頁介面
- ✅ 基礎對話測試

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置環境變數

環境變數已經在 `.env` 文件中配置好了，包含：
- SenseChat API 憑證
- 模型名稱
- 數據庫設定

### 3. 測試 API 連接

```bash
python test_api.py
```

這個測試腳本會：
- 測試 SenseChat API 連接
- 生成測試角色
- 進行簡單對話測試

### 4. 啟動 Web 應用

```bash
python -m uvicorn backend.main:app --reload
```

或者直接：

```bash
python backend/main.py
```

### 5. 訪問應用

打開瀏覽器訪問：
- **使用者介面**: http://localhost:8000/ui
- **API 文檔**: http://localhost:8000/docs
- **健康檢查**: http://localhost:8000/health

## 📁 專案結構

```
7755/
├── backend/
│   ├── main.py                 # FastAPI 主應用
│   ├── config.py               # 配置設定
│   ├── models.py               # 數據模型
│   ├── api_client.py           # SenseChat API 客戶端
│   └── character_generator.py  # 角色生成邏輯
├── test_api.py                 # API 測試腳本
├── requirements.txt            # Python 依賴
├── .env                        # 環境變數
├── .gitignore                 # Git 忽略文件
├── Implementation_Plan.md      # 詳細實作計劃
├── Resources.md               # API 文檔資源
└── README.md                  # 專案說明
```

## 🎯 功能特色

### Phase 1 功能（已完成）

1. **用戶輸入收集**
   - 基本資料（姓名）
   - 理想伴侶類型
     - 性格特質
     - 說話風格
     - 興趣愛好
     - 年齡範圍
     - 職業背景
   - 個人記憶
     - 喜好
     - 不喜歡的事物
     - 生活習慣
     - 個人背景

2. **智能角色生成**
   - 基於性格類型自動命名
   - 生成角色身份和背景
   - 詳細人設設定（最多 500 字）
   - 擴展設定（JSON 格式，最多 2000 字）
   - 初始好感度設定（Level 1）

3. **角色類型**
   - 溫柔體貼型
   - 活潑開朗型
   - 知性優雅型
   - 可愛天真型

4. **實時對話**
   - 使用 SenseChat-Character-Pro API
   - JWT 自動認證
   - 支持多輪對話
   - 記憶用戶偏好

## 🔧 API 端點

### POST /api/generate-character
生成 AI 角色

**請求體**:
```json
{
  "user_name": "小明",
  "dream_type": {
    "personality_traits": ["溫柔", "體貼"],
    "talking_style": "溫柔體貼",
    "interests": ["音樂", "閱讀"],
    "age_range": "22-25",
    "occupation": "學生"
  },
  "custom_memory": {
    "likes": {"food": ["咖啡"]},
    "dislikes": {"general": ["吵鬧"]},
    "habits": {"daily_routine": "早睡早起"},
    "personal_background": {"occupation": "工程師"}
  }
}
```

**回應**:
```json
{
  "success": true,
  "character": {
    "name": "小雨",
    "nickname": "雨雨",
    "gender": "女",
    "identity": "22-25歲，學生，喜歡音樂",
    "detail_setting": "性格溫柔體貼...",
    "other_setting": "{...}",
    "feeling_toward": [{"name": "小明", "level": 1}]
  },
  "initial_message": "嗨！我是小雨..."
}
```

### POST /api/test-chat
測試與角色對話

**請求體**:
```json
{
  "character_settings": {...},
  "user_name": "小明",
  "user_message": "你好！"
}
```

### GET /api/test-connection
測試 API 連接狀態

## 🎨 使用方式

### 網頁介面使用流程

1. **訪問** http://localhost:8000/ui
2. **輸入基本資料**
   - 填寫你的名字
3. **描述理想伴侶**
   - 選擇說話風格
   - 勾選性格特質
   - 填寫興趣愛好
   - 設定年齡範圍和職業
4. **分享個人資訊**
   - 你的喜好
   - 不喜歡的事物
   - 生活習慣
   - 個人背景
5. **生成專屬伴侶**
   - 系統自動生成 AI 角色
   - 查看角色資料
   - 開始對話！

## 📊 技術細節

### SenseChat-Character-Pro API

- **模型**: SenseChat-Character-Pro
- **上下文長度**: 32K tokens (約 100+ 輪對話)
- **速率限制**: 60 RPM
- **最大回應**: 4096 tokens
- **語言支持**: 繁體中文、英文

### JWT 認證

- 使用 HS256 算法
- Token 有效期：30 分鐘
- 自動刷新機制（提前 5 分鐘）

### 角色設定限制

- `name`: 最多 50 字符
- `gender`: 最多 50 字符
- `identity`: 最多 200 字符
- `nickname`: 最多 50 字符
- `detail_setting`: 最多 500 字符
- `other_setting`: 最多 2000 字符（JSON 字串）

## 🔜 後續開發計劃

### Phase 2 - 對話流程優化
- 完整會話歷史管理
- 數據庫持久化
- 好感度系統實作

### Phase 3 - 進階功能
- 知識庫整合
- 多輪對話優化
- 特殊事件觸發

詳細計劃請參考 `Implementation_Plan.md`

## 🐛 故障排除

### API 連接失敗
- 檢查 `.env` 文件中的憑證是否正確
- 確認網絡連接正常
- 檢查是否超過 60 RPM 速率限制

### 角色生成失敗
- 確保必填欄位都有填寫
- 檢查字符長度是否超過限制
- 查看終端錯誤訊息

### 對話無回應
- 檢查 JWT Token 是否過期
- 確認角色設定正確
- 查看 API 錯誤訊息

## 📝 License

此專案僅供學習和研究使用。

## 🙏 致謝

- SenseNova API 提供強大的角色對話能力
- FastAPI 框架
- 所有開源貢獻者

---

**開發者**: Claude Code
**最後更新**: 2025-10-22
