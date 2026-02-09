"""
SBR keywords
by @brick_briceno 2025

"""

import b_color
from b_color import print_color as b_print
from b_color import (hls_to_rgb, hex_to_rgb, rbg_to_hex, rgb_to_hls,
                     color1, color2, color3, color4, color5)
from sbr_types import pulse_will_be
#from threading import Thread
from sbr_utils import *
from sbr_types import *
from variables import *
#from sbr_help import *
import lib.MidiFile
import itertools
import generators
import effects
import base64
import shutil
import Bsound
import Sbyte
import time
import gzip
import lib
import sys
import os

try: import keyboard
except ImportError:
    print("Missing keyboard library")
    print("Some features, such as games or playing"
            "the piano, may cause errors on this system")
    input("To continue, press any key")


welcome = """
▒█▀▀▀█ ▒█▀▀█ ▒█▀▀█
░▀▀▀▄▄ ▒█▀▀▄ ▒█▄▄▀
▒█▄▄▄█ ▒█▄▄█ ▒█░▒█

The SBR language provides super creative tools
to musicians to make good music and from this make memorable melodies

With all my heart I hope that good things can be
made with this tool, I hope that people have fun experimenting
with it and that it helps all of you make better music, hugs <3

@Brick_briceno 2022
"""

def pause_code(_in="\n", end=""):
    b_print(f"{_in}Press enter to continue{end}", color=color5, end="")
    input(end)

def sbr_licence(_):
    "Show license"
    print("""
BSD 3-Clause License

Copyright (c) 2025, Miguel Briceño

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
""".strip())

def sbr_help(instruction):
    "Everyone asks me for help but, no one asks me how I am"
    if len(instruction) != 0:
        h = instruction[0].strip()#.lower()
        if h.lower() == "tutorial":
            b_print("This is how we do this Syntax", color=color1)
            sbr_help(["syntax"]), input()

            b_print("but what is the Operators", color=color1)
            sbr_help(["operators"]), input()

            b_print("and how many Generators there are?", color=color1)
            sbr_help(["generators"]), input()

            b_print("and... how many Effects there are?", color=color1)
            sbr_help(["effects"]), input()

            b_print("the keywords are awsome!", color=color1)
            sbr_help(["keywords"]), input()
            clean_console()

            b_print("Check the SBR's Documentation for learn music and more about this increible lenguage ;)", color=color2)
            b_print("An explosion of music, available in several languages, Visit it now! Click, click!")
            b_print("github.com/Brick-Briceno/SBR/blob/main/docs/en/README.md", color="#fff")
            input()

        elif "effect" in h.lower():
            print("The effects are put after a data")
            print("or a generator that in turn returns a data")
            print("Example: B1011 X2")
            print("generator^     ^ effect")
            for keys, value in zip(effects.record.keys(), effects.record.values()):
                print(keys, value.__doc__ if value.__doc__ else 
                      "There's no description", sep=f" {'.'*((12)-len(keys))} ")

        elif "generator" in h.lower():
            print("Example: B 1011")
            print("generator^ ^^^^one argument")
            for keys, value in zip(generators.record.keys(), generators.record.values()):
                print(keys, value.__doc__ if value.__doc__ else 
                      "There's no description", sep=f" {'.'*((12)-len(keys))} ")

        elif "keyword" in h.lower():
            for keys, value in zip(record.keys(), record.values()):
                print(keys, value.__doc__ if value.__doc__ else 
                      "There's no description", sep=f" {'.'*((12)-len(keys))} ")

        elif "variable" in h.lower():
            print("Variables are like boxes, you can save things inside")
            print("They must be in lowercase and they can't start with a number")

        elif h in tuple(effects.record)+tuple(generators.record)+tuple(record):
            if h in tuple(generators.record)[:-1]: #[:-1] that's so that is doesn't show the empty generator it must be last
                doc = generators.record[h].__doc__
                print(doc) if doc else print(f"There's no description for '{h}'")
            elif h in tuple(effects.record):
                doc = effects.record[h].__doc__
                print(doc) if doc else print(f"There's no description for '{h}'")
            elif h in tuple(record):
                doc = record[h].__doc__
                print(doc) if doc else print(f"There's no description for '{h}'")

        elif h in ("operators", "operator", "+", "-"):
            print("Unless you're doing a math operation, I mean, only numbers")
            print("The operators divide the whole block, be careful to put them inside groups")
            print("+ adds numbers and superimposes rhythms (investigate OR gate)")
            print("- subtracts numbers and superimposes rhythms but")
            print("turns to zeros where the 1 match in the same place (investigate XOR gate)")
        elif "syntax" in h:
            print("""
In case of havin purely numeric characters, it will be
prossed as a mathematical operation and the order of the
operations will be based on the PEMDAS standard (parentesis,
exponents, multiplication, addition, subtraction)

Examples:
5+5*2 = 15
(5+5)*2 = 20

You can do this as well
(5+5)2 = 20

""")
            input("but... and if it's melodic")
            clean_console()
            print("""
However, in case of containing generators, effects or any musical data
such as notes, tones, rhythms or a groups, everything will be
processed left to right in this order

Examples:
  ↓↓↓↓all this are an argument, only one
 B1000 L8 = B1000 1000
 ↑     ↑     ↑
 ↑     ↑     (zeros and ones) these are the rhythm data
 ↑    (L) repeats the number of bits until x number long (effect)
(B) is used to generate the bits (generator)

The total of all the code is called Brick :D""")
            input("Other example")
            clean_console()
            print("""
 M0,-2,2,-1
 ↑     ↑
 ↑    (0,-2,2,-1) arguments are separated by commas
(M) is used to generate the tones
""")
        elif h.lower().replace("?", "") in ("how are u", "how're u",
                                            "how are you", "how're you"):
            print("I'm fine, thanks for asking ^^")
        else: print(f"No help information for '{instruction[0]}'")
    else:
        clean_console()
        #r, g, b = hex_to_rgb(color1)
        base = rgb_to_hls(*hex_to_rgb(color1)[:3])[0]
        for i, char in enumerate(welcome):
            grade = base-i*(360/6/len(welcome))
            h, _, _ = hls_to_rgb(grade, 1, 1)
            r, g, b = hls_to_rgb(h, 1, 1)
            hexa = rbg_to_hex(r, g, b)
            b_print(char, end="", color=hexa, sep="")
            time.sleep(.005)
        #input("sísí me vale vrg")
        pause_code()
        print("""Type 'help' and the function to study
For example type:
help tutorial
help effects
help generators
help keywords
help operators
help syntax
help E

licence

invite me a coffee :)
donate <3
""")



