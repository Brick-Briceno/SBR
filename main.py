"""
SBR IDE developed by @brick_briceno in 2026

This app, developed for Android and Windows, was created to fulfill one
of SBR's many strengths, its easy distribution and virality

This file is not the main kernel file, like __main__.py, this is the
interface initializer, It's called "main" for compilation purposes

I hope it helps you a lot and all of you can experiment with this
the only rule is that there are no rules :)

"""

from kivy.utils import platform

if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE
        ])

from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.utils import get_color_from_hex
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.codeinput import CodeInput
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform
from kivy.app import App
from kivy.core.window import Window
#from kivy.metrics import dp


from interpreter import SBR_ERROR, sbr_line

COLORS = {
    "bg": "#0d1117",
    "accent": "#58a6ff",
    "token_bg": "#21262d",
    "text": "#c9d1d9",
    "play": "#238636",
    "stop": "#da3633",
}


class LineNumberBar(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.1, 0.1, 0.1, 1)
        self.foreground_color = (0.5, 0.5, 0.5, 1)
        self.multiline = True
        self.readonly = True
        self.font_size = "14sp"
        self.size_hint_x = None
        self.width = "40dp"
        self.padding = [10, 10, 5, 10]
        self.background_normal = ""
        self.background_active = ""
        self.background_disabled_normal = ""
        self.background_disabled_active = ""
        self.background_color = (0.1, 0.1, 0.1, 1)


class SBR_Editor(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="horizontal", **kwargs)
        self.spacing = 0
        
        # Create line number bar
        self.line_numbers = LineNumberBar()
        self.line_numbers.bind(height=self.update_line_numbers)
        
        # Create the code input
        self.code_input = CodeInput()
        self.code_input.background_color = get_color_from_hex(COLORS["bg"])
        self.code_input.foreground_color = get_color_from_hex(COLORS["text"])
        self.code_input.font_size = "14sp"
        self.code_input.padding = [10, 10]
        
        # Connect text change events
        self.code_input.bind(text=self.on_text_change)
        self.code_input.bind(cursor=self.update_line_numbers)
        self.code_input.bind(focus=self.update_line_numbers)
        
        # Add widgets
        self.add_widget(self.line_numbers)
        self.add_widget(self.code_input)
        
        # Initial line number update
        self.update_line_numbers()
    
    def update_line_numbers(self, *args):
        """Update the line numbers based on the code input"""
        # Get the current line count
        line_count = len(self.code_input._lines) if hasattr(self.code_input, "_lines") else 1
        
        # Generate line numbers
        line_numbers = "\n".join(str(i + 1) for i in range(max(1, line_count)))
        
        # Update the line numbers display
        self.line_numbers.text = line_numbers
        
        # Ensure the line numbers match the code input"s scrolling
        self.line_numbers.scroll_y = self.code_input.scroll_y
    
    def on_text_change(self, instance, value):
        "This method is called whenever the text changes"
        self.update_line_numbers()
        print(f"Text updated. Length: {len(self.code_input.text)}")
        print(f"Last character: {self.code_input.text[-1] if self.code_input.text else "empty"}")
    
    # Delegate text property to code_input
    @property
    def text(self):
        return self.code_input.text
        
    @text.setter
    def text(self, value):
        self.code_input.text = value
        self.update_line_numbers()
    
    # Delegate other important properties and methods
    def insert_text(self, substring, from_undo=False):
        return self.code_input.insert_text(substring, from_undo)
        
    def delete_selection(self, *args):
        return self.code_input.delete_selection(*args)
        
    def _keyboard_on_key_down(self, *args, **kwargs):
        return self.code_input._keyboard_on_key_down(*args, **kwargs)
        
    def on_touch_down(self, touch, *args, **kwargs):
        # Forward touch events to code_input
        if self.collide_point(*touch.pos):
            touch.push()
            touch.apply_transform_2d(self.code_input.to_local)
            result = self.code_input.on_touch_down(touch, *args, **kwargs)
            touch.pop()
            return result
        return super().on_touch_down(touch, *args, **kwargs)


