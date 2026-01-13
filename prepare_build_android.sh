#!/bin/bash
set -e

# 1. Instalación de dependencias del sistema (ESTO SÍ REQUIERE SUDO)
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev openjdk-17-jdk unzip \
    build-essential libffi-dev libssl-dev autoconf automake libtool

# 2. Configurar JAVA_HOME
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# 3. Preparar entorno virtual (SIN SUDO)
python3.11 -m venv venv

source venv/bin/activate

# 4. Instalar herramientas de Python
pip install --upgrade pip
pip install Cython==0.29.33  # Versión más estable para Kivy/Buildozer
pip install buildozer

# 5. Crear buildozer.spec con la corrección de python3
cat > buildozer.spec << 'EOL'
[app]
title = SBR
package.name = sbrinterpreter
package.domain = org.sbr
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 2.1
requirements = python3,kivy
android.permissions = INTERNET
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
log_level = 2
EOL
