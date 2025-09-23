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

    #BOOLEANS
    "true": 1,
    "false": 0,
    #" and ": " * ",
    #" or ": " + ",

    #NUMBERS
    "phi": (5**.5+1)/2,
    "pi": 3.141592653589793,
    "euler": 2.718281828459045,

    #CHORDS
    "trd": "M{0,2,4}",
    "sep": "M{0,2,4,6}",
    "nov": "M{0,2,4,6,8}",
    "sus4": "M{0,3,4}",
    "sus2": "M{0,1,4}",

    #PROGRESSIONS
    "pop": "M 0,-2,2,-1 Chord1,3,5",
    "soda": "M -2,-1,0 Chord1,3,5",
    "born": "M -2,-3,0 Chord1,3,5",
    # 67(1'7ma)(4'7ma) m
    "zeus": "(trd+-2) (trd+-1) (sep) (sep+3)",
    # 163(7sus4) m
    #"hera": "0",
    # 13671 m
    #"poseidon": "0",
    # 1736 m
    #"demeter": "0",
    # 6513 m
    # 1765m
    # 1374 m
    # 1567 m
    # 1541 m
    # 1561 m
    # 1(b6)(b7)1 m
    # 156 M
    # 14564 M
    # 4156 M
    # 4165M
    # 1564 M
    # 1635 M
    # 6451 M
    # 1(3M)(4m) M
    # 415 M
    # 251 M
    # 1(b7)4 M
    # 2516 M
    # 564511 M
    # 561 M
    # 15634145 M
    # 1(b7)(b6)5 M
    # 1(3M)4(6m) M
    # 17(6’7)7 156(7sus4)7 m
    # 136(7sus4)7 416(7sus)7 m
    # 14(2#)6M M
    # 1(4M)(5M)
    # A E G#7 C#m7 ----  B F#/A# F#m11 A Am9 A/B
    # "ares": "0",
    # "athena": "0",
    # "apollo": "0",
    # "artemis": "0",
    # "hephaestus": "0",
    # "aphrodite": "0",
    # "hermes": "0",
    # "dionysus": "0",
    # "hades": "0",
    # "persephone": "0",
    # "cronus": "0",
    # "rhea": "0",
    # "odin": "0",
    # "frigg": "0",
    # "thor": "0",
    # "loki": "0",
    # "baldur": "0",
    # "freyja": "0",
    # "freyr": "0",
    # "heimdall": "0",
    # "tyr": "0",
    # "idun": "0",
    # "bragi": "0",
    # "sif": "0",
    # "hel": "0",
    # "fenrir": "0",
    # "jormungandr": "0",
    # "sleipnir": "0",
    # "huginn": "0",
    # "muninn": "0",
    # "ymir": "0",
    # "skadi": "0",
    # "njord": "0",
    # "valkyrie": "0",
    # "mjolnir": "0",
    # "asgard": "0",

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

    #TONES (plase don't change, could u corrupt the interpreter)
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
