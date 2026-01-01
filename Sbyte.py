"""
Symmetry Melody Api v2.1
@Brick_briceno 2023
"""

import time

"Pulsos a bpm"

ultimo_toque = 0
lista_taps = [0]
def tap(max_pulses=15, max_time=2.5):
    global lista_taps
    global ultimo_toque
    if lista_taps[0] > max_time or lista_taps[0] == 0: lista_taps = []
    if (time.time() - ultimo_toque) > 2:
        ultimo_toque = 0
        lista_taps = [0]
    media_bpm = 0
    if ultimo_toque:
        if len(lista_taps) >= max_pulses: lista_taps.pop(0)
        lista_taps.append(time.time() - ultimo_toque)
        media_bpm = 60/(sum(lista_taps)/len(lista_taps))
    ultimo_toque = time.time()
    if media_bpm: return media_bpm
