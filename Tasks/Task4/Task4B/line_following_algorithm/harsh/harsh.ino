#include <WiFi.h>

const char* ssid = "MSI";
const char* pass = "jaimatadi";
const uint16_t port = 8002; 
const char* host = "192.168.137.171";

uint16_t leftSpeed = 255;
uint16_t rightSpeed = 255;

const uint16_t nodeTurnDelay = 970;  //1200 //970
const uint16_t turnDelay = 20;
const uint16_t sideTurnDelay = 40;

int sensor1Pin = 33;  
int sensor2Pin = 32; 
int sensor3Pin = 35; 
int sensor4Pin = 34;  
int sensor5Pin = 4;  //25

int leftMotorPin1 = 12;
int leftMotorPin2 = 14;
int rightMotorPin1 = 27;
int rightMotorPin2 = 26;

const uint16_t ena = 13; //4
const uint16_t enb = 25;

int ledPin = 5;
int buzzer = 15;

enum State {
  FOLLOW_LINE,
  DETECT_NODE,
  STOP
};

State currentState = FOLLOW_LINE;
char roadConfiguration[100] ;
int currentRoadIndex = 0;

WiFiClient client;
String msg ;
int command ;

void setup() {

  delay(5000);

  Serial.begin(115200);
  while(!Serial){delay(100);}

  pinMode(leftMotorPin1, OUTPUT);
  pinMode(leftMotorPin2, OUTPUT);
  pinMode(rightMotorPin1, OUTPUT);
  pinMode(rightMotorPin2, OUTPUT);

  pinMode(ledPin, OUTPUT);
  pinMode(buzzer, OUTPUT);

  setMotorSpeeds(leftSpeed, rightSpeed);

  digitalWrite(ledPin, HIGH);
  digitalWrite(buzzer, LOW);
  delay(1000);
  digitalWrite(ledPin, LOW);
  digitalWrite(buzzer, HIGH);

  WiFi.begin(ssid, pass);

  while(!WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.println("...");
  }

  Serial.print("connected to: ");
  Serial.println(WiFi.localIP());

  while(!client.connect(host, port)){
    Serial.println("connection to host failed");
    delay(200);
  }

  Serial.println("client connected");

}

void loop() {

  int s1v = read(sensor1Pin, 3500);
  int s2v = read(sensor2Pin, 3100);
  int s3v = read(sensor3Pin, 3500);
  int s4v = read(sensor4Pin, 3500);
  int s5v = read(sensor5Pin, 3500);

  if (s2v == HIGH && s3v == HIGH && s4v == HIGH) {
    currentState = DETECT_NODE;
  }

  switch (currentState) {
    case FOLLOW_LINE:
      followLine(s1v, s2v, s3v, s4v, s5v);
      break;
    case DETECT_NODE:
      detectNode();
      break;
    case STOP:
      stop();
      break;
  }

}

void followLine(int s1, int s2, int s3, int s4, int s5) {

  if (s3 == HIGH && s2 == LOW && s4 == LOW){
      forward();
      delay(turnDelay);
  }
  else if (s2 == HIGH || s4 == HIGH){
    if (s2 == HIGH ^ s4 == HIGH ){
      if (s2 == HIGH){
        left();
        delay(turnDelay);
      }
      else {
        right();
        delay(turnDelay);
      }      
    }
  }
  else {
    if (s1 == HIGH ^ s5 == HIGH){
      if (s1 == HIGH){
        right();
        delay(sideTurnDelay);
      }
      else {
        left();
        delay(sideTurnDelay);
      }
    }
    else {
      forward();
      delay(10);
    }
  }  
}


