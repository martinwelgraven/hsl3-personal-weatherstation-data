import os
import sys
from pathlib import Path
from typing import Any, cast

""" below intput message is received by the HomeServer (headers added by HS)
POST /ecowittData HTTP/1.1
HOST: 192.168.1.2
Connection: Close
Content-Type: application/x-www-form-urlencoded
Content-Length: 476

PASSKEY=000000AC0C0C0F000000000000A00000&stationtype=EasyWeatherV1.7.5&dateutc=2026-03-05+09:56:55&tempinf=67.3&humidityin=47&baromrelin=30.245&baromabsin=30.154&tempf=51.8&humidity=76&winddir=147&windspeedmph=0.4&windgustmph=1.1&maxdailygust=6.9&rainratein=0.000&eventrainin=0.000&hourlyrainin=0.000&dailyrainin=0.000&weeklyrainin=0.000&monthlyrainin=0.000&yearlyrainin=135.969&totalrainin=135.969&solarradiation=48.63&uv=0&vpd=0.093&wh65batt=0&freq=868M&model=WS2900_V2.01.18
"""

TEST_MESSAGE = f'POST /ecowittData HTTP/1.1\r\nHOST: 192.168.1.2\r\nConnection: Close\r\nContent-Type: application/x-www-form-urlencoded\r\r\nContent-Length: 476\r\nPASSKEY=000000AC0C0C0F000000000000A00000&stationtype=EasyWeatherV1.7.5&dateutc=2026-03-05+09:56:55&tempinf=67.3&humidityin=47&baromrelin=30.245&baromabsin=30.154&tempf=51.8&humidity=76&winddir=147&windspeedmph=0.4&windgustmph=1.1&maxdailygust=6.9&rainratein=0.000&eventrainin=0.000&hourlyrainin=0.000&dailyrainin=0.000&weeklyrainin=0.000&monthlyrainin=0.000&yearlyrainin=135.969&totalrainin=135.969&solarradiation=48.63&uv=0&vpd=0.093&wh65batt=0&freq=868M&model=WS2900_V2.01.18'

# Ensure project root is on sys.path so we can import 'hsl3' and 'src'
ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src" / "hsl3_personal_weatherstation_data"

for path in (ROOT_DIR, SRC_DIR):
	if str(path) not in sys.path:
		sys.path.insert(0, str(path))

from hsl3.hsl3 import Hsl3Framework
from hsl3.hsl3_wrapper import Hsl3WrapperModule
from hsl3.hsl3_server import simple_http_server
from src.hsl3_personal_weatherstation_data.hsl3_14649_personal_weatherstation_data import LogicModule

logic_node_name = "weatherdata_ecowitt"

# ===================================
# SETTINGS FOR TESTING PURPOSES

use_server = False

# ===================================

def main():

    if sys.platform == "win32":
        os.system('cls')
    else:
        os.system('clear')
    print(" === Starting test_14649_weatherdata_ecowitt === ")
    print(" ")

    config_file = ''
    if os.path.exists(SRC_DIR / "config_host_healthcheck.json"):
        config_file = SRC_DIR / "config_host_healthcheck.json"
    elif os.path.exists(SRC_DIR / "config_host_healthcheck.yaml"):
        config_file = SRC_DIR / "config_host_healthcheck.yaml"
    else:
        raise RuntimeError("No configuration file found for host health check.")

    
    hsl3 = Hsl3Framework("14649_weatherdata_ecowitt")
    logic_module = LogicModule(hsl3)
    wrapper_node = Hsl3WrapperModule(str(config_file), cast(Any, logic_module))
    hsl3.config = wrapper_node.config

    wrapper_node.set_input_value("IN02_TEMP_UNIT", 1) # Temperature Celcius
    wrapper_node.set_input_value("IN03_SPEED_UNIT", 1) # Speed to km/h
    wrapper_node.set_input_value("IN04_PRESSURE_UNIT", 1) # Pressure to bar
    wrapper_node.set_input_value("IN05_DEPTH_UNIT", 1) # Length to mm
    wrapper_node.set_input_value("IN06_VPD_UNIT", 0) # Length to mm

    def set_input01(sender, headers, data):
        node_data = ''
        for key, value in headers.items():
            if node_data != '':
                node_data += '\r\n'
            node_data += f'{key}: {value}' 
        node_data += '\r\n' + data
        wrapper_node.set_input_value("IN01_DATA", node_data.encode("ascii"))

    simple_http_server(set_input01 ,3005)
    # To keep the main program running (so the HTTP server continues to listen),
    # you can use a loop or wait for user input. For testing, wait for keyboard interrupt:
    
    wrapper_node.set_input_value("IN01_DATA", b"")  # Trigger on_calc to process the empty input and log the keys for debugging 
    
    print(" ")
    print(" === DEBUG LOG ===")
    print(" ")
    logic_module.debug.print_log()


    if use_server:
        try:
            while True:
                pass  # Infinite loop to keep the program alive
        except KeyboardInterrupt:
            print("Shutting down server due to KeyboardInterrupt.")
    else:
        wrapper_node.set_input_value("IN01_DATA", TEST_MESSAGE.encode("ascii"))  # Trigger on_calc with the test message  
    
    print(" ")
    print(" === End of Testing: 14649_weatherdata_ecowittW: OK === ")
    


if __name__ == "__main__":
    main()
