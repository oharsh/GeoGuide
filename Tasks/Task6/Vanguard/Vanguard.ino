/*
 * Author List:     Abhishek Ranjan, Arijit Goswami, Gaurav Singh, Harsh Yadav
 * Team Id:         GG_1667
 * Filename:        Vanguard.ino
 * Theme:           Geo Guide
 * Functions:       setup(), loop(), followLine(int, int, int, int, int), nodeDetected(), stop(), left(), right(), forward(), setMotorSpeed(int,int),
 *                  sensorsReading(), uTurn(), black_or_not(int, int), read(int, int)
 * Global Variables:  ssid, pass, port, host, leftSpeed, rightSpeed, nodeTurnDelay, turnDelay, sideTurnDelay,
 */

#include <WiFi.h>
#include <string.h>

// Wifi Credentials and Host information
const char *ssid = "MSI";
const char *pass = "jaimatadi";
const uint16_t port = 8002;
const char *host = "192.168.137.181";

// Motor Speed Variables
uint16_t leftSpeed = 255;
uint16_t rightSpeed = 255;

// Amount of time for which the vanguard will take turn on passing the node
const uint16_t nodeTurnDelay = 660;

// Reallignment time while following middle road
const uint16_t turnDelay = 20;

// Reallignment time of the vanguard whenever it touches the side rails
const uint16_t sideTurnDelay = 60;

// GPIO's pin definition for IR sensors
int sensor1Pin = 33;
int sensor2Pin = 32;
int sensor3Pin = 35;
int sensor4Pin = 34;
int sensor5Pin = 39;

// GPIO's pin definition for motors
int leftMotorPin1 = 12;
int leftMotorPin2 = 14;
int rightMotorPin1 = 27;
int rightMotorPin2 = 26;

// GPIO's pin definition for enable a and enable b
const uint16_t ena = 13;
const uint16_t enb = 25;

// Buzzer pin
int buzzer = 15;

// head: head variable is used to track the direction of head of the Vanguard
char head;

// State is an enum corresponding to the three state of the robot
enum State
{
  FOLLOW_LINE,
  NODE_DETECT,
  STOP
};

// sense: sense is an structure which will be used to store reading from the sensors.
struct sense
{
  int s1;
  int s2;
  int s3;
  int s4;
  int s5;
};

// sensor is an instance of the structure 'sense'
sense sensor;

// Initially the robot is set to FOLLOW_LINE state.
State currentState = FOLLOW_LINE;

// roadConfiguration: this variable is used to store the road configuration
// for the robot in order to reach the destination this will also contain
// information like orientation of head of the robot, status of the run whether
// ie. I- Start of Run
//     Q- End of Run
//     T- Represent one of the two possible orientation of the robot's head
//     F- Represent the other possible orientation of the robot's head (opposite of 'T')
String roadConfiguration;

// int currentRoadIndex = 0;//del
// bool ready = true;de
// String emergency = "E";de

// WiFiClient object is initiated with the name client
WiFiClient client;

/*
 * Function Name: setup
 * Input:         None
 * Output:        Initialize variable, set pin mode, Initialize the Wi-fi using ssid and pass variable,
 *                it also checks whether Wi-fi status is connected or not, after esp establishes a connection with the wifi it will
 *                try to connect to the socket which is open on the host computer.
 * Logic:         this function will run only once after each powerup or reset of the board
 * Example Call:  setup function is automatically called when sketch starts.
 */

