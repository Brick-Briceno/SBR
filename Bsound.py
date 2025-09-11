"""
Symmetry Melody Api v2.1
@Brick_briceno 2023
"""
from variables import variables_user
from lib.synthesizer import create_tone
from errors import SBR_ERROR
from sbr_utils import *
from sbr_types import *

try: import soundfile as sf
except ImportError:
    print("Missing soundfile library")

from pygame import mixer
import numpy as np
#import numba as nb
import random
import time
#import os

"""
pip install pygame
pip install soundfile
pip install numpy
pip install numba
"""

"Configurar Variables"

#audio vars
sample_rate = 44100
arrays_bank = {}
volumen = 1

#motor config
valve_distortion_gain = 0 #40
random_stereo_value = .6
random_tunin_cst = 0
humanize_ms = 0

mixer.pre_init(sample_rate, -16, 2, 1024)
mixer.init()

sound = None

def play_array(audio_data, sleep=False):
    pause()
    # Convertir a int16
    global sound
    audio_data_int16 = (audio_data * 2**15*.9).astype(np.int16)
    audio_data_int16 = np.ascontiguousarray(audio_data_int16)
    # Reproducir el audio
    sound = mixer.Sound(array=audio_data_int16)
    sound.play()
    #Thread(target=sa.play_buffer, args=(audio_data_int16, 2, 2, sample_rate)).start()
    if sleep: time.sleep((1/sample_rate)*len(audio_data))

def pause():
    if sound is None: return
    sound.fadeout(800)


def audio_render_engine(meta_data):
    note_path, when_kick = meta_data["files"], meta_data["position"]
    effects, velocity = meta_data["effect"], meta_data["velocity"]
    panning, duration = meta_data["panning"], meta_data["duration"]
    cromatic_note, afination = meta_data["cromatic_note"], meta_data["afination_cst"]

    if not len(note_path): raise SBR_ERROR("Empty data")
    #cargar archivos necesarios en un diccionario
    for _file in note_path:
        if _file not in arrays_bank.keys():
            try:
                #verificar si el sonido es sintetico
                if len(_file) == 1:
                    #crear el tono sintetico
                    old_hz = sample_rate
                    arrays_bank[_file] = create_tone(ord(_file), .3, sample_rate)
                else: arrays_bank[_file], old_hz = sf.read(_file)
            except sf.LibsndfileError: raise SBR_ERROR(f"Error loading file: {_file}")
            except TypeError: raise SBR_ERROR(f"Error in audio engine")
            #quitar espacios en silencio
            arrays_bank[_file] = audio_effects.remove_ending_in_silence(arrays_bank[_file])
            #verificar si tiene la misma frecuencia de muestreo y bits
            if old_hz != sample_rate:
                arrays_bank[_file] = audio_effects.resampling(
                    arrays_bank[_file], sample_rate, old_hz).astype(np.float32)

            #verificar si es audio estereo
            if len(arrays_bank[_file].shape) == 1:
                arrays_bank[_file] = arrays_bank[_file].reshape(-1, 1)
                arrays_bank[_file] = np.repeat(arrays_bank[_file], 2, axis=1)

    total_muestras = 0
    #Obtener la duración total de muestras requerida para la mezcla
    for _file, when, af in zip(note_path, when_kick, afination, strict=True):
        if af == 0: durtn = sample_rate*when + len(arrays_bank[_file])
        else: durtn = sample_rate*when + len(arrays_bank[_file])/af/.01
        if total_muestras < durtn:
            total_muestras = int(durtn)+5

    #Crear un array de ceros para almacenar la mezcla (array en silencio)
    mixed_audio = np.zeros((total_muestras, 2), dtype=np.float32)

    #procesar datos y efectos
    for note_path, when_kick, fx, v, panning, duration, _, af in zip(
        note_path, when_kick, effects, velocity, panning, duration, cromatic_note, afination, strict=True):

        #Cargar el archivo de audio
        #verificar si se debe estrirar el audio antes de resamplearlo
        #esto ayuda a que el audio no pierda resolucion al cambiar el sample rate
        if af != 0:
            audio_data, hz = sf.read(note_path)
            audio_data = audio_data.astype(np.float32)
            audio_data = audio_effects.remove_ending_in_silence(audio_data)
            audio_data = audio_effects.vinyl(audio_data, af)
            audio_data = audio_effects.resampling(audio_data,
                        sample_rate_old=hz, new_sample_rate=sample_rate)
        else: audio_data = arrays_bank[note_path]
        #Obtener el tiempo de inicio
        tiempo_inicio = int(when_kick * sample_rate)
        #panning
        audio_data = audio_effects.pan_sound(audio_data, panning)
        #afination

        #velocity
        audio_data *= v

        #effects
        if fx == 7:
            if when_kick == 0: continue
            audio_data = audio_data[::-1]
            tiempo_inicio -= len(audio_data)

            if tiempo_inicio < 0: #cortar cola si empieza antes del segundo 0
                audio_data = audio_data[1+~tiempo_inicio:]
                tiempo_inicio = 0

        #Superponer el sonido en el resultado (mezcla los canales individualmente)
        mixed_audio[tiempo_inicio:tiempo_inicio+len(audio_data), :] += audio_data

    mixed_audio = audio_effects.remove_ending_in_silence(mixed_audio)
    if np.max(mixed_audio) == 0: raise SBR_ERROR("Empty audio")
    #normalizar la mezcla (opcional)
    mixed_audio /= np.max(np.abs(mixed_audio))
    #distorsion de valvula
    mixed_audio = audio_effects.valve_distortion(
        mixed_audio, gain=valve_distortion_gain)
    #normalizar la mezcla (opcional)
    #mixed_audio /= np.max(np.abs(mixed_audio)) # esto ya lo hace la distorsion de valvula
    #regular volumen
    mixed_audio *= volumen
    #retornar el array
    return mixed_audio


