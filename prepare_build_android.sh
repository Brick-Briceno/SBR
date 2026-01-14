#!/bin/bash
set -e

# 1. Actualización e instalación de dependencias del sistema
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv openjdk-17-jdk unzip \
    build-essential libffi-dev libssl-dev autoconf automake libtool \
    python-is-python3 ffmpeg libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev \
    libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev

# 2. Configuración de Java
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 3. Creación del entorno virtual
python3.11 -m venv venv
source venv/bin/activate

# 4. Instalación de herramientas de Python
pip install --upgrade pip setuptools
pip install Cython==0.29.33 buildozer

# 5. Crear buildozer.spec (Asegúrate de que source.dir sea el correcto)
cat > buildozer.spec << 'EOL'
[app]
title = SBR
version = 2.1
package.name = sbrinterpreter
package.domain = org.sbr
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
requirements = python3,kivy==2.3.0

android.api = 33
android.ndk = 25b
android.minapi = 21
orientation = portrait
android.archs = arm64-v8a
android.allow_backup = False
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 0
EOL
