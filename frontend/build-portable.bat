@echo off
echo ========================================
echo   校修通 - 便携版打包工具
echo ========================================
echo.

:: Step 1: Build frontend
echo [1/3] 构建前端...
call npx vite build --base=./
if errorlevel 1 (
    echo 构建失败！
    pause
    exit /b 1
)
echo 前端构建完成！

:: Step 2: Prepare portable structure
echo [2/3] 准备便携版结构...
if exist "release\校修通" rmdir /s /q "release\校修通"
mkdir "release\校修通"
xcopy /e /y /i "node_modules\electron\dist\*" "release\校修通\" >nul
mkdir "release\校修通\resources\app\dist"
mkdir "release\校修通\resources\app\electron"
xcopy /e /y "dist\*" "release\校修通\resources\app\dist\" >nul
xcopy /e /y "electron\*" "release\校修通\resources\app\electron\" >nul
:: 生成精简的 package.json（Electron 只需要 main 字段）
echo {"main":"electron/main.js","name":"campus-fix","version":"1.0.0"} > "release\校修通\resources\app\package.json"
copy /y "release\校修通\electron.exe" "release\校修通\校修通.exe" >nul
echo 便携版组装完成！

:: Step 3: Create desktop shortcut
echo [3/3] 创建桌面快捷方式...
powershell -Command "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\校修通.lnk');$s.TargetPath='%CD%\release\校修通\校修通.exe';$s.WorkingDirectory='%CD%\release\校修通';$s.Description='校园维修追踪平台';$s.Save()"
echo 桌面快捷方式已创建！

echo.
echo ========================================
echo   打包完成！双击桌面的"校修通"即可启动
echo ========================================
pause
