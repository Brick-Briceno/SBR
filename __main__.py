"""
The SBR language provides super creative tools
to musicians to make good music and from this make memorable melodies

With all my heart I hope that good things can be
made with this tool I hope that people have fun experimenting
with it and that it helps them make better music, hugs <3

@Brick_briceno 2022
"""

# ============================================================================
# IMPORTS
# ============================================================================

# Standard library
import os
import sys
import time
import platform
from datetime import datetime
from traceback import format_exc

# SBR modules
from interpreter import sbr_line, SBR_ERROR, get_if_open_string, get_ident_level
from b_color import color1, color2, color3, color4, color5
from sbr_utils import clean_console, format_time
from variables import code_that_has_been_made
from b_color import print_color as b_print
from keywords import sbr_import

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

__version__ = "2.0.12"

# Debug mode flag
DEBUG = False

# Program paths
program_path = os.path.abspath(__file__)
program_directory = os.path.dirname(program_path)
temp_dir = os.path.join(program_directory, "temp")


# ============================================================================
# SETUP & INITIALIZATION
# ============================================================================

def parse_debug_flag():
    """Parse and remove debug flag from sys.argv"""
    global DEBUG
    if any(cm in sys.argv for cm in ("-d", "-dev")):
        if len(sys.argv) > 1 and sys.argv[1] in ("-d", "-dev"):
            sys.argv.pop(1) 
        DEBUG = True


def setup_environment():
    """Initialize environment (create temp folder, etc.)"""
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)


def initialize_main_preset():
    """Load main.sm preset file or prompt user to create it"""

    if not os.path.exists(os.path.join(program_directory, "main.sm")):
        #clean_console()
        b_print("Error:", color=color3, end="")
        b_print("The main preset file does not exist", color=color4)
        b_print("Please create the preset file, no matter if the file is empty", color=color2)
        b_print("Do you want to create it? type 'yes'", color=color5)

        if input("> ").lower() == "yes":
            with open(os.path.join(program_directory, "main.sm"), "w") as _file:
                _file.write("\"\n"
                           "This is the main preset file for SBR\n"
                           "You can add your own presets here\n"
                           "or leave it empty to use the default presets\n"
                           "\"\n\n")
            b_print("File created successfully! please try to reload the program", color=color1)
    try: sbr_import(["main.sm"])
    except SBR_ERROR as bad:
        b_print("Error:", color=color3, end="")
        b_print(bad, color=color4)
        sbr_line("exit")


# ============================================================================
# ERROR HANDLING
# ============================================================================

def error_log():
    """Create a bug log file with error details"""
    print("SBR has stopped working")
    print("Send bugs.log file to the creator of this program")
    
    lines = "\n".join(code_that_has_been_made)
    
    with open("bugs.log", "a") as _file:
        _file.write(
            f"system time {datetime.now()}\n"
            f"SBR version: {__version__}\n"
            f"Python version: {platform.python_version()}\n"
            f"Platform: {platform.platform()}\n\n"
            f"Program path: {program_path}\n\n"
            f"keywords entered by the user:\n{lines}\n"
            f"{'*' * 32}\n"
            f"Python errors:\n\n{format_exc()}\n\n"
        )

    input("Press a key...")


def handle_sbr_error(error: SBR_ERROR, line_number: int = None):
    """Handle SBR errors with consistent formatting"""
    if line_number:
        b_print(f"Error in line {line_number}:", color=color3, end=" ")
    else:
        b_print("Error:", color=color3, end="")
    b_print(error, color=color4)


def handle_exception(exception: Exception):
    """Handle unexpected exceptions"""
    if DEBUG: raise exception
    error_log()


# ============================================================================
# KEYWORD HANDLERS
# ============================================================================

def get_prompt_string():
    """Generate appropriate prompt string based on state"""
    if not (get_ident_level() or get_if_open_string()):
         consol = "> " if not DEBUG else "(dev) > "
    else:
        indent_chars = 4
        consol = "  " + (" " * indent_chars * get_ident_level())
    return consol


def print_result(result):
    """Print execution result with proper formatting"""
    if result is None: return
    try:
        if type(result) is list:
            for line in result:
                b_print(line, color=color1)
        else:
            b_print(result, color=color1)
    except ValueError:
        b_print(
            f"Result is too large to view, the limit is {sys.get_int_max_str_digits()}",
            color=color3
        )
        b_print(
            "If you wanna change this use 'set_max_digits' (640 to 2 147 483 647 range)",
            color=color4
        )


