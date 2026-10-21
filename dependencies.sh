# Necesario
python -m pip install --upgrade pip
python -m pip install soundfile
python -m pip wheel setuptools
python -m pip install numpy
#python -m pip install pygame
python -m pip install keyboard
python -m pip install pygame-ce
python -m pip install scipy

# Para compilar
python -m pip install pyinstaller
python -m pip install -U Nuitka #valen los 2 pero este es recomendado

# Cosas alternativas
python -m pip install numba
python -m pip install briefcase
python -m pip install matplotlib

# Rust (for audio engine)
cd Bsound/audio_engine
cargo add cpal
cd ../..
