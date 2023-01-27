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
        app_trains = fetch_approaching_trains()
        mainController.process_approaching_trains(app_trains)
        time.sleep(5)
