@echo off
echo Ejecute .\dependencies "If u dont do it before"
mkdir bin
cd bin
python -m pyinstaller --noconfirm --onedir --console --icon "..\br256.ico" --name "sm"  "..\__main__.py"
python compile_docs.py
cd ..
echo "compilation finished :D"
pause
