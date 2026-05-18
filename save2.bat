@echo off
chcp 65001 > nul
cd "C:\Users\이경태\FastMatMul"
git add .
git commit -m "Auto save: FastMatMul update"
git push origin main
echo FastMatMul 저장 완료
pause