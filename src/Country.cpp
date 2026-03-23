#include "Country.h"
#include <iostream>

void Country::display() const {
    std::cout << "=== " << name << " (ID: " << id << ") ===\n";
    std::cout << "  Provinces (" << provinces.size() << "):\n";
    for (const auto& province : provinces) {
        std::cout << "    - " << province.name << " (Province ID: " << province.id << ")\n";
    }
    std::cout << "\n";
}

void Country::displayStats() const {
    std::cout << "=== " << name << " Stats ===\n";
    std::cout << "  Manpower  : " << manpower  << "k men\n";
    std::cout << "  Industry  : " << industry  << " factories\n";
    std::cout << "  Resources : " << resources << " units\n";  // NEW
    std::cout << "\n";
}

// NEW: each turn, gain resources based on industry
void Country::advanceTurn() {
    int gained = industry / 10;
    resources += gained;
}