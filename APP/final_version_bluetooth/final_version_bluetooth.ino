#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoBLE.h>


#include "HX711.h"

HX711 scale;

uint8_t dataPin = 4;
uint8_t clockPin = 5;

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 32 // OLED display height, in pixels

// Declaration for SSD1306 display connected using I2C
#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

BLEService myService("00001234-0000-1000-8000-00805f9b34fb");  // create service
BLEIntCharacteristic myCharacteristic("0000ABCD-0000-1000-8000-00805f9b34fb", BLERead | BLEWrite);

//all the pins
const int redPin1 = 13; // RGB LED 1 red
const int redPin2 = 10; // RGB LED 1 red
const int bluePin1 = 12; // RGB LED 1 blue
const int bluePin2 = 9; // RGB LED 1 red
const int greenPin1 = 11; // RGB LED 1 green
const int greenPin2 = 8; // RGB LED 1 green
const int switchPin = 6; //switch
const int buzzerPin = 7; // buzzer

// all variables
float dailyGoal = 2000; // from Iwos code
unsigned long massBottle = 0; // retrieved from calibration unit
unsigned long mass_OLD = 0; //retrieved from calibration unit
unsigned long mass_NEW = 0;
unsigned long drunkAmount = 0;
int displayFilled = 0;
unsigned long lastDrinkingMoment = 0;
unsigned long noBottleMoment = 0;
bool reminderOn = false;
bool reminderState = false;
bool measure = true;
bool calibrate = true; //from Iwos code.


void setup() {
  Serial.begin(9600); // Serial communication

  // RGB LEDs and buzzer pins are OUTPUT and switch is INPUT
  pinMode(redPin1, OUTPUT); 
  pinMode(bluePin1, OUTPUT);
  pinMode(greenPin1, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(switchPin, INPUT_PULLUP); 

  // initialize the OLED object
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }
  display.clearDisplay();
  display.display();
  scale.begin(dataPin, clockPin);
  //number that follows from prior calibration.
  scale.set_scale(-44);   
  // reset the scale to zero = 0, this means the mass of the scale, which is always present, is 0.
  scale.tare(20);
  digitalWrite(buzzerPin, LOW);
  setColor (0,0,0);

  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }
  BLE.setLocalName("HydromateBLE");
  BLE.setAdvertisedService(myService);
  myService.addCharacteristic(myCharacteristic);
  BLE.addService(myService);
  myCharacteristic.writeValue(0);
  BLE.advertise();

}
void loop() { 
  Serial.println(scale.get_units(1));
  if (calibrate==true){//calibration unit is only executed if calibrate is set to true.
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(WHITE);
    display.setCursor(0, 0);
    display.print("Remove your \nbottle from Hydromate");
    display.display(); 
    delay(5000);
    scale.tare(20);
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 2);
    display.print("Place your EMPTY \nbottle on Hydromate.");
    display.display();
    delay(5000);
    massBottle=scale.get_units(1); //massBottle is defined here
    Serial.println(massBottle);
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    display.print("Place your FILLED \nbottle on hydromate");
    display.display();
    delay(10000);
    mass_OLD=scale.get_units(1)-massBottle; //mass_OLD is defined here
    Serial.println(mass_OLD);
    display.clearDisplay();
    display.setTextSize(1);
    display.setCursor(0, 0);
    mass_NEW=mass_OLD;
    if ((mass_OLD<0) || (massBottle<50) || (mass_OLD>3000) || (massBottle>3000)) {
      display.clearDisplay();
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.print("Calibration failed, \n try again");
      display.display();
      calibrate=true;
      delay(5000);
    }
    else {
      display.clearDisplay();
      display.setTextSize(1);
      display.setCursor(0, 0);
      display.print("Calibration \nsuccesful!");
      display.display();
      lastDrinkingMoment=millis();
      calibrate=false;
      delay(3000);
    }
  }



  if (scale.get_units(1)>massBottle){ //mass is measured only once if and only if the bottle is on the station. 
    if (measure == true){ //block is only executed once after placing back bottle.
     digitalWrite(buzzerPin, LOW); 
      reminderState=false;
      setColor (0,0,0);
      delay(5000); 
      mass_NEW=scale.get_units(1)-massBottle; //used for amount and reminder calculations.
      Serial.println(mass_NEW);
      measure=false;
      noBottleMoment=0;
      
    }
  }
  if ((scale.get_units(1)<massBottle) && (calibrate == false)){ 
    if (noBottleMoment == 0){ //if bottle is not on station, after 2 seconds LED colors red (resetted when placed back).
      noBottleMoment=millis();
      }
    if (((millis()-noBottleMoment) > 2000) && (noBottleMoment != 0) ){ //&& digitalRead(switchPin == LOW)
      setColor(255,0,0); 
    }
    if (measure == false){ //scale is tared again once, 5 seconds after removing bottle.
      setColor(0,0,0);
      digitalWrite(buzzerPin, LOW);
      delay(5000);
      scale.tare(20);
      measure=true;
        }
  }

  
  

  if (mass_NEW<(mass_OLD-50) && (calibrate == false) && (mass_OLD-mass_NEW<5000)) { //If mass has decreased, add to amount and reset reminder timer.
    drunkAmount+=(mass_OLD-mass_NEW);
    lastDrinkingMoment=millis();
    Serial.print("You have drunk, drunkAmount is [ml] = ");
    Serial.println(drunkAmount);
  }

  if (((millis()-lastDrinkingMoment)>15000) && (drunkAmount<dailyGoal)){ //if reminder timer is longer than 15s, start procedure.
    reminderState=true;
  }

  if ((reminderState==true) && (scale.get_units(1)>massBottle)) {
    // in reminderState, turn on light every 2s for 0.5 with blue light
    if ( ((millis() - lastDrinkingMoment) % 2000) < 500 && digitalRead(switchPin) == LOW) {
        setColor(0,255,0);
        digitalWrite(buzzerPin, HIGH); 
      
          reminderOn = true;
        }
    else {
      if (reminderOn == true) {
          reminderOn = false;
          setColor(0,0,0);
          digitalWrite(buzzerPin, LOW); 
        }
      }
       
    
  }
  if (drunkAmount < dailyGoal) {
      displayFilled = drunkAmount / dailyGoal * 114;
      }
      else {
        displayFilled = 114;
      }
  display.clearDisplay(); //always output to screen.
  display.fillRect(0,0,120,32,WHITE); //outline of the battery
  display.fillRect(2,2,116,28, BLACK);
  display.fillRect(120,8,10,16, WHITE); // small rectangle at top battery
  display.fillRect(3,4,displayFilled,24,WHITE); //filling battery
  display.drawLine(22,2,22,28,BLACK); 
  display.drawLine(42,2,42,28,BLACK);
  display.drawLine(62,2,62,28,BLACK);
  display.drawLine(82,2,82,28,BLACK);
  display.drawLine(102,2,102,28,BLACK);
  display.display();
  mass_OLD=mass_NEW;

  BLEDevice central = BLE.central();
  if (central) {
      Serial.print("Connected to central: ");
      Serial.println(central.address());
      while (central.connected()) {
          myCharacteristic.writeValue(drunkAmount);
      }
      Serial.print("Disconnected from central: ");
      Serial.println(central.address());
  }

}

void setColor(int redValue, int greenValue, int blueValue) {
  analogWrite(redPin1, redValue);
  analogWrite(redPin2, redValue);
  analogWrite(bluePin1, blueValue);
  analogWrite(bluePin2, blueValue);
  analogWrite(greenPin1, greenValue);
  analogWrite(greenPin2, greenValue);
}