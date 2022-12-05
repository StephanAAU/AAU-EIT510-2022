/*
 * CapSwitch.h - Library for switching capacitors in an antenna system
*/

/* Include necessary libraries */
#include <esp32-hal-ledc.h>
#include <Esp.h>
#include <stdint.h>
#include <Preferences.h>

#ifndef CapSwitch_h
#define CapSwitch_h

class CapSwitch {
    private:
        /* Base variables */
        static const uint8_t BASE_CAP_AMOUNT = 1;
        static const uint8_t BASE_PIN_START = 30;

        

        /* Another base variable */
        

        int FindTableIndex(uint8_t val);
        int FindTestTableIndex(uint8_t val);

    public:
        /* Variables set by constructor */
        uint8_t _cap_amount;
        uint8_t _pin_start;
        
        /* Variables */
        String _pref_name;
        bool _single_pin_state = false;

        /* Functions */
        // CapSwitch(uint8_t cap_amount = BASE_CAP_AMOUNT, uint8_t pin_start = BASE_PIN_START);
        CapSwitch(uint8_t cap, String prefName);
        int ClusterStaticSwitch(uint8_t capState);
        int SingleStaticSwitch(uint8_t capState);
        int SinglePWMSwitch(uint8_t pwmVal);

        int TestSwitches();
};

#endif