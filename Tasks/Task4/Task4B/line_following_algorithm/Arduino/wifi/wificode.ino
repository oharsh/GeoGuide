#include <L298N.h>
#include <WiFi.h>
// Line Follower Robot with Node Decision Arduino Code

const char* ssid = "MSI";                    //Enter your wifi hotspot ssid
const char* password =  "jaimatadi";               //Enter your wifi hotspot password
const uint16_t port = 8002;
const char * host = "192.168.137.50"; 

// Define pin numbers for IR sensors
int sensor1Pin = 19;
int sensor2Pin = 2;
int sensor3Pin = 18;
int sensor4Pin = 4;
int sensor5Pin = 15;

// Define motor control pins
int in1 = 12;  
int in2 = 14;
int in3 = 27;
int in4 = 26;

int en1 = 13;
int en2 = 25;

WiFiClient client;

L298N motorL(en1, in1, in2);
L298N motorR(en2, in3, in4);
// Define LED pin for debugging
//int ledPin = 13;

// Define state variables
enum State {
  FOLLOW_LINE,
  DETECT_NODE,
  STOP
};

State currentState = FOLLOW_LINE;
char roadConfiguration[] = "SSRLRRSRSLS";  // Example road configuration string
int currentRoadIndex = 0;

void setup() {
  // Set up sensor pins as inputs
  Serial.begin(115200);

    WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("...");
  }
 
  Serial.print("WiFi connected with IP: ");
  Serial.println(WiFi.localIP());

  pinMode(sensor1Pin, INPUT);
  pinMode(sensor2Pin, INPUT);
  pinMode(sensor3Pin, INPUT);
  pinMode(sensor4Pin, INPUT);
  pinMode(sensor5Pin, INPUT);

  // Set up motor control pins as outputs
  // pinMode(leftMotorPin1, OUTPUT);
  // pinMode(leftMotorPin2, OUTPUT);
  // pinMode(rightMotorPin1, OUTPUT);
  // pinMode(rightMotorPin2, OUTPUT);
  motorL.setSpeed(250);
  motorR.setSpeed(250);
  // Set up LED pin for debugging
  //pinMode(ledPin, OUTPUT);
  client.connect(host, port);
  delay(500);

}

void loop() {
  // Read sensor values
  Serial.begin(115200);
  int sensor1 = digitalRead(sensor1Pin);
  int sensor2 = digitalRead(sensor2Pin);
  int sensor3 = digitalRead(sensor3Pin);
  int sensor4 = digitalRead(sensor4Pin);
  int sensor5 = digitalRead(sensor5Pin);

 
  client.print(sensor1); 
  client.print(sensor2); 
  client.print(sensor3); 
  client.print(sensor4); 
  client.println(sensor5); 
  // Check for node detection
  if (sensor2 == HIGH && sensor3 == HIGH && sensor4 == HIGH) {
    currentState = DETECT_NODE;
  }

  // State machine logic
  switch (currentState) {
    case FOLLOW_LINE:
      followLine(sensor1, sensor2, sensor3, sensor4, sensor5);
      break;
    case DETECT_NODE:
      detectNode();
      break;
    case STOP:
      stopMotors();
      break;
  }
}  

void followLine(int LM, int L, int C, int R, int RM) {
  // Implement your line following logic here
  // Adjust motor speeds based on sensor readings
  // ...
  // if (!((C == HIGH) && (L == HIGH) && (R == HIGH))){
  //   if (L == HIGH){
  //   left();
  //   }
  //   else if (R == HIGH){
  //   right();
  //   }
  //   else {
  //     forward();
  //   }
  // }
  // else {
    if (C == LOW && L == LOW && R == LOW){
      if (LM == LOW && RM == LOW){
        forward();
        delay(50);
      }
      if (LM == HIGH){
        right();
        delay(50);
      }
      if (RM == HIGH){
        left();
        delay(50);
      }
    }
    else {
    
      if((LM==LOW && L==LOW && C==HIGH && R==LOW && RM==LOW) || (LM==LOW && L==LOW && C==LOW && R==LOW && RM==LOW)){
            forward();
      }
      // MOVE LEFT
      if((LM==LOW && L==HIGH && C==LOW && R==LOW && RM==LOW) || (LM==LOW && L==LOW && C==LOW && R==LOW && RM==HIGH) || (LM==LOW && L==HIGH && C==LOW && R==LOW && RM==HIGH)){
      left();
      }
      // MOVE RIGHT
      if((LM==LOW && L==LOW && C==LOW && R==HIGH && RM==LOW) || (LM==HIGH && L==LOW && C==LOW && R==LOW && RM==LOW) || (LM==HIGH && L==LOW && C==LOW && R==HIGH && RM==LOW)){
            right();
      }
      
      delay(50);  // Adjust delay as needed
    }
}

void detectNode() {
  // Stop motors at the node
  stopMotors();
  // info();
  delay(500);  // Adjust delay as needed

  // Read the road configuration at the current index
  char currentRoadElement = roadConfiguration[currentRoadIndex];

  // Make decisions based on the road configuration
  switch (currentRoadElement) {
    case 'S':
      // Move forward
      // Stop the robot
      Serial.println("Moving forward");
        stop();
        delay(500);
        forward();
        delay(500);
      break;
    case 'R':
      // Turn right (90 degrees)
      // Stop the robot
      Serial.println("Moving Right");
        stop();
        delay(500);
        right();
        // Adjust the delay to achieve a 90-degree turn
        delay(1200);
        stop();

      break;
    case 'L':
      // Turn left (90 degrees)
      // Stop the robot
      Serial.println("Moving Left");
      stop();
      // Delay to ensure the robot comes to a complete stop
      delay(500);
    
      // Turn left by running the left motor backward and the right motor forward
      left();
    
      // Adjust the delay to achieve a 90-degree turn
      delay(1200);
    
      // Stop the robot after the turn
     stop();
         
      break;
    case 'U':
      // Make a U-turn
      
      break;
  }
  // info();
  currentRoadIndex++;
  currentState = FOLLOW_LINE;
}

void stopMotors() {
  // Implement motor stopping logic here
  // ...
     motorL.stop();
     motorR.stop();
    //  info();
}

// void right(){
//         digitalWrite(leftMotorPin1, HIGH);
//         digitalWrite(leftMotorPin2, LOW);
//         digitalWrite(rightMotorPin1, LOW);
//         digitalWrite(rightMotorPin2, LOW);
// }

// void left(){
//       digitalWrite(leftMotorPin1, LOW);
//       digitalWrite(leftMotorPin2, LOW);
//       digitalWrite(rightMotorPin1, HIGH);
//       digitalWrite(rightMotorPin2, LOW);
// }

// void forward(){
//         digitalWrite(leftMotorPin1, HIGH);
//         digitalWrite(leftMotorPin2, LOW);
//         digitalWrite(rightMotorPin1, HIGH);
//         digitalWrite(rightMotorPin2, LOW);
// }
// void stop(){

// }

void forward(){
  motorL.forward();
  motorR.forward();
}
void left(){
  motorL.stop();
  motorR.forward();
}
void right(){
  motorL.forward();
  motorR.stop();
}
void stop(){
  motorL.stop();
  motorR.stop();
}
// void info(){
//   WebSerial.println("Status");
//   WebSerial.print(sensor1Value);
//   WebSerial.print(sensor2Value);
//   WebSerial.print(sensor3Value);
//   WebSerial.print(sensor4Value);
//   WebSerial.print(sensor5Value);
// }
