"""
The SBR language provides super creative tools
to musicians to make good music and from this make memorable melodies

With all my heart I hope that good things can be
made with this tool I hope that people have fun experimenting
with it and that it helps them make better music, hugs <3

@Brick_briceno 2023
"""

from variables import code_that_has_been_made
from b_color import print_color as b_print
from b_color import random_palette
from interpreter import sbr_line, SBR_ERROR
import interpreter as sbr_ident
from traceback import format_exc
from datetime import datetime
import platform
import sys
import os

"""
pip install soundfile
pip install pygame
pip install numpy
pip install numba
pip install colorama
"""

__version__ = "2.0.0"

color1, color2, color3, color4, color5 = random_palette()

def error_log():
    print("SBR has stopped working")
    print("Send bug.log file to the creator of this program")
    lines = ""
    for line in code_that_has_been_made:
        lines += line+"\n"
    with open("bug.log", "a") as f:
        f.write(f"system time {datetime.now()}\n")
        f.write(f"sbr version: {__version__}\n")
        f.write(f"python version: {platform.python_version()}\n")
        f.write(f"platform: {platform.platform()}\n\n")
        f.write(f"Commands entered by the user:\n{lines}\n{"*"*32}\n")
        f.write(f"Python errors:\n\n{format_exc()}\n\n")
    input("Press a key...")


program_path = os.path.abspath(__file__)
program_directory = os.path.dirname(program_path)

try: sbr_line(f"welcome {program_directory}\\main.sm")
except SBR_ERROR as bad:
    b_print("Error:", color=color3, end="")
    b_print(bad, color=color4)
    b_print("Please create the preset file, no matter if the file is empty", color=color2)
    sbr_line("exit:")


if __name__ == "__main__" and len(sys.argv) == 1:
    os.system("cls")
    b_print(f"Welcome to SBR {".".join(__version__.split(".")[:2])} by @Brick_briceno", color=color1)
    b_print("Type 'help:' for more info or 'exit:' to... exit", color=color2)
    awake = True
    ident = 2
    while awake:
        try:
            command = input("> " if not (sbr_ident.open_keys or not sbr_ident.off_long_comment)
                            else "  "+(" "*ident*sbr_ident.open_keys))
            if command in ("cls", "clear", "..", "..."): os.system("cls")
            else:
                code_that_has_been_made.append(command)
                result = sbr_line(command)
                if result is not None:
                    try:
                        if type(result) is list:
                            for line in result: b_print(line, color=color1)
                        else: b_print(result, color=color1)
                    except ValueError:
                        b_print(f"Result is too large to view, the limit is {sys.get_int_max_str_digits()}", color=color3)
                        b_print("If you wanna change this use set_max_digits: (640 to 2 147 483 647 range)", color=color4)
        except SBR_ERROR as bad:
            b_print("Error:", color=color3, end="")
            b_print(bad, color=color4)
        except (KeyboardInterrupt, EOFError, SystemExit): awake = False
        #if u wanna do it without protection comment the following line of code
        except Exception: awake = error_log() #create a log
    b_print("good bye!", color=color5)

elif sys.argv[1] == "-v":
    b_print(f"SBR {__version__} by @Brick_briceno")

elif sys.argv[1] in ("-h", "-help"):
    if len(sys.argv) >= 3:
        sbr_line(f"help:{sys.argv[2]}")
    else: sbr_line("help:")

elif sys.argv[1] in ("-c", "-code"):
    if len(sys.argv) >= 3:
        try:
            for n, line in enumerate(sys.argv[2].splitlines(), start=1):
                code_that_has_been_made.append(line)
                sbr_line(line)
        except SBR_ERROR as bad:
            print(f"Error in line {n}:", bad)
        except Exception: error_log() #create a log
else:
    try:
        with open(sys.argv[1], "r") as _file:
            _file = _file.read()
        for n, line in enumerate(_file.splitlines(), start=1):
            code_that_has_been_made.append(line)
            sbr_line(line)
    except SBR_ERROR as bad:
        b_print(f"Error in line {n}:", bad)
    except FileNotFoundError:
        b_print(f"This file does not exist '{sys.argv[1]}'")
    except Exception: error_log() #create a log
