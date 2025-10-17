@echo off
REM Run both Streamlit apps simultaneously for API Integration Demo

echo.
echo ======================================================
echo  🔌 API Integration Demo - Dual Window Setup
echo ======================================================
echo.
echo Starting two Streamlit applications:
echo   1. Guidewire Backend (port 8501)
echo   2. Customer Portal (port 8502)
echo.
echo Arrange the windows side-by-side to see live integration!
echo.
echo ======================================================
echo.

REM Start app_v2.py (Guidewire backend view) on port 8501
start "Guidewire Backend" cmd /k "cd src && %USERPROFILE%\anaconda3\envs\insurance-system\python.exe -m streamlit run app_v2.py --server.port 8501"

REM Wait 3 seconds before starting second app
timeout /t 3 /nobreak > nul

REM Start app_customer_portal.py (Customer view) on port 8502
start "Customer Portal" cmd /k "cd src && %USERPROFILE%\anaconda3\envs\insurance-system\python.exe -m streamlit run app_customer_portal.py --server.port 8502"

echo.
echo ✅ Both applications starting...
echo.
echo 📋 Instructions:
echo   1. Wait for both browser tabs to open
echo   2. In Guidewire Backend tab, select "Case 4: API Integration Demo"
echo   3. In Customer Portal tab, click "Get Free Quote" on any product
echo   4. Watch the Guidewire Backend window show real-time processing!
echo.
echo Press any key to close this window (apps will keep running)...
pause > nul

