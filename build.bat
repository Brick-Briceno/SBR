@echo off
echo Ejecute .\dependecies "If u dont do it before"
mkdir bin
cd bin
pyinstaller --noconfirm --onedir --console --icon "..\br256.ico" --name "SBR 2"  "..\__main__.py"
cd ../docs
py compile_docs.py
cd ..
echo "compilation finished :D"
echo "and the documentation too >:D"
pause
