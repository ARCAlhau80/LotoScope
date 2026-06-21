@echo off
title LotoScope Dashboard
cd /d "%~dp0dashboard"
echo ========================================
echo   LotoScope Dashboard (Next.js Full-Stack)
echo ========================================
echo.
echo Iniciando servidor em http://localhost:3003
echo.
npx next dev --port 3003
pause
