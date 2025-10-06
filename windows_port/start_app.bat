@echo off
REM 建立虛擬環境並啟動 Rene 的抽獎器

IF NOT EXIST .venv (
    python -m venv .venv
)

CALL .venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM 使用預設 5000 埠啟動，如需修改請改成 python app.py --port 8000
python app.py --host 0.0.0.0 --port 5000
