"""
El lenguaje SBR proporciona
herramientras super creativas
a los musicos para hacer ritmos y a partir
de este hacer melodias memorables

@Brick_briceno 2023
"""

#Para usarlo solo meta el texto en SBR.compilador("codigo SBR") :D

"""
Deseo de todo corazón que se puedan
sacar cosas buenas con esta herramienta
deseo que las personas se diviertan
experimentando con el o que les ayude a hacer mejor musica
"""

import random

class SBR:
    "variables"
    datos = "0123468"
    paramts = ",1234567890"
    gen = "BEC?"
    efects = "LXSD*QRIP}{"
    math = "+-"
    salidas = []
    vars_default = {"contra": "B0010", "son": "B1001001000101000",
                    "bossa": "B1001001000100100", "dembow":"B10010010"}
    vars_temp = {}
    
    propiedades = {"tempo": 128}

    "funciones complementarias"

    def numeros(txt):
        salida = ""
        for x in txt:
            if x in "1234567890": salida += x
        return int(salida)

    def asignar_canal(ritmo, canal):
        if not canal: return
        elif len(SBR.salidas) >= canal: SBR.salidas[canal-1] = ritmo
        else: SBR.salidas = SBR.salidas + [""]*(canal-1-len(SBR.salidas))+[ritmo]

    def limpiar(code):
        new = ""
        for x in code:
            if x in SBR.gen+SBR.efects+SBR.datos+SBR.paramts+SBR.math+")(": new += x
        return new
    
    "funciones de compilación"

    def compilador(code):
        code = SBR.comentarios(code)#quita comentarios menos los saltos de linea
        if type(code) == tuple: return code
        SBR.salidas.clear() #resetear salidas
        SBR.vars_temp = SBR.vars_default.copy()
        linea_var = 0 #ultima linea donde se hacia algo relacionado a variables
        for n_line, line in enumerate(code.split("\n"), start=1):
            if not line.isascii(): return SBR.Error(18, n_line)
            #Si asigna una variable
            elif "=" in line:
                #Errores de asignación de variables
                caja = line.split("=")
                caja = caja[0].strip(), caja[1].strip()
                if caja[0] == "": return SBR.Error(4, n_line)#asignando a la nada
                elif caja[1] == "": return SBR.Error(3, n_line)#asignando nada a la variable
                elif caja[0] in "$\".:"+SBR.datos+SBR.paramts+ \
                SBR.gen+SBR.efects+SBR.math: return SBR.Error(5, n_line)#nombre invalido

                #Asignar variable
                ritmo = SBR.pre_magia(caja[1])
                if type(ritmo) == int: return SBR.Error(ritmo, n_line)
                SBR.vars_temp[caja[0]] = ritmo

            #Si hay algún comando
            elif ":" in line:
                #quitar espacios y vergas locas
                linea_pasada = ""
                caja = line.split(":")
                if caja[0] == "": return SBR.Error(14, n_line)
                letra = caja[0].strip()[0].upper()
                caja[0], caja[1] = caja[0].strip()[1:].strip(), caja[1].strip()

                #agregar salida
                if letra == "S":
                    #si la salida está vacia
                    if caja[1] == "": return SBR.Error(12, n_line)

                    #si la variable no existe
                    elif not caja[1] in SBR.vars_temp: return SBR.Error(2, n_line)

                    #Si la salida no tiene nungún canal asignado
                    elif caja[0] == "": return "OK", [SBR.pre_magia(caja[1])]

                    #canal es numero?
                    elif caja[0].isnumeric(): SBR.asignar_canal(SBR.vars_temp[caja[1]], SBR.numeros(caja[0]))

                    else: SBR.Error(16, n_line)

                #Asignar tempo
                elif letra == "T":
                    try: SBR.propiedades["tempo"] = int(caja[1])
                    except ValueError: return SBR.Error(13, n_line)

                #Comando de letra no registrada
                else: return SBR.Error(15, n_line)
        
        return "OK", SBR.salidas #Fin del compilador, retorna "OK" en la compilación 

    def pre_magia(code):
        #Esta función procesa las variables y envia una señal a magia
        #Ordenar las variables por longitud de texto (mayores primero)
        lista_keys = sorted(list(SBR.vars_temp), key=len, reverse=True)

        #Iterar variables y remplazar fracmentos de texto
        for variable in lista_keys: code = code.replace(variable, SBR.vars_temp[variable])

        #Compilar SBR
        ritmo = SBR.magia(#si devuelve un entero significa que ese es el numero de error
            SBR.limpiar(code.replace(" ", "").upper()))#solo caracteres de sbr

        return ritmo #independientemente que haya un error este se verifica más adelante

    def magia(code):
        #Verificar si hay parentesis
        while "(" in code or ")" in code:#esta función compila lo que está entre parentesis a binario y quita los parentesis también
            parent = SBR.parentesis(code)
            if type(parent) == int: return parent
            comp = SBR.magia(parent)
            if type(comp) == int: return comp
            code = code.replace(f"({parent})", comp)

        #verificar si hay un error
        if code[0] in SBR.efects: return 9 #error 9
        if code[0] in SBR.math: return 17 #error 17
        elif not code[0] in SBR.gen: return 10 #error 10
        ritmo, math = [], "" #aqui se almacena el ritmo, y el operador
        #Separar bloques y partes de bloques
        for brick in SBR.dividir(code, SBR.gen)[1:]:
            if brick[-1:] in SBR.math: brick, math = brick[:-1], brick[-1:]
            elif set(brick).intersection(set(SBR.math)): return 17
            else: math = None
            #Extraer información del generador
            if set(brick).intersection(set(SBR.math)): return 10
            cosa = SBR.dividir(brick, SBR.efects)
            letra_gen, gen_parametros, efectos = cosa[0][0], cosa[0][1:].split(","), cosa[1:]
            crudo = Generadores.asignar(letra_gen, gen_parametros)
            #Aplicar efectos
            for efecto in efectos: crudo = Efectos.asignar(efecto[0], crudo, efecto[1:].split(","))

            ritmo += [crudo]+[math]

        #procesar operadores
        ritmo = Matematica.invocar(ritmo)

        return f"B{ritmo}"


    def comentarios(code):
        n = 1 #numero de linea actual
        linea_inicio = 0#linea donde se abrió un comentario largo
        #Qué tipo de comentario "Si está activado?"
        corto, largo = False, False
        new_code = ""
        code = code.replace("###", "\x03")
        for x in code+"\n":
            if x == "#": corto = not corto
            elif x == "\n":
                corto = False
                new_code += x
                n += 1
            elif x == "\x03":
                largo = not largo
                linea_inicio = n

            if not(corto or largo) and x != "\n": new_code += x

        if largo: return SBR.Error(6, linea_inicio)
        return new_code.replace("\x03", "").replace("#", "")#.strip()
    
    def parentesis(code):
        p = 0
        eureca = False
        new = ""
        for x in code:
            if "(" == x:
                p += 1
                eureca = True
            elif ")" == x:
                if not eureca: return 7
                p -= 1
                if not p: eureca = False
            if eureca: new += x
        if not p-1: return 8
        return new[1:]


    def dividir(code, cosa):
        brick = ""
        bloques = []
        for x in code+cosa[0]:
            if x in cosa:
                bloques.append(brick)
                brick = ""
                brick += x
            else: brick += x

        return bloques

    def Error(numero_error, linea):
        try: return "F", f"Error #{numero_error} en la linea {linea}, {SBR.lista_errores[f"ERROR_{numero_error}"]}"
        except KeyError: return "F", "Error desconocido"

    lista_errores = {
        "ERROR_1": "Codigo vacio",
        "ERROR_2": "Esta variable no existe",
        "ERROR_3": "No has agregado nada a la variable",
        "ERROR_4": "Estás agregando algo a la nada, no hay variable",
        "ERROR_5": "Este nombre de variable no es valido",
        "ERROR_6": "Nunca finalizó el comentario",
        "ERROR_7": "Nunca se abrió un parentesis",
        "ERROR_8": "Nunca se cerró un parentesis",
        "ERROR_9": "Debes empezar el bloque por un generador, no un efecto",
        "ERROR_10": "Debes empezar el bloque por un generador, no otra cosa",
        "ERROR_11": "No hay bloque con qué usar operador",
        "ERROR_12": "Salida vacia",
        "ERROR_13": "Asignación de tempo invalida",
        "ERROR_14": "No hay comando antes del doble punto",
        "ERROR_15": "No se reconoce este comando",
        "ERROR_16": "Debes asignar un canal de salida al comando S, por ejemplo \"S7: E5S3\" salida para el canal 7",
        "ERROR_17": "Debes empezar el bloque por un generador, no un operador",
        "ERROR_18": "Caracter fuera de rango U+0000-U+007F",
        }

    def leer(ruta):
        with open(ruta, "r") as archivo: return archivo.read()


