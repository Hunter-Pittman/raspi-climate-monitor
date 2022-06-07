from sense_hat import SenseHat
from os.path import exists
from datetime import datetime
import configparser
import time
import seqlog
import logging

seqlog.set_global_log_properties(
    Application="ClimateMonitor"
)

sense = SenseHat()
config = configparser.ConfigParser()

sense.clear()

config_loc = "/home/pi/sensehat_climate_monitor.conf"

# Handle if the config listed in config_loc does not exists
conf_exists = exists(config_loc)
if (conf_exists == False):
        print("The configuration file does not exist in the default location, creating a default config...")
        config['temperature_config'] = {'TEMP_WARN': '90.0', 'TEMP_ALERT': '95.0'}
        config['humidity_config'] = {'HUMIDITY_WARN': '10.0', 'HUMIDITY_ALERT': '70.0' }
        config['temperature_sensor_offset'] = {'TEMP_OFFSET': '19.0'}
        with open('config_loc', 'w') as configfile:
                config.write(configfile)

# Reads the config file for this program and stores values in script variables
config.read(config_loc)

temp_warn_threshold = float(config['temperature_config']['TEMP_WARN'])
temp_alert_threshold = float(config['temperature_config']['TEMP_ALERT'])

humidity_warn_threshold = float(config['humidity_config']['HUMIDITY_WARN'])
humidity_alert_threshold = float(config['humidity_config']['HUMIDITY_ALERT'])

temp_offset = float(config['temperature_sensor_offset']['TEMP_OFFSET'])

# Checks for conflicting configuration
if (temp_warn_threshold >= temp_alert_threshold or humidity_warn_threshold >= humidity_alert_threshold):
        msg = "WARNING! Your configuration has errors most likely casued by the alert threshold being lower than the warn threshold. Correct this issue and rerun the program."
        sense.show_message("WARNING! Config has errors")
        exit



def send_to_seq(temp):
    seqlog.log_to_seq(
        server_url=[YOUR SERVER IP/URL HERE],
        api_key=[YOUR API KEY HERE],
        level=logging.INFO,
        batch_size=10,
        auto_flush_timeout=10,  # seconds
        override_root_logger=True,
    )

    logging.info("Generic Server Room Temperature: {temp}", temp=temp)

def get_temp():
        sense.clear()
        temp = sense.temperature
        fahrenheit_temp = round(temp_to_fahrenheit(temp), 1)

        if (fahrenheit_temp >= temp_warn_threshold and fahrenheit_temp <= (temp_alert_threshold - 0.1)):
            sense.show_message(str(fahrenheit_temp), text_colour=[255, 255, 0])
        if (fahrenheit_temp >= temp_alert_threshold):
            sense.show_message(str(fahrenheit_temp), text_colour=[255, 0, 0])
        else:
            sense.show_message(str(fahrenheit_temp), text_colour=[0, 255, 0])

        print(fahrenheit_temp)
        send_to_seq(fahrenheit_temp)

def temp_to_fahrenheit(temp):
        temp = temp / 5 * 9 + 32 - temp_offset
        return temp


def main():
        while True:
                get_temp()
                time.sleep(60)

main()
