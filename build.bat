@echo off
echo Ejecute .\dependencies "If u dont do it before"
mkdir bin
cd bin
pyinstaller --noconfirm --onefile --console --icon "..\br256.ico" --name "sm"  "..\__main__.py"
cd ..
echo "compilation finished :D"
pause
