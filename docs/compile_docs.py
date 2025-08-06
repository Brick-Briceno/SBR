from playwright.sync_api import sync_playwright
import markdown
import os
import io


with open("table.css", "r", encoding="utf-8") as file:
    CSS = file.read()

__P = sync_playwright().start()
BROWSER = __P.chromium.launch()

def __del__():
    #lo siguiente es para liberar recursos
    BROWSER.close()
    __P.stop()



with open("table.css", "r", encoding="utf-8") as file:
    CSS = file.read()

title = "Documentación de la API"

md = ""

html_code = markdown.markdown(
    md, extensions=[
        'tables',        # Soporte para tablas
        'fenced_code',   # Bloques de código
        'md_in_html'     # Mejor soporte HTML
    ])

html_full = f"""<!doctype html>
<html lang="es">
    <head>
        <title>{title}</title>
        <style>{CSS}</style>
    </head>
    <body>
        <h1>{title}</h1>
        {html_code}
    </body>
</html>
"""#.replace(" "*2, "").replace("\n", "")

if ... == ".pdf":
    page = BROWSER.new_page()
    page.set_content(html_full)
    page.pdf()
