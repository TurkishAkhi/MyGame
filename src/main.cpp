#include <SFML/Graphics.hpp>
#include <vector>
#include <string>
#include <sstream>
#include "Country.h"
#include "Province.h"
#include "MapRenderer.h"

const int WIN_W     = 900;
const int WIN_H     = 600;
const int SIDEBAR_W = 180;
const int TOPBAR_H  = 50;

const sf::Color COL_BG          {26,  28,  36};
const sf::Color COL_PANEL       {18,  19,  26};
const sf::Color COL_BORDER      {46,  49,  64};
const sf::Color COL_GOLD        {184, 150,  62};
const sf::Color COL_TEXT        {201, 205, 216};
const sf::Color COL_TEXT_DIM    {85,  90,  110};
const sf::Color COL_TEXT_BRIGHT {232, 223, 192};
const sf::Color COL_GREEN       {106, 158,  90};
const sf::Color COL_HOVER       {30,  32,  48};
const sf::Color COL_OCEAN       {30,  37,  53};

void drawRect(sf::RenderWindow& win, float x, float y, float w, float h,
              sf::Color fill, sf::Color border = sf::Color::Transparent, float t = 1.f) {
    sf::RectangleShape r({w, h});
    r.setPosition({x, y});
    r.setFillColor(fill);
    if (border != sf::Color::Transparent) { r.setOutlineThickness(t); r.setOutlineColor(border); }
    win.draw(r);
}

void drawText(sf::RenderWindow& win, const sf::Font& font, const std::string& str,
              float x, float y, unsigned int size, sf::Color color) {
    sf::Text t(font, str, size);
    t.setPosition({x, y});
    t.setFillColor(color);
    win.draw(t);
}

bool drawButton(sf::RenderWindow& win, const sf::Font& font, const std::string& label,
                float x, float y, float w, float h, sf::Color bg, sf::Color tc,
                bool hover, bool clicked) {
    drawRect(win, x, y, w, h, hover ? sf::Color(212,174,82) : bg);
    sf::Text t(font, label, 12);
    t.setFillColor(tc);
    auto tb = t.getLocalBounds();
    t.setPosition({x+(w-tb.size.x)/2.f, y+(h-tb.size.y)/2.f-2});
    win.draw(t);
    return clicked && sf::FloatRect({x,y},{w,h}).contains(
        sf::Vector2f(sf::Mouse::getPosition(win)));
}