def sbr_import(args):
    "I import external resources into the project"
    if not len(args):
        return
    data = args[0]
    try:
        with open(data, "r") as _file:
            _file = _file.read()
        wait = "  Importing..."
        print(wait, end="\r")
        for n_line, line in enumerate(_file.splitlines(), start=1):
            sbr_line(line)
        print(" "*len(wait), end="\r")
    except SBR_ERROR as bad:
        raise SBR_ERROR(f"Import error in line {n_line}:", bad)
    except FileNotFoundError:
        raise SBR_ERROR(f"Import error this file doesn't exist '{data}'")
    except PermissionError:
        raise SBR_ERROR(f"The system doesn't have permission to accesss this file '{data}'")
    except OSError:
        raise SBR_ERROR(f"Invalid syntax on import '{data}'")



sbr_line = None


def instrument(arg):
    "I record an instrument"
    if len(arg) == 0:
        raise SBR_ERROR("Enter the path of an instrument or sample")
    else:
        _id = len(vars_instruments.keys())
        inst = Instrument(arg[0], _id)
        if f"${inst.name}" in vars_instruments.keys():
            print(f"This instrument already exists: {inst.name}")
        vars_instruments[f"${inst.name}"] = inst


seno = Instrument("seno", 2**32)
vars_instruments[f"${seno.name}"] = seno

def phrase(arg):
    print("Hi! how are you :)")

def print_dict(d: dict, name: str, is_end=False):
    b_print(name, color=color1)
    n = 0
    _, eje_v = shutil.get_terminal_size()
    for k, v in zip(d, d.values()):
        b_print(k, color=color3, end="")
        b_print("=", end="", color=color5)
        b_print(v, color=color4,
                end="\n" if len(f"{k}{v}") > 5 else "")
        if n >= eje_v-4:
            pause_code()
            n = 0
        n += 1

    if not is_end:
        pause_code()
        print("\n")



