"""
Aura Synthesizer
By @Brick_briceño 2025

About:
This module typically works with 32-bit stereo audio
unless specified otherwise in specific module functions

Automations are low-frequency arrays returned as parameters for those automations

Presets can be stored in JSON format for easy modification
Zlib converts them to binary, while BaseX and Zlib convert them into a string,
allowing them to be sent via message or posted on forums and social media

This is an SBR module, so Aura knows nothing about BPM, scales, or note durations,
It doesn't know whether it is in monophonic or polyphonic mode, nor does it know the tuning,
Temperament or the specific frequency to which it is tuned—the SBR and Bsound core handles all of that

"""


from scipy.fft import irfft as fft_irfft, rfft as fft_rfft
from scipy.signal import butter, lfilter_zi, lfilter, resample_poly
from numba import jit, prange
import soundfile as sf
import numpy as np
import time
import json
import zlib
import ast


SAMPLE_RATE = 44_100


def _tension_curve(progress: np.ndarray, tension: float) -> np.ndarray:
    """Map 0..1 progress to a normalized logarithmic curve"""
    progress = np.asarray(progress, dtype=np.float32)
    progress = np.clip(progress, 0, 1)
    if tension > 0:
        curvature = 10 ** (2 * tension) - 1
        return (np.log1p(curvature * progress) / np.log1p(curvature)).astype(
            np.float32, copy=False
        )
    if tension < 0:
        curvature = 10 ** (-2 * tension) - 1
        return 1 - (
            np.log1p(curvature * (1 - progress)) / np.log1p(curvature)
        ).astype(np.float32, copy=False)
    return progress


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
        frequencies = np.asarray(frequency, dtype=np.float32)
        if frequencies.ndim == 0:
            t = np.linspace(
                0, samples / SAMPLE_RATE, samples, endpoint=False, dtype=np.float32
            )
            return (2 * np.pi * frequencies * t).astype(np.float32, copy=False)
        if frequencies.ndim != 1:
            raise ValueError("frequency must be a scalar or a one-dimensional array")
        if len(frequencies) != samples:
            raise ValueError("frequency array must have one value per sample")

        phase = np.zeros(samples, dtype=np.float32)
        if samples > 1:
            phase[1:] = np.cumsum(frequencies[:-1])
        return (2 * np.pi * phase / SAMPLE_RATE).astype(np.float32, copy=False)

    def _stretch_values(samples, stretch):
        values = np.asarray(stretch, dtype=np.float32)
        if values.ndim > 1 or (values.ndim == 1 and len(values) != samples):
            raise ValueError("stretch must be a scalar or have one value per sample")
        if not np.all(np.isfinite(values)) or np.any(values < 0):
            raise ValueError("stretch must contain finite, non-negative values")
        return values

    def _stretched_harmonics(samples, frequency, amplitude, stretch, waveform):
        frequencies = np.asarray(frequency, dtype=np.float32)
        if frequencies.ndim > 1 or (
            frequencies.ndim == 1 and len(frequencies) != samples
        ):
            raise ValueError("frequency must be a scalar or have one value per sample")
        if samples == 0:
            return np.zeros(0, dtype=np.float32)

        max_frequency = np.max(np.abs(frequencies))
        if max_frequency == 0:
            return np.zeros(samples, dtype=np.float32)

        result = np.zeros(samples, dtype=np.float32)
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
        return result.astype(np.float32, copy=False)

    def silence(samples):
        return np.zeros((samples, 2), dtype=np.float32)

    def noise(samples, amplitude=1.0):
        rng = np.random.default_rng()
        return rng.standard_normal(
            size=samples, dtype=np.float32
        ) * np.float32(amplitude)

    def vinyl(samples, db=-18):
        data = WaveTables.sample("vinyl.ogg")
        if samples == 0:
            return np.zeros((0, data.shape[1]), dtype=data.dtype)
        if len(data) < samples:
            data = np.tile(data, (int(np.ceil(samples / len(data))), 1))
        return (data[:samples] * (10 ** (db / 20))).astype(np.float32, copy=False)

    def sine(samples, frequency=440, amplitude=1.0):
        return (np.sin(WaveTables._phase(samples, frequency)) * amplitude).astype(
            np.float32, copy=False
        )

    def square(samples, frequency=440, amplitude=1.0, stretch=0.0):
        stretch = WaveTables._stretch_values(samples, stretch)
        if np.any(stretch):
            return WaveTables._stretched_harmonics(
                samples, frequency, amplitude, stretch, "square"
            )
        return (
            np.sign(np.sin(WaveTables._phase(samples, frequency))) * amplitude
        ).astype(np.float32, copy=False)

    def sawtooth(samples, frequency=440, amplitude=1.0, stretch=0.0):
        stretch = WaveTables._stretch_values(samples, stretch)
        if np.any(stretch):
            return WaveTables._stretched_harmonics(
                samples, frequency, amplitude, stretch, "sawtooth"
            )
        phase = WaveTables._phase(samples, frequency)
        return (
            2 * (phase / (2 * np.pi) - np.floor(0.5 + phase / (2 * np.pi)))
        ).astype(np.float32, copy=False) * np.float32(amplitude)

    def triangle(samples, frequency=440, amplitude=1.0, stretch=0.0):
        stretch = WaveTables._stretch_values(samples, stretch)
        if np.any(stretch):
            return WaveTables._stretched_harmonics(
                samples, frequency, amplitude, stretch, "triangle"
            )
        phase = WaveTables._phase(samples, frequency)
        return (
            2 * np.abs(
                2 * (phase / (2 * np.pi) - np.floor(0.5 + phase / (2 * np.pi)))
            ) - 1
        ).astype(np.float32, copy=False) * np.float32(amplitude)

    def sample(path):
        data, samplerate = sf.read(path, dtype="float32", always_2d=True)
        if samplerate != SAMPLE_RATE:
            divisor = np.gcd(samplerate, SAMPLE_RATE)
            data = resample_poly(
                data, SAMPLE_RATE // divisor, samplerate // divisor, axis=0
            ).astype(np.float32, copy=False)
        if data.shape[1] == 1:
            data = np.repeat(data, 2, axis=1)
        elif data.shape[1] > 2:
            raise ValueError("Audio file must be mono or stereo")
        return data


