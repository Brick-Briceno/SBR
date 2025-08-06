"""
Symmetry Melody v1.0
by @Brick_Briceno 2023
"""
#Librerias uwu
from tkinter import messagebox, filedialog as FileDialog
from sys import argv as desde_sys
from tkinter import ttk
import tkinter as tk

from webbrowser import open as open_link
from threading import Thread
from pygame import mixer
import midiutil
import random
import psutil
import time

#Modulos SBR
import commands
import variables


titulo_ventana = "Symmetry Melody v1.0 by @Brick_briceno"

def notificacion(titulo, msj):
    root_msj = tk.Tk()
    root_msj.withdraw()
    messagebox.showinfo(msj, titulo)


"Sistema de Guardado"

def hex_a_bi(hexad):
    return "{0:02240b}".format(int(hexad, 16))

def bi_a_hex(bi):
    return "{0:0>1X}".format(int(bi, 2))

def list_a_str_bi(lista):
    salida = ""
    for x in lista:
        salida += str(x)
    return salida

def str_bi_a_list(bi):
    salida = []
    for x in bi:
        salida.append(int(x))
    return salida

def actualizar_botones():
    for x in range(len(Piano_Roll)):
        if not Piano_Roll[x]:    
            if not ((34 - (x // 64))%7):
                buttons_c1[x].configure(bg=color_tonica)
            else:
                buttons_c1[x].configure(bg="black")
        else:
            buttons_c1[x].configure(bg=color_boton)

def abrir(externo):
    if externo == False:
        global ruta
        ruta = FileDialog.askopenfilename(
        initialdir='.', 
        filetypes=(("Simmetry Melody Proyect", "*.smp"),),
        title="Abrir un Proyecto :D")
    global tempo
    global tono_de_escala
    global tipo_escala_n
    global octava_a_anadir
    global Piano_Roll
    cosas = ["", "",
             "", "", ""]
    archivo = open(ruta)
    n = 0
    for x in archivo.read():
        if x != ",":
            cosas[n] += x
        else:
            n += 1
    archivo.close()
    tempo = int(cosas[0])
    tono_de_escala = int(cosas[1])
    tipo_escala_n = int(cosas[2])
    octava_a_anadir = int(cosas[3])
    actualizar_barra(None)
    Piano_Roll = str_bi_a_list(hex_a_bi(cosas[4]))
    root.title(titulo_ventana + " " + ruta)
    actualizar_botones()


def guardar():
    if ruta != None:
        fichero = open(ruta, 'w+')
        fichero.write(str(tempo) + "," + str(tono_de_escala)
                      + "," + str(tipo_escala_n) + "," +
                      str(octava_a_anadir)  + "," +
                      bi_a_hex(list_a_str_bi(Piano_Roll)))
        fichero.close()
    else:
        guardar_como()

def guardar_como():
    global ruta
    fichero = FileDialog.asksaveasfile(title="Guardar Proyecto", 
        mode="w", defaultextension=".smp")
    if fichero == None:
        return "sexo"
    ruta = fichero.name
    fichero = open(ruta, 'w+')
    fichero.write(str(tempo) + "," + str(tono_de_escala)
                      + "," + str(tipo_escala_n) + "," +
                      str(octava_a_anadir)  + "," +
                      bi_a_hex(list_a_str_bi(Piano_Roll)))
    fichero.close()
    root.title(titulo_ventana + " " + ruta)

def mid_export():
    fichero = FileDialog.asksaveasfile(title="Exportar .Mid", 
        mode="w", defaultextension=".mid")
    if fichero == None:
        return

    time = 0# Tiempo inicial en ticks
    mf = midiutil.MIDIFile(1)   # Un solo track
    mf.addTempo(0, time, tempo)
    for corchea in range(64):
        for tono in range(35):
            if Piano_Roll[posicion_lista(tono, corchea)]:
                octava_anadir = 2
                grado = tono + 1
                while grado > 7:
                    octava_anadir += 1
                    grado -= 7
                else:
                    note = ((octava_anadir)*12)+escalas_list[tipo_escala_n][grado-1]+tono_de_escala-13+(7*4)
                #print(0, 0, note, corchea, 1, 100)
                mf.addNote(0, 0, note, corchea/4, .25, 100)

    # Exportación del archivo MIDI
    with open(fichero.name, "wb") as output_file:
        mf.writeFile(output_file)


"Cargar samples en la ram"


"""Parte de generación de Ritmos"""

#Configuración de Sonido

#paramrtros aplican a mas partes del programa a parte de esta uwu
frecuencia_muestreo = 44100
buffer = 1024

mixer.pre_init(frecuencia_muestreo, -16, 2, buffer)
mixer.init()

sample1 = mixer.Sound("inst/Kick.wav")
sample2 = mixer.Sound("inst/Clap.wav")
sample3 = mixer.Sound("inst/Snare.wav")
sample4 = mixer.Sound("inst/Hat.wav")

claqueta_fuerte = mixer.Sound("sounds/golpe_fuerte.wav")
claqueta_suave = mixer.Sound("sounds/golpe_suave.wav")

#Sonidos de inicio y final:
inicio = mixer.Sound("sounds/inicio.wav")
final = mixer.Sound("sounds/final.wav")

ritmos = [sample1, sample2, sample3, sample4]


"""Codigo de editor de melodias"""

Piano_Roll = [0]*64*35
color_boton = "#00CA65"
color_boton_pulso = "#FC19A5"
color_tonica = "#1A1A1A"

def posicion_lista(tono, corchea): #esto calcula el indice de la lista mediante sus 2 argumetos
    return ((34-tono)*64)+(corchea)

def tono_y_corchea_desde_indice(indice):
    corchea = indice % 64 + 1
    tono = 35 - (indice // 64)
    return tono, corchea

#lista con los 64*35 botones de las partituras
buttons_c1 = [0 for x in range(64*35)]

def cambiar_color_e_indice(indice):
    if Piano_Roll[indice]:
        Piano_Roll[indice] = 0
        if not ((34 - (indice // 64))%7):
            buttons_c1[indice].configure(bg=color_tonica)
        else:
            buttons_c1[indice].configure(bg="black")
    else:
        Piano_Roll[indice] = 1
        buttons_c1[indice].configure(bg=color_boton)
        Thread(target=tocar_nota, args=(tipo_instrumento,
                tono_y_corchea_desde_indice(indice)[0]-1+7*(octava_a_anadir-2))).start()


def pulso_boton(indice, color):#si el color NO es None, será negro
    buttons_c1[indice].configure(bg=color_boton_pulso)
    time.sleep(55/tempo)
    if not color or Piano_Roll[indice]:
        buttons_c1[indice].configure(bg=color_boton)
    elif not ((34 - (indice // 64))%7):
            buttons_c1[indice].configure(bg=color_tonica)
    else:
        buttons_c1[indice].configure(bg="black")


def harmonia_negativa_diatonica():
   global Piano_Roll
   salida = [0 for x in range(35*64)]
   for x in range(35*64):
       if Piano_Roll[x]:
           corchea = tono_y_corchea_desde_indice(x)[1]
           tono = tono_y_corchea_desde_indice(x)[0]
           nuevo_tono = tono-(tono*2)+28+(7*3)
           salida[posicion_lista(nuevo_tono+5, corchea-1)] = 1
   Piano_Roll = salida
   actualizar_botones()

def subir_bajar(accion):
   global Piano_Roll
   salida = [0 for x in range(35*64)]
   for x in range(35*64):
       if Piano_Roll[x]:
           corchea = tono_y_corchea_desde_indice(x)[1]
           tono = tono_y_corchea_desde_indice(x)[0]
           nuevo_tono = tono+accion
           salida[posicion_lista(nuevo_tono+1, corchea-1)] = 1
   Piano_Roll = salida
   actualizar_botones()


"""Reproductor de Melodias y Ritmos"""

def teclado(grado):#la variable grado2 es para que al cambiar la octava
    grado2 = grado-1+(7*octava_a_anadir)#no cambie tambien donde brillan los botones
    Thread(target=tocar_nota, args=(tipo_instrumento, grado2)).start()
    Thread(target=pulso_boton, args=(posicion_lista(grado+13, 0), True)).start()


"""Instrumentos"""

instrumentos = []

nombre_de_instrumentos = [inst.name for inst in variables.vars_instruments.values()]

for i in range(len(nombre_de_instrumentos)):
    try:
        if "#" in nombre_de_instrumentos[i]:
            nombre_de_instrumentos.pop(i)
            instrumentos.pop(i)
    except:
        break

def tocar_nota(instrumento, nota):
    ...

def cambiar_instrumento(inst):
    global tipo_instrumento
    tipo_instrumento = inst

tempo = 128
activador = False
tipo_escala_n = 0
tono_de_escala = 5
octava_a_anadir = 2
tipo_instrumento = 0
#volumen maximo 1 y minimmo 0, 50% = 0.5
volumen = 1

def nuevo_p():
    global tipo_escala_n
    global tono_de_escala
    global octava_a_anadir
    global Piano_Roll
    global ruta
    Piano_Roll = [0 for x in range(35*64)]
    tipo_escala_n = 0
    tono_de_escala = 5
    octava_a_anadir = 4
    ruta = None
    actualizar_barra(None)
    actualizar_botones()
    root.title(titulo_ventana)


def reproductor():
    corchea = 0
    global activador
    activador = True
    while activador:
        #Render audio
        if not corchea:
            sbr_tones_code = "M"
            sbr_rhythm_code = "B"
            for corchea in range(64):
                sbr_tones_code += ",{"
                bit = False
                for tono in range(35):
                    if Piano_Roll[posicion_lista(tono, corchea)]:
                        bit = True
                        sbr_tones_code += f",{tono}"
                sbr_tones_code += "}"
                sbr_rhythm_code += "1" if bit else "0"
        commands.play(["Struct{V0;"+""+";Sm{"+sbr_rhythm_code+";"+sbr_tones_code+"}}"])

        #Melodia
        for tono in range(35):
            if Piano_Roll[posicion_lista(tono, corchea)]:
                #pulso del boton
                Thread(target=pulso_boton, args=(posicion_lista(tono, corchea), None)).start()

        #Claqueta
        if claqueta_activada and (corchea in [x*4 for x in range(16)]):
            claqueta_suave.play()
        elif claqueta_activada and (corchea in [x*16 for x in range(4)]):
            claqueta_fuerte.play()

        corchea += 1
        if corchea == 64:
            corchea = 0
        time.sleep(15/tempo)


def play_pause():
    global activador
    if activador:
        activador = False
        boton_play_pause.configure(bg="black", fg="white")
    else:
        re = Thread(target=reproductor)
        re.start()
        boton_play_pause.configure(bg="white", fg="black")

claqueta_activada = False
def claqueta():
    global claqueta_activada
    claqueta_activada = not claqueta_activada

#Funciones de Botones

def redondear_tempo():
    global Tempo
    tempo = round(tempo)
    #TempoD.set(Tempo)

LastPulseTime = 0
bpm_media = []
def tempo_calc():
    global LastPulseTime
    global tempo
    global bpm_media
    CurrentTime = time.time()
    if LastPulseTime == 0:
          LastPulseTime = CurrentTime
    #Aquí se calcula el valor BPM
    bpm = 60/(CurrentTime-LastPulseTime)
    bpm_media.append(bpm)
    LastPulseTime = CurrentTime
    tempo = sum(bpm_media)/len(bpm_media)
    tempo = round(tempo)
    #print(bpm_media)
    #print(tempo)
    actualizar_barra(None)
    if bpm < 45:
        LastPulseTime = 0
        bpm_media = []

#Menú bar

mensaje_brick = ""

mensajes_ramdon_brick = ("Con la tecla ¨T¨ puedes marcar el tempo :)",
                         "Con las teclas de numeros tienes samples de ritmos ;)",
                         "Una vez me hice la paja con gasolina O:",
                         "No es necesario que uses muchas notas en una canción, con 5 o hasta 3 está bien uwu",
                         "Con la tecla ¨Y¨ activas una claqueta para llevar el tempo 0w0",
                         "tienes un teclado con las teclas: ¨z¨ hasta ¨-¨",
                         "No pienses en tu ex amigo! enfocate en la musica!!! B)",
                         "Los momentos de inspiración llegan cuando estás en el baño, Brick Briceño - 2020",
                         "Puedes usar tecnicas como la harmonia negativa o cambiar el ritmo de una melodia ;D",
                         "Buscame en redes como @Brick_briceno ;)",
                         "Aveces un pequeño detalle le da vida a Toda la canción...",
                         "La musica nos lleva a otros mundos que solo están en muestra imaginacíon",
                         "las notas agudas se suelen usar para imprecionar, dependiendo del caso claro")

mostrar_mensaje = True
def random_brick():
    n = len(mensajes_ramdon_brick)-1
    while mostrar_mensaje:
        time.sleep(random.randint(20, 130))
        n_anterior = n
        while n == n_anterior:
            n = random.randint(0, len(mensajes_ramdon_brick)-1)
        n_anterior = n

        global mensaje_brick
        mensaje_brick = "   -   Tip " + str(n+1) + ": " + mensajes_ramdon_brick[n]
        actualizar_barra(None)
        time.sleep(random.randint(10, 15))
        mensaje_brick = ""
        actualizar_barra(None)

var_cpu = True
cpu_str = ""
def cpu():
    global cpu_str
    sepd = ""
    while var_cpu:
        cpu_porc = psutil.cpu_percent()
        if cpu_porc < 10:
            sepd = "  "
        else:
            sepd = ""
        cpu_str = "CPU: " + str(cpu_porc) + "% " + sepd + "▄"*int(cpu_porc/10) + "_"*(10-int(cpu_porc/10))
        actualizar_barra(None)
        time.sleep(1)


def cafe():
    open_link("https://paypal.me/BrickUwu")
    """Esto me ayuda a seguir creando
    Sofware Libre para Todos :D
    """

"""Interfaz"""

root = tk.Tk()
root.geometry("1024x560")# Establecer el tamaño de la ventana
root.title(titulo_ventana)
root.iconbitmap("sbr.ico")
root.resizable(0, 0)

# Crear un ttk.Style para personalizar la apariencia de los widgets
style = ttk.Style()
style.theme_use("alt")

"""Ventana 1: editor de melodias"""

frame_melodia = tk.Frame(root, bg="black")
frame_melodia.pack(expand=True, fill="both")

corchea_s = []
for x in range(64+16):
    if not x%5 == 0:
        corchea_s.append(x)

tono_r = [x for x in range(35)]
tono_r.reverse()
separador = 0
for tono in range(35):
    for corchea in range(64):
        button_c1 = tk.Button(frame_melodia, command=lambda arg=posicion_lista(tono, corchea): cambiar_color_e_indice(arg), width=1, height=1, bg="black", font=("Helvetica", 5))
        if not (tono%7):
            button_c1.configure(bg=color_tonica)

        button_c1.grid(row=tono_r[tono], column=corchea_s[corchea], padx=0, pady=0)
        buttons_c1[posicion_lista(tono, corchea)] = button_c1

for x in range(64+16):
    if not x%5 == 0:
        corchea_s.append(x)

for tono in range(35):
    for corchea in range(64+16):
        if corchea%5 == 0 and corchea:
            separador_label = tk.Label(frame_melodia, text="", width=1, height=1, bg=color_tonica, font=("Micro", 1))
            separador_label.grid(row=tono_r[tono], column=corchea)

del tono_r

#Controles Melodia
frame_controles_melodia = tk.Frame(root, bg="snow")
frame_controles_melodia.place(x=5, y=430)

def subir_bajar_tonalidad(subir):
    global tono_de_escala
    if subir:
        tono_de_escala += 1
        if tono_de_escala > 11:
            tono_de_escala = 0
    else:
        tono_de_escala -= 1
        if tono_de_escala < 0:
            tono_de_escala = 11

    actualizar_barra(None)


def subir_bajar_octava(subir):
    global octava_a_anadir
    if subir:
        octava_a_anadir += 1
    else:
        octava_a_anadir -= 1

    actualizar_barra(None)


boton_play_pause = tk.Button(frame_controles_melodia, text="Play", bg="black", fg="white", command=play_pause, font=("Helvetica", 18))
boton_play_pause.grid(row=0, column=0)

boton_bajar_tonalidad = tk.Button(frame_controles_melodia, text="<T", bg="black", fg="white", command=lambda arg= 0: subir_bajar_tonalidad(arg), font=("Helvetica", 18))
boton_bajar_tonalidad.grid(row=0, column=2)

boton_suibir_tonalidad = tk.Button(frame_controles_melodia, text="T>", bg="black", fg="white", command=lambda arg= 1: subir_bajar_tonalidad(arg), font=("Helvetica", 18))
boton_suibir_tonalidad.grid(row=0, column=1)

boton_bajar_octava = tk.Button(frame_controles_melodia, text="<O", bg="black", fg="white", command=lambda arg= 0: subir_bajar_octava(arg), font=("Helvetica", 18))
boton_bajar_octava.grid(row=0, column=3)

boton_suibir_octava = tk.Button(frame_controles_melodia, text="O>", bg="black", fg="white", command=lambda arg= 1: subir_bajar_octava(arg), font=("Helvetica", 18))
boton_suibir_octava.grid(row=0, column=4)

boton_harmonia_negativa_diatonica = tk.Button(frame_controles_melodia, text="Hrm N", bg="#170017", fg="white", command=harmonia_negativa_diatonica, font=("Helvetica", 18))
boton_harmonia_negativa_diatonica.grid(row=0, column=5)

boton_bajar = tk.Button(frame_controles_melodia, text="<", bg="#170017", fg="white", command=lambda arg= 32: subir_bajar(arg), font=("Helvetica", 18))
boton_bajar.grid(row=0, column=6)
 
boton_subir = tk.Button(frame_controles_melodia, text=">", bg="#170017", fg="white", command=lambda arg= -1: subir_bajar(arg), font=("Helvetica", 18))
boton_subir.grid(row=0, column=7)

#Menú bar
menu_bar = tk.Menu(root)

# Crear el menú "Archivo"
archivo_menu = tk.Menu(menu_bar, tearoff=0)
archivo_menu.add_command(label="Nuevo", command=nuevo_p)
archivo_menu.add_command(label="Abrir", command=lambda arg=False: abrir(arg))
archivo_menu.add_command(label="Guardar", command=guardar)
archivo_menu.add_command(label="Guardar como...", command=guardar_como)
archivo_menu.add_command(label="Exportar .mid", command=mid_export)
archivo_menu.add_separator()
archivo_menu.add_command(label="Salir", command=root.quit)
archivo_menu.config(bg="black", fg="snow")

menu_bar.add_cascade(label="Archivo", menu=archivo_menu)

#Escalas Menú
escalas_menu = tk.Menu(menu_bar, tearoff=0)

"""Barra de Estado"""

nombres_escalas = ["Mayor", "Menor", "Menor melodico",
                    "Lidio", "Mixolidio", "Dorico", "Frigio",
                    "Locrio", "Arabe"]

def actualizar_barra(n_esc):
    global tipo_escala_n
    if n_esc != None:
        tipo_escala_n = n_esc
    statusbar_label.configure(text="Tempo: " +
                              str(tempo) + "    -   Ecala: " +
                              ["C", "C#", "D", "D#", "E", "F",
                               "F#", "G", "G#", "A", "A#", "B"][tono_de_escala]+
                               " " +
                               nombres_escalas[tipo_escala_n] + mensaje_brick +
                               "    -   " + cpu_str)

statusbar = tk.Frame(root, bg="black", width=400, height=20)
statusbar.pack(fill=tk.X)
statusbar_label = tk.Label(statusbar, text="", bg="#262626",
                    fg="white", width=400, anchor=tk.W, font=("Helvetica", 12))
statusbar_label.pack(fill=tk.X)
actualizar_barra(None)

for x in range(len(nombres_escalas)):
    escalas_menu.add_command(label=nombres_escalas[x], command=lambda arg=x: actualizar_barra(arg))

escalas_menu.config(bg="black", fg="snow")

menu_bar.add_cascade(label="Escalas", menu=escalas_menu)

#Instrumentos Menú

instrumentos_menu = tk.Menu(menu_bar, tearoff=0)

for x in range(len(nombre_de_instrumentos)):
    instrumentos_menu.add_command(label=nombre_de_instrumentos[x], command=lambda arg=x: cambiar_instrumento(arg))

instrumentos_menu.config(bg="black", fg="snow")
menu_bar.add_cascade(label="Instrumentos :)", menu=instrumentos_menu)

ayuda_menu = tk.Menu(menu_bar, tearoff=0)
ayuda_menu.add_command(label="Ayuda", command=lambda arg1="Hola!!!", arg2="Pronto versión 2": notificacion(arg1, arg2))
ayuda_menu.add_command(label="Dame un Cafe <3", command=cafe)
ayuda_menu.config(bg="black", fg="snow")

menu_bar.add_cascade(label="Ayuda", menu=ayuda_menu)

#Asignar el menú bar a la ventana
root.config(menu=menu_bar)


"""Atajos de Teclado"""

#controles basicos
root.bind("<space>", lambda event: play_pause())
root.bind("t", lambda event: tempo_calc())
root.bind("T", lambda event: tempo_calc())
root.bind("y", lambda event: claqueta())
root.bind("}", lambda event: subir_bajar_tonalidad(1))
root.bind("{", lambda event: subir_bajar_tonalidad(0))
root.bind("<Control-s>", lambda event: guardar())
root.bind("<Control-S>", lambda event: guardar())
root.bind("<Control-n>", lambda event: nuevo_p())
root.bind("<Control-N>", lambda event: nuevo_p())
root.bind("<Control-o>", lambda event: abrir(False))
root.bind("<Control-O>", lambda event: abrir(False))
root.bind("<Control-m>", lambda event: mid_export())
root.bind("<Control-M>", lambda event: mid_export())
root.bind("n", lambda event: harmonia_negativa_diatonica())
root.bind("N", lambda event: harmonia_negativa_diatonica())


#Ritmos samples

root.bind("1", lambda event: sample1.play())
root.bind("2", lambda event: sample2.play())
root.bind("3", lambda event: sample3.play())
root.bind("4", lambda event: sample4.play())


#teclado
root.bind("Z", lambda event: teclado(1))
root.bind("z", lambda event: teclado(1))
root.bind("X", lambda event: teclado(2))
root.bind("x", lambda event: teclado(2))
root.bind("C", lambda event: teclado(3))
root.bind("c", lambda event: teclado(3))
root.bind("V", lambda event: teclado(4))
root.bind("v", lambda event: teclado(4))
root.bind("B", lambda event: teclado(5))
root.bind("b", lambda event: teclado(5))
root.bind("N", lambda event: teclado(6))
root.bind("n", lambda event: teclado(6))
root.bind("M", lambda event: teclado(7))
root.bind("m", lambda event: teclado(7))
root.bind(",", lambda event: teclado(8))
root.bind(".", lambda event: teclado(9))
root.bind("-", lambda event: teclado(10))

#root.state('zoomed')

#si desde windows abres el proyecto
#con el programa sale esta ruta
try:
    global ruta
    ruta = desde_sys[1]
    abrir(True)
except IndexError:
    ruta = None

msj_br = Thread(target=random_brick)
msj_br.start()

my_thread = Thread(target=cpu)
my_thread.start()

inicio.play()
root.mainloop()
final.play()
activador = False
mostrar_mensaje = False
var_cpu = False
