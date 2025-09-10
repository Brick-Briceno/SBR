@echo off
mkdir bin
echo "pip install pyinstaller"
cd bin
pyinstaller --noconfirm --onedir --console --optimize "2" --icon "..\br256.ico" --name "SBR2"  "..\__main__.py"
cd ..
echo "compilation finished :D"
echo "and now, compile the documentation >:D"
