#include <IRremote.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define PIR_PIN D3
#define IR_RECEIVER_PIN D4

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

void setup()
{
  Serial.begin(9600);
  pinMode(PIR_PIN, INPUT);
  IrReceiver.begin(IR_RECEIVER_PIN);

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { // Address 0x3D for 128x64
    Serial.println(F("SSD1306 allocation failed"));
    for(;;);
  }
  delay(2000);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(20, 30);
  display.println("Sportski pozdrav!");
  display.display(); 
}

void loop() {
  // if(digitalRead(PIR_PIN)==HIGH) {
  //   Serial.println("Movement detected.");
  // } else {
  //   Serial.println("Did not detect movement.");
  // }

  // if(IrReceiver.decode()){ 
  //   Serial.println(IrReceiver.decodedIRData.decodedRawData , HEX);
  //   IrReceiver.resume();
  // }
}