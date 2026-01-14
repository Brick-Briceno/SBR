"""
SBR IDE developed by @brick_briceno in 2026

This app, developed for Android and Windows, was created to fulfill one
of SBR's many strengths, its easy distribution and virality

This file is not the main kernel file, like __main__.py, this is the
interface initializer. It's called "main" for compilation purposes.

I hope it helps you a lot and all of you can experiment with this
the only rule is that there are no rules :)

"""

from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.utils import get_color_from_hex
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.codeinput import CodeInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.app import App

#from interpreter import sbr_line


COLORS = {
    'bg': '#0d1117',
    'accent': '#58a6ff',
    'token_bg': '#21262d',
    'text': '#c9d1d9',
    'play': '#238636',
    'stop': '#da3633',
}


class SBR_Editor(CodeInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = get_color_from_hex(COLORS['bg'])
        self.foreground_color = get_color_from_hex(COLORS['text'])
        self.font_name = 'consola.ttf'
        self.font_size = '14sp'
        
        # Connect text_validate event to detect changes
        self.bind(text=self.on_text_change)
    
    def on_text_change(self, instance, value):
        "This method is called whenever the text changes"
        print(f"Text updated. Length: {len(self.text)}")
        print(f"Last character: {self.text[-1] if self.text else 'empty'}")


class TokenButton(Button):
    """Suggestion button for the keyboard"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = get_color_from_hex(COLORS['token_bg'])
        self.color = get_color_from_hex(COLORS['accent'])
        self.size_hint_x = None
        self.width = 120
        self.font_name = 'consola.ttf'


class SBR_IDE(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # TABS
        self.tp = TabbedPanel(
            do_default_tab=False,
            tab_width=150,  # Fixed width for each tab
            tab_height=40,   # Tab height
            background_color=(0.1, 0.1, 0.1, 1),  # Tab panel background color
            tab_pos='top_mid'  # Tab position (top center)
        )

        # EDITOR TAB
        self.tab_editor = TabbedPanelItem(text='Editor')
        self.code_input = SBR_Editor(text='# SBR Project\nprint "Hello World"')
        self.tab_editor.add_widget(self.code_input)

        # INTERPRETER (REPL)
        self.tab_repl = TabbedPanelItem(text='Interpreter')
        repl_layout = BoxLayout(orientation='vertical')

        self.repl_scroll = ScrollView()
        self.repl_output = Label(
            text="[color=#58a6ff]SBR REPL v1.0[/color]>",
            markup=True, font_size='14sp', size_hint_y=None,
            halign='left', valign='top', padding=(10, 10)
        )

        # Manual black background for the Label
        with self.repl_output.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 1)
            self.rect = Rectangle(size=self.repl_output.size, pos=self.repl_output.pos)

        self.repl_output.bind(texture_size=self.repl_output.setter('size'))
        self.repl_output.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.repl_output.bind(size=self._update_rect, pos=self._update_rect)

        self.repl_scroll.add_widget(self.repl_output)

        self.repl_input = TextInput(
            multiline=False, size_hint_y=None, height=50,
            background_color=(0.1, 0.1, 0.1, 1), foreground_color=(1,1,1,1)
        )
        # Bind REPL Enter key
        self.repl_input.bind(on_text_validate=self.enviar_a_repl)
        
        repl_layout.add_widget(self.repl_scroll)
        repl_layout.add_widget(self.repl_input)
        self.tab_repl.add_widget(repl_layout)
        
        # Add tabs to TabbedPanel (interpreter first)
        self.tp.add_widget(self.tab_repl)
        self.tp.add_widget(self.tab_editor)

        # TERMINAL (read-only)
        self.tab_terminal = TabbedPanelItem(text='Terminal')
        terminal_layout = BoxLayout(orientation='vertical')
        
        # ScrollView para la terminal
        self.terminal_scroll = ScrollView()
        self.terminal_output = Label(
            text="[color=#58a6ff]Read-only Terminal\n----------------------[/color]",
            markup=True,
            font_size='14sp',
            size_hint_y=None,
            halign='left',
            valign='top',
            padding=(10, 10)
        )
        self.terminal_output.bind(texture_size=self.terminal_output.setter('size'))
        self.terminal_output.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.terminal_scroll.add_widget(self.terminal_output)
        
        # Add Label to terminal layout
        terminal_layout.add_widget(self.terminal_scroll)
        self.tab_terminal.add_widget(terminal_layout)
        self.tp.add_widget(self.tab_terminal)
        
        # Método para agregar texto a la terminal
        self.terminal_output.text = ""

        # SUGGESTIONS (TOKENS)
        self.token_scroll = ScrollView(size_hint_y=None, height=50, do_scroll_y=False)
        self.token_bar = GridLayout(rows=1, size_hint_x=None, spacing=5, padding=5)
        self.token_bar.bind(minimum_width=self.token_bar.setter('width'))
        self.setup_token_buttons()  # Configure token buttons

        # PLAY/STOP BUTTON
        self.action_bar = BoxLayout(size_hint_y=None, height=60, padding=5, spacing=10)
        self.btn_play = Button(
            text='PLAY', 
            background_normal='',
            background_color=get_color_from_hex(COLORS['play']),
            on_release=self.toggle_play_stop
        )

        self.action_bar.add_widget(Label())  # Spacer
        self.action_bar.add_widget(self.btn_play)

        # Add to main layout (self)
        self.add_widget(self.tp)
        self.add_widget(self.token_scroll)
        self.add_widget(self.action_bar)


    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


    def add_token(self, instance):
        target = self.code_input if self.tp.current_tab == self.tab_editor else self.repl_input
        target.insert_text(instance.text + " ")
        target.focus = True


    def toggle_play_stop(self, instance):
        "Run or pause the code"
        if instance.text == 'PLAY':
            instance.text = 'STOP'
            instance.background_color = get_color_from_hex(COLORS['stop'])
            # Switch to terminal tab
            self.tp.switch_to(self.tab_terminal)

            self.repl_output.text += "\n[color=#58a6ff]Running code...[/color]"
            self.add_to_terminal("[color=#58a6ff]Starting execution...[/color]")

        else:
            instance.text = 'PLAY'
            instance.background_color = get_color_from_hex(COLORS['play'])

            self.repl_output.text += "\n[color=#da3633]Execution stopped[/color]"
            self.add_to_terminal("[color=#da3633]Execution stopped[/color]")


    def setup_token_buttons(self, suggestions=["play", "print", ";", ",", ""]):
        """Configure tokens in the suggestion bar"""
        # Clear existing buttons if any
        self.token_bar.clear_widgets()
        
        # Create buttons for each token
        for t in suggestions:
            btn = TokenButton(text=t)
            btn.bind(on_release=self.add_token)
            self.token_bar.add_widget(btn)
        
        # Make sure ScrollView contains the button layout
        if self.token_bar not in self.token_scroll.children:
            self.token_scroll.add_widget(self.token_bar)

    def enviar_a_repl(self, instance):
        # This is the logic for the REPL to work
        comando = instance.text
        if comando.strip():
            self.repl_output.text += f"\n[b]>[/b] {comando}\n"
            # This is where you would call your SBR interpreter
            self.repl_output.text += "\n"*5
            
            # Also show the command in the terminal
            self.add_to_terminal(f"[color=#58a6ff]Command executed:[/color] {comando}")
            instance.text = ""

    def add_to_terminal(self, text):
        """Add text to the read-only terminal"""
        if self.terminal_output:
            # Add new text at the beginning so the most recent appears at the top
            self.terminal_output.text = f"{text}\n{self.terminal_output.text}"


class SBR_App(App):
    def build(self):
        Window.clearcolor = get_color_from_hex(COLORS['bg'])
        return SBR_IDE()


if __name__ == '__main__':
    SBR_App().run()
