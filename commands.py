"""
SBR Commands
"""

#from pprint import pprint
from compiler import (compiler, replace_variables, effects, generators)
from threading import Thread
from pprint import pprint
from variables import *
from sbr_help import *
from os import system
import Bsound
import Sbyte
import editor 
import time
import sys

welcome = """The SBR language provides super creative tools
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

def sbr_help(instruction):
    if len(instruction) != 0:
        h = instruction[0]
        if h in ("effects", "effect"):
            print("The effects are put after a data")
            print("or a generator that in turn returns a data")
            print("Example: B1011 X2")
            print("generator^     ^ effect")
            for keys, value in zip(effects.record.keys(), effects.record.values()):
                print(keys, value.__doc__ if value.__doc__ else 
                      "There's no description", sep=f" {"."*((12)-len(keys))} ")

        elif h in ("generators", "generator"):
            print("Example: B 1011")
            print("generator^ ^^^^one argument")
            for keys, value in zip(generators.record.keys(), generators.record.values()):
                print(keys, value.__doc__ if value.__doc__ else 
                      "There's no description", sep=f" {"."*((12)-len(keys))} ")

        elif h in ("commands", "command"):
            for keys, value in zip(record.keys(), record.values()):
                print(keys, value.__doc__ if value.__doc__ else 
                      "There's no description", sep=f" {"."*((12)-len(keys))} ")

        elif h in ("variables", "variable"):
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
        elif h in ("syntax"):
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
            print("""
 M0,-2,2,-1
 ↑     ↑
 ↑    (0,-2,2,-1) arguments are separated by commas
(M) is used to generate the tones
""")
        else: print(f"No help information for '{instruction[0]}'")
    else:
        from b_color import print_color, hls_to_rgb, rbg_to_hex
        system("cls")
        for i, char in enumerate(welcome.split(" ")):
            grade = 360*(i/len(welcome))*1.5
            h, _, _ = hls_to_rgb(grade, 1, 1)
            r, g, b = hls_to_rgb(h, 1, 1)
            hexa = rbg_to_hex(r, g, b)
            print_color(char, end="", color=hexa, sep=" ")
            time.sleep(.01)

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

invite me a coffee :)
donate:
""")


def sbr_lines_2(idea):
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
    if len(arg) == 0:
        raise SBR_ERROR("Enter the path of an instrument or sample")
    else:
        _id = len(vars_instruments.keys())
        inst = Instrument(arg[0], _id)
        if f"${inst.name}" in vars_instruments.keys():
            print(f"This instrument already exists: {inst.name}")
        vars_instruments[f"${inst.name}"] = inst

def phrase(arg):
    print("Hi! how are you:")

def sbr_vars(arg):
    print("Default")
    pprint(variables_sys)
    print("Instruments")
    pprint(vars_instruments)
    print("Users'")
    pprint(variables_user)

def sbr_exit(_):
    print("Use ctrl+C to exit or cancel processes")
    raise SystemExit

def code_made(args):
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
            with open(args[0]+".sbr", "w") as f:
                f.write(code)
        except: print(f"Error saving the file {args[0]}.sbr")

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
    for x in args:
        data = sbr_lines_2(x)
        if isinstance(data, (Melody, Rhythm)):
            print(f"metric --- {data.metric}")
        else: raise SBR_ERROR("Only rhythms and melodies have metric")

def sbr_print(args):
    for x in args:
        data = sbr_lines_2(x)
        print(data)

def sbr_type(args):
    for arg in args:
        result = sbr_lines_2(arg)
        result_type = type(result).__name__
        print(result, result_type,
              sep=" is an " if result_type[0].upper() in ("a", "e", "i", "o", "h") else " is a ")


def euclidean_brute_force(args):
    ...

def obj_to_array(text_sbr_obj):
        program_path = os.path.abspath(__file__)
        program_directory = os.path.dirname(program_path)
        obj_data = sbr_lines_2(text_sbr_obj)
        #Melody
        if isinstance(obj_data, Melody):
            obj_data = Structure([Instrument(f"{program_directory}\\inst\\Strange Thong", 2**31),
                Velocity([0]), obj_data#it need a default instrument
            ])

        #Rhythm
        elif isinstance(obj_data, Rhythm):
            obj_data = Structure([
                Instrument(f"{program_directory}\\inst\\Kick.wav", 2**32), Velocity([0]),
                Melody([obj_data, Tones([7*7])]) #it need a default sample to the Rhythm
            ])
        
        #Tones
        elif isinstance(obj_data, Tones):
            obj_data = Structure([
                Instrument(f"{program_directory}\\inst\\Strange Thong", 2**32), Velocity([0]),
                Melody([obj_data, Rhythm("10"*len(obj_data))]) #it need a default sample to the Rhythm
            ])

        meta_data = Bsound.struct_to_metadata(obj_data)
        audio_array = Bsound.audio_render_engine(meta_data)
        return audio_array


def play(args):
    if len(args) == 0:
        print("Enter a data to play")
    else:
        audio_array = obj_to_array(args[0])
        Bsound.play_array(audio_array)


def export(args):
    #this export to mp3, wav and .mid
    if len(args) < 2:
        print("Enter a data to export and the file name")
        print("Example: B1000;; uwu.mp3")
    else:
        audio_array = obj_to_array(args[0])
        try: Bsound.sf.write(file=args[1], data=audio_array, samplerate=Bsound.sample_rate)
        except: raise SBR_ERROR("Error in audio export")


def template(args): #command template
    ...

def set_max_digits(args):
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

def tap(_):
    print("Mark the tempo to calculate it")
    print("Press D and Enter when you're done :)")
    while 1:
        d = input()
        request = Sbyte.tap()
        if d.upper() == "D": break
        elif request:
            request = round(request)
            print(f"Bpm is {request}", end="\r")
        else: print("Try again")

def rec(_):
    __doc__ = "Kick enter to record the Rhythm faster"
    print("Kick enter to record the Rhythm faster")
    print("Listen to the tempo first and then start recording :D")
    play(["C4"])
    global history, part
    part = ["0"]*32
    history.clear()
    for _ in range(32):
        print(record_rhythem(history))
        input()
        history.append(time.time())

def sbr_editor(_):
    Thread(target=editor.main).start()

def sleep(arg):
    if len(arg) == 0:
        raise SBR_ERROR("Enter the time to sleep")
    else:
        s = sbr_lines_2(arg[0])
        if isinstance(s, (int, float)):
            time.sleep(s)
        else: raise SBR_ERROR("Only numbers are allowed")

def donate(_):
    print("Help this project continue to grow")
    print("https://paypal.me/BrickUwu")
    print("Binance ID: 482 345 114 (recomended)")
    print("Thank you for your donation <3")


record = {
    "help": sbr_help,
    "donate": donate,
    "exit": sbr_exit,
    "print": sbr_print,
    "type": sbr_type,
    #"pulse": fn_pulse,
    "vars": sbr_vars,
    "clock": clock,
    "ident": ident,
    "play": play,
    "sleep": sleep,
    "export": export,
    "metric": metric,
    "phrase": phrase,
    "editor": sbr_editor,
    "rec": rec,
    "tap": tap,
    "code_made": code_made,
    "instrument": instrument,
    "set_max_digits": set_max_digits,
    "euclidean_brute_force": euclidean_brute_force,
}
