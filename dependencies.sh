# Necesario
pip install --upgrade pip
pip wheel setuptools
pip install numpy
pip install soundfile

# Para compilar
pip install pyinstaller
pip install -U Nuitka #valen los 2 pero este es recomendado


# Cosas alternativas
pip install numba
pip install kivy

# Rust (for audio engine)
cd Bsound/audio_engine
cargo add cpal
cd ../..
