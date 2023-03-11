# vr-passthrough-sound-localization
- Direction of Arrival
## Hardware
Respeaker 4-Mic Array: https://github.com/SeeedDocument/ReSpeaker-4-Mic-Array-for-Raspberry-Pi

## Installation Guide
### Microphone
1. Mount Respeaker onto Raspberry Pi
2. Get Seed voice card source code + install all relevant drivers: https://gitlab.ethz.ch/aweichbrodt/seeed-voicecard. 
Use `sudo ./install.sh --compat-kernel`
3. Get and install ODAS library: https://github.com/introlab/odas
4. Fine tune configuration file
5. Use ODAS Web for visualization: https://github.com/introlab/odas_web


## How to run
### Socket_server.py
TODO:

## Architecture
TODO: 
## Sample Output
JSON File
{
"sounds":
  [
    {
      "direction": 
        {"x": 0.388, "y": 0.364, "z": 0.847},
        "type": "VOICE"
    }
  ]
}
