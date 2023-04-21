from configparser import ConfigParser
import os


DEFAULT_UDP_IP = "192.168.0.101"
DEFAULT_UDP_PORT = "7777"
DEFAULT_LEDS_NUM = "42"
DEFAULT_LEDS_BRIGHTNESS = "255"

class PickerConfigs(ConfigParser):
    def __init__(self, name):
        ConfigParser.__init__(self)

        self.config_path = os.path.join(os.getcwd(), name)

        self["settings"] = {
            "default_udp_ip": DEFAULT_UDP_IP,
            "default_udp_port": DEFAULT_UDP_PORT, 
            "default_leds_count": DEFAULT_LEDS_NUM,
            "default_leds_brightness": DEFAULT_LEDS_BRIGHTNESS,
        }

    def create(self):
        if not os.path.isfile(self.config_path):
            with open(self.config_path, 'w+') as f:
                self.write(f)
            print("Config File created.")
        else:
            print("Config already exists.")