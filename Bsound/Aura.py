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

    "master": {
        "master_gain_db": -0.1,
        "legato": True,
        "glide": True,
        "portamento": .045, #this is the time in seconds for the glide effect
        "portamento_tension": 0, # this goes from -1 to 1
        "effects": {
            # Add compression
            "la2a": {
                "peak_reduction": 50.0,
                "gain": 50.0,
                "ratio": 5,
            },
            "reverb": {
                "room_size": 0.98,
                "wet_level": 0.35,
                "dry_level": 0.65,
                "width": 1.2,
            },
        },
    },

    # Variables (They can be used as parameters for automations, LFOs, and envelopes)
    # inside variables you can use mathematical operators to create complex modulation

    # "note_hz", example: "note_hz * 2" for an octave above

    # "note_number", example: "note_number + 12" for an octave above
    # it can also be used to control the intensity of a parameter
    # for example, if you want fewer harmonics in the treble
    # you can use "note_number / 127" to control the number of harmonics

    # "octave" is note_number / 12
    # "glide" is the pitch-ratio array for the current note

    # "duration" is a constant indicating how long it lasts, expressed in seconds
    # "duration_progress" is an array progressing from 0 to duration in seconds

    # "velocity" put this variable after a "1-" and connect it to the ADSR attack
    # it will sound softer if you play more gently and stronger if you play hard, like a real instrument
    # "1-velocity" (goes from 1 to 0) and not the other way around

    # "portamento" (goes from 0 to 1) in how long it takes to complete the glide

    "data": {
        # oscillators, ADSR envelopes, and LFOs are defined in this dictionary
        # there are only 2 data types: numbers and arrays
        # and all are valid in all effect, oscillator, and LFO inputs

        # This "osc1" is optional; you can easily name it "papi rupi" if you want
        # this works like variables that store waveforms with values you can place anywhere else
        # and be careful: a variable name for the oscillator, envelope, or anything else stored in "data"
        # cannot match an effect name or any reserved word
        # the standard is to call oscillators "oscX"
        # and envelopes "envX", sometimes with an additional description
        "osc1": {
            # Available waveform types: sine, square, sawtooth, triangle, noise, silence
            "waveform": "square",
            "frequency": "note_hz * vibrato",
            "amplitude": "velocity * env1",
            "stretch": "duration_progress ",
            "duration": "duration",
            "effects": {
                "drive": {
                    "gain_db": 20,
                    "normalize": True,
                },
            },
        },
        "vibrato": {
            "waveform": "square",
            "frequency": 8,
            "amplitude": "duration_progress * .5",
            "stretch": 0,
            "duration": "duration",
        },
        "env1": {
            # All oscillators/envelopes must have a "waveform" or a "DAHDSR_envelope"
            # The compiler will look for one or the other to find other parameters
            "DAHDSR_envelope": {
                # Delay before the envelope starts, in seconds (>= 0)
                "delay": 0,
                # Attack duration until the envelope reaches its maximum, in seconds
                # This can easily be "1.125 - velocity * 1.1"
                # so it has less attack if played harder
                "attack": 0.25,
                # Time held at maximum level before decay, in seconds
                "hold": 0.2,
                # Duration of the fall from maximum to sustain level, in seconds
                "decay": .5,
                # Sustain amplitude in [0, 1]; 1 is maximum and 0 is silence
                "sustain_level": 0.5,
                # Duration of the sustain phase, in seconds
                "sustain": 0.5,
                # Duration of the release from sustain level to silence, in seconds
                "release": 2,

                # Attack curve tension in [-1, 1]: positive rises faster initially
                "attack_tension": 0.25,
                # Decay curve tension in [-1, 1]
                "decay_tension": -0.25,
                # Release curve tension in [-1, 1]
                "release_tension": 0.25,
            },
        },
    },

    # Not all oscillators need to be routed to the master output
    "out": [
        "osc1",
        ]
},


from scipy.signal import butter, lfilter_zi, lfilter, resample_poly
import soundfile as sf
from numba import jit, prange
import numpy as np
import ast
import time
import json
import zlib


SAMPLE_RATE = 44_100


