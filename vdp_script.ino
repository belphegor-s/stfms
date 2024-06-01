int pin1 = 12; 
int pin2 = 13;

void setup() {
  pinMode(pin1, OUTPUT);
  pinMode(pin2, OUTPUT);
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for the serial port to connect. Necessary for boards with native USB.
  }
}

void loop() {
  const char* commands[] = {"00", "01", "10", "11"};
  int laneCounts[4] = {0, 0, 0, 0};
  int highestCount = 0;
  int laneWithHighestCount = 0;

  for (int i = 0; i < 4; i++) {
    Serial.println(commands[i]);
    Serial.flush(); // Ensure all data is sent before continuing
    delay(5000);
    
    if (Serial.available() > 0) {
      laneCounts[i] = Serial.parseInt();
      Serial.print("Count for ");
      Serial.print(commands[i]);
      Serial.print(": ");
      Serial.println(laneCounts[i]);
    }

    if (laneCounts[i] > highestCount) {
      highestCount = laneCounts[i];
      laneWithHighestCount = i;
    }

    // Log which lane has the highest count so far
    Serial.print("Highest count so far is in lane ");
    Serial.print(laneWithHighestCount);
    Serial.print(" with count: ");
    Serial.println(highestCount);
    
    // Activate the corresponding lights
    switch (laneWithHighestCount) {
      case 0: digitalWrite(pin1, LOW); digitalWrite(pin2, LOW); break;
      case 1: digitalWrite(pin1, HIGH); digitalWrite(pin2, LOW); break;
      case 2: digitalWrite(pin1, LOW); digitalWrite(pin2, HIGH); break;
      case 3: digitalWrite(pin1, HIGH); digitalWrite(pin2, HIGH); break;
    }

    Serial.println("Updated traffic light settings based on vehicle count.");
    
    // Adjust delay based on vehicle count
    int delayTime = highestCount < 5 ? 5000 : highestCount < 10 ? 3000 : 1000;
    delay(delayTime);
  }
}
