from scipy.signal import lfilter
import soundfile as sf
import numpy as np
import time


"""
This module typically works with 32-bit stereo audio
unless specified otherwise in specific module functions

Automations are low-frequency arrays returned as parameters for those automations

"""


SAMPLE_RATE = 44_100

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
            Extracts the side (difference) signal from stereo audio
            Returns a mono signal where L = L - R
            """
            if input_audio.ndim == 1:
                return np.zeros_like(input_audio)  # No side info in mono
            return input_audio[:, 0] - input_audio[:, 1]  # L - R

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

            return (b0/a0, b1/a0, b2/a0, a1/a0, a2/a0)

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


# def play_array(audio_data, sample_rate=44100, sleep=False):
#     """Play an audio array."""
#     audio_data_int16 = (audio_data * 2**15 * 0.9).astype(np.int16)
#     audio_data_int16 = np.ascontiguousarray(audio_data_int16)
#     sound = mixer.Sound(array=audio_data_int16)
#     sound.play()
#     if sleep:
#         time.sleep((1/sample_rate) * len(audio_data))



def main():
    duration = 2
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

    # Generate test signal (1kHz tone)
    audio = np.sin(2 * np.pi * 1000 * t)

    # Create automations
    freq_automation = np.linspace(100, 5000, len(t))  # Frequency sweep
    q_automation = np.ones(len(t)) * 0.707  # Constant Q
    gain_automation = np.sin(t * np.pi) * 12  # Variable gain

    # Apply equalization
    processed_audio = Audio_Effects.Filters_Equalization.time_varying_eq(
        audio, freq_automation, q_automation, gain_automation
    )

    # Save result
    sf.write("processed_audio.wav", processed_audio, SAMPLE_RATE)


if __name__ == "__main__":
    main()
