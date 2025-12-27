#!/bin/bash -e

# Check if required utilities are available
for cmd in otf2bdf bdftopcf; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: Required utility '$cmd' not found in PATH or not executable"
        echo "On macOS, install with: brew install otf2bdf bdftopcf"
        exit 1
    fi
done

# DPI set to 72 for compatibility with CircuitPython Fonts Bundle 
DISPLAY_DPI=72
FONT=Federation

set -x
rm -f fonts/${FONT}-*-latin1.bdf fonts/${FONT}-*-latin1.pcf
for size in 20 96; do
    otf2bdf -r ${DISPLAY_DPI} -l 32_255 -p ${size} "fonts-src/${FONT}.ttf" -o "fonts/${FONT}-${size}-latin1.bdf"
    bdftopcf -o "fonts/${FONT}-${size}-latin1.pcf" "fonts/${FONT}-${size}-latin1.bdf"
    rm -f "fonts/${FONT}-${size}-latin1.bdf"
done