class Matematica:
    def invocar(data):
        salida = data[0]
        if data[-1:][0] == None: data = data[:-1]
        elif data[-1:][0] in SBR.math: data = data[:-1]
        for x in range(len(data)-2):
            if data[x+1] == None: salida += data[x+2] #Concatenar
            elif data[x+1] == "+": salida = Matematica.superponer(salida, data[x+2])
            elif data[x+1] == "-": salida = Matematica.fantasma(salida, data[x+2])

        return salida

    def superponer(r1, r2):
        r1, r2 = Efectos.cuantizar(r1), Efectos.cuantizar(r2)
        salida = ""
        if len(r1) > len(r2): r2 += "0"*(len(r1)-len(r2))
        else: r1 += "0"*(len(r2)-len(r1))
        for b1, b2 in zip(r1, r2): salida += str(int(int(b1) or int(b2))) #or
        return salida

    "Esta es la misma función de arria solo que usa una compuerta Xor"
    def fantasma(r1, r2):
        r1, r2 = Efectos.cuantizar(r1), Efectos.cuantizar(r2)
        salida = ""
        if len(r1) > len(r2): r2 += "0"*(len(r1)-len(r2))
        else: r1 += "0"*(len(r2)-len(r1))
        for b1, b2 in zip(r1, r2): salida += str(int(int(b1) ^ int(b2))) #xor
        return salida

