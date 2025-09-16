# Lenguaje SBR  
Sintaxis Brick Ritmo

*Los siguientes son códigos para generar ritmos y melodías a través de algoritmos, sobre todo en el programa Symmetry Melody 2 creado por @Brick\_briceno*

*Este mini tutorial estará dividido en 3 partes primero la parte rítmica, seguido de la parte melódica o mejor dicho tonal, y finalmente la parte verdaderamente melódica, cómo unir un poco las piezas y algunas que otras herramientas del control de flujo* 

Empecemos por la parte rítmica 

**El Ritmo** 🥁

*Nuestras literalmente piezas de Lego serán…*

**Generadores:** C, B, E, A, N  
**Efectos:** L, X, D, R, I, P, \[, \], S, Q, \*  
**Operadores:** \+, \-, nada  
**Parámetros:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 0

**C** (repetir un número)

*Cuando sale C seguido de un número significa que pondrá X pulsos cada determinada cantidad de tiempos hasta que el bucle termine, por defecto son 32 bits*

C3 \= 1001 0010 0100 1001 0010 0100 1001 0010  
C4 \= 1000 1000 1000 1000 1000 10001 000 1000  
C5 \= 1000 0100 0010 0001 0000 1000 0100 0010

Si quieres que la longitud del bucle sea 8 lo escribes así

C3,8 \= 10010010

la **C** es un **Generador**, los generadores pueden admitir varios parámetros, son como una especie de maquinita que le metes uno o más datos y te arroja un resultado, si nos ponemos más técnicos es en programación o matemáticas lo que llamamos una función

![](img/image31.png)  
*Esto en SBR se Le conoce como bloque o Brick, se compone de:*

*Un generador (indispensable)*  
*Parámetros (opcional)*  
*Un efecto (opcional)*  
*Parámetros para el efecto (opcional)*

Puede haber un generador sin parámetros y con un valor preestablecido, puede también tener parámetros, puede tener efectos y estos pueden o no tener parámetros, al fin y al cabo en un bloque no puede haber 2 generadores, pero si en un código unimos varios bloques simplemente se pegan sin más complejidad

Pero… ¿Y qué es un efecto?

**L** (definir la **L**ongitud)

la L es nuestro primer efecto

Si quieres que la longitud de un dato o ritmo sea 8 lo escribes así tambien

Se repite el bucle hasta finalizar las 8 semicorcheas o bits, pero recuerda que estamos en base a 16 por lo si no ponemos el valor L seguirá hasta llegar a 16

En realidad quedaría así

C3,16 \= 10010010 01001001

C3,16 \= C3L16

Si tenemos un ritmo más corto que el parámetro de L este repetirá el bucle hasta completar el parámetro L, osea lo cortará hasta donde este diga

Por ejemplo

C3L4L8 \= 1001 1001

C3 nos arroja una secuencia de puros “100” repetidos hasta llegar a una longitud de 32, con L4 lo recortamos a 4 bits “1001” y después lo volvemos a alargar con otro efecto L pero alargando la a 8 bits, “osea mil uno mil uno”, “1001 1001”

**B** (escribes el ritmo en binario)

En realidad en este maravilloso lenguaje no se escriben solo unos y ceros para identificar un ritmo, debes ponerle una B mayúscula al principio, B es un generador y los números son sus parámetros o argumentos

B10101 \= 10101

B1L4 \= B1111  
B100L4 \= B1001  
B1000L8 \= B10001000

C3,4 \= B1001  
C3L4 \= B1001

**N** (otra forma de escribir los números) 

N3 3 2 \= B1001 0100  
N3 3 3 3 2 2 \= B1001 0010 0100 1010  
N2221 2221 2 \= B1010 1011 0101 0110 

**X** (duplicas la longitud del ritmo)  
*Estiras el ritmo*

Agarramos cada uno de los dígitos y entremedio le metemos (x cantidades de ceros menos 1\)

Ósea si tenemos por ejemplo  
B10010010X2

