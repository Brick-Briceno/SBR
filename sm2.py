from tkinter import Tk, filedialog
from errors import SBR_ERROR
from pathlib import Path
from nt import error
import webview
import os



class MusicEditorAPI:
    def __init__(self):
        self.current_file = None
        self.project_dir = Path(__file__).parent
        self.window = None

    def execute_script(self, code: str):
        from interpreter import sbr_line
        try:
            for n_line, line in enumerate(code.splitlines(), start=1):
                sbr_line(line)
        except SBR_ERROR as bad:
            return {"message": f"Error in line {n_line}: {bad}"}

        return {"message": "sussefull"}


    def save_script(self, code):
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        filepath = filedialog.asksaveasfilename(
            title="Guardar Script",
            defaultextension=".sm",
            filetypes=[
                ("Sm Scripts", "*.sm"),
                ("Todos los archivos", "*.*")
            ],
            initialdir=self.project_dir
        )

        root.destroy()
        
        if not filepath:
            return {'success': False, 'message': 'Guardado cancelado'}

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code)
        
        self.current_file = filepath
        return {
            'success': True,
            'path': os.path.basename(filepath),
            'message': 'Script guardado'
        }
    
    def load_script(self):
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        filepath = filedialog.askopenfilename(
            title="Cargar Script",
            filetypes=[
                ("Sm Scripts", "*.sm"),
                ("Todos los archivos", "*.*")
            ],
            initialdir=self.project_dir
        )
        
        root.destroy()
        
        if not filepath:
            return {'success': False, 'message': 'Carga cancelada'}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()

        self.current_file = filepath
        return {
            'success': True,
            'code': code,
            'path': os.path.basename(filepath)
        }
    
    def export_midi(self):
        print("notes")
    
    def toggle_fullscreen(self):
        if self.window:
            self.window.toggle_fullscreen()


def main():
    api = MusicEditorAPI()
    html_path = Path(__file__).parent / "src/sm2.html"
    window = webview.create_window(
        title="Welcome to Simmetric melody 2 ",
        url=str(html_path),
        js_api=api,
        width=1400,
        height=800,
        resizable=True,
        #fullscreen=True,
        min_size=(1000, 600),
    )
    api.window = window
    webview.start()
