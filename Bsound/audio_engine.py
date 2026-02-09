import soundfile as sf
import numpy as np
import ctypes
import os


LIB_FILE_NAME = "Bsound/audio_engine"

lib_extension = ".os"
if os.name == "nt":
    lib_extension = ".dll"


lib_path = os.path.abspath(LIB_FILE_NAME + lib_extension)
lib = ctypes.CDLL(lib_path)

lib.play_audio_ptr.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_size_t, ctypes.c_uint32]
lib.set_volume.argtypes = [ctypes.c_float]
lib.set_volume.restype = None
lib.get_volume.argtypes = []
lib.get_volume.restype = ctypes.c_float


#lib.set_volume(1)
lib.get_volume()
#print(current_volume)

# Cargar audio
data, samplerate = sf.read("music.mp3", dtype="float32")
data = np.ascontiguousarray(data, dtype=np.float32).flatten()

# Obtener el puntero del array de NumPy
data_ptr = data.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
print(dir(lib))
lib.play_audio_ptr(data_ptr, data.size, samplerate)
