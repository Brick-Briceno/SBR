from sbr_parser import only_has, split_without_group
from sbr_types import *
from errors import *
import generators
import effects


class syntax_data:
    # Operators
    math = set("+-")
    # Data types caracteres
    string = "\"'"
    rhythms = "0123456789"
    numbers = ".-0123456789"
    tones = "|b#-0123456789"
    all_data = set(numbers+tones+rhythms)
    numbers_with_operators = ".0123456789+-*/~^&%()"

def something_of_them_in_others(them, others):
    others = set(others)
    #the followin line can be deleted but the str on
    #the argument must be passed, it'd run faster :D
    them = set(them)
    for gen in them:
        if gen in others:
            return True
    return False


def separate_brick(code):
    end = []
    result = []
    brick =  ""
    parmt = False
    code += ",B"
    args = syntax_data.all_data.union(",")
    #keys(code) #throw an error if there is an error in the syntax
    level_key = 0

    string_on_mode = 0 #This variable has 3 modes
    # 0. There are no open quotes
    # 1. It's enabled and collecting arguments
    # 2. Add a quote and say goodbye

    for char in code:
        #If there is an open quotation mark, treat it as an argument
        if char in syntax_data.string:
            string_on_mode += 1

        #everything that is inside a keys will be interpreted as an argument data
        #'elif' bucause keys inside quotation mark are arguments
        elif char == "{": level_key += 1
        elif char == "}":
            level_key -= 1
            brick += "}"
            continue

        #continue with the other logic
        #the complete group (array) is added with all its characters if it's an argument
        if char in args or level_key or string_on_mode:
            # reset string mode
            if string_on_mode == 2:
                string_on_mode = 0
            if not parmt:
                result.append(brick)
                brick = ""
            brick += char
            parmt = True
        else:
            if parmt:
                result.append(delete_args(split_without_group(brick)))
                brick = ""
            brick += char
            parmt = False
    for i in range(0, len(result), 2):
        end.append(result[i:i+2])
    return end


def create_brick(original_list):
    split_list = []
    current_sublist = []
    for sublist in original_list:
        if sublist and sublist[0] in tuple(generators.record):
            if current_sublist:
                split_list.append(current_sublist)
            #start a new sublist (with the current sublist :v)
            current_sublist = [sublist]
        else: current_sublist.append(sublist)

    if current_sublist: split_list.append(current_sublist)
    return split_list


def prepare_metadata(brick_code):
    uwu = separate_brick(brick_code)
    return create_brick(uwu)


def separate_by_operators(cadena):
    result = []
    part = ""
    if cadena[0] in syntax_data.math and cadena[1] not in syntax_data.numbers:
        raise SBR_ERROR(f"You can't start the brick with an operator")
    for caracter, will in zip(cadena, cadena[1:]+"\xff"):
        if (caracter in syntax_data.math and not(
            #There's a diference between sub operator and negative number
            caracter == "-" and will in syntax_data.numbers)):
            result.append(part)
            result.append(caracter)
            part = ""
        else: part += caracter

    result.append(part.strip())
    return [x for x in result if x]


def keys2(code, signo=r"{}"):
    p = 0
    eureca = False
    new = ""
    for x in code:
        if signo[0] == x:
            p += 1
            eureca = True
        elif signo[1] == x:
            if not eureca: raise SBR_ERROR(f"A {signo[0]} was never opened '{code}'")
            p -= 1
            if not p: break
        if eureca: new += x
    if not p-1: raise SBR_ERROR(f"Never closed a '{signo[0]}' '{code}'")
    return new[1:]


def mathematical_operators(data):
    if len(data) <= 2: return data[0]
    a = data[0]
    for i in range(1, len(data) - 1, 2):
        #does this type of data have these methods?
        if not isinstance(a, (Rhythm, Note, Tones, Velocity, Times, Group,
                              Melody, Note, Melody, Polyrhythm, Structure)):
            raise SBR_ERROR(
                f"With the '{type(a).__name__}' type you cannnot concatenate, overlay, or ghost")
        operator = data[i]
        b = data[i + 1]
        if operator is None:
            a = a.concatenate(b)
        elif operator == "+":
            a = a.overlap(b)
        elif operator == "-":
            a = a.ghost(b)
    return a

def keys_are_correct(code, signo=r"{}"):
    p = 0
    for x in code:
        if signo[0] == x:
            p += 1
        elif signo[1] == x:
            if p == 0: raise SBR_ERROR(f"A {signo[0]} was never opened '{code}'")
            p -= 1
    if not p-1: raise SBR_ERROR(f"Never closed a '{signo[0]}' '{code}'")


def prosses_str_array(data):
    keys_are_correct(data)
    level = 0
    item = ""
    new = []
    for char in data[1:-1]+";":
        if char == "{":
            level += 1
        elif char == "}":
            level -= 1
        if char == ";" and not level:
            new.append(item)
            item = ""
            continue
        item += char

    return new

