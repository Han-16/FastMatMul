@echo off
chcp 65001 > nul
cd "C:\Users\이경태\FastMatMul"
git pull --rebase origin main
echo FastMatMul 업데이트 완료
pause