B10010010X2 \= 1000001000001000

Reemplazamos los 1 por 10 y los 0 por 00  
Si X fuera 3 entonces 1 sería 100 y 0 seria 000 etc

B1X4L8 C3L8 \= 10001000 10010010

por cierto, los espacios en el código se eliminan automáticamente

serán bloques separados, salvo que… usemos operadores

**E** (euclidiano)

Genera ritmos euclidianos, ritmos que suenan excelentes y se encuentran en la música tradicional de prácticamente todas las culturas

Aquí tienes un enlace de todas las culturas que usaron y siguen usando ritmos euclidianos

[The Euclidean Algorithm Generates Traditional Musical Rhythms](https://cgm.cs.mcgill.ca/~godfried/publications/banff.pdf)

En SBR puedes generar estos ritmos tan agradables y más

El 1er parámetro define la cantidad de pulsos que se distribuirán de forma simétrica en (2do parámetro) cantidad de bits

E5,8 \= B1101 1010

5 pulsos en un total de 8 bits   
Osea, 5 pulsos y 3 ceros (8-5=3)

E3,8 \= B1001 0010

Por cierto si no asignamos un segundo parámetro, este se establecerá por defecto como 16 

E5,16 \= E5

Y si no asignamos nada este se establecerá como E5

E \= E5

De aquí podemos experimentar mucho con estos sonidos 

E4 \= B1000 1000 1000 1000  
E5 \= B1001 0010 0100 1000 (simplemente E)  
E6 \= B1001 0010 1001 0010  
E7 \= B1010 1001 0101 0010  
E8 \= B1010 1010 1010 1010  
E9 \= B1010 1011 0101 0110  
E10 \= B1011 0110 1011 0110

y así…

En caso de que añadamos un tercer parámetro este actuará como un efecto L, lo que puede darnos una gran variedad de ritmos

Varios de ellos los he escuchado en música pop, sobre todo en hits de los 80 y de alrededor de 2015

Ejemplo

E5,14,16 \= B1001 0010 0100 1010  
E10,15,16 \= B1101 1011 0110 1101

¿Has escuchado estos ritmos en alguna melodía de alguna canción? A mí se me vienen a la mente 3, ejemplos, Ariana grande, Shakira, y AC DC

Los ritmos euclidianos esconden una ciencia detrás, puedes leer más sobre esto en un artículo de esta documentación llamado *“La magia de los ritmos euclidianos”* donde conocerás curiosidades sobre estos y su increíble historia

Léelo porque esa información no te la cuentan en casi ningúna parte de internet y ni siquiera en los conservatorios

Y todo eso no lo puedo resumir en un tutorial tan corto

**\+** (superpone 2 ritmos)

Ejemplo

B1X4L8+C3L8 \= B10011010

B1100+B1010 \= B1110

**\-** (elimina pulsos donde sean iguales)  
*Es una compuerta XOR*

*0 xor 0 \= 0*  
*1 xor 0 \= 1*  
*0 xor 1 \= 1*  
*1 xor 1 \= 0*

B0101-B0011 \= B0110

E3,8-E4,8 \= 00010010

**R** (revierte el ritmo)

E1,10,16 \= 1000000000100000  
E1,10,16R \= 0000010000000001

**I** (invierte el ritmo)  
*A esto se le llama compuerta not*

E5,14,16 \= 1001001001001010

E5,14,16I \= 0110110110110101

**\<\<** (cambia una posición a la izquierda)

B0101\<\< \= B1010

**\>\>** (cambia una posición a la derecha)

B0101\>\> \= B1010

E5\>\> \= B0100 1001 0010 0100   
E5\>\>2 \= B0010 0100 1001 0010  
E5\>\>3 \= B0001 0010 0100 1001

*No es necesario que le pongas ningún parámetro si quieres que sea 1*

**()** paréntesis

(C3L8\<\<+B0111L8)I \= B1000 1000 

Imaginemos que queremos invertir, revertir o aplicar cualquier otro efecto a un conjunto grande de otros ritmos, pues para eso nos sirven los paréntesis  
\* (Multiplica y repite datos)

B1000 1000\*2 \= B1000 1000 1000 1000   
N5L8\*8 \+ C4 \= B1000 1100 1000 1100 1000 1100 1000 1100 1000 0100 1000 0100 1000 0100 1000 0100

**S** (dejo pasar solo cierta cantidad de pulsos)  
*Imagínate que tienes una melodía con un ritmo para una letra que tiene siete sílabas contadas, solo quieres dejar pasar las primeras 9 notas*

Tomamos un ritmo con 9 pulsos 

E9 \= B1010 1011 0101 0110

Y dejemos pasar solo los primeros 7   
E9S \= B1010 1011 0101 0000

7 es el valor por defecto… de este efecto

Si quieres vamos a dejar pasar solo los primeros tres cursos pies…

E,S3 \= B1001 0010 0000 0000

*Si te preguntas qué hace esa coma ahí, pues debes separar los efectos o generadores con algún argumento o una coma para saber que no quieres usar un efecto que no existe, “ES” por ejemplo*

*Pero… ¿Qué pasa si no quiero quitar los primeros pulsos sino que quiero tenerlo de forma más simétrica y escoger cuáles pulsos quiero quitar?*

*Pues para eso nos sirve nuestro siguiente efecto*

**Q** (quito pulsos)  
*En muchas canciones es muy común tener un ritmo de la melodía o del ritmo y quitar notas y ponerlas después para sorprender por presencia o por su ausencia*

E,Q \= E,Q1  
E \= B1001 0010 0100 1000  
E,Q1 \= B0001 0010 0100 1000   
E,Q2 \= B1000 0010 0100 1000   
E,Q3 \= B1001 0000 0100 1000

Y si quiero agregar pulsos?

**Add** (agrega pulsos al bit que tú quieras)

B1001 0010 Add 4 \= B1001 1010

**\[** y **\]** (Contar el ritmo por pedazos)

Supongamos que queremos repetir una melodía o un ritmo para crear un poco de familiaridad  
B10011010\[4 \= B1010   
B10011010\]4 \= B1001

*mostrará desde el primer bit hasta el cuarto, si queremos repetir esto…*

B10011010\]4L2 \= B10011001

