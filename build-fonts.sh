#!/bin/bash -ex

DISPLAY_DPI=72

FONT=Federation
rm -f fonts/${FONT}-*-latin1.bdf fonts/${FONT}-*-latin1.pcf
for size in 20 96; do
    otf2bdf -r ${DISPLAY_DPI} -l 32_255 -p ${size} "fonts-src/${FONT}.ttf" -o "fonts/${FONT}-${size}-latin1.bdf"
    bdftopcf -o "fonts/${FONT}-${size}-latin1.pcf" "fonts/${FONT}-${size}-latin1.bdf"
    rm -f "fonts/${FONT}-${size}-latin1.bdf"
done
