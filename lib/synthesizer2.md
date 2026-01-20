# Aura

Ok necesito hacer el backend de un sintetizador, y para empezar los presets, o la información que se tiene que sintetizar estará estructurados de la siguiente manera en json

Existirá mierda que se llamará generador que puede tener un argumento del 0 al 1, de 0 a .3333 será un rango entre seno y triángulo, de .3333 a .6666 de triángulo a cuadrada, de .6666 a 1 hasta diente de sierra

## Existirán variables globales como

El velocity 

Cuántas negras lleva sonando la nota (duración) 

Altura de la nota

El bpm

## Cada objeto tendrá atributos, que en realidad son strings con referencia

progreso del slide

intensidad del side

Todos esos atributos en realidad son variables globales Solo que con su nombre al principio para tener una referencia clara

se podrán crear tantas envolventes como sean posibles y a todos los parámetros se podrán automatizar con cualquier cosa a su vez, bien rico todo uff

las envolventes también se les puede automatizar con otras envolventes no automatizadas o con variables globales

Y una envolvente también puede ser el retorno de un generador

También hay una pequeña función que genera datos aleatorios


### El main

El main puede tener muchas de las propiedades, efectos y características que tiene sus hijos, los osciladores

Si es polimorfismo por ejemplo

Existirán dos tipos de efectos los de tipo 1 y los de tipo 2


### Efectos tipo 1

Los de tipo 1 se aplican al wave table, osea a un array de audio que tiene una frecuencia de hipotéticamente 1hz que durará un segundo, esto significa que tendrá su fase positiva como negativa 

Algunos de los efectos tipo uno van a ser

El estiramiento de armónicos

El pulso, que va a dividir la onda a la mitad y poner un silencio y ese silencio va a ir creciendo hasta que vaya desplazando la longitud de las otras dos partes de la onda

La formante de la onda 

El Smear

Vocoder

Amplitudes aleatorias 

Filtros paso bajo y paso alto que se van a controlar con números positivos o negativos, dos efectos en uno solo, además de que se va a filtrar los armónicos a partir de las frecuencias de esa onda, no va a filtrar por hz con un ecualizador normal en un Master 

Dispersión de la fase

Tono de shepard

Flanger

Phaser

Ecualizador

### Cómo funciona?
A nivel de gestión de memoria el sintetizador

Para ahorrar recursos primero se crea el wave table con todos los efectos de este, y después se pasa por una fórmula que te devuelve la cantidad de repeticiones que el tablet necesita y el porcentaje de aceleración para tener la duración y la frecuencia exacta que se necesita


### Efectos tipo 2
Estos son los que se le pone al array de audio resultante 

ADSL con sus otros parámetros, los parámetros completos quedarían el delay, ataque, hold, sustain y release, es simplemente un efecto sencillo de automatización de volumen en sí

Ecualizador, quizás sea un poco redundante porque ya gay un ecualizador en los efectos de tipo 1 pero en algún caso puede servir

Chorus, que en este caso tiene más sentido ponerlo de tipo 2 porque aquí las ondas pueden ser más variables durante un sonido más largo de un ciclo de onda

Phaser

Distorsión, de válvulas, diodo, cliper, y con una envolvente se podrá crear una distorsión propia 

Delay 

Compresor óptico, analógico, y limpio

Normalizador, sea en picos, rms, o lufs por curva isotónica

Otras cosas

A las envolventes se les podrá poner distorsiones que se pueden expresar con fórmulas matemáticas Como por ejemplo la logarítmica o las lineales o condicionales 

Esto servirá para un montón de cosas exponencialmente inimaginables como hacer que glide sea más lento al principio por ejemplo

Qué llevo hecho?

Ya tengo una rever, los filtros paso alto y paso bajo se hacen con scipy, y el delay simplemente se hace superponiendo trozos de array un poco después, calculando el bpm y todas esas cosas

Podría quedar mejor así

```

Main{
    "id_manzana"; Osc 1 effect_type_one
    "id_pera"; Osc 1 effect_type_one
    "id_mango"; Osc 1 effect_type_one
} ADSL .1, .9, .8, .2

```

## Tipos de datos

1. floats (numeros)
2. arrays (envolventes o wave tables) quizas tanmbien generadores de vectores con curvas
3. referencias (son como punteros que toman un id de qué se quiere automatizar)

```json

{
    "lfos": {
        "": 0,
    },
    "main": {
        // effectos para el main, se aplican a todos los osciladores
        "effects": {
            "ADLS": {"delay": .1, "attack": .9, "hold": .8, "sustain": .2},
            "glide": .5, // puede tambien ser otro objeto, puede ser false tambien
            "isophonic curve": true,
            "Eq": [
                {"Hz": 440, "Db": -3, "Q": 1.2},
            ], //
            },
        // osciladores
        "osl1": {
            /* el argumento de "wave" va del 0 al 1, de 0 a .3333 será un rango entre
            seno y triángulo, de .3333 a .6666 de triángulo a cuadrada,
            de .6666 a 1 hasta diente de sierra */
            "wave": 1, // en este caso es un diente de cierra
            //"wave": "id_sample", // tambien puede ser un sample
            // si solo, volume y muted en algún oscilador son 0 y o false lado automaticamente no suena nada
            "volume": 1,
            "muted": false,
            "solo": false,
            // effectos para el oscilador
            "effects": {
                "harmonic stretch": .5,
                "pulse": .75,
                },
        }
    }
}


```

El estiramiento de armónicos

El pulso, que va a dividir la onda a la mitad y poner un silencio y ese silencio va a ir creciendo hasta que vaya desplazando la longitud de las otras dos partes de la onda

La formante de la onda 

El Smear

Vocoder

Amplitudes aleatorias 

Filtros paso bajo y paso alto que se van a controlar con números positivos o negativos, dos efectos en uno solo, además de que se va a filtrar los armónicos a partir de las frecuencias de esa onda, no va a filtrar por hz con un ecualizador normal en un Master 

Dispersión de la fase

Tono de shepard

Flanger

Phaser

Ecualizador



## Backend

No se como mierda lo haré pero de que lo hago lo hago

