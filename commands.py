"""
SBR Commands
"""

#from pprint import pprint
from compiler import (compiler, replace_variables, magia,
                      effects, generators, pulse_will_be)
from b_color import (hls_to_rgb, hex_to_rgb, rbg_to_hex, rgb_to_hls,
                     color1, color2, color3, color4, color5)
from b_color import print_color as b_print
from threading import Thread
from pprint import pprint
from sbr_utils import *
from variables import *
from sbr_help import *
import itertools
import shutil
import midiutil
import Bsound
import Sbyte
import time
import lib
import sys
import os

welcome = """
▒█▀▀▀█ ▒█▀▀█ ▒█▀▀█ 
░▀▀▀▄▄ ▒█▀▀▄ ▒█▄▄▀ 
▒█▄▄▄█ ▒█▄▄█ ▒█░▒█

The SBR language provides super creative tools
to musicians to make good music and from this make memorable melodies

With all my heart I hope that good things can be
made with this tool, I hope that people have fun experimenting
with it and that it helps all of you make better music, hugs <3

@Brick_briceno 2023
"""

def clean_code(code):
    #delete spaces
    code = code.replace(" ", "")
    code = code.replace("\t", "")
    #delete comments
    code = delete_comments(code)
    #there's no multiline group uwu
    #is it ascii?
    if not(code.isascii() or "ñ" in code):
        raise SBR_ERROR("The instruction isn't ascii")
    return code


off_long_comment = True
def delete_comments(code):
    #delete short comment
    code = code.split("--", 1)[0]
    new_code = ""
    global off_long_comment
    code = code.replace("***", "\xff")
    for char in code:
        if char == "\xff":
            off_long_comment = not off_long_comment
        elif off_long_comment:
            new_code += char
    return new_code.replace("\xff", "")

def sbr_licence(_):
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
            b_print("the Commands are awsome!", color=color1)
            sbr_help(["commands"]), input()
            b_print("check the SBR's Documentation for learn music and more about this increible lenguage ;)", color=color2)
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

        elif "command" in h.lower():
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
        input()
        print("""Type 'help:' and the function to study
For example type:
help: tutorial
help: effects
help: generators
help: commands
help: operators
help: syntax
help: E

licence:

invite me a coffee :)
donate: <3
""")


def sbr_lines_2(idea: str):
    idea = clean_code(idea)
    #The code is empety
    if idea == "": raise
    #Detect and replace variables
    idea = replace_variables(idea)
    #delete spaces
    idea = idea.replace(" ", "").replace("\t", "")
    #compile, which is actually interpreting xD
    return compiler(idea)


def compile_variables():
    for var_name, var_content in zip(variables_user.keys(), variables_user.values()):
        variables_user[var_name] = sbr_lines_2(str(var_content))
    for var_name, var_content in zip(variables_sys.keys(), variables_sys.values()):
        variables_sys[var_name] = sbr_lines_2(str(var_content))

compile_variables()

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

def print_dict(d: dict, name: str):
    b_print(name, color=color1)
    for k, v in zip(d, d.values()):
        b_print(k, color=color3, end="")
        b_print("=", end="", color=color5)
        b_print(v, color=color4)

def sbr_vars(args):
    print_dict(vars_instruments, "Instruments")
    print_dict(variables_sys, "Constants")
    print_dict(variables_user, "Of Users")

def sbr_exit(_):
    "Never give up, stay hard"
    print("Use Ctrl+C to exit or cancel any processes")
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
    #organize arguments
    if len(args) == 0: return
    elif len(args) == 1:
        spaces = 4
        code = sbr_lines_2(args[0])
    else:
        if not args[0].isnumeric(): raise SBR_ERROR("This value must be numeric")
        code = sbr_lines_2(args[1])
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
    for x in args:
        data = sbr_lines_2(x)
        if isinstance(data, (Melody, Rhythm)):
            print(f"metric --- {data.metric}")
        else: raise SBR_ERROR(f"Only rhythms and melodies have metric, not {type(data.__name__)}")

