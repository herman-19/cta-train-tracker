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
        tlc5947[channel_index] = 4095

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

    def remove_old_trains(self, new_station_ids):
        to_be_removed = set(self.last_processed_station_ids).difference(set(new_station_ids))
        print("Old:", to_be_removed)
        for station_id in to_be_removed:
            for driver in self.drivers:
                if station_id in driver.station_to_channel:
                    driver.turn_off_LED(driver.station_to_channel[station_id])
        self.last_processed_station_ids = new_station_ids

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
        self.remove_old_trains(station_ids)
        for station_id in station_ids:
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
