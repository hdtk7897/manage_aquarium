//
// 湿温度センサー AM2320 I2C接続サンプル
//

#include <Wire.h>
#define DEV_ADR 0x5c  // AM2320スレーブアドレス

uint8_t data[8];

void setup() {
  Wire.begin();            
  Serial.begin(115200);
}

void loop() {
    Serial.println("aaa");
  delay(1000);
}
