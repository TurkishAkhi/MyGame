#pragma once
#include <string>

struct Province {
    int id;
    std::string name;
    int ownerCountryId;  // Which country owns this province
};