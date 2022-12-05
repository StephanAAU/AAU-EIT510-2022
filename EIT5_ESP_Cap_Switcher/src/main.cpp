

#include <Arduino.h>
#include <Esp.h>
#include <CapSwitch.h>

/* Set up cap switches */
// CapSwitch switch1(4, 32); // Pins 34-35 do not work on my board
// CapSwitch switch2(4, 16);
// CapSwitch switchTrim; // THIS IS A SINGLE PIN AT PIN 30
// const int switchArrSize = 3;
// CapSwitch switchArr[switchArrSize] = {switch1, switch2, switchTrim};

CapSwitch sw0(18, "sw0");
CapSwitch sw1(5, "sw1");
CapSwitch sw2(17, "sw2");
CapSwitch sw3(16, "sw3");

CapSwitch sw4(23, "sw4");
CapSwitch sw5(22, "sw5");
CapSwitch sw6(21, "sw6");
CapSwitch sw7(19, "sw7");

CapSwitch swTune(13, "swTune");

const int switchArrSize = 9;
CapSwitch switchArr[switchArrSize] = {sw0, sw1, sw2, sw3, sw4, sw5, sw6, sw7, swTune};

Preferences prefs;
char prefNameSpace[] = "defaultPins";

int PutPreference(CapSwitch sw) {
    char prefArr[sw._pref_name.length() + 1];
    strcpy(prefArr, sw._pref_name.c_str());

    prefs.putBool(prefArr, sw._single_pin_state);

    return 0;
}

int GetPreference(CapSwitch sw) {
    char prefArr[sw._pref_name.length() + 1];
    strcpy(prefArr, sw._pref_name.c_str());

    bool state = prefs.getBool(prefArr, false);

    digitalWrite((sw._pin_start), state);
    sw._single_pin_state = state;

    return 0;
}

void setup() {
    Serial.begin(115200);
    while(!Serial) {}
    Serial.println("Setup happening");

    ledcSetup(1, 12000, 8);

    prefs.begin(prefNameSpace, false);

    for(int i = 0; i < switchArrSize; i++) {
        GetPreference(switchArr[i]);
    }

    Serial.begin(115200);
    Serial.println("Ready to receive\n");
    
}

void loop() {
    if(Serial.available()) {
        // Form will be *,*,*

        String command = Serial.readStringUntil(',');
        int cluster    = Serial.readStringUntil(',').toInt();
        int state      = Serial.readStringUntil('\n').toInt();

        if(cluster < 0 || cluster > switchArrSize) {
            Serial.printf("Error: Cluster number out of bounds\n");
            return;
        }
        else if(command.equals("single")) {
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
        else if(command.equals("save")) {
            for(int i = 0; i < switchArrSize; i++) {
                PutPreference(switchArr[i]);
            }
            Serial.printf("Setup saved");
        }

        else {
            Serial.printf("Invalid command\n");
        }
    }
}

// void loop() {
//     if(Serial.available()) {
//         // Form will be *,*,*

//         String command = Serial.readStringUntil(',');
//         int cluster    = Serial.readStringUntil(',').toInt();
//         int state      = Serial.readStringUntil('\n').toInt();

//         // if(cluster == 0 || state == 0) {return;}

//         if(cluster < 0 || cluster > switchArrSize) {
//             Serial.printf("Error: Cluster number out of bounds\n");
//             return;
//         }
//         if(command.equals("static")) {
//             if(switchArr[cluster].ClusterStaticSwitch(state) == 0) {
//                 Serial.printf("Switch cluster %i changed to static state %i\n", cluster, state);
//             }
//             else {
//                 Serial.printf("Something went wrong\n");
//             }
//         }
//         else if(command.equals("single")) {
//             if(state < 0 || state > 1) {
//                 Serial.printf("Error: State is not 0 or 1\n");
//                 return;
//             }
//             if(switchArr[cluster].SingleStaticSwitch(state) == 0) {
//                 Serial.printf("Switch %i changed to static state %i\n", cluster, state);
//             }
//             else {
//                 Serial.printf("Something went wrong\n");
//             }
//         }
//         else if(command.equals("pwm")) {
//             if(state < 0 || state > 255) {
//                 Serial.printf("Error: Duty cycle is not between 0 and 100\n");
//                 return;
//             }
//             if(switchArr[cluster].SinglePWMSwitch(state) == 0) {
//                 Serial.printf("Switch %d changed to duty cycle %d%%\n", cluster, state);
//             }
//             else {
//                 Serial.printf("Something went wrong\n");
//             }
//         }
//         else if(command.equals("test")) {
//             if(switchArr[cluster].TestSwitches() == 0) {
//                 Serial.printf("Switches tested\n");
//             }
//             else {
//                 Serial.printf("Something went wrong\n");
//             }
//         }

//         else {
//             Serial.printf("Invalid command\n");
//         }
//     }

// }