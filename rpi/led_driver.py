from dataclasses import dataclass, field
from typing import List, Dict
import board
import busio
import digitalio
import led_mappings

import adafruit_tlc5947

# Initialize SPI bus
spi = busio.SPI(clock=board.SCLK, MOSI=board.MOSI)

# Initialize TLC5947
DRIVER_COUNT = 8  # change this to the number of drivers you have chained
LATCH = digitalio.DigitalInOut(board.D5)
tlc5947 = adafruit_tlc5947.TLC5947(spi, LATCH, num_drivers=DRIVER_COUNT)

@dataclass
class LedDriver:
    id: int
    description: str
    station_to_channel: Dict[str, int]

    def turn_on_LED(self, channel: int):
        # Set channel PWM to max 4095
        channel_index = self.id * 24 + int(channel)
        tlc5947[channel_index] = 512

    def turn_off_LED(self, channel: int):
        # Set channel PWM to min 0
        channel_index = self.id * 24 + int(channel)
        tlc5947[channel_index] = 0


@dataclass
class MainDriversController:
    drivers: List[LedDriver] = field(
        default_factory=lambda: [
            LedDriver(0, "Board 0", led_mappings.led_driver_0_channels),
            LedDriver(1, "Board 1", led_mappings.led_driver_1_channels),
            LedDriver(2, "Board 2", led_mappings.led_driver_2_channels),
            LedDriver(3, "Board 3", led_mappings.led_driver_3_channels),
            LedDriver(4, "Board 4", led_mappings.led_driver_4_channels),
            LedDriver(5, "Board 5", led_mappings.led_driver_5_channels),
            LedDriver(6, "Board 6", led_mappings.led_driver_6_channels),
            LedDriver(7, "Board 7", led_mappings.led_driver_7_channels),
        ]
    )
    last_processed_station_ids: List[str] = field(default_factory=lambda: [])

    def process_stations(self, new_station_ids):
        stations_to_be_shut_off = list(set(self.last_processed_station_ids) - set(new_station_ids))
        stations_to_be_turned_on = list(set(new_station_ids) - set(self.last_processed_station_ids))
        # print("Previous:", self.last_processed_station_ids)
        # print("New:", new_station_ids)
        # print("To Be Removed:", stations_to_be_shut_off)
        # print("New Trimmed:", stations_to_be_turned_on)
        for station_id in stations_to_be_shut_off:
            for driver in self.drivers:
                if station_id in driver.station_to_channel:
                    driver.turn_off_LED(driver.station_to_channel[station_id])
        self.last_processed_station_ids = new_station_ids
        return stations_to_be_turned_on

    def get_station_ids(self, approaching_trains):
        stations = []
        for key in approaching_trains:
            if approaching_trains[key] is not None:
                for train in approaching_trains[key]:
                    station = train["nextStaId"] + "_" + key.lower()
                    stations.append(station)
        return stations

    def process_approaching_trains(self, approaching_trains):
        station_ids = self.get_station_ids(approaching_trains)
        new_station_ids = self.process_stations(station_ids)
        # print("New Stations:", new_station_ids)
        for station_id in new_station_ids:
            for driver in self.drivers:
                if station_id in driver.station_to_channel:
                    print(
                        station_id,
                        "found in Driver",
                        driver.id,
                        ". Station:",
                        driver.station_to_channel[station_id],
                    )
                    driver.turn_on_LED(driver.station_to_channel[station_id])
                    break

    def turn_line_on(self, color):
        for driver in self.drivers:
            for key in driver.station_to_channel:
                if color in key:
                   driver.turn_on_LED(driver.station_to_channel[key])

    def turn_line_off(self, color):
        for driver in self.drivers:
            for key in driver.station_to_channel:
                if color in key:
                   driver.turn_off_LED(driver.station_to_channel[key])
