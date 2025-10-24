# 在 Windows 上運行專案

由於 WSL 環境限制，建議直接在 Windows 上運行此專案。

## 方法 1: 使用 Windows 命令提示字元 (推薦)

### 1. 打開命令提示字元 (CMD)
- 按 `Win + R`
- 輸入 `cmd`
- 按 Enter

### 2. 切換到專案目錄
```cmd
cd C:\Users\Administrator\Desktop\7755
```

### 3. 檢查 Python 安裝
```cmd
python --version
```

如果顯示 Python 版本（建議 3.8+），繼續下一步。
如果提示找不到 Python，請先安裝：https://www.python.org/downloads/

### 4. 安裝依賴
```cmd
python -m pip install -r requirements.txt
```

### 5. 運行測試
```cmd
python test_api.py
```

### 6. 啟動開發服務器
```cmd
python -m uvicorn backend.main:app --reload
```

### 7. 訪問網頁
打開瀏覽器訪問：
```
http://localhost:8000/ui
```

---

## 方法 2: 使用 PowerShell

### 1. 打開 PowerShell
- 按 `Win + X`
- 選擇 "Windows PowerShell"

### 2. 切換到專案目錄
```powershell
cd C:\Users\Administrator\Desktop\7755
```

### 3. 運行設置腳本
```powershell
python -m pip install -r requirements.txt
```

### 4. 運行測試
```powershell
python test_api.py
```

### 5. 啟動服務器
```powershell
python -m uvicorn backend.main:app --reload
```

---

## 方法 3: 使用雙擊腳本

我已經創建了方便的批次檔：

1. **安裝依賴**: 雙擊 `setup.bat`
2. **運行測試**: 雙擊 `run_test.bat`（即將創建）
3. **啟動服務器**: 雙擊 `run_server.bat`（即將創建）

---

## 常見問題

### Q: 提示 "python 不是內部或外部命令"
**A**: Python 未安裝或未加入 PATH
1. 下載 Python: https://www.python.org/downloads/
2. 安裝時勾選 "Add Python to PATH"

### Q: pip 安裝失敗
**A**: 嘗試升級 pip
```cmd
python -m pip install --upgrade pip
```

### Q: ModuleNotFoundError
**A**: 依賴未正確安裝
```cmd
python -m pip install -r requirements.txt --user
```

### Q: 端口 8000 被佔用
**A**: 使用其他端口
```cmd
python -m uvicorn backend.main:app --reload --port 8080
```
然後訪問 http://localhost:8080/ui

---

## 預期測試結果

運行 `python test_api.py` 後，你應該看到：

```
🚀 開始測試 Dating Chatbot - Phase 1

============================================================
測試 API 連接...
============================================================
✅ API 連接成功！

============================================================
測試角色生成...
============================================================

角色名稱: 小雨
暱稱: 雨雨
性別: 女
身份: 22-25歲，學生，甜美可愛，喜歡音樂

詳細設定:
性格溫柔體貼，說話輕聲細語，總是關心對方的感受...

✅ 角色生成成功！

============================================================
測試與角色對話...
============================================================

👤 小明: 你好！很高興認識你
💕 小雨: 你好！我也很高興認識你...

✅ 對話測試完成！

============================================================
✅ 所有測試完成！
============================================================
```

---

## 啟動服務器後

訪問 http://localhost:8000/ui 你會看到：

1. **歡迎頁面** - 紫色漸變背景
2. **輸入表單** - 4步驟引導
3. **角色生成** - 自動生成你的AI伴侶
4. **對話介面** - 即時聊天

---

**如有問題，請查看 README.md 或 QUICKSTART.md**
