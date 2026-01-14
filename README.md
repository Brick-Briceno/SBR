# SBR language 🚀

![](https://img.shields.io/badge/python-3.13-blue) ![](https://img.shields.io/badge/license-BSD%203--Clause-green)

The SBR language provides super creative tools \
to musicians to make good music and from this make memorable melodies

With all my heart I hope that good things can be made with this tool \
I hope that people have fun experimenting with it and that it helps \
all of you make better music, hugs 💙

@Brick\_briceno 2023

## Why did I do it?

SBR began in 2022 as a simple tool born from my obsession with combining \
mathematics with melodies, especially for memorable music, I found it more \
comfortable to use ones and zeros than staves, so I started applying logic \
gates like AND, OR, NOT, and XOR, since I had some knowledge of digital \
electronics. But before that, what truly captivated me was a 2004 article about \
Euclidean rhythms and how prominently they appeared in the traditional music of \
many cultures. Later, I discovered that by combining them with certain effects,\
I could create pop songs with billions of views across all platforms using \
simple formulas. Besides Euclidean rhythms and logic gates, I applied \
repetition and structural techniques that I already knew and had been using in\
my music since 2019, combined with adding and removing notes that I learned

while analyzing various songs. In 2023, I decided it would become a language, \
as that was the best way to scale the project and integrate it with other \
technologies

That was, and still is, the purpose of SBR. Originally, it only... Rhythms, in \
its version 2 melodies, chords, sounds, sirings, numerical data, arrays, among \
other types of data that are like wheat with which you can create doughs with \
it in turn you can create a lot of types of foods based on flours, the same here 

## Tutorial

- [Tutorial SBR 😉](docs/en/README.md)
- [Click here to learn more about SBR 🎹](docs/en/about.md)


## Key Features ✨

- **Intuitive Syntax**: Designed to be easy to learn and use.
- **Interoperability with Python**: You can use SBR data types with Python

*Check the SBR data types module*


### Compile in Windows 💻

```bash
# 1. Download
git clone --depth 1 https://github.com/Brick-Briceno/SBR.git
cd SBR
# 2. Install dependencies ()
Get-Content ./dependencies.sh | Out-String | Invoke-Expression
# 3. Compile exe
.\build.bat

```

### Compile in Android 📱

```bash
# 1. Clone and enter the folder
git clone --depth 1 https://github.com/Brick-Briceno/SBR.git
cd SBR

# 2. Give permissions and prepare (this creates the venv and buildozer.spec)
chmod +x prepare_build_android.sh
bash prepare_build_android.sh

# 3. COMPILE (Using the absolute path to buildozer from the venv)
source venv/bin/activate
./venv/bin/buildozer -v android debug
echo "The checksum is as follows:"
sha256sum bin/*

```
