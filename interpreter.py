from compiler import compiler
from errors import SBR_ERROR
from sbr_parser import *
from variables import *
import commands


def sbr_import(data):
    data = data.replace("\xff", " ")
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


def replace_variables(code: str):
    all_variables = list(variables_sys)+list(variables_user)+list(vars_instruments)
    for variable in all_variables:
        if variable in code: break
    else: return code

    #Sort variables by text length (largest first)
    all_variables = sorted(all_variables, key=len, reverse=True)
    for variable in all_variables:
        if variable in variables_sys:
            code = code.replace(variable, str(variables_sys[variable]))
        elif variable in variables_user:
            code = code.replace(variable, str(variables_user[variable]))
        elif variable in vars_instruments:
            code = code.replace(variable, f"${vars_instruments[variable].inst_id}")

    return code


def sbr_line(idea: str):
    """Process a single line of SBR code"""
    #string
    idea = multiline_string(idea)
    if idea == None: return

    #the code is empety
    elif idea.strip() == "": return
    #clean code
    idea = clean_code(idea)

    #multiline code
    split_lines = ";;" #token to split lines
    if split_lines in idea:
        lines_data = []
        for line in idea.split(split_lines):
            lines_data.append(sbr_line(line))
        #delete None types
        return [x for x in lines_data if x is not None]

    #groups
    idea = indentation(idea)

    #just it's a simple variable
    strip_idea = idea.strip()
    if strip_idea in variables_user:
        return variables_user[strip_idea]
    elif strip_idea in variables_sys:
        return variables_sys[strip_idea]
    elif strip_idea in vars_instruments:
        return vars_instruments[strip_idea]

    #Commands
    #el primer espacio separa el comando de los datos, el : separa los argumentos
    command_and_args_with_spaces = idea.strip().split(" ", 1)
    if command_and_args_with_spaces[0] in commands.record:
        command = command_and_args_with_spaces[0]
        if len(command_and_args_with_spaces) == 1:
            return commands.record[command]([])
        else:
            args = delete_args(command_and_args_with_spaces[1].split(":"))
            return commands.record[command](args)

    #logic to check if it's a variables
    elif "=" in idea:
        var_name, instruction = idea.split("=", 1)
        var_name, instruction = var_name.strip(), instruction.strip()
        #is there a = in the string? (this is not a variable definition)
        if "\"" in var_name: ...
        elif instruction == "":
            raise SBR_ERROR("You have not added anything to the variable")
        #verificar que sea un nombre de variable correcto
        elif var_name == "":
            raise SBR_ERROR("You are adding something to nothing, there is no variable")
        elif not only_has(var_name, "abcdefghijklmnñopqrstuvwxyz_0123456789:") or len(
                        var_name) == 1 or (":" in var_name and not var_name[0].isnumeric()):
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

#send the function to the commands library
commands.sbr_line = sbr_line

#compile the variables

def compile_variables():    
    #ordenar las variables por longitud de nombre de mayor a menor
    for key in variables_user:
        variables_user[key] = sbr_line(str(variables_user[key]))
    for key in variables_sys:
        variables_sys[key] = sbr_line(str(variables_sys[key]))

compile_variables()
