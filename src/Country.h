#pragma once
#include <string>
#include <vector>
#include "Province.h"

struct Country {
    int id;
    std::string name;

    int manpower;    // Available recruits (in thousands)
    int industry;    // Industrial capacity (factories)
    int resources;   // NEW: current stockpile, grows each turn

    std::vector<Province> provinces;

    void display() const;
    void displayStats() const;

    // NEW: called every time the player advances a turn
    void advanceTurn();
};