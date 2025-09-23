"""
Generators developed by @brick_briceno in 2022

I hope it helps you a lot and all of you can experiment with this
the only rule is that there are no rules :)
"""

from sbr_types import *
import numpy as np
import random

"Efectos ritmicos"


def B(args: list[Rhythm | int | str | Group]):
    "Here I wrote a joke but I got canceled xD"
    if args == []: return Rhythm()
    rhythm = ""
    for arg in one_dimention_list_recurtion(args):
        if isinstance(arg, Rhythm):
            rhythm += arg.bin
        else: rhythm += str(arg)
    return Rhythm(rhythm) #es la misma vaina no?

def N(args: list[int]):
    "I really like to dance, I count 3, 3, 2, yeah, 3, 1, 2, 2, (N332 is = B10010010)"
    salida = ""
    if args == []: return Rhythm()
    for x in str(args[0]):
        if x == "0": continue
        salida += str(10**(int(x)-1))
    return Rhythm(salida)

def C(args: list[int]):
    "Every x amount of time I spit a 1, args: every x bits, length"
    if not len(args): args = [3, 32]
    elif not len(args)-1: args.append(32)
    string = (f"{10**(int(args[0])-1)}"*int(args[1]))[:int(args[1])]
    return Rhythm(string)

def E(args: list[int]):
    "I love symmetry, args: pulses, lenght, L, I'm the algorithm that started it all, in peace rest Godfried T <3"
    if not len(args): args = [5, 16, 16]
    elif not len(args)-1: args += [16]*2
    elif not len(args)-2: args += [args[1]]
    a, b, c = args[:3]
    a, b, c = int(a), int(b), int(c)
    if a > b: a = b
    if a == 0: return ["0" for i in range(c)]

    #Simetrizar
    pattern = []
    counts = []
    remainders = []
    divisor = b - a
    remainders.append(a)
    level = 0
    while True:
        counts.append(divisor // remainders[level])
        remainders.append(divisor % remainders[level])
        divisor = remainders[level]
        level = level + 1
        if remainders[level] <= 1: break
    counts.append(divisor)

    def build(level):
        if level == -1: pattern.append(0)
        elif level == -2: pattern.append(1)
        else:
            for i in range(0, counts[level]): build(level - 1)
            if remainders[level] != 0: build(level - 2)

    build(level)
    i = pattern.index(1)
    pattern = pattern[i:] + pattern[0:i]

    #Ajustar longitud
    n = 0
    final_pattern = ""
    while c != len(final_pattern):
        if n == len(pattern): n = 0
        final_pattern += f"{pattern[n]}"
        n += 1

    return Rhythm(final_pattern) #Yeii :D

def A(args: list[int]): #Argumentos: longitud, cantidad, empezar por 1?
    "I'm so indecisive, I generate random rhythms every time I'm back, args: lenght, quantity, start with 1?"
    #crear argumentos en caso de que no los haya
    if not len(args): args = [8, 0, 0]
    elif len(args) == 1: args += [0]*2
    elif len(args) == 2: args += [0]
    args = int(args[0]), int(args[1]), int(args[2])

    #verificar que A sea mayor o igual que B
    if args[0] == 0 or args[1] > args[0]: return ""

    #verificar que se deba empezar por un 1
    elif args[2] != 0: indices = [0]
    else: indices = []

    #si la cantidad es 0 se definirá de forma aleatoria
    cantidad = args[1]
    if cantidad == 0: cantidad = random.randint(1, args[0])

    #generar indices
    while len(indices) < cantidad:
        dato = random.randint(0, args[0]-1)
        if not dato in indices: indices.append(dato)

    #Si el ritmo debe empezar por 1
    
    pre_final = [0]*args[0]
    for x in indices: pre_final[x] = 1
    
    #pasar a string
    final = ""
    for x in pre_final:
        if x == 1: final += "1"
        else: final += "0"

    return Rhythm(final)

"Generadores Numericos"

def Range(args: list[int]):
    "I'm the range generator, args: start, end, step, if you don't put anything I'll return an empty group"
    if len(args) == 0: return Group()
    elif len(args) == 1: return Group(range(args[0]))
    elif len(args) == 2: return Group(range(args[0], args[1]))
    elif len(args) == 3: return Group(range(args[0], args[1], args[2]))

"Generadores Tonales"

def M(args: list[int | Note | Tones | Group]):
    "I'm the tones's abstraction, give me numbers or notes and I'll sing for Ü ;)"
    return Tones(args)


def one_dimention_list_recurtion(group):
    new = []
    for item in group:
        if not isinstance(item, list):
            new.append(item)
        else:
            for x in one_dimention_list_recurtion(item):
                new.append(x)
    return new


def J(args: list[int | Group]):
    "My philosophy is that notes don't matter, intervals produce the emotions"
    if args == []: return Tones()
    #I don't wanted to repeat code pero yo vivo la vida relax xd
    #this for loop is the Arp effect
    notes = []
    args = one_dimention_list_recurtion(args)
    if len(args) == 0: raise SBR_ERROR("")
    grade = args[0]
    for x in args[1:]:
        notes.append(grade)
        grade += x
    return Tones(notes)

"Generadores de Velocity"

def V(args: list[Velocity | int | float]):
    "I give intensity or subtlety to the notes"
    if args == []: return Velocity()
    return Velocity(args) #es la misma vaina no?

"Generadores de Longitud de notas"

def T(args: list[Times | int | float]):
    "I tell notes until when they are necessary"
    if args == []: return Times()
    return Times(args) #es la misma vaina no?

"Generadores Grupos"

def Seno(args: list[int | float]):
    "Put me 2 or 3 parameters and then, got a seno array group"
    # __doc__ is a local variable, don't delete it
    if len(args) not in (2, 3): raise SBR_ERROR(
        "You must put 2 or 3 parameters in the 'Seno' generator",
        "frecuency, length and normalization amplitude")
    if len(args) == 2:
        freq, length = args
        max_array = 1
    else: freq, length, max_array = args

    if max_array == 0: return Group()
    time_array = np.linspace(0/max_array, 1, length, endpoint=False)
    sine_wave = np.sin(2 * np.pi * freq * time_array)
    array = Group(sine_wave*max_array)
    return array


"Generadores Melodicos"

def Sm(args: list[Group]):
    "Symmetric Melody, I keep every detail of the melody"
    if not len(args): raise SBR_ERROR("Sm needs at least one argument")
    return Melody(args[0])

"Generadores Poliritmicos"

def Poly(args: list[Group]):
    "Polyrhythmia, within my store various rhythms and generates its structures"
    if not len(args): raise SBR_ERROR("Poly needs at least one argument")
    return Polyrhythm(args[0])

"Generadores Estructura"

def Struct(args: list[Group]):
    "Do you've amazing ideas but don't know how to put together the puzzle? I'm your solution"
    if not len(args): raise SBR_ERROR("Struct needs at least one argument")
    return Structure(args[0])


"Registro de generadores"

from variables import vars_instruments

def inst(args: list[int]):
    "I'm the instrument generator, i've a good feeling yeah, if you wanna use me, you must to put the instrument ID"
    if not len(args): raise SBR_ERROR("The instrument needs at least one argument")
    for name, obj in zip(vars_instruments.keys(), vars_instruments.values()):
        if obj.inst_id == args[0]: break
    else: raise SBR_ERROR(
        f"This instrument ID isn't exist ${args[0]}",
        "type 'vars:' to see the available instruments")
    return Instrument(vars_instruments[name].path, obj.inst_id)

#in case only one group has been sent
def return_data(args: list[None]):
    if len(args) == 0:
        raise SBR_ERROR("You must to put more arguments")
    elif len(args) == 1:
        return args[0]
    elif len(args) >= 2:
        return Group(args)

record = {
    "B": B,
    "E": E,
    "C": C,
    "N": N,
    "A": A,
    "M": M,
    "J": J,
    "T": T,
    "V": V,
    "$": inst,
    "Sm": Sm,
    "Poly": Poly,
    "Seno": Seno,
    "Range": Range,
    "Struct": Struct,
    "": return_data,
}

#decorate all generators
for name, func in record.items():
    if name: record[name] = SBR_Function(func)
