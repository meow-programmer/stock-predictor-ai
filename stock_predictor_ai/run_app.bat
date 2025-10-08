@echo off
cd /d "%~dp0"
echo =========================================
echo   Launching Stock Predictor Dashboard
echo =========================================
start "" streamlit run app.py
exit /b
