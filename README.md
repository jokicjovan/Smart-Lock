# Smart-Lock

## Overview
The Smart-Lock project is a secure and innovative door control system built using the ESP 8266 for internet connectivity, the ESP 32 for video streaming, and a local server running ResNet50 and VGG16 models for face recognition.

- **ESP8266**: Handles communication and Wi-Fi connectivity.
- **ESP32**: Manages video streaming for face recognition.
- **Local Server**: Runs face recognition models.

## Features
- **Unlock Methods**:
  - **RFID**: Unlock the door using an authorized RFID card.
  - **PIN Code**: Enter a PIN code via a keypad or screen.
  - **Face Recognition**: Uses a camera to capture faces for verification.

- **Security Features**:
  - Alarm after three incorrect PIN attempts.
  - Camera snapshots of unauthorized access attempts.
  - Detailed logs of unlocking attempts.
  - Notifications to owners in case of suspicious activity.

- **Display**: Shows system status and a simple user menu.

## System Activation
The system is activated when a proximity sensor detects a person near the door. The camera then captures the image and sends it to a local server for face recognition.

## Setup
### Hardware:
- **ESP 8266** (for lock manipulation)
- **ESP 32** (for video streaming)
- RFID Reader
- Keypad or screen for PIN input
- Camera (for face recognition)
- Proximity sensor
- Buzzer (alarm)
- Display

### Software:
- Arduino IDE
- Libraries for RFID, keypad, Wi-Fi, and face recognition (ResNet50 and VGG16)

## Installation
1. Clone the repository:  
   `git clone https://github.com/jokicjovan/Smart-Lock.git`

2. Install required libraries in the Arduino IDE.

3. Configure Wi-Fi credentials in the code.

4. Upload the code to the ESP modules.

5. Set up the local server for face recognition (ResNet50, VGG16).

## Usage
- **RFID**: Scan an authorized RFID card to unlock the door.
- **PIN Code**: Enter the correct PIN code on the keypad or screen.
- **Face Recognition**: The system uses the camera for face verification (if enabled).

## License
This project is licensed under the MIT License.

## Contributions
Feel free to fork the repository and submit pull requests for improvements and fixes.

## Acknowledgements
Thanks to the open-source community for providing valuable resources in building the Smart-Lock system.

## Demo
![20240124_183954](https://github.com/vukasinb7/Smart-Lock/assets/51921035/a50f6589-2bef-476e-9a25-5261436b4ac3)

### RFID Unlock
https://github.com/vukasinb7/Smart-Lock/assets/51921035/39936019-b7f6-4677-b1db-a3396ef2b5e7

### Pin Unlock
https://github.com/vukasinb7/Smart-Lock/assets/51921035/6db37615-96e7-4641-a52c-213ec19f2875

### Change Pin
https://github.com/vukasinb7/Smart-Lock/assets/51921035/9ae02323-b954-4454-9a6c-9dadcb5a535c

### Add New Face
https://github.com/vukasinb7/Smart-Lock/assets/51921035/89f61633-000a-4b69-88e4-db1149f8da9b

### Face Recognition
https://github.com/vukasinb7/Smart-Lock/assets/51921035/14e8de73-c724-4877-ab06-3ad2226fe69c

### Face Recognition Dark Mode
https://github.com/vukasinb7/Smart-Lock/assets/51921035/0f65f87c-7333-4b1f-ba6f-4f22c13cde54

## Alarm
https://github.com/vukasinb7/Smart-Lock/assets/51921035/a5415788-063d-4e4b-bac8-c0de92248742



