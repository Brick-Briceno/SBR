from sbr_types import *

"Variables"

code_that_has_been_made = []

variables_user = {
    "tempo": 128,
    "tone": 5,
    "mode": "B101101011010",
    }

vars_instruments = {}

variables_sys = {
    #RHYTHMS
    "offbeat": "B0010",
    "son": "B1001001000101000",
    "bossa": "B1001001000100100",
    "dembow":"B10010010",
    "shiko": "B1000101000101000",
    "soukous": "B1001001000110000",
    "rumba": "B1001000100101000",
    "gahu": "B100100100010010",

    #CHORDS

    #PORGRESSIONS
    "pop": "M0,-2,2,-1 Chord1,3,5",

    #The Scales are formed by their mode and their tone

    #MODES
    "lydian": "B101010110101",
    "lonic": "B101011010101", #major
    "mixolidian": "B101011010110",
    "doric": "B101101010110",
    "wind": "B101101011010", #minor
    "phrygian": "B110101011010",
    "locrian": "B110101101010",
    "minor_harmonic": "B101101011001",
    "arabic": "B110011011001",
    "hungara": "B101100111001",

    #TONES
    "a_": 9,
    "a#_": 10,
    "b_": 11,
    "c_": 0,
    "c#_": 1,
    "d_": 2,
    "d#_": 3,
    "e_": 4,
    "f_": 5,
    "f#_": 6,
    "g_": 7,
    "g#_": 8,
}

#don't delete this code
for i, x in enumerate(variables_sys):
    if not x.islower():
        raise TypeError(
            f"The variable's name must be lower '{list(variables_sys)[i]}'")
