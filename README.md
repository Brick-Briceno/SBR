# SBR language 🚀

![](https://img.shields.io/badge/python-3.13-blue) ![](https://img.shields.io/badge/license-BSD%203--Clause-green)

The SBR language provides super creative tools
to musicians to make good music and from this make memorable melodies

With all my heart I hope that good things can be
made with this tool, I hope that people have fun experimenting
with it and that it helps all of you make better music, hugs 💙

@Brick\_briceno 2023

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
git clone https://github.com/Brick-Briceno/SBR.git
cd SBR
# 2. Install dependencies ()
Get-Content ./dependencies.sh | Out-String | Invoke-Expression
# 3. Compile exe
.\build.bat

```

### Compile in Android 📱

```bash
# 1. Clone and enter the folder
git clone https://github.com/Brick-Briceno/SBR.git
%cd SBR

# 2. Give permissions and prepare (this creates the venv and buildozer.spec)
chmod +x prepare_build_android.sh
./prepare_build_android.sh

# 3. COMPILE (Using the absolute path to buildozer from the venv)
./venv/bin/buildozer -v android debug

```