class Envelopes:
    def DAHDSR_envelope(
        delay,
        attack,
        hold,
        decay,
        sustain_level,
        sustain,
        release,
        attack_tension: float = 0,
        decay_tension: float = 0,
        release_tension: float = 0,
    ) -> np.ndarray:
        """
        Generate a DAHDSR envelope in float32 format

        Args:
            delay (float | int): Delay before the envelope starts, must
                be greater than or equal to 0 seconds
            attack (float | int): Duration of the attack phase, from 0
                until the envelope reaches its maximum level
            hold (float | int): Time the envelope stays at its maximum
                level before the decay begins
            decay (float | int): Duration of the fall from the maximum
                level to the sustain level
            sustain_level (float): Envelope sustain level in the range [0, 1],
                where 1 is the maximum level and 0 is silence
            sustain (float | int): Duration of the sustain phase, during
                which the envelope remains constant
            release (float | int): Duration of the envelope release, from
                the sustain level down to 0
            attack_tension (float, optional): Attack curve shape in the range
                from -1 to 1, positive values rise faster at the beginning and
                negative values make the rise smoother
            decay_tension (float, optional): Decay curve shape in the range from
                -1 to 1, adjusts the fall toward the sustain level
            release_tension (float, optional): Release curve shape in the range
                from -1 to 1, changes the final fade down to 0

        Raises:
            ValueError: If any time is negative, sustain_level is outside [0, 1],
                any tension is outside [-1, 1], or SAMPLE_RATE is not a positive
                integer

        Returns:
            np.ndarray: One-dimensional array containing the calculated envelope
                in float32 format
        """
        if any(seconds < 0 for seconds in (
            delay,
            attack,
            hold,
            decay,
            sustain,
            release,
        )):
            raise ValueError("Envelope times cannot be negative")
        if not 0 <= sustain_level <= 1:
            raise ValueError("sustain_level must be between 0 and 1")
        if any(not -1 <= tension <= 1 for tension in (
            attack_tension, decay_tension, release_tension
        )):
            raise ValueError("Tensions must be between -1 and 1")
        if not isinstance(SAMPLE_RATE, (int, np.integer)) or SAMPLE_RATE <= 0:
            raise ValueError("SAMPLE_RATE must be a positive integer")

        segments = [
            np.zeros(int(round(delay * SAMPLE_RATE)), dtype=np.float32)
        ]

        attack_count = int(round(attack * SAMPLE_RATE))
        if attack_count:
            progress = np.arange(attack_count, dtype=np.float32) / attack_count
            segments.append(_tension_curve(progress, attack_tension))

        hold_count = int(round(hold * SAMPLE_RATE))
        if hold_count:
            segments.append(np.ones(hold_count, dtype=np.float32))

        decay_count = int(round(decay * SAMPLE_RATE))
        if decay_count:
            progress = np.arange(decay_count, dtype=np.float32) / decay_count
            curve = _tension_curve(progress, decay_tension)
            segments.append(1 + (sustain_level - 1) * curve)

        sustain_count = int(round(sustain * SAMPLE_RATE))
        if sustain_count:
            segments.append(
                np.full(sustain_count, sustain_level, dtype=np.float32)
            )

        release_count = int(round(release * SAMPLE_RATE))
        if release_count:
            progress = np.arange(release_count, dtype=np.float32) / release_count
            curve = _tension_curve(progress, release_tension)
            segments.append(sustain_level * (1 - curve))

        if not any(segment.size for segment in segments):
            raise ValueError("At least one envelope stage must have positive duration")
        envelope = np.concatenate(segments)
        envelope[-1] = 0
        return envelope.astype(np.float32)


