@echo off
echo ================================================
echo  PSU RACING - QUICK FIX DEPLOYMENT
echo ================================================
echo.
echo This will:
echo 1. Deploy camera test scripts
echo 2. Deploy fixed main script
echo 3. Deploy fixed dashboard files
echo.
pause

echo.
echo [1/5] Deploying basic camera test...
scp pi_scripts\camera_test.py pi@berryspie:~/racing/camera_test.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to deploy camera test!
    pause
    exit /b 1
)

echo.
echo [2/5] Deploying comprehensive camera test...
scp pi_scripts\camera_test_all.py pi@berryspie:~/racing/camera_test_all.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to deploy comprehensive test!
    pause
    exit /b 1
)

echo.
echo [3/5] Deploying SIMPLE version (no recording)...
scp pi_scripts\gps_sync_streamer_SIMPLE.py pi@berryspie:~/racing/gps_sync_streamer.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to deploy main script!
    pause
    exit /b 1
)

echo.
echo [4/5] Deploying dashboard HTML...
scp app\index.html pi@berryspie:~/racing/app/index.html
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to deploy HTML!
    pause
    exit /b 1
)

echo.
echo [5/5] Deploying dashboard JavaScript...
scp app\script.js pi@berryspie:~/racing/app/script.js
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to deploy JavaScript!
    pause
    exit /b 1
)

echo.
echo ================================================
echo  DEPLOYMENT COMPLETE!
echo ================================================
echo.
echo Next steps:
echo 1. SSH into Pi: ssh pi@berryspie
echo 2. Run comprehensive test: python3 ~/racing/camera_test_all.py
echo 3. If camera works, run: cd ~/racing && python3 gps_sync_streamer.py
echo.
echo Dashboard will be at: http://172.20.10.4:8001/app/
echo.
pause
