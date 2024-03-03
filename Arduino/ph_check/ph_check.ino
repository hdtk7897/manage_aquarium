const int analogInPin = A0; 
int sensorValue = 0; 
float average;
int   loopCnt    = 50;
float neutral_val = 795;
float intercept   = 700;
float slope     = -2.5;
 
void setup() {
  Serial.begin(9600);
}
 
 
void loop() {

  average = 0.0;
  for(int i=0;i<loopCnt;i++) {
    average += analogRead(analogInPin);
    delay(10);
  }
  average /= loopCnt;
  float diff = neutral_val - average;
  float phVal = (intercept - diff * slope) / 100;
  
  Serial.print("voltage : ");
  Serial.print(average);
  Serial.print(", ph : ");
  Serial.println(phVal);
  delay(1000);
}
