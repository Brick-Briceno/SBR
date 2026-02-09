#!/bin/bash

echo "Installing dependencies..."
chmod +x ./dependencies.sh
#./dependencies.sh

echo "Creating bin directory..."
mkdir -p bin

echo "Building SBR audio engine..."
cd Bsound || exit 1
chmod +x install_audio_engine.sh
bash install_audio_engine.sh
cd ..

# Determine the correct library extension
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    LIB_EXT="dll"
else
    LIB_EXT="so"
fi

    #--onefile \
echo "Building SBR..."
_python -m nuitka \
    --mode=accelerated \
    --enable-plugin=numpy \
    --include-module=soundfile \
    --output-dir=bin \
    --lto=yes \
    --onefile-no-compression \
    --jobs=$(nproc) \
    --include-data-files=Bsound/libaudio_engine.$LIB_EXT=libaudio_engine.$LIB_EXT \
    --windows-icon-from-ico=br256.ico \
    --assume-yes-for-downloads \
    --output-filename=sm \
    --follow-imports \
    --follow-import-to=* \
    __main__.py

echo "Compilation finished! 🎉"
echo "The executable is available in the bin/ directory"
