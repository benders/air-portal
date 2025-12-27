# Air Quality Display for Adafruit PyPortal


## Setup External libraries

```
cp /Volumes/CIRCUITPY/boot_out.txt ./

circup --path . install -r circup-requirements.txt
```


## Copying to the device

```
./sync.sh
```

## Freezing circup libs

```
circup --path . freeze -r && mv requirements.txt circup-requirements.txt
```
