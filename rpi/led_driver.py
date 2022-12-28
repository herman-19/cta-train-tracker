from dataclasses import dataclass, field
from typing import List, Dict
import led_mappings

# https://docs.python.org/3.7/library/dataclasses.html#dataclasses.dataclass


@dataclass
class LedDriver:
    id: int
    description: str
    station_to_channel: Dict[str, int]

    def turn_on_LED(self, channel: int):
        # Calculate offset using driver.id and channel number
        # Set channel PWM to max 4095
        pwm = 4095

    def turn_off_LED(self, channel: int):
        # Calculate offset using driver.id and channel number
        # Set channel PWM to min 0
        pwm = 0


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
