from tkinter.scrolledtext import ScrolledText
from pathlib import Path
from tkinter import ttk
import tkinter as tk
import numpy as np
import threading
import queue
import pygame
import json
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from Bsound.Aura import Aura, SAMPLE_RATE


NOTE_HZ = 261.626
NOTE_DURATION = 2
AUTOPLAY_DELAY_MS = 1

DEFAULT_PRESET = """
{
        "meta": {
            "version": "1.0.0",
            "name": "Sweet Little Sound",
            "description": "This is a test sound",
            "author": "Brick Briceño",
            "category": "Bass",
            "tags": [
                "resampling",
                "distorted",
                "sub"
            ]
        },
        "master": {
            "master_gain_db": -0.1,
            "legato": true,
            "glide": true,
            "portamento": 0.045,
            "portamento_tension": 0,
            "effects": {
                "optical_compressor": {
                    "peak_reduction": 50.0,
                    "gain": 50.0,
                    "ratio": 5
                },
                "drive": {
		    "gain_db": 6
                }
            }
        },
        "data": {
            "osc1": {
                "waveform": "triangle",
                "frequency": "note_hz + vibrato",
                "amplitude": "velocity * env1 * vibrato",
                "stretch": 3,
                "duration": "duration",
                "effects": {
                    "drive": {
                        "gain_db": 6,
                        "normalize": true
                    }
                }
            },
            "vibrato": {
                "waveform": "triangle",
                "frequency": 8,
                "amplitude": "duration_progress * 2",
                "stretch": 0,
                "duration": "duration"
            },
            "env1": {
                "DAHDSR_envelope": {
                    "delay": 0,
                    "attack": 0.25,
                    "hold": 0.2,
                    "decay": 0.6,
                    "sustain_level": 0.03,
                    "sustain": 0.01,
                    "release": 1.2,
                    "attack_tension": 0,
                    "decay_tension": -0.25,
                    "release_tension": 0.25
                }
            }
        },
        "out": [
            "osc1"
        ]
    }

"""


BACKGROUND = "#101419"
PANEL = "#181e24"
FOREGROUND = "#dce5e8"
MUTED = "#91a0a6"
GRID = "#303a41"
TRACE = "#29d7b0"
ACCENT = "#167c68"


