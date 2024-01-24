#define IR_USE_AVR_TIMER3
#include <IRremote.hpp>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <MFRC522.h>
#include <SPI.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Crypto.h>
#include <SHA256.h>


#define PIR_PIN D3
#define IR_RECEIVER_PIN D4
#define RFID_RST_PIN D0
#define RFID_SS_PIN D8
#define BUTTON_PIN D9
#define BUZZER_PIN D10

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

const char* ssid = "VuleSM";
const char* password = "parrotrio";
const char* mqtt_server = "192.168.1.2";

SHA256 sha256;
Hash* hash = &sha256;


WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
#define MSG_BUFFER_SIZE (50)
char msg[MSG_BUFFER_SIZE];
int value = 0;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);


IRrecv irrecv(IR_RECEIVER_PIN);
decode_results results;
String pinInput = "";
bool isPirOn = false;
bool changePinMode=false;
String newPin = "";

unsigned long lastButtonPressTime = 0;
const unsigned long debounceDelay = 1000;

byte readCard[4];
const int numOfMasterTags = 2;
String masterTagsIDs[numOfMasterTags] = { "22827021", "703FC221" };
String tagID = "";
MFRC522 mfrc522(RFID_SS_PIN, RFID_RST_PIN);

bool isAuthorized = false;
void setup() {
  Serial.begin(9600);

  pinMode(PIR_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(messageCallback);

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
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (!isAuthorized) {
    if (digitalRead(PIR_PIN) != isPirOn) {
      isPirOn = digitalRead(PIR_PIN);
      sendPirValue(isPirOn);
    }
    if (isPirOn) {
      while (scanTagID()) {
        sendTagValues(tagID);
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
          sendPinInput(pinInput);
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
    

  if (pinInput.length() > 0) {
    String pin = "";
    for (int i = 0; i < pinInput.length(); ++i) {
      pin = pin + "* ";
    }
    displayText(pin);
  }else{displayText("Unauthorized");}
  } else if (isAuthorized && !changePinMode) {
    if (IrReceiver.decode()) {
      IrReceiver.resume();
      if (!(IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT)) {
        Serial.println(IrReceiver.decodedIRData.command);
        String digit="";
        switch (IrReceiver.decodedIRData.command) {
          case 28:
            digit = "OK";
            break;
          case 13:
            digit = "#";
        }
        if (digit == "OK") {
          sendCapture();
        }
        if (digit == "#") { 
          displayText("Enter new pin");
          changePinMode=true;
        }
      }
    }
    if (digitalRead(BUTTON_PIN) == LOW) {
      if (millis() - lastButtonPressTime >= debounceDelay) {
        lastButtonPressTime = millis();
        pinInput = "";
        lockSystem();
      }
    }
  }
  else if (isAuthorized && changePinMode){
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
          if (newPin.length() == 4)
            sendNewPin(newPin);
            displayText("Authorized");
        } else if (digit == "DEL") {
          if (newPin.length() > 0)
            newPin = newPin.substring(0, newPin.length() - 1);
        } else if (digit != "") {
          if (newPin.length() < 4) {
            newPin = newPin + digit;
          }
        }

        if (newPin.length() > 0) {
          String pin = "";
          for (int i = 0; i < newPin.length(); ++i) {
            pin = pin + "* ";
          }
          displayText(pin);
        }
      }
    }
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
void setup_wifi() {

  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}
void sendPirValue(bool value) {
  JsonDocument doc;
  doc["action"] = "pir";
  doc["state"] = isPirOn;
  String msg = "";
  serializeJson(doc, msg);
  Serial.println(msg);
  client.publish("FromLock", msg.c_str());
}
void sendPinInput(String pinInput) {
  JsonDocument doc;
  doc["action"] = "pinUnlock";
  doc["pin"] = calculateSHA256(pinInput);
  String msg = "";
  serializeJson(doc, msg);
  client.publish("FromLock", msg.c_str());
}

void sendNewPin(String pinInput) {
  JsonDocument doc;
  doc["action"] = "newPin";
  doc["pin"] = calculateSHA256(pinInput);
  String msg = "";
  serializeJson(doc, msg);
  newPin="";
  changePinMode=false;
  client.publish("FromLock", msg.c_str());
}
void sendTagValues(String cardInput) {
  JsonDocument doc;
  doc["action"] = "tagUnlock";
  doc["tag"] = calculateSHA256(tagID);
  String msg = "";
  serializeJson(doc, msg);
  Serial.println(msg);
  client.publish("FromLock", msg.c_str());
}
void lockSystem() {
  JsonDocument doc;
  doc["action"] = "lock";
  String msg = "";
  serializeJson(doc, msg);
  Serial.println(msg);
  client.publish("FromLock", msg.c_str());
}
void sendCapture() {
  JsonDocument doc;
  doc["action"] = "capture";
  String msg = "";
  serializeJson(doc, msg);
  Serial.println(msg);
  client.publish("FromLock", msg.c_str());
}


void messageCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  JsonDocument doc;
  deserializeJson(doc, payload);
  if (!doc["capture"].isNull()) {
    if (doc["capture"] == "done") {
      displayText("Face added!");
      delay(3000);
      displayText("Authorized");
    }
    if (doc["capture"] == "fail") {
      displayText("Error! TryAgain!");
      delay(3000);
      displayText("Authorized");
    }

  } else {
    isAuthorized = doc["authorized"] == true;
    Serial.println(isAuthorized);
    if (isAuthorized) {
      displayText("Authorized");
    } else {
      displayText("UnAuthorized");
    }
  }
  pinInput = "";
}
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe("ToLock");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

String calculateSHA256(String data) {
  uint8_t value[32];
  hash->reset();
  hash->update(data.c_str(), strlen(data.c_str()));
  hash->finalize(value, sizeof(value));
  String result = "";
  for (size_t i = 0; i < 32; i++) {
    result += String(value[i], HEX);
  }
  Serial.println(result);
  return result;
}
