@echo off
REM ================================================================
REM Launch Script: Guidewire Underwriting Center Demo
REM ================================================================

echo.
echo ================================================================
echo   Guidewire Underwriting Center - Interactive Demo
echo ================================================================
echo.

REM Check if database exists
if not exist "pnc_demo.db" (
    echo [INFO] Database not found. Creating and seeding database...
    cd src
    "%USERPROFILE%\anaconda3\envs\insurance2\python.exe" seed_database.py
    if errorlevel 1 (
        echo [ERROR] Failed to create database.
        pause
        exit /b 1
    )
    cd ..
    echo [SUCCESS] Database created successfully!
    echo.
) else (
    echo [INFO] Database found. Using existing database.
    echo [TIP] To reset database, delete pnc_demo.db and run seed_database.py
    echo.
)

echo [INFO] Launching Underwriting Center...
echo [INFO] App will be available at: http://localhost:8504
echo.
echo ================================================================
echo   DEMO INSTRUCTIONS:
echo   1. Click on "Floor ^& Decor Outlets" (SUB-2026-001)
echo   2. Follow the 15-step demo flow in the README
echo   3. Experience AI-powered underwriting!
echo ================================================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Launch the Underwriting Center app
"%USERPROFILE%\anaconda3\envs\insurance2\python.exe" -m streamlit run underwritingcenter\app_underwriting.py --server.port 8504

pause

