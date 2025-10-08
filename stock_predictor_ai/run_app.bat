@echo off
echo =========================================
echo   🚀 Launching Stock Predictor Dashboard
echo =========================================
cd /d "%~dp0"
python -m streamlit run app.py
pause
