const int analogInPin = A0; 
int sensorValue = 0; 
unsigned long int avgValue; 
float b;
int buf[10],temp;
 
void setup() {
  Serial.begin(9600);
}
 
 
void loop() {
  /*
  //Vol cal.
  int sensorValue = analogRead(A0);
  float voltage = sensorValue * (5.0 / 1023.0);
  Serial.print(analogRead(sensorValue));
  Serial.print(" : ");
  Serial.println(voltage);
  */
  
  for(int i=0;i<10;i++) {
    buf[i]=analogRead(analogInPin);
    delay(10);
  }
  for(int i=0;i<9;i++){
    for(int j=i+1;j<10;j++){
      if(buf[i]>buf[j]){
        temp=buf[i];
        buf[i]=buf[j];
        buf[j]=temp;
      }
    }
  }
  
  avgValue=0;
  for(int i=2;i<8;i++) avgValue+=buf[i];
  
  float pHVol=(float)avgValue*5.0/1024/6;
  float phValue = -5.737 * pHVol + 21.426;
 
  Serial.print("sensor = ");
  Serial.println(phValue);
  delay(20);
}
