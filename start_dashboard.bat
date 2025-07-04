@echo off
chcp 65001 >nul
echo 🚀 서버 로그 분석 대시보드 시작
echo ==========================================
echo.
echo 📊 로그 자동 생성 및 실시간 분석 대시보드
echo 🌐 웹 접속: http://127.0.0.1:5000/
echo.
echo ⏹️ 중단하려면 Ctrl+C를 누르세요
echo ==========================================
echo.

python ServerLogAnalysis/run_dashboard.py

pause 