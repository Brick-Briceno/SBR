# Aura class documentation

## Overview

`Aura` is the high-level synthesis engine used by the Bsound system. Instead of composing notes manually in arrays, the class loads a declarative preset, resolves its formulas, renders audio nodes, applies effects, and returns a stereo note

This system is designed to be a preset-driven synth layer: the user defines a sound in structured JSON-like Python dictionaries, and `Aura` compiles it into audio


## Responsibilities of the class

`Aura` is responsible for:

- loading presets from Python dicts, compressed bytes, or BaseX strings
- validating the preset schema
- resolving internal variable expressions
- generating oscillator and envelope data
- merging outputs into stereo audio
- applying master effects
- exporting the preset in different binary/text formats

## Relevant file

- [Aura.py](B:/BrickData/SBR/Bsound/Aura.py)

## Main class

```python
class Aura:
    def __init__(self, preset: bytes | dict | str, cache=True):
```

## Constructor behavior

```python
synth = Aura(preset_example)
```

The constructor accepts three valid preset input types:

- `dict`: already loaded preset object
- `bytes`: compressed JSON preset
- `str`: BaseX-encoded preset string

### Input validation

During initialization, the class verifies:

- `meta` exists and is a dict
- `meta.name`, `meta.version`, `meta.description`, `meta.author`, `meta.category` are strings
- `meta.tags` is a non-empty list
- `master` exists and is a dict
- `master` contains required keys such as `master_gain_db`, `legato`, `glide`, and `portamento`
- `data` exists and is a non-empty dict
- `out` exists and is a non-empty list

If something is invalid, it raises `AURA_ERROR`

## Internal state

`Aura` stores the following important attributes:

- `self.preset`: the validated preset dictionary
- `self.last_note`: last note frequency used
- `self.cache`: whether note reuse through caching is enabled
- `self.arrays_bank`: cache of previously computed notes

## Core generation method

### `get_note(note_hz=261.626, duration=4, velocity=.8, gain_db=-.1) -> np.ndarray`

This is the central method. It generates a note from the preset and returns a stereo audio buffer

### Parameters

- `note_hz`: fundamental frequency in Hz
- `duration`: note length in seconds
- `velocity`: note intensity scale factor
- `gain_db`: final gain to apply, in dB

### Return

Returns a NumPy array with shape `(samples, 2)`, meaning stereo audio

### Internals

`get_note()` performs the following pipeline:

1. Reads and validates master settings such as gain, glide, and portamento
2. Computes pitch glide when `glide` is enabled and a previous note exists
3. Builds a context with variables like:
   - `note_hz`
   - `note_number`
   - `octave`
   - `duration`
   - `duration_progress`
   - `velocity`
   - `glide`
   - `portamento`
4. Resolves each node stored in `preset['data']`
5. Evaluates formulas and arrays safely
6. Converts every output node to stereo
7. Sums the output nodes into a single mixed output
8. Applies master effects
9. Stores the result in cache if enabled
10. Applies the final gain offset and returns the result

### Example

```python
synth = Aura(preset_example)
audio = synth.get_note(note_hz=440.0, duration=1.5, velocity=0.9, gain_db=-1.5)
```

## Preset format

A valid preset is a dictionary with at least the following structure:

