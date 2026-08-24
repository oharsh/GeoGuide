/*
 * Bench test for the motor driver and a single IR sensor.
 *
 * Drives the motors forward until the IR sensor reads a line, then stops. Use
 * it to confirm the motor wiring polarity and the sensor threshold before
 * assembling the full five-sensor array.
 */

//Motor pin connections
#define in1 16
#define in2 4
#define in3 2
#define in4 15
//ir pin connection
#define irPin 17

void setup() {
  //Motor pins as output
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  //sensor pin as input
  pinMode(irPin, INPUT);
  //Keeping all motors off initially
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);

}

void loop() {
  if(digitalRead(irPin)){
    //Move
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
    digitalWrite(in3, HIGH);
    digitalWrite(in4, LOW);    
  }
  else{
    //Stop
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
    digitalWrite(in3, LOW);
    digitalWrite(in4, LOW);
  }
}