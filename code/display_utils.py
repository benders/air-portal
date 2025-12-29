import time

import board

from adafruit_display_text.label import Label
from adafruit_pyportal import PyPortal

SCREEN_WIDTH = board.DISPLAY.width
SCREEN_HEIGHT = board.DISPLAY.height

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
def text_box(target, top, string, max_chars):
    text = PyPortal.wrap_nicely(string, max_chars)
    new_text = ""
    test = ""

    for w in text:
        new_text += "\n" + w
        test += "M\n"

    text_height = Label(target.font, text="M", color=0x03AD31)
    text_height.text = test  # Odd things happen without this
    glyph_box = text_height.bounding_box
    target.text = ""  # Odd things happen without this
    target.y = int(glyph_box[3] / 2) + top
    target.text = new_text


def new_label(font, x_pos: str, y: int, placeholder_text: str, background_color: tuple[int, int, int] | None = None) -> Label:
    label = Label(
        font,
        text=placeholder_text,
        color=bytes((255,255,255)),
        background_color=background_color
    )
    if x_pos == "left":
        label.x = 16
    elif x_pos == "right":
        label.x = SCREEN_WIDTH - 16 - label.bounding_box[2]
    else:
        raise ValueError("x_pos must be 'left' or 'right'")
    
    label.y = y
    return label