def sbr_vars(args):
    """I show you all the variables and others things"""
    print_dict(vars_instruments, "Instruments")
    print_dict(variables_sys, "Constants")
    print_dict(variables_user, "Vars Users")
    print_dict(defines, "Defines",
               is_end=True)


def sbr_exit(args):
    "I exit the program"
    raise SystemExit


def code_made(args):
    "I remember all you really do it"
    _all = False
    save = False
    if len(args) >= 1:
        if "all" in args:
            _all = True
            args = list(args)
            for _ in range(args.count("all")):
                args.remove("all")
        else: print("Type 'code_made: all' to see everything you have written")
    if len(args) >= 1:
        save = True
    code = ""
    for line in code_that_has_been_made[:-1]:
        if "=" in line or _all:
            code += line+"\n"
    code += code_that_has_been_made[-1]+"\n"
    if not save:
        print("-"*42)
        for line in code.splitlines():
            print("\t"+line)
        print("-"*42)
    else: #if save is true
        try:
            with open(args[0]+".sm", "w") as f:
                f.write(code)
        except: print(f"Error saving the file {args[0]}.sm")

def clock(args):...


def ident(args):
    "I ident ur code babe :-3"
    #organize arguments
    if len(args) == 0: return
    elif len(args) == 1:
        spaces = 4
        code = sbr_line(args[0])
    else:
        if not args[0].isnumeric(): raise SBR_ERROR("This value must be numeric")
        code = sbr_line(args[1])
        spaces = int(args[0])
    #ident
    ident_code = ""
    level = 0
    for char in str(code):
        ident_code += char
        if char == "{":
            level += 1
            ident_code += "\n"+" "*spaces
        elif char == ";":
            ident_code += "\n"+" "*spaces

    print(ident_code)


def metric(args):
    "How many pulses does any data have"
    for arg in args:
        data = sbr_line(arg)
        if isinstance(data, (Melody, Rhythm)):
            print(f"metric --- {data.metric}")
        else: raise SBR_ERROR(f"Only rhythms and melodies have metric, not {type(data.__name__)}")


def sbr_len(args):  
    "What length is a data"
    for arg in args:
        ""
        data = sbr_line(arg)
        if isinstance(data, (Melody, Rhythm, Group, Tones)):
            print(f"Its length is --- {len(data)}")
        else: raise SBR_ERROR(f"Only rhythms and melodies have len, not {type(data.__name__)}")

def sbr_print(args):
    "I show things on the console, and... that's it"
    for x in args:
        data = sbr_line(x)
        print(data)


def sbr_type(args):
    "I display the data type of what you give me"
    for arg in args:
        result = sbr_line(arg)
        result_type = type(result).__name__
        print(result, result_type,
              sep=" is an " if result_type[0].lower() in (
                  "a", "e", "i", "o", "h") else " is a ")


def generate_fn_paramts(fn_name: str, fn_n_range_params: tuple[int]) -> tuple:
    rang = range(1+fn_n_range_params[0], 1+fn_n_range_params[1])
    Fn_params = []
    for x in rang:
        Fn_params.append(f"{fn_name}{x}")
        for y in rang:
            if x > y: continue
            Fn_params.append(f"{fn_name}{x},{y}")

    return tuple(Fn_params)


def generate_bricks_dicts():
    max_bricks = 5
    operators = ("+", "-")
    _vars = ("son", "bossa")
    _vars = tuple(f"B{variables_sys[x].bin}" for x in _vars) #compile vars:
    g_E = generate_fn_paramts(fn_name="E", fn_n_range_params=(1, 16))
    g_X = ("X2", "X3")
    #g_Q = generate_fn_paramts(fn_name="Q", fn_n_range_params=())
    for x in range(1, 1+max_bricks):
        perms = itertools.permutations(operators+g_X+_vars+g_E, r=x)
        for perm in perms:
            _perm = "".join(perm)
            if (perm[0] in operators or
                _perm[0] == "X" or
                _perm[-1:] in operators or
                any([f"{o}X" in _perm for o in operators])
                ): continue
            yield _perm
            #if "X" in "".join(perm): input()

