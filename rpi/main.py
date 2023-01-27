import time

# import json
# https://www.pythoncheatsheet.org/modules/json-module
from cta_api import fetch_approaching_trains
from led_driver import MainDriversController

def test_line_leds(mc, line):
    mc.turn_line_on(line)
    time.sleep(2)
    mc.turn_line_off(line)

def test_all_lines_leds(mc):
    test_line_leds(mc, "red")
    test_line_leds(mc, "green")
    test_line_leds(mc, "orange")
    test_line_leds(mc, "pink")
    test_line_leds(mc, "blue")
    test_line_leds(mc, "brown")
    test_line_leds(mc, "purple")
    test_line_leds(mc, "yellow")

if __name__ == "__main__":
    mainController = MainDriversController()
    while True:
        # Poll API every 15 seconds.
        app_trains = fetch_approaching_trains()
        mainController.process_approaching_trains(app_trains)
        time.sleep(15)

        # TODO: Update server to use comma-separated requests to Locaions API.
        #       This will enable this application to sleep 5 seconds instead of 15 seconds and keep under 50,000 transaction limit.
        #       More up to date LEDs.
        # Instead of following 2 requests for blue and red...
        #     https://lapi.transitchicago.com/api/1.0/ttpositions.aspx?key=7bea3c1b04b344f18f1ec4a3a3eb7d95&rt=blue&outputType=JSON
        #     https://lapi.transitchicago.com/api/1.0/ttpositions.aspx?key=7bea3c1b04b344f18f1ec4a3a3eb7d95&rt=red&outputType=JSON
        # Use...
        #     https://lapi.transitchicago.com/api/1.0/ttpositions.aspx?key=7bea3c1b04b344f18f1ec4a3a3eb7d95&rt=blue,red&outputType=JSON
