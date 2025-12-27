# Air Quality Display for Adafruit PyPortal


## Setup External libraries

```
cp /Volumes/CIRCUITPY/boot_out.txt ./

circup bundle-add adafruit/circuitpython-fonts # You only need to do this once

circup --path . install -r circup-requirements.txt
```


## Copying to the device

```
./sync.sh
```