class Audio_Effects:
    class Gain_Distortion_Dynamics:
        def remove_ending_in_silence(audio, threshold=10e-4):
            # Find the last index where the audio exceeds the threshold
            final_index = np.where(np.abs(audio) > threshold)[0][-1]
            # Trim the audio up to that index
            return audio[:final_index + 1]

        def drive(audio_input: np.ndarray, gain_dbs=1.0, normalize=False) -> np.ndarray:
            """Use the hyperbolic tangent to distort the audio signal"""
            audio_input = np.asarray(audio_input, dtype=np.float32)
            audio_output = np.tanh(
                audio_input * 
                Audio_Effects.Audio_Analysis.dbs_to_float(gain_dbs)
                )
            if normalize:
                audio_output /= np.max(np.abs(audio_output))
            return audio_output.astype(np.float32, copy=False)

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
            audio = np.asarray(audio_input, dtype=np.float32)
            if audio.ndim not in (1, 2):
                raise ValueError("audio_input must be mono or have shape (frames, channels)")

            frame_count = audio.shape[0]

            def parameter_values(
                name, value, minimum, maximum=None, nearest_even=False
            ):
                try:
                    values = np.asarray(value, dtype=np.float32)
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
                return audio

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

            held_audio = np.empty_like(quantized, dtype=np.float32)
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
            return (wet_mix * held_audio + (1 - wet_mix) * audio).astype(
                np.float32, copy=False
            )

        @jit(nopython=True, cache=True, parallel=True)
        def _triode12ax7_solve_plate_voltage(
            grid_voltages, supply_voltage, plate_load, mu, exponent, kg1, kp, kvb
        ):
            plate_voltages = np.empty_like(grid_voltages)
            for index in prange(grid_voltages.size):
                grid_voltage = grid_voltages[index]
                low = 0.0
                high = supply_voltage
                for _ in range(32):
                    midpoint = (low + high) * 0.5
                    argument = kp * (
                        1.0 / mu
                        + grid_voltage
                        / np.sqrt(kvb + midpoint * midpoint)
                    )
                    if argument > 0.0:
                        softplus = argument + np.log1p(np.exp(-argument))
                    else:
                        softplus = np.log1p(np.exp(argument))
                    e1 = midpoint * softplus / kp
                    plate_current = max(e1, 0.0) ** exponent / kg1
                    residual = (
                        midpoint + plate_load * plate_current - supply_voltage
                    )
                    if residual > 0.0:
                        high = midpoint
                    else:
                        low = midpoint
                plate_voltages[index] = (low + high) * 0.5
            return plate_voltages

        def valve_distortion(audio: np.ndarray, gain_db=20,
                             normalize=False, high_pass_filter=True) -> np.ndarray:
            audio = np.asarray(audio, dtype=np.float32)
            if (
                audio.ndim not in (1, 2)
                or audio.shape[0] == 0
                or (audio.ndim == 2 and audio.shape[1] not in (1, 2))
            ):
                raise ValueError("Audio must be a non-empty mono or stereo array")

            drive_gain = Audio_Effects.Audio_Analysis.dbs_to_float(gain_db)

            oversampling = 4
            audio = resample_poly(audio, oversampling, 1, axis=0)

            # Single common-cathode 12AX7 stage, circuit values are explicit
            supply_voltage = 250.0
            plate_load = 100_000.0
            grid_bias = -1.5
            mu, exponent, kg1, kp, kvb = 100.0, 1.4, 1060.0, 600.0, 300.0

            quiescent_plate = Audio_Effects.Gain_Distortion_Dynamics._triode12ax7_solve_plate_voltage(
                np.asarray([grid_bias], dtype=np.float32),
                supply_voltage, plate_load, mu, exponent, kg1, kp, kvb
            )[0]
            grid_voltage = grid_bias + audio * drive_gain
            # Approximate grid-current onset: a real grid draws current above 0 V
            grid_voltage = np.minimum(grid_voltage, 0.0)
            plate_voltage = Audio_Effects.Gain_Distortion_Dynamics._triode12ax7_solve_plate_voltage(
                np.ascontiguousarray(grid_voltage.reshape(-1)),
                supply_voltage, plate_load, mu, exponent, kg1, kp, kvb
            ).reshape(grid_voltage.shape)
            distorted_audio = (quiescent_plate - plate_voltage) / supply_voltage
            distorted_audio = resample_poly(
                distorted_audio, 1, oversampling, axis=0
            )

            if high_pass_filter:
                b, a = butter(1, 27.5, btype="highpass", fs=SAMPLE_RATE)
                b = b.astype(np.float32)
                a = a.astype(np.float32)
                zi = lfilter_zi(b, a).reshape(
                    (-1,) + (1,) * (distorted_audio.ndim - 1)
                )
                zi = zi * np.expand_dims(distorted_audio[0], axis=0)
                distorted_audio, _ = lfilter(
                    b, a, distorted_audio, axis=0, zi=zi
                )

            if normalize:
                peak = np.max(np.abs(distorted_audio))
                if peak > 0:
                    distorted_audio /= peak

            return distorted_audio.astype(np.float32, copy=False)

        @jit(nopython=True, cache=True)
        def _t4_cell_and_tube_dsp(audio, peak_reduction_knob, gain_knob, ratio):
            """
            C-compiled DSP core (via Numba) to process audio sample by sample
            Emulates the T4 optical cell and the 12AX7 amplification stage
            """
            n_samples = audio.shape[0]
            n_channels = audio.shape[1] if audio.ndim > 1 else 1
            if n_channels not in (1, 2):
                raise ValueError("Audio must be mono or stereo")

            output = np.zeros_like(audio)
            
            # 1. Adjust controls (0 - 100)
            # Peak Reduction increases the sidechain gain against a fixed internal threshold
            sc_gain = 10.0 ** ((peak_reduction_knob - 50.0) / 20.0)
            # Gain controls output makeup (0 to ~40 dB)
            makeup_linear = 10.0 ** ((gain_knob * 0.4) / 20.0)
            
            # Internal LA-2A parameters
            THRESHOLD_DB = -24.0
            
            # 2. T4 cell time constants (RC filters)
            # Attack averaged in 10ms
            alpha_A = np.exp(-1.0 / (SAMPLE_RATE * 0.010)) 
            # The CdS photocell has a two-stage release:
            # 50% recovery in ~60ms (fast)
            alpha_R_fast = np.exp(-1.0 / (SAMPLE_RATE * 0.060))
            # The remainder takes 1 to 15 seconds (program-dependent)
            # We will use 2.5 seconds as the representative memory effect average
            alpha_R_slow = np.exp(-1.0 / (SAMPLE_RATE * 2.500))
            
            env_fast = 0.0
            env_slow = 0.0
            
            # Offset for asymmetric saturation (basic even-harmonic emulation of the 12AX7 triode)
            tube_bias = 0.15 
            bias_compensation = np.tanh(tube_bias)
            
            for i in range(n_samples):
                # Level detection (stereo-linked if there is more than 1 channel)
                if n_channels == 2:
                    sc_level = max(np.abs(audio[i, 0]), np.abs(audio[i, 1])) * sc_gain
                elif audio.ndim == 2:
                    sc_level = np.abs(audio[i, 0]) * sc_gain
                else:
                    sc_level = np.abs(audio[i]) * sc_gain

                if sc_level < 1e-9:
                    sc_level = 1e-9
                sc_db = 20.0 * np.log10(sc_level)
                
                # Calculate the gain-reduction target
                if sc_db > THRESHOLD_DB:
                    target_gr = (sc_db - THRESHOLD_DB) * (1.0 - 1.0/ratio)
                else:
                    target_gr = 0.0
                    
                # 3. T4 cell envelope follower
                # Attack
                if target_gr > env_fast:
                    env_fast = alpha_A * env_fast + (1.0 - alpha_A) * target_gr
                else:
                    # Fast release (first 50%)
                    env_fast = alpha_R_fast * env_fast + (1.0 - alpha_R_fast) * target_gr
                    
                if target_gr > env_slow:
                    env_slow = alpha_A * env_slow + (1.0 - alpha_A) * target_gr
                else:
                    # Slow release (light memory for the remaining 50%)
                    env_slow = alpha_R_slow * env_slow + (1.0 - alpha_R_slow) * target_gr
                    
                # The sum of both averaged envelopes generates the dual-optical fall curve
                current_gr_db = 0.5 * env_fast + 0.5 * env_slow
                
                # Convert dB reduction to linear gain
                gain_reduction_linear = 10.0 ** (-current_gr_db / 20.0)
                
                    # 4. Apply gain and pass through the tube stage (12AX7)
                if audio.ndim == 2:
                    for c in range(n_channels):
                        sample = audio[i, c] * gain_reduction_linear * makeup_linear
                        tube_out = np.tanh(sample + tube_bias) - bias_compensation
                        output[i, c] = tube_out
                else:
                    sample = audio[i] * gain_reduction_linear * makeup_linear
                    tube_out = np.tanh(sample + tube_bias) - bias_compensation
                    output[i] = tube_out

            return output

        def compressor_la2a(audio, peak_reduction=50.0, gain=50.0, ratio=5):
            """
            LA-2A style compression processor

            Parameters:
            - peak_reduction: (0-100) controls how much compression is applied
            - gain: (0-100) output make-up gain
            - ratio: compression ratio
            """

            # Apply the compiled DSP stage
            audio = np.asarray(audio, dtype=np.float32)
            audio_procesado = Audio_Effects.Gain_Distortion_Dynamics._t4_cell_and_tube_dsp(
                audio, peak_reduction, gain, ratio)

            return audio_procesado.astype(np.float32, copy=False)

        @jit(nopython=True, cache=True)
        def _br11ck67_analog_core(audio_in, input_gain_lin, output_gain_lin, att_coef, rel_coef, ratio, thresh_db):
            """
            br11ck67 core processing sample by sample
            Includes feedback loop, FET asymmetry, and transformer distortion (hysteresis)
            """
            out = np.zeros_like(audio_in)
            n_channels = audio_in.shape[1]
            env = 0.0  # Gain reduction state (dB)
            feedback_sample = np.zeros(n_channels, dtype=audio_in.dtype)
            transformer_state = np.zeros(n_channels, dtype=audio_in.dtype)
            
            for i in range(len(audio_in)):
                # Linked feedback detector to keep the stereo image stable
                detector_signal = 0.0
                for c in range(n_channels):
                    channel_level = abs(feedback_sample[c] + 0.001)
                    if channel_level > detector_signal:
                        detector_signal = channel_level

                x_db = 20.0 * np.log10(detector_signal + 1e-12) if detector_signal > 1e-12 else -120.0
                
                # 3. Gain Reduction target (GR)
                if x_db > thresh_db:
                    gr_target_db = (x_db - thresh_db) * (1.0 - (1.0 / ratio))
                else:
                    gr_target_db = 0.0
                    
                # 4. Envolvente (Program-Dependent)
                delta = gr_target_db - env
                if delta > 0:
                    env += att_coef * delta  # Ataque
                else:
                    # Dynamic release: it falls more slowly if there is a lot of accumulated compression
                    dynamic_rel = rel_coef * (1.0 - (min(env, 40.0) / 40.0) * 0.1) 
                    env += dynamic_rel * delta
                    
                # 5. Apply linear GR to the input signal
                gr_linear = 10.0 ** (-env / 20.0)
                for c in range(n_channels):
                    x = audio_in[i, c] * input_gain_lin
                    x_comp = x * gr_linear

                    # Save the compressed sample for the feedback detector
                    feedback_sample[c] = x_comp

                    # FET stage: gain and asymmetric saturation
                    x_out = x_comp * output_gain_lin
                    asym_drive = x_out + 0.15 * (x_out ** 2)
                    fet_out = np.tanh(asym_drive)

                    # Output transformer stage with per-channel memory
                    diff = fet_out - transformer_state[c]
                    non_linear_drive = np.tanh(diff * 1.2) + 0.05 * (diff ** 2)
                    transformer_state[c] += 0.5 * non_linear_drive
                    out[i, c] = transformer_state[c]
                
            return out

        def br11ck67_analog(audio_in, input_db=12.0, output_db=-6.0,
                            attack_ms=0.2, release_ms=300.0, ratio=4.0,
                            all_buttons_in=False, oversampling=4):
            """
            Main FET br11ck67_analog controller with anti-aliasing oversampling

            Parameters:
            - audio_in: NumPy array (mono or processed channel by channel)
            - oversampling: 1 (Off), 2, 4, or 8. (4x recommended for analog distortion without aliasing)
            """
            audio_in = np.asarray(audio_in, dtype=np.float32)
            mono_input = audio_in.ndim == 1
            if mono_input:
                audio_in = audio_in[:, np.newaxis]
            elif audio_in.ndim != 2:
                raise ValueError("Audio must be mono or stereo")
            if audio_in.shape[0] == 0 or audio_in.shape[1] not in (1, 2):
                raise ValueError("Audio must have samples and one or two channels")
            if not np.all(np.isfinite(audio_in)):
                raise ValueError("Audio must contain only finite values")
            audio_in = np.ascontiguousarray(audio_in)
            
            # 1. Configure analog parameters
            if all_buttons_in:
                ratio = 100.0 
                attack_ms = 0.02 
                input_db += 6.0 # internal massive push
                
            threshold_db = -24.0 # fixed internal threshold
            
            input_gain_lin = 10.0 ** (input_db / 20.0)
            output_gain_lin = 10.0 ** (output_db / 20.0)
            
            # 2. OVERSAMPLING (increase the sample rate)
            if oversampling > 1:
                # resample_poly applies a high-quality automatic anti-aliasing FIR filter
                audio_up = resample_poly(audio_in, oversampling, 1, axis=0)
                fs_up = SAMPLE_RATE * oversampling
            else:
                audio_up = audio_in
                fs_up = SAMPLE_RATE
                
            # Calculate IIR coefficients using the internal sample rate (fs_up)
            att_coef = 1.0 - np.exp(-1.0 / (fs_up * (attack_ms / 1000.0)))
            rel_coef = 1.0 - np.exp(-1.0 / (fs_up * (release_ms / 1000.0)))

            # 3. C-speed processing
            processed_up = Audio_Effects.Gain_Distortion_Dynamics._br11ck67_analog_core(
                np.ascontiguousarray(audio_up),
                input_gain_lin, output_gain_lin,
                                            att_coef, rel_coef, ratio, threshold_db)
                                            
            # 4. DOWNSAMPLING (return to the original fs while removing ultrasonic frequencies)
            if oversampling > 1:
                processed = resample_poly(processed_up, 1, oversampling, axis=0)
            else:
                processed = processed_up
                
            # Strictly limit the output to [-1.0, 1.0] to avoid digital clipping during export
            processed = np.clip(processed, -1.0, 1.0)
            processed = processed.astype(np.float32, copy=False)
            return processed[:, 0] if mono_input else processed

    class Stereo_Expansion:
        def pan_sound(sound, pan_level: float):
            sound = np.asarray(sound, dtype=np.float32)
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
            input_audio = np.asarray(input_audio, dtype=np.float32)
            if input_audio.ndim == 1:
                input_audio = np.column_stack((input_audio, input_audio))
            return input_audio

        def to_mono(input_audio):
            """
            Converts stereo audio to mono by averaging both channels
            If input is already mono, returns it as is
            """
            input_audio = np.asarray(input_audio, dtype=np.float32)
            if input_audio.ndim == 1:
                return input_audio # Already mono
            return np.mean(input_audio, axis=1) # Average L and R channels

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

        def reverb(input_audio, room_size=.92, wet_level=.45, dry_level=.55, width=1.5, tail_db=-60):
            """
            Process stereo audio with reverb using the Schroeder/Moorer algorithm
            Calculates the reverb tail length using the target level in dB

            Args:
                tail_db: Target level for the reverb tail in dB, defaults to -80
            """

            # 1, tail calculation
            # Base delay definitions in samples
            comb_delays = [1557, 1617, 1491, 1422]
            
            # Calculate the longest possible delay
            # The right channel has extra spread, so the maximum effective delay is the maximum base delay plus 20 times the width
            max_delay_base = max(comb_delays)
            max_effective_delay = max_delay_base + (20 * width)

            # Room size cannot be greater than or equal to 1 because that creates infinite feedback
            if room_size >= 1:
                raise AURA_ERROR("Room_size cannot be >= 1.0 (infinite feedback)")
            safe_room_size = min(room_size, 0.999)

            if tail_db > 0:
                raise AURA_ERROR("tail_db must be less than or equal to 0")

            # Calculate samples until the tail reaches the requested dB level
            tail_samples = int(
                abs((tail_db / 20 * max_effective_delay) / np.log10(safe_room_size))
            )
            
            # Add a 20 percent safety buffer to compensate for All-Pass filter diffusion
            padding_samples = int(tail_samples * 1.2)

            # 2, audio preparation

            # Convert to stereo using the external library
            input_audio = Audio_Effects.Stereo_Expansion.to_stereo(input_audio)
            
            # Generate silence using the calculated tail length
            # WaveTables.silence returns an array of zeros
            silence = WaveTables.silence(padding_samples) 
            
            # Ensure silence has two columns if input is stereo
            if input_audio.ndim == 2 and silence.ndim == 1:
                silence = np.column_stack((silence, silence))
                
            input_audio = np.vstack((input_audio, silence)).astype(
                np.float32, copy=False
            )

            # 3, DSP processing

            allpass_delays = [225, 341]
            allpass_gain = 0.7

            # Ensure the audio is stereo for processing
            if input_audio.ndim == 1:
                input_audio = np.column_stack((input_audio, input_audio))

            # Initialize outputs
            output_l = np.zeros_like(input_audio[:, 0])
            output_r = np.zeros_like(input_audio[:, 1])
            channels = [input_audio[:, 0], input_audio[:, 1]]
            outputs = [output_l, output_r]

            for i, channel in enumerate(channels):
                # A, parallel comb filter stage
                comb_out = np.zeros_like(channel)
                
                # Apply the spread to the right channel
                spread_factor = 0 if i == 0 else (20 * width)

                for delay in comb_delays:
                    eff_delay = int(delay + spread_factor)
                    # Apply the comb filter
                    comb_out += Audio_Effects.Filters_Equalization \
                        .comb_filter(channel, eff_delay, safe_room_size)

                # B, series all-pass filter stage
                ap_out = comb_out
                for delay in allpass_delays:
                    eff_delay = int(delay + spread_factor)
                    # Apply the all-pass filter
                    ap_out = Audio_Effects.Filters_Equalization \
                        .allpass_filter(ap_out, eff_delay, allpass_gain)

                outputs[i] = ap_out
            
            # 4, final mix
            
            # Scale the wet signal to avoid clipping when summing the comb filters
            wet_signal = np.column_stack((outputs[0], outputs[1])) * 0.1

            return (
                (input_audio * dry_level) + (wet_signal * wet_level)
            ).astype(np.float32, copy=False)

        def stereo_expander(input_audio, mix=.5, start_in_hz=180):
            """
            Expands a mono signal by panning across 32 alternating bands

            ``mix`` blends the expanded signal with the original mono signal
            """

            input_audio = np.asarray(input_audio, dtype=np.float32)
            if input_audio.ndim != 1:
                raise ValueError("input_audio must be a mono one-dimensional array")

            stereo_dry = np.column_stack((input_audio, input_audio))
            if input_audio.size == 0 or mix == 0:
                return stereo_dry

            mid_spectrum = fft_rfft(input_audio)
            frequencies = (
                np.arange(len(mid_spectrum), dtype=np.float32)
                * (SAMPLE_RATE / len(input_audio))
            )

            band_count = 32
            band_centers = np.geomspace(
                start_in_hz, SAMPLE_RATE / 2, num=band_count, dtype=np.float32
            )
            band_position = np.interp(
                np.log(np.maximum(frequencies, start_in_hz)),
                np.log(band_centers),
                np.arange(band_count),
            ).astype(np.float32)
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
                    fft_irfft(left_spectrum, n=len(input_audio)),
                    fft_irfft(right_spectrum, n=len(input_audio)),
                )
            )
            return (stereo_dry * (1 - mix) + expanded * mix).astype(
                np.float32, copy=False
            )

        def delay(input_audio, input_gain=-6, times=(1.5, 1.5, 2, 1, 2), pan=0.12, ping_pong=True, offset=0):
            """
            Add a series of stereo echoes to the original audio

            Each value in times is the interval in seconds before the next echo,
            input_gain sets the gain applied to each successive echo in dB,
            pan sets the echo balance from full left at -1 to full right at 1,
            ping_pong alternates the pan direction between successive echoes,
            offset delays the right channel when positive or the left when negative
            """

            input_audio = Audio_Effects.Stereo_Expansion.to_stereo(input_audio)
            if input_audio.ndim != 2 or input_audio.shape[1] != 2:
                raise ValueError("input_audio must be mono or stereo audio")

            intervals = np.atleast_1d(np.asarray(times, dtype=np.float32))
            input_gain, pan, offset = np.asarray(
                (input_gain, pan, offset), dtype=np.float32
            )

            if intervals.ndim != 1 or not np.all(np.isfinite(intervals)):
                raise ValueError("times must be a one-dimensional list of finite values")
            if np.any(intervals < 0):
                raise ValueError("delay intervals in times must be non-negative")
            if not np.all(np.isfinite((input_gain, pan, offset))):
                raise ValueError("input_gain, pan, and offset must be finite")
            if not -1 <= pan <= 1:
                raise AURA_ERROR("pan must be between -1 and 1")

            if intervals.size == 0 or input_audio.size == 0:
                return input_audio.astype(np.float32, copy=False)

            input_audio = input_audio.astype(np.float32, copy=False)
            interval_samples = np.rint(
                intervals * SAMPLE_RATE
            ).astype(np.int64)
            echo_starts = np.cumsum(interval_samples)
            offset_samples = int(
                np.rint(np.abs(offset) * SAMPLE_RATE)
            )
            offset_channel = 1 if offset > 0 else 0
            output_samples = max(
                len(input_audio),
                max(
                    int(start) + len(input_audio)
                    + (offset_samples if offset else 0)
                    for start in echo_starts
                ),
            )
            output = np.zeros((output_samples, 2), dtype=np.float32)
            output[:len(input_audio)] += input_audio
            gain_factor = np.float32(
                Audio_Effects.Audio_Analysis.dbs_to_float(input_gain)
            )

            # Add each echo at its cumulative delay, applying gain and pan per repeat
            for index, start in enumerate(echo_starts):
                echo_pan = pan * (-1 if ping_pong and index % 2 else 1)
                echo = Audio_Effects.Stereo_Expansion.pan_sound(
                    input_audio, echo_pan
                ) * np.float32(gain_factor ** (index + 1))
                start = int(start)
                for channel in range(2):
                    channel_start = start
                    if offset and channel == offset_channel:
                        channel_start += offset_samples
                    output[
                        channel_start:channel_start + len(echo), channel
                    ] += echo[:, channel]

            return output

    class Tuning_Stretching:
        def vinyl_stretching(data, factor):
            if not factor:
                return data
            return Audio_Effects.Tuning_Stretching.resampling(data, int(factor * SAMPLE_RATE), SAMPLE_RATE)

        def resampling(audio_data, sample_rate_old, new_sample_rate):
            audio_data = np.asarray(audio_data, dtype=np.float32)
            # Compute the number of samples for the new sample rate
            ratio = new_sample_rate / sample_rate_old
            new_num_samples = int(len(audio_data) * ratio)

            if not new_num_samples or not len(audio_data):
                return np.zeros(
                    (new_num_samples, *audio_data.shape[1:]),
                    dtype=np.float32,
                )

            # Create float32 positions and interpolate without widening audio arrays
            positions = np.linspace(
                0, len(audio_data) - 1, new_num_samples, dtype=np.float32
            )
            lower_indices = np.floor(positions).astype(np.intp)
            upper_indices = np.minimum(lower_indices + 1, len(audio_data) - 1)
            fraction = positions - lower_indices.astype(np.float32)

            # Interpolate without widening audio arrays
            if audio_data.ndim > 1:
                fraction = fraction.reshape(
                    (-1,) + (1,) * (audio_data.ndim - 1)
                )
            return (
                audio_data[lower_indices]
                + (audio_data[upper_indices] - audio_data[lower_indices])
                * fraction
            ).astype(np.float32, copy=False)

    class Filters_Equalization:
        def comb_filter(signal, delay_samples, feedback):
            """Creates a comb filter (Comb Filter)"""
            signal = np.asarray(signal, dtype=np.float32)
            b = np.zeros(delay_samples + 1, dtype=np.float32)
            b[delay_samples] = 1
            a = np.zeros(delay_samples + 1, dtype=np.float32)
            a[0] = 1
            a[delay_samples] = -feedback
            return lfilter(b, a, signal)

        def allpass_filter(signal, delay_samples, gain):
            """Creates an all-pass filter (All-Pass Filter) for diffusion"""
            signal = np.asarray(signal, dtype=np.float32)
            b = np.zeros(delay_samples + 1, dtype=np.float32)
            b[0] = -gain
            b[delay_samples] = 1
            a = np.zeros(delay_samples + 1, dtype=np.float32)
            a[0] = 1
            a[delay_samples] = -gain
            return lfilter(b, a, signal)

        def _calculate_peaking_coeffs(fc, Q, dBgain):
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

            return tuple(
                np.float32(value)
                for value in (b0/a0, b1/a0, b2/a0, a1/a0, a2/a0)
            )

        def parametricEq(input_signal, freq_array, q_array, gain_array):
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
            input_signal = np.asarray(input_signal, dtype=np.float32)
            output_signal = np.zeros_like(input_signal, dtype=np.float32)

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
                b0, b1, b2, a1, a2 = Audio_Effects.Filters_Equalization._calculate_peaking_coeffs(fc, Q, gain)
                
                # Apply difference equation (Direct Form I)
                y0 = b0*x0 + b1*x1 + b2*x2 - a1*y1 - a2*y2
                
                # Update buffers
                output_signal[n] = y0
                x2, x1 = x1, x0
                y2, y1 = y1, y0

            return output_signal

    class Special:
        def normalize(audio_signal):
            audio_signal = np.asarray(audio_signal, dtype=np.float32)
            max_val = np.max(np.abs(audio_signal))
            if max_val == 0:
                return audio_signal
            return audio_signal / max_val

        def invert_phase(audio_signal):
            """Invert the phase of the signal (mono or multichannel)"""
            return -np.asarray(audio_signal, dtype=np.float32)

        def reverse(audio_signal):
            """Reverse the audio in time without separating its channels"""
            return np.asarray(audio_signal, dtype=np.float32)[::-1].copy()

        def fade_in(audio_signal, start=0, end=None):
            """Apply a linear fade-in between the start and end indices, inclusive"""
            return Audio_Effects.Special._apply_fade(audio_signal, start, end, True)

        def fade_out(audio_signal, start=0, end=None):
            """Apply a linear fade-out between the start and end indices, inclusive"""
            return Audio_Effects.Special._apply_fade(audio_signal, start, end, False)

        def _apply_fade(audio_signal, start, end, is_fade_in):
            audio_signal = np.asarray(audio_signal, dtype=np.float32)
            is_stereo = audio_signal.ndim == 2 and audio_signal.shape[1] == 2
            if end is None:
                end = len(audio_signal) - 1
            if start < 0 or end < start or end >= len(audio_signal):
                raise ValueError("start and end must be valid signal indices")

            result = audio_signal.copy()
            gain = np.linspace(
                0.0, 1.0, end - start + 1, dtype=np.float32
            )
            if not is_fade_in:
                gain = gain[::-1]
            if result.ndim > 1:
                gain = gain.reshape((-1,) + (1,) * (result.ndim - 1))
            result[start:end + 1] *= gain
            if result.ndim > 1 and not is_stereo:
                result = np.mean(result, axis=tuple(range(1, result.ndim)))
            return result

    class Audio_Analysis:
        def float_to_dbs(sample, reference_value=1):
            # reference_value = 1 #32-bit floating
            peak_value = np.abs(np.max(sample))
            peak_db = 20 * np.log10(peak_value / reference_value)
            return peak_db

        def dbs_to_float(peak_db, reference_value=1):
            peak_value = reference_value * 10**(peak_db / 20)
            return peak_value

        def rms(audio_signal):
            return np.sqrt(np.mean(audio_signal**2))


