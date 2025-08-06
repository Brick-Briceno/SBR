"""
Everything related to color and design
@Brick_briceno 2024
"""

import random
from colorama import init

init()

def hex_to_rgb(hexa):
    if len(hexa) == 7:
        return int(hexa[1:3],16), int(hexa[3:5],16), int(hexa[5:],16), 255
    elif len(hexa) == 4:
        return int(hexa[1],16)*17, int(hexa[2],16)*17, int(hexa[3],16)*17, 255
    elif len(hexa) == 9:
        return int(hexa[1:3],16), int(hexa[3:5],16), int(hexa[5:7],16), int(hexa[7:],16)
    elif len(hexa) == 5:
        return int(hexa[1],16)*17, int(hexa[2],16)*17, int(hexa[3],16)*17, int(hexa[4],16)*17
    else: raise TypeError(f"This is not an RGB hex code: {hexa}")

def print_color(*objects, color="#ccc", sep=" ", end="\n", go_to_print=True):
    r, g, b, _ = hex_to_rgb(color)
    text = ""
    for item in objects:
        text += str(item)+sep
    text = f"\033[38;2;{r};{g};{b}m{text}\033[0m"
    if go_to_print: print(text+end, sep="", end="")
    else: return text

def hls_to_rgb(h, l, s):
    #H = tono, rango de 0 a 360, son grados en un circulo cromatico
    #S = saturación, rango de 0 a 1, flotante claro
    #L = luminocidad, rango de 0 a 1
    l /= 2

    c = (1-abs(2*l-1))*s
    x = (1-abs((h/60)%2-1))*c
    m = l - c/2

    if 0 <= h < 60: r, g, b = c, x, 0
    elif 60 <= h < 120: r, g, b = x, c, 0
    elif 120 <= h < 180: r, g, b = 0, c, x
    elif 180 <= h < 240: r, g, b = 0, x, c
    elif 240 <= h < 300: r, g, b = x, 0, c
    else: r, g, b = c, 0, x

    r = int((r+m)*255)
    g = int((g+m)*255)
    b = int((b+m)*255)

    return r, g, b

def rbg_to_hex(r, g, b):
    r, g, b = hex(r)[2:], hex(g)[2:], hex(b)[2:]
    if len(r) == 1: r = "0" + r
    if len(g) == 1: g = "0" + g
    if len(b) == 1: b = "0" + b
    return f"#{r}{g}{b}"


def complementary(h):
    return (h+180)%360

def monocromatic(h):
    return (h+13.5)%360, (h-13.5)%360, (h+27)%360, (h-27)%360

def triad(h):
    return (h+360/3*1)%360, (h+360/3*2)%360

def quad(h):
    return (h+360/4*1)%360, (h+360/4*2)%360, (h+360/4*3)%360


def random_palette():
    #selecionar tipo de armonia
    opcion_harm = random.choices(
        #tipos de armonia y sus probabilidades
        ["complementario"]*50+
        ["triada"]*30+
        ["monocromatico"]*15+
        ["cuatriada"]*5
        )[0]

    #selecionar nivel de contraste
    opcion_constraste = random.choices(
        ["alto"]*35+
        ["normal"]*60+
        ["bajo"]*5
        )[0]

    #generar un color de base
    color_base = random.randint(0, 360), 1, 1

    #procesar color
    if opcion_harm == "complementario":
        color_1 = color_base
        color_2 = complementary(color_base[0]), 1, 1
        color_3 = color_1
        color_4 = color_2
        color_5 = color_2
    elif opcion_harm == "triada":
        color_1 = color_base
        color_2 = triad(color_base[0])[0], 1, 1
        color_3 = triad(color_base[0])[1], 1, 1
        color_4 = color_base
        color_5 = color_2
    elif opcion_harm == "monocromatico":
        color_1 = color_base
        color_2 = monocromatic(color_base[0])[0], 1, 1
        color_3 = monocromatic(color_base[0])[1], 1, 1
        color_4 = monocromatic(color_base[0])[2], 1, 1
        color_5 = monocromatic(color_base[0])[3], 1, 1
    elif opcion_harm == "cuatriada":
        color_1 = color_base
        color_2 = quad(color_base[0])[0], 1, 1
        color_3 = quad(color_base[0])[1], 1, 1
        color_4 = quad(color_base[0])[2], 1, 1
        color_5 = color_base

    #calcular constraste
    if opcion_constraste == "alto":
        color_3 = color_3[0], .9, .4
        color_4 = color_4[0], .9, .4
        color_5 = color_5[0], .9, .333
    elif opcion_constraste == "normal":
        color_3 = color_3[0], .8, .4
        color_4 = color_4[0], .8, .4
        color_5 = color_5[0], .7, .333
    elif opcion_constraste == "bajo":
        color_1 = color_1[0], (.8/2)*4, 1
        color_2 = color_2[0], (.8/2)*4, 1
        color_3 = color_3[0], (.8/2)*3, .5
        color_4 = color_4[0], (.8/2)*3, .5
        color_5 = color_5[0], (.8)*2, .333

    #converit a hls a rgb a hexadecimal
    paleta = []
    for color in (color_1, color_2, color_3, color_4, color_5):
        h, l, s = color
        r, g, b = hls_to_rgb(h, l, s)
        paleta.append(rbg_to_hex(r, g, b))

    return paleta


color1, color2, color3, color4, color5 = random_palette()


