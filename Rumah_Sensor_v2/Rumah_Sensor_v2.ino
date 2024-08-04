#include "cactus_io_AM2302.h"

#define AM2302_PIN 2     


#include <Wire.h>
#include <Adafruit_INA219.h>
Adafruit_INA219 ina219;

AM2302 dht(AM2302_PIN);

//  float busvoltage;
//  float current_mA;

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
}
 
void loop() {


  suhu();
  baterai();

  Serial.print(dht.temperature_C);
  Serial.print(",");
  Serial.print(dht.humidity);
  delay(1000);
 
}
