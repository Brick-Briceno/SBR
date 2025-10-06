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
from b_color import (color1, color2, color3,
                    color4, color5) # a random palette of colors
from interpreter import sbr_line, SBR_ERROR
import interpreter as sbr_ident
from traceback import format_exc
from datetime import datetime
from sbr_utils import *
import platform
import time
import sys
import os

"""
pip install soundfile
pip install colorama
pip install pygame
pip install numpy
"""

__version__ = "2.0.7"

# Set to True to enable debug mode, which will raise exceptions instead of logging them
DEBUG = False
if any(cm in sys.argv for cm in ("-d", "-dev")):
    sys.argv.pop(1) if sys.argv[1] in ("-d", "-dev") else 0
    DEBUG = True

program_path = os.path.abspath(__file__)
program_directory = os.path.dirname(program_path)

# Create 'temp' folder if it does not exist
temp_dir = os.path.join(program_directory, "temp")
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)


def error_log():
    print("SBR has stopped working")
    print("Send bug.log file to the creator of this program")
    lines = ""
    for line in code_that_has_been_made:
        lines += line+"\n"
    with open("bug.log", "a") as _file:
        _file.write(f"system time {datetime.now()}\n"
        f"SBR version: {__version__}\n"
        f"Python version: {platform.python_version()}\n"
        f"Platform: {platform.platform()}\n\n"
        f"Program path: {program_path}\n\n"
        f"Commands entered by the user:\n{lines}\n{'*'*32}\n"
        f"Python errors:\n\n{format_exc()}\n\n")
    input("Press a key...")


try: sbr_line(f"welcome {program_directory.replace(" ", "\xff")}/main.sm")
except SBR_ERROR as bad:
    clean_console()
    b_print("Error:", color=color3, end="")
    b_print(bad, color=color4)
    b_print("Please create the preset file, no matter if the file is empty", color=color2)
    b_print("Do you want to create it? type 'yes'", color=color5)
    if input("> ").lower() == "yes":
        with open(os.path.join(program_directory, "main.sm"), "w") as _file:
            _file.write("***\n"
                        "This is the main preset file for SBR\n"
                        "You can add your own presets here\n"
                        "or leave it empty to use the default presets\n"
                        "***\n\n")
        b_print("File created successfully! please try to reload the program", color=color1)
    sbr_line("exit:")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        if not DEBUG: clean_console()
        b_print(f"Welcome to SBR {".".join(__version__.split(".")[:2])} by @Brick_briceno", color=color1)
        b_print("Type 'help:' for more info or 'exit:' to... exit", color=color2)
        awake = True
        ident = 2
        while awake:
            try:
                consol = ""
                if not sbr_ident.open_keys or sbr_ident.long_comment: consol = "> "
                else: consol = "  "+(" "*ident*sbr_ident.open_keys)
                if DEBUG: consol = "(dev) " + consol
                command = input(consol)
                if command in ("cls", "clear", "..", "..."): clean_console()
                elif command in ("pause", "\x10", "."): sbr_line("pause:")
                else:
                    code_that_has_been_made.append(command)
                    # calculate time of ejecution
                    start = time.time()
                    result = sbr_line(command)
                    if DEBUG and result is not None:
                        b_print(type(result).__name__, format_time(time.time() - start), end=" ")
                    # print types
                    if result is not None:
                        try:
                            if type(result) is list:
                                for line in result: b_print(line, color=color1)
                            else: b_print(result, color=color1)
                        except ValueError:
                            b_print("Result is too large to view, the limit is "
                                    f"{sys.get_int_max_str_digits()}", color=color3)
                            b_print("If you wanna change this use 'set_max_digits:' "
                                    "(640 to 2 147 483 647 range)", color=color4)
            except SBR_ERROR as bad:
                b_print("Error:", color=color3, end="")
                b_print(bad, color=color4)
            except (KeyboardInterrupt, EOFError, SystemExit): awake = False
            #if u wanna do it without protection comment the following line of code
            except Exception as e:
                if DEBUG: raise e
                awake = error_log() #create a log
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
                if DEBUG: raise bad
                print(f"Error in line {n}:", bad)
            except (KeyboardInterrupt, SystemExit):
                b_print("good bye!", color=color5)
            except Exception as e:
                if DEBUG: raise e
                error_log() #create a log

    else:
        try:
            with open(sys.argv[1], "r") as _file:
                _file = _file.read()
            for n, line in enumerate(_file.splitlines(), start=1):
                b_print(f" Loading.{'.'*(n%3)} line {n}", " "*15, end="\r", color=color1)
                code_that_has_been_made.append(line)
                sbr_line(line)
        except SBR_ERROR as bad:
            b_print(f"Error in line {n}:", bad)
        except (KeyboardInterrupt, SystemExit):
            b_print("good bye!", color=color5)
        except FileNotFoundError:
            b_print(f"This file does not exist '{sys.argv[1]}'")
        except OSError:
            b_print(f"Invalid argument '{sys.argv[1]}' Did you mean -> -code '{sys.argv[1]}' <-?")
        except Exception as e:
            if DEBUG: raise e
            error_log() #create a log

#clean trash
sbr_line("del_temp:")
