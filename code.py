import time
import board
import busio
import displayio
import os

import adafruit_adt7410
import adafruit_touchscreen

from analogio import AnalogIn

from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from adafruit_pyportal import PyPortal

from code import display_utils
from code import purpleair

# ------------- Functions ------------- #

def get_temperature(source):
    if source:  # Only if we have the temperature sensor
        celsius = source.temperature
        return (celsius * 1.8) + 32

#
# Initialize, then run forever
#

if __name__ == "__main__":
    pyportal = PyPortal(
        status_neopixel=board.NEOPIXEL
    )

    # ------------- Inputs and Outputs Setup ------------- #
    light_sensor = AnalogIn(board.LIGHT)
    try:
        # attempt to init. the temperature sensor
        i2c_bus = busio.I2C(board.SCL, board.SDA)
        adt = adafruit_adt7410.ADT7410(i2c_bus, address=0x48)
        adt.high_resolution = True
    except ValueError:
        # Did not find ADT7410. Probably running on Titano or Pynt
        adt = None

    # ------------- Screen Setup ------------- #
    # pyportal.set_background("/pyportal_startup.bmp")  # Display an image until the loop starts

    display = board.DISPLAY
    display.rotation = 0

    # Default Label styling
    TABS_X = 0
    TABS_Y = 0

    # Touchscreen setup
    # ------Rotate 0:
    screen_width = 320
    screen_height = 240
    ts = adafruit_touchscreen.Touchscreen(board.TOUCH_XL, board.TOUCH_XR,
                                        board.TOUCH_YD, board.TOUCH_YU,
                                        calibration=((5200, 59000), (5800, 57000)),
                                        size=(screen_width, screen_height))

    # ---------- Text Boxes ------------- #
    # Set the font and preload letters
    font = bitmap_font.load_font("/fonts/Helvetica-Bold-16.bdf")
    font.load_glyphs(b"abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()")

    splash = displayio.Group()
    sensor_view = displayio.Group()

    sensors_label = Label(font, text="Data View", color=0x03AD31)
    sensors_label.x = TABS_X
    sensors_label.y = TABS_Y
    sensor_view.append(sensors_label)

    sensor_data = Label(font, text="Data View", color=0x03AD31)
    sensor_data.x = TABS_X + 16  # Indents the text layout
    sensor_data.y = 150
    sensor_view.append(sensor_data)

    display_utils.text_box(
        font,
        sensors_label,
        TABS_Y,
        "This screen can display sensor readings.",
        40,
    )

    board.DISPLAY.root_group = splash

    # ------------- Network Init --------------#
    pyportal.network.connect()

    if pyportal.network.is_connected:
        print("Network connected!")
        print("IP address:", pyportal.network.ip_address)
    else:
        raise RuntimeError("Network connection failed!")

    METADATA_FIELDS = ["name", "latitude", "longitude", "altitude", "last_seen"]
    # AIR_QUALITY_FIELDS = ["pm2.5", "confidence", "humidity", "temperature", "pressure"]
    AIR_QUALITY_FIELDS = ["pm2.5", "last_seen"]

    API_KEY = os.getenv("PURPLEAIR_API_KEY")
    SENSOR_ID = os.getenv("PURPLEAIR_SENSOR_ID")

    pyportal.network.requests.get("http://example.com")  # Warm up requests module

    try:
        sensor_metadata = purpleair.fetch_sensor_data(pyportal.network.requests, API_KEY, SENSOR_ID, METADATA_FIELDS)
        print(sensor_metadata)
    except Exception as e:
        print(f"Error fetching sensor metadata: {e}")
        # Continue with the program even if we can't get the initial metadata


    # ------------- Code Loop ------------- #
    while True:
        touch = ts.touch_point
        light = light_sensor.value
        sensor_data.text = "Touch: {}\nLight: {}\nTemp: {:.0f}°F".format(
            touch, light, get_temperature(adt)
        )

        display_utils.layerVisibility("show", splash, sensor_view)
        time.sleep(0.1)