def brute_force(args):
    "I use brute force to discover data combinations, compressing and summarizing musical information"
    if len(args) != 1:
        raise SBR_ERROR("Put just one argument")
    elif isinstance(args[0], (Rhythm, Tones, Melody)):
        raise SBR_ERROR("Put just one Rhythms, Tones and Melodies")
    #Brute force
    data = sbr_line(args[0])

    if isinstance(data, Rhythm):
        if not all([x in "01" for x in data.bin]):
            raise SBR_ERROR("only zeros are allowed in the rhythm :)")
        leng = len(data)
        for code in generate_bricks_dicts():
            code = f"{code}L{leng}"
            #print(code)
            _compile = magia(code).bin
            if _compile == data.bin: return code
            #print(code, _compile)

    elif isinstance(data, Tones):
        return "Jumps0,4"

    elif isinstance(data, Melody):
        start = time.time()
        rh = brute_force([f"B{data.rhythm.bin}"])
        tns = brute_force([repr(data.tones)])
        end = time.time() - start
        print(f"melody found in {end:.2f}s")

        result = "Sm{"+rh+"; "+tns+"}"
    else: raise SBR_ERROR("Put a Tones, Rhythm or Melody data")

    print(result)


def obj_to_array(text_sbr_obj: str, meta_data=False):
        program_path = os.path.abspath(__file__)
        program_directory = os.path.dirname(program_path)
        obj_data = sbr_line(text_sbr_obj)
        #%AppData%
        #Melody
        if isinstance(obj_data, Melody):
            obj_data = Structure([Velocity([0]), seno, obj_data
                                  #it need a default instrument
            ])

        #Rhythm
        elif isinstance(obj_data, Rhythm):
            obj_data = Structure([Instrument(f"{program_directory}/inst/Kick.wav", 2**32), Velocity([0]),
                Melody([obj_data, Tones([6*7]) * obj_data.metric]) #it need a default sample to the Rhythm
            ])

        #Note and tones
        elif isinstance(obj_data, (Tones, Note)):
            if isinstance(obj_data, Note): obj_data = Tones([obj_data])
            obj_data = Structure([seno, Velocity([0]),
                Melody([obj_data, Rhythm('1000'*len(obj_data))]) #it need a default sample to the Rhythm
            ])

        #Instrument
        elif isinstance(obj_data, Instrument):
            obj_data = Structure([
                obj_data, Velocity([0]),
                Melody([Tones([[35, 42, 49]]), Rhythm(1)]) #it need a default sample to the Rhythm
            ])
        #else: raise SBR_ERROR("This isn't a Struct, Tones, Note, Instrument, Rhythm or Melody data")

        wait = "  Wait..."
        print(wait, end="\r")
        __meta_data = Bsound.struct_to_metadata(obj_data)
        if meta_data: return __meta_data
        array = Bsound.audio_render_engine(__meta_data)
        print(" "*len(wait), end="\r")
        return array

def play(args):
    "I bring the sense of sound to life in your brain"
    if len(args) == 0:
        print("Enter a data to play")
    elif len(args) == 1:
        audio_array = obj_to_array(args[0])
        Bsound.play_array(audio_array)
    else:
        audio_array = obj_to_array(args[0])
        Bsound.play_array(audio_array, sleep=args[1])

def pause(args):
    "Umm i just pause, i don't know what u wanna i say .-."
    Bsound.pause()

def export(args):
    "I export addictive substances... the music!!! I've it in mp3, wav and mid, which do you want?"
    #this export to mp3, wav and mid
    if len(args) < 2:
        raise SBR_ERROR("Enter a data to export and the file name",
                        "For example: B1000 : uwu.mp3")

    elif separate_path_extension(args[1])[2].lower() in (".mid", ".midi", ".rmi", ".kar"):
        meta_data = obj_to_array(args[0], meta_data=True)
        mf = lib.MidiFile.MIDIFile(1)
        tempo = variables_user["tempo"]
        mf.addTempo(0, 0, tempo)

        when_kick =  [when*tempo/60 for when in meta_data["position"]]
        duration = [dur/4 for dur in meta_data["duration"]]
        cromatic_note = meta_data["cromatic_note"]
        velocity = [int(vel*100) for vel in meta_data["velocity"]]
        #longit = len(sbr_line(args[0]))//4
        for when, vel, dur, crom in zip(when_kick, velocity, duration, cromatic_note):
            #if when+dur > longit:
                #dur = longit-when #nojda chamo, no tengo cabeza pa una simple formula, njd
            if vel > 127: vel = 127
            mf.addNote(0, 0, crom, when, dur, vel)

        # Exportación del archivo MIDI
        with open(args[1].strip(), "wb") as output_file:
            mf.writeFile(output_file)
    else:
        audio_array = obj_to_array(args[0])
        try: Bsound.sf.write(file=args[1].strip(), data=audio_array, samplerate=Bsound.sample_rate)
        except: raise SBR_ERROR("Error in audio export")