class TokenButton(Button):
    """Suggestion button for the keyboard"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = get_color_from_hex(COLORS["token_bg"])
        self.color = get_color_from_hex(COLORS["accent"])
        self.size_hint_x = None
        self.width = 120
        #self.font_name = "consola.ttf"


class SBR_IDE(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        # TABS
        self.tp = TabbedPanel(
            do_default_tab=False,
            tab_width=150,
            tab_height=40,
            background_color=(0.1, 0.1, 0.1, 1),
            tab_pos="top_mid"
        )

        # EDITOR TAB
        self.tab_editor = TabbedPanelItem(text="Editor")
        self.code_input = SBR_Editor()
        self.code_input.text = "# SBR Project"
        self.tab_editor.add_widget(self.code_input)

        # INTERPRETER (REPL)
        self.tab_repl = TabbedPanelItem(text="Interpreter")
        repl_layout = BoxLayout(orientation="vertical")

        self.repl_scroll = ScrollView()
        self.repl_output = Label(
            text="[color=#58a6ff]SBR REPL v1.0[/color]>",
            markup=True, font_size="14sp", size_hint_y=None,
            halign="left", valign="top", padding=(10, 10)
        )

        # Manual black background for the Label
        with self.repl_output.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0, 0, 0, 1)
            self.rect = Rectangle(size=self.repl_output.size, pos=self.repl_output.pos)

        self.repl_output.bind(texture_size=self.repl_output.setter("size"))
        self.repl_output.bind(width=lambda s, w: s.setter("text_size")(s, (w, None)))
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
        self.tab_terminal = TabbedPanelItem(text="Terminal")
        terminal_layout = BoxLayout(orientation="vertical")
        
        # ScrollView para la terminal
        self.terminal_scroll = ScrollView()
        self.terminal_output = Label(
            text="[color=#58a6ff]Read-only Terminal\n----------------------[/color]",
            markup=True,
            font_size="14sp",
            size_hint_y=None,
            halign="left",
            valign="top",
            padding=(10, 10)
        )
        self.terminal_output.bind(texture_size=self.terminal_output.setter("size"))
        self.terminal_output.bind(width=lambda s, w: s.setter("text_size")(s, (w, None)))
        self.terminal_scroll.add_widget(self.terminal_output)
        
        # Add Label to terminal layout
        terminal_layout.add_widget(self.terminal_scroll)
        self.tab_terminal.add_widget(terminal_layout)
        self.tp.add_widget(self.tab_terminal)
        
        self.terminal_output.text = ""

        # SUGGESTIONS (TOKENS)
        self.token_scroll = ScrollView(size_hint_y=None, height=50, do_scroll_y=False)
        self.token_bar = GridLayout(rows=1, size_hint_x=None, spacing=5, padding=5)
        self.token_bar.bind(minimum_width=self.token_bar.setter("width"))
        self.setup_token_buttons()

        # PLAY/STOP BUTTON
        self.action_bar = BoxLayout(size_hint_y=None, height=60, padding=5, spacing=10)
        self.btn_play = Button(
            text="PLAY", 
            background_normal="",
            background_color=get_color_from_hex(COLORS["play"]),
            on_release=self.toggle_play_stop
        )

        self.action_bar.add_widget(Label())  # Spacer
        self.action_bar.add_widget(self.btn_play)

        # Status bar to show cursor position
        self.status_bar = Label(
            text="Línea: 1, Columna: 1",
            size_hint_y=None,
            height=30,
            color=(1, 1, 1, 1),
            halign="right",
            valign="middle",
            text_size=(Window.width, None),
            padding_x=10
        )
        
        # Add to main layout (self)
        self.add_widget(self.tp)
        self.add_widget(self.token_scroll)
        self.add_widget(self.action_bar)
        self.add_widget(self.status_bar)
        
        # Set up keyboard listeners
        self.setup_keyboard_listeners()
        
        # Connect cursor position updates
        self.code_input.code_input.bind(cursor=self.update_cursor_position)


    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


    def add_token(self, instance):
        if self.tp.current_tab == self.tab_editor:
            target = self.code_input.code_input
        else:
            target = self.repl_input
        target.insert_text(instance.text + " ")
        target.focus = True


    def toggle_play_stop(self, instance):
        "Run or pause the code"
        if instance.text == "PLAY":
            instance.text = "STOP"
            instance.background_color = get_color_from_hex(COLORS["stop"])
            # Switch to terminal tab
            self.tp.switch_to(self.tab_terminal)

            self.repl_output.text += "\n[color=#58a6ff]Running code...[/color]"
            self.add_to_terminal("[color=#58a6ff]Starting execution...[/color]")

        else:
            instance.text = "PLAY"
            instance.background_color = get_color_from_hex(COLORS["play"])

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
        comando = instance.text.strip()
        if comando:
            # This is where you would call your SBR interpreter
            try:
                obj = sbr_line(comando)
                if obj is not None:
                    self.repl_output.text += f"{obj}\n"
            except SBR_ERROR as e:
                self.repl_output.text += f"{e}\n"

            instance.text = ""

    def add_to_terminal(self, text):
        """Add text to the read-only terminal"""
        if self.terminal_output:
            # Add new text at the beginning so the most recent appears at the top
            self.terminal_output.text = f"{text}\n{self.terminal_output.text}"

    def setup_keyboard_listeners(self):
        """Set up keyboard visibility listeners"""
        # Set initial positions
        self.token_scroll.pos_hint = {"x": 0, "top": 1}
        self.action_bar.pos_hint = {"x": 0, "top": 0}
        self.action_bar.size_hint_y = None
        self.action_bar.height = 60
        
        if platform == "android":
            try:
                from jnius import autoclass
                from android.runnable import run_on_ui_thread
                
                # Get the Android View and WindowManager
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                View = autoclass("android.view.View")
                
                # Get the root view
                activity = PythonActivity.mActivity
                root_view = activity.getWindow().getDecorView().getRootView()
                
                @run_on_ui_thread
                def adjust_for_keyboard():
                    # Calculate keyboard height
                    rect = android.graphics.Rect()
                    root_view.getWindowVisibleDisplayFrame(rect)
                    screen_height = root_view.getHeight()
                    keyboard_height = screen_height - rect.bottom
                    
                    # Update UI on the main thread
                    if keyboard_height > screen_height * 0.15:  # Keyboard is shown
                        Window.keyboard_height = keyboard_height
                        self.token_scroll.y = keyboard_height
                        self.action_bar.y = keyboard_height + self.token_scroll.height
                    else:  # Keyboard is hidden
                        self.token_scroll.y = 0
                        self.action_bar.y = self.token_scroll.height
                
                # Listen for layout changes to detect keyboard
                root_view.getViewTreeObserver().addOnGlobalLayoutListener(
                    lambda: adjust_for_keyboard()
                )
                
            except Exception as e:
                print(f"Error setting up Android keyboard listener: {e}")
                # Fallback to Kivy"s keyboard listener
                Window.bind(keyboard_height=self._on_keyboard_height)
        else:
            # For desktop/other platforms
            Window.bind(keyboard_height=self._on_keyboard_height)
    
    def _on_keyboard_height(self, instance, keyboard_height):
        """Handle keyboard height changes for non-Android platforms"""
        if keyboard_height > 0:
            # Keyboard is shown
            self.token_scroll.y = keyboard_height
            self.action_bar.y = keyboard_height + self.token_scroll.height
        else:
            # Keyboard is hidden
            self.token_scroll.y = 0
            self.action_bar.y = self.token_scroll.height
            
    def update_cursor_position(self, instance, value):
        """Update the status bar with current cursor position"""
        try:
            line = instance.cursor_row + 1  # Convert to 1-based index
            col = instance.cursor_col + 1   # Convert to 1-based index
            self.status_bar.text = f"Línea: {line}, Columna: {col}"
        except Exception as e:
            print(f"Error updating cursor position: {e}")


class SBR_App(App):
    def build(self):
        #Window.clearcolor = get_color_from_hex(COLORS["bg"])
        Window.set_icon("br512.png")
        return SBR_IDE()


if __name__ == "__main__":
    try:
        SBR_App().run()
    except Exception as e:
        import traceback
        if platform != "android":
            with open("/storage/emulated/0/sbr_error.log", "w") as f:
                f.write(str(e) + "\n" + traceback.format_exc())
