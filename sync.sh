#!/bin/bash -e

# Determine target path based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    TARGET="/Volumes/CIRCUITPY"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Try common Linux mount points
    if [ -d "/mnt/CIRCUITPY" ]; then
        TARGET="/mnt/CIRCUITPY"
    elif [ -d "/run/media/$USER/CIRCUITPY" ]; then
        TARGET="/run/media/$USER/CIRCUITPY"
    elif [ -d "/media/$USER/CIRCUITPY" ]; then
        TARGET="/media/$USER/CIRCUITPY"
    else
        echo "Error: Cannot find CIRCUITPY mount point"
        echo "Please specify the mount point manually or ensure the device is mounted"
        exit 1
    fi
else
    echo "Error: Unsupported OS type: $OSTYPE"
    exit 1
fi

# Check if target exists
if [ ! -d "$TARGET" ]; then
    echo "Error: Target directory $TARGET does not exist"
    exit 1
fi

# Check if target is a mount point
if [[ "$OSTYPE" == "darwin"* ]]; then
    # On macOS, check if it's in the mount output
    if ! mount | grep -q " on $TARGET "; then
        echo "Error: $TARGET is not a mount point"
        exit 1
    fi
else
    # On Linux, use mountpoint command
    if ! mountpoint -q "$TARGET" 2>/dev/null; then
        echo "Error: $TARGET is not a mount point"
        exit 1
    fi
fi

# Check if target is writable
if [ ! -w "$TARGET" ]; then
    echo "Error: $TARGET is not writable"
    exit 1
fi

# Check if boot_out.txt exists
if [ ! -f "$TARGET/boot_out.txt" ]; then
    echo "Error: $TARGET/boot_out.txt does not exist"
    echo "This may not be a valid CircuitPython device"
    exit 1
fi

echo "All safety checks passed. Syncing to $TARGET ..."
sync
rsync -rvc --cvs-exclude --exclude=.\* --exclude=boot_out.txt --exclude=__pycache__ --delete . "$TARGET/."
sync
