/*
 * CapSwitch.h - Library for switching capacitors in an antenna system
*/
// lul
/* Include header file */
#include "CapSwitch.h"

/* Include header file for tables */
#include "CapSwitchTables.h"

/*
 * Constructor
 * Output: None
 * Remarks:
 * The following function sets up the capacitor switch board
 * Base switch pin is pin 30. Only 1 switch is started at base
*/
// CapSwitch::CapSwitch(uint8_t cap_amount, uint8_t pin_start) {
//     /* Set variables given to constructor */
//     _cap_amount = cap_amount;
//     _pin_start = pin_start;

//     /* Set pins as outputs */
//     for(int i = 0; i < _cap_amount; i++) {
//         pinMode((_pin_start + i), OUTPUT);
//     }
// }

CapSwitch::CapSwitch(uint8_t cap, String prefName) {
    _pin_start = cap;
    _pref_name = prefName;
    /* Set pin as outputs */
    pinMode(cap, OUTPUT);
}

/*
 * Name: FindTableIndex
 * Input: val
 * Output: Index
*/
int CapSwitch::FindTableIndex(uint8_t val) {
    
    for(int i = 0; i < tableSize; i++) {
        if(CapTable[i][0] == val) {
            return i;
        }
    }

    return -1;
}
int CapSwitch::FindTestTableIndex(uint8_t val) {
    
    for(int i = 0; i < 16; i++) {
        if(CapTableTest[i][0] == val) {
            return i;
        }
    }

    return -1;
}

/*
 * Name: StaticSwitch
 * Input: capState
 * Output: Error code
 * Remarks:
 * 
*/
int CapSwitch::ClusterStaticSwitch(uint8_t capState) {
    
    unsigned char b;
    int tableIndex = FindTableIndex(capState);
    if(tableIndex == -1) {return 1;}

    for(int j = _cap_amount - 1; 0 <= j; j--) {
        b = (CapTable[tableIndex][1] >> j) & 0b01;
        uint8_t capPin = _pin_start + j;

        if(b) {
            digitalWrite(capPin, HIGH);
        }
        else {
            digitalWrite(capPin, LOW);
        }
    }
    
    return 0;
}

/*
 * Name: SingleStaticSwitch
 * Input: capState
 * Output: Error code
 * Remarks:
*/
int CapSwitch::SingleStaticSwitch(uint8_t capState) {

    // digitalWrite((_pin_start), !_single_pin_state);
    // _single_pin_state = !_single_pin_state;

    digitalWrite((_pin_start), capState);
    _single_pin_state = capState;

    return 0;
}

/*
 * Name: PWMSwitch
 * Input: dutyVal
 * Output: Error code
 * Remarks:
*/
int CapSwitch::SinglePWMSwitch(uint8_t dutyVal) {
    
    int pwmVal = map(dutyVal, 0, 100, 0, 255);

    ledcAttachPin(_pin_start, 1);
    ledcWrite(_pin_start, pwmVal);
    ledcDetachPin(_pin_start);

    return 0;
}

/*
 * Name: TestSwitches
 * Input: 
 * Output: Error code
 * Remarks: uses CapTableTest LUT
*/
int CapSwitch::TestSwitches() {

    /* 16 test cases in the LUT */
    for(int i = 0; i < 16; i++) {

        unsigned char b;
        int tableIndex = FindTestTableIndex(i);
        if(tableIndex == -1) {return 1;}
        
        for(int j = 3; 0 <= j; j--) {
            // b = (CapTableTest[i][1] >> j) & 0b01;
            b = (CapTableTest[tableIndex][1] >> j) & 0b01;
            uint8_t capPin = _pin_start + j;

            if(b) {
                digitalWrite(capPin, HIGH);
                Serial.printf("Writing HIGH to pin %i\n", capPin);
            }
            else {
                digitalWrite(capPin, LOW);
                Serial.printf("Writing LOW to pin %i\n", capPin);
            }
        }
        Serial.printf("\n");
        delay(1000);
    }

    return 0;
}