class AURA_ERROR(Exception):
    def __init__(self, message="", advice=None):
        self.message, self.advice = message, advice
        super().__init__()

    def __str__(self):
        return (self.message if self.advice is None
         else f"{self.message} ({self.advice})")


#ALPHABET = tuple("".join(chr(i) for i in range(0x3400, 0x3400 + 2048)))

ALPHABET = tuple(dict.fromkeys("""

0123456789
aàáâãäåăæbcçdðeèéêëfghiìíîïĳjklmnñoòóôõöøœpqrsšșt
țuùúûüvwxyýÿzþßAÀÁÂÃÄÅÆBCÇDÐEÈÉÊËFGHIÌÍÎÏĲJKLMNÑOÒÓÔÕÖØŒPQR
SŠȘTȚUÙÚÛÜVWXYÝZÞẞ!#$%&'*+,-./<>?@[]^_`|~¡¢£¤¥§©«®°
±²³µ¶·»¿×÷=

""".replace("\n", "")))

BASE = len(ALPHABET)

def encode_baseX(data_bytes: bytes) -> str:
    if not data_bytes:
        return ""

    # 1. Convert the bytes into a large integer
    num = int.from_bytes(data_bytes, byteorder='big')
    if num == 0:
        return ALPHABET[0] * len(data_bytes)

    # 2. Convert the number to our Base96
    encoded = ""
    while num > 0:
        num, rem = divmod(num, BASE)
        encoded = ALPHABET[rem] + encoded

    # 3. Preservar los ceros (bytes nulos) iniciales
    pad_count = 0
    for byte in data_bytes:
        if byte == 0:
            pad_count += 1
        else:
            break
            
    return (ALPHABET[0] * pad_count) + encoded