void setup()
{
  delay(5000);
  WiFi.begin(ssid, pass);
  delay(1000);

  // setting the motor pins mode to output
  pinMode(leftMotorPin1, OUTPUT);
  pinMode(leftMotorPin2, OUTPUT);
  pinMode(rightMotorPin1, OUTPUT);
  pinMode(rightMotorPin2, OUTPUT);

  // setting the buzzer pin mode to output
  pinMode(buzzer, OUTPUT);

  // This function is used to set the right and left motor speed using enable a and enable b pin
  setMotorSpeed(leftSpeed, rightSpeed);

  // negative logic buzzer
  digitalWrite(buzzer, LOW);
  delay(1000);
  digitalWrite(buzzer, HIGH);

  // it will stop further execution of the program until the wifi is connected.
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.println("...");
  }

  Serial.print("connected with ip: ");
  Serial.println(WiFi.localIP());

  // it will stop further execution of the program until client is connected to the socket
  while (!client.connect(host, port))
  {
    Serial.println("no connection");
    delay(500);
  };
  Serial.println("connection established");
  while (!client.available())
  {
    delay(50);
  }
  // Vanguard will request for the first set of configuration to reach the first event
  roadConfiguration = client.readStringUntil('\n');
  Serial.println("new road config obtained");
  Serial.println(roadConfiguration);
}

/*
 * Function Name:  loop
 * Input:          None
 * Output:         None
 * Logic:          take reading from the sensors to estimate its location with
 *                 respect to the road
 *                 check the roadConfiguration string and based on that decides
 *                 what instruction are to be performed for example
 *                 I- Start of Run
 *                 Q- End of Run
 *                 T- Represent one of the two possible orientation of the robot's head
 *                 F- Represent the other possible orientation of the robot's head 
 *                    (opposite of 'T')
 *                 T and F are used to tell the desired orientation for the robot
 *                 in order to reach a particular destination
 *
 * Example Call: loop function will be executing
 */

void loop()
{

  sensor = sensorsReading();

  // if the first char of roadConfiguration equals 'Q' this means that the Vanguard has
  // completed its mission and has arrived HOME
  if (roadConfiguration[0] == 'Q')
  {
    client.print("HOME");
    while (!client.available())
    {
      sensor = sensorsReading();
      followLine(sensor.s1, sensor.s2, sensor.s3, sensor.s4, sensor.s5);
    }
    stop();
    digitalWrite(buzzer, LOW);
    delay(5000);
    digitalWrite(buzzer, HIGH);
    while (true)
    {
      stop();
      delay(1000);
    }
  }
  // if first char of roadConfiguration equals 'I' this indicates that the Vanguard is
  // currently at the HOME.
  if (roadConfiguration[0] == 'I')
  {
    roadConfiguration.remove(0, 1);
  }

  // Below code checks the orientation of the head of the Vanguard if it is correctly
  // alligned it will just move forward otherwise it will take a u-turn and corrects itself
  //'T' and 'F' are used to represent the two possible direction of the robot

  else if (roadConfiguration[0] == 'T')
  {
    if (head == 'T')
    {
      roadConfiguration.remove(0, 1);
    }
    else
    {
      uTurn();
      roadConfiguration.remove(0, 1);
    }
  }

  else if (roadConfiguration[0] == 'F')
  {
    if (head == 'F')
    {
      roadConfiguration.remove(0, 1);
    }
    else
    {
      uTurn();
      roadConfiguration.remove(0, 1);
    }
  }

  // Whenever the Vanguard is about to reach the event destination and just crossed the last node
  // ie roadConfiguration is empty. It will send a "ALERT" signal to the control center which
  // will tell the Vanguard exactly when to stop
  // On receiving the stop signal the Vanguard will stop and wait for 1 second,
  // After that it will request for new roadConfiguration for the next destination
  if (roadConfiguration.isEmpty())
  {
    client.print("ALERT");
    while (!client.available())
    {
      sensor = sensorsReading();
      followLine(sensor.s1, sensor.s2, sensor.s3, sensor.s4, sensor.s5);
    }
    stop();
    client.flush();
    client.println("SEND");
    digitalWrite(buzzer, LOW);
    delay(1000);
    digitalWrite(buzzer, HIGH);
    roadConfiguration = client.readStringUntil('\n');
    return;
  }

  // this will check for the NODE, if the three middle sensors are HIGH at the same
  // time, this tells the Vanguard that there is a node below it
  if (sensor.s2 == HIGH && sensor.s3 == HIGH && sensor.s4 == HIGH)
  {
    currentState = NODE_DETECT;
  }

  // switch the current state of the robot

  switch (currentState)
  {
  case FOLLOW_LINE:
    followLine(sensor.s1, sensor.s2, sensor.s3, sensor.s4, sensor.s5);
    break;
  case NODE_DETECT:
    nodeDetected();
    break;
  case STOP:
    stop();
    delay(1000);
    break;
  }

}

