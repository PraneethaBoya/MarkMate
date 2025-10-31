@echo off
echo ========================================
echo MarkMate Quick Setup for Render
echo ========================================
echo.
echo This will:
echo 1. Register all users (admin + students)
echo 2. Train the ML model
echo.
echo This takes about 30 seconds...
echo.
pause

cd "%~dp0"

echo.
echo [1/2] Registering users...
python register_remote_users.py

echo.
echo [2/2] Training model...
python train_via_api.py

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now log in at:
echo https://praneethaboya.github.io/MarkMate/login.html
echo.
echo Username: K.Nagaraju
echo Password: IIITDMK
echo.
pause
