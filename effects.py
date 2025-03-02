"""
Effects developed by @brick_briceno in 2023

I hope it helps you a lot and you can experiment with this
the only rule is that there are no rules :)
"""

import random
from generators import E as __E
from sbr_types import *

"efectos de ritmo"

def L(data, arg):
    valid_argument_type("L", input_data=data, input_types=(Rhythm, Tones, Group), args=arg, args_types=(int,))
    if not len(arg): return data
    if isinstance(data, Rhythm):
        data = data.bin
        if len(data) <= int(arg[0]): return Rhythm((data*int(arg[0]))[:int(arg[0])])
        return Rhythm(data[:int(arg[0])])
    if len(data) <= int(arg[0]): return type(data)((data*int(arg[0]))[:int(arg[0])])
    return type(data)(data[:int(arg[0])])

def X(data, arg):
    valid_argument_type("X", input_data=data, input_types=(Rhythm,), args=arg, args_types=(int,))
    if not len(arg): arg = [2]
    arg = arg[0]
    if arg == 0: return Rhythm()
    elif arg == 1: return Rhythm(data)
    data = data.bin
    #Ritmos binarios
    if arg == 2:
        data = data.replace("0", "00")
        data = data.replace("1", "10")
        data = data.replace("2", "11")
        data = data.replace("4", "11")
        data = data.replace("8", "11")
        data = data.replace("3", "10010010")
        data = data.replace("6", "1000010000100000")

    #Ritmos ternarios o mayores a 2
    elif arg > 2:
        data = data.replace("0", "0"*arg).replace("1", "1"+"0"*(arg-1))
        data = data.replace("3", __E([3, 4*arg, 4*arg]).bin)
        data = data.replace("6", __E([3, 8*arg, 8*arg]).bin)
        data = data.replace("2", __E([2, arg, arg]).bin)
        data = data.replace("4", __E([4, arg, arg]).bin)
        data = data.replace("8", __E([8, arg, arg]).bin)

    return Rhythm(data)

def S(data, arg):
    valid_argument_type("S", input_data=data, input_types=(Rhythm,), args=arg, args_types=(int,))
    if not len(arg): arg = [7, 0]
    if len(arg) == 1: arg += [0]
    data = data.bin
    data = quantize(data)
    modo = int(arg[1])
    if modo: data = data[::-1]
    arg = int(arg[0])
    final = ""
    cantidad = 0
    for pulso in data:
        if pulso == "1" and cantidad < arg:
            cantidad += 1
            final += "1"
        else: final += "0"

    if modo: return Rhythm(final[::-1])
    return Rhythm(final)

def D(data, args):
    valid_argument_type("D", input_data=data, input_types=(Rhythm,), args=args, args_types=(int,))
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

def R(data, _):
    valid_argument_type("R", input_data=data,
                        input_types=(Rhythm, Group, Tones, Velocity, Times, Melody))
    if len(data) <= 1: return type(data)()
    elif len(data) != 0:
        return data.reverse()

def I(data, _):
    valid_argument_type("'I'", input_data=data, input_types=(Rhythm, Tones, int, Note))
    return ~data

def Q(data, args):
    if [] == 0: args = [1]
    valid_argument_type("Q", input_data=data, input_types=(Rhythm, Tones, Group, Melody),
                        args=args, args_types=(int,))
    if not isinstance(data, Rhythm):
        end = []
        for n, item in enumerate(data, start=1):
            if n in args:
                end.append(item)
        if isinstance(data, Tones): return Tones(end)
        elif isinstance(data, Group): return Group(end)
    elif isinstance(data, Melody):...
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

def turn_right(data, args):
    if len(args) == 0: args = [1]
    valid_argument_type(">", input_data=data, input_types=(Rhythm, Tones, Group, Melody),
                        args=args, args_types=(int,))
    data = data.bin
    if args == []: args = [1]
    elif args == [0]: return Rhythm(data)
    args = int(args[0])
    while args > len(data): args -= len(data)
    return Rhythm(data[-args:]+data[:-args])

def turn_left(data, args):
    valid_argument_type("<", input_data=data, input_types=(Rhythm, Tones, Group, Melody),
                        args=args, args_types=(int,))
    if args == []: args = [1]
    return turn_right(data, [len(data)-args[0]])

def abrir(data, arg):
    valid_argument_type("Neither [ nor ]", input_data=data, input_types=(Rhythm, Tones, Group),
                        args=arg, args_types=(int,))
    if len(data) <= 1:
        return type(data)()
    elif arg == []: arg = [1]
    if isinstance(data, Rhythm):
        data = data.bin
        return Rhythm(data[int(arg[0]):])
    
    return type(data)(data[int(arg[0]):])

def cerrar(data, args):
    return R(abrir(R(data, 0), args), 0)

def mul(data, arg):
    if arg != []:
        return data*int(arg[0])
    return data

#lo de arriba parece un pene :D

"efectos numericos"

def Round(data, _):
    valid_argument_type("Round", input_data=data,
                        input_types=(int, float, Note, Group))
    return round(data)

"efectos de tonales"

def Oct(data, args):
    valid_argument_type("Oct", input_data=data, input_types=(Tones, Note, Melody, int),
                        args=args, args_types=(int,))
    if len(args) == 0: return data
    return data+args[0]*7

def Th(data, args):
    return Oct(data, args)-1

def Chord(data, args):
    valid_argument_type("Oct", input_data=data, input_types=(Tones, Group, Note, int),
                        args=args, args_types=(int,))
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

def Arp(data, args):
    valid_argument_type("Arp", input_data=data, input_types=(Tones, Group))
    end = []
    for x in data:
        if isinstance(x, Group):
            for y in x:
                end.append(y)
        else: end.append(x)

    return Tones(end)

#efectos de grupo

def G(data, args):
    valid_argument_type("G", input_data=data, input_types=(list, Rhythm),
                        args=args, args_types=(int,))
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
    ">>": turn_right,
    "<<": turn_left,
    "[": abrir,
    "]": cerrar,
    "*": mul,
    "Arp": Arp,
    "Oct": Oct,
    "Th": Th,
    "G": G,
    "Round": Round,
    "Chord": Chord,
}