"audio effects"

class audio_effects:
    def pan_sound(sound, pan):
        # Asegúrate de que el sonido tenga 2 canales
        if sound.shape[1] != 2:
            raise ValueError("El sonido debe tener 2 canales (estéreo)")

        # Calcula las ganancias para los canales izquierdo y derecho
        left_gain = np.sqrt(0.5 * (1 - pan))
        right_gain = np.sqrt(0.5 * (1 + pan))

        # Aplica las ganancias a los canales
        panned_sound = np.zeros_like(sound)
        panned_sound[:, 0] = sound[:, 0] * left_gain  # Canal izquierdo
        panned_sound[:, 1] = sound[:, 1] * right_gain  # Canal derecho
        return panned_sound

    def resampling(audio_data, sample_rate_old, new_sample_rate):
        # Calcular el número de muestras para la nueva frecuencia de muestreo
        ratio = new_sample_rate / sample_rate_old
        num_muestras_nuevo = int(len(audio_data) * ratio)

        # Crear los índices originales y nuevos
        indices_originales = np.arange(len(audio_data))
        indices_nuevos = np.linspace(0, len(audio_data) - 1, num_muestras_nuevo)

        # Interpolar para obtener el audio reesampleado
        if audio_data.ndim == 1:  # Audio mono
            audio_reesampleado = np.interp(indices_nuevos, indices_originales, audio_data)
        else:  # Audio estéreo o multicanal
            audio_reesampleado = np.array([
                np.interp(indices_nuevos, indices_originales, audio_data[:, i])
                for i in range(audio_data.shape[1])]).T

        return audio_reesampleado

    def vinyl(data, n):
        if not n: return data
        return audio_effects.resampling(data, int(n*sample_rate), sample_rate)

    def float_to_dbs(muestra, valor_referencia=1):
        #valor_referencia = 1 #32bits fotante
        valor_pico = np.abs(np.max(muestra))
        db_pico = 20 * np.log10(valor_pico / valor_referencia)
        return db_pico

    def dbs_to_float(db_pico, valor_referencia=1):
        valor_pico = valor_referencia * 10**(db_pico / 20)
        return valor_pico

    # @nb.njit
    # def limitador_16bits(data, umbral=-1, ms=10):
    #     #función no terminada
    #     umbral_int = 2**15*10**(umbral/20)
    #     for x in data:
    #         (x[0]+x[1])/2


    #@nb.njit
    def remove_ending_in_silence(audio, umbral=10e-4):
        # Encontrar el último índice donde el audio supera el umbral
        indice_final = np.where(np.abs(audio) > umbral)[0][-1]
        # Cortar el audio hasta ese índice
        return audio[:indice_final + 1]


    def valve_distortion(audio_input: np.ndarray, gain=1.2) -> np.ndarray:
        if gain == 0: return audio_input
        #parámetros del modelo de una válvula 12AX7 (por ejemplo, un 12AX7)
        # Voltajes de polarización de la válvula (ejemplo)
        Vpk = 275  # Voltaje de placa
        Vgk = -2   # Voltaje de rejilla (polarización)

        k_p = 600  # Parámetro para el exponente
        k_vb = 300  # Voltaje de polarización
        mu = 100  # Factor de amplificación
        Ex = 1.4  # Coeficiente
        v = 6.3

        # La entrada de la rejilla es la suma del voltaje de polarización y la señal de audio
        # Tienes que escalar el audio para que se ajuste al rango de voltaje de la válvula
        V_audio = audio_input * v  # Ajusta este valor según tu necesidad
        V_total = Vgk + V_audio
        # Calcula la corriente de placa (Ip) usando la fórmula de Koren
        # Evitar la división por cero y logaritmos de números negativos
        V_term = Vpk + Ex * np.log(1 + np.exp(V_total / Ex))
        # Manejar el caso de logaritmo de un número negativo
        log_arg = (V_term / mu) - (V_total / gain)
        # Establecer los valores negativos en 0 para evitar log(negativo)
        log_arg[log_arg < 0] = 0.0
        Ip = (k_p * np.log(1 + np.exp((k_p * np.log(1 + np.exp(log_arg))) / k_vb)))
        # La salida distorsionada es la corriente de placa
        distorted_audio = Ip / np.max(np.abs(Ip))

        # Normaliza para que el pico negativo sea -1 y el positivo sea 1
        max_pos = np.max(distorted_audio)
        min_neg = np.min(distorted_audio)
        # Escala el audio para que el rango sea [-1, 1]
        distorted_audio = 2 * (distorted_audio - min_neg) / (max_pos - min_neg) - 1

        return distorted_audio

