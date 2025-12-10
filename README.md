# Air Quality Display for Adafruit PyPortal


## Setup External libraries

```
cp /Volumes/CIRCUITPY/boot_out.txt ./
circup --path . install adafruit_pyportal adafruit_adt7410
```


## Copying to the device

```
rsync -av --cvs-exclude --exclude=.\* --delete . /Volumes/CIRCUITPY/.
```

