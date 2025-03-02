# SBR language 🚀

![](https://img.shields.io/badge/python-3.13-blue) ![](https://img.shields.io/badge/license-MIT-green)

The SBR language provides super creative tools
to musicians to make good music and from this make memorable melodies

With all my heart I hope that good things can be
made with this tool, I hope that people have fun experimenting
with it and that it helps all of you make better music, hugs 💙

@Brick\_briceno 2023

## Key Features ✨

- **Intuitive Syntax**: Designed to be easy to learn and use.
- **Interoperability with Python**: You can use SBR data types with Python


## Install

```bash
git clone https://github.com/Brick-Briceno/SBR.git
cd SBR
pip .
```

***The program must have a main.sm file to work, in which the data, commands or variables that you want to have loaded whenever you run the interpreter will be stored.***

## How to use

***To learn how to use it with "help:" in the console and all the information will appear***


![](img/image1.png)
It's not necessary to have 2 parameters, it can be just one

### Syntax

In case of havin purely numeric characters, it will be  
prossed as a mathematical operation and the order of the  
operations will be based on the PEMDAS standard (parentesis,  
exponents, multiplication, addition, subtraction)  

```
Examples:
5+5*2 = 15  
(5+5)*2 = 20

--You can do this as well  
(5+5)2 = 20  
```

but... and if it's melodic?  

However, in case of containing generators, effects or any musical data  
such as notes, tones, thythms or a groups, everything will be  
processed left to right in this order  

Examples:  
```
  ↓↓↓↓all this are an argument, only one  
 B1000 L8 = B1000 1000  
 ↑     ↑     ↑  
 ↑     ↑     (zeros and ones) these are the rhythm data  
 ↑    (L) repeats the number of bits until x number long (effect)  
(B) is used to generate the bits (generator)  
```

The total of all the code is called Brick :D  
Other example  

```
 M0,-2,2,-1  
 ↑     ↑  
 ↑    (0,-2,2,-1) arguments are separated by commas  
(M) is used to generate the tones  
```

### Run some of these commands to take full advantage of the language's potential
```
help: tutorial
help: effects
help: generators
help: commands
help: operators
help: syntax
help: E
```
