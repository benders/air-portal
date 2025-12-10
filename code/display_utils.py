import time

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_pyportal import PyPortal

# Set visibility of layer
def layerVisibility(state, layer, target):
    try:
        if state == "show":
            time.sleep(0.1)
            layer.append(target)
        elif state == "hide":
            layer.remove(target)
    except ValueError:
        pass


# return a reformatted string with word wrapping using PyPortal.wrap_nicely
def text_box(font, target, top, string, max_chars):
    text = PyPortal.wrap_nicely(string, max_chars)
    new_text = ""
    test = ""

    for w in text:
        new_text += "\n" + w
        test += "M\n"

    text_height = Label(font, text="M", color=0x03AD31)
    text_height.text = test  # Odd things happen without this
    glyph_box = text_height.bounding_box
    target.text = ""  # Odd things happen without this
    target.y = int(glyph_box[3] / 2) + top
    target.text = new_text

