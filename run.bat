@echo off

REM 仮想環境のアクティベート
call venv\Scripts\activate

REM 依存関係のインストール
pip install -r requirements.txt

REM Streamlitアプリの起動
streamlit run app.py --server.port 8501 --server.address localhost