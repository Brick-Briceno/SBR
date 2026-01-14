"""
Symmetry Melody Api v2.1
@Brick_briceno 2023

"""

TEXT_FILE = "src/words_es.txt"

class Smetric():
    def __init__(self):
        texto_letra = ""
        data_base = []

    def act_data_base(self):
        try:
            a = open(TEXT_FILE, encoding="utf-8").read() + "\n"
        except UnicodeDecodeError:
            a = open(TEXT_FILE, encoding="ansi").read() + "\n"
        self.data_base = a.split()
    
    def eliminar_numeros(txt):
        txt_final = ""
        for x in txt:
            if not x in [str(x) for x in range(10)]: txt_final += x
        return txt_final

    def simplificar_sonido(palabra):
        palabra = palabra.strip()
        palabra = palabra.lower()
        if palabra[-1:] == "y": palabra = palabra[:-1] + "i"
        palabra = palabra.replace(" y ", " i ")
        palabra = palabra.replace("y ", "i ")
        palabra = palabra.replace("á", "a")
        palabra = palabra.replace("é", "e")
        palabra = palabra.replace("í", "i")
        palabra = palabra.replace("ó", "o")
        palabra = palabra.replace("ú", "u")
        palabra = palabra.replace("h", "")
        palabra = palabra.replace("ll", "y")
        palabra = palabra.replace("gue", "ge")
        palabra = palabra.replace("gi", "ji")
        palabra = palabra.replace("ca", "ka")
        palabra = palabra.replace("co", "ko")
        palabra = palabra.replace("cu", "ku")
        palabra = palabra.replace("cc", "kc")
        palabra = palabra.replace("c", "s")
        palabra = palabra.replace("z", "s")
        palabra = palabra.replace("ex", "eks")
        palabra = palabra.replace("x", "s")
        palabra = palabra.replace("qu", "k")
        return palabra


    def separar_silabas(self, palabra):
        palabra = palabra.strip()
        if not len(palabra): return [""]
        if 1 == len(palabra): return [palabra]
        vocales = list("aeiouáéíóúAEIOUÁÉÍÓÚ")
        son_u = ["ch", "sh", "ll", "qu", "gr",
                 "br", "cr", "dr", "fr", "kr",
                 "pr", "rr", "tr", "bl", "cl",
                 "fl", "pl", "tl", "gl", "ns"]
        son_s = ['♦', '♣', '♠', '◙', '♀', '╝',
                 '☼', '►', '◄', '◙', '¶', '§',
                 '▬', '↑', '↓', '→', '←', '∟',
                 '↔', '◘', '¶', '╚', '▲', '▼']

        for x in range(len(son_u)):
            palabra = palabra.replace(son_u[x], son_s[x])

        silabas = []
        silaba_actual = ""
        no_vocal = False#true si no hay vocal
        for x in palabra:
            if x in vocales:
                no_vocal = True
        if not no_vocal:
            return [palabra]

        silabas = []
        silaba_actual = ""
        palabra += ">>"
        for x in range(len(palabra)):
            if silaba_actual == "":
                silaba_actual += palabra[x]
            elif palabra[x] in vocales:
                silaba_actual += palabra[x]
            elif x != len(palabra)-1:
                if not palabra[x] in vocales and not palabra[x+1] in vocales:
                    silaba_actual += palabra[x]
                    silabas.append(silaba_actual)
                    silaba_actual = ""
                else:#es consonante
                    silabas.append(silaba_actual)
                    silaba_actual = ""
                    silaba_actual += palabra[x]

        for x in range(len(son_u)):
                for y in range(len(silabas)):
                    silabas[y] = silabas[y].replace(son_s[x], son_u[x])
                    silabas[y] = silabas[y].replace(">", "")
        silabas2 = []
        
        for x in silabas:
            silabas2.append(x.strip())
        silabas = []
        for x in silabas2:
            if x != "":
                silabas.append(x)

        return silabas

    def the2vocales(self, palabra):
        #palabra = Letra.simplificar_sonido(palabra)
        hola = ""
        for x in palabra[::-1]:
            if x in tuple("aeiou" + "áéíúó"): hola += x
        return hola[::-1]

    def busc_rima_cons(self, palabra):
        lista_de_palabras = []
        palabra = palabra.replace(" ", "")
        palabra = self.simplificar_sonido(palabra)
        if not len(self.separar_silabas(self.simplificar_sonido(palabra))) < 2:
            sila = self.separar_silabas(self.simplificar_sonido(palabra))[-2][1::]
            sila += self.separar_silabas(self.simplificar_sonido(palabra))[-1]
        else: return []


        for x in self.data_base:
            if not len(self.separar_silabas(self.simplificar_sonido(x))) < 2:
                sila2 = self.separar_silabas(self.simplificar_sonido(x))[-2][1::]
                sila2 += self.separar_silabas(self.simplificar_sonido(x))[-1]

                if sila == sila2:
                    print(x)
                    lista_de_palabras.append(x)

        return lista_de_palabras

    def busc_rima_asonante(self, palabra):
        vocales = self.the2vocales(self.simplificar_sonido(palabra))
        for x in self.data_base:
            if vocales == self.the2vocales(x):
                print(x)

    def calcular_n_silabas(self, letra_c):
        lista_lineas = []
        texto_final = ""
        for x in letra_c.splitlines():
            if x != "": lista_lineas.append(x)
        for x in lista_lineas:
            texto_final += x + " " + str(len(self.separar_silabas(
                self.simplificar_sonido(x).replace(" ", "").replace(",", "")))) + "\n"

        return texto_final
