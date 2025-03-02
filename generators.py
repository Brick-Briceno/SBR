"""
Generators developed by @brick_briceno in 2023

I hope it helps you a lot and all of you can experiment with this
the only rule is that there are no rules :)
"""

from sbr_types import *
import random

"Efectos ritmicos"

def B(arg):
    "Here I wrote a joke but I got canceled xD"
    valid_argument_type("B", arg, (Rhythm, int,))
    if arg == []: return Rhythm()
    return Rhythm(arg[0]) #es la misma vaina no?

def N(arg):
    "I really like to dance, I count 3, 3, 2, yeah, 3, 1, 2, 2, (N332 is = B10010010)"
    valid_argument_type("N", arg, (int,))
    salida = ""
    if arg == []: return Rhythm()
    for x in str(arg[0]):
        if x == "0": continue
        salida += str(10**(int(x)-1))
    return Rhythm(salida)

def C(arg):
    "Every x amount of time I spit a 1, args: every x bits, length"
    valid_argument_type("C", arg, (int,))
    if not len(arg): arg = [3, 32]
    elif not len(arg)-1: arg.append(32)
    string = (f"{10**(int(arg[0])-1)}"*int(arg[1]))[:int(arg[1])]
    return Rhythm(string)

def E(arg):
    "I love symmetry, args: pulses, lenght, L, I'm the algorithm that started it all, in peace rest Godfried T <3"
    valid_argument_type("E", arg, (int,))
    if not len(arg): arg = [5, 16, 16]
    elif not len(arg)-1: arg += [16]*2
    elif not len(arg)-2: arg += [arg[1]]
    a, b, c = arg[:3]
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

def A(arg): #Argumentos: longitud, cantidad, empezar por 1?
    "I'm so indecisive, I generate random rhythms every time I'm back, args: lenght, quantity, start with 1?"
    valid_argument_type("A", arg, (int,))
    #crear argumentos en caso de que no los haya
    if not len(arg): arg = [8, 0, 0]
    elif len(arg) == 1: arg += [0]*2
    elif len(arg) == 2: arg += [0]
    arg = int(arg[0]), int(arg[1]), int(arg[2])

    #verificar que A sea mayor o igual que B
    if arg[0] == 0 or arg[1] > arg[0]: return ""

    #verificar que se deba empezar por un 1
    elif arg[2] != 0: indices = [0]
    else: indices = []

    #si la cantidad es 0 se definirá de forma aleatoria
    cantidad = arg[1]
    if cantidad == 0: cantidad = random.randint(1, arg[0])

    #generar indices
    while len(indices) < cantidad:
        dato = random.randint(0, arg[0]-1)
        if not dato in indices: indices.append(dato)

    #Si el ritmo debe empezar por 1
    
    pre_final = [0]*arg[0]
    for x in indices: pre_final[x] = 1
    
    #pasar a string
    final = ""
    for x in pre_final:
        if x == 1: final += "1"
        else: final += "0"

    return Rhythm(final)

"Generadores Numericos"

def Range(arg):
    valid_argument_type("Range", arg, (int,))
    if len(arg) == 0: return Group()
    elif len(arg) == 1: return Group(range(arg[0]))
    elif len(arg) == 2: return Group(range(arg[0], arg[1]))
    elif len(arg) == 3: return Group(range(arg[0], arg[1], arg[2]))

"Generadores Tonales"

def M(arg):
    "I'm the tones's abstraction, give me numbers or notes and I'll sing for Ü ;)"
    valid_argument_type("M", arg, (int, Note, Tones, Group))
    return Tones(arg)

def Jumps(arg):
    "My philosophy is that notes don't matter, intervals produce the emotions"
    valid_argument_type("Jumps", arg, (int,))
    end = []
    grade = 0
    for x in arg:
        end.append(grade)
        grade += x
    return Tones(end)

"Generadores de Velocity"

def V(arg):
    "I give intensity or subtlety to the notes"
    valid_argument_type("V", arg, (Velocity, int, float))
    if arg == []: return Velocity()
    return Velocity(arg) #es la misma vaina no?

"Generadores de Longitud de notas"

def T(arg):
    "I tell notes until when they are necessary"
    valid_argument_type("T", arg, (Times, int, float))
    if arg == []: return Times()
    return Times(arg) #es la misma vaina no?

"Generadores Melodicos"

def Sm(arg):
    "Symmetric Melody, I keep every detail of the melody"
    valid_argument_type("Sm", arg, (Group,))
    if not len(arg): raise SBR_ERROR("Sm needs at least one argument")
    return Melody(arg[0])

"Generadores Poliritmicos"

def Poly(arg):
    "Polyrhythmia, within my store various rhythms and generates its strutures"
    valid_argument_type("Poly", arg, (Group,))
    if not len(arg): raise SBR_ERROR("Poly needs at least one argument")
    return Polyrhythm(arg[0])

"Generadores Estructura"

def Struct(arg):
    "Do you've amazing ideas but don't know how to put together the puzzle? I'm your solution"
    valid_argument_type("Struct", arg, (Group,))
    if not len(arg): raise SBR_ERROR("Struc needs at least one argument")
    return Structure(arg[0])


"Registro de generadores"

from variables import vars_instruments

def inst(arg):
    valid_argument_type("An instrument", arg, (int,))
    if not len(arg): raise SBR_ERROR("The instrument needs at least one argument")
    for name, obj in zip(vars_instruments.keys(), vars_instruments.values()):
        if obj.inst_id == arg[0]:
            break
    else: raise SBR_ERROR(
        "This instrument ID isn't exist", "type 'vars:' to see the available instruments")
    return Instrument(vars_instruments[name].path, obj.inst_id)

#in case only one group has been sent
def return_data(arg):
    if len(arg) == 0:
        raise SBR_ERROR("You must to put more arguments")
    elif len(arg) == 1:
        return arg[0]
    elif len(arg) >= 2:
        return Group(arg)

record = {
    "B": B,
    "E": E,
    "C": C,
    "N": N,
    "A": A,
    "M": M,
    "Jumps": Jumps,
    "T": T,
    "V": V,
    "$": inst,
    "Sm": Sm,
    "Poly": Poly,
    "Range": Range,
    "Struct": Struct,
    "": return_data,
}
