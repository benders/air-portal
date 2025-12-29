#!/bin/bash -e

# Check if required utilities are available
for cmd in otf2bdf bdftopcf; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "Error: Required utility '$cmd' not found in PATH or not executable"
        echo "On macOS, install with: brew install otf2bdf bdftopcf"
        exit 1
    fi
done

# Convert a font to PCF format
#   $1 - font name (e.g., "Federation")
#   $2 - font size (e.g., 20, 96)
convert() {
    local font="$1"
    local size="$2"
    
    # 1 pixel = 1/72 inch = 1 point
    DISPLAY_DPI=72

    otf2bdf -r ${DISPLAY_DPI} -l 32_255 -p ${size} "fonts-src/${font}.ttf" -o "fonts/${font}-${size}-latin1.bdf"
    bdftopcf -o "fonts/${font}-${size}-latin1.pcf" "fonts/${font}-${size}-latin1.bdf"
    rm -f "fonts/${font}-${size}-latin1.bdf"
}

set -x
rm -f fonts/*.bdf fonts/*.pcf

convert Federation 20
convert Federation 96
