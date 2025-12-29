import time
import board
# import busio
import displayio
import os
import random

# import adafruit_adt7410
import adafruit_touchscreen
from adafruit_bitmap_font import bitmap_font

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
    standard_font = bitmap_font.load_font("/fonts/Federation-20-latin1.pcf")
    large_font = bitmap_font.load_font("/fonts/Federation-96-latin1.pcf")

    # BG_COLOR = 0xFFAA00  # Orange
    BG_COLOR = None  # Transparent
    TOP_ROW = 24
    THIRD_ROW = 180
    BOTTOM_ROW = 210

    splash = displayio.Group()
    sensor_view = displayio.Group()

    sensors_label = Label(standard_font, text="Please wait...", color=bytes(purpleair.WHITE), background_color=BG_COLOR)
    sensors_label.x = 16  # Indents the text layout
    sensors_label.y = TOP_ROW  # Slightly lower than top edge
    sensor_view.append(sensors_label)

    aqi_display = Label(large_font, text="000", color=bytes(purpleair.WHITE), background_color=BG_COLOR)
    aqi_display.x = 16  # Indents the text layout
    aqi_display.y = 100
    sensor_view.append(aqi_display)

    a_display = Label(standard_font, text="000°F", color=bytes(purpleair.WHITE), background_color=BG_COLOR)
    a_display.x = 16  # Indents the text layout
    a_display.y = THIRD_ROW
    sensor_view.append(a_display)

    c_display = Label(standard_font, text="Connecting", color=bytes(purpleair.WHITE), background_color=BG_COLOR)
    c_display.x = 16  # Indents the text layout
    c_display.y = BOTTOM_ROW
    sensor_view.append(c_display)

    b_display = Label(standard_font, text="100% RH", color=bytes(purpleair.WHITE), background_color=BG_COLOR)
    b_display.x = 320 - 16 - b_display.bounding_box[2]  # Right align
    b_display.y = THIRD_ROW
    sensor_view.append(b_display)

    d_display = Label(standard_font, text="0000 ft", color=bytes(purpleair.WHITE), background_color=BG_COLOR)
    d_display.x = 320 - 16 - d_display.bounding_box[2]  # Right align
    d_display.y = BOTTOM_ROW
    sensor_view.append(d_display)

    board.DISPLAY.root_group = splash
    display_utils.layerVisibility("show", splash, sensor_view)


    # ------------- Network Init --------------#
    pyportal.network.connect()

    if pyportal.network.is_connected:
        print("Network connected!")
        print("IP address:", pyportal.network.ip_address)
    else:
        raise RuntimeError("Network connection failed!")

    METADATA_FIELDS = ["name", "latitude", "longitude", "altitude", "model", "last_seen"]
    # AIR_QUALITY_FIELDS = ["pm2.5", "confidence", "humidity", "temperature", "pressure"]
    AIR_QUALITY_FIELDS = ["pm2.5", "temperature", "humidity", "last_seen"]

    API_KEY = os.getenv("PURPLEAIR_API_KEY")
    SENSOR_ID = os.getenv("PURPLEAIR_SENSOR_ID")

    # pyportal.network.requests.get("http://example.com")  # Warm up requests module

    # Initialize PurpleAir client with the requests library
    purpleair_client = purpleair.PurpleAirClient(pyportal.network.requests, API_KEY)

    # Fetch sensor metadata once at start
    try:
        sensor_metadata = purpleair_client.fetch_sensor_data(SENSOR_ID, METADATA_FIELDS)
        print(sensor_metadata)
        # Change the label to the sensor name
        name = sensor_metadata["sensor"]["name"]
        sensors_label.text = name

        # Update status display
        model = sensor_metadata["sensor"].get("model", "Unknown")
        c_display.text = f"{model}"

        # Altitude
        altitude = sensor_metadata["sensor"].get("altitude", "?")
        d_display.text = f"{altitude} ft"

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

                # Calculate AQI and color from PM2.5
                pm25 = sensor.get("pm2.5")
                aqi = purpleair.aqiFromPM(pm25)
                raw_color = purpleair.aqiColor(aqi)

                # Update temperature display
                temperature_f = sensor.get("temperature")
                corrected_temperature_f = purpleair.estimate_temperature(temperature_f)
                a_display.text = "{: 3.0f}°F".format(corrected_temperature_f)

                # Update humidity display on time line
                humidity = sensor.get("humidity")
                corrected_humidity = purpleair.estimate_humidity(humidity)
                b_display.text = "{:3.0f}% RH".format(humidity)

                # Set new deadline
                update_deadline = time.monotonic() + (UPDATE_INTERVAL + random.randrange(0, 30))
                print(f"Update in {update_deadline - time.monotonic()} seconds")
            except OSError as e:
                print(f"OSError while fetching sensor data: {e}")
                print("Resetting...")
                import microcontroller
                microcontroller.reset()
            except Exception as e:
                print(f"Error fetching sensor data: {type(e)}")
                print(e)
                # Set a shorter deadline for retry on error
                update_deadline = time.monotonic() + 30
                print(f"Will retry in 30 seconds\n")
                # Set blank display on error
                raw_color = purpleair.RED
                aqi = None  # Error state

        value_string = "% 3d" % aqi if aqi is not None else "ERR"
        aqi_display.text = value_string
        aqi_display.color = bytes(raw_color)

        # display_utils.layerVisibility("show", splash, sensor_view)
        time.sleep(0.1)