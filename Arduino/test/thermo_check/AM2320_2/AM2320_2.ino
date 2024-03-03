// 温湿度センサー AM2320 ONE-WIRE アクセステスト
#define BAUDRATE 9600
#define DATAPIN 2 // コレは何番ピンでも良い
 
char str[120] ;
 
// ----- Senser Data
struct AM2320_s {
  uint8_t humidityH ;   // 湿度の HIGH Byte
  uint8_t humidityL ;   // 湿度の LOW BYTE
  uint8_t temperatureH; // 温度の HIGH Byte
  uint8_t temperatureL; // 温度の LOW Byte
} am2320 ;
 
bool readAM2320( ) {
  uint8_t readData[5] ;
  uint8_t checkSum = 0 ;
  int setPos = 0 ;
  int bitLen = 0 ;
  int stat = HIGH ;
  uint8_t bitData ;
  unsigned long beginTime ;
  unsigned long passTime ;
  unsigned long zeroTime = 35 ; // 35μ秒以下なら０ 以上なら１と判定 ※仕様では0は26～28μ秒
  bool flagStart = false;
 
  for (int i=0;i<5;i++) {
    readData[i] = 0 ;
  }
 
  // ----- データ送信要求 -----
  pinMode(DATAPIN, OUTPUT); //開始信号
  delay(2); // 0.8~20mS Typ:1mS
  pinMode(DATAPIN, INPUT);
  while(digitalRead(DATAPIN) == LOW) {
    delayMicroseconds(5) ;
  }
 
  // ----- ACSEPT -----
  flagStart = false;
  passTime = 0 ;
  beginTime = micros();
  while (passTime < 1000) {
    passTime = micros() - beginTime ;
    if (digitalRead(DATAPIN) !=  stat) {
      if (stat == HIGH) {
        stat = LOW ;
        if (flagStart) {
           break ; 
        }
      } else {
        beginTime = micros();
        flagStart = true ;
        stat = HIGH ;
      }
    }
  }
  
  // ----- データ受信 -----
  bitData = 0x80 ;
  flagStart = false;
  passTime = 0 ;
  beginTime = micros();
  while (bitLen < 40 && passTime < 1000) {
    passTime = micros() - beginTime ;
    if (digitalRead(DATAPIN) !=  stat) {
      if (stat == HIGH) {
        stat = LOW ;
        if (flagStart) {
          // ----- 1Bit 受信 -----
          if (passTime > zeroTime) {
            readData[setPos] |= bitData ;
          }
          if (bitData != 0x01) {
            bitData >>= 1 ;
          } else {
            bitData = 0x80 ;
            setPos ++ ;
          }
 
          // ----- ステート変数リセット -----
          beginTime = micros();
          flagStart = false;
          bitLen ++ ;
        }
      } else {
        beginTime = micros();
        flagStart = true ;
        stat = HIGH ;
      }
    }
  }
 
  // ----- 取得データ格納 -----
  am2320.humidityH = readData[0] ;   // 湿度の HIGH Byte
  am2320.humidityL = readData[1] ;   // 湿度の LOW Byte
  am2320.temperatureH = readData[2]; // 温度の HIGH Byte
  am2320.temperatureL = readData[3]; // 温度の LOW Byte
  checkSum = readData[0] + readData[1] + readData[2] + readData[3] ;
  return (bitLen == 40 && checkSum == readData[4]) ;
}
 
void setup() {
  Serial.begin(BAUDRATE);
  Serial.println("\nAM2320 - Read") ;
 
  pinMode(DATAPIN, INPUT_PULLUP);
}
 
void loop() {
  if (readAM2320( )) {
    int hum = (am2320.humidityH << 8) + am2320.humidityL ;
    int tem = ((am2320.temperatureH & 0x7F) << 8) + am2320.temperatureL ;
    if ((am2320.temperatureH & 0x80) != 0) tem *= -1 ;
    sprintf(str,"湿度:%2d.%d%%  気温:%2d.%d℃", hum / 10 , hum % 10 , tem / 10 , tem % 10) ;
    Serial.println(str) ;
  }
  delay(3000) ;
}