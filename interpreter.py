import commands
from sbr_types import Melody, Rhythm, Group, Tones
from compiler import (only_has, replace_variables, compiler,
                      delete_args, variables_sys, variables_user,
                      off_long_comment, delete_comments, SBR_ERROR)
#system vars
piece_of_code = ""
open_keys = 0


def indentation(code, symbols="{}"):
    global piece_of_code
    global open_keys
    _open, _close = symbols
    for char in code:
        #possible errors
        if open_keys == 0 and char == "}":
            piece_of_code = ""
            raise SBR_ERROR(f"A key was never opened")
        elif open_keys != 0 and char == "=":
            piece_of_code = ""
            open_keys = 0
            raise SBR_ERROR(f"You cannot assign variables inside an group")
        elif open_keys != 0 and char == ":":
            piece_of_code = ""
            open_keys = 0
            raise SBR_ERROR(f"You cannot run commands inside an group")

        #continue with the logic
        elif char is _open:
            open_keys += 1
        elif char is _close:
            open_keys -= 1
        piece_of_code += char

    if open_keys:
        piece_of_code += ";"
        return ""
    end = piece_of_code
    piece_of_code = ""
    return end

def clean_code(code):
    #delete spaces
    code = code.replace(" ", "")
    code = code.replace("\t", "")
    #delete comments
    #multiline group
    #is it ascii?
    if not(code.isascii() or "ñ" in code):
        raise SBR_ERROR("The instruction isn't ascii")
    return code

def sbr_import(data):
    data = data.replace("\xff", " ")
    try:
        with open(data, "r") as _file:
            _file = _file.read()
        for n_line, line in enumerate(_file.splitlines(), start=1):
            sbr_line(line)
    except SBR_ERROR as bad:
        raise SBR_ERROR(f"Import error in line {n_line}:", bad)
    except FileNotFoundError:
        raise SBR_ERROR(f"Import error this file doesn't exist '{data}'")
    except PermissionError:
        raise SBR_ERROR(f"The system doesn't have permission to accesss this file '{data}'")


def sbr_line(idea):
    #multiline code
    if "\\"*3 in idea:
        lines_data = []
        for line in idea.split("\\"*3):
            lines_data.append(sbr_line(line))
        #delete None types
        return [x for x in lines_data if x is not None]

    #import file
    imp = idea.split()
    if imp != []:
        if imp[0] in ("import", "welcome"):
            if len(imp) == 2:
                sbr_import(imp[1])
            else: raise SBR_ERROR("You must import a code file")
            return
        elif imp[0] == "for":
            # 1=variable, 2=iter object, 3=code
            if len(imp) == 4:
                iter_obj = sbr_line(imp[2])
                if isinstance(iter_obj, int):
                    iter_obj = range(iter_obj)
                #convert the objet to a group
                else: iter_obj = sbr_line(f"{imp[2]}G")
                lines_data = []
                for x in iter_obj:
                    sbr_line(f"{imp[1]}={x}")
                    lines_data.append(sbr_line(imp[3]))
                return [x for x in lines_data if x is not None]
            else: raise SBR_ERROR(
                "For loop must have varible name, iter object and code")
            return

    #delete comments and indentation
    idea = delete_comments(idea)
    idea = indentation(idea)

    #the code is empety
    if idea == "": return
    #logic to check the type of instruction
    elif "=" in idea:
        idea = clean_code(idea)
        var_name, instruction = idea.split("=", 1)
        if instruction == "":
            raise SBR_ERROR("You have not added anything to the variable")
        #verificar que sea un nombre de variable correcto
        elif var_name == "":
            raise SBR_ERROR("You are adding something to nothing, there is no variable")
        elif not only_has(var_name, "abcdefghijklmnñopqrstuvwxyz_0123456789:") or var_name == "b" or (":" in var_name and not var_name[0].isnumeric()):
            raise SBR_ERROR(f"This is not a valid variable name '{var_name}'")
        elif var_name in variables_sys:
            raise SBR_ERROR(f"This variable '{var_name}' is immutable and cannot be modified, please chose another name")
        #all correct
        instruction = replace_variables(instruction)
        instruction = compiler(instruction)
        #Check if a specific metric is necessary
        if ":" in var_name:
            metric, var_name = var_name.split(":", 1)
            metric = compiler(metric)
            if not isinstance(metric, int):
                raise SBR_ERROR("The metric must be expressed in integers")
            if isinstance(instruction, (Melody, Rhythm)):
                if metric != instruction.metric:
                    raise SBR_ERROR(f"The metric entered must be {metric} and this data is {instruction.metric}")
            else: raise SBR_ERROR("This data type has no metric")
        variables_user[var_name] = instruction

    elif ":" in idea:
        command, instruction = idea.split(":", 1)
        command = clean_code(command)
        instruction = instruction.strip()
        if command == "":
            raise SBR_ERROR("You need to write a command")
        elif not command in commands.record:
            raise SBR_ERROR(f"This command does not exist '{command}'")
        else: #all correct
            commands.record[command](delete_args(instruction.split(";;")))
    else:
        idea = clean_code(idea)
        #Detect and replace variables
        idea = replace_variables(idea)
        idea = idea.replace(" ", "")
        #compile, which is actually interpreting xD
        return compiler(idea)

