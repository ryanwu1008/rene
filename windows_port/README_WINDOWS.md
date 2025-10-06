# Rene 抽獎器（Windows 版）

這個資料夾包含在 Windows 10/11 上部署與執行的最小專案。使用前請確認已安裝：

- [Python 3.9 以上（64-bit）](https://www.python.org/downloads/windows/)（安裝時勾選 *Add Python to PATH*）
- 額外的 Visual C++ 14.0 以上編譯工具（若安裝 PyTorch 失敗，請安裝 [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/)）

## 快速開始

1. **下載專案**  
   將整個 `windows_port` 資料夾複製到 Windows 電腦，例如 `C:\ReneDraw`。

2. **建立虛擬環境並安裝套件**  
   開啟 *Windows Terminal* 或 *PowerShell*，進入資料夾：
   ```powershell
   cd C:\ReneDraw\windows_port
   .\start_app.bat
   ```
   首次執行會：
   - 建立 `.venv` 虛擬環境
   - 安裝所需套件（Flask、EasyOCR、PyTorch 等）
   - 啟動 Flask 伺服器（預設 5000 埠）

3. **開啟網站**  
   瀏覽器前往 `http://127.0.0.1:5000/`（若 Batch 指令改了埠號，請跟著調整）。
   - 第一次啟動 EasyOCR 會下載權重，需要一些時間。
   - 若顯示埠號被占用，可修改 `start_app.bat` 最後一行，例如 `python app.py --port 5050`。

4. **重新啟動**  
   之後要再次啟動時，直接執行：
   ```powershell
   cd C:\ReneDraw\windows_port
   .\.venv\Scripts\activate
   python app.py --port 5000
   ```

## 常見問題

- **PyTorch 安裝失敗**：請確認已安裝 Visual C++ Build Tools，或改用 CPU 版輪子（批次檔會自動從 PyPI 安裝最新 CPU 版）。
- **OCR 速度慢**：EasyOCR 目前使用 CPU 推論，如有 GPU 可額外安裝 CUDA 版本的 torch，並將 `app.py` 內 `easyocr.Reader([...], gpu=False)` 改為 `gpu=True`。
- **想要部署到雲端**：可將 `windows_port` 裡的檔案推到 GitHub，並依照 Render / Railway 等平台的 Python Web Service 指南進行部署。

## 資料夾結構

```
windows_port
├── app.py
├── comment_sampler.py
├── requirements.txt
├── start_app.bat
├── static
│   ├── app.js
│   └── styles.css
└── templates
    ├── base.html
    └── index.html
```

祝你在 Windows 上也能輕鬆完成抽獎活動！