class SignalPlot(tk.Canvas):
    def __init__(self, master, mode):
        super().__init__(
            master,
            background=PANEL,
            highlightthickness=1,
            highlightbackground=GRID,
        )
        self.mode = mode
        self.values = None
        self.detail = ""
        self.hover_callback = None
        self._hover_x = None
        self._hover_x_values = None
        self._hover_y_values = None
        self.bind("<Configure>", self.redraw)
        self.bind("<Motion>", self._on_mouse_motion)
        self.bind("<Leave>", self._on_mouse_leave)

    def set_data(self, values, detail):
        self.values = values
        self.detail = detail
        self.redraw()

    def set_hover_callback(self, callback):
        self.hover_callback = callback

    def _on_mouse_motion(self, event):
        if self.hover_callback is None or self._hover_x is None:
            return

        width = self.winfo_width()
        height = self.winfo_height()
        left, right, top, bottom = 48, width - 16, 18, height - 30
        if not (left <= event.x <= right and top <= event.y <= bottom):
            self.hover_callback("")
            return

        index = int(np.argmin(np.abs(self._hover_x - event.x)))
        x_value = self._hover_x_values[index]
        y_value = self._hover_y_values[index]
        if self.mode == "wave":
            message = f"Waveform · {x_value:.4f} s · {y_value:+.4f}"
        else:
            message = f"Spectrum · {x_value:.2f} Hz · {y_value:.1f} dB"
        self.hover_callback(message)

    def _on_mouse_leave(self, _event=None):
        if self.hover_callback is not None:
            self.hover_callback("")

    def redraw(self, _event=None):
        self.delete("all")
        self._hover_x = None
        self._hover_x_values = None
        self._hover_y_values = None
        width = self.winfo_width()
        height = self.winfo_height()
        left, right, top, bottom = 48, width - 16, 18, height - 30
        if right <= left or bottom <= top:
            return

        for fraction in (0.25, 0.5, 0.75):
            y = top + fraction * (bottom - top)
            self.create_line(left, y, right, y, fill=GRID)
        for fraction in (0.25, 0.5, 0.75):
            x = left + fraction * (right - left)
            self.create_line(x, top, x, bottom, fill=GRID)
        self.create_line(left, bottom, right, bottom, fill=MUTED)
        self.create_line(left, top, left, bottom, fill=MUTED)

        if self.values is None:
            return

        if self.mode == "wave":
            count = min(self.values.size, 1200)
            if count < 2:
                return
            indices = np.linspace(0, self.values.size - 1, count, dtype=np.int32)
            samples = np.clip(self.values[indices], -1.0, 1.0)
            points = []
            self._hover_x = np.linspace(left, right, count)
            self._hover_x_values = indices / SAMPLE_RATE
            self._hover_y_values = samples
            for index, sample in enumerate(samples):
                x = self._hover_x[index]
                y = top + (1.0 - (sample + 1.0) / 2.0) * (bottom - top)
                points.extend((x, y))
            self.create_text(
                6, top, text="1", fill=MUTED, anchor="w"
            )
            self.create_text(
                6, (top + bottom) / 2, text="0", fill=MUTED, anchor="w"
            )
            self.create_text(
                6, bottom, text="-1", fill=MUTED, anchor="w"
            )
            self.create_line(*points, fill=TRACE, width=2, smooth=False)
            self.create_text(
                right, height - 8, text="time →", fill=MUTED, anchor="se"
            )
            return

        frequencies, levels = self.values
        visible = (frequencies >= 20) & (frequencies <= 16000)
        frequencies = frequencies[visible]
        levels = levels[visible]
        if frequencies.size == 0:
            return
        if frequencies.size > 1800:
            indices = np.linspace(
                0, frequencies.size - 1, 1800, dtype=np.int32
            )
            frequencies = frequencies[indices]
            levels = levels[indices]
        points = []
        self._hover_x = left + (
            (np.log10(frequencies) - np.log10(20))
            / (np.log10(16000) - np.log10(20))
        ) * (right - left)
        self._hover_x_values = frequencies
        self._hover_y_values = levels
        for index, (frequency, level) in enumerate(zip(frequencies, levels)):
            x = self._hover_x[index]
            y = bottom - np.clip(level + 80, 0, 80) / 80 * (bottom - top)
            points.extend((x, y))
        for frequency in (20, 100, 1000, 8000, 16000):
            x = left + (
                (np.log10(frequency) - np.log10(20))
                / (np.log10(16000) - np.log10(20))
            ) * (right - left)
            self.create_text(
                x, height - 8, text=f"{frequency:g}", fill=MUTED, anchor="s"
            )
        for decibels in (0, -40, -80):
            y = bottom - (decibels + 80) / 80 * (bottom - top)
            self.create_text(
                left - 5, y, text=str(decibels), fill=MUTED, anchor="e"
            )
        if len(points) >= 4:
            self.create_line(*points, fill=TRACE, width=2, smooth=False)


class AuraScopeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aura Scope")
        self.root.geometry("1320x840")
        self.root.minsize(800, 560)
        self.root.configure(background=BACKGROUND)
        self.root.state("zoomed")

        self.autoplay = tk.BooleanVar(value=False)
        self._autoplay_job = None
        self._generation = 0
        self._results = queue.Queue()
        self._current_sound = None
        self._closing = False
        self._build_ui()
        self.root.bind("<Control-p>", self._on_play_shortcut)
        self.root.bind("<Control-P>", self._on_play_shortcut)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(40, self._poll_results)
        self.root.after(150, self.play_note)

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TFrame", background=BACKGROUND
        )
        style.configure(
            "Panel.TFrame", background=PANEL
        )
        style.configure(
            "TLabel", background=BACKGROUND, foreground=FOREGROUND
        )
        style.configure(
            "Panel.TLabel", background=PANEL, foreground=FOREGROUND
        )
        style.configure(
            "Status.TLabel", background=PANEL, foreground=MUTED
        )
        style.configure(
            "ErrorStatus.TLabel", background=PANEL, foreground="#ff8a80"
        )
        style.configure(
            "StatusBar.TLabel", background=PANEL, foreground=FOREGROUND
        )
        style.configure(
            "TCheckbutton", background=BACKGROUND, foreground=FOREGROUND
        )
        style.map(
            "TCheckbutton",
            background=[("active", BACKGROUND)],
            foreground=[("active", FOREGROUND)],
        )
        style.configure(
            "Play.TButton",
            background=ACCENT,
            foreground="#ffffff",
            padding=(14, 8),
            font=("TkDefaultFont", 10, "bold"),
        )
        style.map(
            "Play.TButton",
            background=[("active", "#20977e"), ("disabled", "#36413f")],
        )

        toolbar = ttk.Frame(self.root, padding=(14, 12, 14, 8))
        toolbar.pack(fill="x")
        ttk.Label(
            toolbar,
            text="AURA SCOPE by @Brick_briceno",
            font=("TkDefaultFont", 17, "bold"),
        ).pack(side="left", padx=(0, 28))
        self.play_button = ttk.Button(
            toolbar,
            text="▶  Play  (Ctrl+P)",
            style="Play.TButton",
            command=self.play_note,
        )
        self.play_button.pack(side="left")
        self.copy_button = ttk.Button(
            toolbar,
            text="Copy SBR preset",
            command=self.copy_preset,
        )
        self.copy_button.pack(side="left", padx=(8, 0))
        ttk.Checkbutton(
            toolbar,
            text="Play on edit",
            variable=self.autoplay,
            command=self._toggle_autoplay,
        ).pack(side="left", padx=18)

        self.status = tk.StringVar(value="Ready")
        self._status_message = "Ready"
        self._status_is_error = False
        status_bar = tk.Frame(
            self.root,
            background=PANEL,
            relief="sunken",
            borderwidth=1,
            height=32,
        )
        status_bar.pack(side="bottom", fill="x", padx=14, pady=(0, 10))
        status_bar.pack_propagate(False)
        ttk.Label(
            status_bar,
            text="STATUS",
            style="StatusBar.TLabel",
            font=("TkDefaultFont", 9, "bold"),
        ).pack(side="left", padx=(10, 8))
        self.status_label = ttk.Label(
            status_bar,
            textvariable=self.status,
            style="Status.TLabel",
            anchor="w",
        )
        self.status_label.pack(side="left", fill="both", expand=True, padx=6)

        content = ttk.Panedwindow(self.root, orient="horizontal")
        content.pack(fill="both", expand=True, padx=14, pady=(2, 8))

        editor_panel = ttk.Frame(content, style="Panel.TFrame", padding=10)
        graph_panel = ttk.Frame(content, padding=(12, 0, 0, 0))
        content.add(editor_panel, weight=2)
        content.add(graph_panel, weight=3)
        ttk.Label(
            editor_panel, text="Aura Preset (JSON)", style="Panel.TLabel"
        ).pack(anchor="w", pady=(0, 8))
        self.editor = ScrolledText(
            editor_panel,
            wrap="none",
            undo=True,
            font=("Consolas", 10),
            background="#11171c",
            foreground=FOREGROUND,
            insertbackground=TRACE,
            selectbackground="#24584e",
            relief="flat",
            padx=10,
            pady=10,
        )
        self.editor.pack(fill="both", expand=True)
        self.editor.insert("1.0", DEFAULT_PRESET)
        self.editor.edit_modified(False)
        self.editor.bind("<<Modified>>", self._on_editor_change)

        graph_panel.rowconfigure(0, weight=1)
        graph_panel.rowconfigure(1, weight=1)
        graph_panel.columnconfigure(0, weight=1)
        self.wave_plot, self.wave_info = self._make_plot_section(
            graph_panel, "Waveform", "Full note", 0
        )
        self.spectrum_plot, self.spectrum_info = self._make_plot_section(
            graph_panel, "Spectrum", "20-16000 Hz · logarithmic scale", 1
        )
        self.wave_plot.set_hover_callback(self._on_plot_hover)
        self.spectrum_plot.set_hover_callback(self._on_plot_hover)

    def copy_preset(self):
        try:
            preset = json.loads(self.editor.get("1.0", "end-1c"))
            preset_text = Aura(preset, cache=False).get_SBR_string_preset
            self.root.clipboard_clear()
            self.root.clipboard_append(preset_text)
            self.root.update_idletasks()
            self._set_status("SBR preset copied to clipboard")
        except Exception as exc:
            self._set_status(
                f"Could not copy preset: {exc}",
                is_error=True,
            )

    def _set_status(self, message, is_error=False):
        single_line_message = "; ".join(str(message).splitlines())
        self._status_message = single_line_message
        self._status_is_error = is_error
        self._show_status(single_line_message, is_error)

    def _on_plot_hover(self, message):
        if message:
            self._show_status(message)
        else:
            self._show_status(self._status_message, self._status_is_error)

    def _show_status(self, message, is_error=False):
        self.status.set(message)
        self.status_label.configure(
            style="ErrorStatus.TLabel" if is_error else "Status.TLabel"
        )

    @staticmethod
    def _make_plot_section(parent, title, detail, row):
        section = ttk.Frame(parent)
        section.grid(row=row, column=0, sticky="nsew", pady=(0, 8))
        section.rowconfigure(2, weight=1)
        section.columnconfigure(0, weight=1)
        ttk.Label(section, text=title, font=("TkDefaultFont", 11, "bold")).grid(
            row=0, column=0, sticky="w", pady=(2, 3)
        )
        info = ttk.Label(section, text=detail, foreground=MUTED)
        info.grid(row=1, column=0, sticky="w", pady=(0, 5))
        plot = SignalPlot(section, mode="wave" if row == 0 else "spectrum")
        plot.grid(row=2, column=0, sticky="nsew")
        return plot, info

    def _on_play_shortcut(self, _event):
        self.play_note()
        return "break"

    def _toggle_autoplay(self):
        if not self.autoplay.get() and self._autoplay_job is not None:
            self.root.after_cancel(self._autoplay_job)
            self._autoplay_job = None

    def _on_editor_change(self, _event=None):
        if not self.editor.edit_modified():
            return
        self.editor.edit_modified(False)
        if not self.autoplay.get():
            return
        if self._autoplay_job is not None:
            self.root.after_cancel(self._autoplay_job)
        self._autoplay_job = self.root.after(
            AUTOPLAY_DELAY_MS, self._play_after_edit
        )

    def _play_after_edit(self):
        self._autoplay_job = None
        if self.autoplay.get():
            self.play_note()

    def play_note(self):
        self._generation += 1
        generation = self._generation
        preset_text = self.editor.get("1.0", "end-1c")
        self.play_button.configure(state="disabled")
        self._set_status("Rendering...")
        threading.Thread(
            target=self._render_note,
            args=(generation, preset_text),
            daemon=True,
        ).start()

    def _render_note(self, generation, preset_text):
        try:
            preset = json.loads(preset_text)
            audio = Aura(preset, cache=False).get_note(
                note_hz=NOTE_HZ,
                duration=NOTE_DURATION,
                velocity=0.8,
                gain_db=-0.1,
            )
            audio = np.asarray(audio, dtype=np.float32)
            if audio.ndim != 2 or audio.shape[1] != 2 or not audio.size:
                raise ValueError("Aura did not return a valid stereo signal.")
            if not np.isfinite(audio).all():
                raise ValueError("The signal contains non-finite values.")

            mono = audio.mean(axis=1)
            wave = mono.copy()

            window = np.hanning(mono.size)
            fft_size = mono.size * 4
            spectrum = np.abs(np.fft.rfft(mono * window, n=fft_size))
            spectrum /= max(float(window.sum()), 1.0)
            spectrum *= 2
            frequencies = np.fft.rfftfreq(fft_size, 1 / SAMPLE_RATE)
            levels = 20 * np.log10(np.maximum(spectrum, 1e-8))
            peak_index = int(np.argmax(spectrum))
            peak_hz = float(frequencies[peak_index])
            peak_db = float(levels[peak_index])
            self._results.put(
                (
                    generation,
                    audio,
                    wave,
                    frequencies,
                    levels,
                    peak_hz,
                    peak_db,
                    None,
                )
            )
        except Exception as exc:
            self._results.put((generation, None, None, None, None, 0, 0, str(exc)))

    def _poll_results(self):
        while True:
            try:
                result = self._results.get_nowait()
            except queue.Empty:
                break
            self._show_result(*result)
        if not self._closing:
            self.root.after(40, self._poll_results)

    def _show_result(
        self,
        generation,
        audio,
        wave,
        frequencies,
        levels,
        peak_hz,
        peak_db,
        error,
    ):
        if generation != self._generation:
            return
        if error is not None:
            self._set_status(f"Preset error: {error}", is_error=True)
            self.play_button.configure(state="normal")
            return

        self.wave_plot.set_data(
            wave,
            f"Full note · {len(wave) / SAMPLE_RATE:.2f} s · "
            f"{SAMPLE_RATE:,} Hz",
        )
        self.spectrum_plot.set_data(
            (frequencies, levels),
            f"20–16000 Hz · log scale · peak: {peak_hz:.2f} Hz · {peak_db:.1f} dB",
        )
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(
                    frequency=SAMPLE_RATE, size=-16, channels=2, buffer=512
                )
            pcm = np.clip(audio, -1, 1)
            pcm = (pcm * 32767).astype(np.int16)
            self._current_sound = pygame.mixer.Sound(buffer=pcm.tobytes())
            self._current_sound.play()
            self._set_status(
                f"Playing {NOTE_HZ:.3f} Hz · "
                f"{len(audio) / SAMPLE_RATE:.2f} s · spectral peak {peak_hz:.2f} Hz"
            )
        except Exception as exc:
            self._set_status(
                f"Signal generated, but playback failed: {exc}",
                is_error=True,
            )
        self.play_button.configure(state="normal")

    def close(self):
        self._closing = True
        if self._autoplay_job is not None:
            self.root.after_cancel(self._autoplay_job)
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        self.root.destroy()


def main():
    root = tk.Tk()
    AuraScopeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
