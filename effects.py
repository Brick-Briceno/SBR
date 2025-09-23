"""
Effects developed by @brick_briceno in 2022

I hope it helps you a lot and you can experiment with this
the only rule is that there are no rules :)
"""

#import random
from generators import E as __E
from sbr_types import *

"efectos de ritmo"

def L(data: list[Rhythm | Tones | Melody | Group], args: list[int]):
    "I shorten or repeat a number depending on the case"
    if not len(args): return data
    if isinstance(data, Rhythm):
        data = data.bin
        if len(data) <= int(args[0]):
            return Rhythm((data*int(args[0]))[:int(args[0])])
        return Rhythm(data[:int(args[0])])
    elif isinstance(data, Melody):
        return Melody((L(data.rhythm, args), L(data.tones, args)))
    if len(data) <= int(args[0]): return type(data)((data*int(args[0]))[:int(args[0])])
    return type(data)(data[:int(args[0])])

def X(data: list[Rhythm], args: list[int]):
    "I stretch the rhythmic pattern as symmetrically as possible"
    if not len(args): args = [2]
    args = args[0]
    if args == 0: return Rhythm()
    elif args == 1: return Rhythm(data)
    data = data.bin
    #Ritmos binarios
    if args == 2:
        data = data.replace("0", "00")
        data = data.replace("1", "10")
        data = data.replace("2", "11")
        data = data.replace("4", "11")
        data = data.replace("8", "11")
        data = data.replace("3", "6")
        data = data.replace("6", "1000010000100000")

    #Ritmos ternarios o mayores a 2
    elif args > 2:
        data = data.replace("0", "0"*args).replace("1", "1"+"0"*(args-1))
        data = data.replace("3", __E([3, 4*args, 4*args]).bin)
        data = data.replace("6", __E([3, 8*args, 8*args]).bin)
        data = data.replace("2", __E([2, args, args]).bin)
        data = data.replace("4", __E([4, args, args]).bin)
        data = data.replace("8", __E([8, args, args]).bin)

    return Rhythm(data)

def S(data: list[Rhythm], args: list[int]):
    "I only let a certain amount of pulses through"
    if not len(args): args = [7, 0]
    if len(args) == 1: args += [0]
    data = data.bin
    data = quantize(data)
    modo = int(args[1])
    if modo: data = data[::-1]
    args = int(args[0])
    final = ""
    cantidad = 0
    for pulso in data:
        if pulso == "1" and cantidad < args:
            cantidad += 1
            final += "1"
        else: final += "0"

    if modo: return Rhythm(final[::-1])
    return Rhythm(final)

def D(data: list[Rhythm], args: list[int]):
    "I apply delay to your rhythms"
    #el primer argumento es la longitud
    #y el segundo las veces que se repite
    #Definir argumentos
    data = quantize(data.bin)
    longitud = len(data)
    if not len(args): args = [3, 3]
    elif len(args) == 1: args.append(3)
    intervalo, cantidad = args[0], args[1]
    data_2 = list(data)
    final = ""

    #Aplicar delay >:D
    for x in range(longitud):
        if data[x] == "0": continue
        for y in range(1, 1+cantidad):
            pulsar = x+intervalo*y
            if pulsar >= longitud: continue
            data_2[pulsar] = "1"

    for x in data_2: final += x
    return Rhythm(final)

def R(data: list[Rhythm | Group | Tones | Velocity | Times | Melody], args: list[None]):
    "I reverse the rhythm"
    if len(data) <= 1: return type(data)()
    elif len(data) != 0:
        return data.reverse()

def I(data: list[Rhythm | Tones | int | float | Note | Group | Melody], args: list[None]):
    "I invert the rhythm, like inverting the color (not gate)"
    if isinstance(data, float):
        return data-data*2
    return ~data

def Q(data: list[Rhythm | Tones | Group | Melody], args: list[int]):
    "Tell me what number you want me to hide"
    if not args: args = [1]
    if not isinstance(data, Rhythm):
        end = []
        for n, item in enumerate(data, start=1):
            if n in args:
                end.append(item)
        if isinstance(data, Tones): return Tones(end)
        elif isinstance(data, Group): return Group(end)
    elif isinstance(data, Melody):
        return Melody(Q(data.rhythm, args), Q(data.tones, args))
    else:
        i = 0
        final = ""
        for i in range(args.count(0)):
            args.remove(0)
        args = [x-1 for x in args] #restar 1
        for p in data.bin:
            if p == "1":
                if i in args: final += "0"
                else: final += "1"
                i += 1
            else: final += "0"
        return Rhythm(final)