def there_are_operators_in_groups(code: str):
    _code = ""
    if "{" in code and any([y in code for y in syntax_data.math]):
        for x in code:
            if "{" == x:
                _code += "{("
            elif ";" == x:
                _code += ");("
            elif "}" == x:
                _code += ")}"
            else: _code += x
    else: return code
    return _code.replace("()", "")


def insert_multiplication_operators(expression):
    result = ""
    for i, char in enumerate(expression):
        if char == "(" and i > 0 and expression[i-1].isdigit():
            result += f"*{char}"
        elif char == ")" and i < len(expression) - 1 and expression[i+1].isdigit():
            result += f"{char}*"
        else:
            result += char
    return result

def maths(expression):
    try:
        result = eval(insert_multiplication_operators(
        expression.replace("...", "").replace("()", "")))
        if isinstance(result, float):
            if result == 0: return 0 #float to int bro! xdd
            return round(result, 8)
        return result
    except (SyntaxError, TypeError):
        raise SBR_ERROR(f"Invalid formula or syntax '{expression}'")
    except ZeroDivisionError:
        print("infinite")
        raise SBR_ERROR(f"Division by zero error '{expression}'")
    except OverflowError:
        raise SBR_ERROR(f"Result too large '{expression}'")


def arg_to_type(data):
    #Check the data type using the syntax in the characters
    #len = 11, 12, 17 = int_numbers, float_numbers, group
    #The conditions are placed from highest to lowest, except for the rhythms
    #It's number  or mathematical operation
    if data == "+": raise SBR_ERROR("Invalid syntax")

    #strings
    elif data.startswith("\""):
        return data

    elif only_has(data, syntax_data.numbers_with_operators) and data[:2] not in (
        f"0{x}" for x in range(10)) and not(data in "|" or data in "b" or data in "#"):
        return maths(data)

    #rhythms
    elif only_has(data, syntax_data.rhythms):
        return Rhythm(data)

    #tones
    elif only_has(data, syntax_data.tones+"."):
        if "." in data: raise SBR_ERROR("Cannot create notes with floats")
        return Note(data)

    #group
    if "{" in data or "}" in data:
        new = []
        for item in prosses_str_array(data):
            if item == "": continue
            new.append(compiler(item))
        return Group(new)

    #bugs
    elif ";" in data and "{" not in data and "}" not in data:
        raise SBR_ERROR(f"Syntax error '{data}'", advice="You can't use ';' here")
    return magia(data)


def compiler(instruction: str):
    #remove spaces that are not in quotation marks
    result = ""
    inside_quotes = False
    for char in instruction:
        if char in syntax_data.string:
            inside_quotes = not inside_quotes
        if char != " " or inside_quotes:
            result += char
    instruction = result

    #if it's a mathematical operation
    if only_has(instruction, syntax_data.numbers_with_operators) and instruction[
        :2] != "00" and not(instruction in "|" or instruction in "b" or instruction in "#"):
        return maths(instruction)

    #maybe it's a sbr data
    return magia(instruction)


def magia(code):
    #are there operators in groups?
    code = there_are_operators_in_groups(code)
    #Check if there're parentesis here
    while "(" in code or ")" in code:
        parent = keys2(code, "()")
        comp = compiler(parent)
        code = code.replace(f"({parent})", str(comp))

    semi_compiled_code = [] #This will be passed to the operator compiler

    #Operators will split the code
    if only_has(code, syntax_data.math): code = "0"
    for brick in separate_by_operators(code):
        if brick in syntax_data.math:
            semi_compiled_code.pop()
            semi_compiled_code.append(brick)
            continue

        else:
            for g in prepare_metadata(brick):
                #g be like [['B', ['101100111001']]] or [['E', ['5', '14', '16']], ['L', ['9', '32']]]
                if len(g[0]) == 1: raise SBR_ERROR(f"Invalid argument of the generator {g[0]}")
                generator, g_arguments, effects_list = g[0][0], g[0][1], g[1:]

                #convert python strings to SBR types
                g_arguments = [arg_to_type(arg) for arg in g_arguments]

                #continue with the logic
                if generator in tuple(effects.record):
                    raise SBR_ERROR(f"You can't start the brick with an effect: '{generator}'")
                elif generator in tuple(generators.record):
                    data = generators.record[generator](g_arguments)
                    for e, e_arg in effects_list:
                        e_arg = [arg_to_type(arg) for arg in e_arg] #str to sbr type

                        #convert strings to SBR types
                        if not e in tuple(effects.record):
                            raise SBR_ERROR(f"This effect doesn't exist: '{e}'")
                        data = effects.record[e](data, e_arg)
                    semi_compiled_code.append(data)
                    semi_compiled_code.append(None)
                elif "$" in generator:
                    raise SBR_ERROR(
                        f"This instrument is not exist: '{generator}'")
                elif generator.islower():
                    raise SBR_ERROR(
                        f"This variable is not defined: '{generator}'")
                else: raise SBR_ERROR(
                        f"This generator doesn't exist: '{generator}', maybe there's an undefine variable") 

    #process operators
    final_data = mathematical_operators(semi_compiled_code)
    return final_data

