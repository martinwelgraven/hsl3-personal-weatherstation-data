# hsl3-weatherdata-ecowitt

A logic node for the GIRA HomeServer for ecowitt weather data processing. This receives and processes Ecowitt formatted weather data, making it accessible within the Gira automation ecosystem. The data is received by the HomeServer through a IP/KNX telegrams (receive) arrangement.
In this repository is a Python framework for building HSL3 (HomeServer Logic 3) modules for Gira HomeServer / Facility Server included. This is developed via [GiraHS HSL3 Development Framework](https://github.com/martinwelgraven/girahs-hsl3)

## Features

- **Weather Data Integration**: Parse Ecowitt and Wunderground weather station data formats
- **Unit Conversion**: Support for multiple unit systems (Celsius/Fahrenheit, km/h/mph, bar/hPa, mm/inch)

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Usage](#usage)
- [HSL3 Concepts](#hsl3-concepts)
- [Data Formats](#data-formats)
- [Testing](#testing)
- [License](#license)

## Installation

### Requirements

- Python 3.9 or higher
- No external dependencies required (uses Python standard library)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd hsl3-weatherdata-ecowitt
```

2. The project is ready to use—no additional package installation needed. All code is self-contained within the `hsl3/` directory.

## Quick Start

### Basic Server Example

```python
from hsl3.hsl3 import HSL3
from hsl3.hsl3_server import simple_http_server
from src.hsl3_14649_weatherdata_ecowitt import LogicModule

# Create HSL3 instance
hsl3 = HSL3("14649_weatherdata_ecowitt")

# Create logic module from configuration
logic_module = LogicModule(hsl3)

# Start HTTP server on port 8080
server, thread = simple_http_server(callback=logic_module.process_data, port=8080)

# Server runs in background thread
# Send weather data via POST to http://localhost:8080/ecowittData
```

### Running the Example

```bash
python tests/test_14649_weatherdata_ecowitt.py
```

This will start the server and allow you to send test weather data.

## Project Structure

```
hsl3/                              # Core HSL3 framewor
│
src/                               # Generated logic modules
├── config_weatherdata_ecowitt.json        # Weather data configuration
├── hsl3_14649_weatherdata_ecowitt.py      # Generated logic module
├── 14649_weatherdata_ecowitt.hsl          # HSL3 source (if applicable)
└── log14649.html                          # Html information file
│
tests/                             # Test suite
└── test_14649_weatherdata_ecowitt.py     # Example test and server demo
```

### Ecowitt Weather Station Format

The server accepts HTTP POST requests with URL-encoded weather data from Ecowitt weather stations:

```
POST /ecowittData HTTP/1.1
Content-Type: application/x-www-form-urlencoded

PASSKEY=000000AC0C0C0F000000000000A00000
&stationtype=EasyWeatherV1.7.5
&dateutc=2026-03-05+09:56:55
&tempinf=67.3
&humidityin=47
&baromrelin=30.245
&baromabsin=30.154
&tempf=51.8
&humidity=76
&winddir=147
&windspeedmph=0.4
&windgustmph=1.1
&maxdailygust=6.9
&rainratein=0.000
&dailyrainin=0.023
&solarradiation=48.63
&uv=0
&vpd=0.093
&model=WS2900_V2.01.18
```

#### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `PASSKEY` | string | Authentication key |
| `stationtype` | string | Weather station model |
| `dateutc` | string | UTC timestamp |
| `tempf` / `tempinf` | float | Temperature (Fahrenheit) |
| `humidity` / `humidityin` | int | Humidity percentage (0-100) |
| `windspeedmph` | float | Wind speed (mph) |
| `windgustmph` | float | Wind gust (mph) |
| `winddir` | int | Wind direction (0-360°) |
| `baromrelin` | float | Relative barometric pressure |
| `baromabsin` | float | Absolute barometric pressure |
| `rainratein` | float | Current rain rate |
| `dailyrainin` | float | Daily rainfall |
| `solarradiation` | float | Solar radiation intensity |
| `uv` | int | UV index |
| `vpd` | float | Vapor Pressure Deficit |

### Unit Conversion

Configure unit preferences via configuration inputs. The module supports:

- **Temperature**: Celsius (1) or Fahrenheit (0)
- **Wind Speed**: km/h (1) or mph (0)
- **Pressure**: bar (1) or hPa (0)
- **Rainfall**: mm (1) or inch (0)
- **Vapor Pressure**: mbar (2), hPa (1), or kPa (0)

## Testing

### Running Tests

```bash
python tests/test_14649_weatherdata_ecowitt.py
```

### Test Configuration

Inside the test file, you can enable/disable the HTTP server:

```python
use_server = False  # Set to True to start HTTP server during tests
```

### Testing Your Custom Module

1. Create a test configuration matching your `LogicModule`
2. Instantiate the module: `logic_module = LogicModule(hsl3)`
3. Call process methods with sample data
4. Verify outputs using `hsl3.outputs` dictionary

Example:

```python
from hsl3.hsl3 import HSL3
from src.your_logic_module import LogicModule

hsl3 = HSL3("your_module_id")
logic = LogicModule(hsl3)

# Simulate input data
logic.process_data(headers, "param1=value1&param2=value2")

# Check outputs
assert hsl3.outputs["OUT01_KEY"] == "expected_value"
```

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please ensure:

- Code follows the existing structure and naming conventions
- JSON configurations are properly formatted and validated
- Tests pass before submitting pull requests
- New features include corresponding documentation

## Additional Resources

- [Gira HomeServer Documentation](https://www.gira.de/) (official Gira resources)
- [Ecowitt Weather Station Documentation](https://www.ecowitt.net/)
- Python standard library: `http.server`, `json`, `threading`, `urllib.parse`

## Support

For issues or questions:

1. Check existing issues on the repository
2. Review configuration examples in `src/`
3. Run tests to isolate problems
4. Enable debug output using HSL3 debug sections