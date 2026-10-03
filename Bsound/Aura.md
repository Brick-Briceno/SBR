# Aura

Es un sintetizador enfocado a la sintesis compleja de sonido

## Como crear presets?

### Tokens y ByteCode

Los decimales o parametros se hacen con float32

Meta datos:
version_compiler
name

Variables:

note_hz
duration
velocity
slide


var + puntero


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
    "meta": {
    "version": "1.0.0",
    "name": "Cyberpunk Reese Bass",
    "author": "AudioDev",
    "category": "Bass",
    "tags": ["resampling", "distorted", "sub"],
    "description": "Heavy wavetable bass with OTT style dynamics and fast LFO"
  },
  "global": {
    "master_gain_db": -0.1,
    "pitch_bend_range": 2,
    "polyphony_mode": "mono",
    "legato": true,
    "glide": true,
    "portamento": .045,
    "tuning_hz": 440.0
  },

  "oscillators": [
    {
      "id": "osc_1",
      "enabled": true,
      "wavetable": {
        "name": "Basic_Shapes",
        "embedded": true,
        "frame_count": 256,
        "sample_rate": 44100,
        "audio_data_base64": "..." 
      },
      "frame_position": 0.35,
      "unison": {
        "count": 7,
        "detune": 0.18,
        "stereo_spread": 0.85,
        "blend": 0.5
      },
      "tuning": {
        "octave": -1,
        "transpose": 0,
        "fine_tune_cents": 0
      },
      "level": 0.85,
      "pan": 0.0,
      "phase": 0.0,
      "phase_randomness": 1.0,
      "warp": {
        "type": "bend_plus",
        "amount": 0.4
      },
      "output_routing": "filter_1"
    }
  ],
  "sample_generator": {
    "enabled": false,
    "sample_path": "samples/noise/white.wav",
    "level": 0.5,
    "key_track": false,
    "loop": true
  },
  "envelopes": [
    {
      "id": "env_1",
      "is_amp_env": true,
      "attack_s": 0.005,
      "decay_s": 0.35,
      "sustain": 0.7,
      "release_s": 0.15,
      "curves": {
        "attack_slope": 0.0,
        "decay_slope": -0.4,
        "release_slope": -0.5
      }
    }
  ],
  "lfos": [
    {
      "id": "lfo_1",
      "sync_mode": "tempo",
      "frequency_hz": 2.0,
      "tempo_division": "1/8t",
      "trigger_mode": "trigger",
      "smooth_ms": 5.0,
      "nodes": [
        {"x": 0.0, "y": 0.0, "control_x": 0.25, "control_y": 0.8},
        {"x": 0.5, "y": 1.0, "control_x": 0.75, "control_y": 0.2},
        {"x": 1.0, "y": 0.0, "control_x": 0.0, "control_y": 0.0}
      ]
    }
  ],
  "filters": [
    {
      "id": "filter_1",
      "enabled": true,
      "type": "lowpass_24db",
      "cutoff_hz": 1200.0,
      "resonance": 0.4,
      "drive": 3.5,
      "key_track": 0.5,
      "routing": "serial"
    }
  ],
  "mod_matrix": [
    {
      "source": "lfo_1",
      "destination": "filter_1.cutoff_hz",
      "amount": 0.65,
      "mode": "bipolar",
      "aux_source": "mod_wheel",
      "aux_amount": 1.0
    },
    {
      "source": "macro_1",
      "destination": "osc_1.frame_position",
      "amount": 1.0,
      "mode": "unipolar"
    }
  ],
  "fx_chain": [
    {
      "type": "distortion",
      "enabled": true,
      "mix": 0.75,
      "params": {
        "mode": "saturate",
        "drive_db": 12.0
      }
    },
    {
      "type": "multiband_compressor",
      "enabled": true,
      "mix": 1.0,
      "params": {
        "upward_comp": 0.5,
        "downward_comp": 0.8,
        "time_scale": 1.0
      }
    }
  ],
  "macros": [
    {"id": "macro_1", "name": "Timbre", "value": 0.35},
    {"id": "macro_2", "name": "Space", "value": 0.0}
  ]
}


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

