@echo off
title LotoScope Dashboard Server
cd /d "%~dp0dashboard"
npx next dev --port 3003 -H 0.0.0.0