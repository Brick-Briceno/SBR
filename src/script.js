// ============================================
// CONFIGURACIÓN DEL PIANO ROLL
// ============================================

const canvas = document.getElementById('pianoroll-canvas');
const ctx = canvas.getContext('2d');

// Notas MIDI (C3 a C6)
const notes = [];
for (let octave = 3; octave <= 6; octave++) {
    ["1|", "2|", "3|", "4|", "5|", "6|", "7|", ].forEach(note => {
        notes.push(note + octave);
    });
}
notes.reverse(); // Notas altas arriba

const NOTE_HEIGHT = 15;
const TIME_WIDTH = 20; // Pixeles por beat
const TOTAL_BEATS = 32;
const PIANO_KEY_WIDTH = 70;

canvas.width = PIANO_KEY_WIDTH + (TOTAL_BEATS * TIME_WIDTH);
canvas.height = notes.length * NOTE_HEIGHT;

// Almacén de notas activas: {nota: 'C4', tiempo: 0, duracion: 1}
let activeNotes = [];
let autoExecuteEnabled = false;
let autoExecuteTimeout = null;

// ============================================
// DIBUJAR PIANO ROLL
// ============================================
function drawPianoRoll() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Fondo
    ctx.fillStyle = '#1e1e1e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Dibujar teclas del piano (izquierda)
    notes.forEach((note, i) => {
        const y = i * NOTE_HEIGHT;
        const isBlackKey = note.includes('#');

        ctx.fillStyle = isBlackKey ? '#0a0a0a' : '#2d2d2d';
        ctx.fillRect(0, y, PIANO_KEY_WIDTH, NOTE_HEIGHT);

        ctx.strokeStyle = '#3e3e3e';
        ctx.strokeRect(0, y, PIANO_KEY_WIDTH, NOTE_HEIGHT);

        ctx.fillStyle = isBlackKey ? '#999' : '#d4d4d4';
        ctx.font = '10px Consolas';
        ctx.fillText(note, 8, y + 11);
    });

    // Dibujar grid de tiempo
    for (let beat = 0; beat <= TOTAL_BEATS; beat++) {
        const x = PIANO_KEY_WIDTH + (beat * TIME_WIDTH);
        ctx.strokeStyle = beat % 4 === 0 ? '#555' : '#333';
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, canvas.height);
        ctx.stroke();
    }

    // Líneas horizontales
    notes.forEach((note, i) => {
        const y = i * NOTE_HEIGHT;
        ctx.strokeStyle = '#2a2a2a';
        ctx.beginPath();
        ctx.moveTo(PIANO_KEY_WIDTH, y);
        ctx.lineTo(canvas.width, y);
        ctx.stroke();
    });

    // Dibujar notas activas
    activeNotes.forEach(noteObj => {
        const noteIndex = notes.indexOf(noteObj.nota);
        if (noteIndex === -1) return;

        const x = PIANO_KEY_WIDTH + (noteObj.tiempo * TIME_WIDTH);
        const y = noteIndex * NOTE_HEIGHT;
        const width = noteObj.duracion * TIME_WIDTH;

        ctx.fillStyle = '#0e639c';
        ctx.fillRect(x + 2, y + 2, width - 4, NOTE_HEIGHT - 4);
        ctx.strokeStyle = '#1177bb';
        ctx.strokeRect(x + 2, y + 2, width - 4, NOTE_HEIGHT - 4);
    });

    updateNoteCount();
}

// ============================================
// INTERACCIÓN CON EL PIANO ROLL
// ============================================
canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (x < PIANO_KEY_WIDTH) return; // Ignorar clicks en teclas

    const noteIndex = Math.floor(y / NOTE_HEIGHT);
    const tiempo = Math.floor((x - PIANO_KEY_WIDTH) / TIME_WIDTH);
    const nota = notes[noteIndex];

    // Verificar si ya existe
    const existingIndex = activeNotes.findIndex(
        n => n.nota === nota && n.tiempo === tiempo
    );

    if (existingIndex === -1) {
        activeNotes.push({
            nota,
            tiempo,
            duracion: 1
        });
        updateStatus(`Nota añadida: ${nota} en beat ${tiempo}`);
    }

    drawPianoRoll();
});