```python

preset_example = {
    "meta": {
        "version": "1.0.0",
        "name": "Example Preset",
        "description": "An example preset for demonstration purposes",
        "author": "Brick Briceño",
        "category": "Bass",
        "tags": ["resampling", "distorted", "sub"],
        "description": "Heavy wavetable bass with OTT style dynamics and fast LFO",
        },

    "master": {
        "master_gain_db": -0.1,
        "legato": True,
        "glide": True,
        "portamento": .045, #this is the time in seconds for the glide effect
        "portamento_tension": 0, # this goes from -1 to 1
        "effects": {
            # Add compression
            "la2a": {
                "peak_reduction": 50.0,
                "gain": 50.0,
                "ratio": 5,
            },
            "reverb": {
                "room_size": 0.98,
                "wet_level": 0.35,
                "dry_level": 0.65,
                "width": 1.2,
            },
        },
    },

    # Variables (They can be used as parameters for automations, LFOs, and envelopes)
    # inside variables you can use mathematical operators to create complex modulation

    # "note_hz", example: "note_hz * 2" for an octave above

    # "note_number", example: "note_number + 12" for an octave above
    # it can also be used to control the intensity of a parameter
    # for example, if you want fewer harmonics in the treble
    # you can use "note_number / 127" to control the number of harmonics

    # "octave" is note_number / 12
    # "glide" is the pitch-ratio array for the current note

    # "duration" is a constant indicating how long it lasts, expressed in seconds
    # "duration_progress" is an array progressing from 0 to duration in seconds

    # "velocity" put this variable after a "1-" and connect it to the ADSR attack
    # it will sound softer if you play more gently and stronger if you play hard, like a real instrument
    # "1-velocity" (goes from 1 to 0) and not the other way around

    # "portamento" (goes from 0 to 1) in how long it takes to complete the glide

    "data": {
        # oscillators, ADSR envelopes, and LFOs are defined in this dictionary
        # there are only 2 data types: numbers and arrays
        # and all are valid in all effect, oscillator, and LFO inputs

        # This "osc1" is optional; you can easily name it "papi rupi" if you want
        # this works like variables that store waveforms with values you can place anywhere else
        # and be careful: a variable name for the oscillator, envelope, or anything else stored in "data"
        # cannot match an effect name or any reserved word
        # the standard is to call oscillators "oscX"
        # and envelopes "envX", sometimes with an additional description
        "osc1": {
            # Available waveform types: sine, square, sawtooth, triangle, noise, silence
            "waveform": "square",
            "frequency": "note_hz * vibrato",
            "amplitude": "velocity * env1",
            "stretch": "duration_progress ",
            "duration": "duration",
            "effects": {
                "drive": {
                    "gain_db": 20,
                    "normalize": True,
                },
            },
        },
        "vibrato": {
            "waveform": "square",
            "frequency": 8,
            "amplitude": "duration_progress * .5",
            "stretch": 0,
            "duration": "duration",
        },
        "env1": {
            # All oscillators/envelopes must have a "waveform" or a "DAHDSR_envelope"
            # The compiler will look for one or the other to find other parameters
            "DAHDSR_envelope": {
                # Delay before the envelope starts, in seconds (>= 0)
                "delay": 0,
                # Attack duration until the envelope reaches its maximum, in seconds
                # This can easily be "1.125 - velocity * 1.1"
                # so it has less attack if played harder
                "attack": 0.25,
                # Time held at maximum level before decay, in seconds
                "hold": 0.2,
                # Duration of the fall from maximum to sustain level, in seconds
                "decay": .5,
                # Sustain amplitude in [0, 1]; 1 is maximum and 0 is silence
                "sustain_level": 0.5,
                # Duration of the sustain phase, in seconds
                "sustain": 0.5,
                # Duration of the release from sustain level to silence, in seconds
                "release": 2,

                # Attack curve tension in [-1, 1]: positive rises faster initially
                "attack_tension": 0.25,
                # Decay curve tension in [-1, 1]
                "decay_tension": -0.25,
                # Release curve tension in [-1, 1]
                "release_tension": 0.25,
            },
        },
    },

    # Not all oscillators need to be routed to the master output
    "out": [
        "osc1",
        ]
},


```

## `meta` section

The `meta` object contains metadata for the preset itself

Required entries:

- `version`: preset version
- `name`: preset display name
- `description`: human-readable description
- `author`: author name
- `category`: category such as `Bass`, `Lead`, `Pad`, etc
- `tags`: list of tags

These values are validated as strings or a non-empty list

## `master` section

The `master` section defines note-wide behavior and final processing

Important keys:

- `master_gain_db`: global gain offset in dB
- `legato`: feature toggle for legato behavior
- `glide`: whether portamento/glide is enabled
- `portamento`: transition time for the glide in seconds
- `portamento_tension`: tension shape of the glide, in `[-1, 1]`
- `effects`: object containing post-mix effect definitions

## `data` section

The `data` section is the heart of the synth. It contains the synthesis graph

A node can be:

- an oscillator definition
- an envelope definition
- a numeric constant
- an array
- a formula expression

### Oscillator node

Example:

```python
"osc1": {
    "waveform": "square",
    "frequency": "note_hz * vibrato",
    "amplitude": "velocity * env1",
    "stretch": "duration_progress",
    "duration": "duration",
    "effects": {
        "drive": {"gain_db": 20, "normalize": True}
    }
}
```

### Envelope node

Example:

```python
"env1": {
    "DAHDSR_envelope": {
        "delay": 0,
        "attack": 0.25,
        "hold": 0.2,
        "decay": 0.5,
        "sustain_level": 0.5,
        "sustain": 0.5,
        "release": 2,
        "attack_tension": 0.25,
        "decay_tension": -0.25,
        "release_tension": 0.25,
    }
}
```