def Add(data: list[Rhythm], args: list[int]):
    "I add pulses wherever you tell me"
    if len(args) == 0: return data
    new = list(data.bin)
    for x in args:
        if len(data.bin) <= x:
            raise SBR_ERROR("Add: The argument is too big")
        new[x] = "1"
    return Rhythm("".join(new))


def turn_right(data: list[Rhythm | Tones | Group | Melody], args: list[int]):
    "I turn the rhythm to the right"
    if len(args) == 0: args = [1]
    if isinstance(data, Rhythm): data = data.bin
    if args == []: args = [1]
    elif args == [0]: return Rhythm(data)
    args = int(args[0])
    while args > len(data): args -= len(data)
    if isinstance(data, str):
        return Rhythm(data[-args:]+data[:-args])
    return type(data)(data[-args:]+data[:-args])

turn_right.__name__ = ">>"

def turn_left(data: list[Rhythm | Tones | Group | Melody], args: list[int]):
    "I turn the rhythm to the left"
    if not args: args = [1]
    return turn_right(data, [len(data)-args[0]])

turn_left.__name__ = "<<"


def abrir(data: list[Rhythm | Tones | Group], args: list[int]):
    "I let certain bits of the beginning pass"
    if len(data) <= 1:
        return type(data)()
    elif args == []: args = [1]
    if isinstance(data, Rhythm):
        data = data.bin
        return Rhythm(data[int(args[0]):])

    return type(data)(data[int(args[0]):])

abrir.__name__ = "Neither [ nor ]"


def cerrar(data: list[Rhythm | Tones | Group], args: list[int]):
    "I let certain bits of the ending go (I'm cousin of the L effect.)"
    return R(abrir(R(data, 0), args), 0)

cerrar.__name__ = "Neither [ nor ]"

def mul(data: list[Rhythm | Tones | Group | Melody | int | float], args: list[int]):
    "I multiplicate notes and fishes"
    if args != []:
        return data*int(args[0])
    return data

#lo de arriba parece un pene :D

mul.__name__ = "*"


"efectos numericos"

def Round(data: list[int | float | Note | Group], args: list[None]):
    "I like the simplicity of numbers, so I round them ^^"
    return round(data)

def Metric(data: list[Rhythm | Melody], args: list[None]):
    "Metrics is one of the most important things in music :)"
    return data.metric

def Len(data: list[Rhythm | Tones | Melody | Group], args: list[None]):
    "I like to measure sizes and distances :D"
    return len(data)


"efectos de tonales"

def Oct(data: list[Tones | Note | Melody | int], args: list[int]):
    "I change the octave of the notes, if you don't put an argument I'll return the same data"
    if len(args) == 0: return data
    return data+args[0]*7

def Th(data: list[Tones | Note | Melody | int], args: list[int]):
    return Oct(data, args)-1

def Chord(data: list[Tones | Note | Group | int], args: list[int]):
    "I love the armonies, so I create chords with the notes you give me"
    if len(args) == 0: return data
    elif isinstance(data, (Note, int)):
        end = []
        for th in args:
            if isinstance(data, (int, Note)):
                end.append(data+(th-1)) #I know pemdas but the code is faster that way
        return Tones(Group(end))
    else:
        progression = []
        for note in data:
            progression.append(Group(Chord(note, args)))
        return Tones(Group(progression))

def Arp(data: list[Tones | Group], args: list[None]):
    "I'm a big fan of trance music :)"
    end = []
    for x in data:
        if isinstance(x, Group):
            for y in x:
                end.append(y)
        else: end.append(x)

    return Tones(end)

#efectos de grupo

def G(data: list[list | Rhythm], args: list[int]):
    "I access an item of an iterable data"
    if len(args) == 0:
        return Group(data)
    elif len(args) == 1:
        return data[args[0]]
    else: raise SBR_ERROR(
        "This effect should have one or no argument")

#efectos de duracion

"Registro de efectos"

record = {
    "L": L,
    "X": X,
    "S": S,
    "D": D,
    "R": R,
    "I": I,
    "Q": Q,
    "Add": Add,
    ">>": turn_right,
    "<<": turn_left,
    "[": abrir,
    "]": cerrar,
    "*": mul,
    "Arp": Arp,
    "Oct": Oct,
    "Th": Th,
    "G": G,
    "Chord": Chord,
    "Round": Round,
    "Metric": Metric,
    "Len": Len,
}

#decorate all effects
for name, func in record.items():
    record[name] = SBR_Function(func)
