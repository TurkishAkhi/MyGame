#include "MapRenderer.h"

MapRenderer::MapRenderer() {} 

MapCountry MapRenderer::makeCountry(int id, const std::string& name,
                                     sf::Color col, sf::Color border,
                                     std::vector<sf::Vector2f> pts) {
    MapCountry mc;
    mc.countryId  = id;
    mc.name       = name;
    mc.color      = col;
    mc.borderColor= border;
    mc.shape.setPointCount(pts.size());
    for (size_t i = 0; i < pts.size(); i++)
        mc.shape.setPoint(i, pts[i]);
    mc.shape.setFillColor(col);
    mc.shape.setOutlineColor(border);
    mc.shape.setOutlineThickness(1.5f);
    return mc;
}

void MapRenderer::build() {
    countries.clear();

    // --- Playable countries ---
    countries.push_back(makeCountry(1, "Germany",
        sf::Color(74,122,181), sf::Color(46,90,138), {
        {358,168},{372,162},{390,165},{405,172},{412,185},
        {408,200},{415,212},{410,225},{395,230},{382,238},
        {370,232},{358,240},{345,235},{338,220},{340,205},
        {348,192},{352,178}
    }));

    countries.push_back(makeCountry(2, "France",
        sf::Color(90,158,111), sf::Color(58,122,80), {
        {290,240},{308,232},{325,235},{338,220},{345,235},
        {340,252},{348,268},{338,282},{322,290},{305,285},
        {292,275},{280,262},{278,248}
    }));

    countries.push_back(makeCountry(3, "Italy",
        sf::Color(196,127,58), sf::Color(154,94,32), {
        {348,268},{362,262},{375,268},{380,282},{372,298},
        {368,315},{358,330},{345,340},{335,328},{330,312},
        {335,295},{338,282}
    }));

    // --- Neutral countries (id = -1) ---
    sf::Color neutCol  {107,107,138};
    sf::Color neutBord {74, 74, 106};

    countries.push_back(makeCountry(-1, "Spain", neutCol, neutBord, {
        {240,268},{265,260},{278,248},{280,262},{292,275},
        {285,290},{268,298},{248,295},{235,282},{232,268}
    }));
    countries.push_back(makeCountry(-1, "UK", neutCol, neutBord, {
        {270,168},{282,162},{292,168},{295,180},{288,192},
        {275,195},{265,188},{262,175}
    }));
    countries.push_back(makeCountry(-1, "Poland", neutCol, neutBord, {
        {412,185},{432,180},{448,185},{452,198},{445,212},
        {432,218},{415,212},{408,200}
    }));
    countries.push_back(makeCountry(-1, "Sweden", neutCol, neutBord, {
        {372,100},{388,92},{400,98},{405,115},{398,132},
        {385,138},{372,132},{365,118},{368,105}
    }));
    countries.push_back(makeCountry(-1, "Norway", neutCol, neutBord, {
        {340,88},{358,80},{372,85},{372,100},{368,105},
        {358,108},{345,105},{335,95}
    }));
    countries.push_back(makeCountry(-1, "Austria", neutCol, neutBord, {
        {382,238},{395,230},{410,235},{415,248},{405,255},
        {390,258},{378,252}
    }));
    countries.push_back(makeCountry(-1, "Portugal", neutCol, neutBord, {
        {225,268},{232,262},{232,268},{235,282},{228,288},
        {218,282},{215,270}
    }));
    countries.push_back(makeCountry(-1, "Switzerland", neutCol, neutBord, {
        {338,252},{350,248},{360,252},{358,262},{348,268},{338,262}
    }));
}

void MapRenderer::draw(sf::RenderWindow& win, int selectedId) {
    for (auto& mc : countries) {
        sf::Color fill = mc.color;
        float outlineThick = 1.5f;

        if (mc.countryId == selectedId && selectedId != -1) {
            // Brighten selected country
            fill = sf::Color(
                std::min(255, (int)mc.color.r + 60),
                std::min(255, (int)mc.color.g + 60),
                std::min(255, (int)mc.color.b + 60)
            );
            outlineThick = 3.f;
        }
        mc.shape.setFillColor(fill);
        mc.shape.setOutlineThickness(outlineThick);
        win.draw(mc.shape);
    }
}

int MapRenderer::getClickedId(sf::Vector2f mousePos) {
    // Check playable countries first (on top)
    for (auto& mc : countries) {
        if (mc.countryId == -1) continue;
        if (mc.shape.getGlobalBounds().contains(mousePos))
            return mc.countryId;
    }
    return -1;
}