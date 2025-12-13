#!/usr/bin/env python3
"""
PurpleAir Sensor Data Retrieval

This script queries the PurpleAir API to retrieve data from a specific sensor.
It uses the API key and sensor ID from config.yml file.
"""

import requests

WHITE = (255,255,255)
GREEN  = (0, 228, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 126, 0)
RED   = (255, 0, 0)
PURPLE = (143, 63, 151)
MAROON = (126, 0, 35)

def url_encode(string):
    encoded_string = ""
    for character in string:
        if character.isalpha() or character.isdigit():
            encoded_string += character
        else:
            encoded_string += f"%{ord(character):x}"
    return encoded_string

def fetch_sensor_data(api_key, sensor_id, field_list):
    """
    Fetch data for a specific sensor from PurpleAir API.

    Args:
        api_key (str): PurpleAir API key
        sensor_id (str or int): ID of the sensor to query
        field_list (list or str): List of fields to retrieve

    Returns:
        dict: Sensor data in JSON format
        
    Raises:
        ValueError: If field_list is not a list or string
        Exception: For API errors, network errors, or data parsing issues
    """
    base_url = "https://api.purpleair.com/v1"
    endpoint = f"/sensors/{sensor_id}"
    url = f"{base_url}{endpoint}"

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    if isinstance(field_list, list):
        fields = ','.join(field_list)
    elif isinstance(field_list, str):
        fields = field_list
    else:
        raise ValueError("field_list must be a list or a string")

    param_string = "fields=" + url_encode(fields)

    try:
        print(f"Fetching data for sensor {sensor_id}")
        response = requests.get(url + "?" + param_string, headers=headers)

        # Check if request was successful
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"API request failed with status code {response.status_code}: {response.text}"
            print(error_msg)
            raise Exception(error_msg)
    except ValueError as e:
        error_msg = f"Request error: {e}"
        print(error_msg)
        raise Exception(error_msg)
    except OSError as e:
        error_msg = f"Network error: {e}"
        print(error_msg)
        raise Exception(error_msg)
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        print(error_msg)
        raise Exception(error_msg)

# Convert US AQI from raw pm2.5 data
def aqiFromPM(pm):
    if pm == 'undefined':
        return "-"
    if not float(pm):
        return "-"
    if pm < 0:
        return pm
    if pm > 1000:
        return "-"
    """
                                        AQI   | RAW PM2.5
    Good                               0 - 50 | 0.0 – 12.0
    Moderate                         51 - 100 | 12.1 – 35.4
    Unhealthy for Sensitive Groups  101 – 150 | 35.5 – 55.4
    Unhealthy                       151 – 200 | 55.5 – 150.4
    Very Unhealthy                  201 – 300 | 150.5 – 250.4
    Hazardous                       301 – 400 | 250.5 – 350.4
    Hazardous                       401 – 500 | 350.5 – 500.4
    """

    if pm > 350.5:
        return calcAQI(pm, 500, 401, 500.4, 350.5)  # Hazardous
    elif pm > 250.5:
        return calcAQI(pm, 400, 301, 350.4, 250.5)  # Hazardous
    elif pm > 150.5:
        return calcAQI(pm, 300, 201, 250.4, 150.5)  # Very Unhealthy
    elif pm > 55.5:
        return calcAQI(pm, 200, 151, 150.4, 55.5)  # Unhealthy
    elif pm > 35.5:
        return calcAQI(pm, 150, 101, 55.4, 35.5)  # Unhealthy for Sensitive Groups
    elif pm > 12.1:
        return calcAQI(pm, 100, 51, 35.4, 12.1)  # Moderate
    elif pm >= 0:
        return calcAQI(pm, 50, 0, 12, 0)  # Good
    else:
        return 'undefined'

def aqiColor(aqi):
    if aqi > 300:
        return MAROON
    elif aqi > 200:
        return PURPLE
    elif aqi > 150:
        return RED
    elif aqi > 100:
        return ORANGE
    elif aqi > 50:
        return YELLOW
    elif aqi >= 0:
        return GREEN
    else:
        return WHITE


# Calculate AQI from standard ranges
def calcAQI(Cp, Ih, Il, BPh, BPl):
    a = (Ih - Il)
    b = (BPh - BPl)
    c = (Cp - BPl)
    return round((a / b) * c + Il)
