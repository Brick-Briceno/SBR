import os

def clean_console():
    "Clears the console on all systems"
    if os.name == 'nt':  # For Windows
        os.system("cls") # this run in cmd, no powershell, clear ain't in cmd
    else:  # For Linux and macOS (and other Unix-like systems)
        os.system("clear")

def one_dimention_list_recurtion(group):
    new = []
    for item in group:
        if not isinstance(item, list):
            new.append(item)
        else:
            for x in one_dimention_list_recurtion(item):
                new.append(x)
    return new

def white_spaces_in_list(args):
    for _ in range(args.count("")):
        args.remove("")
    return args


def white_spaces_in_list(args: list[str]) -> list[str]:
    return [arg for arg in args if arg.strip() != ""]


def only_has(data: str, allowed_characters: str) -> bool:
    "Check if string only contains allowed characters"
    for char in data:
        if char not in allowed_characters:
            return False
    return True


def convert_unions_to_tuples(x) -> tuple | None:
    t = x.__args__[0]
    if t is None: return t #, in other universe this returned a tuple
    elif isinstance(t, type):
        return t,
    else: return t.__args__


def separate_path_extension(file_path: str):
    # Get the directory and the filename
    directory, filename = os.path.split(file_path)
    # Separate the filename and the extension
    name, extension = os.path.splitext(filename)
    return directory, name, extension


def format_time(seconds: float):
    if seconds < 0:
        return f"{seconds} Time can't be negative"
    MICROSECONDS = 1e-6
    MILLISECONDS = 1e-3
    MINUTES = 60
    HOURS = MINUTES * 60
    DAYS = HOURS * 24

    if seconds >= DAYS:
        return f"{seconds / DAYS:.2f} days"
    elif seconds >= HOURS:
        return f"{seconds / HOURS:.2f} h"
    elif seconds >= MINUTES:
        return f"{seconds / MINUTES:.2f} min"
    elif seconds >= 1:
        return f"{seconds:.2f} s"
    elif seconds >= MILLISECONDS:
        return f"{seconds * 1e3:.2f} ms"
    elif seconds >= MICROSECONDS:
        return f"{seconds * 1e6:.2f} µs"
    else:
        return f"{seconds * 1e9:.2f} ns"

def extract_keys(text: str) -> list[str]:
    results = []
    temp = ""
    inside = False
    for char in text:
        if char == "{":
            inside = True
            continue
        elif char == "}":
            inside = False
            if temp:
                results.append(temp)
                temp = ""
            continue
        if inside:
            temp += char            
    return results


def word_counter(text: str) -> str:
    len_text = len(text)
    spaces = text.count(" ")
    words = len(text.split())
    sentences = (
          text.count("?")
        + text.count("!")
        + text.count(". ") #the spaces are in case there are ellipses
        + text.count(".\n")
        )

    return f"""
Text Features:
Words {words}
Reading Time {format_time(words * 60 / 250)}
Characters {len_text}
Characters without spaces {len_text - spaces}
Paragraphs {len(text.split("\n"))}
Sentences {sentences + 1}
""".strip()


def this_is_in_quotation(thing: str, text: str) -> bool:
    _string_is_open = False
    for char in text.replace(thing, "\x00"):
        if char == "\"":
            _string_is_open = not _string_is_open   
        elif char == "\x00" and _string_is_open:
            return True
    return False

