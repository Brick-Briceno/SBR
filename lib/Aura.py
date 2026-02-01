from scipy.signal import lfilter
#from pygame import mixer
import soundfile as sf
import numpy as np
import time


"""
Aqui se trabaja en 32 bits en estereo por lo general
salvo en funciones muy especificas del modulo


Las automatizaciones son arrays de baja frecuencia retornadas por parametros para esas automatizaciones

"""


SAMPLE_RATE = 44_100

class Aura:
    ...


class WaveTables:
    def silence(samples):
        return np.zeros((samples, 2))

    def seno(samples):
        ...

    def square(samples):
        ...


class Audio_Effects: 
    class Gain_Distortion_Dynamics:
        def float_to_dbs(muestra, reference_value=1):
            # reference_value = 1 #32-bit floating
            valor_pico = np.abs(np.max(muestra))
            db_pico = 20 * np.log10(valor_pico / reference_value)
            return db_pico

        def dbs_to_float(db_pico, reference_value=1):
            valor_pico = reference_value * 10**(db_pico / 20)
            return valor_pico

        def remove_ending_in_silence(audio, umbral=10e-4):
            # Find the last index where the audio exceeds the threshold
            indice_final = np.where(np.abs(audio) > umbral)[0][-1]
            # Trim the audio up to that index
            return audio[:indice_final + 1]

        def valve_distortion(audio_input: np.ndarray, gain=1.2) -> np.ndarray:
            if gain == 0: return audio_input
            # Parameters for a 12AX7 tube model
            # Tube bias voltages
            Vpk = 275  # Plate voltage
            Vgk = -2   # Grid voltage (bias)

            k_p = 600  # Exponent parameter
            k_vb = 300  # Bias voltage
            mu = 100  # Amplification factor
            Ex = 1.4  # Coefficient
            v = 6.3

            # The grid input is the sum of the bias voltage and the audio signal
            # You must scale the audio so it fits within the tube voltage range
            V_audio = audio_input * v  # Adjust this value as needed
            V_total = Vgk + V_audio
            # Compute plate current (Ip) using Koren's formula
            # Avoid division by zero and logs of negative numbers
            V_term = Vpk + Ex * np.log(1 + np.exp(V_total / Ex))
            # Handle the case of log of a negative number
            log_arg = (V_term / mu) - (V_total / gain)
            # Clamp negative values to 0 to avoid log(negative)
            log_arg[log_arg < 0] = 0.0
            Ip = (k_p * np.log(1 + np.exp((k_p * np.log(1 + np.exp(log_arg))) / k_vb)))
            # The distorted output is the plate current
            distorted_audio = Ip / np.max(np.abs(Ip))

            # Normalize so the negative peak is -1 and the positive peak is 1
            max_pos = np.max(distorted_audio)
            min_neg = np.min(distorted_audio)
            # Scale audio to the [-1, 1] range
            distorted_audio = 2 * (distorted_audio - min_neg) / (max_pos - min_neg) - 1
            return distorted_audio


    class Stereo_Expansion:
        def pan_sound(sound, pan_level: float):
            # Ensure the sound has 2 channels
            if sound.shape[1] != 2:
                raise ValueError("Sound must have 2 channels (stereo)")

            # Compute gains for left and right channels
            left_gain = np.sqrt(0.5 * (1 - pan_level))
            right_gain = np.sqrt(0.5 * (1 + pan_level))

            # Apply gains to the channels
            panned_sound = np.zeros_like(sound)
            panned_sound[:, 0] = sound[:, 0] * left_gain  # Left channel
            panned_sound[:, 1] = sound[:, 1] * right_gain  # Right channel
            return panned_sound

        def to_stereo(input_audio):
            # Asegurar que sea estéreo, si es mono lo duplicamos
            if input_audio.ndim == 1:
                input_audio = np.column_stack((input_audio, input_audio))
            return input_audio

        def to_mono(input_audio):
            """
            Converts stereo audio to mono by averaging both channels
            If input is already mono, returns it as is
            """
            if input_audio.ndim == 1:
                return input_audio  # Already mono
            return np.mean(input_audio, axis=1)  # Average L and R channels

        def only_side(input_audio):
            """
            Extracts the side (difference) signal from stereo audio
            Returns a mono signal where L = L - R
            """
            if input_audio.ndim == 1:
                return np.zeros_like(input_audio)  # No side info in mono
            return input_audio[:, 0] - input_audio[:, 1]  # L - R

        def only_L(input_audio):
            """
            Extracts the left channel from stereo audio.
            If input is mono, returns it as is.
            """
            if input_audio.ndim == 1:
                return input_audio  # Return mono as is
            return input_audio[:, 0]  # Return left channel

        def only_R(input_audio):
            """
            Extracts the right channel from stereo audio.
            If input is mono, returns it as is.
            """
            if input_audio.ndim == 1:
                return input_audio  # Return mono as is
            return input_audio[:, 1]  # Return right channel

        def rever(input_audio, room_size=.92, wet_level=.45, dry_level=.55, width=1.5):
            """
            Procesa audio estéreo con reverberación (Algoritmo Schroeder/Moorer).
            Calcula dinámicamente la cola de reverberación para llegar a -80dB.
            """

            # 1. CÁLCULO DE LA COLA (RT80)
            #             
            # Definición de delays base (en muestras)
            comb_delays = [1557, 1617, 1491, 1422]
            
            # Calculamos el delay más largo posible.
            # El canal derecho tiene un extra de 'spread', así que el delay efectivo máximo es:
            # Max Base Delay + (20 * width)
            max_delay_base = max(comb_delays)
            max_effective_delay = max_delay_base + (20 * width)

            # Protección: room_size no puede ser >= 1.0 (feedback infinito)
            safe_room_size = min(room_size, 0.999)

            # FÓRMULA RT80: N = (-4 * delay) / log10(ganancia)
            # Calculamos cuántas muestras tarda en caer la señal a -80dB (0.0001 de amplitud)
            rt80_samples = int(abs((-4 * max_effective_delay) / np.log10(safe_room_size)))
            
            # Agregamos un Buffer de seguridad (20%) para compensar la difusión de los filtros All-Pass
            padding_samples = int(rt80_samples * 1.2)


            # 2. PREPARACIÓN DEL AUDIO

            # Volver a estéreo (usando tu librería externa)
            input_audio = Audio_Effects.Stereo_Expansion.to_stereo(input_audio)
            
            # Generar silencio usando el cálculo dinámico
            # Nota: WaveTables.silence debe devolver un array de ceros con la forma correcta
            silence = WaveTables.silence(padding_samples) 
            
            # Aseguramos que el silencio tenga 2 columnas si el input es estéreo (N, 2)
            if input_audio.ndim == 2 and silence.ndim == 1:
                silence = np.column_stack((silence, silence))
                
            input_audio = np.vstack((input_audio, silence))


            # 3. PROCESAMIENTO DSP

            allpass_delays = [225, 341]
            allpass_gain = 0.7

            # Asegurar que sea estéreo para el procesamiento (N, 2)
            if input_audio.ndim == 1:
                input_audio = np.column_stack((input_audio, input_audio))

            # Inicializar salidas
            output_l = np.zeros_like(input_audio[:, 0])
            output_r = np.zeros_like(input_audio[:, 1])
            channels = [input_audio[:, 0], input_audio[:, 1]]
            outputs = [output_l, output_r]

            for i, channel in enumerate(channels):
                # A. Etapa de Filtros Peine (Paralelo)
                comb_out = np.zeros_like(channel)
                
                # Si es el canal derecho (i=1), aplicamos el spread
                spread_factor = 0 if i == 0 else (20 * width)

                for delay in comb_delays:
                    eff_delay = int(delay + spread_factor)
                    # Llamada a tu librería externa
                    comb_out += Audio_Effects.Filters_Equalization \
                        .comb_filter(channel, eff_delay, safe_room_size)

                # B. Etapa de Filtros Todo-Paso (Serie)
                ap_out = comb_out
                for delay in allpass_delays:
                    eff_delay = int(delay + spread_factor)
                    # Llamada a tu librería externa
                    ap_out = Audio_Effects.Filters_Equalization \
                        .allpass_filter(ap_out, eff_delay, allpass_gain)

                outputs[i] = ap_out
            
            # 4. MEZCLA FINAL
            
            # Escalar la señal Wet para evitar clipping al sumar los peines
            # (El 0.1 original es correcto para evitar saturación tras sumar 4 filtros)
            wet_signal = np.column_stack((outputs[0], outputs[1])) * 0.1
            
            return (input_audio * dry_level) + (wet_signal * wet_level)


    class Tuning_Stretching:
        def vinyl(data, n):
            if not n: return data
            return Audio_Effects.Tuning_Stretching.resampling(data, int(n*sample_rate), sample_rate)

        def resampling(audio_data, sample_rate_old, new_sample_rate):
            # Compute the number of samples for the new sample rate
            ratio = new_sample_rate / sample_rate_old
            num_muestras_nuevo = int(len(audio_data) * ratio)

            # Create original and new indices
            indices_originales = np.arange(len(audio_data))
            indices_nuevos = np.linspace(0, len(audio_data) - 1, num_muestras_nuevo)

            # Interpolate to obtain the resampled audio
            if audio_data.ndim == 1:  # Mono audio
                audio_reesampleado = np.interp(indices_nuevos, indices_originales, audio_data)
            else:  # Stereo or multichannel audio
                audio_reesampleado = np.array([
                    np.interp(indices_nuevos, indices_originales, audio_data[:, i])
                    for i in range(audio_data.shape[1])]).T

            return audio_reesampleado


    class Filters_Equalization:
        def comb_filter(signal, delay_samples, feedback):
            """Creates a comb filter (Comb Filter)"""
            b = np.zeros(delay_samples + 1)
            b[delay_samples] = 1
            a = np.zeros(delay_samples + 1)
            a[0] = 1
            a[delay_samples] = -feedback
            return lfilter(b, a, signal)

        def allpass_filter(signal, delay_samples, gain):
            """Creates an all-pass filter (All-Pass Filter) for diffusion."""
            b = np.zeros(delay_samples + 1)
            b[0] = -gain
            b[delay_samples] = 1
            a = np.zeros(delay_samples + 1)
            a[0] = 1
            a[delay_samples] = -gain
            return lfilter(b, a, signal)


# def play_array(audio_data, sample_rate=44100, sleep=False):
#     """Reproduce un array de audio."""
#     audio_data_int16 = (audio_data * 2**15 * 0.9).astype(np.int16)
#     audio_data_int16 = np.ascontiguousarray(audio_data_int16)
#     sound = mixer.Sound(array=audio_data_int16)
#     sound.play()
#     if sleep:
#         time.sleep((1/sample_rate) * len(audio_data))



def main_test():
    #data, _ = sf.read("music.mp3")
    data, _ = sf.read("yo.wav")
    #data = Audio_Effects.Stereo_Expansion.rever(data, wet_level=1)
    #sf.write("output.flac", data, SAMPLE_RATE)


if __name__ == "__main__":
    main_test()
    ...

