import json
from enums.watchdog_battery_config_enum import WatchdogBatteryConfigEnum
from enums.watchdog_state_enum import WatchdogStateEnum


class WatchdogAppServer:
    def __init__(self, watchdog=None, last_seen=None, state=WatchdogStateEnum.OK.value,
                 battery_config=WatchdogBatteryConfigEnum.NORMAL.value, active=False):
        self.watchdog = watchdog
        self.last_seen = last_seen
        self.state = state
        self.battery_config = battery_config
        self.active = active

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