def sbr_len(args):
    "What length is a data"
    for x in args:
        ""
        data = sbr_lines_2(x)
        if isinstance(data, (Melody, Rhythm, Group, Tones)):
            print(f"len --- {len(data)}")
        else: raise SBR_ERROR(f"Only rhythms and melodies have len, not {type(data.__name__)}")

def sbr_print(args):
    for x in args:
        data = sbr_lines_2(x)
        print(data)

def sbr_type(args):
    for arg in args:
        result = sbr_lines_2(arg)
        result_type = type(result).__name__
        print(result, result_type,
              sep=" is an " if result_type[0].lower() in (
                  "a", "e", "i", "o", "h") else " is a ")


tokens_tones = ("Jumps", "M", "", "", "", "", "", "", )
tokens_rhythm = {"E": tuple("E"+",".join([str(z) for z in x])
                        for x in itertools.permutations(range(1, 18), 3)),
                 "C": tuple("C"+",".join([str(z) for z in x])
                        for x in itertools.permutations(range(1, 33), 2)),
                 "N": tuple("N"+",".join([str(z) for z in x])
                        for x in itertools.permutations(range(1, 10**3), 1)),
                 }

tokens_effects = ("*,", "L,", "X,", "S,", "Q,", "R,", "I,", ">>,",
                  "<<,", "[,", "],", "D,", "Add,",)

def brute_force(args):
    #print("THE COMMAND WILL BE AVAILABLE SOON")
    #return
    if len(args) != 1:
        raise SBR_ERROR("Put just one argument")
    elif isinstance(args[0], (Rhythm, Tones, Melody)):
        raise SBR_ERROR("Put just one Rhythms, Tones and Melodies")
    #Brute force
    data = sbr_lines_2(args[0])

    if isinstance(data, Rhythm):
        for x in range(1, 4):
            for y in itertools.permutations(("+", "-")+
                                            tokens_rhythm["E"]+
                                            tokens_rhythm["C"]+
                                            tokens_rhythm["N"], x):
                print("".join(y))

        return "E"

    elif isinstance(data, Tones):
        return "Jumps0,5"

    elif isinstance(data, Melody):
        start = time.time()
        rh = brute_force([f"B{data.rhythm.bin}"])
        tns = brute_force([repr(data.tones)])
        end = time.time() - start
        print(f"melody found in {end:.2f}s")

        result = "Sm{"+rh+"; "+tns+"}"

    print(result)


def obj_to_array(text_sbr_obj: str, meta_data=False):
        program_path = os.path.abspath(__file__)
        program_directory = os.path.dirname(program_path)
        obj_data = sbr_lines_2(text_sbr_obj)
        #%AppData%
        #Melody
        if isinstance(obj_data, Melody):
            obj_data = Structure([seno, Velocity([0]), obj_data
                                  #it need a default instrument
            ])

        #Rhythm
        elif isinstance(obj_data, Rhythm):
            obj_data = Structure([Instrument(f"{program_directory}\\inst\\Kick.wav", 2**32), Velocity([0]),
                Melody([obj_data, Tones([7*7])]) #it need a default sample to the Rhythm
            ])

        #Note and tones
        elif isinstance(obj_data, (Tones, Note)):
            if isinstance(obj_data, Note): obj_data = Tones([obj_data])
            obj_data = Structure([seno, Velocity([0]),
                Melody([obj_data, Rhythm('10'*len(obj_data))]) #it need a default sample to the Rhythm
            ])

        #Instrument
        elif isinstance(obj_data, Instrument):
            obj_data = Structure([
                obj_data, Velocity([0]),
                Melody([Tones([[35, 42, 49]]), Rhythm(1)]) #it need a default sample to the Rhythm
            ])

        wait = "Wait..."
        print(wait, end="\r")
        __meta_data = Bsound.struct_to_metadata(obj_data)
        if meta_data: return __meta_data
        array = Bsound.audio_render_engine(__meta_data)
        print(" "*len(wait), end="\r")
        return array

