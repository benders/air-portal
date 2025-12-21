## TODO: Pull air-quality data

Air quality data will be pulled from the PurpleAir API. It should always be displayed using AQI, including standard color based on AQI levels, so that a person can see it quickly at a glance.

TODOs:
* Run loop should fetch update from purpleair only if the data is stale (2 minutes)
* Show the old data if new data is unable to be fetched for up to 10 minutes. Show an error if it is older than that.
* Along with AQI in large numbers, the outside temperature and other interesting weather data should be displayed in the normal font.
* Display Wifi logo and SSID name during connection
* Figure out why label text is offset from top
* Create larger font for AQI
* Display age of displayed data in small text at bottom?

## Work in progress