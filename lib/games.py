"""
SBR Games Module
by @brick_briceno 2026
"""

sbr_line = ...
b_color = ...


from b_color import print_color as b_print
import os

# Don't run "sbr line" outside of a function
# Because you'll see something like this

#   File "C:\  >:D  \SBR\lib\games.py", line 4, in <module>
#     sbr_line("play Sm{son Q4; pop} Oct5")
#     ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# TypeError: 'ellipsis' object is not callable

#sbr_line("play Sm{son Q4; pop} Oct5")

def sbr_lines(code: str):
    """Execute SBR code in multiples lines"""
    for line in code.splitlines():
        sbr_line(line)

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu_header():
    """Display the menu header."""
    b_print("""
╔══════════════════════════╗
║      SBR GAMES MENU      ║
╚══════════════════════════╝
""".strip(), color="#e0dd15")


def show_menu_footer():
    "Display the menu footer"
    print("╰──────────────────────────╯")



def auditory_training():
    "A game that tests your musical listening skills"
    clear_screen()
    b_print("🎵 Auditory Training 🎵", color="#4CAF50")
    print("This game will test your ability to recognize musical notes and intervals.")
    input("Press Enter to start the game...")

    print("what scale is this?")

    sbr_lines("""
    tempo = Random 95, 125.
    tone = (Random c_, b_) -3
    mode = Random 0, 11
    --play Struct{V0; $} Oct5 : true
    -- esta vaina hay que terminarla xd

    """)


def game_menu(args):
    "Display the main game menu and handle user input"
    while True:
        clear_screen()
        show_menu_header()
        
        # Display available games
        for i, (name, func) in enumerate(games.items(), start=1):
            print(f" {i}. {name}")
        print(f" {len(games) + 1}. Exit")
        
        show_menu_footer()
        
        choice = input("\nEnter your choice (number): ").strip().lower()
        
        # Check for exit condition
        if choice == str(len(games) + 1) or choice in ('exit', 'quit', 'q'):
            b_print("\nThank you for playing SBR Games! 👋\n", color="#FF5733")
            break

        # Validate input is a number
        if not choice.isdigit():
            input("\n❌ Please enter a valid number. Press Enter to continue...")
            continue
            
        choice_num = int(choice)
        
        # Validate choice is within range
        if choice_num < 1 or choice_num > len(games):
            input(f"\n❌ Please enter a number between 1 and {len(games)}. Press Enter to continue...")
            continue
        
        # Get and execute the selected game
        game_name = list(games.keys())[choice_num - 1]
        games[game_name]()

# Available games dictionary
games = {
    "🎵 Auditory Training": auditory_training,
    # Add more games here as they are developed
}
