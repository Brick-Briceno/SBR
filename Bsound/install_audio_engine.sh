#!/bin/bash

# Ensure we're in the correct directory
cd audio_engine

# Install dependencies if needed
# cargo add cpal

# Terminate any running Rust processes
if command -v taskkill &> /dev/null; then
    # Windows con Git Bash
    cmd //c "taskkill /F /IM rust-analyzer.exe /T 2>nul"
    cmd //c "taskkill /F /IM cargo.exe /T 2>nul"
else
    # Linux/macOS
    pkill -f rust-analyzer || true
    pkill -f cargo || true
fi

# Check platform
lib_extension=".so"
if [[ "$OSTYPE" == "msys" ]]; then
    lib_extension=".dll"
elif [[ "$OSTYPE" == "win32" ]]; then
    lib_extension=".dll"
elif [[ "$OSTYPE" == "cygwin" ]]; then
    lib_extension=".dll"    
fi

# Build the audio engine
cargo build --release


# Move the compiled library to the parent directory
rm "../audio_engine$lib_extension"
mv "target/release/audio_engine$lib_extension" "../audio_engine$lib_extension"

cd ..

# Optional: clean up build artifacts
# cargo clean
