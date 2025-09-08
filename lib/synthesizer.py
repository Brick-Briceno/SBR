import numpy as np

# Simplified isophonic curve data (in dB) for a loudness level of 40 phon.
# This is an approximation for illustrative purposes. Actual values ​​are more detailed.
# The key is the frequency in Hz, the value is the loudness level in dB.
ISOPHONIC_CURVE = {
    20: 60, 25: 55, 31.5: 50, 40: 45, 50: 40,
    63: 35, 80: 30, 100: 25, 125: 20, 160: 17,
    200: 15, 250: 13, 315: 12, 400: 10, 500: 9,
    630: 8, 800: 7, 1000: 6, 1250: 5, 1600: 4,
    2000: 4, 2500: 5, 3150: 6, 4000: 7, 5000: 8,
    6300: 9, 8000: 10, 10000: 11, 12500: 12, 16000: 15
}

def create_tone(note_number: int, duration_seconds: float = 1.0,
                SAMPLE_RATE = 44100) -> np.ndarray:
    freq = 440 * 2**((note_number-69) / 12)
    
    # 2. Obtain the amplitude factor of the isophonic curve
    # We use linear interpolation for frequencies not in the dictionary
    keys = sorted(ISOPHONIC_CURVE.keys())

    # Find the two closest frequencies to interpolate
    if freq <= keys[0]:
        db_level = ISOPHONIC_CURVE[keys[0]]
    elif freq >= keys[-1]:
        db_level = ISOPHONIC_CURVE[keys[-1]]
    else:
        i = 0
        while keys[i] < freq:
            i += 1
        
        f1 = keys[i-1]
        f2 = keys[i]
        db1 = ISOPHONIC_CURVE[f1]
        db2 = ISOPHONIC_CURVE[f2]
        
        # Interpolación lineal
        db_level = db1 + (freq - f1) * (db2 - db1) / (f2 - f1)

    # Convertir dB a factor de amplitud. Se usa una referencia de 0 dB para 1.0 de amplitud.
    # El valor 40 fon es la referencia para un nivel de presión sonora de 40 dB SPL
    # a 1000 Hz, que en nuestro modelo es la frecuencia con menor valor dB (6 dB).
    # La normalización se ajusta para que el tono más fuerte (en nuestro modelo)
    # no exceda la amplitud máxima.
    max_db_level = max(ISOPHONIC_CURVE.values()) # dB del tono más bajo, que es el más ruidoso
    amplitude_factor = 10**((db_level - max_db_level) / 20)

    # 3. Generar la onda senoidal
    num_samples = int(duration_seconds * SAMPLE_RATE)
    time_array = np.linspace(0, duration_seconds, num_samples, endpoint=False)
    
    # Onda senoidal pura
    sine_wave = np.sin(2 * np.pi * freq * time_array)

    fade_in_samples = 300
    fade_in = np.linspace(0, 1, fade_in_samples)
    sine_wave[:fade_in_samples] *= fade_in

    fade_out_samples = 300
    fade_out = np.linspace(1, 0, fade_out_samples)
    sine_wave[-fade_out_samples:] *= fade_out

    return sine_wave * amplitude_factor