canvas.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    if (x < PIANO_KEY_WIDTH) return;

    const noteIndex = Math.floor(y / NOTE_HEIGHT);
    const tiempo = Math.floor((x - PIANO_KEY_WIDTH) / TIME_WIDTH);
    const nota = notes[noteIndex];

    // Eliminar nota
    const existingIndex = activeNotes.findIndex(
        n => n.nota === nota && n.tiempo === tiempo
    );

    if (existingIndex !== -1) {
        activeNotes.splice(existingIndex, 1);
        updateStatus(`Nota eliminada: ${nota} en beat ${tiempo}`);
        drawPianoRoll();
    }
});

// ============================================
// FUNCIONES DE LA INTERFAZ
// ============================================
function clearPianoRoll() {
    activeNotes = [];
    drawPianoRoll();
    updateStatus('Piano roll limpiado');
}

function clearEditor() {
    document.getElementById('text-editor').value = '';
    updateStatus('Editor limpiado');
}

function updateStatus(message) {
    document.getElementById('status-text').textContent = message;
}

function updateNoteCount() {
    document.getElementById('note-count').textContent = `Notas: ${activeNotes.length}`;
}

function addOutput(message, type = 'info') {
    const outputPanel = document.getElementById('output-panel');
    const line = document.createElement('div');
    line.className = `output-line output-${type}`;

    const timestamp = new Date().toLocaleTimeString('es-ES', {
        hour12: false
    });
    line.textContent = `[${timestamp}] ${message}`;

    outputPanel.appendChild(line);
    outputPanel.scrollTop = outputPanel.scrollHeight;

    // Limitar a 100 líneas
    while (outputPanel.children.length > 101) {
        outputPanel.removeChild(outputPanel.children[1]);
    }
}

function toggleAutoExecute() {
    autoExecuteEnabled = document.getElementById('auto-execute-checkbox').checked;
    if (autoExecuteEnabled) {
        addOutput('Auto-ejecución activada', 'success');
    } else {
        addOutput('Auto-ejecución desactivada', 'info');
    }
}

// ============================================
// COMUNICACIÓN CON PYTHON (PyWebView API)
// ============================================
async function executeScript() {
    const code = document.getElementById('text-editor').value;
    if (!code.trim()) {
        updateStatus('⚠️ No hay script para ejecutar');
        return;
    }

    try {
        const result = await pywebview.api.execute_script(code);
        updateStatus('✅ Script ejecutado: ' + result.message);

        // Imprimir output
        if (result.output) {
            addOutput(result.output, result.success ? 'success' : 'error');
        } else {
            addOutput(result.message, result.success ? 'success' : 'error');
        }

        // Si Python devuelve notas, actualizar piano roll
        if (result.notes) {
            activeNotes = result.notes;
            drawPianoRoll();
        }
    } catch (error) {
        updateStatus('❌ Error: ' + error);
        addOutput('Error: ' + error, 'error');
    }
}

async function saveScript() {
    const code = document.getElementById('text-editor').value;
    try {
        const result = await pywebview.api.save_script(code);
        updateStatus('✅ Guardado: ' + result.path);
    } catch (error) {
        updateStatus('❌ Error al guardar: ' + error);
    }
}

async function loadScript() {
    try {
        const result = await pywebview.api.load_script();
        if (result.code) {
            document.getElementById('text-editor').value = result.code;
            updateStatus('✅ Script cargado');
        }
    } catch (error) {
        updateStatus('❌ Error al cargar: ' + error);
    }
}

async function exportMidi() {
    if (activeNotes.length === 0) {
        updateStatus('⚠️ No hay notas para exportar');
        return;
    }

    try {
        const result = await pywebview.api.export_midi(activeNotes);
        updateStatus('✅ MIDI exportado: ' + result.path);
    } catch (error) {
        updateStatus('❌ Error al exportar: ' + error);
    }
}

// ============================================
// AUTO-EJECUCIÓN AL ESCRIBIR
// ============================================
document.getElementById('text-editor').addEventListener('input', () => {
    if (!autoExecuteEnabled) return;

    // Debounce: esperar 500ms después de dejar de escribir
    clearTimeout(autoExecuteTimeout);
    autoExecuteTimeout = setTimeout(() => {
        executeScript();
    }, 500);
});

// ============================================
// ATAJOS DE TECLADO
// ============================================
document.addEventListener('keydown', (e) => {
    // F12: Ejecutar script
    if (e.key === 'F12') {
        e.preventDefault();
        executeScript();
        return;
    }

    // F11: Pantalla completa
    if (e.key === 'F11') {
        e.preventDefault();
        pywebview.api.toggle_fullscreen();
        return;
    }
});

// ============================================
// INICIALIZACIÓN
// ============================================
drawPianoRoll();
updateStatus('Editor listo');
addOutput('Editor inicializado', 'success');
