@echo off
title CFPB Analysis - Modern Web Dashboard
color 0A
echo.
echo  =====================================================
echo  🏛️  CFPB Consumer Complaint Analytics Dashboard
echo  =====================================================
echo  🚀 Starting Modern Web Interface...
echo  📊 Interactive Charts ^& Beautiful Visualizations
echo  🎯 Real CFPB Data Analysis ^& Comparison Tools
echo  =====================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install Streamlit if needed
echo 📦 Installing required packages...
pip install streamlit plotly pandas numpy requests matplotlib seaborn openpyxl >nul 2>&1

REM Kill any existing Streamlit processes
taskkill /F /IM streamlit.exe >nul 2>&1

echo.
echo 🌐 Launching web dashboard...
echo 📍 Your browser will open automatically
echo 🔗 URL: http://localhost:8501
echo.
echo ⏹️  Press Ctrl+C to stop the server
echo ====================================================
echo.

REM Launch Streamlit
streamlit run web_dashboard.py --server.port 8501 --server.headless false

pause