**3** (no es un efecto ni un generador, es un dato)

un dato como el **“1”** y el **“0”**, el **“3”** significa tresillo de negra, por lo tanto mide 4 bits

¿Qué pasa si sumamos el 3 a un patrón? se suma igual

B3     1010 \= B3    1010 

esto tiene una duración de una negras ya que el 3 ocupa 4 espacios en la dimensión temporal

¿Qué pasa si superponemos el 3 a un patrón? buscará la forma más simétrica de hacerlo

pasa algo muy interesante

B3+B1010 \= B1110

B3X2 \= B6

*El 6 representa el tresillo de blanca*

¿Pero qué pasa al superponerlo con otro ritmo?

Distribuirá de forma **simétrica** en la duración de ese pulso y después lo superpondrá con este

B6-B0000 \= B1001 0010  
B6-B0000 \= E3,8

Es como que el 3 viene por defecto en el primer parámetro del comando **E** y el segundo parametro seria la X

B3X2 \= E3,8  
B3X4 \= E3,16  
B3X8 \= E3,32

**A** aleatorio (genera un número aleatorio con la longitud de su parámetro)

*Útil al no tener inspiración, lo aleatorio suele ser asimétrico por lo que puede sonar feo, pero con técnicas como una moderada repetición creativamente se puede obtener un buen resultado, en otras palabras mezclarlo con el efecto “\[\]” puede ser una gran ayuda*

A4 ≈ 1000  
A4 ≈ 0100  
A4 ≈ 1001  
A4 ≈ 0011

puede ser cualquier cosa, pero también este efecto también puede tener un 2do parámetro

