"""
Aura Synthesizer
By @Brick_briceño 2025

About:
This module typically works with 32-bit stereo audio
unless specified otherwise in specific module functions

Automations are low-frequency arrays returned as parameters for those automations

Presets can be stored in JSON format for easy modification
Gzip converts them to binary, while Base64 (and Gzip) converts them into a string,
allowing them to be sent via message or posted on forums and social media

This is an SBR module, so Aura knows nothing about BPM, scales, or note durations,
It doesn't know whether it is in monophonic or polyphonic mode, nor does it know the tuning,
Temperament or the specific frequency to which it is tuned—the SBR and Bsound core handles all of that

"""

preset_example = {
    "meta": {
        "version": "1.0.0",
        "name": "Example Preset",
        "description": "An example preset for demonstration purposes",
        "author": "Brick Briceño",
        "category": "Bass",
        "tags": ["resampling", "distorted", "sub"],
        "description": "Heavy wavetable bass with OTT style dynamics and fast LFO",
        },

    "global": {
        "master_gain_db": -0.1,
        "legato": True,
        "glide": True,
        "portamento": .045, #this is the time in seconds for the glide effect
        "effects": {
            # Añadimos compresion
            "la2a": {
                "peak_reduction": 50.0,
                "gain": 50.0,
                "mode": "compress"
            },
            "reverb": {
                "room_size": 0.92,
                "wet_level": 0.35,
                "dry_level": 0.65,
                "width": 1.2
            }
        }
    },

    # Variables (They can be used as parameters for automations, LFOs, and envelopes)
    # dentro de las variables puedes usar operadores matemáticos crear modulación compleja

    # "note_hz", ejemplo: "note_hz * 2" para una octava arriba

    # "note_number", ejemplo: "note_number + 12" para una octava arriba
    # Tambien puede ser usado para controlar la intensidad de un parametro
    # Por ejemplo si quieres que haya menos harmonicos en los agudos
    # Puedes usar "note_number / 127" para controlar la cantidad de harmonicos

    # "duration" es una cosntante cuanto dura expresado en segundos
    # "duration_progress" te sirve por ejemplo para conectarlo al vobrato
    # mientas avanza la nota, el vobrato se va haciendo mas intenso, va de (0 a 100)

    # "velocity" pones esta variable despues de un "1-" y lo conectas al attak del ADSR
    # sonará más suave si tocas más despacio y más fuerte si tocas duro, como un instrumento real
    # "1-velocity" (va de 1 a 0) y no a la inversa

    # "portamento" (va de 0 a 1) en lo que tarda en completar el glide

    "data": {
        # los osciladores, envolventes ADSR y LFOs se definen en este diccionario
        #Solo hay 2 tipos de datos, numeros y arrays
        # Y todos son validos en todas las entradas de efectos, osciladores y LFOs
        1: {
            "waveform": "sawtooth",
            "frequency": "note_hz",
            "amplitude": 0.8,
            "stretch": 0.0,
        },
    },
    "out": [1, 2, 3]
}


from scipy.signal import lfilter, resample_poly
import soundfile as sf
from numba import njit
import numpy as np
import base64
import time
import gzip
import json



SAMPLE_RATE = 44_100

# Simplified isophonic curve data (in dB) for a loudness level of 40 phon
# This is an approximation for illustrative purposes. Actual values ​​are more detailed
# The key is the frequency in Hz, the value is the loudness level in dB
ISOPHONIC_CURVE = {
    20: 60, 25: 55, 31.5: 50, 40: 45, 50: 40,
    63: 35, 80: 30, 100: 25, 125: 20, 160: 17,
    200: 15, 250: 13, 315: 12, 400: 10, 500: 9,
    630: 8, 800: 7, 1000: 6, 1250: 5, 1600: 4,
    2000: 4, 2500: 5, 3150: 6, 4000: 7, 5000: 8,
    6300: 9, 8000: 10, 10000: 11, 12500: 12, 16000: 15
}