def fn_drag_n_drop(args):
    if not len(args):
        raise SBR_ERROR("Any argument here :O", "mid or mp3 etc : vars like melody, bass etc")
    elif len(args) == 1:
        raise SBR_ERROR("Put the extension and the vars", "mid or mp3 etc : vars like melody, bass etc")
    ext = args[0]
    _vars = [x.strip() for x in args[1:]]
    for var_name in _vars:
        file_name = f"temp/{var_name}.{ext}"
        export([var_name, file_name])
    os.startfile("temp") if os.name == "nt" else os.system("xdg-open temp")
    b_print("Files will be deleted after closing", "Press enter to continue", color=color5)
    input()


def set_max_digits(args):
    "Don't looking for the 5th hand's cat, I'm not so interesting"
    if not len(args):
        return print("set a value please")
    n = sbr_line(args[0])
    if n < 2**31 and n >= 640:
        sys.set_int_max_str_digits(n)
    else: print("the value of being from '640' 'to 2 147 483 647' or '(2**31)-1'")


part = ["0"] * 32
history = []

def record_rhythm(history):
    tempo = variables_user["tempo"]
    global part
    for x in history:
        item = round((x-history[0])*(tempo/15))
        if item < 32:
            part[item] = "1"
        else: item -= 16
    return Rhythm("".join(part))

def rec(_):
    "Hit a enter key on the console and I'll record your rhythm B)"
    global history, part
    print("Hit a enter key on the console and I'll record your rhythm B)")
    print("Listen to the tempo first and then start recording :D")
    play(["C4"])

    part = ["0"] * 32
    history.clear()

    for _ in range(32):
        print(record_rhythm(history))
        d = input()
        history.append(time.time())
        if d.upper() == "D":
            return print()


alt = ""
def piano(args):
    "I'm a piano on a console, what can I say?"
    if len(args) not in (0, 1):
        raise SBR_ERROR("Just one or zero arguments")
    if len(args) == 1:
        instr = sbr_line(args[0])
        if isinstance(instr, Instrument):
            inst_id = instr.inst_id
        else: raise SBR_ERROR("This ain't an Instrument!")
    else: inst_id = seno.inst_id
    keys = {
        #5th octve
        "a": 35, "s": 36, "d": 37, "f": 38,
        "g": 39, "h": 40, "j": 41, "k": 42,
        "l": 43, "ñ": 44, "{": 45,

        #4th octve
        "z": 28, "x": 29, "c": 30, "v": 31,
        "b": 32, "n": 33, "m": 34, ",": 35,
        ".": 36, "-": 37,

        #6th octve
        "q": 42, "w": 43, "e": 44, "r": 45,
        "t": 46, "y": 47, "u": 48, "i": 49,
        "o": 50, "p": 51, "´": 52, "+": 53,
        "}": 54,}
    b_print("Live piano from SBR... ¡Enjoy!", color=color1)
    active = True
    def live_piano(event):
        global alt
        if not active: return
        key_name = event.name
        if "1" == key_name: alt = "b"
        elif "2" == key_name: alt = "#"
        print(key_name, end="\r")
        if key_name.lower() in keys:
            n = Note(keys[key_name.lower()])
            print(f"          Note: {alt}{n}  \r", end="")
            play(["Struct{V0;$"+str(inst_id)+";Sm{B1;M"+str(n)+alt+"}}"])
            alt = ""

    keyboard.on_press(live_piano)
    keyboard.wait("enter")
    active = False


def games(args):
    "I'm a menu with several musical games 4 you ;D"
    # inject the necessary modules
    lib.games.sbr_line = sbr_line
    lib.games.b_color = b_color
    # load the games menu
    lib.games.game_menu(args)


def tap(_):
    "Use me for know the tempo that you are beating"
    print("Mark the tempo to calculate it")
    print("Press D or ctrl+D and Enter when you're done :)")
    while True:
        d = input()
        request = Sbyte.tap()
        if d.upper() == "D":
            return print()
        elif request:
            request = round(request)
            variables_user["tempo"] = request
            print(f"Bpm is {request}", end="\r")
        else: print("Try again")


