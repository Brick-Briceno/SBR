from interpreter import sbr_line, SBR_ERROR
import itertools

def generate_text(characters, length):
    return [''.join(combination) for combination in itertools.product(characters, repeat=length)]

characters = "0123456789"
characters = (",", "E,", "L,", "Q,", "S,", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
length = 2
generated_text = generate_text(characters, length)

length_of_arguments = 0
effects_to_use = 0
generators_to_use = 0
operators_to_use = 0

print(generated_text)

the_match = "10001010101010001101101010101110"
            #10001000100010001000100010001000

# Print the generated text
for text in generated_text:
    if text[0] in ("L", "X", "S", "Q"): continue
    elif text[0].isnumeric(): continue
    elif text[0] == ",": continue
    text = text.replace(",,", "")
    try:
        result = sbr_line(f"({text})L32")
        #print(result, text)
        if result.bin == the_match:
            print(text, the_match, "\nthe end")
            break
    except SBR_ERROR: 0
