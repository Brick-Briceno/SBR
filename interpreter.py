"""
Interpreter developed by @brick_briceno in 2025

"""

from compiler import compiler
from errors import SBR_ERROR
from sbr_utils import *
from variables import *
import generators
import keywords


"Variables"
ident_level = 0
piece_of_string = ""
open_string  = False
piece_of_code_in_groups = ""
COMMENTARY_TOKEN = "--"
SPLIT_LINES_TOKEN = ";;"


def get_ident_level() -> int:
    return ident_level

def get_if_open_string() -> int:
    return open_string


def replace_variables(code: str) -> str:
    all_variables = list(variables_sys)+list(variables_user)+list(vars_instruments)
    all_variables = sorted(all_variables, key=len, reverse=True)

    #Split by quotes and process only the parts outside quotes (even indices)
    split_code = code.split('"')
    for i in range(0, len(split_code), 2): #Only process even indices
        piece_of_code = split_code[i]
        for variable in all_variables:
            if variable in variables_sys:
                piece_of_code = piece_of_code.replace(
                    variable, str(variables_sys[variable]))
            elif variable in variables_user:
                piece_of_code = piece_of_code.replace(
                    variable, str(variables_user[variable]))
            elif variable in vars_instruments:
                piece_of_code = piece_of_code.replace(
                    variable, f"${vars_instruments[variable].inst_id}")
        split_code[i] = piece_of_code

    return '"'.join(split_code)


def keys(code: str) -> str:
    """
    Handle multiline code with {} brackets
    Tracks opening and closing braces to allow multiline expressions
    Code is accumulated until all braces are balanced
    """
    global piece_of_code_in_groups, ident_level, open_string

    for char in code:
        #if he string is open
        if char == "\"": open_string = not open_string
        # Possible errors!!!
        elif ident_level == 0 and char == "}" and not open_string:
            piece_of_code_in_groups = ""
            ident_level = 0
            raise SBR_ERROR(f"A key was never opened")

        elif ident_level != 0 and char == "=" and not open_string:
            piece_of_code_in_groups = ""
            ident_level = 0
            raise SBR_ERROR(f"You cannot assign variables inside an group")

        # Continue with the logic
        elif char == "{" and not open_string:
            ident_level += 1
        elif char == "}"and not open_string:
            ident_level -= 1
        piece_of_code_in_groups += char

    if ident_level:
        # Still have open braces, add semicolon and continue
        piece_of_code_in_groups += ";"
        return

    # All braces balanced, return complete expression
    _end = piece_of_code_in_groups
    piece_of_code_in_groups = ""
    return _end


def clean_code(code: str) -> str:
    # Remove all spaces and comments that are not in quotation marks
    if COMMENTARY_TOKEN in code:
        i = 0
        global open_string
        code2 = code.replace(COMMENTARY_TOKEN, "\x00")
        for char in code2:
            i += 1
            if char == "\"":
                open_string = not open_string

            elif char == "\x00" and not open_string:
                i += len(COMMENTARY_TOKEN) - 1
                return code[:i - len(COMMENTARY_TOKEN)]

    return code


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
            # ---> return None <--- 
    else:
        if open_string:
            piece_of_string += line + "\n"
        else:
            return line


def sbr_line(idea: str):
    """Process a single line of SBR code"""
    #the code is empety
    if idea.strip() == "": return

    #multiline code
    if SPLIT_LINES_TOKEN in idea:
        lines_data = []
        for line in idea.split(SPLIT_LINES_TOKEN):
            lines_data.append(sbr_line(line))
        #delete None types
        return [x for x in lines_data if x is not None]

    #clean code
    idea = clean_code(idea)
    if idea == "": return

    #string
    idea = multiline_string(idea)
    if idea == None: return

    #groups 
    idea = keys(idea)
    if idea == None: return

    #just it's a simple variable
    strip_idea = idea.strip()
    if strip_idea in variables_user:
        return variables_user[strip_idea]
    elif strip_idea in variables_sys:
        return variables_sys[strip_idea]
    elif strip_idea in vars_instruments:
        return vars_instruments[strip_idea]

    #keywords
    #el primer espacio separa el comando de los datos, el : separa los argumentos
    keyword_and_args_with_spaces = idea.strip().split(" ", 1)
    if keyword_and_args_with_spaces[0] in keywords.record:
        keyword = keyword_and_args_with_spaces[0]
        if len(keyword_and_args_with_spaces) == 1:
            return keywords.record[keyword]([])
        else:
            args = white_spaces_in_list(keyword_and_args_with_spaces[1].split(":"))
            return keywords.record[keyword](args)

    #logic to check if it's a variables
    elif "=" in idea:
        var_name, instruction = idea.split("=", 1)
        var_name, instruction = var_name.strip(), instruction.strip()
        #is there a = in the string? (this is not a variable definition)
        if "\"" in var_name:
            #compile, which is actually interpreting xD
            idea = replace_variables(idea)
            hola = compiler(idea)
            return hola
        elif instruction == "":
            raise SBR_ERROR("You have not added anything to the variable")
        #verificar que sea un nombre de variable correcto
        elif var_name == "":
            raise SBR_ERROR("You are adding something to nothing, there is no variable")
        elif not only_has(var_name, "abcdefghijklmnñopqrstuvwxyz_0123456789") or len(
                        var_name) == 1 or var_name[0].isnumeric():
            raise SBR_ERROR(f"This is not a valid variable name '{var_name}'")
        elif var_name in variables_sys:
            raise SBR_ERROR(f"This variable '{var_name}' is immutable and cannot be modified, please chose another name")

        #if everything is ok
        instruction = replace_variables(instruction)
        instruction = compiler(instruction)
        variables_user[var_name] = instruction

    else:
        #compile, which is actually interpreting xD
        idea = replace_variables(idea)
        hola = compiler(idea)
        return hola

#send the function to the keywords and generators library
keywords.sbr_line = sbr_line
generators.sbr_line = sbr_line

#compile the variables

def compile_variables():    
    #ordenar las variables por longitud de nombre de mayor a menor
    for key in variables_user:
        variables_user[key] = sbr_line(str(variables_user[key]))
    for key in variables_sys:
        variables_sys[key] = sbr_line(str(variables_sys[key]))

compile_variables()
