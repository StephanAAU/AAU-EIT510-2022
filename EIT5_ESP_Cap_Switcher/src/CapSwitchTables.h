/*
 * CapSwitchTables.h - Header file for tables and variables
*/

#ifndef CapSwitchTables_h
#define CapSwitchTables_h

static const unsigned short CapTableTest[16][2] = {
    {0,  0b0000},
    {1,  0b0001},
    {2,  0b0010},
    {3,  0b0011},
    {4,  0b0100},
    {5,  0b0101},
    {6,  0b0110},
    {7,  0b0111},
    {8,  0b1000},
    {9,  0b1001},
    {10, 0b1010},
    {11, 0b1011},
    {12, 0b1100},
    {13, 0b1101},
    {14, 0b1110},
    {15, 0b1111},
};

static const int tableSize = 2;
static const unsigned short CapTable[tableSize][2] = {
    {0, 0b0},
    {1, 0b1},
};

#endif