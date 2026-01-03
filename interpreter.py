from compiler import compiler
from errors import SBR_ERROR
from sbr_parser import *
from variables import *
import generators
import commands


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
        elif not only_has(var_name, "abcdefghijklmnñopqrstuvwxyz_0123456789:") or len(
                        var_name) == 1 or (":" in var_name or var_name[0].isnumeric()):
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

#send the function to the commands and generators library
commands.sbr_line = sbr_line
generators.sbr_line = sbr_line

#compile the variables

def compile_variables():    
    #ordenar las variables por longitud de nombre de mayor a menor
    for key in variables_user:
        variables_user[key] = sbr_line(str(variables_user[key]))
    for key in variables_sys:
        variables_sys[key] = sbr_line(str(variables_sys[key]))

compile_variables()