def run_repl():
    """Run interactive REPL (Read-Eval-Print Loop)"""
    if not DEBUG:
        clean_console()

    b_print(f"Welcome to SBR {__version__} by @Brick_briceno", color=color1)
    b_print("Type 'help' for more info or 'exit' to... exit", color=color2)

    awake = True
    while awake:
        try:
            input_text = input(get_prompt_string())
            # Special keywords
            if input_text in ("cls", "clear", "..", "..."):
                clean_console()
                continue

            elif input_text == "exit":
                # The keyword 'exit' already exists, but beginners should
                # know that 'Ctrl+C' makes it easier to exit :)
                print("Use Ctrl+C to exit or cancel any processes")
                return
            elif input_text in ("pause", "\x10", "."):
                sbr_line("pause")
                continue

            # Execute keyword
            code_that_has_been_made.append(input_text)
            start = time.time()
            result = sbr_line(input_text)

            # Show debug info
            if DEBUG:
                elapsed = format_time(time.time() - start)
                if type(result) not in (type(None), list):
                    b_print(type(result).__name__, end="")
                b_print(elapsed, end="")

            # Print result
            print_result(result)

        # Errors
        except SBR_ERROR as bad:
            handle_sbr_error(bad)
        except (KeyboardInterrupt, EOFError, SystemExit):
            awake = False
        except MemoryError:
            handle_sbr_error(
                SBR_ERROR("There is not enough RAM to perform this operation")
                )
        except Exception as e:
            if DEBUG: raise e
            awake = error_log() # Returns None so loop exits

    b_print("good bye!", color=color5)


def run_file(filepath: str):
    """Execute a .sm file"""
    try:
        with open(filepath, "r") as _file:
            code = _file.read()
        
        for n, line in enumerate(code.splitlines(), start=1):
            b_print(
                f" Loading.{'.' * (n % 3)} line {n}",
                " " * 15,
                end="\r",
                color=color1
            )
            code_that_has_been_made.append(line)
            sbr_line(line)

    except SBR_ERROR as bad:
        handle_sbr_error(bad, n)
    except FileNotFoundError:
        b_print(f"This file does not exist '{filepath}'", color=color3)
    except OSError:
        b_print(
            f"Invalid argument '{filepath}' Did you mean -> -code '{filepath}' <-?",
            color=color3
        )
    except (KeyboardInterrupt, SystemExit):
        b_print("good bye!", color=color5)
    except MemoryError:
        handle_sbr_error(
            SBR_ERROR("There is not enough RAM to perform this operation")
            )
    except Exception as e:
        handle_exception(e)


def run_code_string(code: str):
    """Execute code from string (for -c flag)"""
    try:
        for n, line in enumerate(code.splitlines(), start=1):
            code_that_has_been_made.append(line)
            sbr_line(line)
    except SBR_ERROR as bad:
        if DEBUG:
            raise bad
        handle_sbr_error(bad, n)
    except (KeyboardInterrupt, SystemExit):
        b_print("good bye!", color=color5)
    except MemoryError:
        handle_sbr_error(SBR_ERROR("There is not enough RAM to perform this operation"))
    except Exception as e:
        handle_exception(e)


def show_version():
    """Display SBR version"""
    b_print(f"SBR {__version__}")


def show_help(topic: str = None):
    """Display help information"""
    if topic:
        sbr_line(f"help {topic}")
    else: sbr_line("help")


# ============================================================================
# MAIN DISPATCHER
# ============================================================================

def main():
    """Main entry point - dispatch based on keyword line arguments"""
    # Parse flags
    parse_debug_flag()
    # Setup environment
    setup_environment()
    initialize_main_preset()

    # No arguments - run REPL
    if len(sys.argv) == 1:
        run_repl()
        return
    
    # Parse keyword
    keyword = sys.argv[1]
    if keyword == "-v":
        show_version()

    elif keyword in ("-h", "-help"):
        topic = sys.argv[2] if len(sys.argv) >= 3 else None
        show_help(topic)
    
    elif keyword in ("-c", "-code"):
        if len(sys.argv) >= 3:
            run_code_string(sys.argv[2])
        else:
            b_print("Error: -code requires a code string argument", color=color3)    
    else:
        # Assume it's a file path
        run_file(keyword)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
