# 快速開始指南

## Windows 用戶

### 1. 安裝依賴
雙擊運行 `setup.bat` 或在命令提示字元中執行：
```cmd
setup.bat
```

### 2. 測試 API
```cmd
python test_api.py
```

### 3. 啟動服務器
```cmd
python -m uvicorn backend.main:app --reload
```

### 4. 訪問網頁
打開瀏覽器：http://localhost:8000/ui

---

## Linux/Mac 用戶

### 1. 安裝依賴
```bash
chmod +x setup.sh
./setup.sh
```

或手動安裝：
```bash
python3 -m pip install -r requirements.txt
```

### 2. 測試 API
```bash
python3 test_api.py
```

### 3. 啟動服務器
```bash
python3 -m uvicorn backend.main:app --reload
```

### 4. 訪問網頁
打開瀏覽器：http://localhost:8000/ui

---

## 常見問題

### Q: 提示 "pip not found"
**A**: 安裝 pip：
```bash
# Linux/Mac
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python3 get-pip.py --user

# Windows
python -m ensurepip --upgrade
```

### Q: API 連接失敗
**A**: 檢查 `.env` 文件中的憑證是否正確：
- SENSENOVA_ACCESS_KEY_ID
- SENSENOVA_SECRET_ACCESS_KEY

### Q: 端口 8000 已被佔用
**A**: 使用其他端口：
```bash
python3 -m uvicorn backend.main:app --reload --port 8080
```

### Q: 模組找不到
**A**: 確保在專案根目錄執行命令：
```bash
cd /mnt/c/Users/Administrator/Desktop/7755
python3 test_api.py
```

---

## 測試流程

### 1. 測試 API 連接
```bash
python3 test_api.py
```

預期輸出：
```
✅ API 連接成功！
✅ 角色生成成功！
✅ 對話測試完成！
```

### 2. 使用網頁介面

1. 訪問 http://localhost:8000/ui
2. 填寫基本資料
3. 描述理想伴侶
4. 分享個人資訊
5. 生成專屬 AI 伴侶
6. 開始對話！

---

## API 端點測試

### 測試連接
```bash
curl http://localhost:8000/api/test-connection
```

### 生成角色
```bash
curl -X POST http://localhost:8000/api/generate-character \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "測試用戶",
    "dream_type": {
      "personality_traits": ["溫柔", "體貼"],
      "talking_style": "溫柔體貼",
      "interests": ["音樂"],
      "age_range": "20-25",
      "occupation": "學生"
    },
    "custom_memory": {
      "likes": {},
      "dislikes": {},
      "habits": {},
      "personal_background": {}
    }
  }'
```

---

## 專案結構快速參考

```
7755/
├── backend/
│   ├── main.py              # FastAPI 應用（啟動入口）
│   ├── api_client.py        # SenseChat API 客戶端
│   ├── character_generator.py  # 角色生成邏輯
│   ├── models.py            # 數據模型
│   └── config.py            # 配置
├── test_api.py              # 測試腳本（重要！）
├── requirements.txt         # 依賴列表
├── .env                     # 環境變數（API 憑證）
└── README.md               # 完整文檔
```

---

## 下一步

完成 Phase 1 測試後，可以開始開發：

- **Phase 2**: 實作完整對話流程和數據庫
- **Phase 3**: 加入好感度系統
- **Phase 4**: 知識庫整合

詳見 `Implementation_Plan.md`

---

**需要幫助？** 檢查 README.md 中的故障排除章節