void detectNode() {
  char currentRoadElement = roadConfiguration[currentRoadIndex];
  switch (currentRoadElement) {
    case 'S':
      Serial.println("Moving forward");
      stop();
      digitalWrite(buzzer, LOW);
      delay(1000);
      digitalWrite(buzzer, HIGH);
      forward();
      delay(400);
      break;
    case 'R':
      Serial.println("Moving Right");
      stop();
      digitalWrite(buzzer, LOW);
      delay(1000);
      digitalWrite(buzzer, HIGH);
      right();
      delay(nodeTurnDelay);
      break;
    case 'L':
      Serial.println("Moving Left");
      stop();
      digitalWrite(buzzer, LOW);
      delay(1000);
      digitalWrite(buzzer, HIGH);
      left();
      delay(nodeTurnDelay);
      break;
    
  }
  currentRoadIndex++;
  currentState = FOLLOW_LINE;
}

void stop() {
  digitalWrite(leftMotorPin1, LOW);
  digitalWrite(leftMotorPin2, LOW);
  digitalWrite(rightMotorPin1, LOW);
  digitalWrite(rightMotorPin2, LOW);
}

void left(){
  digitalWrite(leftMotorPin1, LOW);
  digitalWrite(leftMotorPin2, LOW);
  digitalWrite(rightMotorPin1, HIGH);
  digitalWrite(rightMotorPin2, LOW);
}

void right(){
  digitalWrite(leftMotorPin1, HIGH);
  digitalWrite(leftMotorPin2, LOW);
  digitalWrite(rightMotorPin1, LOW);
  digitalWrite(rightMotorPin2, LOW);
}

void forward(){
  digitalWrite(leftMotorPin1, HIGH);
  digitalWrite(leftMotorPin2, LOW);
  digitalWrite(rightMotorPin1, HIGH);
  digitalWrite(rightMotorPin2, LOW);
}

int black(int val, int test){
  if (val > test){
    return 1;
  }
    return 0;
}

void setMotorSpeeds(int leftSpeed, int rightSpeed) {
  analogWrite(ena, leftSpeed);
  analogWrite(enb, rightSpeed);
}

void printInfo(int analog, int digital = 0){
  Serial.print(analog);  
  Serial.print(" ");
  Serial.print(digital);
  Serial.print("  ");
}

void blackFollow(){

  int s2 = analogRead(sensor2Pin);
  int s3 = analogRead(sensor3Pin);
  int s4 = analogRead(sensor4Pin);

  s2 = black(s2, 3100);
  s3 = black(s3, 3500);
  s4 = black(s4, 3500);


  if (s3 == HIGH && s2 == LOW && s4 == LOW){
      forward();
      delay(turnDelay);
    }
    else if (s2 == HIGH || s4 == HIGH){
      if (s2 == HIGH ^ s4 == HIGH ){
        if (s2 == HIGH){
          left();
          delay(turnDelay);
        }
        else {
          right();
          delay(turnDelay);
        }
      }
    }
}

int read(int pin, int ref){

  int final = analogRead(pin);
  final = black(final, ref);
  return final;

}

void printCompleteInfo(){

  int sensor1Value = analogRead(sensor1Pin);
  int sensor2Value = analogRead(sensor2Pin);
  int sensor3Value = analogRead(sensor3Pin);
  int sensor4Value = analogRead(sensor4Pin);
  int sensor5Value = analogRead(sensor5Pin);

  int s1v = black(sensor1Value, 3500);
  int s2v = black(sensor2Value, 3100);
  int s3v = black(sensor3Value, 3500);
  int s4v = black(sensor4Value, 3500);
  int s5v = black(sensor5Value, 3500);

  printInfo(sensor1Value, s1v);
  printInfo(sensor2Value, s2v);
  printInfo(sensor3Value, s3v);
  printInfo(sensor4Value, s4v);
  printInfo(sensor5Value, s5v);
  Serial.println("");

}

// if (currentRoadIndex == 11){
//     long int start = millis();
//     while (millis() - start < 1000){
//       blackFollow();
//     }
//     stop();
//     digitalWrite(ledPin, HIGH);
//     digitalWrite(buzzer, LOW);
//     delay(5000);
//     digitalWrite(ledPin, LOW);
//     digitalWrite(buzzer, HIGH);
//     while(1){
//       stop();
//     }
//   }