def random_float():
    return random.randint(-100, 100)/100

ms = 0
def struct_to_metadata(data):
    if not isinstance(data, Structure):
        raise SBR_ERROR("This isn't a struct data")
    audio_data = {
        "cromatic_note": [], "afination_cst": [],
        "position": [], "duration": [],
        "files": [], "velocity": [],
        "panning": [], "effect": []}

    #temp vars
    tempo = variables_user["tempo"]
    mode = variables_user["mode"]
    tone = variables_user["tone"]
    assigning_instrument = True
    assigning_volumen = True
    volumen_track = 0
    inst = None
    global ms
    if not isinstance(mode, Rhythm):
        raise SBR_ERROR("The scale mode should be a rhythm data")
    #Proses data
    for obj in data:
        if isinstance(obj, Melody):
            if assigning_instrument or assigning_volumen:
                raise SBR_ERROR("You must assign an instrument and a volume before anything else")
            #(bit=int, notes=[], vel=[], time=[])
            for bit, notes, vel, time in obj:
                #one_dimention_list_recurtion()
                if bit == 0: ms += 15/tempo
                elif bit in (1, 5, 7, 9):
                    if isinstance(notes[0], Note): note = [notes[0]]
                    else: note = notes[0]
                    for note in one_dimention_list_recurtion(note):
                        croma = inst.grade_to_cromatic(mode, tone, note) 
                        audio_data["velocity"].append(vel[0]*volumen_track)
                        audio_data["cromatic_note"].append(croma)
                        audio_data["position"].append(ms)
                        if inst.type == "sampled":
                            audio_data["files"].append(inst.path)
                            audio_data["afination_cst"].append(
                                inst.calculate_interval(croma-60)
                                +random_float()*(random_tunin_cst/100))
                        else:
                            audio_data["afination_cst"].append(random_float()*(random_tunin_cst/100))
                            if inst.name == "seno":
                                audio_data["files"].append(chr(croma))
                            else: audio_data["files"].append(inst.path_note(croma))
                        audio_data["duration"].append(time[0]/15*tempo)
                        if inst.type == "sampled" or croma < 36:
                            audio_data["panning"].append(0)
                        else: audio_data["panning"].append(random_float()*random_stereo_value)
                        if bit == 7:
                            audio_data["effect"].append(7)
                        else: audio_data["effect"].append(0)
                    ms += 15/tempo

                elif bit in (3, 6, 2, 4, 8):
                    for _note, v, t in zip(notes, vel, time, strict=True):
                        if isinstance(_note, Note): _note = [_note]
                        for note in one_dimention_list_recurtion(_note):
                            croma = inst.grade_to_cromatic(mode, tone, note)
                            audio_data["velocity"].append(v*volumen_track)
                            audio_data["cromatic_note"].append(croma)
                            audio_data["position"].append(ms)
                            if inst.type == "sampled":
                                audio_data["files"].append(inst.path)
                                audio_data["afination_cst"].append(
                                    inst.calculate_interval(croma-60)
                                    +random_float()*(random_tunin_cst/100))
                            else:
                                audio_data["afination_cst"].append(random_float()*(random_tunin_cst/100))
                                audio_data["files"].append(inst.path_note(croma))
                            if bit == 3: audio_data["duration"].append(t/80*tempo)
                            elif bit == 6: audio_data["duration"].append(t/160*tempo)
                            elif bit == 2: audio_data["duration"].append(t/7.5*tempo)
                            elif bit == 4: audio_data["duration"].append(t/3.75*tempo)
                            elif bit == 8: audio_data["duration"].append(t/1.875*tempo)
                            if inst.type == "sampled" or croma < 36:
                                audio_data["panning"].append(0)
                            else: audio_data["panning"].append(random_float()*random_stereo_value)
                            audio_data["effect"].append(0)

                        if bit == 3: ms += (4/3)*15/tempo
                        elif bit == 6: ms += (8/3)*15/tempo
                        elif bit == 2: ms += (1/2)*15/tempo
                        elif bit == 4: ms += (1/4)*15/tempo
                        elif bit == 8: ms += (1/8)*15/tempo

        elif isinstance(obj, Rhythm):
            if assigning_instrument or assigning_volumen:
                raise SBR_ERROR("You must assign an instrument and a volume before anything else")
            for bit in obj:
                if bit == 0: ms += 15/tempo
                elif bit in (1, 5, 7, 9):
                    audio_data["velocity"].append(.8)
                    audio_data["cromatic_note"].append(60)
                    audio_data["position"].append(ms)
                    if inst.type == "sampled":
                        audio_data["files"].append(inst.path)
                        audio_data["afination_cst"].append(random_float()*(random_tunin_cst/100))
                    else:
                        audio_data["afination_cst"].append(random_float()*(random_tunin_cst/100))
                        audio_data["files"].append(inst.path_note(60))
                    audio_data["duration"].append(0)
                    audio_data["panning"].append(0)
                    if bit == 7:
                        audio_data["effect"].append(7)
                    else: audio_data["effect"].append(0)
                    ms += 15/tempo

                elif bit in (3, 6, 2, 4, 8):
                    iterations = 3 if bit == 6 else bit
                    for _ in range(iterations):
                        audio_data["velocity"].append(.8)
                        audio_data["cromatic_note"].append(60)
                        audio_data["position"].append(ms)
                        if inst.type == "sampled":
                            audio_data["files"].append(inst.path)
                            audio_data["afination_cst"].append(random_float()*(random_tunin_cst/100))
                        else:
                            audio_data["afination_cst"].append(random_float()*(random_tunin_cst/100))
                            audio_data["files"].append(inst.path_note(croma))
                        audio_data["duration"].append(0)
                        if inst.type == "sampled" or croma < 36:
                            audio_data["panning"].append(0)
                        else: audio_data["panning"].append(random_float()*random_stereo_value)
                        audio_data["effect"].append(0)

                        if bit == 3: ms += (4/3)*15/tempo
                        elif bit == 6: ms += (8/3)*15/tempo
                        elif bit == 2: ms += (1/2)*15/tempo
                        elif bit == 4: ms += (1/4)*15/tempo
                        elif bit == 8: ms += (1/8)*15/tempo

        elif isinstance(obj, Velocity):
            if len(obj) >= 1:
                volumen_track = audio_effects.dbs_to_float(obj[0])
                assigning_volumen = False
        elif isinstance(obj, Instrument):
            assigning_instrument = False
            inst = obj
            ms = 0

    return audio_data