def decode_baseX(encoded_str: str) -> bytes:
    if not encoded_str:
        return b""

    # 1. Convert the Base96 string back into a large integer
    num = 0
    for char in encoded_str:
        num = num * BASE + ALPHABET.index(char)

    # 2. Restaurar los ceros iniciales
    pad_count = 0
    for char in encoded_str:
        if char == ALPHABET[0]:
            pad_count += 1
        else:
            break

    if num == 0:
        return b'\x00' * pad_count

    # 3. Convert the number back into bytes
    byte_length = (num.bit_length() + 7) // 8
    
    data_bytes = num.to_bytes(byte_length, byteorder='big')

    return (b'\x00' * pad_count) + data_bytes


def _replace_preset_names(expression, names):
    """Replace whole variable names without regex or partial-name collisions."""
    result = []
    referenced = []
    index = 0
    while index < len(expression):
        char = expression[index]
        if char == "_" or char.isalpha():
            end = index + 1
            while end < len(expression) and (
                expression[end] == "_" or expression[end].isalnum()
            ):
                end += 1
            name = expression[index:end]
            result.append(names.get(name, name))
            referenced.append(name)
            index = end
        else:
            result.append(char)
            index += 1
    return "".join(result), referenced


def _validate_preset_expression(parsed, expression, variables):
    allowed_nodes = (
        ast.Expression, ast.Constant, ast.Name, ast.Load,
        ast.UnaryOp, ast.UAdd, ast.USub, ast.BinOp, ast.Add,
        ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    )
    nodes = list(ast.walk(parsed))
    if len(nodes) > 256:
        raise AURA_ERROR("Preset expression is too complex")
    for node in nodes:
        if not isinstance(node, allowed_nodes):
            raise AURA_ERROR(f"Unsupported operation in formula '{expression}'")
        if isinstance(node, ast.Name) and node.id not in variables:
            raise AURA_ERROR("Preset error", advice="Variable not found")
        if isinstance(node, ast.Constant) and not isinstance(
            node.value, (int, float)
        ):
            raise AURA_ERROR("Preset expressions only allow numeric constants")
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            exponent = node.right
            if isinstance(exponent, ast.UnaryOp) and isinstance(
                exponent.op, (ast.UAdd, ast.USub)
            ):
                exponent = exponent.operand
            if isinstance(exponent, ast.Constant) and abs(exponent.value) > 16:
                raise AURA_ERROR("Preset exponent magnitude cannot exceed 16")