int main() {
    // --- Data ---
    Province berlin={1,"Berlin",1}, hamburg={2,"Hamburg",1}, munich={3,"Munich",1};
    Province paris={4,"Paris",2},   lyon={5,"Lyon",2},       marseille={6,"Marseille",2};
    Province rome={7,"Rome",3},     milan={8,"Milan",3},     naples={9,"Naples",3};

    std::vector<Country> countries = {
        {1,"Germany",800,120,0,{berlin,hamburg,munich}},
        {2,"France", 600, 90,0,{paris,lyon,marseille}},
        {3,"Italy",  400, 60,0,{rome,milan,naples}},
    };

    int selectedIdx = 0;
    int turn = 1;
    std::vector<std::string> eventLog = {"Turn 1 - game started."};

    // --- Map ---
    MapRenderer mapRenderer;
    mapRenderer.build();

    // --- Window ---
    sf::RenderWindow window(sf::VideoMode({(unsigned)WIN_W,(unsigned)WIN_H}), "HOI4 Clone");
    window.setFramerateLimit(60);
    sf::Font font;
    if (!font.openFromFile("assets/font.ttf")) return -1;

    // Map viewport (right of sidebar, below topbar)
    sf::View mapView(sf::FloatRect({0,0},{720,590}));
    mapView.setViewport(sf::FloatRect(
        {(float)SIDEBAR_W/WIN_W, (float)TOPBAR_H/WIN_H},
        {1.f - (float)SIDEBAR_W/WIN_W, 1.f - (float)TOPBAR_H/WIN_H}
    ));

    while (window.isOpen()) {
        sf::Vector2i mouse = sf::Mouse::getPosition(window);
        bool clicked = false;

        while (const std::optional ev = window.pollEvent()) {
            if (ev->is<sf::Event::Closed>()) window.close();
            if (ev->is<sf::Event::MouseButtonPressed>()) {
                clicked = true;
                // Convert mouse to map coordinates
                sf::Vector2f mapMouse = window.mapPixelToCoords(mouse, mapView);
                int clickedId = mapRenderer.getClickedId(mapMouse);
                if (clickedId != -1) {
                    for (int i = 0; i < (int)countries.size(); i++)
                        if (countries[i].id == clickedId) { selectedIdx = i; break; }
                }
            }
        }

        window.clear(COL_BG);

        // === TOP BAR ===
        drawRect(window, 0, 0, WIN_W, TOPBAR_H, COL_PANEL, COL_BORDER);
        drawText(window, font, "HOI4 CLONE", 20, 14, 14, COL_GOLD);
        drawText(window, font, "TURN", WIN_W-240, 10, 10, COL_TEXT_DIM);
        drawText(window, font, std::to_string(turn), WIN_W-200, 8, 22, COL_TEXT_BRIGHT);

        float bx=WIN_W-155, by=10, bw=135, bh=30;
        bool bHov = sf::FloatRect({bx,by},{bw,bh}).contains(sf::Vector2f(mouse));
        if (drawButton(window, font, "ADVANCE TURN >", bx, by, bw, bh, COL_GOLD, COL_BG, bHov, clicked)) {
            for (auto& c : countries) c.advanceTurn();
            turn++;
            std::ostringstream oss;
            oss << "Turn " << turn << " - ";
            for (size_t i=0; i<countries.size(); i++) {
                oss << countries[i].name << " +" << countries[i].industry/10;
                if (i < countries.size()-1) oss << ", ";
            }
            oss << " resources.";
            eventLog.push_back(oss.str());
            if (eventLog.size() > 5) eventLog.erase(eventLog.begin());
        }

        // === SIDEBAR ===
        drawRect(window, 0, TOPBAR_H, SIDEBAR_W, WIN_H-TOPBAR_H, COL_PANEL, COL_BORDER);
        drawText(window, font, "COUNTRIES", 14, TOPBAR_H+12, 9, COL_TEXT_DIM);
        for (int i=0; i<(int)countries.size(); i++) {
            float ty = TOPBAR_H + 35 + i*40.f;
            sf::FloatRect tab({0,ty},{(float)SIDEBAR_W,36});
            bool th = tab.contains(sf::Vector2f(mouse));
            drawRect(window, 0, ty, SIDEBAR_W, 36, (i==selectedIdx||th)?COL_HOVER:COL_PANEL);
            if (i==selectedIdx) drawRect(window, 0, ty, 3, 36, COL_GOLD);
            drawText(window, font, countries[i].name, 16, ty+10, 13,
                     i==selectedIdx ? COL_TEXT_BRIGHT : COL_TEXT);
            if (clicked && th) selectedIdx = i;
        }

        // === INFO BOX (bottom-left of map) ===
        Country& c = countries[selectedIdx];
        float ix = SIDEBAR_W+12, iy = WIN_H-110;
        drawRect(window, ix, iy, 210, 98, COL_PANEL, COL_BORDER);
        drawText(window, font, c.name,                    ix+12, iy+10, 15, COL_TEXT_BRIGHT);
        drawText(window, font, "Manpower : "+std::to_string(c.manpower)+"k", ix+12, iy+34, 11, COL_TEXT);
        drawText(window, font, "Industry : "+std::to_string(c.industry)+" fac", ix+12, iy+50, 11, COL_TEXT);
        drawText(window, font, "Resources: "+std::to_string(c.resources)+
                 "  (+"+std::to_string(c.industry/10)+"/turn)", ix+12, iy+66, 11, COL_GREEN);

        // === MAP (drawn with map view) ===
        window.setView(mapView);
        drawRect(window, 0, 0, 720, 590, COL_OCEAN);
        mapRenderer.draw(window, countries[selectedIdx].id);
        window.setView(window.getDefaultView());

        window.display();
    }
    return 0;
}