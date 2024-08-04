#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27,16,4);

#include "cactus_io_AM2302.h"

#define AM2302_PIN 2     


#include <Wire.h>
#include <Adafruit_INA219.h>
Adafruit_INA219 ina219;

AM2302 dht(AM2302_PIN);

//  float busvoltage;
//  float current_mA;

//setting lcd i2c/////////////////////////
byte suhu[8] =
{
  B00100,
  B01010,
  B01010,
  B01110,
  B11111,
  B11111,
  B01110,
  B00000
};

// Membuat ikon kelelembaban // 
byte kelembaban[8] =
{
  B00100,
  B01010,
  B01010,
  B10001,
  B10001,
  B10001,
  B01110,
  B00000
};
///////////////////////////////////////////

void setup() {
  Serial.begin(9600); 
  dht.begin();
  while (!Serial) {
      // will pause Zero, Leonardo, etc until serial console opens
      delay(1);
  }
  uint32_t currentFrequency;
  if (! ina219.begin()) {
        while (1) { delay(10); }
    
  }
  dht.begin();
  ina219.begin();

/////////////////////////LCD I2C///////////////
  lcd.init();
  lcd.backlight();
  lcd.createChar(1, kelembaban);
  lcd.createChar(2, suhu);
  lcd.setCursor(0,0);
  lcd.print("Rizky");
  lcd.setCursor(0,1);
  lcd.print("Rahmatullah");
  dht.begin();
  delay(2000);
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.write(2);
  lcd.print(" Suhu: ");
  lcd.setCursor(0,1);
  lcd.write(1);
  lcd.print(" Kelembaban: ");
}
 
void loop() {

  float shuntvoltage = 0;
  float busvoltage = 0;
  float current_mA = 0;
  float loadvoltage = 0;
  float power_mW = 0;
  shuntvoltage = ina219.getShuntVoltage_mV();
  busvoltage = ina219.getBusVoltage_V();
  current_mA = ina219.getCurrent_mA();
  power_mW = ina219.getPower_mW();
  loadvoltage = busvoltage + (shuntvoltage / 1000);
   dht.readHumidity();
  dht.readTemperature();
  
  // Check if any reads failed and exit early (to try again).
  if (isnan(dht.humidity) || isnan(dht.temperature_C)) {
    lcd.setCursor(8,0);
    lcd.print("Error");
    lcd.setCursor(13,1);
    lcd.print("Error");
    return;
  }
  
  lcd.setCursor(8,0);
  lcd.print(dht.temperature_C,1);
  lcd.print((char)223);
  lcd.print("C     ");
  lcd.setCursor(13,1);
  lcd.print(dht.humidity,0);
  lcd.print("%     ");
  delay(1000);
 
  // Jeda Waktu, ubah menjadi 2000 untuk DHT22//
  delay(1000);
  Serial.print(dht.temperature_C);
  Serial.print(",");
  Serial.print(dht.humidity);
  Serial.print(",");
  Serial.print(busvoltage);
  Serial.print(",");
  Serial.println(current_mA);
  delay(1000);
 
}