class WaveTables:
    def _phase(samples, frequency):
        frequencies = np.asarray(frequency)
        if frequencies.ndim == 0:
            t = np.linspace(0, samples / SAMPLE_RATE, samples, endpoint=False)
            return 2 * np.pi * frequencies * t
        if frequencies.ndim != 1:
            raise ValueError("frequency must be a scalar or a one-dimensional array")
        if len(frequencies) != samples:
            raise ValueError("frequency array must have one value per sample")

        phase = np.zeros(samples)
        if samples > 1:
            phase[1:] = np.cumsum(frequencies[:-1])
        return 2 * np.pi * phase / SAMPLE_RATE

    def _stretch_values(samples, stretch):
        values = np.asarray(stretch)
        if values.ndim > 1 or (values.ndim == 1 and len(values) != samples):
            raise ValueError("stretch must be a scalar or have one value per sample")
        if not np.all(np.isfinite(values)) or np.any(values < 0):
            raise ValueError("stretch must contain finite, non-negative values")
        return values

    def _stretched_harmonics(samples, frequency, amplitude, stretch, waveform):
        frequencies = np.asarray(frequency)
        if frequencies.ndim > 1 or (
            frequencies.ndim == 1 and len(frequencies) != samples
        ):
            raise ValueError("frequency must be a scalar or have one value per sample")
        if samples == 0:
            return np.zeros(0)

        max_frequency = np.max(np.abs(frequencies))
        if max_frequency == 0:
            return np.zeros(samples)

        result = np.zeros(samples)
        nyquist = SAMPLE_RATE / 2
        waveform = str(waveform).lower()
        harmonic_limit = min(256, int(nyquist / max_frequency))
        for harmonic in range(1, harmonic_limit + 1):
            partial_frequency = harmonic * frequencies * np.sqrt(
                (1 + stretch * harmonic**2) / (1 + stretch)
            )
            if np.max(np.abs(partial_frequency)) >= nyquist:
                break

            if waveform == "square":
                if harmonic % 2 == 0:
                    continue
                coefficient = 4 / (np.pi * harmonic)
            elif waveform == "triangle":
                if harmonic % 2 == 0:
                    continue
                coefficient = (8 / (np.pi**2)) * ((-1) ** ((harmonic - 1) // 2)) / (harmonic**2)
            else:
                coefficient = (2 / np.pi) * ((-1) ** (harmonic + 1)) / harmonic

            result += coefficient * np.sin(
                WaveTables._phase(samples, partial_frequency)
            )

        peak = np.max(np.abs(result))
        if peak > 0:
            result = result * (amplitude / peak)
        return result

    def silence(samples):
        return np.zeros((samples, 2))

    def noise(samples, amplitude=1.0):
        rng = np.random.default_rng()
        data = rng.normal(0.0, amplitude, size=samples)
        return data

    def sine(samples, frequency=440, amplitude=1.0):
        return np.sin(WaveTables._phase(samples, frequency)) * amplitude

    def square(samples, frequency=440, amplitude=1.0, stretch=0.0):
        stretch = WaveTables._stretch_values(samples, stretch)
        if np.any(stretch):
            return WaveTables._stretched_harmonics(
                samples, frequency, amplitude, stretch, "square"
            )
        return np.sign(np.sin(WaveTables._phase(samples, frequency))) * amplitude

    def sawtooth(samples, frequency=440, amplitude=1.0, stretch=0.0):
        stretch = WaveTables._stretch_values(samples, stretch)
        if np.any(stretch):
            return WaveTables._stretched_harmonics(
                samples, frequency, amplitude, stretch, "sawtooth"
            )
        phase = WaveTables._phase(samples, frequency)
        return (2 * (phase / (2 * np.pi) - np.floor(0.5 + phase / (2 * np.pi)))) * amplitude


    def triangle(samples, frequency=440, amplitude=1.0, stretch=0.0):
        stretch = WaveTables._stretch_values(samples, stretch)
        if np.any(stretch):
            return WaveTables._stretched_harmonics(
                samples, frequency, amplitude, stretch, "triangle"
            )
        phase = WaveTables._phase(samples, frequency)
        return (2 * np.abs(2 * (phase / (2 * np.pi) - np.floor(0.5 + phase / (2 * np.pi)))) - 1) * amplitude

    def sample(path):
        data, samplerate = sf.read(path, dtype="float32", always_2d=True)
        if samplerate != SAMPLE_RATE:
            divisor = np.gcd(samplerate, SAMPLE_RATE)
            data = resample_poly(
                data, SAMPLE_RATE // divisor, samplerate // divisor, axis=0
            )
        if data.shape[1] == 1:
            data = np.repeat(data, 2, axis=1)
        elif data.shape[1] > 2:
            raise ValueError("Audio file must be mono or stereo")
        return data

class Audio_Effects:
    class Gain_Distortion_Dynamics:
        def float_to_dbs(sample, reference_value=1):
            # reference_value = 1 #32-bit floating
            peak_value = np.abs(np.max(sample))
            peak_db = 20 * np.log10(peak_value / reference_value)
            return peak_db

        def dbs_to_float(peak_db, reference_value=1):
            peak_value = reference_value * 10**(peak_db / 20)
            return peak_value

        def remove_ending_in_silence(audio, threshold=10e-4):
            # Find the last index where the audio exceeds the threshold
            final_index = np.where(np.abs(audio) > threshold)[0][-1]
            # Trim the audio up to that index
            return audio[:final_index + 1]

        def bit_crush(
            audio_input: np.ndarray,
            bit_depth=8,
            mix_wet=1,
            sample_rate_reduction=1,
        ) -> np.ndarray:
            """Reduce bit depth and hold samples to lower the effective sample rate

            Each parameter can be a scalar or a one-dimensional array with one
            value per audio frame. ``sample_rate_reduction=4`` captures a new
            frame every four input frames while preserving the input length
            """
            audio = np.asarray(audio_input)
            if audio.ndim not in (1, 2):
                raise ValueError("audio_input must be mono or have shape (frames, channels)")

            frame_count = audio.shape[0]

            def parameter_values(
                name, value, minimum, maximum=None, nearest_even=False
            ):
                try:
                    values = np.asarray(value, dtype=float)
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"{name} must contain numeric values") from exc
                if values.ndim > 1 or (
                    values.ndim == 1 and len(values) != frame_count
                ):
                    raise ValueError(
                        f"{name} must be a scalar or have one value per audio frame"
                    )
                if not np.all(np.isfinite(values)):
                    raise ValueError(f"{name} must contain finite values")
                if nearest_even:
                    values = np.maximum(2, np.rint(values / 2) * 2)
                if np.any(values < minimum) or (
                    maximum is not None and np.any(values > maximum)
                ):
                    bounds = f"{minimum} to {maximum}" if maximum is not None else f"at least {minimum}"
                    raise ValueError(f"{name} must be {bounds}")
                return np.broadcast_to(values, (frame_count,))

            depths = parameter_values("bit_depth", bit_depth, 2, nearest_even=True)
            wet_mix = parameter_values("mix_wet", mix_wet, 0, 1)
            reduction = parameter_values(
                "sample_rate_reduction", sample_rate_reduction, 1
            )

            if np.all(depths >= 32) and np.all(reduction == 1):
                return audio_input

            depth_scale = np.exp2(np.minimum(depths, 32) - 1) - 1
            if audio.ndim == 2:
                depth_scale = depth_scale[:, np.newaxis]
            quantized = np.round(
                np.clip(audio, -1.0, 1.0) * depth_scale
            ) / depth_scale
            quantized = np.where(
                (depths >= 32).reshape(
                    (frame_count,) + (1,) * (audio.ndim - 1)
                ),
                audio,
                quantized,
            )

            held_audio = np.empty_like(quantized, dtype=np.result_type(quantized, float))
            phase = 1.0
            held_frame = None
            for frame in range(frame_count):
                if phase >= 1.0 - 1e-12:
                    held_frame = quantized[frame]
                    phase = max(0.0, phase - 1.0)
                held_audio[frame] = held_frame
                phase += 1.0 / reduction[frame]

            if audio.ndim == 2:
                wet_mix = wet_mix[:, np.newaxis]
            return wet_mix * held_audio + (1 - wet_mix) * audio


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

        def _t4_cell_and_tube_dsp(audio, peak_reduction_knob, gain_knob, ratio):
            """
            Bucle DSP compilado en C (vía Numba) para procesar el audio muestra por muestra
            Emula la celda óptica T4 y la etapa de amplificación 12AX7
            """
            n_samples = audio.shape[0]
            n_channels = audio.shape[1] if audio.ndim > 1 else 1
            if n_channels not in (1, 2):
                raise ValueError("Audio debe ser mono o estéreo")

            output = np.zeros_like(audio)
            
            # 1. Ajuste de controles (0 - 100)
            # Peak Reduction incrementa la ganancia del sidechain contra un umbral fijo interno
            sc_gain = 10.0 ** ((peak_reduction_knob - 50.0) / 20.0)
            # Gain controla el makeup de salida (0 a ~40 dB)
            makeup_linear = 10.0 ** ((gain_knob * 0.4) / 20.0)
            
            # Parámetros internos del LA-2A
            THRESHOLD_DB = -24.0
            
            # 2. Constantes de tiempo de la Celda T4 (Filtros RC)
            # Ataque promediado en 10ms
            alpha_A = np.exp(-1.0 / (SAMPLE_RATE * 0.010)) 
            # La fotocelda CdS tiene un release de dos etapas:
            # 50% de recuperación en ~60ms (rápido)
            alpha_R_fast = np.exp(-1.0 / (SAMPLE_RATE * 0.060))
            # El resto de la recuperación toma de 1 a 15 segundos (dependiente del programa)
            # Usaremos 2.5 segundos como promedio representativo del efecto de memoria
            alpha_R_slow = np.exp(-1.0 / (SAMPLE_RATE * 2.500))
            
            env_fast = 0.0
            env_slow = 0.0
            
            # Offset para saturación asimétrica (Emulación básica de armónicos pares del triodo 12AX7)
            tube_bias = 0.15 
            bias_compensation = np.tanh(tube_bias)
            
            for i in range(n_samples):
                # Detección de nivel (Enlazado estéreo si hay más de 1 canal)
                if n_channels == 2:
                    sc_level = max(np.abs(audio[i, 0]), np.abs(audio[i, 1])) * sc_gain
                else:
                    sc_level = np.abs(float(audio[i])) * sc_gain

                sc_level = max(sc_level, 1e-9)  # Evitar log(0)
                sc_db = 20.0 * np.log10(sc_level)
                
                # Cálculo del objetivo de reducción de ganancia
                if sc_db > THRESHOLD_DB:
                    target_gr = (sc_db - THRESHOLD_DB) * (1.0 - 1.0/ratio)
                else:
                    target_gr = 0.0
                    
                # 3. Seguidor de envolvente (Envelope Follower) de la celda T4
                # Ataque
                if target_gr > env_fast:
                    env_fast = alpha_A * env_fast + (1.0 - alpha_A) * target_gr
                else:
                    # Release rápido (primer 50%)
                    env_fast = alpha_R_fast * env_fast + (1.0 - alpha_R_fast) * target_gr
                    
                if target_gr > env_slow:
                    env_slow = alpha_A * env_slow + (1.0 - alpha_A) * target_gr
                else:
                    # Release lento (memoria lumínica para el 50% restante)
                    env_slow = alpha_R_slow * env_slow + (1.0 - alpha_R_slow) * target_gr
                    
                # La suma de ambas envolventes promediadas genera la curva de caída dual óptica
                current_gr_db = 0.5 * env_fast + 0.5 * env_slow
                
                # Convertir reducción en dB a ganancia lineal
                gain_reduction_linear = 10.0 ** (-current_gr_db / 20.0)
                
                    # 4. Aplicar ganancia y pasar por la etapa de tubos (12AX7)
                if n_channels == 2:
                    for c in range(n_channels):
                        sample = audio[i, c] * gain_reduction_linear * makeup_linear
                        tube_out = np.tanh(sample + tube_bias) - bias_compensation
                        output[i, c] = tube_out
                else:
                    sample = float(audio[i]) * gain_reduction_linear * makeup_linear
                    tube_out = np.tanh(sample + tube_bias) - bias_compensation
                    output[i] = tube_out
                        
            return output

        def compressor_la2a(audio, peak_reduction=50.0, gain=50.0, mode='compress'):
            """
            LA-2A style compression processor

            Parameters:
            - peak_reduction: (0-100) controls how much compression is applied
            - gain: (0-100) output make-up gain
            - mode: 'compress' (~3:1 ratio) or 'limit' (~10:1 ratio)
            """

            # Configure mode
            ratio = 3.0 if mode == 'compress' else 10.0

            # Apply the compiled DSP stage
            audio_procesado = Audio_Effects.Gain_Distortion_Dynamics._t4_cell_and_tube_dsp(
                audio, peak_reduction, gain, ratio)

            return audio_procesado

        @njit
        def _1176_analog_core(audio_in, input_gain_lin, output_gain_lin, att_coef, rel_coef, ratio, thresh_db):
            """
            Núcleo del 1176 iterando muestra por muestra
            Incluye bucle Feedback, asimetría FET y distorsión de Transformador (Histéresis)
            """
            out = np.zeros_like(audio_in)
            
            env = 0.0  # Estado de la reducción de ganancia (dB)
            feedback_sample = 0.0  # Memoria del detector (Z^-1)
            transformer_state = 0.0  # Memoria del núcleo magnético del transformador
            
            for i in range(len(audio_in)):
                # 1. Drive de Entrada
                x = audio_in[i] * input_gain_lin
                
                # 2. Detección Feedback (Lee la salida del FET del ciclo anterior)
                # Añadimos offset de 0.001 para emular el bias DC del circuito detector
                detector_signal = abs(feedback_sample + 0.001) 
                x_db = 20.0 * np.log10(detector_signal + 1e-12) if detector_signal > 1e-12 else -120.0
                
                # 3. Target de Reducción de Ganancia (GR)
                if x_db > thresh_db:
                    gr_target_db = (x_db - thresh_db) * (1.0 - (1.0 / ratio))
                else:
                    gr_target_db = 0.0
                    
                # 4. Envolvente (Program-Dependent)
                delta = gr_target_db - env
                if delta > 0:
                    env += att_coef * delta  # Ataque
                else:
                    # Release dinámico: Suelta más lento si hay mucha compresión acumulada
                    dynamic_rel = rel_coef * (1.0 - (min(env, 40.0) / 40.0) * 0.1) 
                    env += dynamic_rel * delta
                    
                # 5. Aplicar GR lineal sobre la señal de entrada
                gr_linear = 10.0 ** (-env / 20.0)
                x_comp = x * gr_linear
                
                # Guardamos la muestra comprimida para el próximo ciclo del detector
                feedback_sample = x_comp 
                
                # 6. Etapa FET: Ganancia y Saturación Asimétrica (Armónicos pares)
                x_out = x_comp * output_gain_lin
                asym_drive = x_out + 0.15 * (x_out ** 2) 
                fet_out = np.tanh(asym_drive)
                
                # 7. Etapa Transformador de Salida (UTC 5002 - Histéresis y Filtro pasabajos natural)
                diff = fet_out - transformer_state
                # Curva de saturación magnética
                non_linear_drive = np.tanh(diff * 1.2) + 0.05 * (diff ** 2)
                transformer_state = transformer_state + 0.5 * non_linear_drive
                
                out[i] = transformer_state
                
            return out

        def urei_1176_analog(audio_in, fs=44100, input_db=12.0, output_db=-6.0, 
                            attack_ms=0.2, release_ms=300.0, ratio=4.0, 
                            all_buttons_in=False, oversampling=8):
            """
            Controlador principal del 1176 con Oversampling anti-aliasing
            
            Parámetros:
            - audio_in: Array de numpy (mono o procesar canales por separado)
            - oversampling: 1 (Off), 2, 4, u 8. (4x recomendado para distorsión analógica sin aliasing).
            """
            
            # 1. Configuración de parámetros analógicos
            if all_buttons_in:
                ratio = 100.0 
                attack_ms = 0.02 
                input_db += 6.0 # Empuje masivo interno
                
            threshold_db = -24.0 # Umbral fijo interno
            
            input_gain_lin = 10.0 ** (input_db / 20.0)
            output_gain_lin = 10.0 ** (output_db / 20.0)
            
            # 2. OVERSAMPLING (Subir la frecuencia de muestreo)
            if oversampling > 1:
                # resample_poly aplica un filtro FIR anti-aliasing automático de altísima calidad
                audio_up = resample_poly(audio_in, oversampling, 1)
                fs_up = fs * oversampling
            else:
                audio_up = audio_in
                fs_up = fs
                
            # Calcular coeficientes IIR usando el sample rate interno (fs_up)
            att_coef = 1.0 - np.exp(-1.0 / (fs_up * (attack_ms / 1000.0)))
            rel_coef = 1.0 - np.exp(-1.0 / (fs_up * (release_ms / 1000.0)))
            
            # 3. Procesamiento en C-Speed
            processed_up = Audio_Effects.Gain_Distortion_Dynamics._1176_analog_core(audio_up, fs_up, input_gain_lin, output_gain_lin, 
                                            att_coef, rel_coef, ratio, threshold_db)
                                            
            # 4. DOWNSAMPLING (Bajar de vuelta a fs original limpiando frecuencias ultrasónicas)
            if oversampling > 1:
                processed = resample_poly(processed_up, 1, oversampling)
            else:
                processed = processed_up
                
            # Limitar salida estricta a [-1.0, 1.0] para evitar clipeo digital al exportar
            return np.clip(processed, -1.0, 1.0)

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
            # Ensure the audio is stereo, if mono duplicate the channel
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
            Extracts the side channel from stereo audio
            """
            if input_audio.ndim == 1:
                raise ValueError("Input audio must be stereo to extract side channel")

            return Audio_Effects.Stereo_Expansion.to_stereo(
                input_audio) - Audio_Effects.Stereo_Expansion.to_mono(
                    input_audio)[:, np.newaxis]

        def only_L(input_audio):
            """
            Extracts the left channel from stereo audio
            If input is mono, returns it as is
            """
            if input_audio.ndim == 1:
                return input_audio  # Return mono as is
            return input_audio[:, 0]  # Return left channel

        def only_R(input_audio):
            """
            Extracts the right channel from stereo audio
            If input is mono, returns it as is
            """
            if input_audio.ndim == 1:
                return input_audio  # Return mono as is
            return input_audio[:, 1]  # Return right channel

        def reverb(input_audio, room_size=.92, wet_level=.45, dry_level=.55, width=1.5):
            """
            Process stereo audio with reverb (Schroeder/Moorer algorithm)
            Dynamically calculates the reverb tail to reach -80dB
            """

            # 1. TAIL CALCULATION (RT80)
            # Base delay definitions (in samples)
            comb_delays = [1557, 1617, 1491, 1422]
            
            # Calculate the longest possible delay.
            # The right channel has an extra 'spread', so the maximum effective delay is:
            # Max Base Delay + (20 * width)
            max_delay_base = max(comb_delays)
            max_effective_delay = max_delay_base + (20 * width)

            # Safety: room_size cannot be >= 1.0 (infinite feedback)
            safe_room_size = min(room_size, 0.999)

            # RT80 FORMULA: N = (-4 * delay) / log10(gain)
            # Calculate how many samples it takes for the signal to drop to -80dB (0.0001 amplitude)
            rt80_samples = int(abs((-4 * max_effective_delay) / np.log10(safe_room_size)))
            
            # Add a safety buffer (20%) to compensate for All-Pass filter diffusion
            padding_samples = int(rt80_samples * 1.2)

            # 2. AUDIO PREPARATION

            # Convert to stereo (using the external library)
            input_audio = Audio_Effects.Stereo_Expansion.to_stereo(input_audio)
            
            # Generate silence using the dynamic calculation
            # Note: WaveTables.silence should return a properly shaped array of zeros
            silence = WaveTables.silence(padding_samples) 
            
            # Ensure silence has 2 columns if input is stereo (N, 2)
            if input_audio.ndim == 2 and silence.ndim == 1:
                silence = np.column_stack((silence, silence))
                
            input_audio = np.vstack((input_audio, silence))

            # 3. DSP PROCESSING

            allpass_delays = [225, 341]
            allpass_gain = 0.7

            # Ensure the audio is stereo for processing (N, 2)
            if input_audio.ndim == 1:
                input_audio = np.column_stack((input_audio, input_audio))

            # Initialize outputs
            output_l = np.zeros_like(input_audio[:, 0])
            output_r = np.zeros_like(input_audio[:, 1])
            channels = [input_audio[:, 0], input_audio[:, 1]]
            outputs = [output_l, output_r]

            for i, channel in enumerate(channels):
                # A. Comb Filter Stage (Parallel)
                comb_out = np.zeros_like(channel)
                
                # If it's the right channel (i=1), apply the spread
                spread_factor = 0 if i == 0 else (20 * width)

                for delay in comb_delays:
                    eff_delay = int(delay + spread_factor)
                    # Call to the external library
                    comb_out += Audio_Effects.Filters_Equalization \
                        .comb_filter(channel, eff_delay, safe_room_size)

                # B. All-Pass Filter Stage (Series)
                ap_out = comb_out
                for delay in allpass_delays:
                    eff_delay = int(delay + spread_factor)
                    # Call to the external library
                    ap_out = Audio_Effects.Filters_Equalization \
                        .allpass_filter(ap_out, eff_delay, allpass_gain)

                outputs[i] = ap_out
            
            # 4. FINAL MIX
            
            # Scale the wet signal to avoid clipping when summing the combs
            # (The 0.1 factor is correct to avoid saturation after summing 4 filters)
            wet_signal = np.column_stack((outputs[0], outputs[1])) * 0.1

            return (input_audio * dry_level) + (wet_signal * wet_level)

        def stereo_expander(input_audio, mix=.5, start_in_hz=180):
            """
            Expande una señal mono paneando 32 bandas alternadas

            ``mix`` mezcla la señal expandida con la señal mono original
            """
            if input_audio.ndim != 1:
                raise ValueError("input_audio must be a mono one-dimensional array")

            stereo_dry = np.column_stack((input_audio, input_audio))
            if input_audio.size == 0 or mix == 0:
                return stereo_dry

            mid_spectrum = np.fft.rfft(input_audio)
            frequencies = np.fft.rfftfreq(len(input_audio), d=1 / SAMPLE_RATE)

            band_count = 32
            band_centers = np.geomspace(
                start_in_hz, SAMPLE_RATE / 2, num=band_count
            )
            band_position = np.interp(
                np.log(np.maximum(frequencies, start_in_hz)),
                np.log(band_centers),
                np.arange(band_count),
            )
            lower_band = np.floor(band_position).astype(int)
            upper_band = np.minimum(lower_band + 1, band_count - 1)
            upper_weight = band_position - lower_band
            lower_weight = 1 - upper_weight

            left_spectrum = np.zeros_like(mid_spectrum)
            right_spectrum = np.zeros_like(mid_spectrum)
            for band in range(band_count):
                band_weight = (
                    np.where(lower_band == band, lower_weight, 0)
                    + np.where(upper_band == band, upper_weight, 0)
                )
                band_spectrum = mid_spectrum * band_weight
                pan = 1 if band % 2 else -1
                left_spectrum += band_spectrum * (1 - pan)
                right_spectrum += band_spectrum * (1 + pan)

            expanded = np.column_stack(
                (
                    np.fft.irfft(left_spectrum, n=len(input_audio)),
                    np.fft.irfft(right_spectrum, n=len(input_audio)),
                )
            )
            return stereo_dry * (1 - mix) + expanded * mix


    class Tuning_Stretching:
        def vinyl(data, n):
            if not n: return data
            return Audio_Effects.Tuning_Stretching.resampling(data, int(n * SAMPLE_RATE), SAMPLE_RATE)

        def resampling(audio_data, sample_rate_old, new_sample_rate):
            # Compute the number of samples for the new sample rate
            ratio = new_sample_rate / sample_rate_old
            new_num_samples = int(len(audio_data) * ratio)

            # Create original and new indices
            original_indices = np.arange(len(audio_data))
            new_indices = np.linspace(0, len(audio_data) - 1, new_num_samples)

            # Interpolate to obtain the resampled audio
            if audio_data.ndim == 1:  # Mono audio
                resampled_audio = np.interp(new_indices, original_indices, audio_data)
            else:  # Stereo or multichannel audio
                resampled_audio = np.array([
                    np.interp(new_indices, original_indices, audio_data[:, i])
                    for i in range(audio_data.shape[1])]).T

            return resampled_audio

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
            """Creates an all-pass filter (All-Pass Filter) for diffusion"""
            b = np.zeros(delay_samples + 1)
            b[0] = -gain
            b[delay_samples] = 1
            a = np.zeros(delay_samples + 1)
            a[0] = 1
            a[delay_samples] = -gain
            return lfilter(b, a, signal)

        def calculate_peaking_coeffs(fc, Q, dBgain):
            """
            Calculate coefficients for a Peaking EQ filter according to
            Robert Bristow-Johnson's 'Audio EQ Cookbook' formulas
            """
            A = 10 ** (dBgain / 40.0)
            w0 = 2 * np.pi * fc / SAMPLE_RATE
            alpha = np.sin(w0) / (2 * Q)
            cos_w0 = np.cos(w0)

            b0 = 1 + alpha * A
            b1 = -2 * cos_w0
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * cos_w0
            a2 = 1 - alpha / A

            return b0/a0, b1/a0, b2/a0, a1/a0, a2/a0

        def time_varying_eq(input_signal, freq_array, q_array, gain_array):
            """
            Applies EQ where parameters change for each sample

            Args:
                input_signal: Input audio signal
                freq_array: Array with center frequencies for each sample
                q_array: Array with Q values for each sample
                gain_array: Array with gain values in dB for each sample

            Returns:
                Processed audio signal
            """
            output_signal = np.zeros_like(input_signal)

            # Buffers to store previous states
            x1, x2 = 0.0, 0.0
            y1, y2 = 0.0, 0.0

            for n in range(len(input_signal)):
                x0 = input_signal[n]
                
                # Get current parameters
                fc = freq_array[n]
                Q = q_array[n]
                gain = gain_array[n]
                
                # Recalculate coefficients
                b0, b1, b2, a1, a2 = Audio_Effects.Filters_Equalization.calculate_peaking_coeffs(fc, Q, gain)
                
                # Apply difference equation (Direct Form I)
                y0 = b0*x0 + b1*x1 + b2*x2 - a1*y1 - a2*y2
                
                # Update buffers
                output_signal[n] = y0
                x2, x1 = x1, x0
                y2, y1 = y1, y0

            return output_signal

    class Special:
        def normalize(audio_signal):
            max_val = np.max(np.abs(audio_signal))
            if max_val == 0:
                return audio_signal
            return audio_signal / max_val

        def invert_phase(audio_signal):
            """Invert the phase of the signal (mono or multichannel)"""
            return -np.asarray(audio_signal)

        def reverse(audio_signal):
            """Reverse the audio in time without separating its channels"""
            return np.asarray(audio_signal)[::-1].copy()

        def fade_in(audio_signal, start=0, end=None):
            """Apply a linear fade-in between the start and end indices, inclusive"""
            return Audio_Effects.Special._apply_fade(audio_signal, start, end, True)

        def fade_out(audio_signal, start=0, end=None):
            """Apply a linear fade-out between the start and end indices, inclusive"""
            return Audio_Effects.Special._apply_fade(audio_signal, start, end, False)

        def _apply_fade(audio_signal, start, end, is_fade_in):
            audio_signal = np.asarray(audio_signal)
            is_stereo = audio_signal.ndim == 2 and audio_signal.shape[1] == 2
            if end is None:
                end = len(audio_signal) - 1
            if start < 0 or end < start or end >= len(audio_signal):
                raise ValueError("start and end must be valid signal indices")

            result = audio_signal.copy()
            gain = np.linspace(0.0, 1.0, end - start + 1)
            if not is_fade_in:
                gain = gain[::-1]
            if result.ndim > 1:
                gain = gain.reshape((-1,) + (1,) * (result.ndim - 1))
            result[start:end + 1] *= gain
            if result.ndim > 1 and not is_stereo:
                result = np.mean(result, axis=tuple(range(1, result.ndim)))
            return result

    class Audio_Analysis:
        def rms(audio_signal):
            return np.sqrt(np.mean(audio_signal**2))


class Aura:
    def __init__(self, preset: bytes | dict | str):
        self.last_note = None
        self.preset = preset
        if isinstance(preset, bytes):
            self.preset = self.get_bin_preset()
        elif isinstance(preset, str):
            self.preset = json.loads(preset)

    def osc_aura(hz, duration, gain, waveform_n,
                 stretch, resonance, resonance_q, resonance_gain):
        pass


    def get_note(self, note_hz=261.626, duration_ms=1, velocity=.8):
        """
        Generate a note from the preset with the specified frequency and duration

        Args:
            note_hz: Fundamental frequency of the note, in Hz
            duration_ms: Duration of the note, in milliseconds
            velocity: Relative intensity of the note (default, 0.8)

        Returns:
            np.ndarray: Audio array with the generated note, in stereo format (2 channels)
        """

        return

    def get_hz_note(self, note_number, tune_reference=440) -> float:
        """
        Convert note number to frequency in Hz
        0 = C0 (16.35 Hz)
        57 = A4 (440 Hz)
        """
        return tune_reference * 2**((note_number-57) / 12)

    def get_note_number(self, f) -> float:
        """
        Convert frequency in Hz to note number
        0 = C0 (16.35 Hz)
        57 = A4 (440 Hz)
        """
        return float(12 * np.log2(f / 440)) + 57

    rb"""Save the preset in different formats for storage or transmission"""

    def get_bin_preset(self):
        """
        Convert the preset dictionary to a binary format for storage or transmission
        """
        preset_json = json.dumps(self.preset, separators=(",", ":"))
        return gzip.compress(preset_json.encode("utf-8"))

    def get_base46_preset(self):
        """
        Convert the preset dictionary to a base46 format for storage or transmission
        """
        preset_json = json.dumps(self.preset, separators=(",", ":"))
        return base64.b64encode(gzip.compress(preset_json.encode("utf-8"))).decode("utf-8")

    def get_string_preset(self):
        """
        Convert the preset dictionary to a string format for storage or transmission
        """
        return json.dumps(self.preset, separators=(",", ":"))



def main():
    """Create an audio array"""

    audio_data = WaveTables.sample("Bsound/guitar_test.mp3")
    audio_data = Audio_Effects.Stereo_Expansion.to_mono(audio_data)
    audio_data = Audio_Effects.Stereo_Expansion.stereo_expander(audio_data)
    #audio_data = Audio_Effects.Stereo_Expansion.only_side(audio_data)

    sf.write("output.mp3", audio_data, SAMPLE_RATE)
    if 0:
        import matplotlib.pyplot as plt
        time_axis = np.arange(len(audio_data)) / SAMPLE_RATE
        plt.plot(time_axis, audio_data, label="Audio data")
        lfo_time_axis = np.arange(len(lfo)) / SAMPLE_RATE
        plt.plot(lfo_time_axis, Audio_Effects.Stereo_Expansion.to_mono(lfo), label="LFO")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.title("Audio data and LFO")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    # convert to stereo and add a subtle room reverb
    # audio_data = Audio_Effects.Stereo_Expansion.to_stereo(audio_data)

    """
    # Automate a resonant peaking EQ with an LFO for an acidic, squelchy tone
    eq_time = np.arange(len(audio_data)) / SAMPLE_RATE
    resonance_lfo = 0.5 * (1 + np.sin(2 * np.pi * 0.35 * eq_time))
    eq_freq = 650 + 2200 * resonance_lfo
    eq_q = np.full(len(audio_data), 12.0)
    eq_gain = 3 + 9 * resonance_lfo
    audio_data = np.column_stack([
        Audio_Effects.Filters_Equalization.time_varying_eq(
            audio_data[:, channel], eq_freq, eq_q, eq_gain
        )
        for channel in range(audio_data.shape[1])
    ])

    audio_data = Audio_Effects.Stereo_Expansion.reverb(
        audio_data,
        room_size=0.92,
        wet_level=0.35,
        dry_level=0.65,
        width=1.2,
    )

    """
    """Play an audio array"""
    import pygame

    pygame.mixer.pre_init(frequency=SAMPLE_RATE, size=-16, channels=2)
    pygame.init()

    #sf.write("output.wav", audio_data, SAMPLE_RATE)

    audio_data_int16 = np.clip(
        audio_data * (2**15 * 0.9), -2**15, 2**15 - 1
    ).astype(np.int16)
    audio_data_int16 = np.ascontiguousarray(audio_data_int16)
    sound = pygame.mixer.Sound(array=audio_data_int16)
    sound.play()
    time.sleep((1/SAMPLE_RATE) * len(audio_data))


if __name__ == "__main__":
    main()
