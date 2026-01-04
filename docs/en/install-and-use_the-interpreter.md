# Install

Windows: 

Source code
```bash
git clone https://github.com/Brick-Briceno/SBR.git
./dependencies.sh
cd SBR
py .
```

***The program must have a main.sm file to work, in which the data, keywords or variables that you want to have loaded whenever you run the interpreter will be stored.***

## How to use

***To learn how to use it with "help:" in the console and all the information will appear***

***Or check the*** [ SBR Tutorial](sbr-tutorial.md)


## How to use the interpreter


## Run some of these keywords to take full advantage of the language's potential
```sbr
--Learn SBR
help:
--view actual variables
vars:

--play sounds
play: Sm{son*2; Jumps 5,-1,5,-1,5,-1,-2,-1,-1 Oct5}
play: Sm{E13S12X2; pop Oct6 Arp}*4

--play sounds and pause everything until the sound stops
play: Sm{son S4 X2; pop Oct5}*4:: true

```

### You can clear the SBR console with these keywords:
```
clear
cls
...
..
```
### You can pause the sound on SBR console with these keywords:
```
pause: (This is the only one that works outside of interactive mode)
ctrl + p + enter
. (a simple dot)
pause
```

My recommendation is that if you want to pause on interactive mode, use a dot
If you have SBR code in a file, it's best to use "pause:"

### You can pass arguments to the executable and open code files to test it
```bash
sm my_amazing_song.sm
py . my_amazing_song.sm
```

### View help
```bash
sm -help
sm -h
```

### Run a small snippet of SBR code
```bash
sm -code "play: |5:: true"
sm -c "play: |5:: true"
```

### Know SBR version
```bash
sm -v
```

- [Home](README.md) 🏡
- [SBR Tutorial](sbr-tutorial.md) 📖

