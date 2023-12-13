#include <IRremote.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <MFRC522.h>
#include <SPI.h>

#define PIR_PIN D3
#define IR_RECEIVER_PIN D4
#define RFID_RST_PIN D0
#define RFID_SS_PIN D8
#define BUTTON_PIN D9

#define SCREEN_WIDTH 128  // OLED display width, in pixels
#define SCREEN_HEIGHT 64  // OLED display height, in pixels
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

IRrecv irrecv(IR_RECEIVER_PIN);
decode_results results;
String pinRes = "8854";
String pinInput = "";

byte readCard[4];
const int numOfMasterTags = 2;
String masterTagsIDs[numOfMasterTags] = {"22827021", "703FC221"};
String tagID = "";
MFRC522 mfrc522(RFID_SS_PIN, RFID_RST_PIN);

bool isAuthorized = false;

void setup() {
  Serial.begin(9600);
  pinMode(PIR_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT);

  IrReceiver.begin(IR_RECEIVER_PIN, false);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {  // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for (;;)
      ;
  }
  delay(2000);
  displayText("Unauthorized");

  SPI.begin();
  mfrc522.PCD_Init();
}

void loop() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    isAuthorized = false;
    pinInput = "";
  }

  if (!isAuthorized) {
    if (digitalRead(PIR_PIN) == HIGH) {
      while (scanTagID()) {
        bool isTagAuthorized = false;
        for (int i = 0; i < numOfMasterTags; ++i) {
          if (tagID == masterTagsIDs[i]) {
            isTagAuthorized = true;
            break;
          }
        }
        isAuthorized = isTagAuthorized;
        pinInput = "";
      }
    }

    if (IrReceiver.decode()) {
      IrReceiver.resume();
      if (!(IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT)) {
        String digit = "";
        switch (IrReceiver.decodedIRData.command) {
          case 69:
            digit = "1";
            break;
          case 70:
            digit = "2";
            break;
          case 71:
            digit = "3";
            break;
          case 68:
            digit = "4";
            break;
          case 64:
            digit = "5";
            break;
          case 67:
            digit = "6";
            break;
          case 7:
            digit = "7";
            break;
          case 21:
            digit = "8";
            break;
          case 9:
            digit = "9";
            break;
          case 25:
            digit = "0";
            break;
          case 28:
            digit = "OK";
            break;
          case 8:
            digit = "DEL";
            break;
        }
        if (digit == "OK") {
          if (pinInput == pinRes) {
            isAuthorized = true;
          }
          pinInput = "";
        } else if (digit == "DEL") {
          if (pinInput.length() > 0)
            pinInput = pinInput.substring(0, pinInput.length() - 1);
        } else if (digit != "") {
          if (pinInput.length() < 4) {
            pinInput = pinInput + digit;
          }
        }
      }
    }
  }
  if (pinInput.length() > 0) {
    String pin = "";
    for (int i = 0; i < pinInput.length(); ++i) {
      pin = pin + "* ";
    }
    displayText(pin);
  } else if (isAuthorized) {
    displayText("Authorized");
  } else {
    displayText("Unauthorized");
  }
}


void displayText(String text) {
  int16_t x1;
  int16_t y1;
  uint16_t width;
  uint16_t height;

  display.getTextBounds(text, 0, 0, &x1, &y1, &width, &height);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor((SCREEN_WIDTH - width) / 2, (SCREEN_HEIGHT - height) / 2);
  display.println(text);
  display.display();
}


boolean scanTagID() {
  if (!mfrc522.PICC_IsNewCardPresent()) {
    return false;
  }
  if (!mfrc522.PICC_ReadCardSerial()) {
    return false;
  }
  tagID = "";
  for (uint8_t i = 0; i < 4; i++) {
    tagID.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  tagID.toUpperCase();
  mfrc522.PICC_HaltA();
  return true;
}