def _align_preset_arrays(parsed, variables):
    names = {node.id for node in ast.walk(parsed) if isinstance(node, ast.Name)}
    lengths = [
        len(variables[name])
        for name in names
        if isinstance(variables[name], np.ndarray)
        and variables[name].ndim == 1
    ]
    if not lengths:
        return variables

    shared_samples = min(lengths)
    return {
        name: value[:shared_samples]
        if name in names
        and isinstance(value, np.ndarray)
        and value.ndim == 1
        else value
        for name, value in variables.items()
    }


class Aura:
    def __init__(self, preset: bytes | dict | str, cache=True):
        self.last_note = None
        self.cache = cache
        self.arrays_bank = {}
        if isinstance(preset, bytes):
            try:
                preset_json = zlib.decompress(preset)
                preset = json.loads(preset_json.decode())
            except (zlib.error, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise AURA_ERROR("This preset is corrupt: invalid compressed JSON") from exc

        elif isinstance(preset, str):
            try:
                preset_bytes = decode_baseX(preset)
                preset_json = zlib.decompress(preset_bytes)
                preset = json.loads(preset_json.decode())
            except (ValueError, zlib.error, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise AURA_ERROR(
                    "This preset is corrupt", advice=str(exc)
                ) from exc

        if isinstance(preset, (list, tuple)) and len(preset) == 1:
            preset = preset[0]
        if not isinstance(preset, dict):
            raise AURA_ERROR("This preset is corrupt: expected a preset object")

        meta = preset.get("meta")
        if not isinstance(meta, dict):
            raise AURA_ERROR("This preset is corrupt: 'meta' must be an object")

        for field in ("name", "version", "description", "author", "category"):
            if not isinstance(meta.get(field), str):
                raise AURA_ERROR(
                    f"This preset is corrupt: 'meta.{field}' must be a string"
                )

        if not isinstance(meta.get("tags"), list) or not meta["tags"]:
            raise AURA_ERROR(
                "This preset is corrupt: 'meta.tags' must be a non-empty list"
            )

        master = preset.get("master")
        if not isinstance(master, dict):
            raise AURA_ERROR("This preset is corrupt: 'master' must be an object")
        for field in ("master_gain_db", "legato", "glide", "portamento"):
            if field not in master:
                raise AURA_ERROR(
                    f"This preset is corrupt: missing 'master.{field}'"
                )

        if not isinstance(preset.get("data"), dict) or not preset["data"]:
            raise AURA_ERROR("This preset is corrupt: 'data' must be a non-empty object")
        if not isinstance(preset.get("out"), list) or not preset["out"]:
            raise AURA_ERROR("This preset is corrupt: 'out' must be a non-empty list")

        self.preset = preset
        self.version = preset["meta"]["version"]
        self.name = preset["meta"]["name"]
        self.description = preset["meta"]["description"]
        self.author = preset["meta"]["author"]
        self.category = preset["meta"]["category"]
        self.tags = preset["meta"]["tags"]
        self.description = preset["meta"]["description"]


    def get_note(self, note_hz=261.626, duration=4, velocity=.8, gain_db=-.1) -> np.ndarray:
        """
        Render one note by evaluating this preset's audio graph

        The method builds a context containing the requested note properties,
        evaluates the preset's data nodes (including oscillators and envelopes),
        applies effects at the node and master levels, and sums the configured
        outputs into a stereo audio array. If glide is enabled and a previous
        note was rendered, the pitch can transition from that note according
        to the preset's portamento settings

        Args:
            note_hz: Fundamental frequency of the requested note, in Hz
            duration: Requested note duration, in seconds, the value and the
                sample rate determines the number of samples rendered
            velocity: Relative note intensity made available to preset
                expressions and nodes, defaults to 0.8
            gain_db: Per-call output gain in decibels, this is added to the
                preset's master gain before being applied to the rendered
                audio

        Returns:
            Audio array: Rendered stereo audio with shape (samples, 2), preset
            outputs are converted to stereo and summed, the final array
            includes node effects, master effects, and the combined output
            gain

        Raises:
            AURA_ERROR: If the preset's master settings, data nodes, effects,
                or outputs are invalid, if a data dependency is missing or
                circular, or if the duration is too short to produce samples

        """

        # Read and validate settings used for gain and pitch glide before the cache lookup
        master = self.preset["master"]
        try:
            master_gain_db = float(master["master_gain_db"])
        except (TypeError, ValueError) as exc:
            raise AURA_ERROR("master.master_gain_db must be numeric") from exc

        cache_key = (note_hz, duration, velocity, self.last_note)
        if self.cache and cache_key in self.arrays_bank:
            # Cache unscaled rendering so each call can apply its own output gain
            audio_note = self.arrays_bank[cache_key]
            if self.preset["master"]["glide"]:
                self.last_note = note_hz
            return audio_note * Audio_Effects.Audio_Analysis.dbs_to_float(
                gain_db + master_gain_db
            )

        try:
            portamento = float(master["portamento"])
            portamento_tension = float(master.get("portamento_tension", 0))
        except (TypeError, ValueError) as exc:
            raise AURA_ERROR(
                "master.portamento and master.portamento_tension or master.portamento must be numeric"
            ) from exc
        if portamento < 0:
            raise AURA_ERROR("master.portamento must be non-negative")
        if not -1 <= portamento_tension <= 1:
            raise AURA_ERROR("master.portamento_tension must be in [-1, 1]")


        note_samples = int(round(duration * SAMPLE_RATE))
        if note_samples <= 0:
            raise AURA_ERROR("duration is too short to produce audio samples")

        pitch_env = np.ones(note_samples, dtype=np.float32)
        portamento_progress = np.ones(note_samples, dtype=np.float32)

        if master["glide"] and self.last_note is not None and portamento > 0:
            transition_samples = min(
                note_samples, max(1, int(round(portamento * SAMPLE_RATE)))
            )
            progress = np.linspace(
                0, 1, transition_samples, dtype=np.float32
            )
            curve = _tension_curve(progress, portamento_tension)
            initial_ratio = self.last_note / note_hz
            pitch_env[:transition_samples] = (
                initial_ratio + (1 - initial_ratio) * curve
            )
            portamento_progress[:transition_samples] = progress

        note_number = self.get_note_number(note_hz)
        # Preset formulas and nodes can refer to these built-in note properties
        context = {
            "note_hz": note_hz,
            "note_number": note_number,
            "octave": note_number / 12,
            "duration": duration,
            "duration_progress": np.linspace(
                0, duration, note_samples, dtype=np.float32
            ),
            "velocity": velocity,
            "glide": pitch_env,
            "portamento": portamento_progress,
        }

        data = self.preset["data"]
        node_aliases = {
            name: f"_{index}_"
            for index, name in enumerate(data)
            if isinstance(name, str)
        }
        if any(name in context for name in node_aliases):
            name = next(name for name in node_aliases if name in context)
            raise AURA_ERROR(
                f"Preset data name '{name}' conflicts with a built-in variable"
            )
        data_bank = dict(context)
        resolving = set()
        effect_handlers = {
            "drive": Audio_Effects.Gain_Distortion_Dynamics.drive,
            "bit_crush": Audio_Effects.Gain_Distortion_Dynamics.bit_crush,
            "valve_distortion": Audio_Effects.Gain_Distortion_Dynamics.valve_distortion,
            "la2a": Audio_Effects.Gain_Distortion_Dynamics.compressor_la2a,
            "compressor_la2a": Audio_Effects.Gain_Distortion_Dynamics.compressor_la2a,
            "br11ck67_analog": Audio_Effects.Gain_Distortion_Dynamics.br11ck67_analog,
            "reverb": Audio_Effects.Stereo_Expansion.reverb,
            "stereo_expander": Audio_Effects.Stereo_Expansion.stereo_expander,
            "delay": Audio_Effects.Stereo_Expansion.delay,
            "normalize": Audio_Effects.Special.normalize,
            "invert_phase": Audio_Effects.Special.invert_phase,
            "reverse": Audio_Effects.Special.reverse,
            "fade_in": Audio_Effects.Special.fade_in,
            "fade_out": Audio_Effects.Special.fade_out,
            "parametricEq": Audio_Effects.Filters_Equalization.parametricEq,
        }
        
        def apply_effects(audio, effects, scope):
            # Resolve effect parameters through the same preset expression system as node values
            if not isinstance(effects, dict):
                raise AURA_ERROR(f"{scope} effects must be an object")
            for effect_name, effect_values in effects.items():
                handler = effect_handlers.get(effect_name)
                if handler is None:
                    raise AURA_ERROR(
                        f"Unsupported effect '{effect_name}' in {scope}"
                    )
                if effect_values is True:
                    effect_values = {}
                if not isinstance(effect_values, dict):
                    raise AURA_ERROR(
                        f"Effect '{effect_name}' parameters must be an object"
                    )
                parameters = {
                    key: self._preset_value(
                        value, data_bank, node_aliases, resolve_node
                    )
                    for key, value in effect_values.items()
                }
                if effect_name == "drive" and "gain_db" in parameters:
                    parameters["gain_dbs"] = parameters.pop("gain_db")
                audio = np.asarray(handler(audio, **parameters), dtype=np.float32)
            return audio

        def resolve_node(name):
            if name in data_bank:
                return data_bank[name]
            if name not in data:
                raise AURA_ERROR(f"Unknown preset data node: {name}")
            if name in resolving:
                raise AURA_ERROR(f"Circular preset data dependency: {name}")

            resolving.add(name)
            try:
                definition = data[name]
                alias = node_aliases.get(name)
                # Envelope and oscillator nodes are rendered specially, other nodes are expressions or values
                if isinstance(definition, dict) and "DAHDSR_envelope" in definition:
                    stages = definition["DAHDSR_envelope"]
                    if not isinstance(stages, dict):
                        raise AURA_ERROR(
                            f"Envelope '{name}' must contain an object"
                        )
                    parameters = {
                        key: self._preset_value(
                            value, data_bank, node_aliases, resolve_node
                        )
                        for key, value in stages.items()
                    }
                    required = (
                        "delay", "attack", "hold", "decay",
                        "sustain_level", "sustain", "release",
                    )
                    missing = [key for key in required if key not in parameters]
                    if missing:
                        raise AURA_ERROR(
                            f"Envelope '{name}' is missing: {', '.join(missing)}"
                        )
                    if any(
                        np.asarray(value).ndim != 0
                        for value in parameters.values()
                    ):
                        raise AURA_ERROR(
                            f"Envelope '{name}' timing and levels must be scalar"
                        )
                    result = Envelopes.DAHDSR_envelope(**parameters)
                elif isinstance(definition, dict) and "waveform" in definition:
                    waveform = definition["waveform"]
                    if not isinstance(waveform, str):
                        raise AURA_ERROR(
                            f"Oscillator '{name}' waveform must be a string"
                        )
                    oscillator_duration = self._preset_value(
                        definition.get("duration", duration),
                        data_bank,
                        node_aliases,
                        resolve_node,
                    )
                    if np.asarray(oscillator_duration).ndim != 0:
                        raise AURA_ERROR(
                            f"Oscillator '{name}' duration must be scalar"
                        )
                    oscillator_duration = float(oscillator_duration)
                    if oscillator_duration < 0:
                        raise AURA_ERROR(
                            f"Oscillator '{name}' duration must be non-negative"
                        )
                    oscillator_samples = int(
                        round(oscillator_duration * SAMPLE_RATE)
                    )
                    if oscillator_samples <= 0:
                        result = np.zeros(0, dtype=np.float32)
                    else:
                        if waveform not in {
                            "sine", "square", "sawtooth", "triangle",
                            "noise", "silence",
                        }:
                            raise AURA_ERROR(
                                f"Unsupported waveform '{waveform}' in '{name}'"
                            )

                        stretch = self._preset_value(
                            definition.get("stretch", 0.0),
                            data_bank,
                            node_aliases,
                            resolve_node,
                        )
                        amplitude = self._preset_value(
                            definition.get("amplitude", 1.0),
                            data_bank,
                            node_aliases,
                            resolve_node,
                        )
                        frequency = self._preset_value(
                            definition.get("frequency", note_hz),
                            data_bank,
                            node_aliases,
                            resolve_node,
                        )
                        parameter_lengths = [
                            len(value)
                            for value in (amplitude, stretch, frequency)
                            if isinstance(value, np.ndarray) and value.ndim == 1
                        ]
                        rendered_samples = min(
                            [oscillator_samples, note_samples, *parameter_lengths]
                        )
                        if rendered_samples == 0:
                            result = np.zeros(0, dtype=np.float32)
                        else:
                            def clip_parameter(value):
                                if isinstance(value, np.ndarray) and value.ndim == 1:
                                    return value[:rendered_samples]
                                return value

                            amplitude = clip_parameter(amplitude)
                            stretch = clip_parameter(stretch)
                            frequency = clip_parameter(frequency)
                            if waveform != "noise" and waveform != "silence":
                                frequency = np.asarray(
                                    frequency, dtype=np.float32
                                ) * pitch_env[:rendered_samples]
                            if waveform == "noise":
                                result = WaveTables.noise(
                                    rendered_samples, amplitude
                                )
                            elif waveform == "silence":
                                result = np.zeros(
                                    rendered_samples, dtype=np.float32
                                )
                            else:
                                generator = {
                                    "sine": WaveTables.sine,
                                    "square": WaveTables.square,
                                    "sawtooth": WaveTables.sawtooth,
                                    "triangle": WaveTables.triangle,
                                }[waveform]
                                parameters = {
                                    "frequency": frequency,
                                    "amplitude": amplitude,
                                }
                                if waveform != "sine":
                                    parameters["stretch"] = stretch
                                result = generator(rendered_samples, **parameters)

                        effects = definition.get("effects", {})
                        result = apply_effects(
                            result, effects, f"oscillator '{name}'"
                        )
                else:
                    result = self._preset_value(
                        definition, data_bank, node_aliases, resolve_node
                    )

                result_values = np.asarray(result)
                if result_values.dtype.kind not in "iuf":
                    raise AURA_ERROR(
                        f"Preset data node '{name}' must contain real numbers"
                    )
                if result_values.ndim > 2 or (
                    result_values.ndim == 2 and result_values.shape[1] not in (1, 2)
                ):
                    raise AURA_ERROR(
                        f"Preset data node '{name}' returned an invalid array shape"
                    )
                result = result_values.astype(np.float32, copy=False)
                if alias is not None:
                    data_bank[alias] = result
                return result
            finally:
                resolving.remove(name)

        # Convert each configured output to stereo, then sum outputs with zero-padding
        output_arrays = []
        for output_name in self.preset["out"]:
            if not isinstance(output_name, str):
                raise AURA_ERROR("Preset output names must be strings")
            output = resolve_node(output_name)
            output = Audio_Effects.Stereo_Expansion.to_stereo(
                np.asarray(output, dtype=np.float32)
            )
            if output.ndim != 2 or output.shape[1] != 2:
                raise AURA_ERROR(
                    f"Preset output '{output_name}' must be mono or stereo audio"
                )
            output_arrays.append(output)

        output_samples = max(len(output) for output in output_arrays)
        audio_note = np.zeros(
            (output_samples, 2),
            dtype=np.float32,
        )
        for output in output_arrays:
            audio_note[:len(output)] += output

        # Master effects operate on the combined signal, gain is applied after caching
        audio_note = apply_effects(
            audio_note, master.get("effects", {}), "master"
        )

        if self.cache:
            self.last_note = note_hz
            self.arrays_bank[cache_key] = audio_note

        return audio_note * Audio_Effects.Audio_Analysis.dbs_to_float(
            gain_db + master_gain_db
        )


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

    @staticmethod
    def _insert_multiplication_operators(expression):
        result = ""
        for i, char in enumerate(expression):
            if char == "(" and i > 0 and expression[i-1].isdigit():
                result += f"*{char}"
            elif char == ")" and i < len(expression) - 1 and expression[i+1].isdigit():
                result += f"{char}*"
            else:
                result += char
        return result

    def _preset_value(self, value, data_bank, node_aliases, resolve_node):
        if isinstance(value, (bool, int, float, np.number)):
            return value
        if isinstance(value, (list, tuple, np.ndarray)):
            return np.asarray(value, dtype=np.float32)
        if not isinstance(value, str):
            raise AURA_ERROR(f"Unsupported preset value type: {type(value).__name__}")

        # Replace complete identifiers only, so names like env1 and env10 stay distinct
        expression, referenced_names = _replace_preset_names(
            value, node_aliases
        )
        for name in referenced_names:
            if name in node_aliases:
                resolve_node(name)
        return self._maths(expression, data_bank)

    def _maths(self, expression, _vars=None):
        variables = {} if _vars is None else dict(_vars)
        expression = self._insert_multiplication_operators(
            expression.replace("...", "").replace("()", "")
        )
        try:
            parsed = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise AURA_ERROR(f"Invalid formula or syntax '{expression}'") from exc

        _validate_preset_expression(parsed, expression, variables)
        variables = _align_preset_arrays(parsed, variables)

        try:
            return eval(
                compile(parsed, "<preset expression>", "eval"),
                {"__builtins__": {}},
                variables,
            )
        except (ArithmeticError, NameError, TypeError, ValueError) as exc:
            raise AURA_ERROR(f"Invalid formula or syntax '{expression}'") from exc


    rb"""Save the preset in different formats for storage or transmission"""

    @property
    def get_bin_preset(self):
        """
        Convert the preset dictionary to a binary format for storage or transmission
        """
        preset_json = json.dumps(self.preset, separators=(",", ":"))

        return zlib.compress(
            preset_json.encode("utf-8"), level=9
            )

    @property
    def get_SBR_string_preset(self):
        """
        Convert the preset dictionary to a string format for storage or transmission
        """

        max_leng = 70
        code = f"""\""
{self.category.upper()} | {self.name}
{self.author}
{" | ".join(self.tags)}
{self.description}
Aura version: {self.version}
\"""".strip()
        code += "\ninstrument {\"" + self.get_baseX_preset + "\"}"
        code = "\n".join(
            code[index:index + max_leng]
            for index in range(0, len(code), max_leng)
        )
        return code + "\n"


    def __str__(self):
        return self.get_SBR_string_preset

    def __repr__(self):
        return str(self)



    @property
    def get_baseX_preset(self):
        """
        Convert the compressed preset to BaseX for text storage or transmission
        """
        return encode_baseX(self.get_bin_preset)

    @property
    def get_json_preset(self):
        """
        Convert the preset dictionary to a string format for storage or transmission
        """
        return json.dumps(self.preset, separators=(",", ":"))[1:-1]

