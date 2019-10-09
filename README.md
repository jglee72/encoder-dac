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
- Alternate Pin for "main" encoder can now be changed via argument list (see encoder.py --help)


# MCP4725 DAC Drivers
Need to install Adafruit_Python_MCP4725.git with the instructions provided below.
UPDATE: this git includes all the necessary files to get up and running.  Skip to
"this is how I setup a new RPi 4"

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

# Help Files and Command Line Arguments

Added a few helpful ways to use alternate pins for the main controller.  May update to have 
any encoder changes.  Also good for running in DEBUG mode.  See below:

    root@raspberrypi:/home/pi/gpio# python encoder.py --help
    usage: encoder.py [-h] [-d] [-i INPUT INPUT INPUT] [-r RESOLUTION] [-b BUTTON]
                      [-e ENCODER]

    Take incremental encoders to output analog voltage via ADC

    optional arguments:
      -h, --help            show this help message and exit
      -d, --debug           Output inline debug comments
      -i INPUT INPUT INPUT, --input INPUT INPUT INPUT
                            change main encoder pins A B and PB associated RPI
                            pins (BCM numbering), eg -i 5 6 13. Expects 3
                            arguments
      -r RESOLUTION, --resolution RESOLUTION
                            Resolution of main encoder (range 0-200).
                            Resolution/4096 x 5V (Default 10= [12mV/enc detent])
      -b BUTTON, --button BUTTON
                            Button Bouncetime in mS (range 0-1000). Ignores noise
                            and button bounce (default: 300)
      -e ENCODER, --encoder ENCODER
                            Encoder Bouncetime in mS (range 0-100). Ignores noise
                            and encoder errors (default: 30)
    root@raspberrypi:/home/pi/gpio#