def _tension_curve(progress: np.ndarray, tension: float) -> np.ndarray:
    """Map 0..1 progress to a normalized logarithmic curve"""
    progress = np.clip(progress, 0, 1)
    if tension > 0:
        curvature = 10 ** (2 * tension) - 1
        return np.log1p(curvature * progress) / np.log1p(curvature)
    if tension < 0:
        curvature = 10 ** (-2 * tension) - 1
        return 1 - (
            np.log1p(curvature * (1 - progress)) / np.log1p(curvature)
        )
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

    def vinyl(samples, db=-18):
        data = WaveTables.sample("vinyl.ogg")
        if samples == 0:
            return np.zeros((0, data.shape[1]), dtype=data.dtype)
        if len(data) < samples:
            data = np.tile(data, (int(np.ceil(samples / len(data))), 1))
        return data[:samples] * (10 ** (db / 20))

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
            np.zeros(int(round(delay * SAMPLE_RATE)), dtype=np.float64)
        ]

        attack_count = int(round(attack * SAMPLE_RATE))
        if attack_count:
            progress = np.arange(attack_count, dtype=np.float64) / attack_count
            segments.append(_tension_curve(progress, attack_tension))

        hold_count = int(round(hold * SAMPLE_RATE))
        if hold_count:
            segments.append(np.ones(hold_count, dtype=np.float64))

        decay_count = int(round(decay * SAMPLE_RATE))
        if decay_count:
            progress = np.arange(decay_count, dtype=np.float64) / decay_count
            curve = _tension_curve(progress, decay_tension)
            segments.append(1 + (sustain_level - 1) * curve)

        sustain_count = int(round(sustain * SAMPLE_RATE))
        if sustain_count:
            segments.append(
                np.full(sustain_count, sustain_level, dtype=np.float64)
            )

        release_count = int(round(release * SAMPLE_RATE))
        if release_count:
            progress = np.arange(release_count, dtype=np.float64) / release_count
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
            audio_output = np.tanh(
                audio_input * 
                Audio_Effects.Audio_Analysis.dbs_to_float(gain_dbs)
                )
            if normalize:
                audio_output /= np.max(np.abs(audio_output))
            return audio_output

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
            audio = np.asarray(audio)
            output_dtype = (
                audio.dtype
                if audio.dtype in (np.dtype(np.float32), np.dtype(np.float64))
                else np.dtype(np.float64)
            )
            if audio.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
                audio = audio.astype(np.float64)
            if (
                audio.ndim not in (1, 2)
                or audio.shape[0] == 0
                or (audio.ndim == 2 and audio.shape[1] not in (1, 2))
            ):
                raise ValueError("Audio must be a non-empty mono or stereo array")
            if not np.all(np.isfinite(audio)):
                raise ValueError("Audio must contain only finite values")
            if not np.isfinite(gain_db):
                raise ValueError("gain_db must be a finite value")

            drive_gain = Audio_Effects.Audio_Analysis.dbs_to_float(gain_db)
            if not np.isfinite(drive_gain):
                raise ValueError("gain_db produces a non-finite gain")

            oversampling = 4
            audio = resample_poly(audio, oversampling, 1, axis=0)

            # Single common-cathode 12AX7 stage; circuit values are explicit
            supply_voltage = 250.0
            plate_load = 100_000.0
            grid_bias = -1.5
            mu, exponent, kg1, kp, kvb = 100.0, 1.4, 1060.0, 600.0, 300.0

            quiescent_plate = Audio_Effects.Gain_Distortion_Dynamics._triode12ax7_solve_plate_voltage(
                np.asarray([grid_bias], dtype=np.float64),
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

            return distorted_audio.astype(output_dtype, copy=False)


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
            audio_procesado = Audio_Effects.Gain_Distortion_Dynamics._t4_cell_and_tube_dsp(
                audio, peak_reduction, gain, ratio)

            return audio_procesado


        @jit(nopython=True, cache=True)
        def _1176_analog_core(audio_in, input_gain_lin, output_gain_lin, att_coef, rel_coef, ratio, thresh_db):
            """
            1176 core processing sample by sample
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
            Main 1176 controller with anti-aliasing oversampling

            Parameters:
            - audio_in: NumPy array (mono or processed channel by channel)
            - oversampling: 1 (Off), 2, 4, or 8. (4x recommended for analog distortion without aliasing)
            """
            audio_in = np.asarray(audio_in)
            mono_input = audio_in.ndim == 1
            if mono_input:
                audio_in = audio_in[:, np.newaxis]
            elif audio_in.ndim != 2:
                raise ValueError("Audio must be mono or stereo")
            if audio_in.shape[0] == 0 or audio_in.shape[1] not in (1, 2):
                raise ValueError("Audio must have samples and one or two channels")
            if audio_in.dtype not in (np.dtype(np.float32), np.dtype(np.float64)):
                audio_in = audio_in.astype(np.float64)
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
            processed_up = Audio_Effects.Gain_Distortion_Dynamics._1176_analog_core(
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
            return processed[:, 0] if mono_input else processed

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
            
            # Calculate the longest possible delay
            # The right channel has an extra 'spread', so the maximum effective delay is:
            # Max Base Delay + (20 * width)
            max_delay_base = max(comb_delays)
            max_effective_delay = max_delay_base + (20 * width)

            # Safety: room_size cannot be >= 1.0 (infinite feedback)
            if room_size >= 1:
                raise AURA_ERROR("Room_size cannot be >= 1.0 (infinite feedback)")
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
            Expands a mono signal by panning across 32 alternating bands

            ``mix`` blends the expanded signal with the original mono signal
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
        def vinyl_stretching(data, factor):
            if not factor:
                return data
            return Audio_Effects.Tuning_Stretching.resampling(data, int(factor * SAMPLE_RATE), SAMPLE_RATE)

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

0123456789aàáâãäåăæbcçdðeèéêëfghiìíîïĳjklmnñoòóôõöøœpqrsšșt
țuùúûüvwxyýÿzþßAÀÁÂÃÄÅÆBCÇDÐEÈÉÊËFGHIÌÍÎÏĲJKLMNÑOÒÓÔÕÖØŒPQR
SŠȘTȚUÙÚÛÜVWXYÝZÞẞ!"#$%&'()*+,-./:;<=>?@[]^_`{|}~¡¢£¤¥§©«®°
±²³µ¶·»¿×÷

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
                raise AURA_ERROR("This preset is corrupt", advice=str(exc)) from exc

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


    def get_note(self, note_hz=261.626, duration=4, velocity=.8, gain_db=-.1) -> np.ndarray:
        """
        Generate a note from the preset with the specified frequency and duration

        Args:
            note_hz: Fundamental frequency of the note, in Hz
            duration: Duration of the note, in seconds
            velocity: Relative intensity of the note (default, 0.8)
            gain_db: The final gain

        Returns:
            np.ndarray: Audio array with the generated note, in stereo format (2 channels)

        """


        master = self.preset["master"]
        try:
            master_gain_db = float(master["master_gain_db"])
        except (TypeError, ValueError) as exc:
            raise AURA_ERROR("master.master_gain_db must be numeric") from exc

        try:
            portamento = float(master["portamento"])
            portamento_tension = float(master.get("portamento_tension", 0))
        except (TypeError, ValueError) as exc:
            raise AURA_ERROR(
                "master.portamento and master.portamento_tension must be numeric"
            ) from exc
        if portamento < 0:
            raise AURA_ERROR("master.portamento must be non-negative")
        if not -1 <= portamento_tension <= 1:
            raise AURA_ERROR("master.portamento_tension must be in [-1, 1]")

        previous_note = self.last_note
        glide_source = (
            previous_note
            if (
                master["glide"]
                and portamento > 0
                and previous_note is not None
                and previous_note != note_hz
            )
            else None
        )
        cache_key = (note_hz, duration, velocity, glide_source)
        if self.cache and cache_key in self.arrays_bank:
            audio_note = self.arrays_bank[cache_key]
            self.last_note = note_hz
            return audio_note * Audio_Effects.Audio_Analysis.dbs_to_float(
                gain_db + master_gain_db
            )

        note_samples = int(round(duration * SAMPLE_RATE))
        if note_samples <= 0:
            raise AURA_ERROR("duration is too short to produce audio samples")

        pitch_env = np.ones(note_samples, dtype=np.float64)
        portamento_progress = np.ones(note_samples, dtype=np.float64)

        if master["glide"] and previous_note is not None and portamento > 0:
            transition_samples = min(
                note_samples, max(1, int(round(portamento * SAMPLE_RATE)))
            )
            progress = np.linspace(0, 1, transition_samples)
            curve = _tension_curve(progress, portamento_tension)
            initial_ratio = previous_note / note_hz
            pitch_env[:transition_samples] = (
                initial_ratio + (1 - initial_ratio) * curve
            )
            portamento_progress[:transition_samples] = progress

        note_number = self.get_note_number(note_hz)
        context = {
            "note_hz": note_hz,
            "note_number": note_number,
            "octave": note_number / 12,
            "duration": duration,
            "duration_progress": np.linspace(0, duration, note_samples),
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
            "normalize": Audio_Effects.Special.normalize,
            "invert_phase": Audio_Effects.Special.invert_phase,
            "reverse": Audio_Effects.Special.reverse,
            "fade_in": Audio_Effects.Special.fade_in,
            "fade_out": Audio_Effects.Special.fade_out,
        }

        def apply_effects(audio, effects, scope):
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
                audio = handler(audio, **parameters)
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
                                frequency = np.asarray(frequency) * pitch_env[
                                    :rendered_samples
                                ]
                            if waveform == "noise":
                                result = WaveTables.noise(
                                    rendered_samples, amplitude
                                )
                            elif waveform == "silence":
                                result = np.zeros(rendered_samples)
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
                if alias is not None:
                    data_bank[alias] = result
                return result
            finally:
                resolving.remove(name)

        output_arrays = []
        for output_name in self.preset["out"]:
            if not isinstance(output_name, str):
                raise AURA_ERROR("Preset output names must be strings")
            output = resolve_node(output_name)
            output = Audio_Effects.Stereo_Expansion.to_stereo(
                np.asarray(output)
            )
            if output.ndim != 2 or output.shape[1] != 2:
                raise AURA_ERROR(
                    f"Preset output '{output_name}' must be mono or stereo audio"
                )
            output_arrays.append(output)

        output_samples = max(len(output) for output in output_arrays)
        audio_note = np.zeros(
            (output_samples, 2),
            dtype=np.result_type(*(output.dtype for output in output_arrays), np.float32),
        )
        for output in output_arrays:
            audio_note[:len(output)] += output

        audio_note = apply_effects(
            audio_note, master.get("effects", {}), "master"
        )

        if self.cache:
            self.arrays_bank[cache_key] = audio_note
        self.last_note = note_hz
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
            return np.asarray(value)
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
        var_name = self.preset["meta"]["name"].replace(" ", "_").lower()
        data = f"$\"{self.get_baseX_preset}\""
        code = f"{var_name} = {data}"
        code = "\n".join(
            code[index:index + max_leng]
            for index in range(0, len(code), max_leng)
        )

        return code


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



def main():
    # python -m cProfile -s tottime Bsound/Aura.py
    """Create an audio array"""

    #audio_data = WaveTables.sample("Bsound/guitar_test.mp3")

    # ***************

    sint1 = Aura(preset_example)

    audio_data = sint1.get_note()
    # ***************

    start_time = time.perf_counter()

    # ***************

    audio_data = sint1.get_note()

    # ***************


    elapsed = time.perf_counter() - start_time
    print(f"Took {elapsed:.3f} seconds")

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


    """Play an audio array"""
    import pygame

    pygame.mixer.pre_init(frequency=SAMPLE_RATE, size=-16, channels=2)
    pygame.init()

    #sf.write("output.wav", audio_data, SAMPLE_RATE)

    audio_data_int16 = np.clip(
        audio_data * (2**15 * .9), -2**15, 2**15 - 1
    ).astype(np.int16)
    audio_data_int16 = np.ascontiguousarray(audio_data_int16)
    sound = pygame.mixer.Sound(array=audio_data_int16)
    sound.play()
    time.sleep((1/SAMPLE_RATE) * len(audio_data))


if __name__ == "__main__":
    main()

