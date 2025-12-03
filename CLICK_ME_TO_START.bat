@echo off
cls
echo.
echo  ========================================================
echo            CFPB CONSUMER COMPLAINT ANALYSIS
echo  ========================================================
echo.
echo  This will:
echo    1. Stop any running Streamlit apps
echo    2. Start the dashboard with the FIXED code
echo    3. Open it in your browser automatically
echo.
echo  ========================================================
echo.
echo  Starting in 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo  [1/2] Stopping old processes...
taskkill /F /IM streamlit.exe 2>nul
taskkill /F /FI "WINDOWTITLE eq *streamlit*" 2>nul
timeout /t 2 /nobreak >nul

echo  [2/2] Starting fresh dashboard with fixed code...
echo.
echo  ========================================================
echo   YOUR BROWSER WILL OPEN AUTOMATICALLY
echo  ========================================================
echo.
echo   What to do next:
echo   1. Wait for browser to open (10-15 seconds)
echo   2. Look at the sidebar - should say "Quick Analysis"
echo   3. Click "Start Analysis" button
echo   4. Wait 30-60 seconds for results!
echo.
echo  ========================================================
echo   Keep this window open! Press Ctrl+C to stop.
echo  ========================================================
echo.

streamlit run web_dashboard.py

