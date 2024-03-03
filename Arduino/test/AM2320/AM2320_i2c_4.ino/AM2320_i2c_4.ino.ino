#include <Wire.h>
#define DEV_ADR 0x5c

uint8_t data[8];

void setup() {
  Wire.begin();            
  Serial.begin(9600);
}

void loop() {
  Wire.beginTransmission(DEV_ADR);
  Wire.endTransmission();

  Wire.beginTransmission(DEV_ADR);
  Wire.write(0x03);
  Wire.write(0x00);
  Wire.write(0x04);
  Wire.endTransmission();

  Wire.requestFrom(DEV_ADR,8); 
  if (Wire.available() >= 8) {
    for (uint8_t i=0; i<8; i++) {
      data[i] = Wire.read();
    }
    
    float rh = ((float)(data[2]*256+data[3]))/10;
    float tp = ((float)(data[4]*256+data[5]))/10;
    
    // ���x�E���x�̕\��
    Serial.print("T=");
    Serial.print(tp);
    Serial.print("c");
    Serial.print(" H=");
    Serial.print(rh);
    Serial.println("%");
  }
  delay(1000);
}
