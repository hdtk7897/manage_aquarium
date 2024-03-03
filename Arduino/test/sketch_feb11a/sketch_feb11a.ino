boolean stringComplete = false;
String inputString = "";  

void setup() {

  Serial.begin(19200);
}

void loop() {
  
  if (stringComplete) {

    Serial.print(inputString);
    inputString = "";
        
    stringComplete = false; 
  }
}

void serialEvent() {

  while (Serial.available()) {
    char inChar = (char)Serial.read(); 
    inputString += inChar;
    if (inChar == '\n') { 
      stringComplete = true; 
     }
  }
}
