# encoder-dac
Translate a rotary encoder to an analog value with a Raspberry Pi and an MCP4725 DAC
Installation. 

# Hardware Setup:
## MCP4725 DAC 
- 12-Bit ADC, I2C communiction
- Standard addressn 0x62
- Connect to SDA and SCL to RPI SDA(), and SCL()
- Connect to 5V and GND of RPI via wiring on a perf board (3.3V optional)

## Rotary Encoder
- Mechanical or Optical Quadrature (grey-code) encoders can be used.
- Optional push button is monitored via any available pins
- if a seperate button is used make sure pin is defined in file


# MCP4725 DAC Drivers
Need to install Adafruit_Python_MCP4725.git with the instructions provided below.

It is unknown why the following repository is considered "Archived" in lieu of circuit python. 
In the attempts to become "simpler" it seems to have become very complex to get simple ADC project
up and running using Circuit Python.  

## To install the library from source (recommended) run the following commands on a Raspberry Pi or other Debian-based OS system:
### This is from archive directory:
    sudo apt-get install git build-essential python-dev
    cd ~
    git clone https://github.com/adafruit/Adafruit_Python_MCP4725.git
    cd Adafruit_Python_MCP4725
    sudo python setup.py install

### This is how I setup a new RPi 4:
    cd /home/pi
    git clone https://github.com/jglee72/encoder-dac.git
    cd Adafruit_Python_MCP4725
    sudo python setup.py install
    cd ..
    python endcoder.py
