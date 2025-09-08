from tkinter import filedialog, messagebox
import tkinter as tk
import os

class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("SBR Code Editor")
        self.root.geometry("500x350")
        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

        # Dark theme configuration
        self.bg_color = "#2E3440"  # Background color
        self.fg_color = "#D8DEE9"  # Text color
        self.menu_bg_color = "#3B4252"  # Menu background color
        self.menu_fg_color = "#ECEFF4"  # Menu text color
        self.text_area_bg = "#3B4252"  # Text area background color
        self.text_area_fg = "#ECEFF4"  # Text area text color
        self.select_bg_color = "#4C566A"  # Selection background color
        self.select_fg_color = "#ECEFF4"  # Selection text color
        self.line_number_bg = "#2E3440"  # Line number background color
        self.line_number_fg = "#81A1C1"  # Line number text color

        # Configure the main window background
        self.root.configure(bg=self.bg_color)

        # Larger font
        self.font = ("Consolas", 14)

        # Create a frame to contain the text area and line numbers
        self.text_frame = tk.Frame(self.root, bg=self.bg_color)
        self.text_frame.pack(expand=True, fill="both")

        # Create a Canvas for line numbers
        self.line_numbers = tk.Canvas(
            self.text_frame,
            bg=self.line_number_bg,
            width=50,
            highlightthickness=0
        )
        self.line_numbers.pack(side="left", fill="y")

        # Create the text area
        self.text_area = tk.Text(
            self.text_frame,
            wrap="word",
            undo=True,
            bg=self.text_area_bg,
            fg=self.text_area_fg,
            insertbackground=self.fg_color,
            selectbackground=self.select_bg_color,
            selectforeground=self.select_fg_color,
            font=self.font,
            padx=10,
            pady=10
        )
        self.text_area.pack(side="right", expand=True, fill="both")

        # Configure the scrollbar
        self.scrollbar = tk.Scrollbar(self.text_area)
        self.scrollbar.pack(side="right", fill="y")
        self.scrollbar.config(command=self.text_area.yview)
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        # Bind events to update line numbers
        self.text_area.bind("<KeyRelease>", self.update_line_numbers)
        self.text_area.bind("<MouseWheel>", self.update_line_numbers)
        self.text_area.bind("<Button-1>", self.update_line_numbers)
        self.scrollbar.bind("<MouseWheel>", self.update_line_numbers)

        # Create the menu
        self.menu_bar = tk.Menu(root, bg=self.menu_bg_color, fg=self.menu_fg_color)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.menu_bg_color, fg=self.menu_fg_color)
        self.file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        self.file_menu.add_command(label="Open", accelerator="Ctrl+O", command=self.open_file)
        self.file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit_app)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        # Edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.menu_bg_color, fg=self.menu_fg_color)
        self.edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.text_area.edit_undo)
        self.edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.text_area.edit_redo)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", accelerator="Ctrl+X", command=self.cut_text)
        self.edit_menu.add_command(label="Copy", accelerator="Ctrl+C", command=self.copy_text)
        self.edit_menu.add_command(label="Paste", accelerator="Ctrl+V", command=self.paste_text)
        self.edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self.select_all)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.root.config(menu=self.menu_bar)

        # Keyboard shortcuts
        self.text_area.bind("<Control-n>", lambda event: self.new_file())
        self.text_area.bind("<Control-o>", lambda event: self.open_file())
        self.text_area.bind("<Control-s>", lambda event: self.save_file())
        self.text_area.bind("<Control-a>", lambda event: self.select_all())

        # Variables
        self.current_file = None
        self.text_area.focus_set()

        # Track changes
        self.text_area.edit_modified(False)
        self.text_area.bind("<<Modified>>", self.on_text_modified)

        # Initialize line numbers
        self.update_line_numbers()

    def on_text_modified(self, event=None):
        """Track changes in the text area."""
        if self.text_area.edit_modified():
            self.root.title("Text Editor - Dark Theme *")
            self.text_area.edit_modified(False)

    def update_line_numbers(self, event=None):
        """Update line numbers in the Canvas."""
        self.line_numbers.delete("all")
        i = self.text_area.index("@0,0")
        while True:
            dline = self.text_area.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            line_num = i.split(".")[0]
            self.line_numbers.create_text(
                40, y,
                anchor="ne",
                text=line_num,
                fill=self.line_number_fg,  # Use fill for text color
                font=self.font
            )
            i = self.text_area.index(f"{i}+1line")

    def new_file(self):
        """Create a new file."""
        if self.check_for_changes():
            self.text_area.delete(1.0, tk.END)
            self.current_file = None
            self.root.title("Text Editor - Dark Theme - New File")
            self.update_line_numbers()

    def open_file(self):
        """Open an existing file."""
        if self.check_for_changes():
            file_path = filedialog.askopenfilename(
                filetypes=[("SBR Files", "*.sm"), ("All Files", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, "r") as file:
                        content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)
                    self.current_file = file_path
                    self.root.title(f"Text Editor - Dark Theme - {os.path.basename(file_path)}")
                    self.update_line_numbers()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open the file:\n{str(e)}")

    def save_file(self):
        """Save the current file."""
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, "w") as file:
                    file.write(content)
                #messagebox.showinfo("Saved", "File saved successfully")
                self.root.title(f"Text Editor - Dark Theme - {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save the file:\n{str(e)}")
        else:
            self.save_as_file()

    def save_as_file(self):
        """Save the file with a new name."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".sm",
            filetypes=[("Text Files", "*.sm"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, "w") as file:
                    file.write(content)
                self.current_file = file_path
                self.root.title(f"Text Editor - Dark Theme - {os.path.basename(file_path)}")
                messagebox.showinfo("Saved", "File saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save the file:\n{str(e)}")

    def check_for_changes(self):
        """Check if there are unsaved changes and prompt the user."""
        if self.text_area.edit_modified():
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Do you want to save changes before proceeding?"
            )
            if response is None:  # User clicked Cancel
                return False
            elif response:  # User clicked Yes
                self.save_file()
        return True

    def exit_app(self):
        """Exit the application."""
        if self.check_for_changes():
            if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
                self.root.destroy()

    def cut_text(self):
        """Cut selected text."""
        self.text_area.event_generate("<<Cut>>")

    def copy_text(self):
        """Copy selected text."""
        self.text_area.event_generate("<<Copy>>")

    def paste_text(self):
        """Paste text from clipboard."""
        self.text_area.event_generate("<<Paste>>")

    def select_all(self):
        """Select all text."""
        self.text_area.tag_add("sel", "1.0", tk.END)

def main():
    root = tk.Tk()
    app = TextEditor(root)
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()


if __name__ == "__main__": main()
