# Author: Martin Welgraven
# Version: 0.1.0
# Logic Node: 14649
# name: weatherstation_server
# Processes an Ecowitt protocoll string from a weatherstation API. Tested with Alecto WS5500. 
# INFO: For testing purposes a Local server is added in the Test. In the HomeServer the built-in data reception should be used. 
# DISCLAIMER: This HSL3 Framework was developed personally and independently. The company GIRA is not involved in the development or maintenance of this software.

class LogicModule:
    """Processes Ecowitt form-urlencoded payloads. Unit conversion is driven by inputs:
    in01=raw data, in02=temp (1=Celsius), in03=speed (1=km/h), in04=pressure (1=bar),
    in05=length (1=mm), in06=vpd (0=kPa, 1=hPa, 2=mbar). Values are stored by key,
    not by position, so config order and validation don't affect conversion logic.
    """

    def __init__(self, hsl3):
        self.fw = hsl3
        self.debug = self.fw.create_debug_section()
        self.input_values = []
        self.stores = []
        self.timers = []

        self.output_values = {
            'PASSKEY': 'OUT01_KEY',
            'stationtype': 'OUT02_STATION',
            'dateutc': 'OUT03_DATE',
            'tempinf': 'OUT04_TEMP_IN',
            'humidityin': 'OUT05_HUMID_IN',
            'baromrelin': 'OUT06_REL_PRESSURE',
            'baromabsin': 'OUT07_ABS_PRESSURE',
            'tempf': 'OUT08_TEMP_OUT',
            'humidity': 'OUT09_HUMID_OUT',
            'winddir': 'OUT10_WINDDIR',
            'windspeedmph': 'OUT11_WINDSPEED',
            'windgustmph': 'OUT12_WINDGUST',
            'maxdailygust': 'OUT13_MAXGUST',
            'rainratein': 'OUT14_RAIN',
            'eventrainin': 'OUT15_RAINEVENT',
            'hourlyrainin': 'OUT16_RAINHOUR',
            'dailyrainin': 'OUT17_RAINDAY',
            'weeklyrainin': 'OUT18_RAINWEEK',
            'monthlyrainin': 'OUT19_RAINMONTH',
            'yearlyrainin': 'OUT20_RAINYEAR',
            'totalrainin': 'OUT21_RAINTOTAL',
            'solarradiation': 'OUT22_SUN',
            'uv': 'OUT23_UV',
            'vpd': 'OUT24_VPD',
            'wh65batt': 'OUT25_BATT',
            'freq': 'OUT26_FREQ',
            'model': 'OUT27_MODEL'
        }


    def on_init(self, inputs, store):
        """
        Initialize the module with input connections.
        
        Processes the input dictionary to register specific input slots (IN01 through IN06).
        Filters keys to prevent duplicate processing of both indexes and identifiers.
        Checks for a valid initial value and stores it in the local input_list
        
        Args:
            inputs: Hsl3Slots object containing input slot definitions
            store: Hsl3Slots object containing the storage object for maintaining state (for this node unused)
        """

        for key in inputs.keys():
            if key in ['IN01_DATA', 'IN02_TEMP_UNIT', 'IN03_SPEED_UNIT', 'IN04_PRESSURE_UNIT', 'IN05_DEPTH_UNIT', 'IN06_VPD_UNIT']:
                value = inputs.value(key)
                if self._is_valid(key, value):
                    self.input_values.append(value)
                else:
                    msg = f"Invalid input value received for {key} : {value}"
                    self.debug.log(msg)
                    self.fw.set_output("OUT28_ERROR", msg.encode("ascii"))


    def on_calc(self, inputs):
        """
        Calculate called if any new input is received by the logic node. Validates and processes incoming data based on input keys. 
        New data on the IN01 parameter is processed always, if any other input has changed, the input is processed only if the value is valid.

        Args:
            inputs:  Hsl3Slots object containing input slot definition
        """

        if inputs.changed('IN01_DATA'):  
            self.input_values[0] = inputs.value('IN01_DATA').decode("ascii")
            self._split_input(self.input_values[0])

        for idx, key in enumerate([ 'IN02_TEMP_UNIT', 'IN03_SPEED_UNIT', 'IN04_PRESSURE_UNIT', 'IN05_DEPTH_UNIT', 'IN06_VPD_UNIT']): 
            if self._is_valid(key, inputs.value(key)):
                self.input_values[idx + 1] = inputs.value(key)
            else:
                msg = f"Invalid input value received for {key} : {inputs.value(key)}"
                self.debug.log(msg)
                self.fw.set_output('OUT28_ERROR', msg.encode("ascii"))


    def on_timer(self, timer):
        """ Left in here to show general structure of the logic module, but not used in this implementation """
        pass

    def get_input_value(self, input_index):
        """ Left in here to show general structure of the logic module, but not used in this implementation """
        pass


    def _is_valid(self, index_or_key, value) -> bool:
        valid_values = []
        if index_or_key in ['IN02_TEMP_UNIT', 'IN03_SPEED_UNIT', 'IN04_PRESSURE_UNIT', 'IN05_DEPTH_UNIT']:
            valid_values = [0, 1]
        elif index_or_key in ['IN06_VPD_UNIT']:
            valid_values = [0, 1, 2]
        else:
            valid_values = []
        
        return (value in valid_values or index_or_key in ['IN01_DATA'])


    def _split_input(self, payload):
        # Prevent processing of unexpected payloads
        if payload.count('\r\n') <= 0:
            if payload != '':
                self.debug.log(f"Payload has an unexpected format {payload}")
            return
        
        # Ignore headers and select the input message
        payload_list = payload.split( '\r\n')
        data = payload_list.pop()
        self.debug.log(f'message received with payload {payload}')
        
        # Split into a list of key=value strings and check length
        # Do not stop processing, length can be smaller due to empty battery of the outdoor weatherstation
        input_data = data.split('&')
        if len(input_data) != 27:
            msg = f"Received data has an invalid length."
            self.debug.log(msg)
            self.fw.set_output("OUT28_ERROR", msg.encode("ascii"))

        # Iterate over each parameter and process the conversions as requested
        for data_point in input_data:
            key, value = data_point.split("=")

            if key in ["tempinf", "tempf"]:
                value = self._fahrenheit_to_celsius(value)
            
            elif key in ["windspeedmph", "windgustmph", "maxdailygust"]:
                value = self._mph_to_kmh(value)
            
            elif key in ["winddir"]:
                value = self._to_winddirection(value)

            elif key in["baromrelin", "baromabsin"]:
                value = self._kpa_to_bar(value)
            
            elif key in ["vpd"]:
                if self.input_values[5] in [1, 2]:
                    kPa = float(value)
                    value = str(kPa * 10)
            
            elif key in ["rainratein", "eventrainin",  "hourlyrainin", "dailyrainin", "weeklyrainin", "monthlyrainin", "yearlyrainin", "totalrainin"]:
                value = self._inch_to_mm(value)
            
            elif key in ["dateutc"]:
                value = self._to_date_string(value)
            
            else:
                pass
            
            # Convert to bytes for output
            if isinstance(value, str):
                value = value.encode("ascii")

            if key in self.output_values.keys():
                self.fw.set_output(self.output_values[key], value)
            
    
    def _mph_to_kmh(self, value: str) -> str:
        if self.input_values[2] != 1:
            return value
        try:
            mph = float(value)
            kmh = mph * 1.60934
            return str(round(kmh, 2))
        except Exception as e:
            self.debug.log(f"Error converting from mph to km/h: {e}")
            return value

    def _kpa_to_bar(self, value: str) -> str:
        if self.input_values[3] != 1:
            return value
        try:
            hpa_value = float(value)
            bar = hpa_value * 0.0338639
            return str(round(bar, 4))
        except Exception as e:
            self.debug.log(f"Error converting from inHg: {e}")
            return value

    
    def _fahrenheit_to_celsius(self, value: str) -> str:
        if self.input_values[1] != 1:
            return value
        try:
            f_value = float(value)
            c_value = (f_value - 32) * 5.0 / 9.0
            return str(round(c_value, 2))
        except Exception as e:
            self.debug.log(f"Error converting from Fahrenheit to Celsius: {e}")
            return value

    
    def _inch_to_mm(self, value: str) -> str:
        if self.input_values[4] != 1:
            return value
        try:
            inch_value = float(value)
            mm_value = inch_value * 25.4
            return str(round(mm_value, 2))
        except Exception as e:
            self.debug.log(f"Error converting from inches to mm: {e}")
            return value
    
    
    def _to_date_string(self, value) -> str:
        from datetime import datetime, timezone
        try:
            dt_value = value.replace('+',' ')
            dt_obj = datetime.strptime(dt_value, '%Y-%m-%d %H:%M:%S')
            dt_obj = dt_obj.replace(tzinfo=timezone.utc)
            local_tz = datetime.now().astimezone().tzinfo
            dt_obj = dt_obj.astimezone(local_tz)
            return dt_obj.strftime('%d-%m-%Y %H:%M:%S')
        except Exception as e:
            self.debug.log(f"Error parsing dateutc '{value}': {e}")
            return value
        
    def _to_winddirection(self, value) -> str:
        try:
            degree = float(value)
            directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
            idx = round(degree / 22.5) % 16
            return directions[idx]
        except Exception as e:
            self.debug.log(f"Error converting wind direction: {e}")
            return value