#pragma once
#include <SFML/Graphics.hpp>
#include <vector>
#include <string>

struct MapCountry {
    int countryId;          // -1 = neutral (not playable)
    std::string name;
    sf::Color color;
    sf::Color borderColor;
    sf::ConvexShape shape;
};

class MapRenderer {
public:
    MapRenderer();
    void build();           // Call once to set up all shapes
    void draw(sf::RenderWindow& win, int selectedId);
    int getClickedId(sf::Vector2f mousePos); // returns countryId or -1

private:
    std::vector<MapCountry> countries;
    MapCountry makeCountry(int id, const std::string& name,
                           sf::Color col, sf::Color border,
                           std::vector<sf::Vector2f> points);
};