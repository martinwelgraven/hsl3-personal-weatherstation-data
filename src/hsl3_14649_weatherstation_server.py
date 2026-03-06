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
            'PASSKEY': 'out01',
            'stationtype': 'out02',
            'dateutc': 'out03',
            'tempinf': 'out04',
            'humidityin': 'out05',
            'baromrelin': 'out06',
            'baromabsin': 'out07',
            'tempf': 'out08',
            'humidity': 'out09',
            'winddir': 'out10',
            'windspeedmph': 'out11',
            'windgustmph': 'out12',
            'maxdailygust': 'out13',
            'rainratein': 'out14',
            'eventrainin': 'out15',
            'hourlyrainin': 'out16',
            'dailyrainin': 'out17',
            'weeklyrainin': 'out18',
            'monthlyrainin': 'out19',
            'yearlyrainin': 'out20',
            'totalrainin': 'out21',
            'solarradiation': 'out22',
            'uv': 'out23',
            'vpd': 'out24',
            'wh65batt': 'out25',
            'freq': 'out26',
            'model': 'out27'
        }


    def on_init(self, inputs, store):
        self.debug.log(f"Called on_init with keys: {inputs.keys()}")

        for key in inputs.keys():
            self._add_input(key, inputs.value(key))


    def on_calc(self, inputs):
        if inputs.changed("in01"):
            self.input_values[0] = inputs.value("in01")
            self._split_input(self.input_values[0])
        for idx, key in enumerate(inputs.keys()):
            if key != "in01" and inputs.changed(key):
                if self._is_valid(key, inputs.value(key)):
                    self.input_values[idx] = inputs.value(key)
                else:
                    msg = f"Invalid input value received for {key}"
                    self.debug.log(msg)
                    self.fw.set_output("out28", msg)

    def on_timer(self, timer):
        pass

    def get_input_value(self, input_index):
        pass


    def _add_input(self, key, value):
        if self._is_valid(key, value):
            self.input_values.append(value)
        else:
            msg = f"Invalid input value received for {key}"
            self.debug.log(msg)
            self.fw.set_output("out28", msg)


    def _is_valid(self, key, value) -> bool:
        valid_values = []
        if key in ['in02', 'in03', 'in04', 'in05']:
            valid_values = [0, 1]
        elif key in ['in06']:
            valid_values = [0, 1, 2]
        else:
            valid_values = []
        return (value in valid_values or key == 'in01')


    def _split_input(self, payload):
        cnt = payload.count('\r\n')
        if payload.count('\r\n') <= 0:
            if payload != '':
                self.debug.log(f"Payload has an unexpected format {payload}")
            return
        
        payload_list = payload.split( '\r\n')
        data = payload_list.pop()
        self.debug.log(f'message received with payload {payload}')
        
        input_data = data.split('&')

        if len(input_data) != 27:
            # Message with an invalid length can occur after firmware update or battery of the outer unit dies
            # These should be logged but not stop the data processing
            msg = "Received data has an invalid length."
            self.debug.log(f'{msg}')
            self.fw.set_output("out28", msg)

        for data_point in input_data:
            key, value = data_point.split("=")

            if key in ['tempinf', 'tempf']:
                value = self._fahrenheit_to_celsius(value)
            elif key in ['windspeedmph', 'windgustmph', 'maxdailygust']:
                value = self._mph_to_kmh(value)
            elif key in['baromrelin', 'baromabsin']:
                value = self._kpa_to_bar(value)
            elif key == 'vpd':
                if self.input_values[5] in [1, 2]:
                    kPa = float(value)
                    value = str(kPa * 10)
            elif key in ['rainratein', 'eventrainin',  'hourlyrainin', 'dailyrainin', 'weeklyrainin', 'monthlyrainin', 'yearlyrainin', 'totalrainin']:
                value = self._inch_to_mm(value)
            elif key == 'dateutc':
                value = self._to_date_string(value)
            else:
                pass
            
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
    
    
    def _to_date_string(self, value):
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