/*
 * Function Name:   followLine
 * Input:           s1-> sensor 1 input
 *                  s2-> sensor 2 input
 *                  s3-> sensor 3 input
 *                  s4-> sensor 4 input
 *                  s5-> sensor 5 input
 * 
 * Output:          NONE

 * Logic:           It makes the Vanguard follow the black line there are set of five IR sensors 
 *                  on the front of the Vanguard it takes the reading from the sensors and based     
 *                  on the readings autocorrects itself.
 *                      
 *                  Turn left:
 *                        sensor 2 is on black line.
 *                        sensor 5 is on black line.
 *                  Turn right:
 *                        sensor 4 is on black line.
 *                        sensor 1 is on black line.
 *                  Move forward:
 *                        sensor 3 is on black line.
 *                        and in all other cases.
 *
 * Example Call:   followLine(sensor.s1, sensor.s2, sensor.s3, sensor.s4, sensor.s5);
*/


void followLine(int s1, int s2, int s3, int s4, int s5)
  {

    if (s3 == HIGH && s2 == LOW && s4 == LOW)
    {
      forward();
      delay(turnDelay);
    }
    else if (s2 == HIGH || s4 == HIGH)
    {
      if (s2 == HIGH ^ s4 == HIGH)
      {
        if (s2 == HIGH)
        {
          left();
          delay(turnDelay);
        }
        else
        {
          right();
          delay(turnDelay);
        }
      }
    }
    else
    {
      if (s1 == HIGH ^ s5 == HIGH)
      {
        if (s1 == HIGH)
        {
          right();
          delay(sideTurnDelay);
        }
        else
        {
          left();
          delay(sideTurnDelay);
        }
      }
      else
      {
        forward();
        delay(10);
      }
    }
  }

/*
   * Function Name:   nodeDetected
   *
   * Input:           NONE
   * 
   * Output:          NONE
   * 
   * Logic:           It takes the first char from the roadConfiguration and use it to decide whether
   *                  to go straight, take a left turn, or take a right turn.
   *                  it also stores the current head orientation for later use.
   *                  
   * Example Call:    nodeDetected();
*/

void nodeDetected()
  {
    char currentRoadElement = roadConfiguration[0];
    switch (currentRoadElement)
    {
    case 'S':
      forward();
      delay(250);
      break;
    case 'R':
      stop();
      delay(100);
      right();
      delay(nodeTurnDelay);
      break;
    case 'L':
      stop();
      delay(100);
      left();
      delay(nodeTurnDelay);
      break;
    }
    roadConfiguration.remove(0, 1);
    if (roadConfiguration[0] == 'T' | roadConfiguration[0] == 'F')
    {
      head = roadConfiguration[0];
      roadConfiguration.remove(0, 1);
    }
    currentState = FOLLOW_LINE;
  }

/*
   * Function Name:   stop
   * Input:           None
   * Output:          Stops the bot
   * Logic:           it sets all the motor pins to LOW
   *
   * Example Call:    stop();
*/

void stop()
  {
    digitalWrite(leftMotorPin1, LOW);
    digitalWrite(leftMotorPin2, LOW);
    digitalWrite(rightMotorPin1, LOW);
    digitalWrite(rightMotorPin2, LOW);
  }

/*
   * Function Name:   left
   * Input:           None
   * Output:          make the bot take left turn
   * Logic:           Both left motor pins(positive and negative) are set to LOW which makes the
   *                  left motor to stop and positive pin of right motor is set to HIGH and negative
   *                  pin to LOW which makes the right motor to move forward. so overall the bot turn
   *                  left.
   *
   * Example Call: left();
*/

