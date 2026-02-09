# SBR language 🚀

![](https://img.shields.io/badge/python-3.14-blue)
![](https://img.shields.io/badge/license-BSD%203--Clause-green)

The SBR language provides super creative tools 
to musicians to make good music and from this make memorable melodies

With all my heart I hope that good things can be made with this tool 
I hope that people have fun experimenting with it and that it helps 
all of you make better music, hugs 💙

@Brick\_briceno 2022

## Why did I do it?

SBR began in 2022 as a simple tool born from my obsession with combining 
mathematics with melodies, especially for memorable music, I found it more 
comfortable to use ones and zeros than staves, so I started applying logic 
gates like AND, OR, NOT, and XOR, since I had some knowledge of digital 
electronics. But before that, what truly captivated me was a 2004 article about 
Euclidean rhythms and how prominently they appeared in the traditional music of 
many cultures. Later, I discovered that by combining them with certain effects,
I could create pop songs with billions of views across all platforms using 
simple formulas. Besides Euclidean rhythms and logic gates, I applied 
repetition and structural techniques that I already knew and had been using in
my music since 2019, combined with adding and removing notes that I learned 
while analyzing various songs. In 2023, I decided it would become a language, 
as that was the best way to scale the project and integrate it with other 
technologies

That was, and still is, the purpose of SBR. Originally, it only... Rhythms, in 
its version 2 melodies, chords, sounds, sirings, numerical data, arrays, among 
other types of data that are like wheat with which you can create doughs with 
it in turn you can create a lot of types of foods based on flours, the same here 

## Tutorial

- [Tutorial SBR 😉](docs/en/README.md)
- [Click here to learn more about SBR 🎹](docs/en/about.md)


## Key Features ✨

- **Docs**: Detailed required documentation and tutorials
- **Games**: fun games for auditory training
- **Efficient florflow**: sbr inspires you to make symmetrical music
- **Interoperability with Python**: You can use SBR data types with Python
- **Discover paradigms**: Discover new musical paradigms and techniques
- **Audio synthesis using an intuitive syntax**: You can create complex soundscapes and polished analog audio effects
- **Separates musical elements**: By separating rhythmic content from melodic content, among other data types

*Check the SBR data types module*


SBR has modules for processing rhythmic and melodic content, where for years its main
objective was to create pure rhythm, currently, it handles more data types,
which together we can colloquially call MIDI

These include lyric analysis that can help you write more or better,
in terms of rhyme, meter, or how to express yourself

It also has data types for creating synthetic sounds so realistic they
are indistinguishable from real ones, allowing you to create the most
complex and interesting sounds possible, the presets are distributed in
plain text as JSON, this is called the SBR Aura engine


## How to Compile SBR

The language is almost entirely pure Python with NumPy modules, but the audio engine is made in Rust,
reading NumPy's memory addresses for greater playback efficiency

### Compile in Windows 🪟 / Linux 🐧

If you're on Windows, you need to compile it in bash,
the script is made to compile in multiplatform using
multiple processor cores

```bash
# 1. Download
git clone --depth 1 https://github.com/Brick-Briceno/SBR.git
cd SBR

# 2. Install dependencies
bash dependencies.sh

# 3. Compile .exe or .os
bash build.sh

```

### Compile in Android 📱

```bash
# You need to be on Linux to compile the APK, use wsl

# Download
git clone --depth 1 https://github.com/Brick-Briceno/SBR.git
cd SBR

# Clean
rm -rf venv bin .buildozer ~/.buildozer

#Install things
sudo apt-get install python3.11-venv
python3.11 -m venv venv
source venv/bin/activate
pip install buildozer

# This uses deprecated features that aren't in Cython 3.0
# https://github.com/cython/cython/issues/4310
pip install Cython==0.29.37
bash dependencies.sh

apt-get update
apt-get install -y libmtdev-dev xsel xclip
apt-get install -y build-essential libltdl-dev libffi-dev libssl-dev autoconf automake libtool
export BUILDOZER_ALLOW_ORG_TEST_DOMAIN=1

# Compile apk
# buildozer android clean # (Use it to clean up temporary build files)
buildozer android debug

```
