"""
SBR games
by @brick_briceno 2026
"""

sbr_line = ...
b_color = ...
from b_color import print_color as b_print

# Don't run "sbr line" outside of a function
# Because you'll see something like this

#   File "C:\  >:D  \SBR\lib\games.py", line 4, in <module>
#     sbr_line("play Sm{son Q4; pop} Oct5")
#     ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# TypeError: 'ellipsis' object is not callable

#sbr_line("play Sm{son Q4; pop} Oct5")


def auditory_training():
    "A game tests your listening skills in music"


def game_menu(args):
    b_print("""
    Welcome to SBR video games!
    Select the game number and have fun!
    """.strip())
    print(b_color)


games = {
    "Auditory training": auditory_training
}