def play(args):
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
    "I export addictive substances... the music! I've it in mp3, wav and mid, which do you want?"
    #this export to mp3, wav and mid
    if len(args) < 2:
        raise SBR_ERROR("Enter a data to export and the file name",
                        "For example: B1000:: uwu.mp3")

    elif separate_path_extension(args[1])[2].lower() in (".mid", ".midi", ".rmi", ".kar"):
        meta_data = obj_to_array(args[0], meta_data=True)
        mf = midiutil.MIDIFile(1)
        tempo = variables_user["tempo"]
        mf.addTempo(0, 0, tempo)

        when_kick =  [when*tempo/60 for when in meta_data["position"]]
        duration = [dur/4 for dur in meta_data["duration"]]
        cromatic_note = meta_data["cromatic_note"]
        velocity = [int(vel*100) for vel in meta_data["velocity"]]
        #longit = len(sbr_lines_2(args[0]))//4
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
        raise SBR_ERROR("Any argument here :O", "mid or mp3 whit:: vars like melody, bass etc")
    drags = []
    ext = args[0]
    _vars = [x.strip() for x in args[1:]]
    for var_name in _vars:
        file_name = f"temp/{var_name}.{ext}"
        export([var_name, file_name])
        drags.append(file_name)

    lib.drag_n_drop.main(drags)


def set_max_digits(args):
    "Don't looking for the 5th hand's cat"
    if not len(args):
        return print("set a value please")
    n = sbr_lines_2(args[0])
    if n < 2**31 and n >= 640:
        sys.set_int_max_str_digits(n)
    else: print("the value of being from '640' 'to 2 147 483 647' or '(2**31)-1'")


history = []

part = ["0"]*32

def record_rhythem(history):
    tempo = variables_user["tempo"]
    global part
    for x in history:
        item = round((x-history[0])*(tempo/15))
        if item < 32:
            part[item] = "1"
        else: item -= 16
    return Rhythm("".join(part))

def rec(_):
    "Kick enter to record the Rhythm faster"
    print("Kick enter to record the Rhythm faster")
    print("Listen to the tempo first and then start recording :D")
    play(["C4"])
    global history, part
    part = ["0"]*32
    history.clear()
    for _ in range(32):
        print(record_rhythem(history))
        d = input()
        history.append(time.time())
        if d.upper() == "D":
            return print()


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


def sbr_editor(_):
    "A simple text editor"
    Thread(target=lib.editor.main).start()

def sm2(_):
    "A little daw that i was made in 2023 after job :)"
    #import sm2

def sleep(arg):
    "I pause the code for a few secounds"
    if len(arg) == 0:
        raise SBR_ERROR("Enter the time to sleep")
    else:
        s = sbr_lines_2(arg[0])
        if isinstance(s, (int, float)):
            time.sleep(s)
        else: raise SBR_ERROR("Only numbers are allowed")

def donate(_):
    "Help this project continue to grow"
    print("Help this project continue to grow")
    print("https://paypal.me/BrickUwu")
    print("Binance ID: 482 345 114 (recomended)")
    print("Thank you for your donation <3")

def ls(_):
    "If you wanna i show you files and folders..."
    #ls command in bash
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
    "I clear temporal files"
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

record = {
    "help": sbr_help,
    "donate": donate,
    "exit": sbr_exit,
    "licence": sbr_licence,
    "print": sbr_print,
    "type": sbr_type,
    "pulse": fn_pulse,
    "vars": sbr_vars,
    "clock": clock,
    "ident": ident,
    "play": play,
    "pause": pause,
    "sm2": sm2,
    "sleep": sleep,
    "export": export,
    "drag_n_drop": fn_drag_n_drop,
    "metric": metric,
    "len": sbr_len,
    "phrase": phrase,
    "editor": sbr_editor,
    "rec": rec,
    "tap": tap,
    "ls": ls,
    "code_made": code_made,
    "instrument": instrument,
    "set_max_digits": set_max_digits,
    "brute_force": brute_force,
    "del_temp": del_temp,
    "valve_distortion_gain": valve_distortion_gain,
}