The envelope generator uses the `Envelopes.DAHDSR_envelope()` helper to produce a one-dimensional amplitude curve

## Supported oscillator waveforms

The waveform resolver supports:

- `sine`
- `square`
- `sawtooth`
- `triangle`
- `noise`
- `silence`

These values are checked and if not supported, `AURA_ERROR` is raised

## Expression system

Aura is able to evaluate strings such as:

```python
"note_hz * vibrato"
"velocity * env1"
"note_number / 127"
"duration_progress * 0.5"
```

This is done through a restricted AST-based evaluation pipeline

### Important details

The system:

- replaces complete variable names without accidental partial matches
- prevents collisions between names such as `env1` and `env10`
- validates allowed arithmetic nodes
- rejects unknown variables
- limits expression complexity and exponent magnitude
- aligns array lengths for simultaneous modulation

Internally the following helpers are used:

- `_replace_preset_names()`
- `_validate_preset_expression()`
- `_align_preset_arrays()`
- `_maths()`

This provides a safer evaluation model than raw `eval()` on arbitrary strings

## Effects available in `master.effects`

The `effect_handlers` registry includes these built-in effects:

- `drive`
- `bit_crush`
- `valve_distortion`
- `la2a`
- `compressor_la2a`
- `br11ck67_analog`
- `reverb`
- `stereo_expander`
- `normalize`
- `invert_phase`
- `reverse`
- `fade_in`
- `fade_out`

These handlers are mapped to the DSP functions defined inside `Audio_Effects` and are called with preset-derived parameters

## Final output routing

Each entry in `preset['out']` is resolved into an array and then converted to stereo using:

```python
Audio_Effects.Stereo_Expansion.to_stereo(np.asarray(output))
```

Then all outputs are summed to obtain the final output buffer:

```python
audio_note = np.zeros((output_samples, 2), dtype=...)
for output in output_arrays:
    audio_note[:len(output)] += output
```

After that, master effects are applied and the note is multiplied by `gain_db + master_gain_db`

## Serialization utilities

Aura offers methods for storing the preset in multiple formats

### `get_bin_preset`

Returns a compressed binary representation of the preset JSON

```python
binary = synth.get_bin_preset
```

### `get_baseX_preset`

Returns a BaseX-encoded string designed for compact textual transport

```python
encoded = synth.get_baseX_preset
```

### `get_json_preset`

Returns compact JSON text of the preset without extra formatting

```python
json_text = synth.get_json_preset
```

### `get_SBR_string_preset`

Creates a text-friendly string version that can be embedded in SBR-style code

```python
code = synth.get_SBR_string_preset
```

## Utility conversion functions

### `get_hz_note(note_number, tune_reference=440) -> float`

Converts a note number to frequency in Hz

Example:

```python
freq = synth.get_hz_note(57)  # 440.0Hz
```

### `get_note_number(f) -> float`

Converts a frequency in Hz to a note number

Example:

```python
n = synth.get_note_number(440.0)
```

## Caching system

When `cache=True`, `Aura` memoizes generated note arrays inside `self.arrays_bank`

The cache key includes:

- `note_hz`
- `duration`
- `velocity`
- `glide_source`

This can speed repeated operations for similar note events

## Error model

`Aura` uses `AURA_ERROR` for preset validation and synthesis errors. Typical causes include:

- invalid preset object
- missing `meta` or `master` keys
- unsupported waveform
- invalid expression
- unknown variable in formula
- circular dependency
- output node shape error
- invalid numeric ranges for portamento or tension

## Minimal practical use

```python
import soundfile as sf
from Bsound.Aura import Aura, SAMPLE_RATE, preset_example

synth = Aura(preset_example)

note = synth.get_note(
    note_hz=220.0,
    duration=2.0,
    velocity=0.9,
    gain_db=-1.0,
)

sf.write("example_note.wav", note, SAMPLE_RATE)
```

## Best practices for preset authors

- Use `oscX` / `envX` naming conventions
- Avoid variable names that match effect names or reserved terms
- Use `note_hz`, `velocity`, and `duration_progress` as the main modulation inputs
- Keep formulas readable and small
- Use portamento only when the glide effect is intentional
- Check `out` list entries to ensure each node is valid and resolves correctly

## In summary

`Aura` is a declarative synthesis interface that converts a preset into real-time audio. Its main value is that it abstracts the complexity of waveform generation, modulation, envelopes, and effects into a readable, preset-based design language. It is the high-level point where the sound designer defines the timbre and the engine turns that definition into stereo audio