Si ponemos “0” al 2do parámetro este tendrá un número aleatorio pero siempre el primer dato será 1

A4,0 ≈ 1000  
A4,0 ≈ 1100  
A4,0 ≈ 1001  
A4,0 ≈ 1011

Si ponemos un número mayor a cero, 7 por ejemplo podemos crear una célula rítmica de 7 pulsos que pueden ser cualquier ritmo

A16,7 ≈ B1100 0010 1001 1100

**Los Tonos 🎹**

*Aquí nos basamos en la dimensión vertical en qué tan grave o agudo suena una nota*

*Si quieres conocer sobre teoría musical básica te recomiendo una sección llamada “teoría musical básica” en esta documentación*

¿Cómo representamos la información Tonal? 🤔

*Pues déjame decirte que SBR es diatónico, O sea aque solamente vamos a jugar con las notas de esa escala, si bien podemos poner notas cromáticas, por temas de practicidad SBR tiene una filosofía y un entorno diatónico*

**Notes** (notas)  
*Grado | Octava*

1|5 \= (primer grado de la 5ta octava)

Si le sumas un grado sería un 2do grado de la 5ta octava  
1|5+1 \= 2|5

Pero si encierras una parte del código en paréntesis de esta manera 5 \+ 1 es 6 entonces sería 1er grado de la 6ta octava

1|(5+1) \= 1|6

Y como “no existe un 8vo grado” entre comillas, que a lo mucho sería… su mismo nombre lo dice, ¡una 8va\! se movería un número a la derecha, por lo tanto sería esto

8|5 \= 1|6

Syntax  
In case of havin purely numeric characters, it will be  
prossed as a mathematical operation and the order of the  
operations will be based on the PEMDAS standard (parentesis,  
exponents, multiplication, addition, subtraction)

Examples:

5+5\*2 \= 15    
(5+5)\*2 \= 20

\--You can do this as well    
(5+5)2 \= 20    
but... and if it's melodic?

However, in case of containing generators, effects or any musical data  
such as notes, tones, rhythms or a groups, everything will be  
processed left to right in this order

Examples:

  ↓↓↓↓all this are an argument, only one    
 B1000 L8 \= B1000 1000    
 ↑     ↑     ↑    
 ↑     ↑     (zeros and ones) these are the rhythm data    
 ↑    (L) repeats the number of bits until x number long (effect)    
(B) is used to generate the bits (generator)    
The total of all the code is called Brick :D  
Other example

 M0,-2,2,-1    
 ↑     ↑    
 ↑    (0,-2,2,-1) arguments are separated by commas    
(M) is used to generate the tones    
Run some of these commands to take full advantage of the language's potential  
help: tutorial  
help: effects \--view all effects  
help: generators \--view all generators  
help: commands \--view all commands  
help: operators  
help: syntax  
help: E

vars: \--view actual variables

play: Sm{son\*2; Jumps 5,-1,5,-1,5,-1,-2,-1,-1 Oct5}  
play: Sm{E13S12X2; pop Oct6 Arp}\*4  
play: Sm{son S4 X2; pop Oct5}\*4

\-- this is a short comment :)

\*\*\*  
this is...  
a long comment  
I can write things  
on the lines I want to  
write, basically a multi-line comment  
\*\*\*

You can clear the SBR console with these commands:

clear  
cls  
...  
..

\-- these are rhythms  
B1000\*4  
C3  
E5,16

\-- these are notes  
1|5 \-- 1st degree of the 5th octave  
1b|7 \-- 1st degree flat, 7th octave  
1\#|7 \-- 1st degree flat, 7th octave

\-- these are groups  
\-- you can save things in them

{} \-- empty group

{1; 2; 3; 4; 5 \-- you don't need a ";" here  
6; 7; 8; 9}

\-- this  
{B10010010  
{69}; 18  
M0,1,2,3,4}  
\-- this is the same as this  
{B1001 0010; {69}; 18; M1|, 2|, 3|, 4|, 5|}