void left()
  {
    digitalWrite(leftMotorPin1, LOW);
    digitalWrite(leftMotorPin2, LOW);
    digitalWrite(rightMotorPin1, HIGH);
    digitalWrite(rightMotorPin2, LOW);
  }

/*
   * Function Name:   right
   * Input:           None
   * Output:          make the bot take right turn
   * Logic:           Both right motor pins(positive and negative) are set to LOW which makes the
   *                  right motor to stop and positive pin of left motor is set to HIGH and negative
   *                  pin to LOW which makes the left motor to move forward. so overall the bot turn
   *                  right.
   *
   * Example Call: right();
*/

void right()
  {
    digitalWrite(leftMotorPin1, HIGH);
    digitalWrite(leftMotorPin2, LOW);
    digitalWrite(rightMotorPin1, LOW);
    digitalWrite(rightMotorPin2, LOW);
  }

/*
   * Function Name:  forward
   * Input:          None
   * Output:         make the bot move forward
   * Logic:          Positive pin of both motor is set to HIGH and Negative pin of both motor
   *                 is set to LOW. which makes the both motor to move forward. so overall the
   *                 bot moves in the straight line.
   *
   * Example Call: forward();
*/

void forward()
  {
    digitalWrite(leftMotorPin1, HIGH);
    digitalWrite(leftMotorPin2, LOW);
    digitalWrite(rightMotorPin1, HIGH);
    digitalWrite(rightMotorPin2, LOW);
  }

/*
  * Function Name:   setMotorSpeed
  * Input:           leftSpeed ->  contains the values from 0 to 255
  *                  rightSpeed -> contains the values form 0 to 255
  * Output:          set the speed of the motors
  * Logic:
  *
  * Example Call: <Example of how to call this function>
*/

void setMotorSpeed(int leftSpeed, int rightSpeed)
{
  analogWrite(ena, leftSpeed);
  analogWrite(enb, rightSpeed);
}

/*
 * Function Name:     read
 * Input:             pin -> IR sensor pin
 *                    ref -> reference value for the analog reading of a particular sensor
 * Output:            return a bool value
 * Logic:             it will compare the analog reading from the sensor against the reference value and
 *                    return a boolean value indicating the presence or absense of black line under the sensor
 * Example Call:      read(sensor1Pin, 3500);
*/

int read(int pin, int ref)
{
  
  int reading = analogRead(pin);
  if(reading > ref)
  {
    return 1;
  }
 
  return 0;
  
}

/*
 * Function Name:   sensorsReading
 * Input:           None
 * Output:          it will return a structure containg reading from the sensors.
 * Logic:           it will use read() function on each sensor pin using a reference value for the sensor
 *                  and store the readings in a struct named sensors.
 * Example Call:    sensorsReading();
*/

sense sensorsReading()
{
  sense sensors;
  sensors.s1 = read(sensor1Pin, 3500);
  sensors.s2 = read(sensor2Pin, 3100);
  sensors.s3 = read(sensor3Pin, 3500);
  sensors.s4 = read(sensor4Pin, 3500);
  sensors.s5 = read(sensor5Pin, 3500);
  return sensors;
}

/*
 * Function Name:    uTurn
 * Input:            None
 * Output:           makes the bot take U turn
 * Logic:            positive pin of left motor is set to HIGH and negative pin to LOW
 *                   (which makes the left motor to move forward)
 *                   positive pin of right motor is set to LOW and negative pin to HIGH
 *                   (which makes the right motor to move in reverse direction)
 *                   overall the bot takes U turn in clockwise direction
 *
 * Example Call:     uTurn();
*/

void uTurn()
{
  digitalWrite(leftMotorPin1, HIGH);
  digitalWrite(leftMotorPin2, LOW);
  digitalWrite(rightMotorPin2, HIGH);
  digitalWrite(rightMotorPin1, LOW);
  delay(1150);
  stop();
}
