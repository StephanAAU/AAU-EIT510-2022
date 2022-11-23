

#include <Arduino.h>
#include <Esp.h>
#include <CapSwitch.h>

/* Set up cap switches */
CapSwitch switch1(4, 32); // Pins 34-35 do not work on my board
CapSwitch switch2(4, 16);
CapSwitch switchTrim; // THIS IS A SINGLE PIN AT PIN 30
const int switchArrSize = 3;
CapSwitch switchArr[switchArrSize] = {switch1, switch2, switchTrim};


void setup() {
    Serial.begin(115200);
    while(!Serial) {}
    Serial.println("Setup happening");

    ledcSetup(1, 12000, 8);

    Serial.begin(115200);
    Serial.println("Ready to receive\n");
    
}

void loop() {
    if(Serial.available()) {
        // Form will be *,*,*

        String command = Serial.readStringUntil(',');
        int cluster    = Serial.readStringUntil(',').toInt();
        int state      = Serial.readStringUntil('\n').toInt();

        // if(cluster == 0 || state == 0) {return;}

        if(cluster < 0 || cluster > switchArrSize) {
            Serial.printf("Error: Cluster number out of bounds\n");
            return;
        }
        if(command.equals("static")) {
            if(switchArr[cluster].ClusterStaticSwitch(state) == 0) {
                Serial.printf("Switch cluster %i changed to static state %i\n", cluster, state);
            }
            else {
                Serial.printf("Something went wrong\n");
            }
        }
        else if(command.equals("sinagle")) {
            if(state < 0 || state > 1) {
                Serial.printf("Error: State is not 0 or 1\n");
                return;
            }
            if(switchArr[cluster].SingleStaticSwitch(state) == 0) {
                Serial.printf("Switch %i changed to static state %i\n", cluster, state);
            }
            else {
                Serial.printf("Something went wrong\n");
            }
        }
        else if(command.equals("pwm")) {
            if(state < 0 || state > 255) {
                Serial.printf("Error: Duty cycle is not between 0 and 100\n");
                return;
            }
            if(switchArr[cluster].SinglePWMSwitch(state) == 0) {
                Serial.printf("Switch %d changed to duty cycle %d%%\n", cluster, state);
            }
            else {
                Serial.printf("Something went wrong\n");
            }
        }
        else if(command.equals("test")) {
            if(switchArr[cluster].TestSwitches() == 0) {
                Serial.printf("Switches tested\n");
            }
            else {
                Serial.printf("Something went wrong\n");
            }
        }

        else {
            Serial.printf("Invalid command\n");
        }
    }

}