\-- these are tones  
M33,34,35  
M6|4, 7|4, 1|5

\-- they are like groups but with notes  
\-- this is a melody

Sm{son\*2; Jumps 4,1,-2,-1,-1,1,-1,-2,1 Oct5}

Sm{-- the melody must have rhythm and tones  
B1001 0010 0010 1000\*2  
M1|5, 5|5, 4|5, 2|6, 1|6, 6|6, 5|6, 3|6, 2|6  
}

play: Sm{son\*2; Jumps 4,1,-2,-1,-1,1,-1,-2,1 Oct5}

How to import Instruments and Sounds  
You can import an instrument this way I recommend that you load all the instruments and sounds you are going to load in the initial main.sm file to avoid this repetitive task

\--Instruments  
instrument: inst\\Synt1  
instrument: inst\\Synt3

\--Samples  
instrument: inst\\Vocal.wav

\--Percusions  
instrument: inst\\Kick.wav  
instrument: inst\\Clap.wav  
instrument: inst\\Hat.wav  
instrument: inst\\Snare.wav  
\-- The instruments are called this way  
$Synt1  
$Kick

\-- They will show something like this in the console  
$12 \*\*\*$Synt1 recorded instrument from 'inst\\Synt1'\*\*\*  
$15 \*\*\*$Kick sampled instrument from 'inst\\Kick.wav'\*\*\*

The letter V indicates the velocity or force with which a note is hit, but in this case it means the decibels of the track. In melodies it ranges from 0 to 1, but in the case of structures it works from \-∞ to 0

\-- creating a polyrhythm in SBR  
tempo \= 103  
i\_dance \= Struct{  
  V0; $Kick; bossa\*2  
  V0; $Clap; C8 \>\>4  
  V0; $Hat; E13L32  
}

play: i\_dance \* 2  
\-- creating a melody in SBR  
mode \= wind  
tone \= e\_  
tempo \= 128

bass \= Sm{  
   B1010 1011\*2 X8  
   M1|1, 6|, 7|, 3|1, 2|1  
}

play: bass\*2 Oct3

view the magic  
\-- creating a Song in SBR  
mode \= wind \-- minor mode  
tone \= f\_ \-- f tone  
tempo \= 128 \-- this is the tempo in bpm

\-- melody

intervals \= 0,4,0,-1,-1,

melody \= Sm{  
   (son Add14 \* 3 C3,4\*2X2Q4) \* 2  
   Jumps {  
      intervals, \-4, intervals, \-1, intervals, 1, 1, 1, \-4  
      intervals, \-4, intervals, \-1, intervals, 1, 2, \-4  
      }  
} Oct5

\-- chords  
chords \= Sm{B1000X4\*8;pop} Oct4

bass \= Sm{  
   B1010 1011\*2 X8  
   M1|1, 6|, 7|, 3|1, 2|1  
} Oct3

song \= Struct{  
  \--melody  
   V0; $Harp; melody  
   V0; $Harp; chords  
   \-- bass  
   V3; $Jazz\_Guitar; bass  
   \-- drumps  
   V0; $Kick; C4,16 son  
   V0; $Clap; C8 \>\>4 X2  
   V0; $Hat; E13L32 X2  
}

play: song

\-- This song was made some time before starting SBR  
\-- https://youtu.be/FNt8UnD2Jl4

You can pass arguments to the executable and open code files to test it  
sm my\_amazing\_song.sm  
py . my\_amazing\_song.sm  
SBR tools and commands  
Arguments in commands are separeted by (::)

help: is used to search for documentation

donate: if you like this tool, help me keep growing \<3

exit: exits the interpreter

license: displays the license

print: displays the data

type: displays the type(s) of data Example

type: 1:: son:: pop:: $Seno  
1 is an int  
B1001 0010 0010 1000 is a Rhythm  
M{1|;3|;5|},{-1|;1|;3|},{3|;5|;7|},{0|;2|;4|} is a Tones  
$8 \*\*\*$Seno\*\*\* is an Instrument  
vars: displays the variables in the system ident: identifies the code play: plays the data you enter Example

