from interpreter import sbr_line, SBR_ERROR
import itertools

characters = (",", "B,", "E,", "L,", "Q,", "S,", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-")
characters = (",", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "-", "M,", "Jumps,", "{", "}")

length = 7

length_of_arguments = 0
effects_to_use = 0
generators_to_use = 0
operators_to_use = 0

the_match = "0,4,0,-1,-1,"

# Print the generated text
for combination in itertools.product(characters, repeat=length):
    text = "".join(combination)
    if text[0] in ("L", "X", "S", "Q"): continue
    elif text[0].isnumeric(): continue
    elif text[0] == ",": continue
    text = text.replace(",,", "")
    try:
        print(text)
        result = sbr_line(f"{text}")
        #print(result, text)
        if str(result) == the_match:
            print(text, the_match, "\nthe end")
            break
    except SBR_ERROR: 0