def sm2(_):
    "A little daw that i made in 2023 after job :)"
    #import sm2


def sm(args_or_melody: list[str] | Melody | Rhythm | Tones):
    "A little script console melody preview that i made in 2024 after work :)"
    if args_or_melody == []: return
    type_data = type(args_or_melody)
    if type_data is Tones:
        tones = args_or_melody
        melody = Melody([
            Rhythm("1000" * len(tones)), tones])
        sm(melody)
        return
    elif type_data not in (Melody, list):
        raise SBR_ERROR("You must only put data Melody")

    elif type_data is list and type_data is not Tones:
        args_or_melody = [sbr_line(y) for y in args_or_melody]
        for x in args_or_melody:
            sm(x)
        return

    #variables
    charters = ["ˍ", "♪", "²", "³", "⁴", "~", "ӡ", "◄", "⁸", "9"]
    #pulse_forte = "|"
    melody = args_or_melody
    rhythm = melody.rhythm
    if not all([x in (0, 1) for x in rhythm]):
        b_print("Args other than 0 and 1 in rhythm can be imprecise".upper(), color="#e00")
    #rhythm_charters = [charters[x] for x in rhythm]
    tones = L(melody.tones, rhythm.metric+1)
    eye_h, eje_v = shutil.get_terminal_size()
    eye_h = len(rhythm) if eye_h > len(rhythm) else eye_h
    _range = tones.max - tones.min +1
    v_org = 0
    h_color = rgb_to_hls(*hex_to_rgb(color1)[:3])[0]
    #generar grafico
    b_print("sm ", end="")
    for x in range(eye_h//4):
        b_print(f"{str(x+1)[-1:]}²³⁴", sep="", end="", color=color2)
    print()
    for r in range(_range):
        actual_note = Note(tones.max-r)
        b_print(f"{str(actual_note):<4}", end="", sep="", color=color1)
        i_note = 0
        for _, fig in enumerate(rhythm, start=1):
            if fig == 0:
                b_print(charters[0], end="", sep="", color=color5)
            else:
                #personalize color
                perz_color = rbg_to_hex(*hls_to_rgb(
                    (h_color + (360/7) * actual_note.bin[0]-1) % 360 # color is defined by the tone
                    , 1, 1))
                if isinstance(tones[i_note], Group):
                    if actual_note in tones[i_note]:
                        b_print(charters[fig], end="", sep="", color=perz_color)
                    else: b_print(charters[0], end="", sep="", color=color1)
                elif actual_note == tones[i_note]:
                    b_print(charters[fig], end="", sep="", color=perz_color)
                else: b_print(charters[0], end="", sep="", color=color5)
                i_note += 1
        v_org += 1
        if v_org+4 > eje_v:
            pause_code(end="")
            v_org = 0
        else: print()
    print(f"Grades: {len(set(tones.one_dimention_int_list))}",
          f"Metric: {rhythm.metric}",
          f"Compasses: {len(rhythm)/16}",
          sep=", ")


def sleep(arg):
    "I pause the code for a few seconds"
    if len(arg) == 0:
        raise SBR_ERROR("Enter the time to sleep")
    else:
        seconds = sbr_line(arg[0])
        if isinstance(seconds, (int, float)):
            time.sleep(seconds)
        else:
            raise SBR_ERROR("Only numbers are allowed")


def donate(_):
    "Help this project continue to grow"
    print("Help this project continue to grow")
    print("https://paypal.me/BrickUwu")
    print("Binance ID: 482 345 114 (recomended)")
    print("Thank you for your donation <3")


def ls(_):
    "If you wanna i show you files and folders..."
    os.system("dir" if os.name == "nt" else "ls")


def fn_pulse(new_pulse):
    "Change the time signature"
    if len(new_pulse) != 1:
        print("Just one argument")
    elif new_pulse[0].isnumeric():
        pulse_will_be(int(new_pulse[0]))
        print(f"Now pulse is {new_pulse[0]} times")
    else: print("Pulse must be an int")


def del_temp(args):
    "I clear temporary files"
    path = "temp"
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


def valve_distortion_gain(args):
    "Set the gain for the valve distortion effect in master"
    if len(args) != 1:
        raise SBR_ERROR("Just one argument")
    elif not args[0].replace(".", "").isnumeric():
        raise SBR_ERROR("Put me a number please >:)")
    Bsound.valve_distortion_gain = float(args[0])


def sbr_if(args):
    "If you try, you can't fail, failure comes from not trying"
    if len(args) < 2:
        raise SBR_ERROR(
            "Syntax error: you must include the condition and code",
            "Example: if true : play son"
            )
    if sbr_line(args[0]):
        sbr_line(":".join(args[1:]))


def sbr_for(args):
    "They did it for you, you do it for them"
    if len(args) < 3:
        raise SBR_ERROR(
            "Syntax error: you must include the variable to iterate over and the code",
            "Example: for degree : Range 1, 11 : play degree|4 : true"
            )
    for x in sbr_line(args[1]):
        sbr_line(f"{args[0]}={x}")
        sbr_line(":".join(args[2:]))


def sbr_while(args):
    "While there is music, there is life, and while there is life, there is music"
    ...


def sbr_fn(args):
    "Hello, have a nice day! :D"
    ...


def sbr_raise(args):
    ...


def info(args):
    "I do several things depending on the type of data you give me"
    for arg in args:
        data = sbr_line(arg)
        type_name = type(data).__name__

        if "str" == type_name:
            print(word_counter(data[1:-1]))

        elif type_name in ("Rhythm", "Group"):
            sbr_type([arg])
            metric([arg])
            sbr_len([arg])

        elif type_name in ("Tones", "Melody"):
            sm([arg])
            sbr_type([arg])
            sbr_len([arg])

        else:
            sbr_type([arg])


def share(args):
    "Share your song as QR or base 64 code"
    if len(args) == 0:
        return
    data = sbr_line(args[0])
    if isinstance(data, str):
        data = data[1:-1].strip()
        if data == "": return

    bytes_encode = str(data).encode()
    bytes_compress = gzip.compress(bytes_encode)
    base64_code = base64.encodebytes(bytes_compress).decode()

    factor = (len(base64_code) / len(bytes_encode))
    factor = round((len(bytes_encode) / len(base64_code) -1) * 100)

    print("before", len(bytes_encode), "after", len(base64_code),
                    "factor", f"{factor}%")
    print(base64_code)


def receive(args):
    "I receive your song as base64 code"
    if len(args) == 0:
        return
    base64_code = args[0].strip()

    try:
        bytes_compress = base64.b64decode(base64_code)
        code = gzip.decompress(bytes_compress).decode()
        print(code)
    except (base64.binascii.Error, gzip.BadGzipFile):
        raise SBR_ERROR("Wrong code")


def reset(args):
    "Reset all"
    global vars_instruments, variables_user, defines
    vars_instruments = default_vars_instruments.copy()
    variables_user = default_variables_user.copy()
    defines = defines.copy()


def define(args):
    "Define like in C"
    global defines
    if len(args) != 2:
        raise SBR_ERROR("Put two arguments")
    defines[args[0].strip()] = args[1].strip()


record = {
    #Keywords
    "if": sbr_if,
    "for": sbr_for,
    "while": sbr_while,
    "fn": sbr_fn,
    "raise": sbr_raise,
    "define": define,
    "reset": reset,
    "quit": sbr_exit,
    "exit": sbr_exit,

    #Tools
    "help": sbr_help,
    "vars": sbr_vars,
    "donate": donate,
    "welcome": sbr_import,
    "licence": sbr_licence,
    "print": sbr_print,
    "share": share,
    "receive": receive,
    "info": info,
    "type": sbr_type,
    "pulse": fn_pulse,
    "clock": clock,
    "ident": ident,
    "play": play,
    "pause": pause,
    "sm": sm,
    "sleep": sleep,
    "export": export,
    "drag_n_drop": fn_drag_n_drop,
    "metric": metric,
    "len": sbr_len,
    "phrase": phrase,
    "piano": piano,
    "rec": rec,
    "tap": tap,
    "ls": ls,
    "games": games,
    "code_made": code_made,
    "instrument": instrument,
    "set_max_digits": set_max_digits,
    "brute_force": brute_force,
    "del_temp": del_temp,
    "valve_gain": valve_distortion_gain,
}
