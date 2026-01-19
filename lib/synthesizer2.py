from scipy.signal import lfilter
from pygame import mixer
import soundfile as sf
import numpy as np
import time


mixer.init()

sample_rate = 44_100

sound = None
def play_array(audio_data, sleep=False):
    #pause()
    # Convertir a int16
    global sound
    audio_data_int16 = (audio_data * 2**15*.9).astype(np.int16)
    audio_data_int16 = np.ascontiguousarray(audio_data_int16)
    # Reproducir el audio
    sound = mixer.Sound(array=audio_data_int16)
    sound.play()
    #Thread(target=sa.play_buffer, args=(audio_data_int16, 2, 2, sample_rate)).start()
    if sleep: time.sleep((1/sample_rate)*len(audio_data))



class StereoReverb:
    def __init__(self, sample_rate=44100, room_size = 0.8, wet_level = 0.3, dry_level = 0.7):
        self.fs = sample_rate
        self.room_size = np.clip(room_size, 0.0, 0.98)
        self.wet_level = np.clip(mix, 0.0, 1.0)
        self.dry_level = dry_level
        self.width = 1.0 # stereo

        # Tiempos de retardo base (en muestras) basados en números primos 
        # para evitar resonancias metálicas (diseño clásico de Schroeder)
        self._comb_delays = [1557, 1617, 1491, 1422]
        self._allpass_delays = [225, 341]
        self._allpass_gains = 0.7

    def _create_comb_filter(self, signal, delay_samples, feedback):
        """
        Crea un filtro peine (Comb Filter).
        y[n] = x[n - D] + g * y[n - D]
        """
        # Coeficientes para scipy.lfilter
        # Numerador (b): Retrasamos la entrada D muestras
        b = np.zeros(delay_samples + 1)
        b[delay_samples] = 1

        # Denominador (a): Feedback en la muestra D
        a = np.zeros(delay_samples + 1)
        a[0] = 1
        a[delay_samples] = -feedback

        return lfilter(b, a, signal)

    def _create_allpass_filter(self, signal, delay_samples, gain):
        """
        Crea un filtro todo-paso (All-Pass Filter) para difusión
        y[n] = -g * x[n] + x[n - D] + g * y[n - D]
        """
        b = np.zeros(delay_samples + 1)
        b[0] = -gain
        b[delay_samples] = 1

        a = np.zeros(delay_samples + 1)
        a[0] = 1
        a[delay_samples] = -gain

        return lfilter(b, a, signal)


    def process(self, input_audio):
        """
        Procesa el audio estéreo
        input_audio: numpy array de forma (samples, 2)
        """
        # Asegurar que sea estéreo, si es mono lo duplicamos
        if input_audio.ndim == 1:
            input_audio = np.column_stack((input_audio, input_audio))

        output_l = np.zeros_like(input_audio[:, 0])
        output_r = np.zeros_like(input_audio[:, 1])

        # Procesamiento independiente por canal para mantener imagen estéreo
        channels = [input_audio[:, 0], input_audio[:, 1]]
        outputs = [output_l, output_r]

        for i, channel in enumerate(channels):
            # 1. Etapa de Filtros Peine (Paralelo)
            comb_out = np.zeros_like(channel)

            # Aplicamos un pequeño "spread" (desviación) en los tiempos de retardo
            # para el canal derecho, creando amplitud estéreo.
            spread_factor = 0 if i == 0 else (20 * self.width) # +20 muestras para el canal R

            for delay in self._comb_delays:
                eff_delay = int(delay + spread_factor)
                comb_out += self._create_comb_filter(channel, eff_delay, self.room_size)

            # 2. Etapa de Filtros Todo-Paso (Serie)
            # Esto suaviza la reverberación
            ap_out = comb_out
            for delay in self._allpass_delays:
                eff_delay = int(delay + spread_factor)
                ap_out = self._create_allpass_filter(ap_out, eff_delay, self._allpass_gains)

            outputs[i] = ap_out

        # 3. Mezcla Wet/Dry
        wet_signal = np.column_stack((outputs[0], outputs[1]))

        # Normalización de seguridad para evitar clipping masivo por la suma de filtros
        wet_signal = wet_signal * 0.1
        final_output = (input_audio * self.dry_level) + (wet_signal * self.wet_level)

        return final_output


data, sample_rate = sf.read("prueba.wav")
data = np.concatenate((data, np.zeros((44100 * 10, 2))), axis=0)

reverb = StereoReverb(sample_rate=sample_rate)
reverb.set_parameters(
    room_size=0.92,
    mix=0.45,
    width=1.5
    )

wet_audio = reverb.process(data)
play_array(wet_audio, sleep=True)
