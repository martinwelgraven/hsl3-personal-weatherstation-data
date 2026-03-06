import os
import sys

""" below intput message is received by the HomeServer (headers added by HS)
HOST: 192.168.1.2
Connection: Close
Content-Type: application/x-www-form-urlencoded
Content-Length: 477
PASSKEY=000000AC0C0C0F000000000000A00000&stationtype=EasyWeatherV1.7.5&dateutc=2026-03-05+09:56:55&tempinf=67.3&humidityin=47&baromrelin=30.245&baromabsin=30.154&tempf=51.8&humidity=76&winddir=147&windspeedmph=0.4&windgustmph=1.1&maxdailygust=6.9&rainratein=0.000&eventrainin=0.000&hourlyrainin=0.000&dailyrainin=0.000&weeklyrainin=0.000&monthlyrainin=0.000&yearlyrainin=135.969&totalrainin=135.969&solarradiation=48.63&uv=0&vpd=0.093&wh65batt=0&freq=868M&model=WS2900_V2.01.18
"""


# Ensure project root is on sys.path so we can import 'hsl3' and 'src'
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from hsl3.hsl3 import HSL3
from hsl3.hsl3_wrapper import Hsl3WrapperNode
from hsl3.hsl3_server import simple_http_server
from src.hsl3_14649_weatherstation_server import LogicModule

logic_node_name = "weatherstation_server"


def main():

    os.system('clear')
    print(" === Starting test_14649_weatherstation_server === ")
    print(" ")
    
    hsl3 = HSL3("14649_weatherstation_server")
    logic_module = LogicModule(hsl3)
    wrapper_node = Hsl3WrapperNode(ROOT_DIR, logic_node_name, logic_module)
    
    wrapper_node.set("in02", 1) # Temperature Celcius
    wrapper_node.set("in03", 1) # Speed to km/h
    wrapper_node.set("in04", 1) # Pressure to bar
    wrapper_node.set("in05", 1) # Length to mm
    wrapper_node.set("in06", 0) # Length to mm

    def set_input01(sender, headers, data):
        node_data = ''
        for key, value in headers.items():
            if node_data != '':
                node_data += '\r\n'
            node_data += f'{key}: {value}' 
        node_data += '\r\n' + data
        wrapper_node.set("in01", node_data)

    simple_http_server(set_input01 ,3005)
    # To keep the main program running (so the HTTP server continues to listen),
    # you can use a loop or wait for user input. For testing, wait for keyboard interrupt:
    
    wrapper_node.set("in01", "") # Content Type 
    
    print(" ")
    print(" === DEBUG LOG ===")
    print(" ")
    logic_module.debug.print_log()
    
    try:
        while True:
            pass  # Infinite loop to keep the program alive
    except KeyboardInterrupt:
        print("Shutting down server due to KeyboardInterrupt.")

    print(" ")
    print(" === End of Testing: 14649_weatherstation_server: OK === ")
    


if __name__ == "__main__":
    main()