\-- plays the content  
play: son

\-- plays the content and pauses playback  
\--until the audio floats finish playing.  
play: son:: true  
sm1: a small piano roll I made in 2022-2023 sleep: pauses the code export: exports the audio of the data in different formats

Example

export: song:: my\_song.mp3  
metric: measures the metric of rhythmic data

editor: a minimalist text editor

rec: records the rhythm you play on the console

tap: calculates the bpm you enter

code\_made: displays and saves a history of the commands you have entered

instrument: is used to import an instrument, be it a folder or .wav file


## SBR tools and commands

Arguments in commands are separeted by (::)

**help:** is used to search for documentation

**donate**: if you like this tool, help me keep growing <3

**exit**: exits the interpreter

**license**: displays the license

**print**: displays the data

**type**: displays the type(s) of data
*Example*
```sbr
type: 1:: son:: pop:: $Seno
1 is an int
B1001 0010 0010 1000 is a Rhythm
M{1|;3|;5|},{-1|;1|;3|},{3|;5|;7|},{0|;2|;4|} is a Tones
$8 ***$Seno*** is an Instrument
```

**vars**: displays the variables in the system
**ident**: identifies the code
**play**: plays the data you enter
*Example*
```
-- plays the content
play: son

-- plays the content and pauses playback
--until the audio floats finish playing.
play: son:: true
```

**sm2**: a small piano roll I made in 2022-2023

**sleep**: pauses the code
```sbr
sleep: .5
-- This pauses the code for half a second<>
```

**export**: exports the audio of the data in different formats
*Example*
```sbr

export: melody:: melody.mid

valve_distortion_gain: 50

export: song:: my_song.mp3
```

**drag_n_drop** drag files to your DAW or File Explorer
*Example*
```sbr
drag_n_drop: mp3::melody:: chords:: bass
```

**metric**: measures the metric of rhythmic data

**editor**: a minimalist text editor

**rec**: records the rhythm you play on the console

**tap**: calculates the bpm you enter

**code_made**: displays and saves a history of the commands you have entered

**instrument**: is used to import an instrument, be it a folder or .wav file
The instrument route is set :)  
*Example*
```sbr
-- Brick's instruments
instrument: inst\Synt1
instrument: inst\Synt3
```
See [How to create instruments](how-to-create-instruments.md) 🎸

**valve_gain** Adds a small tube distortion that simulates the 12AX7 tube
*Example*
```sbr
valve_gain: 50
```

**brute_force** Reduce the size of your rhythmic, tonal, and melodic data
*Example*
```sbr
brute_force: melody
```

#### and many more commands
```
help ........ Everyone asks me for help but, no one asks me how I am  
donate ...... Help this project continue to grow  
exit ........ Never give up, stay hard  
licence ..... There's no description  
print ....... There's no description  
type ........ There's no description  
pulse ....... Change the time signature  
vars ........ There's no description  
clock ....... There's no description  
ident ....... There's no description  
play ........ There's no description  
pause ....... Umm i just pause, i don't know what u wanna i say .-.  
sm2 ......... A little daw that i was made in 2023 after job :)  
sleep ....... I pause the code for a few secounds  
export ...... I export addictive substances... the music! I've it in mp3, wav and mid, which do you want?  
drag_n_drop . There's no description  
metric ...... How many pulses does any data have  
len ......... What length is a data  
phrase ...... There's no description  
editor ...... A simple text editor  
rec ......... Kick enter to record the Rhythm faster  
tap ......... Use me for know the tempo that you are beating  
ls .......... If you wanna i show you files and folders...  
code_made ... I remember all you really do it  
instrument .. I record an instrument  
set_max_digits  Don't looking for the 5th hand's cat  
brute_force . There's no description  
del_temp .... I clear temporal files  
valve_distortion_gain  Set the gain for the valve distortion effect in master  
```
