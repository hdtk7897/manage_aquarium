/*
# This sample codes is for testing the pH meter V1.0.
 # Editor : YouYou
 # Date   : 2013.10.12
 # Ver    : 0.1
 # Product: pH meter
 # SKU    : SEN0161
*/

#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>
  
#define ONE_WIRE_BUS 10 // データ(黄)で使用するポート番号
#define SENSER_BIT    9      // 精度の設定bit
#define SensorPin 0          //pH meter Analog output to Arduino Analog Input 0
#define DEV_ADR 0x5c

uint8_t data[8];

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

unsigned long int avgValue;  //Store the average value of the sensor feedback
float b;
int buf[10],temp;

void setup()
{
  pinMode(13,OUTPUT);
  Wire.begin();
  Serial.begin(9600);  
  Serial.println("Ready");    //Test the serial monitor
  sensors.setResolution(SENSER_BIT);

}

void loop()
{
    // ph取得
    float phVal = getPh();
  
    // 温湿度取得
    float rh = 0;
    float tp = 0;
    getTempHumid(rh, tp);
  
  
    // 水温取得
    sensors.requestTemperatures();              // 温度取得要求
    float wtemp = sensors.getTempCByIndex(0);

    
/*
    Serial.print("pH:");  
    Serial.print(phVal);
    Serial.print(", WT:");
    Serial.print(wtemp); //温度の取得&シリアル送信
    Serial.print("c");
    Serial.print(", T:");
    Serial.print(tp);
    Serial.print("c");
    Serial.print(", H:");
    Serial.print(rh);
    Serial.println("%");
*/
    Serial.println("pH:"+String(phVal)+", WT:"+String(wtemp)+"c, T:"+String(tp)+"c, H:"+String(rh)+"%");
  
    delay(1000);
}

float getPh() {
  for(int i=0;i<10;i++)       //Get 10 sample value from the sensor for smooth the value
  { 
    buf[i]=analogRead(SensorPin);
    delay(10);
  }
  for(int i=0;i<9;i++)        //sort the analog from small to large
  {
    for(int j=i+1;j<10;j++)
    {
      if(buf[i]>buf[j])
      {
        temp=buf[i];
        buf[i]=buf[j];
        buf[j]=temp;
      }
    }
  }
  avgValue=0;
  for(int i=2;i<8;i++)                      //take the average value of 6 center sample
    avgValue+=buf[i];
  float phValue=(float)avgValue*5.0/1024/6; //convert the analog into millivolt
  phValue=3.5*phValue;                      //convert the millivolt into pH value
  return phValue;
}

void getTempHumid(float &rh, float &tp) {
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
    
    rh = ((float)(data[2]*256+data[3]))/10;
    tp = ((float)(data[4]*256+data[5]))/10;
  }
}
