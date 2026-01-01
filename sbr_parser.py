"""
SBR Parser Utilities Module
Centralizes code parsing, cleaning, and comment handling
by @brick_briceno 2025
"""

from errors import SBR_ERROR


"Variables"
open_char = {}
piece_of_code = {}
piece_of_string = ""
open_string = False

COMMENTARY_CHARACTER = "--"


def clean_code(code: str) -> str:
    # Remove all spaces and comments that are not in quotation marks
    if not open_string:
        code = code.split(COMMENTARY_CHARACTER, 1)[0] \
            #.replace(" ", "")

    # Validate ASCII (allow ñ as exception)
    if not(code.isascii() or "ñ" in code):
        raise SBR_ERROR(f"The instruction isn't ascii '{code}'")
    return code


def delete_args(args: list[str]) -> list[str]:
    return [arg for arg in args if arg.strip() != ""]


def only_has(data: str, allowed_characters: str) -> bool:
    "Check if string only contains allowed characters"
    for char in data:
        if char not in allowed_characters:
            return False
    return True


def get_ident_level() -> int:
    """Get the current indentation level"""
    return sum(open_char.values())


def multiline_string(line: str) -> str | None:
    global piece_of_string, open_string
    quotation_is_odd_number = line.count('"') % 2
    if quotation_is_odd_number:
        if open_string:
            open_string = False
            return piece_of_string + line + "\n"
        else:
            open_string = True
            piece_of_string = line + "\n"
    else:
        if open_string:
            piece_of_string += line + "\n"
        else:
            return line


def indentation(code: str, _open="{", _close="}", end=";") -> str:
    """
    Handle multiline code with {} brackets
    Tracks opening and closing braces to allow multiline expressions
    Code is accumulated until all braces are balanced
    """
    if _open not in open_char:
        open_char[_open] = 0
    if _open not in piece_of_code:
        piece_of_code[_open] = ""
    for char in code:
        # Possible errors
        if open_char[_open] == 0 and char == _close:
            piece_of_code[_open] = ""
            raise SBR_ERROR(f"A key was never opened")
        elif open_char[_open] != 0 and char == "=":
            piece_of_code[_open] = ""
            open_char[_open] = 0
            raise SBR_ERROR(f"You cannot assign variables inside an group")
        elif open_char[_open] != 0 and char == ":":
            piece_of_code[_open] = ""
            open_char[_open] = 0
            raise SBR_ERROR(f"You cannot run commands inside an group")

        # Continue with the logic
        elif char is _open:
            open_char[_open] += 1
        elif char is _close:
            open_char[_open] -= 1
        piece_of_code[_open] += char

    if open_char[_open]:
        # Still have open braces, add semicolon and continue
        piece_of_code[_open] += end
        return ""
    # All braces balanced, return complete expression
    end = piece_of_code[_open]
    piece_of_code[_open] = ""
    return end


def split_without_group(code: str, split: str = ",") -> list[str]:
    "Split code by delimiter while respecting {} groups"
    level_key = 0
    brick = ""
    result = []
    for char in code + ",":
        # Everything inside {} is treated as single argument
        if char == "{":
            level_key += 1
        elif char == "}":
            level_key -= 1

        if char == split and not level_key:
            result.append(brick)
            brick = ""
        else:
            brick += char

    return result
