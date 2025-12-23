import time
import board
# import busio
import displayio
import os
import random

# import adafruit_adt7410
import adafruit_touchscreen

# from analogio import AnalogIn

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
    # light_sensor = AnalogIn(board.LIGHT)
    # try:
    #     # attempt to init. the temperature sensor
    #     i2c_bus = busio.I2C(board.SCL, board.SDA)
    #     adt = adafruit_adt7410.ADT7410(i2c_bus, address=0x48)
    #     adt.high_resolution = True
    # except ValueError:
    #     # Did not find ADT7410. Probably running on Titano or Pynt
    #     adt = None

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

    # from font_orbitron_light_webfont_18_latin1 import FONT as orbitron_font
    from font_junction_regular_24_latin1 import FONT as standard_font
    from font_junction_bold_72_latin1 import FONT as large_font
    # from font_league_spartan_medium_18_latin1 import FONT as spartan_font
    
    # Set the font and preload letters
    # font = bitmap_font.load_font("/fonts/Helvetica-Bold-16.bdf")
    # font.load_glyphs(b"abcdefghjiklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890- ()")

    splash = displayio.Group()
    sensor_view = displayio.Group()

    sensors_label = Label(standard_font, text="Please wait...", color=bytes(purpleair.WHITE))
    sensors_label.x = TABS_X + 16  # Indents the text layout
    sensors_label.y = TABS_Y + 16  # Slightly lower than top edge
    sensor_view.append(sensors_label)

    aqi_display = Label(large_font, text="Loading...", color=bytes(purpleair.WHITE))
    aqi_display.x = TABS_X + 16  # Indents the text layout
    aqi_display.y = 120
    sensor_view.append(aqi_display)

    # display_utils.text_box(
    #     sensors_label,
    #     TABS_Y,
    #     "Please wait...",
    #     40,
    # )

    board.DISPLAY.root_group = splash
    display_utils.layerVisibility("show", splash, sensor_view)


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

    # Initialize PurpleAir client with the requests library
    purpleair_client = purpleair.PurpleAirClient(pyportal.network.requests, API_KEY)

    # Fetch sensor metadata once at start
    try:
        sensor_metadata = purpleair_client.fetch_sensor_data(SENSOR_ID, METADATA_FIELDS)
        print(sensor_metadata)
        # Change the label to the sensor name
        name = sensor_metadata["sensor"]["name"]
        display_utils.text_box(
            sensors_label,
            TABS_Y,
            name,
            40,
        )
    except Exception as e:
        print(f"Error fetching sensor metadata: {e}")
        # Continue with the program even if we can't get the initial metadata

    UPDATE_INTERVAL = 120  # seconds
    update_deadline = 0 # Force immediate update on first loop

    # ------------- Code Loop ------------- #
    while True:
        # touch = ts.touch_point
        # light = light_sensor.value
        # sensor_data.text = "Touch: {}\nLight: {}\nTemp: {:.0f}°F".format(
        #     touch, light, get_temperature(adt)
        # )

        if time.monotonic() >= update_deadline:
            try:
                sensor_response = purpleair_client.fetch_sensor_data(SENSOR_ID, AIR_QUALITY_FIELDS)
                print(sensor_response)
                sensor = sensor_response.get("sensor", {})
                pm25 = sensor.get("pm2.5")
                aqi = purpleair.aqiFromPM(pm25)
                raw_color = purpleair.aqiColor(aqi)

                # Set new deadline
                update_deadline = time.monotonic() + (UPDATE_INTERVAL + random.randrange(0, 30))
                print(f"Update in {update_deadline - time.monotonic()} seconds")
            except OSError as e:
                print(f"OSError while fetching sensor data: {e}")
                print("Resetting...")
                import microcontroller
                microcontroller.reset()
            except Exception as e:
                print(f"Error fetching sensor data: {e}")
                # Set a shorter deadline for retry on error
                update_deadline = time.monotonic() + 30
                print(f"Will retry in 30 seconds")
                # Set blank display on error
                raw_color = purpleair.RED
                aqi = None  # Blank display

        value_string = "%3d" % aqi if aqi is not None else "no data"  # Blank if aqi is None (error)
        aqi_display.text = value_string
        aqi_display.color = bytes(raw_color)

        # display_utils.layerVisibility("show", splash, sensor_view)
        time.sleep(0.1)