class Generadores:
    def asignar(letra, args):
        #eliminar Argumentos vacios
        for _ in range(args.count("")): args.remove("")
        if letra == "E": return Generadores.E(args)
        elif letra == "B": return Generadores.B(args)
        elif letra == "C": return Generadores.C(args)
        elif letra == "?": return Generadores.aleatorio(args)
    
    def B(arg):
        if arg == []: return ""
        return arg[0] #es la misma vaina no?
    
    def C(arg):
        if not len(arg): arg = [3, 32]
        elif not len(arg)-1: arg.append(32)
        return (f"{10**(int(arg[0])-1)}"*int(arg[1]))[:int(arg[1])]

    def E(arg):
        if not len(arg): arg = [5, 16, 16]
        elif not len(arg)-1: arg += [16]*2
        elif not len(arg)-2: arg += [16]
        a, b, c = arg
        a, b, c = int(a), int(b), int(c)
        if a > b: a = b
        if a == 0: return ["0" for i in range(c)]
        
        #Simetrizar
        pattern = []
        counts = []
        remainders = []
        divisor = b - a
        remainders.append(a)
        level = 0
        while True:
            counts.append(divisor // remainders[level])
            remainders.append(divisor % remainders[level])
            divisor = remainders[level]
            level = level + 1
            if remainders[level] <= 1: break
        counts.append(divisor)

        def build(level):
            if level == -1: pattern.append(0)
            elif level == -2: pattern.append(1)
            else:
                for i in range(0, counts[level]): build(level - 1)
                if remainders[level] != 0: build(level - 2)

        build(level)
        i = pattern.index(1)
        pattern = pattern[i:] + pattern[0:i]

        #Ajustar longitud
        n = 0
        final_pattern = ""
        while c != len(final_pattern):
            if n == len(pattern): n = 0
            final_pattern += f"{pattern[n]}"
            n += 1

        return final_pattern #Yeii :D
    
    def aleatorio(arg): #Argumentos: longitud, cantidad, empezar por 1?
        #crear argumentos en caso de que no los haya
        if not len(arg): arg = [8, 0, 0]
        elif len(arg) == 1: arg += [0]*2
        elif len(arg) == 2: arg += [0]
        arg = int(arg[0]), int(arg[1]), int(arg[2])

        #verificar que A sea mayor o igual que B
        if arg[0] == 0 or arg[1] > arg[0]: return ""

        #verificar que se deba empezar por un 1
        elif arg[2] != 0: indices = [0]
        else: indices = []

        #si la cantidad es 0 se definirá de forma aleatoria
        cantidad = arg[1]
        if cantidad == 0: cantidad = random.randint(1, arg[0])

        #generar indices
        while len(indices) < cantidad:
            dato = random.randint(0, arg[0]-1)
            if not dato in indices: indices.append(dato)

        #Si el ritmo debe empezar por 1
        
        pre_final = [0]*arg[0]
        for x in indices: pre_final[x] = 1
        
        #pasar a string
        final = ""
        for x in pre_final:
            if x == 1: final += "1"
            else: final += "0"

        return final


class Efectos:
    def asignar(letra, data, args):
        for i in range(args.count("")): args.remove("")
        if letra == "L": return Efectos.L(data, args)
        elif letra == "X": return Efectos.X(data, args)
        elif letra == "S": return Efectos.S(data, args)
        elif letra == "P": return Efectos.P(data, args)
        elif letra == "Q": return Efectos.Q(data, args)
        elif letra == "D": return Efectos.D(data, args)
        elif letra == "R": return Efectos.R(data)
        elif letra == "I": return Efectos.I(data)
        elif letra == "*": return Efectos.multiplicar(data, args)
        elif letra == "{": return Efectos.abrir(data, args)
        elif letra == "}": return Efectos.cerrar(data, args)


    def L(data, arg):
        if not len(arg): return data
        elif len(data) <= int(arg[0]): return (data*int(arg[0]))[:int(arg[0])]
        return data[:int(arg[0])]

    def X(data, arg):
        if not len(arg): arg = ["2"]
        arg = int(arg[0])
        if arg == 0: return ""
        elif arg == 1: return data
        #Ritmos binarios
        elif arg == 2:
            data = data.replace("0", "00")
            data = data.replace("1", "10")
            data = data.replace("2", "11")
            data = data.replace("4", "11")
            data = data.replace("8", "11")
            data = data.replace("3", "10010010")
            data = data.replace("6", "1000010000100000")

        #Ritmos ternarios o mayores a 2
        elif arg > 2:
            data = data.replace("0", "0"*arg).replace("1", "1"+"0"*(arg-1))
            data = data.replace("3", Generadores.E([3, 4*arg, 4*arg]))
            data = data.replace("6", Generadores.E([3, 8*arg, 8*arg]))
            data = data.replace("2", Generadores.E([2, arg, arg]))
            data = data.replace("4", Generadores.E([4, arg, arg]))
            data = data.replace("8", Generadores.E([8, arg, arg]))

        return data

    def S(data, arg):
        if not len(arg): arg = ["7", "0"]
        if len(arg) == 1: arg += ["0"]
        data = Efectos.cuantizar(data)
        modo = int(arg[1])
        if modo: data = data[::-1]
        arg = int(arg[0])
        final = ""
        cantidad = 0
        for pulso in data:
            if pulso == "1" and cantidad < arg:
                cantidad += 1
                final += "1"
            else: final += "0"

        if modo: return final[::-1]
        return final

    def D(data, arg):
        longitud = len(data)
        data = Efectos.cuantizar(data)
        if not len(arg): arg = ["3", "3"]
        elif len(arg) == 1: arg.append("3")
        intervalo, cantidad = int(arg[0]), int(arg[1])
        data_2 = list(data)
        final = ""

        #Aplicar delay >:D
        for x in range(longitud):
            if data[x] == "0": continue
            for y in range(1, 1+cantidad):
                pulsar = x+intervalo*y
                if pulsar >= longitud: continue
                data_2[pulsar] = "1"

        for x in data_2: final += x

        return final, data


    def R(data): return data[::-1]
    
    def I(data):
        salida = ""
        data = Efectos.cuantizar(data)
        for x in data: salida += str(int(not bool(int(x))))
        return salida
    
    def P(data, arg):
        if arg == []: arg = ["1"]
        elif arg == ["0"]: return data
        arg = int(arg[0])
        while arg > len(data): arg -= len(data)
        return data[-arg:]+data[:-arg]

    def Q(data, arg):
        for i in range(arg.count("0")): arg.remove("0")
        arg = [int(x)-1 for x in arg] #Convertir argumentos a enteros y restar 1
        final = ""
        i = 0
        for p in data:
            if p == "1":
                if i in arg: final += "0"
                else: final += "1"
                i += 1
            else: final += "0"

        return final

    def abrir(data, arg):
        if arg == []: arg = [1]
        return data[int(arg[0]):]
    
    def cerrar(data, arg):
        if arg == []: arg = [1]
        return data[:-int(arg[0])]
    
    def multiplicar(data, arg):
        if arg != []:
            return data*int(arg[0])
        return data
    
    #lo de arriba parece un pene :D

    "Funciones complemetarias"

    def cuantizar(data):
        data = data.replace("6", "10010010")
        data = data.replace("3", "1110")
        data = data.replace("8", "1")
        data = data.replace("4", "1")
        data = data.replace("2", "1")
        return data
