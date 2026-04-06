import pygame
import sys
import math
import json
import os
import random

# ═══════════════════════════════════════════════════
#  PROJEKT FRONTLINE  v6.0
#  NEU: Schwierigkeitsgrad, Achievements, Pause-Menü,
#       Spieler-Skins, Waffen-Upgrades / Level-Up
# ═══════════════════════════════════════════════════

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT  = 1200, 600
WORLD_WIDTH    = 4800
screen         = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT  = screen.get_size()   # ← passt sich deinem Monitor an
pygame.display.set_caption("PROJEKT FRONTLINE  v7.0")
clock          = pygame.time.Clock()
FPS            = 60

# ═══════════════════════════════════════════════════
#  V7.0 COLOR PALETTE — EXTENDED
# ═══════════════════════════════════════════════════
RED         = (220,  50,  50)
GREEN       = ( 50, 210,  85)
YELLOW      = (245, 215,  55)
WHITE       = (255, 255, 255)
GRAY        = (150, 150, 155)
DARK        = ( 12,  12,  18)
ORANGE      = (245, 135,  35)
CYAN        = ( 55, 225, 225)

FLAME_COL   = (255, 120,  20)
EMP_COL     = (140, 255, 255)
SHIELD_COL  = ( 80, 180, 255)

BULLET_COL  = (255, 245, 110)
SNIPER_COL  = (110, 225, 255)
ROCKET_COL  = (255, 105,  35)
GRENADE_COL = ( 85, 165,  85)

WATER_COL   = ( 20,  80, 165)
BUBBLE_COL  = (105, 185, 255)
TORPEDO_COL = ( 55, 225, 185)
SPEAR_COL   = (185, 225, 255)
SKY_ZONE_COL= (185, 215, 255)

NEON_PINK   = (255,  60, 180)
NEON_BLUE   = ( 60, 130, 255)
ACID_GREEN  = ( 80, 255, 120)
DEEP_RED    = (140,  10,  10)
GOLD        = (255, 195,  50)
SILVER      = (190, 195, 210)
SHADOW_COL  = (  8,   6,  18)
FOG_LIGHT   = (200, 215, 240)

# V7.0 NEW COLORS
LAVA_COL        = (255,  60,   0)
LAVA_GLOW       = (255, 140,  20)
SPACE_BLUE      = (  5,   8,  28)
PLASMA_COL      = (180,  50, 255)
PLASMA_GLOW     = (220, 120, 255)
TOXIC_GREEN     = ( 80, 255,  60)
TOXIC_DARK      = ( 30,  80,  20)
NEON_ORANGE     = (255, 140,  20)
STEEL_BLUE      = ( 70,  90, 130)
VOID_PURPLE     = ( 40,   5,  70)
HOLOGRAM_CYAN   = ( 40, 220, 210)
EXPLOSION_WHITE = (255, 245, 235)
BLOOD_RED       = (160,   8,   8)
ELECTRIC_BLUE   = ( 30,  80, 255)
MAGMA_ORANGE    = (255,  85,   0)
ICE_BLUE        = (160, 210, 255)
RUST_COL        = (140,  70,  30)
CHROME_COL      = (200, 210, 220)

# V7.0 ZONE SKY GRADIENTS (zones 1-8)
ZONE_SKY = {
    1: ((22, 28, 48),   (40, 55, 90)),
    2: ((12, 32, 14),   (28, 58, 24)),
    3: ((72, 48, 22),   (130, 90, 38)),
    4: (( 8,  8, 22),   (18, 18, 44)),
    5: ((140,170,205),  (200, 225, 248)),
    6: (( 5,  3, 14),   (14,  8, 30)),
    # NEW V7 ZONES
    7: ((28,  8,  4),   (80,  25,  8)),   # Volcanic — deep red-orange
    8: (( 2,  2, 10),   ( 5,  5, 20)),    # Space Station — near-black
}

ZONE_GROUND = {
    1: (( 55, 42, 30), ( 80, 62, 40), (42, 32, 22)),
    2: (( 30, 55, 22), ( 50, 80, 32), (20, 38, 14)),
    3: ((125, 88, 40), (165,118, 58), (90, 62, 28)),
    4: (( 35, 35, 48), ( 55, 55, 72), (22, 22, 32)),
    5: ((175,195,218), (210, 228, 248),(140,160,185)),
    6: (( 25, 18, 38), ( 42, 30, 62), (15, 10, 25)),
    # NEW V7 ZONES
    7: ((100, 35, 10), (145,  55, 18), (70, 20,  5)),   # Volcanic — dark basalt
    8: (( 18, 22, 32), ( 30, 38, 55), (10, 14, 22)),    # Space Station — metal panels
}

GROUND_Y            = HEIGHT - 80
HIGHSCORE_FILE      = "frontline_scores.json"
ACHIEVEMENTS_FILE   = "frontline_achievements.json"
SETTINGS_FILE       = "frontline_settings.json"
NUM_ZONES           = 8   # V7: expanded from 6 to 8

GROUND_Y            = HEIGHT - 80
HIGHSCORE_FILE      = "frontline_scores.json"
ACHIEVEMENTS_FILE   = "frontline_achievements.json"
SETTINGS_FILE = "frontline_settings.json"

DEFAULT_SETTINGS = {
    "master_volume": 0.8,
    "sfx_volume":    1.0,
    "fps_cap":       60,
    "resolution":    "fullscreen",
    "screenshake":   True,
    "particles":     True,
    "show_fps":      False,
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            for k, v in DEFAULT_SETTINGS.items():
                if k not in data:
                    data[k] = v
            return data
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)

def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

def apply_settings(s):
    vol = s["master_volume"] * s["sfx_volume"]
    try:
        if 'SFX' not in globals(): return
        for attr in vars(SFX):
            obj = getattr(SFX, attr)
            if isinstance(obj, pygame.mixer.Sound):
                obj.set_volume(vol)
    except Exception:
        pass

SETTINGS = load_settings()
# Apply FPS from settings immediately
_cap = SETTINGS.get("fps_cap", 60)
FPS  = _cap if _cap and _cap > 0 else 9999
CAMERA_LERP         = 0.10
PARTICLE_FRICTION   = 0.97
GRENADE_THROW_CHANCE= 0.005

# ═══════════════════════════════════════════════════
#  SCHWIERIGKEITSGRAD
# ═══════════════════════════════════════════════════
DIFFICULTY_SETTINGS = {
    "easy": {
        "label": "EINFACH",
        "color": GREEN,
        "enemy_hp_mult":    0.6,
        "enemy_speed_mult": 0.7,
        "enemy_dmg_mult":   0.6,
        "shoot_rate_mult":  1.5,   # höher = langsamer
        "player_hp_bonus":  50,
        "score_mult":       0.7,
        "desc": "Für Einsteiger — Feinde schwächer, mehr HP",
    },
    "normal": {
        "label": "NORMAL",
        "color": YELLOW,
        "enemy_hp_mult":    1.0,
        "enemy_speed_mult": 1.0,
        "enemy_dmg_mult":   1.0,
        "shoot_rate_mult":  1.0,
        "player_hp_bonus":  0,
        "score_mult":       1.0,
        "desc": "Klassisches Erlebnis",
    },
    "hard": {
        "label": "SCHWER",
        "color": RED,
        "enemy_hp_mult":    1.5,
        "enemy_speed_mult": 1.3,
        "enemy_dmg_mult":   1.4,
        "shoot_rate_mult":  0.7,   # niedriger = schneller
        "player_hp_bonus":  -20,
        "score_mult":       1.5,
        "desc": "Nur für Profis — 1.5x Score",
    },
}
current_difficulty = "normal"

def get_diff():
    return DIFFICULTY_SETTINGS[current_difficulty]

SKINS = {
    "standard": {
        "label":    "Infanterist",
        "body":     (62, 88, 54),
        "head":     (188, 148, 102),
        "helmet":   (48, 66, 40),
        "vest":     (52, 78, 44),
        "boot":     (28, 22, 14),
        "glove":    (42, 34, 22),
        "desc":     "Woodland MARPAT — Standardausrüstung",
        "unlock":   None,
    },
    "desert": {
        "label":    "Wüstenjäger",
        "body":     (168, 132, 72),
        "head":     (198, 158, 108),
        "helmet":   (148, 112, 58),
        "vest":     (158, 122, 64),
        "boot":     (88, 68, 38),
        "glove":    (108, 82, 48),
        "desc":     "Desert DCU — Sandtarn Spezialist",
        "unlock":   None,
    },
    "arctic": {
        "label":    "Arktis-Ranger",
        "body":     (208, 218, 228),
        "head":     (215, 208, 198),
        "helmet":   (192, 202, 215),
        "vest":     (198, 210, 222),
        "boot":     (148, 158, 168),
        "glove":    (178, 188, 198),
        "desc":     "Arctic Multicam — Kälteresistent",
        "unlock":   "zone_5",
    },
    "shadow": {
        "label":    "Schattenkrieger",
        "body":     (28, 28, 36),
        "head":     (48, 42, 38),
        "helmet":   (18, 18, 26),
        "vest":     (22, 22, 32),
        "boot":     (12, 12, 16),
        "glove":    (18, 14, 10),
        "desc":     "Black Ops — Nacht-Ops Spezialist",
        "unlock":   "all_zones",
    },
}
current_skin = "standard"

# ═══════════════════════════════════════════════════
#  ACHIEVEMENTS
# ═══════════════════════════════════════════════════
ACHIEVEMENTS_DEF = {
    "first_blood":   {"name":"Erster Schuss",      "desc":"Ersten Feind besiegt",            "icon":"🎯"},
    "zone_1":        {"name":"Stadtbefreier",       "desc":"Zone 1 abgeschlossen",            "icon":"🏙"},
    "zone_3":        {"name":"Wüstensturm",         "desc":"Zone 3 abgeschlossen",            "icon":"🏜"},
    "zone_5":        {"name":"Arktis-Krieger",      "desc":"Zone 5 abgeschlossen",            "icon":"❄"},
    "all_zones":     {"name":"Befreier",            "desc":"Alle 6 Zonen abgeschlossen",      "icon":"🏆"},
    "tank_killer":   {"name":"Panzerknacker",       "desc":"Ersten Tank zerstört",            "icon":"💥"},
    "air_ace":       {"name":"Luftass",             "desc":"10 Luftfeinde abgeschossen",      "icon":"✈"},
    "combo_5":       {"name":"Combo-Meister",       "desc":"5er-Combo erreicht",              "icon":"⚡"},
    "no_damage":     {"name":"Unberührt",           "desc":"Zone ohne Schaden abgeschlossen", "icon":"🛡"},
    "grenade_multi": {"name":"Sprengmeister",       "desc":"3 Feinde mit einer Granate",      "icon":"💣"},
    "weapon_max":    {"name":"Waffenarsenal",       "desc":"Waffe auf Max-Level gebracht",    "icon":"⬆"},
    "hard_clear":    {"name":"Eiserner Wille",      "desc":"Spiel auf Schwer abgeschlossen",  "icon":"💀"},
    "score_10k":     {"name":"10.000 Punkte",       "desc":"10.000 Score erreicht",           "icon":"🌟"},
    "knife_only":    {"name":"Nahkämpfer",          "desc":"Zone mit Messer abgeschlossen",   "icon":"🔪"},
    # V7.0 NEW ACHIEVEMENTS
    "zone_7":        {"name":"Lavabezwinger",        "desc":"Zone 7 abgeschlossen",            "icon":"🌋"},
    "zone_8":        {"name":"Kosmischer Krieger",   "desc":"Zone 8 abgeschlossen",            "icon":"🚀"},
    "base_master":   {"name":"Festungsbauer",        "desc":"5 Basis-Strukturen gebaut",       "icon":"🏗"},
    "mine_killer":   {"name":"Minenmeister",         "desc":"5 Feinde mit Minen getötet",      "icon":"💣"},
    "mech_slayer":   {"name":"Mech-Jäger",           "desc":"Sniper-Mech zerstört",            "icon":"🤖"},
    "riot_breaker":  {"name":"Schildbrecher",        "desc":"10 Riot-Soldaten besiegt",        "icon":"🛡"},
    "score_50k":     {"name":"50.000 Punkte",        "desc":"50.000 Score erreicht",           "icon":"💫"},
    "no_damage_v7":  {"name":"Unverwundbar",         "desc":"Zone 7 oder 8 ohne Schaden",      "icon":"⚡"},
    "coop_kill":     {"name":"Teamwork",             "desc":"Im Co-op 50 Feinde besiegt",      "icon":"🤝"},
}

def load_achievements():
    if os.path.exists(ACHIEVEMENTS_FILE):
        with open(ACHIEVEMENTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_achievement(key):
    data = load_achievements()
    if key not in data:
        data[key] = True
        with open(ACHIEVEMENTS_FILE, "w") as f:
            json.dump(data, f)
        return True  # Neu freigeschaltet!
    return False

# ═══════════════════════════════════════════════════
#  STORY
# ═══════════════════════════════════════════════════
STORY = {
    0: ["GEHEIMAKTE: OPERATION ENDGERICHT — STUFE ROT",
        "Vor 72 Stunden hat General OMEGA alle 8 Sektoren gesperrt.",
        "Er hat Atomcodes gestohlen. Städte fallen. Stille im Funk.",
        "Unser gesamtes Militär: ausgeschaltet. Satellite: tot.",
        "Du wurdest aus dem Gefängnis geholt. Kriegsverbrecherparagraph.",
        "Wir geben dir Waffen, Munition — und eine Chance.",
        "Räume alle 8 Zonen. Töte OMEGA. Frage nicht warum.",
        "Du bist nicht unser Held. Du bist unsere letzte Waffe."],

    1: ["Zone 1 gesäubert — schneller als erwartet.",
        "OMEGA hat unsere Geschwindigkeit unterschätzt.",
        "Er zieht Verstärkung in den Wald. Stealth-Einheiten.",
        "Sie werden dich nicht kommen sehen wollen.",
        "Sei schneller. Sei brutaler.",
        "Zone 2: Wald. Dunkel. Dicht. Tödlich."],

    2: ["Wald unter Kontrolle. Verluste: null.",
        "OMEGAs Panzerdivision rückt durch die Wüste vor.",
        "Drei Panzerregimenter. Mörserstellung im Rücken.",
        "Normale Kugeln prallt an Stahl ab — nutze Raketen [5].",
        "Selbstmordattentäter bewachen die Flanken. Abstand halten.",
        "Die Wüste brennt. Gut so."],

    3: ["Panzerdivision vernichtet. Bemerkenswert.",
        "OMEGAs Militärbasis ist das nächste Ziel.",
        "Schwere Schützen. Riot-Schildsoldaten. Helikopter.",
        "Flanke die Schildträger — von vorne kommst du nicht durch.",
        "Stinger [6] für Luftziele. Immer.",
        "Zeig ihnen, dass keine Basis sicher ist."],

    4: ["Basis gefallen. OMEGA ist wütend.",
        "Er schickt seine Elite in die Arktis.",
        "Sniper-Mechs mit Laser. Flammensoldaten. Jets.",
        "Flammensoldaten töten auf kurze Distanz sofort. ABSTAND.",
        "Sniper-Mech: Laser-Warnung sichtbar — weiche rechtzeitig aus.",
        "In der Arktis gibt es keine zweite Chance."],

    5: ["Arktis gesichert. Du bist ein Monster.",
        "OMEGAs Festung liegt offen. Zone 6.",
        "Drei Kampfphasen. Volle Stärke. Null Gnade.",
        "Phase 1: Bodenkampf. Phase 2: Schild. Phase 3: Luft.",
        "Explosive Waffen sind dein bester Freund.",
        "Bring ihn zu Fall. Aber er hat noch Karten im Ärmel."],

    6: ["Festung Omega — erschüttert. Nicht besiegt.",
        "OMEGA hat sich in ein Vulkangebiet zurückgezogen.",
        "Er will unsere Technik schmelzen. Unsere Moral brechen.",
        "WARNUNG: Lava-Kontakt ist sofortiger Tod.",
        "WARNUNG: Bomber-Jets aus dem Orbit fliegen Angriffswellen.",
        "Baue Deckung [B+F]. Nutze Strukturen zum Überleben.",
        "Flame-Troopers. Sniper-Mechs. Bomber. Alles gleichzeitig.",
        "Wenn du das überlebst — bist du kein Mensch mehr."],

    7: ["Vulkanfront überwunden. Unfassbar.",
        "OMEGA ist in den Orbit geflohen. Raumstation Alpha.",
        "Keine Atmosphäre. Keine Regeln. Keine Verstärkung für dich.",
        "Er hat sich selbst in seine stärkste Form verwandelt.",
        "Gravitations-Pulls. Plasma-Orbs. Sechs Kampfphasen.",
        "Alle Einheitentypen auf einmal. Maximum-Dichte.",
        "Das ist das Ende der Welt — oder das Ende von OMEGA.",
        "Nur einer von euch verlässt diese Station lebendig."],
}

# ═══════════════════════════════════════════════════
#  WAFFEN-UPGRADE SYSTEM
# ═══════════════════════════════════════════════════
WEAPON_UPGRADE_KILLS = [0, 5, 15, 30]  # Kills für Level 1/2/3/4

class WeaponStats:
    """Verwaltet Kills und Level pro Waffe."""
    def __init__(self):
        self.kills = {}   # weapon_name -> kill_count
        self.level = {}   # weapon_name -> level (0-3)
        self.new_level_notif = {}  # weapon_name -> frames_to_show

    def reset(self):
        self.__init__()

    def add_kill(self, weapon_name):
        self.kills[weapon_name] = self.kills.get(weapon_name, 0) + 1
        old_lv = self.level.get(weapon_name, 0)
        new_lv = 0
        for i, threshold in enumerate(WEAPON_UPGRADE_KILLS):
            if self.kills[weapon_name] >= threshold:
                new_lv = i
        self.level[weapon_name] = new_lv
        if new_lv > old_lv:
            self.new_level_notif[weapon_name] = 180  # 3 Sek.
            return True
        return False

    def get_level(self, weapon_name):
        return self.level.get(weapon_name, 0)

    def get_dmg_mult(self, weapon_name):
        lv = self.get_level(weapon_name)
        return 1.0 + lv * 0.25   # +25% pro Level

    def get_fire_rate_mult(self, weapon_name):
        lv = self.get_level(weapon_name)
        return max(0.5, 1.0 - lv * 0.1)  # -10% Cooldown pro Level

    def update_notifs(self):
        for k in list(self.new_level_notif.keys()):
            self.new_level_notif[k] -= 1
            if self.new_level_notif[k] <= 0:
                del self.new_level_notif[k]

    def draw_notifs(self, surf):
        f = pygame.font.SysFont("consolas", 18, bold=True)
        y = HEIGHT // 2 + 40
        for wname, frames in self.new_level_notif.items():
            alpha = min(255, frames * 4)
            lv = self.get_level(wname)
            txt = f"⬆ {wname}  LEVEL {lv}  (+{lv*25}% DMG)"
            s = f.render(txt, True, YELLOW)
            surf_a = pygame.Surface((s.get_width()+20, s.get_height()+8), pygame.SRCALPHA)
            surf_a.fill((0, 0, 0, 100))
            surf_a.blit(s, (10, 4))
            surf_a.set_alpha(alpha)
            surf.blit(surf_a, (WIDTH//2 - surf_a.get_width()//2, y))
            y += 30

WSTATS = WeaponStats()

SKILL_TREE = {
    "combat": {
        "color": (220, 50, 50), "label": "KAMPF", "icon": "⚔",
        "perks": [
            {"id": "dmg1",       "name": "Schaden I",       "desc": "+15% Schaden",           "cost": 2,  "requires": None},
            {"id": "dmg2",       "name": "Schaden II",      "desc": "+25% Schaden",           "cost": 4,  "requires": "dmg1"},
            {"id": "dmg3",       "name": "Schaden III",     "desc": "+40% Schaden",           "cost": 7,  "requires": "dmg2"},
            {"id": "crit",       "name": "Kritisch",        "desc": "15% Crit × 2 DMG",       "cost": 5,  "requires": None},
            {"id": "explosive",  "name": "Sprengmeister",   "desc": "+30% Explosionsradius",  "cost": 4,  "requires": None},
            {"id": "rapid",      "name": "Schnellfeuer",    "desc": "-15% Feuerrate CD",      "cost": 3,  "requires": "dmg1"},
            {"id": "headshot",   "name": "Kopfschuss",      "desc": "+20% Scharfschützen-DMG","cost": 4,  "requires": "crit"},
        ]
    },
    "mobility": {
        "color": (50, 200, 220), "label": "MOBILITAET", "icon": "⚡",
        "perks": [
            {"id": "spd1",       "name": "Sprint I",        "desc": "+20% Tempo",             "cost": 2,  "requires": None},
            {"id": "spd2",       "name": "Sprint II",       "desc": "+35% Tempo",             "cost": 4,  "requires": "spd1"},
            {"id": "spd3",       "name": "Sprint III",      "desc": "+50% Tempo",             "cost": 6,  "requires": "spd2"},
            {"id": "jump2",      "name": "Doppelsprung",    "desc": "2× in der Luft springen","cost": 5,  "requires": None},
            {"id": "roll_cd",    "name": "Schnellrolle",    "desc": "Dodge-CD −40%",          "cost": 3,  "requires": None},
            {"id": "wallrun",    "name": "Wandläufer",      "desc": "2× Wandsprung",          "cost": 4,  "requires": "jump2"},
            {"id": "dash",       "name": "Kampf-Dash",      "desc": "Roll macht +50% DMG",    "cost": 5,  "requires": "roll_cd"},
        ]
    },
    "survival": {
        "color": (50, 210, 80), "label": "UEBERLEBEN", "icon": "🛡",
        "perks": [
            {"id": "hp1",        "name": "Zähigkeit I",     "desc": "+25 Max-HP",             "cost": 2,  "requires": None},
            {"id": "hp2",        "name": "Zähigkeit II",    "desc": "+50 Max-HP",             "cost": 4,  "requires": "hp1"},
            {"id": "hp3",        "name": "Zähigkeit III",   "desc": "+75 Max-HP",             "cost": 6,  "requires": "hp2"},
            {"id": "regen",      "name": "Regeneration",    "desc": "+1 HP/s bei ≤30% HP",    "cost": 5,  "requires": None},
            {"id": "lives",      "name": "Extra Leben",     "desc": "+1 Leben",               "cost": 6,  "requires": None},
            {"id": "armor",      "name": "Panzerung",       "desc": "−20% Schaden",           "cost": 5,  "requires": "hp1"},
            {"id": "lifesteal",  "name": "Lebensraub",      "desc": "5% Schaden → HP",        "cost": 6,  "requires": "hp2"},
        ]
    },
    "tech": {
        "color": (245, 200, 40), "label": "TECHNIK", "icon": "🔧",
        "perks": [
            {"id": "ammo1",      "name": "Munitionsgurt",   "desc": "Raketen +4 Magazin",     "cost": 3,  "requires": None},
            {"id": "ammo2",      "name": "Überladung",      "desc": "Alle Waffen +25% Mag.",  "cost": 5,  "requires": "ammo1"},
            {"id": "turret2",    "name": "Doppelturm",      "desc": "Max Geschütze 2 → 4",    "cost": 5,  "requires": None},
            {"id": "turret3",    "name": "Eliteturm",       "desc": "Turret +50% DMG+Range",  "cost": 6,  "requires": "turret2"},
            {"id": "grenade2",   "name": "Granatenpack",    "desc": "Startgranaten × 2",      "cost": 3,  "requires": None},
            {"id": "grapple_cd", "name": "Greifhaken II",   "desc": "Grapple-CD −50%",        "cost": 4,  "requires": None},
            {"id": "emp_range",  "name": "EMP-Reichweite",  "desc": "EMP-Radius +50%",        "cost": 4,  "requires": None},
        ]
    },
}

class SkillTree:
    def __init__(self):
        self.points   = 0
        self.unlocked = set()

    def reset(self):
        self.__init__()

    def earn(self, n=1):
        self.points += n

    def can_unlock(self, perk_id):
        for branch in SKILL_TREE.values():
            for p in branch["perks"]:
                if p["id"] == perk_id:
                    if perk_id in self.unlocked:
                        return False, "Bereits freigeschaltet"
                    req = p.get("requires")
                    if req and req not in self.unlocked:
                        req_name = req
                        for b2 in SKILL_TREE.values():
                            for p2 in b2["perks"]:
                                if p2["id"] == req:
                                    req_name = p2["name"]
                        return False, f"Benötigt: {req_name}"
                    if self.points < p["cost"]:
                        return False, f"Braucht {p['cost']} Pkt."
                    return True, "OK"
        return False, "Unbekannt"

    def unlock(self, perk_id):
        ok, _ = self.can_unlock(perk_id)
        if not ok: return False
        for branch in SKILL_TREE.values():
            for p in branch["perks"]:
                if p["id"] == perk_id:
                    self.points -= p["cost"]
                    self.unlocked.add(perk_id)
                    return True
        return False

    def has(self, perk_id):        return perk_id in self.unlocked

    def dmg_multiplier(self):
        m = 1.0
        if self.has("dmg1"): m += 0.15
        if self.has("dmg2"): m += 0.25
        if self.has("dmg3"): m += 0.40
        return m

    def sniper_dmg_mult(self):
        return 1.20 if self.has("headshot") else 1.0

    def speed_multiplier(self):
        m = 1.0
        if self.has("spd1"): m += 0.20
        if self.has("spd2"): m += 0.35
        if self.has("spd3"): m += 0.50
        return m

    def max_hp_bonus(self):
        b = 0
        if self.has("hp1"): b += 25
        if self.has("hp2"): b += 50
        if self.has("hp3"): b += 75
        return b

    def armor_reduction(self):    return 0.20 if self.has("armor") else 0.0
    def lifesteal_pct(self):      return 0.05 if self.has("lifesteal") else 0.0
    def max_turrets(self):        return 4 if self.has("turret2") else 2
    def turret_dmg_mult(self):    return 1.50 if self.has("turret3") else 1.0
    def max_grenades(self):       return 10 if self.has("grenade2") else 5
    def extra_lives(self):        return 1 if self.has("lives") else 0
    def crit_chance(self):        return 0.15 if self.has("crit") else 0.0
    def explosion_radius_mult(self): return 1.30 if self.has("explosive") else 1.0
    def roll_cooldown_mult(self): return 0.60 if self.has("roll_cd") else 1.0
    def roll_damage_mult(self):   return 1.50 if self.has("dash") else 1.0
    def double_jump(self):        return self.has("jump2")
    def wall_jump_count(self):    return 2 if self.has("wallrun") else 1
    def grapple_cd_mult(self):    return 0.50 if self.has("grapple_cd") else 1.0
    def emp_radius_mult(self):    return 1.50 if self.has("emp_range") else 1.0
    def regen_active(self):       return self.has("regen")
    def fire_rate_mult(self):     return 0.85 if self.has("rapid") else 1.0
    def extra_ammo(self):         return self.has("ammo2")

SKILLS = SkillTree()

# ═══════════════════════════════════════════════════
#  COMBO-SYSTEM
# ═══════════════════════════════════════════════════
class ComboSystem:
    TIMEOUT = 180  # 3 Sek.

    def __init__(self):
        self.count  = 0
        self.timer  = 0
        self.max    = 0
        self.notif  = 0

    def kill(self):
        self.timer  = self.TIMEOUT
        self.count += 1
        self.max    = max(self.max, self.count)
        self.notif  = 60
        if self.count >= 5:
            save_achievement("combo_5")

    def update(self):
        if self.timer > 0:
            self.timer -= 1
            if self.timer == 0:
                self.count = 0
        if self.notif > 0: self.notif -= 1

    def score_bonus(self):
        """Bonus-Multiplikator basierend auf Combo."""
        if self.count >= 10: return 3.0
        if self.count >= 5:  return 2.0
        if self.count >= 3:  return 1.5
        return 1.0

    def draw(self, surf):
        if self.count < 2: return
        f = pygame.font.SysFont("consolas", 22, bold=True)
        col = ORANGE if self.count < 5 else RED
        txt = f.render(f"COMBO x{self.count}  +{int((self.score_bonus()-1)*100)}%", True, col)
        # Pulsieren
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 3
        x = WIDTH // 2 - txt.get_width() // 2
        y = int(HEIGHT // 2 - 120 - pulse)
        s = pygame.Surface((txt.get_width()+16, txt.get_height()+8), pygame.SRCALPHA)
        s.fill((0, 0, 0, 120))
        s.blit(txt, (8, 4))
        surf.blit(s, (x-8, y-4))

COMBO = ComboSystem()

# ═══════════════════════════════════════════════════
#  PLAYER XP & LEVEL SYSTEM
# ═══════════════════════════════════════════════════
XP_FILE = "frontline_xp.json"
XP_PER_LEVEL = [0, 500, 1200, 2500, 4500, 7500, 12000, 18000, 26000, 36000, 50000]

class PlayerProgression:
    def __init__(self):
        self.load()

    def load(self):
        if os.path.exists(XP_FILE):
            try:
                with open(XP_FILE,"r") as f:
                    data = json.load(f)
                self.xp           = data.get("xp", 0)
                self.level        = data.get("level", 1)
                self.total_kills  = data.get("total_kills", 0)
                self.total_zones  = data.get("total_zones", 0)
                self.unlocked_perks= set(data.get("unlocked_perks", []))
                self.perk_points  = data.get("perk_points", 0)
                return
            except: pass
        self.xp            = 0
        self.level         = 1
        self.total_kills   = 0
        self.total_zones   = 0
        self.unlocked_perks= set()
        self.perk_points   = 0

    def save(self):
        with open(XP_FILE,"w") as f:
            json.dump({
                "xp": self.xp,
                "level": self.level,
                "total_kills": self.total_kills,
                "total_zones": self.total_zones,
                "unlocked_perks": list(self.unlocked_perks),
                "perk_points": self.perk_points,
            }, f, indent=2)

    def add_xp(self, amount):
        leveled = False
        self.xp += amount
        max_lv = len(XP_PER_LEVEL) - 1
        while self.level < max_lv and self.xp >= XP_PER_LEVEL[self.level]:
            self.level      += 1
            self.perk_points += 2
            leveled = True
            SFX.play(SFX.level_up)
        self.save()
        return leveled

    def xp_to_next(self):
        if self.level >= len(XP_PER_LEVEL)-1: return 0
        return XP_PER_LEVEL[self.level] - self.xp

    def xp_progress(self):
        if self.level >= len(XP_PER_LEVEL)-1: return 1.0
        prev = XP_PER_LEVEL[self.level-1]
        nxt  = XP_PER_LEVEL[self.level]
        return max(0.0, min(1.0, (self.xp - prev) / max(1, nxt-prev)))

    def add_kill(self): self.total_kills += 1; self.save()
    def add_zone(self): self.total_zones += 1; self.save()

PROGRESSION = PlayerProgression()

class XPNotification:
    def __init__(self): self.entries = []; self.levelup_timer = 0

    def add_xp(self, amount, leveled=False):
        self.entries.append({"amount": amount, "timer": 90,
                              "y": float(HEIGHT//2 - 60)})
        if leveled: self.levelup_timer = 240

    def update(self):
        for e in self.entries:
            e["timer"] -= 1; e["y"] -= 0.8
        self.entries = [e for e in self.entries if e["timer"]>0]
        if self.levelup_timer > 0: self.levelup_timer -= 1

    def draw(self, surf):
        f2 = pygame.font.SysFont("consolas",14,bold=True)
        for e in self.entries:
            alpha6=min(255,e["timer"]*4)
            t2=f2.render(f"+{e['amount']} XP",True,(100,220,255))
            t2.set_alpha(alpha6)
            surf.blit(t2,(WIDTH-190,int(e["y"])))
        if self.levelup_timer > 0:
            alpha7=min(255,self.levelup_timer*3)
            scale3=1.0+abs(math.sin(pygame.time.get_ticks()*0.01))*0.06
            f3=pygame.font.SysFont("consolas",32,bold=True)
            lt2=f3.render(f"LEVEL {PROGRESSION.level}!",True,YELLOW)
            ls2=pygame.transform.scale(lt2,
                (int(lt2.get_width()*scale3),int(lt2.get_height()*scale3)))
            ls2.set_alpha(alpha7)
            s3=pygame.Surface((ls2.get_width()+24,ls2.get_height()+12),pygame.SRCALPHA)
            s3.fill((0,0,0,100))
            pygame.draw.rect(s3,YELLOW,(0,0,s3.get_width(),s3.get_height()),2,border_radius=5)
            s3.blit(ls2,(12,6)); s3.set_alpha(alpha7)
            surf.blit(s3,(WIDTH//2-s3.get_width()//2,HEIGHT//2-140))

XP_NOTIF = XPNotification()

# ═══════════════════════════════════════════════════
#  ACHIEVEMENT NOTIFICATION
# ═══════════════════════════════════════════════════
class AchievementNotif:
    def __init__(self):
        self.queue  = []
        self.timer  = 0
        self.current= None

    def push(self, key):
        if key in ACHIEVEMENTS_DEF:
            self.queue.append(key)

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        elif self.queue:
            self.current = self.queue.pop(0)
            self.timer   = 240

    def draw(self, surf):
        if not self.current or self.timer <= 0: return
        alpha = min(255, self.timer * 4)
        cfg   = ACHIEVEMENTS_DEF[self.current]
        f1    = pygame.font.SysFont("consolas", 14, bold=True)
        f2    = pygame.font.SysFont("consolas", 18, bold=True)
        t1    = f1.render("ACHIEVEMENT FREIGESCHALTET!", True, YELLOW)
        t2    = f2.render(f"{cfg['icon']}  {cfg['name']}", True, WHITE)
        t3    = f1.render(cfg['desc'], True, GRAY)
        w     = max(t1.get_width(), t2.get_width(), t3.get_width()) + 40
        h     = 80
        x     = WIDTH - w - 20
        y     = 140
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        pygame.draw.rect(panel, YELLOW, (0, 0, w, h), 2, border_radius=6)
        panel.blit(t1, (20, 8))
        panel.blit(t2, (20, 26))
        panel.blit(t3, (20, 54))
        panel.set_alpha(alpha)
        surf.blit(panel, (x, y))

ACHIEV_NOTIF = AchievementNotif()

def unlock(key):
    if save_achievement(key):
        ACHIEV_NOTIF.push(key)
        # Skin freischalten prüfen
        for sname, sdata in SKINS.items():
            if sdata["unlock"] == key:
                pass  # Skin ist nun verfügbar

# ═══════════════════════════════════════════════════
#  SOUND
# ═══════════════════════════════════════════════════
def make_sound_raw(samples, vol=0.4):
    SR = 44100
    buf = bytearray(len(samples) * 2)
    for i, s in enumerate(samples):
        v = max(-32767, min(32767, int(s * vol * 32767)))
        buf[i*2] = v & 0xFF; buf[i*2+1] = (v >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))

def _env(n, atk=0.002, dec=0.15, sus=0.3, rel=0.55):
    a=int(atk*n); d=int(dec*n); s=int(sus*n); r=max(0,n-a-d-s)
    out=[]
    for i in range(a): out.append(i/max(a,1))
    for i in range(d): out.append(1.0-(1.0-0.5)*i/max(d,1))
    for i in range(s): out.append(0.5)
    for i in range(r): out.append(0.5*(1-i/max(r,1)))
    while len(out)<n: out.append(0.0)
    return out[:n]

def synth_pistol():
    SR=44100; n=int(SR*0.22)
    env=_env(n,0.001,0.06,0.0,0.94)
    out=[]
    for i in range(n):
        t=i/SR; e=env[i]
        crack=random.uniform(-1,1)*math.exp(-t*90)
        body=(math.sin(2*math.pi*160*t)*math.exp(-t*28)
             +math.sin(2*math.pi*310*t)*math.exp(-t*40)*0.4)
        tail=random.uniform(-1,1)*math.exp(-t*18)*0.25
        out.append((crack*0.6+body*0.55+tail)*e)
    return make_sound_raw(out, 0.55)

def synth_rifle():
    SR=44100; n=int(SR*0.16)
    env=_env(n,0.001,0.04,0.0,0.96)
    out=[]
    for i in range(n):
        t=i/SR; e=env[i]
        crack=random.uniform(-1,1)*math.exp(-t*110)
        snap=(math.sin(2*math.pi*280*t+math.sin(2*math.pi*80*t)*3)
              *math.exp(-t*50))
        out.append((crack*0.7+snap*0.5)*e)
    return make_sound_raw(out, 0.45)

def synth_sniper():
    SR=44100; n=int(SR*0.55)
    env=_env(n,0.001,0.08,0.25,0.67)
    out=[]
    for i in range(n):
        t=i/SR; e=env[i]
        crack=random.uniform(-1,1)*math.exp(-t*60)
        boom=(math.sin(2*math.pi*90*t)*math.exp(-t*8)
             +math.sin(2*math.pi*180*t)*math.exp(-t*14)*0.5
             +math.sin(2*math.pi*60*t)*math.exp(-t*5)*0.6)
        tail=random.uniform(-1,1)*math.exp(-t*12)*0.2
        out.append((crack*0.5+boom*0.65+tail)*e)
    return make_sound_raw(out, 0.6)

def synth_shotgun():
    SR=44100; n=int(SR*0.30)
    env=_env(n,0.001,0.06,0.02,0.92)
    out=[]
    for i in range(n):
        t=i/SR; e=env[i]
        blast=random.uniform(-1,1)*math.exp(-t*40)
        body=(math.sin(2*math.pi*110*t)*math.exp(-t*12)
             +math.sin(2*math.pi*220*t)*math.exp(-t*20)*0.4)
        out.append((blast*0.75+body*0.5)*e)
    return make_sound_raw(out, 0.65)

def synth_rocket_launch():
    SR=44100; n=int(SR*0.55)
    out=[]
    for i in range(n):
        t=i/SR
        whoosh=random.uniform(-1,1)*math.exp(-t*4)*0.8
        hiss=random.uniform(-1,1)*(0.3+t*0.4)*math.exp(-t*2)*0.5
        shriek=math.sin(2*math.pi*(800-t*600)*t)*math.exp(-t*5)*0.35
        env_v=min(1.0,t*20)*(1-t/1.5)
        out.append((whoosh+hiss+shriek)*env_v)
    return make_sound_raw(out, 0.55)

def synth_explosion(big=False):
    SR=44100; dur=0.9 if big else 0.55; n=int(SR*dur)
    out=[]
    for i in range(n):
        t=i/SR
        k=1.5 if big else 1.0
        thud=(math.sin(2*math.pi*55*k*t)*math.exp(-t*5*k)
             +math.sin(2*math.pi*80*k*t)*math.exp(-t*8*k)*0.6
             +math.sin(2*math.pi*38*k*t)*math.exp(-t*3.5*k)*0.8)
        rumble=random.uniform(-1,1)*math.exp(-t*6*k)*0.6
        crack=random.uniform(-1,1)*math.exp(-t*40)*0.4
        out.append(thud*0.7+rumble*0.4+crack*0.3)
    return make_sound_raw(out, 0.7 if big else 0.55)

def synth_knife():
    SR=44100; n=int(SR*0.09)
    out=[]
    for i in range(n):
        t=i/SR
        swish=random.uniform(-1,1)*math.exp(-t*55)*0.7
        ring=math.sin(2*math.pi*1800*t)*math.exp(-t*80)*0.4
        out.append(swish+ring)
    return make_sound_raw(out, 0.35)

def synth_jump():
    SR=44100; n=int(SR*0.18)
    out=[]
    for i in range(n):
        t=i/SR
        freq=280+t*120
        v=math.sin(2*math.pi*freq*t)*math.exp(-t*18)
        out.append(v)
    return make_sound_raw(out, 0.2)

def synth_hit_player():
    SR=44100; n=int(SR*0.22)
    out=[]
    for i in range(n):
        t=i/SR
        thud=math.sin(2*math.pi*120*t)*math.exp(-t*30)
        noise=random.uniform(-1,1)*math.exp(-t*25)*0.5
        out.append(thud*0.7+noise*0.5)
    return make_sound_raw(out, 0.5)

def synth_hit_enemy():
    SR=44100; n=int(SR*0.08)
    out=[]
    for i in range(n):
        t=i/SR
        ping=math.sin(2*math.pi*600*t)*math.exp(-t*60)
        out.append(ping)
    return make_sound_raw(out, 0.3)

def synth_tank_shot():
    SR=44100; n=int(SR*0.70)
    out=[]
    for i in range(n):
        t=i/SR
        boom=(math.sin(2*math.pi*45*t)*math.exp(-t*4)
             +math.sin(2*math.pi*75*t)*math.exp(-t*7)*0.7
             +math.sin(2*math.pi*28*t)*math.exp(-t*2.5)*0.9)
        rumble=random.uniform(-1,1)*math.exp(-t*5)*0.55
        crack=random.uniform(-1,1)*math.exp(-t*55)*0.5
        out.append(boom*0.65+rumble*0.45+crack*0.3)
    return make_sound_raw(out, 0.72)

def synth_pickup():
    SR=44100; n=int(SR*0.22)
    out=[]
    for i in range(n):
        t=i/SR
        f1=math.sin(2*math.pi*660*t)*math.exp(-t*12)
        f2=math.sin(2*math.pi*880*t+0.3)*math.exp(-t*14)*0.7
        out.append(f1+f2)
    return make_sound_raw(out, 0.28)

def synth_boss_roar():
    SR=44100; n=int(SR*0.7)
    out=[]
    for i in range(n):
        t=i/SR
        lfo=math.sin(2*math.pi*3.5*t)*0.4
        body=(math.sin(2*math.pi*(65+lfo*20)*t)*math.exp(-t*2.5)
             +math.sin(2*math.pi*(110+lfo*30)*t)*math.exp(-t*3.5)*0.6
             +math.sin(2*math.pi*42*t)*math.exp(-t*1.8)*0.7)
        rumble=random.uniform(-1,1)*math.exp(-t*3)*0.5
        out.append(body*0.65+rumble*0.45)
    return make_sound_raw(out, 0.65)

def synth_shield_hit():
    SR=44100; n=int(SR*0.18)
    out=[]
    for i in range(n):
        t=i/SR
        freq=800-t*400
        v=math.sin(2*math.pi*freq*t)*math.exp(-t*22)
        noise=random.uniform(-1,1)*math.exp(-t*30)*0.3
        out.append(v*0.7+noise)
    return make_sound_raw(out, 0.32)

def synth_levelup():
    SR=44100; n=int(SR*0.45)
    freqs=[440,550,660,880]
    out=[]
    for i in range(n):
        t=i/SR; seg=int(t/(0.45/4)); seg=min(seg,3)
        v=math.sin(2*math.pi*freqs[seg]*t)*max(0,1-t*2.8)
        out.append(v)
    return make_sound_raw(out, 0.3)

def synth_zone_clear():
    SR=44100; n=int(SR*0.8)
    out=[]
    for i in range(n):
        t=i/SR
        chord=(math.sin(2*math.pi*523*t)
              +math.sin(2*math.pi*659*t)*0.8
              +math.sin(2*math.pi*784*t)*0.7
              +math.sin(2*math.pi*1047*t)*0.5)
        env_v=min(1.0,t*8)*(1-max(0,(t-0.5)/0.3))
        out.append(chord*env_v*0.3)
    return make_sound_raw(out, 0.35)

class SoundManager:
    def __init__(self):
        self.enabled = True
        try:
            self.shoot_pistol  = synth_pistol()
            self.shoot_rifle   = synth_rifle()
            self.shoot_sniper  = synth_sniper()
            self.shoot_shotgun = synth_shotgun()
            self.shoot_rocket  = synth_rocket_launch()
            self.shoot_stinger = synth_rocket_launch()
            self.knife_slash   = synth_knife()
            self.explosion     = synth_explosion(big=False)
            self.big_explosion = synth_explosion(big=True)
            self.hit_player    = synth_hit_player()
            self.hit_enemy     = synth_hit_enemy()
            self.jump          = synth_jump()
            self.grenade_throw = synth_rocket_launch()
            self.zone_clear    = synth_zone_clear()
            self.boss_roar     = synth_boss_roar()
            self.tank_shot     = synth_tank_shot()
            self.pickup        = synth_pickup()
            self.shield_hit    = synth_shield_hit()
            self.level_up      = synth_levelup()
            self.achievement   = synth_levelup()
            self.pause         = synth_hit_enemy()
        except Exception as ex:
            print(f"SoundManager init failed: {ex}")
            self.enabled = False
            class _D:
                def play(self): pass
            for a in ["shoot_pistol","shoot_rifle","shoot_sniper","shoot_shotgun",
                      "shoot_rocket","shoot_stinger","knife_slash","explosion",
                      "big_explosion","hit_player","hit_enemy","jump","grenade_throw",
                      "zone_clear","boss_roar","tank_shot","pickup","shield_hit",
                      "level_up","achievement","pause"]:
                setattr(self, a, _D())

    def play(self, s):
        if s:
            try: s.play()
            except: pass

SFX = SoundManager()

# ═══════════════════════════════════════════════════
#  V7.0 DESTRUCTIBLE ENVIRONMENT SYSTEM
# ═══════════════════════════════════════════════════
class DestructibleCrate:
    """Explosive crate — shoot it to trigger chain explosion."""
    W = 32; H = 32; MAX_HP = 30
    def __init__(self, x, y, kind="ammo"):
        self.x = float(x); self.y = float(y - self.H)
        self.hp = self.MAX_HP; self.alive = True
        self.kind = kind   # "ammo","fuel","explosive"
        self.age = 0; self.crack_seed = random.randint(0,9999)
        self.bob = random.uniform(0,6.28)

    @property
    def rect(self): return pygame.Rect(int(self.x)-self.W//2, int(self.y), self.W, self.H)

    def take_damage(self, amount, explode_chain=None):
        self.hp -= amount
        PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 4)
        if self.hp <= 0:
            self.alive = False
            scale = {"ammo":1.0,"fuel":1.8,"explosive":2.4}[self.kind]
            PARTICLES.spawn_explosion(self.rect.centerx, self.rect.centery, scale=scale)
            SFX.play(SFX.big_explosion if self.kind=="explosive" else SFX.explosion)
            # Chain explosion damages nearby crates
            if explode_chain is not None:
                for other in explode_chain:
                    if other is self or not other.alive: continue
                    d = math.hypot(other.rect.centerx-self.rect.centerx,
                                   other.rect.centery-self.rect.centery)
                    if d < 120:
                        other.take_damage(50, explode_chain)
            return True
        return False

    def draw(self, surf, cam_x=0):
        if not self.alive: return
        sx = int(self.x)-cam_x; cy = int(self.y)
        t = pygame.time.get_ticks()
        hr = self.hp/self.MAX_HP

        col_map = {
            "ammo":      ((80,65,42),(100,82,52),(55,44,28)),
            "fuel":      ((42,90,42),(58,120,58),(28,62,28)),
            "explosive": ((120,42,28),(155,58,38),(88,28,18)),
        }
        bc,bhi,bdk = col_map[self.kind]
        tint = int((1-hr)*50)
        bc  = tuple(min(255,c+tint) for c in bc)

        # Shadow
        sh = pygame.Surface((self.W+4,6),pygame.SRCALPHA)
        pygame.draw.ellipse(sh,(0,0,0,55),(0,0,self.W+4,6))
        surf.blit(sh,(sx-self.W//2-2,cy+self.H-2))

        # Crate body
        pygame.draw.rect(surf,bc,(sx-self.W//2,cy,self.W,self.H),border_radius=2)
        # Top face
        pygame.draw.rect(surf,bhi,(sx-self.W//2,cy,self.W,5),border_radius=2)
        # Side shadow
        pygame.draw.rect(surf,bdk,(sx+self.W//2-6,cy,6,self.H))
        # Wood planks / metal bands
        cr = random.Random(self.crack_seed)
        if self.kind=="ammo":
            for band_y in (cy+4, cy+self.H-6):
                pygame.draw.rect(surf,(65,52,34),(sx-self.W//2,band_y,self.W,3))
            for plank_x in range(sx-self.W//2+6,sx+self.W//2-4,8):
                pygame.draw.line(surf,bdk,(plank_x,cy+2),(plank_x,cy+self.H-2),1)
        elif self.kind=="fuel":
            # Cylindrical stripes
            pygame.draw.rect(surf,(45,100,45),(sx-self.W//2+4,cy+2,self.W-8,self.H-4),border_radius=4)
            pygame.draw.rect(surf,(60,140,60),(sx-self.W//2+4,cy+2,self.W-8,6),border_radius=4)
            # Hazard stripes
            for si in range(4):
                stripe_x = sx-self.W//2+si*9
                pygame.draw.polygon(surf,(200,180,20),
                    [(stripe_x,cy+self.H-4),(stripe_x+5,cy+self.H-4),
                     (stripe_x+8,cy+4),(stripe_x+3,cy+4)])
            # FUEL label
            lf=pygame.font.SysFont("consolas",8,bold=True)
            surf.blit(lf.render("FUEL",True,(200,255,200)),(sx-10,cy+12))
        else:  # explosive
            pygame.draw.rect(surf,(130,48,30),(sx-self.W//2+3,cy+3,self.W-6,self.H-6),border_radius=2)
            # Warning stripes
            for si2 in range(5):
                sy2=cy+4+si2*6
                sc2=(240,60,20) if si2%2==0 else (20,20,20)
                pygame.draw.rect(surf,sc2,(sx-self.W//2+3,sy2,self.W-6,3))
            lf2=pygame.font.SysFont("consolas",7,bold=True)
            surf.blit(lf2.render("TNT",True,(255,220,50)),(sx-9,cy+12))
            # Danger symbol pulse
            pulse2=int(40+abs(math.sin(t*0.08))*80)
            ds=pygame.Surface((20,20),pygame.SRCALPHA)
            pygame.draw.circle(ds,(255,50,20,pulse2),(10,10),10)
            surf.blit(ds,(sx-10,cy-12))

        # Damage cracks
        if hr<0.6:
            for _ in range(int((1-hr)*5)):
                crx=sx-self.W//2+cr.randint(2,self.W-4)
                cry=cy+cr.randint(2,self.H-4)
                pygame.draw.line(surf,(25,18,12),(crx,cry),
                                 (crx+cr.randint(-5,5),cry+cr.randint(-5,5)),1)
        # HP bar
        bw=self.W+4; bxb=sx-bw//2; byb=cy-10
        pygame.draw.rect(surf,(10,8,6),(bxb,byb,bw,4))
        hc=(50,200,80) if hr>0.5 else (220,40,40)
        if hr>0: pygame.draw.rect(surf,hc,(bxb,byb,int(bw*hr),4))


class DestructibleBarrel:
    """Oil/explosive barrel. Shoots fire when destroyed."""
    W = 22; H = 34; MAX_HP = 20
    def __init__(self, x, y, kind="oil"):
        self.x=float(x); self.y=float(y-self.H)
        self.hp=self.MAX_HP; self.alive=True; self.kind=kind
        self.rolling=False; self.roll_vx=0.0; self.vy=0.0
        self.on_ground=False

    @property
    def rect(self): return pygame.Rect(int(self.x)-self.W//2,int(self.y),self.W,self.H)

    def take_damage(self,amount,explode_chain=None):
        self.hp-=amount
        if self.hp<=0:
            self.alive=False
            if self.kind=="oil":
                PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=1.2)
                for _ in range(8):
                    ang=random.uniform(0,6.28); sp=random.uniform(3,9)
                    PARTICLES.spawn_ember(self.x+math.cos(ang)*20,
                                          self.y+math.sin(ang)*10)
            else:
                PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=1.6)
            SFX.play(SFX.explosion)
            return True
        else:
            self.rolling=True
            self.roll_vx=random.uniform(-6,6)
        return False

    def update(self):
        if not self.alive: return
        if self.rolling:
            self.vy=min(self.vy+0.5,12); self.y+=self.vy
            self.x+=self.roll_vx; self.roll_vx*=0.92
            if abs(self.roll_vx)<0.3: self.rolling=False
            self.on_ground=False
            for plat in current_platforms:
                r=self.rect
                if r.colliderect(plat) and self.vy>=0:
                    if r.bottom-self.vy<=plat.top+abs(self.vy)+2:
                        self.y=plat.top-self.H; self.vy=-self.vy*0.3
                        self.on_ground=True
            if self.y>GROUND_Y: self.y=GROUND_Y-self.H; self.vy=-self.vy*0.3

    def draw(self,surf,cam_x=0):
        if not self.alive: return
        sx=int(self.x)-cam_x; cy=int(self.y)
        hr=self.hp/self.MAX_HP
        base_col=(55,55,55) if self.kind=="oil" else (140,50,28)
        hi_col=(80,80,80) if self.kind=="oil" else (175,68,40)
        pygame.draw.rect(surf,base_col,(sx-self.W//2,cy,self.W,self.H),border_radius=4)
        pygame.draw.rect(surf,hi_col,(sx-self.W//2,cy,self.W,6),border_radius=4)
        # Metal bands
        for by in (cy+4, cy+self.H-6):
            pygame.draw.rect(surf,(35,35,35),(sx-self.W//2,by,self.W,3))
        if self.kind=="oil":
            lf=pygame.font.SysFont("consolas",7,bold=True)
            surf.blit(lf.render("OIL",True,(200,200,200)),(sx-8,cy+13))
        else:
            lf2=pygame.font.SysFont("consolas",7,bold=True)
            surf.blit(lf2.render("EXP",True,(255,200,50)),(sx-9,cy+13))
            pd=int(40+abs(math.sin(pygame.time.get_ticks()*0.06))*60)
            ps=pygame.Surface((14,14),pygame.SRCALPHA)
            pygame.draw.circle(ps,(255,80,20,pd),(7,7),7)
            surf.blit(ps,(sx-7,cy-8))


class DestructiblePillar:
    """Stone/metal pillar. Breaks into rubble chunks when destroyed."""
    W = 28; H = 80; MAX_HP = 120
    def __init__(self, x, y):
        self.x=float(x); self.y=float(y-self.H)
        self.hp=self.MAX_HP; self.alive=True
        self.crack_stage=0   # 0=intact, 1=cracked, 2=crumbling
        self.rubble=[]

    @property
    def rect(self): return pygame.Rect(int(self.x)-self.W//2,int(self.y),self.W,self.H)

    def take_damage(self,amount):
        self.hp-=amount
        old_stage=self.crack_stage
        if self.hp<self.MAX_HP*0.66: self.crack_stage=1
        if self.hp<self.MAX_HP*0.33: self.crack_stage=2
        if old_stage!=self.crack_stage:
            PARTICLES.spawn_dust(self.rect.centerx,self.rect.centery)
            SFX.play(SFX.hit_enemy)
        if self.hp<=0:
            self.alive=False
            PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=0.6)
            # Spawn rubble chunks
            for _ in range(6):
                self.rubble.append({
                    "x":float(self.rect.centerx),"y":float(self.rect.centery),
                    "vx":random.uniform(-6,6),"vy":random.uniform(-8,-2),
                    "size":random.randint(5,12),"rot":random.uniform(0,360),
                    "rs":random.uniform(-12,12),"life":120,
                })
            SFX.play(SFX.explosion)

    def update_rubble(self):
        for r in self.rubble:
            r["x"]+=r["vx"]; r["y"]+=r["vy"]
            r["vy"]+=0.4; r["vx"]*=0.95
            r["rot"]+=r["rs"]; r["life"]-=1
            if r["y"]>GROUND_Y: r["y"]=GROUND_Y; r["vy"]=-r["vy"]*0.3
        self.rubble=[r for r in self.rubble if r["life"]>0]

    def draw(self,surf,cam_x=0):
        # Draw rubble
        for r in self.rubble:
            rx=int(r["x"])-cam_x; ry=int(r["y"])
            alpha=min(255,r["life"]*3)
            rs2=pygame.Surface((r["size"]*2,r["size"]*2),pygame.SRCALPHA)
            pygame.draw.rect(rs2,(88,78,60,alpha),(0,0,r["size"]*2,r["size"]*2),border_radius=2)
            rot=pygame.transform.rotate(rs2,r["rot"])
            surf.blit(rot,(rx-rot.get_width()//2,ry-rot.get_height()//2))
        if not self.alive: return
        sx=int(self.x)-cam_x; cy=int(self.y)
        hr=self.hp/self.MAX_HP
        tint=int((1-hr)*40)
        bc=(88+tint,78-tint//2,60-tint//2)
        bhi=(112,98,76); bdk=(62,54,40)
        # Column body
        pygame.draw.rect(surf,bc,(sx-self.W//2,cy,self.W,self.H),border_radius=3)
        pygame.draw.rect(surf,bhi,(sx-self.W//2,cy,self.W,8),border_radius=3)
        pygame.draw.rect(surf,bdk,(sx-self.W//2,cy+self.H-8,self.W,8))
        # Fluting lines
        for fi in range(4):
            fx=sx-self.W//2+4+fi*8
            pygame.draw.line(surf,bdk,(fx,cy+8),(fx,cy+self.H-8),1)
        # Capital / base
        pygame.draw.rect(surf,bhi,(sx-self.W//2-4,cy-4,self.W+8,8),border_radius=2)
        pygame.draw.rect(surf,bhi,(sx-self.W//2-4,cy+self.H-4,self.W+8,8),border_radius=2)
        # Cracks
        if self.crack_stage>=1:
            cr=random.Random(int(self.x))
            for _ in range(self.crack_stage*4):
                crx=sx-self.W//2+cr.randint(2,self.W-4)
                cry=cy+cr.randint(10,self.H-10)
                pygame.draw.line(surf,(45,35,25),(crx,cry),
                                 (crx+cr.randint(-8,8),cry+cr.randint(-12,12)),1)
        # HP bar
        bw=self.W+4; bxb=sx-bw//2; byb=cy-10
        pygame.draw.rect(surf,(10,8,6),(bxb,byb,bw,4))
        hc=(50,200,80) if hr>0.5 else (220,180,40) if hr>0.25 else (220,40,40)
        if hr>0: pygame.draw.rect(surf,hc,(bxb,byb,int(bw*hr),4))


class EnvironmentSystem:
    """Manages all destructible objects in a zone."""
    def __init__(self): self.reset()

    def reset(self):
        self.crates:  list[DestructibleCrate]  = []
        self.barrels: list[DestructibleBarrel] = []
        self.pillars: list[DestructiblePillar] = []

    def spawn_for_zone(self, zone_num, platforms):
        self.reset()
        rng = random.Random(zone_num * 77)
        # Spawn crates along ground
        for i in range(6+zone_num*2):
            x = rng.randint(300, WORLD_WIDTH-300)
            kind = rng.choice(["ammo","ammo","fuel","explosive"])
            self.crates.append(DestructibleCrate(x, GROUND_Y, kind))
        # Barrels
        for i in range(4+zone_num):
            x = rng.randint(200, WORLD_WIDTH-200)
            kind = "oil" if rng.random()<0.6 else "explosive"
            self.barrels.append(DestructibleBarrel(x, GROUND_Y, kind))
        # Pillars on some platforms
        for plat in platforms[1:]:
            if rng.random()<0.4:
                self.pillars.append(DestructiblePillar(
                    plat.centerx+rng.randint(-40,40), plat.top))

    def take_bullet_damage(self, bullets, enemy_bullets):
        """Check all destructibles against bullets."""
        for crate in self.crates:
            if not crate.alive: continue
            for b in bullets+enemy_bullets:
                if b.alive and b.get_rect().colliderect(crate.rect):
                    b.alive=False
                    crate.take_damage(b.damage, self.crates)
                    break
        for barrel in self.barrels:
            if not barrel.alive: continue
            for b in bullets+enemy_bullets:
                if b.alive and b.get_rect().colliderect(barrel.rect):
                    b.alive=False
                    barrel.take_damage(b.damage)
                    break
        for pillar in self.pillars:
            if not pillar.alive: continue
            for b in bullets+enemy_bullets:
                if b.alive and b.get_rect().colliderect(pillar.rect):
                    b.alive=False
                    pillar.take_damage(b.damage)
                    break

    def take_explosion_damage(self, ex, ey, radius, damage):
        for crate in self.crates:
            if not crate.alive: continue
            d=math.hypot(crate.rect.centerx-ex, crate.rect.centery-ey)
            if d<radius:
                crate.take_damage(int(damage*(1-d/radius)), self.crates)
        for barrel in self.barrels:
            if not barrel.alive: continue
            d=math.hypot(barrel.rect.centerx-ex, barrel.rect.centery-ey)
            if d<radius:
                barrel.take_damage(int(damage*(1-d/radius)))
        for pillar in self.pillars:
            if not pillar.alive: continue
            d=math.hypot(pillar.rect.centerx-ex, pillar.rect.centery-ey)
            if d<radius*0.6:
                pillar.take_damage(int(damage*(1-d/radius)))

    def update(self):
        for b in self.barrels: b.update()
        for p in self.pillars: p.update_rubble()

    def draw(self, surf, cam_x=0):
        for p in self.pillars: p.draw(surf, cam_x)
        for c in self.crates:
            if c.alive: c.draw(surf, cam_x)
        for b in self.barrels:
            if b.alive: b.draw(surf, cam_x)

ENV_SYSTEM = EnvironmentSystem()

# ═══════════════════════════════════════════════════
#  WETTER
# ═══════════════════════════════════════════════════
class WeatherParticle:
    __slots__ = ("x","y","vx","vy","size","alpha","kind")
    def __init__(self, kind="rain"):
        self.kind  = kind
        self.alpha = random.randint(80, 200)
        if kind == "rain":
            self.x=random.randint(0,WIDTH); self.y=random.randint(-HEIGHT,0)
            self.vx=random.uniform(-1,1);   self.vy=random.uniform(12,20)
            self.size=random.randint(1,2)
        elif kind == "snow":
            self.x=random.randint(0,WIDTH); self.y=random.randint(-HEIGHT,0)
            self.vx=random.uniform(-1.5,1.5); self.vy=random.uniform(1,3)
            self.size=random.randint(2,5)
        elif kind == "dust":
            self.x=random.randint(0,WIDTH); self.y=random.randint(0,HEIGHT)
            self.vx=random.uniform(3,8);   self.vy=random.uniform(-0.5,0.5)
            self.size=random.randint(3,8)
        elif kind == "embers":
            self.x=random.randint(0,WIDTH); self.y=random.randint(HEIGHT//2,HEIGHT)
            self.vx=random.uniform(-1,1);   self.vy=random.uniform(-3,-1)
            self.size=random.randint(1,3)

    def update(self):
        self.x+=self.vx; self.y+=self.vy
        if self.kind=="snow": self.vx+=random.uniform(-0.1,0.1)
        if self.y>HEIGHT+10: self.y=random.randint(-50,-5); self.x=random.randint(0,WIDTH)
        if self.x>WIDTH+10: self.x=-10
        if self.x<-10: self.x=WIDTH+5
        if self.y<-HEIGHT: self.y=HEIGHT+5

    def draw(self, surf):
        sx=int(self.x); sy=int(self.y)
        if self.kind=="rain":
            pygame.draw.line(surf,(180,200,255,self.alpha),(sx,sy),(sx-1,sy+self.size*3),1)
        elif self.kind=="snow":
            pygame.draw.circle(surf,(230,240,255),(sx,sy),self.size)
        elif self.kind=="dust":
            pygame.draw.ellipse(surf,(200,170,100),(sx,sy,self.size*2+2,self.size+2))
        elif self.kind=="embers":
            pygame.draw.circle(surf,(255,140,30),(sx,sy),self.size)

class WeatherSystem:
    ZONE_WEATHER={1:"rain",2:"fog",3:"dust",4:"embers",5:"snow",6:"rain",7:"embers",8:"none"}
    def __init__(self):
        self.particles=[];self.kind="none"
        self.fog_surf=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        self.fog_offset=0.0
    def set_zone(self,zone_num):
        self.kind=self.ZONE_WEATHER.get(zone_num,"none");self.particles=[]
        count={"rain":200,"snow":120,"dust":80,"embers":60,"fog":0,"none":0}.get(self.kind,0)
        for _ in range(count):
            self.particles.append(WeatherParticle(self.kind if self.kind!="fog" else "rain"))
    def update(self):
        self.fog_offset+=0.3
        for p in self.particles: p.update()
    def draw_behind(self,surf):
        if self.kind=="fog":
            self.fog_surf.fill((0,0,0,0))
            for i in range(5):
                ox=int(math.sin((self.fog_offset+i*40)*0.008)*60)
                pygame.draw.ellipse(self.fog_surf,(150,170,140,35+i*8),(ox-100+i*220,HEIGHT//2-80,400,200))
            surf.blit(self.fog_surf,(0,0))
    def draw_front(self,surf):
        if self.kind in ("rain","snow","dust","embers"):
            for p in self.particles: p.draw(surf)
        if self.kind=="rain":
            ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((20,40,80,18)); surf.blit(ov,(0,0))
        elif self.kind=="dust":
            ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA); ov.fill((180,140,60,22)); surf.blit(ov,(0,0))

WEATHER=WeatherSystem()

# ═══════════════════════════════════════════════════
#  PARTIKEL
# ═══════════════════════════════════════════════════
_PCACHE: dict = {}
def _get_pcache(color, radius):
    key = (color, radius)
    if key not in _PCACHE:
        d = radius * 2 + 2
        s = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, 220), (radius+1, radius+1), radius)
        _PCACHE[key] = s
    return _PCACHE[key]


class Particle:
    __slots__ = ("x","y","vx","vy","life","max_life","color",
                 "size","gravity","mode","rotation","rot_speed")

    def __init__(self, x, y, vx, vy, life, color, size=3, gravity=0.15, mode="circle"):
        self.x=float(x); self.y=float(y)
        self.vx=vx;      self.vy=vy
        self.life=life;  self.max_life=life
        self.color=color; self.size=size
        self.gravity=gravity; self.mode=mode
        self.rotation=random.uniform(0,360)
        self.rot_speed=random.uniform(-8,8)

    def update(self):
        self.x+=self.vx; self.y+=self.vy
        self.vy+=self.gravity
        self.vx*=PARTICLE_FRICTION
        self.life-=1
        self.rotation+=self.rot_speed

    def draw(self, surf, cam_x=0):
        if self.life<=0: return
        ratio=self.life/self.max_life
        sx=int(self.x)-cam_x; sy=int(self.y)
        r=max(1,int(self.size*ratio))
        alpha=int(220*ratio)

        if self.mode=="glow":
            s=_get_pcache(self.color, r*2).copy()
            s.set_alpha(alpha)
            surf.blit(s,(sx-r*2-1,sy-r*2-1))
            s2=_get_pcache(self.color, r).copy()
            s2.set_alpha(min(255,int(alpha*1.4)))
            surf.blit(s2,(sx-r-1,sy-r-1))
        elif self.mode=="spark":
            angle=math.atan2(self.vy,self.vx)
            length=max(4,int(r*3*ratio))
            ex=int(sx-math.cos(angle)*length)
            ey=int(sy-math.sin(angle)*length)
            pygame.draw.line(surf,self.color,(sx,sy),(ex,ey),max(1,r))
        elif self.mode=="square":
            half=max(1,r//2)
            pygame.draw.rect(surf,self.color,(sx-half,sy-half,r,r))
        else:
            pygame.draw.circle(surf,self.color,(sx,sy),r)

    @property
    def alive(self): return self.life>0


class ParticleSystem:
    MAX_PARTICLES = 500

    def __init__(self): self.particles=[]

    def _p(self, *a, **kw):
        if len(self.particles) < self.MAX_PARTICLES:
            self.particles.append(Particle(*a, **kw))

    def spawn_muzzle_flash(self, x, y, d):
        for _ in range(6):
            a=random.uniform(-0.55,0.55); sp=random.uniform(5,13)
            c=random.choice([(255,255,190),(255,225,85),(255,165,35)])
            self._p(x,y,math.cos(a)*sp*d,math.sin(a)*sp,random.randint(4,8),c,random.randint(3,5),0,"glow")
        for _ in range(4):
            a=random.uniform(-0.4,0.4); sp=random.uniform(8,18)
            self._p(x,y,math.cos(a)*sp*d,math.sin(a)*sp,random.randint(3,7),(255,255,220),2,0.3,"spark")

    def spawn_blood(self, x, y, count=8):
        for _ in range(count):
            a=random.uniform(0,2*math.pi); sp=random.uniform(2,7)
            c=random.choice([(205,10,10),(245,30,30),(165,0,0)])
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp-2,random.randint(16,30),c,random.randint(2,5),0.28,"circle")

    def spawn_death_explosion(self, x, y):
        for _ in range(12):
            a=random.uniform(0,2*math.pi); sp=random.uniform(3,11)
            c=random.choice([(225,14,14),(255,42,42)])
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp-3,random.randint(20,45),c,random.randint(3,6),0.22,"circle")
        for _ in range(5):
            a=random.uniform(0,2*math.pi); sp=random.uniform(2,7)
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp-4,random.randint(25,50),(105,22,22),random.randint(4,8),0.22,"square")

    def spawn_explosion(self, x, y, scale=1.0):
        for _ in range(int(28*scale)):
            a=random.uniform(0,2*math.pi); sp=random.uniform(2,12*scale)
            c=random.choice([(255,225,55),(255,135,22),(255,72,12)])
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp-3,random.randint(18,45),c,random.randint(4,max(4,int(9*scale))),0.26,"glow")
        for _ in range(int(10*scale)):
            a=random.uniform(0,2*math.pi); sp=random.uniform(5,16*scale)
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp-4,random.randint(10,24),(255,255,105),2,0.36,"spark")
        for _ in range(int(6*scale)):
            a=random.uniform(0,2*math.pi); sp=random.uniform(3,8*scale)
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp-2,random.randint(28,55),(62,58,52),random.randint(4,9),0.32,"square")

    def spawn_air_death(self, x, y):
        for _ in range(18):
            a=random.uniform(0,2*math.pi); sp=random.uniform(3,12)
            c=random.choice([(255,205,32),(255,102,12),(255,52,12)])
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp-2,random.randint(22,48),c,random.randint(3,7),0.32,"glow")
        for _ in range(6):
            self._p(x,y,random.uniform(-6,6),random.uniform(-3,2),random.randint(36,70),(72,72,82),random.randint(4,9),0.42,"square")

    def spawn_tank_death(self, x, y):
        for _ in range(35):
            a=random.uniform(0,2*math.pi); sp=random.uniform(2,16)
            c=random.choice([(255,225,55),(255,135,22),(255,62,7)])
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp-4,random.randint(28,60),c,random.randint(4,11),0.22,"glow")
        for _ in range(10):
            self._p(x,y,random.uniform(-12,12),random.uniform(-16,-4),random.randint(45,85),(52,47,42),random.randint(5,11),0.48,"square")

    def spawn_bullet_impact(self, x, y, color=None):
        c=color or (205,182,105)
        for _ in range(5):
            a=random.uniform(-math.pi,0); sp=random.uniform(1,5)
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp,random.randint(6,14),c,2,0.26,"spark")

    def spawn_dust(self, x, y):
        for _ in range(4):
            self._p(x,y,random.uniform(-2,2),random.uniform(-3,-1),random.randint(10,20),(132,112,82),random.randint(2,5),-0.01,"circle")

    def spawn_shell(self, x, y, d):
        self._p(x,y,-d*random.uniform(2,5),random.uniform(-4,-2),random.randint(20,36),(215,192,65),3,0.45,"square")

    def spawn_sparks(self, x, y, count=6):
        for _ in range(count):
            a=random.uniform(0,2*math.pi); sp=random.uniform(3,9)
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp,random.randint(6,16),(255,225,62),2,0.32,"spark")

    def spawn_smoke(self, x, y):
        if random.random()<0.35:
            self._p(x,y,random.uniform(-1,1),random.uniform(-2,-0.5),random.randint(18,36),(108,108,112),random.randint(4,8),-0.02,"circle")

    def spawn_pickup(self, x, y, color):
        for _ in range(10):
            a=random.uniform(0,2*math.pi); sp=random.uniform(1.5,6)
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp-2,random.randint(18,36),color,random.randint(2,5),0.1,"glow")

    def spawn_sniper_trail(self, x1, y1, x2, y2):
        steps=int(math.hypot(x2-x1,y2-y1)/18)
        for i in range(steps):
            t=i/max(steps,1)
            px=x1+(x2-x1)*t; py=y1+(y2-y1)*t
            self._p(px,py,0,0,random.randint(4,9),(185,245,255),random.randint(1,3),0,"circle")

    def spawn_shotgun_spread(self, x, y, d):
        for _ in range(10):
            a=random.uniform(-0.65,0.65); sp=random.uniform(3,8)
            self._p(x,y,math.cos(a)*sp*d,math.sin(a)*sp,random.randint(3,7),(255,245,105),random.randint(2,4),0,"glow")

    def spawn_ember(self, x, y):
        self._p(x+random.uniform(-30,30),y+random.uniform(-10,10),
                random.uniform(-0.8,0.8),random.uniform(-3,-0.8),
                random.randint(35,75),(255,random.randint(80,180),20),random.randint(2,4),-0.04,"glow")

    def spawn_ice_crystal(self, x, y):
        self._p(x+random.uniform(-40,40),y+random.uniform(-5,5),
                random.uniform(-0.5,0.5),random.uniform(-1,0.2),
                random.randint(25,60),(195,220,255),random.randint(2,4),0.01,"circle")

    def spawn_neon_spark(self, x, y, color):
        for _ in range(3):
            a=random.uniform(0,2*math.pi); sp=random.uniform(1,4)
            self._p(x,y,math.cos(a)*sp,math.sin(a)*sp,random.randint(6,18),color,2,0.1,"spark")

    def update(self):
        if not SETTINGS.get("particles", True):
            self.particles=[]
            return
        self.particles=[p for p in self.particles if p.alive]
        for p in self.particles: p.update()

    def draw(self, surf, cam_x=0):
        for p in self.particles:
            p.draw(surf, cam_x)


PARTICLES = ParticleSystem()

screen_shake=0
_spotlight_surf=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)

# ═══════════════════════════════════════════════════
#  KILL FLASH & HIT NUMBERS
# ═══════════════════════════════════════════════════
class KillFlash:
    """Weißer Screen-Flash bei Kill."""
    def __init__(self): self.timer = 0; self.intensity = 0; self.color = (255,255,255)

    def trigger(self, intensity=60, color=(255,255,255)):
        self.timer = intensity
        self.intensity = intensity
        self.color = color

    def update(self): 
        if self.timer > 0: self.timer -= 2

    def draw(self, surf):
        if self.timer <= 0: return
        a = int(min(120, self.timer * 2.5))
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        s.fill((255, 255, 255, a))
        surf.blit(s, (0, 0))

KILL_FLASH = KillFlash()

class DamageNumber:
    """Aufsteigende Schadensanzeige über dem Feind."""
    __slots__ = ("x", "y", "vy", "value", "life", "max_life", "color", "is_kill", "font")
    def __init__(self, x, y, value, is_kill=False):
        self.x = float(x) + random.uniform(-20, 20)
        self.y = float(y) - 20
        self.vy = -2.5
        self.value = value
        self.is_kill = is_kill
        self.life = 70 if not is_kill else 100
        self.max_life = self.life
        size = 26 if is_kill else 18
        self.color = (255, 60, 60) if is_kill else (255, 220, 80)
        self.font = pygame.font.SysFont("consolas", size, bold=True)

    def update(self):
        self.y += self.vy
        self.vy *= 0.92
        self.life -= 1

    def draw(self, surf, cam_x=0):
        if self.life <= 0: return
        alpha = int(255 * self.life / self.max_life)
        label = f"KILL! -{self.value}" if self.is_kill else f"-{self.value}"
        t = self.font.render(label, True, self.color)
        ts = pygame.Surface((t.get_width() + 4, t.get_height() + 2), pygame.SRCALPHA)
        if self.is_kill:
            # Schwarzer Schatten
            shadow = self.font.render(label, True, (0, 0, 0))
            ts.blit(shadow, (4, 3))
        ts.blit(t, (2, 1))
        ts.set_alpha(alpha)
        surf.blit(ts, (int(self.x) - cam_x - ts.get_width()//2, int(self.y)))

    @property
    def alive(self): return self.life > 0

class DamageNumbers:
    def __init__(self): self.numbers = []

    def add(self, x, y, value, is_kill=False):
        self.numbers.append(DamageNumber(x, y, value, is_kill))

    def update(self): 
        self.numbers = [n for n in self.numbers if n.alive]
        for n in self.numbers: n.update()

    def draw(self, surf, cam_x=0):
        for n in self.numbers: n.draw(surf, cam_x)

DMG_NUMBERS = DamageNumbers()

# ═══════════════════════════════════════════════════
#  ZONE CLEAR EFFEKT
# ═══════════════════════════════════════════════════
class ZoneClearEffect:
    def __init__(self):
        self.active = False
        self.timer = 0
        self.particles = []

    def trigger(self):
        self.active = True
        self.timer = 180
        self.particles = []
        for _ in range(80):
            self.particles.append({
                "x": random.randint(0, WIDTH),
                "y": random.randint(-50, HEIGHT // 2),
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(2, 7),
                "color": random.choice([
                    (255, 220, 50), (50, 220, 80), (50, 180, 255),
                    (255, 80, 80), (200, 80, 255), (255, 255, 255)
                ]),
                "size": random.randint(4, 10),
                "rot": random.uniform(0, 360),
                "rot_speed": random.uniform(-8, 8),
            })

    def update(self):
        if not self.active: return
        self.timer -= 1
        if self.timer <= 0:
            self.active = False; return
        for p in self.particles:
            p["x"] += p["vx"]; p["y"] += p["vy"]
            p["vy"] += 0.1; p["rot"] += p["rot_speed"]
            if p["y"] > HEIGHT + 20:
                p["y"] = -10; p["x"] = random.randint(0, WIDTH)

    def draw(self, surf):
        if not self.active: return
        alpha = min(255, self.timer * 3)
        # "ZONE BEFREIT!" Banner
        if self.timer > 60:
            f = pygame.font.SysFont("consolas", 54, bold=True)
            txt = f.render("ZONE BEFREIT!", True, YELLOW)
            shadow = f.render("ZONE BEFREIT!", True, (80, 60, 0))
            scale = 1.0 + abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.05
            scaled = pygame.transform.scale(txt,
                (int(txt.get_width()*scale), int(txt.get_height()*scale)))
            s_scaled = pygame.transform.scale(shadow,
                (int(shadow.get_width()*scale), int(shadow.get_height()*scale)))
            bx = WIDTH//2 - scaled.get_width()//2
            by = HEIGHT//2 - 80
            ss = pygame.Surface((scaled.get_width()+20, scaled.get_height()+12), pygame.SRCALPHA)
            ss.fill((0, 0, 0, 140))
            surf.blit(ss, (bx - 10, by - 6))
            surf.blit(s_scaled, (bx + 3, by + 3))
            surf.blit(scaled, (bx, by))
        # Konfetti
        for p in self.particles:
            s = pygame.Surface((p["size"], p["size"]//2 + 2), pygame.SRCALPHA)
            s.fill((*p["color"], int(alpha * 0.9)))
            rotated = pygame.transform.rotate(s, p["rot"])
            surf.blit(rotated, (int(p["x"]) - rotated.get_width()//2,
                                int(p["y"]) - rotated.get_height()//2))

ZONE_CLEAR_FX = ZoneClearEffect()

# ═══════════════════════════════════════════════════
#  VIGNETTE / DAMAGE OVERLAY
# ═══════════════════════════════════════════════════
_vignette_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

def draw_vignette(surf, player):
    """Rote Vignette bei wenig HP, pulsierend."""
    hp_ratio = player.hp / player.MAX_HP
    if hp_ratio > 0.4: return
    intensity = int((0.4 - hp_ratio) / 0.4 * 160)
    pulse = abs(math.sin(pygame.time.get_ticks() * 0.004)) * 40
    a = min(200, intensity + int(pulse))
    _vignette_surf.fill((0, 0, 0, 0))
    # Vignette: Rand dunkel, Mitte transparent
    for r_step in range(8):
        r_frac = r_step / 8
        rad_x = int(WIDTH * (0.5 + r_frac * 0.5))
        rad_y = int(HEIGHT * (0.5 + r_frac * 0.5))
        layer_a = int(a * r_frac * 0.4)
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        layer.fill((0, 0, 0, 0))
        # Rote Ränder
        pygame.draw.rect(layer, (180, 0, 0, layer_a),
                         (0, 0, WIDTH - rad_x, HEIGHT))
        pygame.draw.rect(layer, (180, 0, 0, layer_a),
                         (rad_x, 0, WIDTH - rad_x, HEIGHT))
        pygame.draw.rect(layer, (180, 0, 0, layer_a),
                         (0, 0, WIDTH, HEIGHT - rad_y))
        pygame.draw.rect(layer, (180, 0, 0, layer_a),
                         (0, rad_y, WIDTH, HEIGHT - rad_y))
        surf.blit(layer, (0, 0))

        

# ═══════════════════════════════════════════════════
#  POWER-UPS
# ═══════════════════════════════════════════════════
class PowerUp:
    SIZE=24
    TYPES={
        "medkit":   {"color":(255,80,80),  "symbol":"H","desc":"Medkit +40 HP"},
        "ammo":     {"color":(255,200,50), "symbol":"A","desc":"Munition voll"},
        "shield":   {"color":(80,160,255), "symbol":"S","desc":"Schild 30 Sek."},
        "grenade":  {"color":(80,200,80),  "symbol":"G","desc":"+3 Granaten"},
        "speed":    {"color":(200,100,255),"symbol":"V","desc":"Tempo +50% 15s"},
        "doubledmg":{"color":(255,120,20), "symbol":"2x","desc":"2x Schaden 15s"},
    }
    def __init__(self,x,y,kind=None):
        self.x=float(x);self.y=float(y)
        self.kind=kind or random.choice(list(self.TYPES.keys()))
        self.alive=True;self.bob=random.uniform(0,2*math.pi)
        self.age=0;self.lifetime=600
    @property
    def rect(self):
        s=self.SIZE
        return pygame.Rect(int(self.x)-s//2,int(self.y)-s//2,s,s)
    def update(self):
        self.age+=1
        if self.age>=self.lifetime: self.alive=False
    def draw(self,surf,cam_x=0):
        if not self.alive: return
        cfg=self.TYPES[self.kind]
        bob_y=int(math.sin(self.age*0.08+self.bob)*4)
        sx=int(self.x)-cam_x;sy=int(self.y)+bob_y;s=self.SIZE
        if self.age>self.lifetime-180 and (self.age//8)%2==0: return
        glow=pygame.Surface((s*3,s*3),pygame.SRCALPHA)
        pulse=int(60+abs(math.sin(self.age*0.1))*80)
        pygame.draw.circle(glow,(*cfg["color"],pulse),(s*3//2,s*3//2),s)
        surf.blit(glow,(sx-s*3//2,sy-s*3//2))
        pygame.draw.rect(surf,DARK,(sx-s//2,sy-s//2,s,s),border_radius=6)
        pygame.draw.rect(surf,cfg["color"],(sx-s//2,sy-s//2,s,s),2,border_radius=6)
        f=pygame.font.SysFont("consolas",13,bold=True)
        t=f.render(cfg["symbol"],True,cfg["color"])
        surf.blit(t,(sx-t.get_width()//2,sy-t.get_height()//2))
    def apply(self,player):
        cfg=self.TYPES[self.kind]
        PARTICLES.spawn_pickup(self.x,self.y,cfg["color"])
        SFX.play(SFX.pickup);self.alive=False
        if self.kind=="medkit": player.hp=min(player.MAX_HP+get_diff()["player_hp_bonus"],player.hp+40)
        elif self.kind=="ammo":
            RAKETENWERFER.ammo=RAKETENWERFER.max_ammo
            STINGER.ammo=STINGER.max_ammo
            player.grenades=player.GRENADES
        elif self.kind=="shield": player.shield_timer=60*30
        elif self.kind=="grenade": player.grenades=min(player.grenades+3,9)
        elif self.kind=="speed": player.speed_boost_timer=60*15
        elif self.kind=="doubledmg": player.dmg_boost_timer=60*15
        return cfg["desc"]

# ═══════════════════════════════════════════════════
#  MINIMAP
# ═══════════════════════════════════════════════════
class Minimap:
    W=240;H=40;X=WIDTH//2-120;Y=HEIGHT-60
    SCALE=W/WORLD_WIDTH
    def draw(self,surf,player,enemies,tanks,air_enemies,jetpack_soldiers,boss,powerups,cam_x):
        if not hasattr(self,'_cache'): self._cache=None; self._frame=0
        self._frame+=1
        if self._frame%3==0 or self._cache is None:
            bg=pygame.Surface((self.W+4,self.H+4),pygame.SRCALPHA)
            bg.fill((0,0,0,160))
            pygame.draw.rect(bg,GRAY,(2,2,self.W,self.H),1)
            pygame.draw.line(bg,(80,70,55),(2,self.H-4),(self.W+2,self.H-4),2)
            for e in enemies:
                pygame.draw.circle(bg,RED,(2+int(e.x*self.SCALE),self.H-6),2)
            for t in tanks:
                tx=2+int(t.x*self.SCALE)
                pygame.draw.rect(bg,(180,120,20),(tx-3,self.H-8,6,4))
            for a in air_enemies+jetpack_soldiers:
                pygame.draw.circle(bg,CYAN,(2+int(a.x*self.SCALE),8),2)
            if boss and boss.alive:
                bx=2+int(boss.x*self.SCALE)
                pygame.draw.circle(bg,ORANGE,(bx,self.H//2),4)
            for p in powerups:
                if p.alive:
                    pygame.draw.circle(bg,YELLOW,(2+int(p.x*self.SCALE),self.H-6),2)
            self._cache=bg
        surf.blit(self._cache,(self.X-2,self.Y-2))
        # Player dot and viewport always live
        vw=int(WIDTH*self.SCALE); cx2=int(cam_x*self.SCALE)
        pygame.draw.rect(surf,(80,80,80),(self.X+cx2,self.Y,vw,self.H),1)
        pygame.draw.circle(surf,GREEN,(self.X+int(player.x*self.SCALE),self.Y+self.H-8),3)
        f=pygame.font.SysFont("consolas",9)
        surf.blit(f.render("MINIMAP",True,GRAY),(self.X,self.Y-10))

MINIMAP=Minimap()

# ═══════════════════════════════════════════════════
#  HIGHSCORE
# ═══════════════════════════════════════════════════
def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE,"r") as f: return json.load(f)
    return []

def save_highscore(name,score,zone):
    scores=load_highscores()
    scores.append({"name":name,"score":score,"zone":zone,"diff":current_difficulty})
    scores.sort(key=lambda x:x["score"],reverse=True)
    with open(HIGHSCORE_FILE,"w") as f: json.dump(scores[:10],f)

class LightSource:
    """A temporary or permanent screen-space light halo."""
    __slots__ = ("x","y","radius","color","intensity","life","max_life","cam_relative")
    def __init__(self, x, y, radius, color, intensity=1.0, life=-1, cam_relative=True):
        self.x           = x
        self.y           = y
        self.radius      = radius
        self.color       = color
        self.intensity   = intensity
        self.life        = life        # -1 = permanent this frame
        self.max_life    = life
        self.cam_relative= cam_relative   # True = world coords, False = screen
 
    @property
    def alive(self): return self.life != 0
 
    def update(self):
        if self.life > 0: self.life -= 1
 
 
# ═══════════════════════════════════════════════════
#  V7.0 DYNAMIC LIGHTING SYSTEM — OVERHAUL
# ═══════════════════════════════════════════════════
class LightSource:
    __slots__ = ("x","y","radius","color","intensity","life","max_life",
                 "cam_relative","flicker","pulse_speed","shadow_cast")
    def __init__(self,x,y,radius,color,intensity=1.0,life=-1,
                 cam_relative=True,flicker=False,pulse_speed=0.0,shadow_cast=False):
        self.x=x; self.y=y; self.radius=radius; self.color=color
        self.intensity=intensity; self.life=life; self.max_life=life
        self.cam_relative=cam_relative; self.flicker=flicker
        self.pulse_speed=pulse_speed; self.shadow_cast=shadow_cast
    @property
    def alive(self): return self.life!=0
    def update(self):
        if self.life>0: self.life-=1


class LightingSystem:
    """
    V7.0 Enhanced lighting:
    - Soft additive halos
    - Flicker support (fire, explosions)
    - Ambient zone lighting (tints whole screen)
    - Light bloom effect on bright sources
    - Volumetric fog interaction
    """
    _SURF_CACHE: dict = {}
    ZONE_AMBIENT = {
        1: (0,   0,   8,  18),    # Night city — slight blue tint
        2: (0,   8,   0,  14),    # Forest — slight green tint
        3: (12,  8,   0,  20),    # Desert — warm orange tint
        4: (0,   0,  12,  22),    # Military — cold blue
        5: (5,   10, 20,  28),    # Arctic — cool blue-white
        6: (8,   0,  12,  30),    # Omega — deep purple
        7: (20,  4,   0,  35),    # Volcanic — red-orange tint
        8: (0,   0,  10,  15),    # Space — near-black tint
    }

    def __init__(self):
        self.lights: list[LightSource] = []
        self._ambient_surf = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        self._bloom_surf   = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        self._tick = 0

    def clear(self):
        self.lights=[l for l in self.lights if l.alive]
        for l in self.lights:
            if l.life>0: l.update()
        self._tick+=1

    def add(self, x, y, radius, color, intensity=1.0, life=1,
            cam_relative=True, flicker=False, pulse_speed=0.0):
        if len(self.lights)<60:
            self.lights.append(LightSource(x,y,radius,color,intensity,life,
                                           cam_relative,flicker,pulse_speed))

    def add_persistent(self, x, y, radius, color, intensity=1.0,
                       flicker=False, pulse_speed=0.05):
        """Add a light that stays until manually removed."""
        self.add(x,y,radius,color,intensity,-1,True,flicker,pulse_speed)

    def add_explosion_light(self, x, y, scale=1.0):
        """Multi-layer explosion lighting."""
        r = int(120*scale); self.add(x,y,r,(255,200,80),1.2,life=12,flicker=True)
        self.add(x,y,int(r*0.6),(255,120,30),0.9,life=8)
        self.add(x,y,int(r*0.3),(255,255,180),1.5,life=5)

    def add_muzzle_light(self, x, y, col=None):
        c = col or (255,220,80)
        self.add(x,y,55,c,1.0,life=3,flicker=True)

    def _get_surf(self, radius, color, alpha):
        key=(radius,color)
        if key not in self._SURF_CACHE:
            d=radius*2+4
            s=pygame.Surface((d,d),pygame.SRCALPHA)
            for r2 in range(radius,0,-2):
                frac=r2/radius
                a2=int(255*(frac**2.2))
                pygame.draw.circle(s,(*color,min(255,a2)),(radius+2,radius+2),r2)
            self._SURF_CACHE[key]=s
        cached=self._SURF_CACHE[key].copy()
        cached.set_alpha(alpha); return cached

    def draw(self, surf, cam_x=0):
        for l in self.lights[:40]:
            if l.max_life>0:
                ratio=l.life/l.max_life
            else:
                ratio=1.0
            intensity=l.intensity*ratio
            if l.flicker:
                intensity*=(0.7+random.random()*0.6)
            if l.pulse_speed>0:
                intensity*=(0.8+abs(math.sin(self._tick*l.pulse_speed))*0.4)
            a=int(255*min(1.0,intensity))
            if a<=6: continue
            sx=int(l.x)-(cam_x if l.cam_relative else 0)
            sy=int(l.y)
            s=self._get_surf(l.radius,l.color,a)
            surf.blit(s,(sx-l.radius-2,sy-l.radius-2),
                      special_flags=pygame.BLEND_RGBA_ADD)
            # Bloom: extra large very faint halo for bright lights
            if intensity>0.8 and l.radius>40:
                bloom_r=l.radius*2
                bs=self._get_surf(bloom_r,l.color,int(a*0.12))
                surf.blit(bs,(sx-bloom_r-2,sy-bloom_r-2),
                          special_flags=pygame.BLEND_RGBA_ADD)

    def draw_ambient(self, surf, zone_num):
        """Apply subtle ambient color tint based on zone."""
        r,g,b,a = self.ZONE_AMBIENT.get(zone_num,(0,0,0,0))
        if a<=0: return
        self._ambient_surf.fill((r,g,b,a))
        surf.blit(self._ambient_surf,(0,0))

    def draw_volumetric_fog(self, surf, zone_num, cam_x, tick):
        """Zone-specific atmospheric effects drawn as layered fog."""
        if zone_num==7:   # Volcanic smoke
            for i in range(3):
                ox=int(math.sin((tick+i*80)*0.007)*120)
                fy=GROUND_Y-60+i*20
                fog=pygame.Surface((WIDTH+40,35),pygame.SRCALPHA)
                fog.fill((80,30,10,12+i*6))
                surf.blit(fog,(ox-20,fy))
            # Lava glow at ground
            lava_a=int(28+abs(math.sin(tick*0.04))*40)
            ls=pygame.Surface((WIDTH,20),pygame.SRCALPHA)
            ls.fill((255,60,0,lava_a))
            surf.blit(ls,(0,GROUND_Y-10))
        elif zone_num==8: # Space station
            # Holographic grid
            if tick%3==0:
                for gx in range(0,WIDTH,80):
                    gs=pygame.Surface((1,HEIGHT),pygame.SRCALPHA)
                    gs.fill((0,100,255,8))
                    surf.blit(gs,(gx,0))
                for gy in range(0,HEIGHT,60):
                    gs2=pygame.Surface((WIDTH,1),pygame.SRCALPHA)
                    gs2.fill((0,100,255,8))
                    surf.blit(gs2,(0,gy))
        elif zone_num==2:  # Forest light shafts
            for i in range(3):
                shaft_x=120+i*320-int(cam_x*0.1)%320
                shaft_a=int(14+abs(math.sin(tick*0.015+i))*16)
                ss=pygame.Surface((55,GROUND_Y),pygame.SRCALPHA)
                pygame.draw.polygon(ss,(200,230,160,shaft_a),
                    [(0,0),(55,0),(55-25,GROUND_Y),(25,GROUND_Y)])
                surf.blit(ss,(shaft_x,0))

LIGHTS = LightingSystem()

# ═══════════════════════════════════════════════════
#  KAMERA
# ═══════════════════════════════════════════════════
class Camera:
    def __init__(self): self.x=0.0
    def update(self,target_x):
        goal=target_x-WIDTH//2
        self.x+=(goal-self.x)*CAMERA_LERP
        self.x=max(0,min(WORLD_WIDTH-WIDTH,self.x))
    def in_view(self,wx,margin=300): return -margin<wx-self.x<WIDTH+margin

# ═══════════════════════════════════════════════════
#  WAFFEN
# ═══════════════════════════════════════════════════
class Weapon:
    def __init__(self,name,damage,fire_rate,bullet_speed,color,
                 auto=False,is_sniper=False,is_rocket=False,is_stinger=False,
                 is_shotgun=False,is_knife=False,ammo=None,sound=None):
        self.name=name;self.damage=damage;self.fire_rate=fire_rate
        self.bullet_speed=bullet_speed;self.color=color
        self.auto=auto;self.is_sniper=is_sniper;self.is_rocket=is_rocket
        self.is_stinger=is_stinger;self.is_shotgun=is_shotgun
        self.is_knife=is_knife;self.sound=sound;self.last_shot=0
        self.max_ammo=ammo;self.ammo=ammo

    def can_shoot(self, weapon_name=""):
        if self.ammo is not None and self.ammo <= 0: return False
        fr = int(self.fire_rate
                 * WSTATS.get_fire_rate_mult(weapon_name)
                 * SKILLS.fire_rate_mult())
        return pygame.time.get_ticks() - self.last_shot >= fr

    def shoot_toward(self,ox,oy,tx,ty,facing=1,dmg_mult=1.0):
        if not self.can_shoot(self.name): return []
        self.last_shot=pygame.time.get_ticks()
        if self.ammo is not None: self.ammo-=1
        if self.sound: SFX.play(self.sound)
        if self.is_knife: return [("melee",ox,oy,facing)]
        dx=tx-ox;dy=ty-oy;dist=math.hypot(dx,dy) or 1
        results=[]
        # Weapon upgrade bonus
        sniper_bonus = SKILLS.sniper_dmg_mult() if self.is_sniper else 1.0
        wdmg = int(self.damage * dmg_mult * WSTATS.get_dmg_mult(self.name) * sniper_bonus)
        if self.is_shotgun:
            for _ in range(8):
                angle = math.atan2(dy, dx) + random.uniform(-0.3, 0.3)
                results.append(Bullet(ox, oy, math.cos(angle)*self.bullet_speed,
                                      math.sin(angle)*self.bullet_speed, wdmg, self.color))
            PARTICLES.spawn_shotgun_spread(ox + (1 if dx > 0 else -1)*16, oy, 1 if dx > 0 else -1)
        elif self.is_rocket or self.is_stinger:
            vx=dx/dist*self.bullet_speed;vy=dy/dist*self.bullet_speed
            results.append(Rocket(ox,oy,vx,vy,wdmg,self.color,is_stinger=self.is_stinger))
        else:
            vx=dx/dist*self.bullet_speed;vy=dy/dist*self.bullet_speed
            PARTICLES.spawn_muzzle_flash(ox+(1 if vx>0 else -1)*16,oy,1 if vx>0 else -1)
            PARTICLES.spawn_shell(ox,oy,1 if vx>0 else -1)
            results.append(Bullet(ox,oy,vx,vy,wdmg,self.color,self.is_sniper))
        return results

PISTOLE        = Weapon("Pistole",        15,  500, 14, BULLET_COL, auto=False, sound=SFX.shoot_pistol)
STURMGEWEHR    = Weapon("Sturmgewehr",     8,   120, 18, ORANGE,     auto=True,  sound=SFX.shoot_rifle)
SCHARFSCHUETZE = Weapon("Scharfschuetze", 55, 1200, 28, SNIPER_COL, auto=False, is_sniper=True,  sound=SFX.shoot_sniper)
SCHROTFLINTE   = Weapon("Schrotflinte",   18,  800, 16, YELLOW,     auto=False, is_shotgun=True, sound=SFX.shoot_shotgun)
RAKETENWERFER  = Weapon("Raketenwerfer",  120,1500, 12, ROCKET_COL, auto=False, is_rocket=True,  ammo=6, sound=SFX.shoot_rocket)
STINGER        = Weapon("Stinger AA",     150,2000, 16, CYAN,       auto=False, is_stinger=True, ammo=4, sound=SFX.shoot_stinger)
MESSER         = Weapon("Messer",         35,  400,  0, RED,        auto=False, is_knife=True,   sound=SFX.knife_slash)
FLAMMENWERFER  = Weapon("Flammenwerfer",  8,   45,  9, FLAME_COL,
                        auto=True,  sound=SFX.shoot_rifle)   # rapid, close range
EMP_CANNON     = Weapon("EMP-Kanone",    20, 2200, 14, EMP_COL,
                        auto=False, ammo=6, sound=SFX.shoot_stinger)
RAILGUN        = Weapon("Railgun",       180, 3500, 38, (200, 80, 255),
                        auto=False, is_sniper=True, ammo=8, sound=SFX.shoot_sniper)

# ═══════════════════════════════════════════════════
#  PROJEKTILE
# ═══════════════════════════════════════════════════

class FlameBullet:
    """Short-lived expanding flame blob — used by Flammenwerfer."""
    RADIUS = 7
    def __init__(self, x, y, vx, vy, damage):
        self.x    = float(x); self.y = float(y)
        self.vx   = vx + random.uniform(-2, 2)
        self.vy   = vy + random.uniform(-2, 2)
        self.damage = damage
        self.alive  = True
        self.life   = random.randint(14, 22)   # frames before fizzle
        self.max_life = self.life
        self.radius = self.RADIUS + random.randint(0, 4)
 
    def update(self):
        self.x += self.vx; self.y += self.vy
        self.vy += 0.08          # slight droop
        self.vx *= 0.90          # air drag
        self.life -= 1
        self.radius = max(2, int(self.RADIUS * (self.life / self.max_life) * 1.8))
        if self.y > GROUND_Y + 20: self.alive = False
 
    def draw(self, surf, cam_x=0):
        if not self.alive: return
        ratio = max(0.01, self.life / self.max_life)
        sx    = int(self.x) - cam_x; sy = int(self.y)
        r     = max(3, self.radius)
        glow_r = max(1, r + 4)
        glow_a = max(1, min(254, int(80 * ratio)))
        # Outer glow
        gs = pygame.Surface((r*3 + 2, r*3 + 2), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*FLAME_COL, glow_a), (r*3//2 + 1, r*3//2 + 1), glow_r)
        surf.blit(gs, (sx - r*3//2 - 1, sy - r*3//2 - 1))
        # Core
        core_g = max(1, min(255, int(200 * ratio)))
        core_b = max(1, min(255, int(30 * ratio)))
        col = (255, core_g, core_b)
        pygame.draw.circle(surf, col, (sx, sy), r)
 
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius*2, self.radius*2)
 
    @property
    def alive_prop(self): return self.alive
 
class Bullet:
    RADIUS = 5
    def __init__(self, x, y, vx, vy, damage, color, is_sniper=False):
        self.x = float(x); self.y = float(y)
        self.vx = vx; self.vy = vy
        self.damage = damage; self.color = color
        self.alive = True; self.is_sniper = is_sniper

    def update(self):
        self.x += self.vx; self.y += self.vy
        if self.x < -200 or self.x > WORLD_WIDTH+200 or self.y < -300 or self.y > HEIGHT+100:
            self.alive = False

    def get_rect(self):
        r = 7 if self.is_sniper else self.RADIUS
        return pygame.Rect(self.x-r, self.y-r, r*2, r*2)

    def draw(self, surf, cam_x=0):
        sx = int(self.x) - cam_x
        sy = int(self.y)
        angle = math.atan2(self.vy, self.vx)
        spd   = math.hypot(self.vx, self.vy)

        if self.is_sniper:
            tail_len = 52
            for i in range(10):
                t = i / 10
                tx = int(sx - math.cos(angle) * tail_len * t)
                ty = int(sy - math.sin(angle) * tail_len * t)
                r  = max(1, int(4 * (1-t)))
                a  = int(230 * (1-t))
                ts = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
                col = (int(180*(1-t)+75*t), int(245*(1-t)+220*t), 255)
                pygame.draw.circle(ts, (*col, a), (r+1, r+1), r)
                surf.blit(ts, (tx-r-1, ty-r-1))
            pygame.draw.circle(surf, (255,255,255), (sx,sy), 4)
            pygame.draw.circle(surf, (160,240,255), (sx,sy), 2)
            gs = pygame.Surface((22,22), pygame.SRCALPHA)
            pygame.draw.circle(gs, (80,200,255,70), (11,11), 11)
            surf.blit(gs, (sx-11, sy-11))
        else:
            core_len = max(6, int(spd * 1.8))
            ex = int(sx - math.cos(angle) * core_len)
            ey = int(sy - math.sin(angle) * core_len)
            for gw, ga in ((8, 35), (5, 70), (3, 130)):
                gsurf = pygame.Surface((abs(ex-sx)+gw*2+4, abs(ey-sy)+gw*2+4), pygame.SRCALPHA)
                ox3 = min(sx,ex); oy3 = min(sy,ey)
                pygame.draw.line(gsurf, (*self.color, ga),
                                 (sx-ox3+gw+2, sy-oy3+gw+2),
                                 (ex-ox3+gw+2, ey-oy3+gw+2), gw)
                surf.blit(gsurf, (ox3-gw-2, oy3-gw-2))
            pygame.draw.line(surf, (255,255,220), (sx,sy), (ex,ey), 2)
            pygame.draw.circle(surf, (255,255,255), (sx,sy), 2)

# ── EMP Projectile ─────────────────────────────────────────────────────────────
class EMPBullet(Bullet):
    """
    Travels like a bullet; on hit creates an EMP pulse that stuns
    mechanical enemies (tanks, drones, helicopters, jets) for 3 seconds.
    """
    EMP_RADIUS = 180
    STUN_FRAMES = 180   # 3 seconds
 
    def __init__(self, x, y, vx, vy, damage):
        super().__init__(x, y, vx, vy, damage, EMP_COL, is_sniper=False)
        self.emp_triggered = False
 
    def trigger_emp(self, all_targets, screen_shake_ref):
        if self.emp_triggered: return
        self.emp_triggered = True
        self.alive = False
        SFX.play(SFX.big_explosion)
        PARTICLES.spawn_explosion(self.x, self.y, scale=0.8)
        LIGHTS.add_explosion_light(self.x, self.y, scale=2.0)
        # EMP ring visual
        for i in range(30):
            ang = (i / 30) * 2 * math.pi
            PARTICLES.spawn_sparks(
                self.x + math.cos(ang) * self.EMP_RADIUS * 0.5,
                self.y + math.sin(ang) * self.EMP_RADIUS * 0.5, 3)
        # Stun mechanical targets in radius
        for t in all_targets:
            d = math.hypot(t.x - self.x, t.y - self.y)
            if d <= self.EMP_RADIUS:
                if isinstance(t, (Tank, Drone, Helicopter, Jet)):
                    t.stun_timer = self.STUN_FRAMES
                    PARTICLES.spawn_sparks(t.rect.centerx, t.rect.centery, 12)
 
    def draw(self, surf, cam_x=0):
        sx = int(self.x) - cam_x; sy = int(self.y)
        # Pulsing cyan orb
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.05)) * 5
        r     = int(8 + pulse)
        gs    = pygame.Surface((r*3, r*3), pygame.SRCALPHA)
        pygame.draw.circle(gs, (*EMP_COL, 80), (r*3//2, r*3//2), r*2)
        surf.blit(gs, (sx - r*3//2, sy - r*3//2))
        pygame.draw.circle(surf, EMP_COL, (sx, sy), r)
        pygame.draw.circle(surf, WHITE, (sx, sy), max(1, r-3))
 
 
# ── Deployable Turret ──────────────────────────────────────────────────────────
class DeployedTurret:
    """
    Player-placed auto-turret — upgraded visuals.
    Detailed military sentry gun with rotating barrel,
    heat shimmer, armour plating, and status lights.
    """
    W = 36; H = 32
    MAX_HP   = 80
    MAX_AMMO = 40
    SHOOT_RATE = 400
    RANGE    = 500
    DAMAGE   = 12

    def __init__(self, x, y):
        self.x          = float(x)
        self.y          = float(y)
        self.hp         = self.MAX_HP
        self.ammo       = self.MAX_AMMO
        self.alive      = True
        self.last_shot  = 0
        self.barrel_angle = 0.0
        self.age        = 0
        self.heat       = 0.0        # 0-1, rises on shoot, cools over time
        self.barrel_recoil = 0.0    # animation offset on fire
        self.deploy_anim   = 0.0    # 0→1 pop-up deploy animation
        self.muzzle_flash  = 0      # frames of flash

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self, all_enemies, bullets):
        if not self.alive: return
        self.age += 1
        self.deploy_anim = min(1.0, self.deploy_anim + 0.08)
        self.heat        = max(0.0, self.heat - 0.004)
        self.barrel_recoil = max(0.0, self.barrel_recoil - 0.8)
        if self.muzzle_flash > 0: self.muzzle_flash -= 1
        if self.ammo <= 0: return
        now    = pygame.time.get_ticks()
        target = None; best_d = self.RANGE
        for e in all_enemies:
            if not getattr(e, 'alive', False): continue
            d = math.hypot(e.rect.centerx - self.rect.centerx,
                           e.rect.centery - self.rect.centery)
            if d < best_d: best_d = d; target = e
        if target and now - self.last_shot >= self.SHOOT_RATE:
            self.last_shot = now; self.ammo -= 1
            ox = self.rect.centerx; oy = self.rect.top + 8
            dx = target.rect.centerx - ox; dy = target.rect.centery - oy
            d  = math.hypot(dx, dy) or 1
            self.barrel_angle  = math.atan2(dy, dx)
            self.barrel_recoil = 5.0
            self.heat          = min(1.0, self.heat + 0.12)
            self.muzzle_flash  = 5
            bullets.append(Bullet(ox, oy, dx/d*16, dy/d*16,
                                  int(self.DAMAGE * SKILLS.turret_dmg_mult()), YELLOW))
            SFX.play(SFX.shoot_pistol)
            PARTICLES.spawn_muzzle_flash(
                ox + int(math.cos(self.barrel_angle)*18),
                oy + int(math.sin(self.barrel_angle)*18), 1)

    def take_damage(self, amount, is_rocket=False):
        self.hp -= amount
        PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 5)
        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_explosion(self.rect.centerx, self.rect.centery, scale=0.7)
            SFX.play(SFX.explosion)

    def draw(self, surf, cam_x=0):
        if not self.alive: return
        t   = pygame.time.get_ticks()
        sx  = int(self.x) - cam_x
        cx2 = sx + self.W // 2
        # Deploy pop-up: slide up from ground
        deploy_offset = int((1.0 - self.deploy_anim) * 28)
        cy2 = int(self.y) + deploy_offset

        # ── Ground shadow ─────────────────────────────────────────────────────
        sh = pygame.Surface((self.W + 8, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0, int(70 * self.deploy_anim)),
                            (0,0,self.W+8,6))
        surf.blit(sh, (cx2-self.W//2-4, int(self.y)+self.H-2))

        # ── BASE PLATE — heavy armoured sled ──────────────────────────────────
        base_col  = (42, 52, 38)
        base_hi   = (58, 72, 50)
        base_shad = (28, 35, 24)
        # Main sled body
        pygame.draw.rect(surf, base_col,
                         (cx2-18, cy2+18, 36, 14), border_radius=3)
        pygame.draw.rect(surf, base_hi,
                         (cx2-18, cy2+18, 36, 4), border_radius=3)
        pygame.draw.rect(surf, base_shad,
                         (cx2-18, cy2+28, 36, 4))
        # Sled skids
        pygame.draw.rect(surf, (32,40,28),
                         (cx2-20, cy2+30, 40, 5), border_radius=2)
        pygame.draw.rect(surf, (48,60,40),
                         (cx2-20, cy2+30, 40, 2), border_radius=2)
        # Anchor bolts
        for bx3 in (cx2-14, cx2+10):
            pygame.draw.circle(surf, base_shad, (bx3, cy2+35), 3)
            pygame.draw.circle(surf, base_hi,   (bx3, cy2+35), 2)

        # ── ROTATION RING — where turret swivels ──────────────────────────────
        ring_col  = (52, 64, 44)
        ring_hi   = (72, 88, 60)
        pygame.draw.ellipse(surf, (28,35,22),
                            (cx2-15, cy2+13, 30, 12))
        pygame.draw.ellipse(surf, ring_col,
                            (cx2-13, cy2+14, 26, 10))
        pygame.draw.ellipse(surf, ring_hi,
                            (cx2-13, cy2+14, 26, 4))
        # Ring gear teeth
        for ri2 in range(8):
            ang2 = (ri2/8)*2*math.pi
            rx2  = int(cx2 + math.cos(ang2)*12)
            ry2  = int(cy2+19 + math.sin(ang2)*3)
            pygame.draw.circle(surf, base_shad, (rx2, ry2), 2)

        # ── TURRET DOME / BODY ────────────────────────────────────────────────
        dome_col  = (55, 68, 46)
        dome_hi   = (75, 92, 62)
        dome_shad = (36, 46, 30)
        # Main dome
        pygame.draw.ellipse(surf, dome_col,  (cx2-16, cy2+2,  32, 20))
        pygame.draw.ellipse(surf, dome_hi,   (cx2-16, cy2+2,  32, 8))
        pygame.draw.ellipse(surf, dome_shad, (cx2-16, cy2+14, 32, 8))
        # Dome border ring
        pygame.draw.ellipse(surf, dome_shad, (cx2-16, cy2+2, 32, 20), 1)
        # Armour panel seam
        pygame.draw.line(surf, dome_shad,
                         (cx2-14, cy2+12), (cx2+14, cy2+12), 1)
        # Rivets on dome top
        for rv_off in (-8, 0, 8):
            pygame.draw.circle(surf, dome_shad, (cx2+rv_off, cy2+5), 2)
            pygame.draw.circle(surf, dome_hi,   (cx2+rv_off, cy2+5), 1)
        # Sensor bulge (rangefinder)
        pygame.draw.ellipse(surf, dome_shad, (cx2-5, cy2+2, 10, 6))
        pygame.draw.ellipse(surf, (80,180,220),  (cx2-3, cy2+3,  4, 4))

        # ── BARREL ASSEMBLY ────────────────────────────────────────────────────
        cos_b = math.cos(self.barrel_angle)
        sin_b = math.sin(self.barrel_angle)
        recoil_offset = self.barrel_recoil   # barrel slides back on fire

        barrel_origin_x = cx2
        barrel_origin_y = cy2 + 12

        # Barrel shroud (thick, short)
        shroud_len = 10
        shr_ex = int(barrel_origin_x + cos_b * shroud_len)
        shr_ey = int(barrel_origin_y + sin_b * shroud_len)
        pygame.draw.line(surf, dome_col,
                         (barrel_origin_x, barrel_origin_y),
                         (shr_ex, shr_ey), 9)
        pygame.draw.line(surf, dome_hi,
                         (barrel_origin_x, barrel_origin_y),
                         (shr_ex, shr_ey), 3)

        # Main barrel (recoils)
        barrel_start_x = barrel_origin_x + int(cos_b * (shroud_len - recoil_offset))
        barrel_start_y = barrel_origin_y + int(sin_b * (shroud_len - recoil_offset))
        barrel_len = 24
        barrel_end_x = int(barrel_start_x + cos_b * barrel_len)
        barrel_end_y = int(barrel_start_y + sin_b * barrel_len)
        pygame.draw.line(surf, (40, 50, 34),
                         (barrel_start_x, barrel_start_y),
                         (barrel_end_x, barrel_end_y), 5)
        pygame.draw.line(surf, (62, 78, 52),
                         (barrel_start_x, barrel_start_y),
                         (barrel_end_x, barrel_end_y), 2)
        # Muzzle brake
        mb_x = barrel_end_x; mb_y = barrel_end_y
        perp_x = -sin_b; perp_y = cos_b
        pygame.draw.rect(surf, (30,38,26),
                         (int(mb_x - 3), int(mb_y - 4), 7, 8), border_radius=1)
        # Muzzle vents
        for vi2 in (-2, 2):
            pygame.draw.line(surf, (22,28,18),
                             (int(mb_x + perp_x*vi2), int(mb_y + perp_y*vi2 - 3)),
                             (int(mb_x + perp_x*vi2), int(mb_y + perp_y*vi2 + 3)), 1)

        # ── MUZZLE FLASH ──────────────────────────────────────────────────────
        if self.muzzle_flash > 0:
            flash_r = self.muzzle_flash * 4
            flash_s = pygame.Surface((flash_r*2+4, flash_r*2+4), pygame.SRCALPHA)
            flash_a = self.muzzle_flash * 45
            pygame.draw.circle(flash_s, (255, 230, 80, flash_a),
                               (flash_r+2, flash_r+2), flash_r)
            pygame.draw.circle(flash_s, (255, 255, 200, flash_a),
                               (flash_r+2, flash_r+2), flash_r//2)
            surf.blit(flash_s, (barrel_end_x-flash_r-2, barrel_end_y-flash_r-2))
            LIGHTS.add(barrel_end_x + cam_x, barrel_end_y,
                       40, (255,210,60), 0.8, life=2)

        # ── HEAT SHIMMER on barrel ─────────────────────────────────────────────
        if self.heat > 0.3:
            heat_a = int(self.heat * 80)
            heat_col = (255, int(100 + self.heat*155), 20)
            pygame.draw.line(surf, (*heat_col, heat_a),
                             (barrel_start_x, barrel_start_y),
                             (barrel_end_x, barrel_end_y), 1)
            # Heat waves
            for hw in range(3):
                hw_off = int(math.sin(t*0.08 + hw*2.1) * 2)
                hs2 = pygame.Surface((6,6), pygame.SRCALPHA)
                pygame.draw.circle(hs2, (*heat_col, int(heat_a*0.5)),
                                   (3,3), 3)
                mid_x = int(barrel_start_x + cos_b*(barrel_len*0.4 + hw*5))
                mid_y = int(barrel_start_y + sin_b*(barrel_len*0.4 + hw*5))
                surf.blit(hs2, (mid_x+hw_off-3, mid_y-3))

        # ── STATUS LIGHTS ─────────────────────────────────────────────────────
        # HP light (green→red)
        hp_ratio = self.hp / self.MAX_HP
        hp_light_col = (int(220*(1-hp_ratio)), int(180*hp_ratio), 20)
        blink = (self.hp < self.MAX_HP*0.3 and (t//200)%2==0)
        if not blink:
            ls3 = pygame.Surface((8,8), pygame.SRCALPHA)
            pygame.draw.circle(ls3, (*hp_light_col, 220), (4,4), 4)
            surf.blit(ls3, (cx2-16, cy2+3))
            # Glow
            lgs = pygame.Surface((14,14), pygame.SRCALPHA)
            pygame.draw.circle(lgs, (*hp_light_col, 70), (7,7), 7)
            surf.blit(lgs, (cx2-19, cy2))

        # Ammo light (blue→off)
        if self.ammo > 0:
            ammo_ratio = self.ammo / self.MAX_AMMO
            ammo_a = int(150 + ammo_ratio*105)
            als = pygame.Surface((6,6), pygame.SRCALPHA)
            pygame.draw.circle(als, (60,160,255,ammo_a), (3,3), 3)
            surf.blit(als, (cx2+10, cy2+4))

        # ── HP / AMMO BARS ─────────────────────────────────────────────────────
        bw = 32; bx4 = cx2-bw//2; by4 = cy2-13
        # HP bar
        pygame.draw.rect(surf, (8,10,6), (bx4, by4, bw, 5), border_radius=2)
        hp_w = max(0, int(bw * hp_ratio))
        hp_col = (50,200,60) if hp_ratio>0.5 else (220,190,50) if hp_ratio>0.25 else (220,40,40)
        if hp_w > 0:
            pygame.draw.rect(surf, hp_col, (bx4, by4, hp_w, 5), border_radius=2)
        pygame.draw.rect(surf, (40,55,34), (bx4, by4, bw, 5), 1, border_radius=2)

        # Ammo bar
        pygame.draw.rect(surf, (6,8,14), (bx4, by4+6, bw, 4), border_radius=2)
        ammo_w = max(0, int(bw * self.ammo / self.MAX_AMMO))
        if ammo_w > 0:
            pygame.draw.rect(surf, (60,140,220), (bx4, by4+6, ammo_w, 4), border_radius=2)
        pygame.draw.rect(surf, (30,45,70), (bx4, by4+6, bw, 4), 1, border_radius=2)

        # ── LABEL ─────────────────────────────────────────────────────────────
        lf2 = pygame.font.SysFont("consolas", 8, bold=True)
        if self.ammo <= 0:
            lt2 = lf2.render("LEER", True, RED)
        elif self.heat > 0.8:
            lt2 = lf2.render("ÜBERHITZT", True, ORANGE)
        else:
            lt2 = lf2.render("TURRET", True, (100,160,80))
        surf.blit(lt2, (cx2 - lt2.get_width()//2, by4-11))

        # ── DEPLOY ANIMATION: slide-up sparks ─────────────────────────────────
        if self.deploy_anim < 1.0 and self.age < 20:
            for _ in range(3):
                PARTICLES.spawn_sparks(cx2 + cam_x,
                                       int(self.y) + self.H, 3)
 
class SandbagCover:
    """Player-placed sandbag barrier. Key [C]. Blocks bullets, has HP."""
    W = 56; H = 22; MAX_HP = 120

    def __init__(self, x, y):
        self.x     = float(x)
        self.y     = float(y)
        self.hp    = self.MAX_HP
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(int(self.x)-self.W//2, int(self.y)-self.H, self.W, self.H)

    def take_damage(self, amount, is_rocket=False):
        dmg = amount if is_rocket else max(1, amount//3)
        self.hp -= dmg
        PARTICLES.spawn_dust(self.rect.centerx, self.rect.centery)
        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_explosion(self.rect.centerx, self.rect.centery, scale=0.3)

    def draw(self, surf, cam_x=0):
        if not self.alive: return
        sx = int(self.x) - cam_x
        sy = int(self.y)
        tint = max(0, int((1 - self.hp/self.MAX_HP) * 40))

        # Shadow
        sh = pygame.Surface((self.W+8, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,55), (0,0,self.W+8,6))
        surf.blit(sh, (sx-self.W//2-4, sy-2))

        # Two rows of bags
        for row in range(2):
            n = 3 if row == 0 else 2
            bw = self.W // 3
            for bi in range(n):
                off = 0 if row==0 else bw//2
                bx2 = sx - self.W//2 + off + bi*bw
                by2 = sy - self.H + row*11
                bc  = (128+tint, 102-tint//2, 58)
                bhi = (152+tint, 122-tint//2, 72)
                bsh = (100+tint,  80-tint//2, 44)
                pygame.draw.ellipse(surf, bc,  (bx2,      by2,     bw-2, 11))
                pygame.draw.ellipse(surf, bhi, (bx2,      by2,     bw-2,  4))
                pygame.draw.ellipse(surf, bsh, (bx2,      by2+7,   bw-2,  4))
                pygame.draw.line(surf, bsh, (bx2+2,by2+5),(bx2+bw-4,by2+5),1)
                pygame.draw.circle(surf, (90,70,38),(bx2+(bw-2)//2,by2+5),2)

        # HP bar
        bw2=self.W-8; bx3=sx-bw2//2; by3=sy-self.H-8
        pygame.draw.rect(surf,(10,8,6),(bx3,by3,bw2,4))
        hr=self.hp/self.MAX_HP
        hc2=(50,200,80) if hr>0.5 else (220,180,40) if hr>0.25 else (220,40,40)
        if hr>0: pygame.draw.rect(surf,hc2,(bx3,by3,int(bw2*hr),4))
        pygame.draw.rect(surf,(60,50,30),(bx3,by3,bw2,4),1)
        lf=pygame.font.SysFont("consolas",8,bold=True)
        surf.blit(lf.render("[C] DECKUNG",True,(140,115,65)),
                  (sx-lf.size("[C] DECKUNG")[0]//2,by3-10))

# ═══════════════════════════════════════════════════
#  V7.0 BASE BUILDING SYSTEM
# ═══════════════════════════════════════════════════
BASE_BUILD_COSTS = {
    "wall":     {"score": 0,   "label": "Mauer [B+1]",       "key": pygame.K_1},
    "mg_nest":  {"score": 0,   "label": "MG-Nest [B+2]",     "key": pygame.K_2},
    "mine":     {"score": 0,   "label": "Mine [B+3]",        "key": pygame.K_3},
    "barrier":  {"score": 0,   "label": "Barriere [B+4]",    "key": pygame.K_4},
    "heal_pad": {"score": 0,   "label": "Heilfeld [B+5]",    "key": pygame.K_5},
}

class BaseWall:
    """Bullet-blocking wall the player builds. Damaged by bullets/explosions."""
    W = 20; H = 60; MAX_HP = 200
    def __init__(self, x, y):
        self.x = float(x); self.y = float(y - self.H)
        self.hp = self.MAX_HP; self.alive = True
        self.crack_seed = random.randint(0,999)

    @property
    def rect(self): return pygame.Rect(int(self.x)-self.W//2, int(self.y), self.W, self.H)

    def take_damage(self, amount, is_rocket=False):
        self.hp -= amount * (3 if is_rocket else 1)
        PARTICLES.spawn_dust(self.rect.centerx, self.rect.centery)
        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_explosion(self.rect.centerx, self.rect.centery, scale=0.4)

    def draw(self, surf, cam_x=0):
        if not self.alive: return
        sx = int(self.x) - cam_x
        hr = self.hp / self.MAX_HP
        # Damage tint
        tint = int((1-hr)*60)
        base_col = (80+tint, 72-tint//2, 60-tint//2)
        hi_col   = (110+tint, 100-tint//2, 85-tint//2)
        shad_col = (55, 48, 38)

        # Shadow
        sh = pygame.Surface((self.W+6,6),pygame.SRCALPHA)
        pygame.draw.ellipse(sh,(0,0,0,55),(0,0,self.W+6,6))
        surf.blit(sh,(sx-self.W//2-3,int(self.y)+self.H-2))

        # Main block
        pygame.draw.rect(surf,base_col,(sx-self.W//2,int(self.y),self.W,self.H),border_radius=2)
        # Top face
        pygame.draw.rect(surf,hi_col,(sx-self.W//2,int(self.y),self.W,6),border_radius=2)
        # Side shadow
        pygame.draw.rect(surf,shad_col,(sx+self.W//2-5,int(self.y),5,self.H))
        # Brick lines
        cr = random.Random(self.crack_seed)
        for row in range(0, self.H, 16):
            offset = 8 if (row//16)%2==0 else 0
            for col in range(-self.W//2+offset, self.W//2, 16):
                pygame.draw.rect(surf,(max(0,base_col[0]-15),max(0,base_col[1]-15),
                                       max(0,base_col[2]-15)),
                                 (sx+col, int(self.y)+row, 14, 14),1)
        # Damage cracks
        if hr < 0.7:
            for _ in range(int((1-hr)*6)):
                crx=sx-self.W//2+cr.randint(2,self.W-4)
                cry=int(self.y)+cr.randint(4,self.H-4)
                pygame.draw.line(surf,(40,30,20),(crx,cry),
                                 (crx+cr.randint(-6,6),cry+cr.randint(-8,8)),1)
        # HP bar
        bw=self.W+4; bx=sx-bw//2; by=int(self.y)-10
        pygame.draw.rect(surf,(10,8,6),(bx,by,bw,5))
        hc=(50,200,80) if hr>0.5 else (220,180,40) if hr>0.25 else (220,40,40)
        if hr>0: pygame.draw.rect(surf,hc,(bx,by,int(bw*hr),5))
        pygame.draw.rect(surf,(55,44,30),(bx,by,bw,5),1)


class MGNest:
    """Player-built auto MG turret with higher fire rate than DeployedTurret."""
    W = 48; H = 36; MAX_HP = 140; MAX_AMMO = 80; SHOOT_RATE = 220; RANGE = 580; DAMAGE = 16
    def __init__(self, x, y):
        self.x = float(x); self.y = float(y)
        self.hp = self.MAX_HP; self.ammo = self.MAX_AMMO
        self.alive = True; self.last_shot = 0; self.barrel_angle = 0.0
        self.heat = 0.0; self.overheated = False; self.overheat_timer = 0
        self.muzzle_flash = 0; self.age = 0; self.deploy_anim = 0.0
        self.total_kills = 0

    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self, all_enemies, bullets):
        if not self.alive: return
        self.age += 1; self.deploy_anim = min(1.0, self.deploy_anim+0.1)
        if self.muzzle_flash>0: self.muzzle_flash-=1
        if self.overheated:
            self.overheat_timer-=1
            self.heat=max(0.0,self.heat-0.012)
            if self.overheat_timer<=0 and self.heat<0.2: self.overheated=False
            return
        self.heat=max(0.0,self.heat-0.006)
        if self.ammo<=0: return
        now=pygame.time.get_ticks(); target=None; best_d=self.RANGE
        for e in all_enemies:
            if not getattr(e,'alive',False): continue
            d=math.hypot(e.rect.centerx-self.rect.centerx,e.rect.centery-self.rect.centery)
            if d<best_d: best_d=d; target=e
        if target and now-self.last_shot>=self.SHOOT_RATE:
            self.last_shot=now; self.ammo-=1
            ox=self.rect.centerx; oy=self.rect.top+6
            dx=target.rect.centerx-ox; dy=target.rect.centery-oy
            d=math.hypot(dx,dy) or 1
            self.barrel_angle=math.atan2(dy,dx)
            self.heat=min(1.0,self.heat+0.07)
            self.muzzle_flash=4
            if self.heat>=1.0: self.overheated=True; self.overheat_timer=180
            bullets.append(Bullet(ox,oy,dx/d*18,dy/d*18,
                                  int(self.DAMAGE * SKILLS.turret_dmg_mult()),ORANGE))
            SFX.play(SFX.shoot_pistol)
            PARTICLES.spawn_muzzle_flash(ox+int(math.cos(self.barrel_angle)*22),
                                          oy+int(math.sin(self.barrel_angle)*22),1)

    def take_damage(self, amount, is_rocket=False):
        self.hp-=amount*(2 if is_rocket else 1)
        PARTICLES.spawn_sparks(self.rect.centerx,self.rect.centery,5)
        if self.hp<=0:
            self.alive=False
            PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=0.8)
            SFX.play(SFX.explosion)

    def draw(self, surf, cam_x=0):
        if not self.alive: return
        t=pygame.time.get_ticks(); sx=int(self.x)-cam_x; cx=sx+self.W//2
        deploy_off=int((1.0-self.deploy_anim)*30); cy=int(self.y)+deploy_off
        # Shadow
        sh=pygame.Surface((self.W+10,7),pygame.SRCALPHA)
        pygame.draw.ellipse(sh,(0,0,0,60),(0,0,self.W+10,7))
        surf.blit(sh,(cx-self.W//2-5,int(self.y)+self.H-2))
        # Sandbag base
        for sbi in range(5):
            bx=cx-22+sbi*10; by=cy+20
            bc=(110,88,50); bhi=(135,108,64)
            pygame.draw.ellipse(surf,bc,(bx,by,12,9))
            pygame.draw.ellipse(surf,bhi,(bx,by,12,4))
        for sbi in range(4):
            bx=cx-17+sbi*10; by=cy+27
            pygame.draw.ellipse(surf,(105,82,46),(bx,by,12,9))
        # Tripod legs
        leg_col=(42,52,40)
        for lx,ly in ((cx-16,cy+36),(cx+16,cy+36),(cx,cy+38)):
            pygame.draw.line(surf,leg_col,(cx,cy+18),(lx,ly),3)
        # Receiver/body
        pygame.draw.rect(surf,(38,46,34),(cx-14,cy+4,28,18),border_radius=3)
        pygame.draw.rect(surf,(56,68,50),(cx-14,cy+4,28,6),border_radius=3)
        # Belt feed
        for bi in range(5):
            pygame.draw.rect(surf,(185,150,40),(cx-12+bi*5,cy+14,4,6),border_radius=1)
        # Barrel
        cos_b=math.cos(self.barrel_angle); sin_b=math.sin(self.barrel_angle)
        blen=28
        bex=int(cx+cos_b*blen); bey=int(cy+12+sin_b*blen)
        pygame.draw.line(surf,(30,38,28),(cx,cy+12),(bex,bey),7)
        pygame.draw.line(surf,(50,62,46),(cx,cy+12),(bex,bey),3)
        # Muzzle brake
        pygame.draw.rect(surf,(22,28,18),(bex-3,bey-4,7,8),border_radius=1)
        # Muzzle flash
        if self.muzzle_flash>0:
            mfs=pygame.Surface((20,20),pygame.SRCALPHA)
            pygame.draw.circle(mfs,(255,220,80,self.muzzle_flash*40),(10,10),9)
            surf.blit(mfs,(bex-10,bey-10))
            LIGHTS.add(bex+cam_x,bey,35,ORANGE,0.7,life=1)
        # Heat bar
        if self.heat>0.1:
            hb_col=(255,int(180*(1-self.heat)),20)
            pygame.draw.rect(surf,(10,8,6),(cx-14,cy-12,28,5),border_radius=2)
            pygame.draw.rect(surf,hb_col,(cx-14,cy-12,int(28*self.heat),5),border_radius=2)
            if self.overheated:
                ot=pygame.font.SysFont("consolas",8,bold=True)
                otr=ot.render("ÜBERHITZT",True,(255,80,20))
                surf.blit(otr,(cx-otr.get_width()//2,cy-22))
        # Status
        lf=pygame.font.SysFont("consolas",8,bold=True)
        if self.ammo<=0:
            surf.blit(lf.render("LEER",True,RED),(cx-10,cy-22))
        # HP bar
        bw2=40; bx2=cx-bw2//2; by2=cy-30
        pygame.draw.rect(surf,(8,10,6),(bx2,by2,bw2,5),border_radius=2)
        hp_r=self.hp/self.MAX_HP
        hc=(50,200,60) if hp_r>0.5 else (220,40,40)
        if hp_r>0: pygame.draw.rect(surf,hc,(bx2,by2,int(bw2*hp_r),5),border_radius=2)
        surf.blit(lf.render("MG-NEST",True,(120,170,90)),(cx-14,by2-11))


class LandMine:
    """Player-placed mine. Triggers on enemy proximity. One-use."""
    RADIUS = 16; TRIGGER_DIST = 45; EXPLOSION_R = 130; DAMAGE = 120
    def __init__(self, x, y):
        self.x = float(x); self.y = float(y)
        self.alive = True; self.triggered = False; self.trigger_timer = 0
        self.age = 0; self.buried_anim = 0.0

    @property
    def rect(self): return pygame.Rect(int(self.x)-self.RADIUS, int(self.y)-4, self.RADIUS*2, 8)

    def update(self, all_enemies, player_ref):
        self.age += 1
        self.buried_anim = min(1.0, self.buried_anim+0.08)
        if self.triggered:
            self.trigger_timer += 1
            if self.trigger_timer == 8:
                self.alive = False
                SFX.play(SFX.big_explosion)
                PARTICLES.spawn_explosion(self.x, self.y, scale=1.4)
                LIGHTS.add_explosion_light(self.x, self.y, scale=2.0)
                # Damage
                for e in all_enemies:
                    d=math.hypot(e.rect.centerx-self.x,e.rect.centery-self.y)
                    if d<self.EXPLOSION_R and e.alive:
                        e.take_damage(int(self.DAMAGE*(1-d/self.EXPLOSION_R)))
                return
            return
        for e in all_enemies:
            if not e.alive: continue
            d=math.hypot(e.rect.centerx-self.x,e.rect.centery-self.y)
            if d<self.TRIGGER_DIST and self.buried_anim>=1.0:
                self.triggered=True
                SFX.play(SFX.hit_enemy)
                PARTICLES.spawn_sparks(self.x,self.y,8)
                break

    def draw(self, surf, cam_x=0):
        if not self.alive: return
        sx=int(self.x)-cam_x; sy=int(self.y)
        t=pygame.time.get_ticks()
        # Buried look
        bury_depth=int((1.0-self.buried_anim)*14)
        sy+=bury_depth
        # Mine disc
        col=(55,55,55) if not self.triggered else (255,80,20)
        pygame.draw.ellipse(surf,col,(sx-14,sy-5,28,10))
        pygame.draw.ellipse(surf,(75,75,75),(sx-14,sy-5,28,4))
        # Center prong
        if not self.triggered:
            pygame.draw.circle(surf,(80,80,80),(sx,sy-3),3)
            pygame.draw.circle(surf,(120,120,120),(sx,sy-3),2)
        else:
            # Blinking
            if (t//80)%2==0:
                bls=pygame.Surface((20,20),pygame.SRCALPHA)
                pygame.draw.circle(bls,(255,40,40,200),(10,10),10)
                surf.blit(bls,(sx-10,sy-14))
                pygame.draw.circle(surf,(255,40,40),(sx,sy-3),4)
        # Warning indicator after arming
        if self.buried_anim>=1.0 and not self.triggered:
            wa=(t//400)%2==0
            if wa:
                ws=pygame.Surface((8,8),pygame.SRCALPHA)
                pygame.draw.circle(ws,(255,200,20,180),(4,4),4)
                surf.blit(ws,(sx-4,sy-13))
        lf=pygame.font.SysFont("consolas",7,bold=True)
        surf.blit(lf.render("MINE",True,(80,80,80)),(sx-9,sy+6))


class HealPad:
    """Deployable healing zone. Heals player slowly while standing on it."""
    W = 80; HEAL_RATE = 60; HEAL_AMOUNT = 1; MAX_CHARGES = 15
    def __init__(self, x, y):
        self.x = float(x); self.y = float(y)
        self.alive = True; self.charges = self.MAX_CHARGES
        self.heal_timer = 0; self.pulse = 0.0; self.age = 0

    @property
    def rect(self): return pygame.Rect(int(self.x)-self.W//2, int(self.y)-8, self.W, 12)

    def update(self, player):
        if not self.alive or self.charges<=0: return
        self.age+=1; self.pulse=(self.pulse+0.06)%(2*math.pi)
        if self.rect.colliderect(player.rect):
            self.heal_timer+=1
            if self.heal_timer>=self.HEAL_RATE:
                self.heal_timer=0; self.charges-=1
                player.hp=min(player.MAX_HP,player.hp+self.HEAL_AMOUNT)
                PARTICLES.spawn_pickup(self.x,self.y,(50,220,80))
                if self.charges<=0:
                    self.alive=False
                    PARTICLES.spawn_dust(self.x,self.y)

    def draw(self, surf, cam_x=0):
        if not self.alive: return
        sx=int(self.x)-cam_x; sy=int(self.y)
        ratio=self.charges/self.MAX_CHARGES
        pulse_a=int(40+abs(math.sin(self.pulse))*60)
        # Glowing pad
        ps=pygame.Surface((self.W+20,24),pygame.SRCALPHA)
        pygame.draw.ellipse(ps,(50,220,80,pulse_a),(0,0,self.W+20,24))
        surf.blit(ps,(sx-self.W//2-10,sy-8))
        # Frame
        pygame.draw.ellipse(surf,(30,120,50),(sx-self.W//2,sy-6,self.W,10))
        pygame.draw.ellipse(surf,(50,200,80),(sx-self.W//2,sy-6,self.W,10),1)
        # Cross symbol
        pygame.draw.rect(surf,(80,255,120),(sx-3,sy-9,6,14),border_radius=1)
        pygame.draw.rect(surf,(80,255,120),(sx-9,sy-4,18,5),border_radius=1)
        # Charges bar
        lf=pygame.font.SysFont("consolas",8,bold=True)
        surf.blit(lf.render(f"HEILFELD ×{self.charges}",True,(50,200,70)),(sx-24,sy+6))
        bw=self.W; bx=sx-bw//2; by=sy+16
        pygame.draw.rect(surf,(8,20,10),(bx,by,bw,4))
        pygame.draw.rect(surf,(50,200,80),(bx,by,int(bw*ratio),4))


class BaseBuildSystem:
    """Manages all player-built structures."""
    def __init__(self):
        self.walls:     list[BaseWall]   = []
        self.mg_nests:  list[MGNest]     = []
        self.mines:     list[LandMine]   = []
        self.barriers:  list[SandbagCover]= []
        self.heal_pads: list[HealPad]    = []
        self.build_mode = False
        self.selected_build = "wall"
        self.total_built = 0
        self.build_preview_alpha = 0

    def reset(self):
        self.__init__()

    def can_build(self, kind, player):
        limits = {"wall":8,"mg_nest":3,"mine":10,"barrier":5,"heal_pad":2}
        lists  = {"wall":self.walls,"mg_nest":self.mg_nests,"mine":self.mines,
                  "barrier":self.barriers,"heal_pad":self.heal_pads}
        active = [s for s in lists[kind] if s.alive]
        return len(active) < limits[kind]

    def place(self, kind, player):
        if not self.can_build(kind, player): return False
        gx = player.rect.centerx + player.facing*60
        gy = player.rect.bottom
        if kind=="wall":
            self.walls.append(BaseWall(gx, gy))
        elif kind=="mg_nest":
            self.mg_nests.append(MGNest(float(gx-24), float(gy-36)))
        elif kind=="mine":
            self.mines.append(LandMine(float(gx), float(gy)))
        elif kind=="barrier":
            self.barriers.append(SandbagCover(float(gx), float(gy)))
        elif kind=="heal_pad":
            self.heal_pads.append(HealPad(float(gx), float(gy)))
        SFX.play(SFX.pickup)
        self.total_built += 1
        if self.total_built >= 5: unlock("base_master")
        return True

    def update(self, all_enemies, bullets, player):
        for w in self.walls:
            for b in bullets:
                if b.alive and b.get_rect().colliderect(w.rect):
                    w.take_damage(b.damage); b.alive=False
        for mg in self.mg_nests: mg.update(all_enemies, bullets)
        for m in self.mines: m.update(all_enemies, player)
        for hp in self.heal_pads: hp.update(player)
        self.walls    = [w for w in self.walls    if w.alive]
        self.mg_nests = [m for m in self.mg_nests if m.alive]
        self.mines    = [m for m in self.mines    if m.alive]
        self.barriers = [b for b in self.barriers if b.alive]
        self.heal_pads= [h for h in self.heal_pads if h.alive]

    def draw(self, surf, cam_x=0):
        for w in self.walls:     w.draw(surf, cam_x)
        for mg in self.mg_nests: mg.draw(surf, cam_x)
        for m in self.mines:     m.draw(surf, cam_x)
        for b in self.barriers:  b.draw(surf, cam_x)
        for h in self.heal_pads: h.draw(surf, cam_x)

    def draw_hud(self, surf, player, build_mode):
        if not build_mode: return
        f = pygame.font.SysFont("consolas",12,bold=True)
        panel=pygame.Surface((280,165),pygame.SRCALPHA)
        for py in range(165):
            t=py/165
            pygame.draw.line(panel,(4,12,4,int(210-t*55)),(0,py),(280,py))
        pygame.draw.rect(panel,(40,100,40),(0,0,280,165),1,border_radius=5)
        pygame.draw.rect(panel,(60,140,60),(0,0,280,3),border_radius=5)
        ht=pygame.font.SysFont("consolas",13,bold=True).render("⚒  BAUMODUS",True,(80,220,80))
        panel.blit(ht,(10,8))
        items=[("wall","Mauer","B+1",len([w for w in self.walls if w.alive]),8),
               ("mg_nest","MG-Nest","B+2",len([m for m in self.mg_nests if m.alive]),3),
               ("mine","Mine","B+3",len([m for m in self.mines if m.alive]),10),
               ("barrier","Barriere","B+4",len([b for b in self.barriers if b.alive]),5),
               ("heal_pad","Heilfeld","B+5",len([h for h in self.heal_pads if h.alive]),2),]
        for i,(kind,label,key,count,limit) in enumerate(items):
            y=28+i*26; is_sel=self.selected_build==kind
            if is_sel:
                sel_bg=pygame.Surface((260,22),pygame.SRCALPHA)
                sel_bg.fill((40,100,40,120))
                pygame.draw.rect(sel_bg,(60,180,60),(0,0,260,22),1,border_radius=2)
                panel.blit(sel_bg,(10,y-2))
            col=(100,220,80) if is_sel else (60,100,60)
            lt=f.render(f"[{key}] {label}  ({count}/{limit})",True,col)
            panel.blit(lt,(14,y))
        surf.blit(panel,(WIDTH-295,HEIGHT-215))

BASE_BUILD = BaseBuildSystem()

# ── Drop System ────────────────────────────────────────────────────────────────
class Drop:
    SIZE = 22
    TYPES = {
        "cash":   {"color": GOLD,   "symbol": "$",  "desc": "+Score Bonus"},
        "ammo":   {"color": YELLOW, "symbol": "A",  "desc": "Munition voll"},
        "hp":     {"color": RED,    "symbol": "+",  "desc": "+25 HP"},
        "grenade":{"color": GREEN,  "symbol": "G",  "desc": "+1 Granate"},
    }
 
    def __init__(self, x, y, kind=None):
        self.x  = float(x); self.y = float(y)
        self.vy = -5.0
        weights = ["cash", "cash", "cash", "ammo", "ammo", "hp", "grenade"]
        self.kind   = kind or random.choice(weights)
        self.alive  = True
        self.age    = 0
        self.lifetime = 420   # 7 seconds
        self.bob    = random.uniform(0, 6.28)
 
    @property
    def rect(self):
        s = self.SIZE
        return pygame.Rect(int(self.x)-s//2, int(self.y)-s//2, s, s)
 
    def update(self):
        self.age += 1
        self.vy = min(self.vy + 0.5, 10)
        self.y  += self.vy
        # Land on ground / platforms
        if self.y >= GROUND_Y - self.SIZE//2:
            self.y = GROUND_Y - self.SIZE//2; self.vy = 0
        for plat in current_platforms:
            pr = self.rect
            if pr.colliderect(plat) and self.vy > 0:
                if pr.bottom - self.vy <= plat.top + abs(self.vy) + 4:
                    self.y = plat.top - self.SIZE//2; self.vy = 0
        if self.age >= self.lifetime: self.alive = False
 
    def draw(self, surf, cam_x=0):
        if not self.alive: return
        # Blink before disappearing
        if self.age > self.lifetime - 120 and (self.age // 6) % 2 == 0: return
        cfg = self.TYPES[self.kind]
        bob_y = int(math.sin(self.age * 0.1 + self.bob) * 3)
        sx    = int(self.x) - cam_x
        sy    = int(self.y) + bob_y
        s     = self.SIZE
        # Glow
        gs2 = pygame.Surface((s*3, s*3), pygame.SRCALPHA)
        pulse2 = int(40 + abs(math.sin(self.age * 0.12)) * 60)
        pygame.draw.circle(gs2, (*cfg["color"], pulse2), (s*3//2, s*3//2), s)
        surf.blit(gs2, (sx - s*3//2, sy - s*3//2))
        # Body
        pygame.draw.rect(surf, DARK, (sx-s//2, sy-s//2, s, s), border_radius=5)
        pygame.draw.rect(surf, cfg["color"], (sx-s//2, sy-s//2, s, s), 2, border_radius=5)
        # Symbol
        f = pygame.font.SysFont("consolas", 12, bold=True)
        t = f.render(cfg["symbol"], True, cfg["color"])
        surf.blit(t, (sx - t.get_width()//2, sy - t.get_height()//2))
 
    def apply(self, player):
        cfg = self.TYPES[self.kind]
        PARTICLES.spawn_pickup(self.x, self.y, cfg["color"])
        SFX.play(SFX.pickup)
        self.alive = False
        if self.kind == "cash":
            bonus = int(150 * get_diff()["score_mult"])
            player.score += bonus
            return f"+{bonus} Score!"
        elif self.kind == "ammo":
            RAKETENWERFER.ammo = RAKETENWERFER.max_ammo
            STINGER.ammo = STINGER.max_ammo
            EMP_CANNON.ammo = EMP_CANNON.max_ammo if EMP_CANNON.max_ammo else None
            return "Munition aufgeladen!"
        elif self.kind == "hp":
            player.hp = min(player.MAX_HP, player.hp + 25)
            return "+25 HP"
        elif self.kind == "grenade":
            player.grenades = min(player.grenades + 1, 9)
            return "+1 Granate"
        return cfg["desc"]
 
 
def maybe_drop(x, y, base_rate=0.35):
    """Call on enemy death. Returns a Drop or None."""
    if random.random() < base_rate:
        return Drop(x, y)
    return None

class Rocket:
    RADIUS=6
    def __init__(self,x,y,vx,vy,damage,color,is_stinger=False):
        self.x=float(x);self.y=float(y);self.vx=vx;self.vy=vy
        self.damage=damage;self.color=color;self.alive=True
        self.is_stinger=is_stinger;self.explosion_r=160 if not is_stinger else 120
        self.homing_target=None

    def get_rect(self):
        r=self.RADIUS
        return pygame.Rect(self.x-r, self.y-r, r*2, r*2)

    def update(self, air_targets=None):
        if self.is_stinger and air_targets:
            if self.homing_target is None or not self.homing_target.alive:
                best = None; best_d = 9999
                for t in air_targets:
                    # Track ALL air types including BomberJet
                    if not getattr(t, 'alive', False): continue
                    d = math.hypot(t.x - self.x, t.y - self.y)
                    if d < best_d: best_d = d; best = t
                self.homing_target = best
            if self.homing_target and getattr(self.homing_target, 'alive', False):
                tx = self.homing_target.x
                # Aim at center of target, not just x origin
                ty = self.homing_target.y + getattr(self.homing_target, 'H', 20) / 2
                dx = tx - self.x; dy = ty - self.y
                dist = math.hypot(dx, dy) or 1
                spd  = math.hypot(self.vx, self.vy)
                self.vx += (dx/dist*spd - self.vx) * 0.10
                self.vy += (dy/dist*spd - self.vy) * 0.10
        self.x += self.vx; self.y += self.vy
        PARTICLES.spawn_smoke(self.x, self.y)
        if self.x < -200 or self.x > WORLD_WIDTH+200 or self.y < -400 or self.y > HEIGHT+100:
            self.alive = False
            
    def explode(self,targets):
        self.alive=False;SFX.play(SFX.big_explosion);PARTICLES.spawn_explosion(self.x,self.y,scale=2.0)
        hits=[]
        for t in targets:
            d=math.hypot(t.x-self.x,t.y-self.y)
            if d<=self.explosion_r: hits.append((t,int(self.damage*(1-d/self.explosion_r))))
        return hits
    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        sy  = int(self.y)
        angle = math.atan2(self.vy, self.vx)
        col   = CYAN if self.is_stinger else ROCKET_COL

        # ── Exhaust flame trail (longest, drawn first) ────────────────────────
        tail_x = sx - math.cos(angle) * 14
        tail_y = sy - math.sin(angle) * 14
        for i in range(10):
            t2 = i / 10
            px = int(tail_x - math.cos(angle) * 36 * t2)
            py = int(tail_y - math.sin(angle) * 36 * t2)
            r2 = max(1, int(7 * (1 - t2)))
            fc = [(255,252,120),(255,200,40),(255,130,20),(220,70,10),
                  (180,40,5),(130,25,3),(90,15,1),(60,8,0),(35,4,0),(15,2,0)][i]
            fa = int(240 * (1-t2))
            fs2 = pygame.Surface((r2*2+2, r2*2+2), pygame.SRCALPHA)
            pygame.draw.circle(fs2, (*fc, fa), (r2+1,r2+1), r2)
            surf.blit(fs2, (px-r2-1, py-r2-1))

        # ── Rocket body (oriented to travel direction) ─────────────────────────
        body_len = 22; body_w = 7
        cos_a = math.cos(angle); sin_a = math.sin(angle)
        perp_x = -sin_a; perp_y = cos_a

        def rpt(along, across):
            return (int(sx + cos_a*along + perp_x*across),
                    int(sy + sin_a*along + perp_y*across))

        # Body polygon
        body_pts = [rpt(-body_len//2, -body_w//2),
                    rpt(-body_len//2,  body_w//2),
                    rpt( body_len//2,  body_w//2),
                    rpt( body_len//2, -body_w//2)]
        body_col2 = (55,75,55) if not self.is_stinger else (30,85,95)
        pygame.draw.polygon(surf, body_col2, body_pts)
        # Top shine
        shine_pts = [rpt(-body_len//2, -body_w//2),
                     rpt( body_len//2, -body_w//2),
                     rpt( body_len//2, -body_w//2+2),
                     rpt(-body_len//2, -body_w//2+2)]
        pygame.draw.polygon(surf, (80,110,80) if not self.is_stinger else (50,120,135),
                            shine_pts)
        # Nose cone
        nose = rpt(body_len//2 + 8, 0)
        pygame.draw.polygon(surf, col,
                            [rpt(body_len//2, -body_w//2),
                             rpt(body_len//2,  body_w//2),
                             nose])
        # Fins
        for sign in (-1, 1):
            pygame.draw.polygon(surf, (40,56,40) if not self.is_stinger else (22,62,72),
                                [rpt(-body_len//2, sign*(body_w//2)),
                                 rpt(-body_len//2 - 8, sign*(body_w//2+6)),
                                 rpt(-body_len//2 + 4, sign*(body_w//2))])
        # Nozzle ring
        noz = rpt(-body_len//2, 0)
        pygame.draw.circle(surf, (22,28,18), noz, 4)
        pygame.draw.circle(surf, (40,50,32), noz, 2)

        # ── Stinger seeker glow ────────────────────────────────────────────────
        if self.is_stinger:
            sg = pygame.Surface((20,20), pygame.SRCALPHA)
            pulse3 = int(60+abs(math.sin(pygame.time.get_ticks()*0.01))*80)
            pygame.draw.circle(sg, (*CYAN, pulse3), (10,10), 10)
            surf.blit(sg, (int(nose[0])-10, int(nose[1])-10))

class Grenade:
    RADIUS=8;GRAVITY=0.4;EXPLOSION_R=130;DAMAGE=60;FUSE_MS=2000
    def __init__(self,x,y,direction):
        self.x=float(x);self.y=float(y);self.vx=direction*10;self.vy=-14
        self.alive=True;self.exploded=False
        self.spawn=pygame.time.get_ticks();self.explode_time=0
        self.hits_in_explosion=0
    def update(self,enemies):
        if self.exploded:
            if pygame.time.get_ticks()-self.explode_time>400: self.alive=False
            return []
        self.vy+=self.GRAVITY;self.x+=self.vx;self.y+=self.vy
        if self.y>=GROUND_Y-self.RADIUS:
            self.y=GROUND_Y-self.RADIUS;self.vy=-self.vy*0.4;self.vx*=0.6;PARTICLES.spawn_dust(self.x,self.y)
        for plat in current_platforms:
            gr=pygame.Rect(self.x-self.RADIUS,self.y-self.RADIUS,self.RADIUS*2,self.RADIUS*2)
            if gr.colliderect(plat) and self.vy>0 and self.y-self.vy<=plat.top+4:
                self.y=plat.top-self.RADIUS;self.vy=-self.vy*0.4;self.vx*=0.6
        if pygame.time.get_ticks()-self.spawn>=self.FUSE_MS: return self._explode(enemies)
        return []
    def _explode(self,enemies):
        self.exploded=True;self.explode_time=pygame.time.get_ticks()
        SFX.play(SFX.explosion);PARTICLES.spawn_explosion(self.x,self.y)
        hits=[]
        eff_r = int(self.EXPLOSION_R * SKILLS.explosion_radius_mult())
        for e in enemies:
            d=math.hypot(e.x-self.x,e.y-self.y)
            if d<=eff_r:
                hits.append((e,int(self.DAMAGE*(1-d/eff_r))))
                self.hits_in_explosion+=1
        if self.hits_in_explosion>=3: unlock("grenade_multi")
        return hits
    def draw(self, surf, cam_x=0):
        sx = int(self.x) - cam_x
        sy = int(self.y)
        if not self.exploded:
            # Schatten
            shadow = pygame.Surface((20, 6), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 60), (0, 0, 20, 6))
            surf.blit(shadow, (sx - 10, sy + self.RADIUS))
            # Granaten-Körper
            pygame.draw.circle(surf, GRENADE_COL, (sx, sy), self.RADIUS)
            pygame.draw.circle(surf, (120, 200, 120), (sx, sy), self.RADIUS, 1)
            # Zünder-Indikator: wird schneller rot je näher Explosion
            fuse_ratio = (pygame.time.get_ticks() - self.spawn) / self.FUSE_MS
            blink_rate = int(6 + fuse_ratio * 20)  # schneller blinken
            if (pygame.time.get_ticks() // blink_rate) % 2 == 0:
                pygame.draw.circle(surf, (255, 50 + int(fuse_ratio*200), 50), (sx, sy), 4)
            # Rauchspur wenn in Bewegung
            if abs(self.vx) > 1 or abs(self.vy) > 1:
                for i in range(3):
                    tx = sx - int(self.vx * i * 1.5)
                    ty = sy - int(self.vy * i * 1.5)
                    a = 80 - i * 25
                    ts = pygame.Surface((8, 8), pygame.SRCALPHA)
                    pygame.draw.circle(ts, (150, 150, 150, a), (4, 4), 4 - i)
                    surf.blit(ts, (tx - 4, ty - 4))
        elif self.exploded:
            # Explosions-Ring
            age = pygame.time.get_ticks() - self.explode_time
            r = int(age * 0.35)
            if r < 80:
                ring = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
                alpha = max(0, 180 - int(age * 0.5))
                pygame.draw.circle(ring, (255, 180, 50, alpha), (r+2, r+2), r, 3)
                surf.blit(ring, (sx - r - 2, sy - r - 2))

# ═══════════════════════════════════════════════════
#  ZONEN
# ═══════════════════════════════════════════════════
current_platforms=[]

def make_zones():
    WW=WORLD_WIDTH; GY=GROUND_Y
    return {
        1:{"zone_num":1, "name":"ZONE 1: ZERSTOERTE STADT",
           "sky":(28,38,58), "ground":(65,52,38),
           "enemy_hp":50, "enemy_speed":2.2, "enemy_shoot_rate":1700,
           "air_enemies":[], "powerup_count":4,
           "shield_positions":  [(1400,GY-52),(2200,GY-52)],
           "sniper_positions":  [(1800,GY-170),(2700,GY-170)],
           "heavy_positions":   [],
           "kamikaze_positions":[],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(260,GY-110,140,18),pygame.Rect(460,GY-170,110,18),
               pygame.Rect(700,GY-120,130,18),pygame.Rect(880,GY-210,100,18),
               pygame.Rect(1050,GY-150,150,18),pygame.Rect(1250,GY-250,120,18),
               pygame.Rect(1500,GY-130,200,18),pygame.Rect(1800,GY-170,110,18),
               pygame.Rect(1980,GY-240,100,18),pygame.Rect(2150,GY-130,130,18),
               pygame.Rect(2350,GY-190,110,18),pygame.Rect(2520,GY-260,130,18),
               pygame.Rect(2700,GY-140,150,18),pygame.Rect(2950,GY-200,130,18)],
           "enemy_positions":[(900,GY-52),(1200,GY-52),(1550,GY-52),(1850,GY-52),
               (2200,GY-52),(2500,GY-52),(2750,GY-52),(880,GY-230),(1250,GY-272),(2520,GY-282)]},
 
        2:{"zone_num":2, "name":"ZONE 2: WALD",
           "sky":(18,42,20), "ground":(35,62,25),
           "enemy_hp":70, "enemy_speed":2.8, "enemy_shoot_rate":1300,
           "air_enemies":[("drone",1200),("drone",2400)], "powerup_count":4,
           "shield_positions":  [(1500,GY-52)],
           "sniper_positions":  [(1000,GY-155),(2800,GY-155)],
           "heavy_positions":   [],
           "kamikaze_positions":[1800,3000],
           "stealth_positions": [(600,GY-52),(2200,GY-52)],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(200,GY-100,100,18),pygame.Rect(370,GY-155,90,18),
               pygame.Rect(530,GY-100,100,18),pygame.Rect(700,GY-200,80,18),
               pygame.Rect(860,GY-140,120,18),pygame.Rect(1040,GY-220,90,18),
               pygame.Rect(1550,GY-80,70,18),pygame.Rect(1850,GY-130,120,18),
               pygame.Rect(2050,GY-200,90,18),pygame.Rect(2750,GY-150,130,18),
               pygame.Rect(3150,GY-150,130,18)],
           "enemy_positions":[(800,GY-52),(1100,GY-52),(1500,GY-52),(1700,GY-52),
               (2000,GY-52),(2300,GY-52),(2600,GY-52),(2900,GY-52),(700,GY-222),(2050,GY-222)]},
 
        3:{"zone_num":3, "name":"ZONE 3: WUESTENFRONT",
           "sky":(80,55,30), "ground":(140,100,50),
           "enemy_hp":85, "enemy_speed":2.5, "enemy_shoot_rate":1400,
           "air_enemies":[("drone",1500),("drone",2800),("drone",3500)], "powerup_count":5,
           "tank_positions":    [(1800,GY-52),(3000,GY-52)],
           "shield_positions":  [(1200,GY-52),(2500,GY-52)],
           "sniper_positions":  [(2000,GY-130),(3200,GY-200)],
           "heavy_positions":   [(2200,GY-62)],
           "kamikaze_positions":[2600,3600],
           "bomber_positions":  [2100,3200],
           "mortar_positions":  [(1400,GY-52),(3100,GY-52)],
           "mech_positions":    [(2400,GY-52)],
           "turret_positions":  [(1100,GY-14),(2900,GY-14)],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(300,GY-90,120,18),pygame.Rect(550,GY-160,100,18),
               pygame.Rect(800,GY-110,130,18),pygame.Rect(1300,GY-130,140,18),
               pygame.Rect(1800,GY-140,120,18),pygame.Rect(2300,GY-160,130,18),
               pygame.Rect(2850,GY-130,140,18),pygame.Rect(3100,GY-200,100,18)],
           "enemy_positions":[(600,GY-52),(950,GY-52),(1300,GY-52),(1650,GY-52),
               (2000,GY-52),(2350,GY-52),(2700,GY-52),(3050,GY-52),(1050,GY-222),(2600,GY-262)]},
 
        4:{"zone_num":4, "name":"ZONE 4: MILITAERBASIS",
           "sky":(12,12,28), "ground":(42,42,52),
           "enemy_hp":110, "enemy_speed":3.0, "enemy_shoot_rate":1000,
           "air_enemies":[("helicopter",1600),("helicopter",3200)], "powerup_count":5,
           "tank_positions":    [(2200,GY-52),(3400,GY-52)],
           "jetpack_positions": [(1400,GY-52),(2600,GY-52)],
           "shield_positions":  [(900,GY-52),(2000,GY-52),(3100,GY-52)],
           "sniper_positions":  [(1700,GY-260),(3300,GY-290)],
           "heavy_positions":   [(1500,GY-62),(3000,GY-62)],
           "kamikaze_positions":[1000,2200,3500],
           "stealth_positions": [(850,GY-52),(2100,GY-52),(3300,GY-52)],
           "bomber_positions":  [1200,2400,3600],
           "mortar_positions":  [(1100,GY-52),(2700,GY-52)],
           "mech_positions":    [(1800,GY-52),(3200,GY-52)],
           "turret_positions":  [(700,GY-14),(1900,GY-14),(3100,GY-14)],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(180,GY-120,100,18),pygame.Rect(520,GY-140,110,18),
               pygame.Rect(920,GY-180,130,18),pygame.Rect(1100,GY-260,100,18),
               pygame.Rect(1480,GY-110,150,18),pygame.Rect(1900,GY-240,90,18),
               pygame.Rect(2280,GY-220,100,18),pygame.Rect(2880,GY-290,120,18),
               pygame.Rect(3250,GY-130,150,18)],
           "enemy_positions":[(600,GY-52),(900,GY-52),(1200,GY-52),(1550,GY-52),
               (1800,GY-52),(2100,GY-52),(2400,GY-52),(2700,GY-52),(3000,GY-52),
               (1100,GY-282),(2880,GY-312)]},
 
        5:{"zone_num":5, "name":"ZONE 5: ARKTIS",
           "sky":(160,190,220), "ground":(200,220,240),
           "enemy_hp":130, "enemy_speed":3.2, "enemy_shoot_rate":900,
           "air_enemies":[("jet",2000),("jet",3500),("helicopter",1200)], "powerup_count":6,
           "tank_positions":    [(1600,GY-52),(2800,GY-52),(3800,GY-52)],
           "jetpack_positions": [(900,GY-52),(2200,GY-52),(3300,GY-52)],
           "shield_positions":  [(1100,GY-52),(2400,GY-52),(3600,GY-52)],
           "sniper_positions":  [(700,GY-220),(1850,GY-270),(3400,GY-250)],
           "heavy_positions":   [(1400,GY-62),(2900,GY-62)],
           "kamikaze_positions":[1300,2500,3700],
           "stealth_positions": [(750,GY-52),(2000,GY-52),(3200,GY-52),(3700,GY-52)],
           "bomber_positions":  [1100,2300,3500],
           "mortar_positions":  [(900,GY-52),(2200,GY-52),(3500,GY-52)],
           "mech_positions":    [(1500,GY-52),(3500,GY-52)],
           "turret_positions":  [(600,GY-14),(1800,GY-14),(3000,GY-14),(3800,GY-14)],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(220,GY-100,110,18),pygame.Rect(620,GY-130,120,18),
               pygame.Rect(860,GY-220,100,18),pygame.Rect(1350,GY-240,90,18),
               pygame.Rect(1850,GY-270,100,18),pygame.Rect(2350,GY-280,90,18),
               pygame.Rect(2850,GY-230,110,18),pygame.Rect(3400,GY-250,100,18)],
           "enemy_positions":[(700,GY-52),(1000,GY-52),(1350,GY-52),(1700,GY-52),
               (2050,GY-52),(2400,GY-52),(2750,GY-52),(3100,GY-52),(3450,GY-52),
               (860,GY-242),(2350,GY-302),(3400,GY-272)]},
 
        6:{"zone_num":6, "name":"ZONE 6: FESTUNG OMEGA",
           "sky":(8,5,18), "ground":(30,25,45),
           "enemy_hp":150, "enemy_speed":3.5, "enemy_shoot_rate":800,
           "air_enemies":[("jet",1800),("jet",3000),("helicopter",2400),("helicopter",3800)],
           "powerup_count":7,
           "tank_positions":    [(1200,GY-52),(2500,GY-52),(3700,GY-52)],
           "jetpack_positions": [(800,GY-52),(2000,GY-52),(3200,GY-52)],
           "shield_positions":  [(700,GY-52),(1500,GY-52),(2300,GY-52),(3400,GY-52)],
           "sniper_positions":  [(1000,GY-260),(2100,GY-300),(3460,GY-290)],
           "heavy_positions":   [(1300,GY-62),(2700,GY-62),(3900,GY-62)],
           "kamikaze_positions":[900,1700,2600,3500],
           "stealth_positions": [(650,GY-52),(1400,GY-52),(2300,GY-52),(3200,GY-52),(3700,GY-52)],
           "bomber_positions":  [800,1600,2500,3400],
           "mortar_positions":  [(700,GY-52),(1800,GY-52),(2900,GY-52),(3800,GY-52)],
           "mech_positions":    [(1000,GY-52),(2500,GY-52),(3800,GY-52)],
           "turret_positions":  [(500,GY-14),(1400,GY-14),(2200,GY-14),(3100,GY-14),(3900,GY-14)],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(200,GY-130,110,18),pygame.Rect(620,GY-160,120,18),
               pygame.Rect(880,GY-260,100,18),pygame.Rect(1380,GY-280,90,18),
               pygame.Rect(1900,GY-300,100,18),pygame.Rect(2420,GY-310,90,18),
               pygame.Rect(2940,GY-270,110,18),pygame.Rect(3460,GY-290,100,18),
               pygame.Rect(3720,GY-160,130,18)],
           "enemy_positions":[(600,GY-52),(950,GY-52),(1300,GY-52),(1650,GY-52),
               (2000,GY-52),(2350,GY-52),(2700,GY-52),(3050,GY-52),(3400,GY-52),(3800,GY-52),
               (880,GY-282),(1900,GY-322),(3460,GY-312)]},

        7:{"zone_num":7, "name":"ZONE 7: VULKANFRONT",
           "sky":(28,8,4), "ground":(100,35,10),
           "enemy_hp":175, "enemy_speed":3.8, "enemy_shoot_rate":750,
           "air_enemies":[("jet",1800),("jet",3200),("helicopter",2600),
                          ("helicopter",3800)],
           "powerup_count":8,
           "tank_positions":    [(1300,GY-52),(2600,GY-52),(3800,GY-52)],
           "jetpack_positions": [(900,GY-52),(2200,GY-52),(3400,GY-52)],
           "shield_positions":  [(800,GY-52),(1600,GY-52),(2400,GY-52),(3600,GY-52)],
           "sniper_positions":  [(1100,GY-260),(2300,GY-300),(3700,GY-290)],
           "heavy_positions":   [(1400,GY-62),(2700,GY-62),(3900,GY-62)],
           "kamikaze_positions":[1000,1900,2800,3700],
           "stealth_positions": [(700,GY-52),(1500,GY-52),(2400,GY-52),(3300,GY-52)],
           "bomber_positions":  [900,1700,2600,3500],
           "mortar_positions":  [(800,GY-52),(1900,GY-52),(3000,GY-52),(3900,GY-52)],
           "mech_positions":    [(1100,GY-52),(2600,GY-52),(4000,GY-52)],
           "turret_positions":  [(600,GY-14),(1500,GY-14),(2400,GY-14),(3200,GY-14),(4000,GY-14)],
           "sniper_mech_positions":   [(1200,GY-52),(2900,GY-52)],
           "riot_positions":          [(700,GY-52),(1800,GY-52),(3100,GY-52)],
           "flame_trooper_positions": [(1000,GY-52),(2200,GY-52),(3600,GY-52)],
           "bomber_jet_positions":    [1400,3000],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(250,GY-140,110,18),pygame.Rect(680,GY-180,120,18),
               pygame.Rect(1100,GY-260,100,18),pygame.Rect(1600,GY-300,90,18),
               pygame.Rect(2100,GY-320,100,18),pygame.Rect(2600,GY-280,90,18),
               pygame.Rect(3100,GY-300,110,18),pygame.Rect(3600,GY-270,100,18),
               pygame.Rect(4000,GY-180,130,18)],
           "enemy_positions":[(700,GY-52),(1050,GY-52),(1400,GY-52),(1750,GY-52),
               (2100,GY-52),(2450,GY-52),(2800,GY-52),(3150,GY-52),(3500,GY-52),(3850,GY-52),
               (1100,GY-282),(2100,GY-342),(3100,GY-322),(3600,GY-292)]},

        8:{"zone_num":8, "name":"ZONE 8: RAUMSTATION ALPHA",
           "sky":(2,2,10), "ground":(18,22,32),
           "enemy_hp":200, "enemy_speed":4.0, "enemy_shoot_rate":650,
           "air_enemies":[("jet",1600),("jet",2800),("jet",4000),
                          ("helicopter",2200),("helicopter",3600)],
           "powerup_count":9,
           "tank_positions":    [(1400,GY-52),(2800,GY-52),(4200,GY-52)],
           "jetpack_positions": [(800,GY-52),(2000,GY-52),(3200,GY-52),(4000,GY-52)],
           "shield_positions":  [(700,GY-52),(1500,GY-52),(2300,GY-52),(3200,GY-52),(4100,GY-52)],
           "sniper_positions":  [(1000,GY-280),(2200,GY-320),(3500,GY-300),(4100,GY-290)],
           "heavy_positions":   [(1300,GY-62),(2600,GY-62),(4000,GY-62)],
           "kamikaze_positions":[900,1700,2500,3300,4100],
           "stealth_positions": [(650,GY-52),(1400,GY-52),(2300,GY-52),(3200,GY-52),(4000,GY-52)],
           "bomber_positions":  [800,1600,2500,3400,4200],
           "mortar_positions":  [(700,GY-52),(1800,GY-52),(2900,GY-52),(3800,GY-52)],
           "mech_positions":    [(1000,GY-52),(2500,GY-52),(4000,GY-52)],
           "turret_positions":  [(500,GY-14),(1300,GY-14),(2100,GY-14),(3000,GY-14),(3800,GY-14),(4300,GY-14)],
           "sniper_mech_positions":   [(1100,GY-52),(2400,GY-52),(3700,GY-52)],
           "riot_positions":          [(800,GY-52),(1900,GY-52),(3100,GY-52),(4100,GY-52)],
           "flame_trooper_positions": [(900,GY-52),(2100,GY-52),(3300,GY-52)],
           "bomber_jet_positions":    [1200,2600,4000],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(220,GY-130,110,18),pygame.Rect(650,GY-170,120,18),
               pygame.Rect(1080,GY-260,110,18),pygame.Rect(1580,GY-310,100,18),
               pygame.Rect(2080,GY-330,110,18),pygame.Rect(2580,GY-290,100,18),
               pygame.Rect(3080,GY-320,110,18),pygame.Rect(3580,GY-280,100,18),
               pygame.Rect(4080,GY-200,140,18)],
           "enemy_positions":[(700,GY-52),(1050,GY-52),(1400,GY-52),(1750,GY-52),
               (2100,GY-52),(2450,GY-52),(2800,GY-52),(3150,GY-52),(3500,GY-52),
               (3850,GY-52),(4200,GY-52),
               (1080,GY-282),(2080,GY-352),(3080,GY-342),(3580,GY-302),(4080,GY-222)]},
    }
 
ZONES=make_zones()

def spawn_powerups(cfg):
    count=cfg.get("powerup_count",4);powerups=[]
    for i in range(count):
        x=random.randint(400,WORLD_WIDTH-400);y=GROUND_Y-50
        if random.random()<0.4 and len(cfg["platforms"])>1:
            plat=random.choice(cfg["platforms"][1:])
            x=plat.centerx+random.randint(-30,30);y=plat.top-12
        powerups.append(PowerUp(x,y))
    return powerups

# ═══════════════════════════════════════════════════
#  SPIELER
# ═══════════════════════════════════════════════════
class Player:
    W=32;H=56;BASE_SPEED=5;JUMP_FORCE=-16;GRAVITY=0.7
    MAX_FALL=18;MAX_LIVES=3;GRENADES=5

    def __init__(self,x,y):
        diff=get_diff()
        hp_perk = (20 if "hp_up_1" in PROGRESSION.unlocked_perks else 0) + \
                  (40 if "hp_up_2" in PROGRESSION.unlocked_perks else 0) + \
                  (60 if "hp_up_3" in PROGRESSION.unlocked_perks else 0)
        self.MAX_HP = (100 + diff["player_hp_bonus"] + hp_perk
                       + SKILLS.max_hp_bonus())
        self.x=float(x);self.y=float(y);self.vx=0.0;self.vy=0.0
        self.on_ground=False;self.was_on_ground=False;self.facing=1
        self.lives = self.MAX_LIVES + SKILLS.extra_lives();self.hp=self.MAX_HP
        bonus_g = 3 if "grenade_up" in PROGRESSION.unlocked_perks else 0
        self.GRENADES = self.GRENADES + bonus_g + (5 if SKILLS.has("grenade2") else 0)
        self.grenades = self.GRENADES;self.weapon=PISTOLE
        self.invincible=0;self.alive=True
        self.score=0;self.walk_frame=0;self.walk_timer=0;self.knife_anim=0
        self.shield_timer = 1800 if "shield_start" in PROGRESSION.unlocked_perks else 0
        self.speed_boost_timer = 0
        self.dmg_boost_timer   = 0
        self.pickup_msg        = ""
        self.pickup_msg_timer  = 0
        self.total_damage_taken= 0
        self.zone_damage_taken = 0
        self.knife_only_zone   = True
        self.air_kills         = 0
        self.stun_timer        = 0
        self.turrets           = []
        self.sandbags          = []
        self.rolling           = False
        self.roll_timer        = 0
        self.roll_cd           = 0
        self.ROLL_DURATION     = 14
        self.ROLL_CD_BASE      = int(55 * SKILLS.roll_cooldown_mult())
        self.roll_dir          = 1
        self.jumps_left        = 1
        self.wall_touching     = 0
        self.wall_jump_left    = 0
        self.grapple_active    = False
        self.grapple_x         = 0.0
        self.grapple_y         = 0.0
        self.grapple_cd        = 0
        self.GRAPPLE_CD        = 90
        self.GRAPPLE_LEN       = 220
        self.GRAPPLE_PULL      = 18.0
        self.regen_timer       = 0

        # Double / wall jump
        self.jumps_left     = 1
        self.wall_touching  = 0
        self.wall_jump_left = 0

        # Grappling hook (Right Mouse Button)
        self.grapple_active = False
        self.grapple_x      = 0.0
        self.grapple_y      = 0.0
        self.grapple_cd     = 0
        self.GRAPPLE_CD     = 90
        self.GRAPPLE_LEN    = 220
        self.GRAPPLE_PULL   = 18.0

        # HP regen ticker
        self.regen_timer    = 0

    @property
    def SPEED(self):
        return int(self.BASE_SPEED * SKILLS.speed_multiplier()
                   * (1.5 if self.speed_boost_timer > 0 else 1))
    @property
    def dmg_mult(self): return 2.0 if self.dmg_boost_timer>0 else 1.0

    def handle_input(self, keys, bullets, rockets, cam_x):
        if getattr(self, "stun_timer", 0) > 0:
            return

        # Horizontal movement
        if not self.rolling:
            self.vx = 0
            speed = int(self.BASE_SPEED * SKILLS.speed_multiplier()
                        * (1.5 if self.speed_boost_timer > 0 else 1))
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.vx = -speed; self.facing = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.vx =  speed; self.facing =  1

        # Grapple hook — Right Mouse Button
        mx, my = pygame.mouse.get_pos()
        tx, ty = mx + cam_x, my
        if pygame.mouse.get_pressed()[2] and not getattr(self, 'rolling', False):
            if self.grapple_cd <= 0 and not self.grapple_active:
                dist = math.hypot(tx - self.rect.centerx, ty - self.rect.centery)
                if dist <= self.GRAPPLE_LEN:
                    self.grapple_active = True
                    self.grapple_x = float(tx)
                    self.grapple_y = float(ty)
        else:
            self.grapple_active = False

        if self.grapple_active:
            dx = self.grapple_x - self.rect.centerx
            dy = self.grapple_y - self.rect.centery
            d  = math.hypot(dx, dy) or 1
            self.vx += dx / d * self.GRAPPLE_PULL * 0.55
            self.vy += dy / d * self.GRAPPLE_PULL * 0.55
            if d < 28:
                self.grapple_active = False
                self.grapple_cd = int(self.GRAPPLE_CD * SKILLS.grapple_cd_mult())

        # Jump / double jump / wall jump
        max_jumps = 2 if SKILLS.double_jump() else 1
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            if self.on_ground:
                self.vy = self.JUMP_FORCE
                self.jumps_left = max_jumps - 1
                self.wall_jump_left = SKILLS.wall_jump_count()
                SFX.play(SFX.jump)
            elif self.wall_touching != 0 and self.wall_jump_left > 0:
                self.vy = self.JUMP_FORCE * 0.90
                self.vx = -self.wall_touching * int(self.BASE_SPEED * 1.8)
                self.wall_jump_left -= 1
                self.wall_touching   = 0
                SFX.play(SFX.jump)
                PARTICLES.spawn_dust(self.rect.centerx, self.rect.centery)
            elif self.jumps_left > 0 and not self.on_ground:
                self.vy = self.JUMP_FORCE * 0.85
                self.jumps_left -= 1
                SFX.play(SFX.jump)
                PARTICLES.spawn_sparks(self.rect.centerx, self.rect.bottom, 8)

        # Dodge roll — LSHIFT
        if keys[pygame.K_LSHIFT] and not self.rolling and self.roll_cd <= 0 and self.on_ground:
            self.rolling    = True
            self.roll_timer = self.ROLL_DURATION
            self.roll_dir   = self.facing
            self.invincible = int(self.ROLL_DURATION * (1000 // 60))
            PARTICLES.spawn_dust(self.rect.centerx, self.rect.bottom)
            SFX.play(SFX.jump)

        # Shooting
        if self.weapon.auto and pygame.mouse.get_pressed()[0]:
            self._fire(bullets, rockets, cam_x)

    def shoot(self,bullets,rockets,cam_x):
        if not self.weapon.auto: self._fire(bullets,rockets,cam_x)

    def _fire(self,bullets,rockets,cam_x):
        mx,my=pygame.mouse.get_pos();tx=mx+cam_x;ty=my
        ox=self.rect.centerx;oy=self.rect.centery
        self.facing=1 if tx>ox else -1
        results=self.weapon.shoot_toward(ox,oy,tx,ty,self.facing,self.dmg_mult)
        LIGHTS.add(ox, oy, 55, ORANGE, 0.8, life=4)
        for r in results:
            if isinstance(r,Bullet): bullets.append(r)
            elif isinstance(r,Rocket): rockets.append(r)
            elif isinstance(r,tuple) and r[0]=="melee": self.knife_anim=15
        # Nur Messer = knife_only achievement möglich
        if self.weapon!=MESSER and results:
            self.knife_only_zone=False

    def get_knife_hit_rect(self):
        return pygame.Rect(self.rect.centerx+self.facing*5,self.rect.centery-10,50,30)

    def throw_grenade(self,grenades):
        if self.grenades>0:
            grenades.append(Grenade(self.rect.centerx,self.rect.top,self.facing))
            self.grenades-=1;SFX.play(SFX.grenade_throw)
            self.knife_only_zone=False

    def update(self):
        global screen_shake

        # HP regen perk
        if SKILLS.regen_active() and self.hp <= self.MAX_HP * 0.30:
            self.regen_timer += 1
            if self.regen_timer >= 60:
                self.regen_timer = 0
                self.hp = min(self.MAX_HP, self.hp + 1)

        # Dodge roll
        if self.rolling:
            self.roll_timer -= 1
            self.vx = self.roll_dir * int(self.BASE_SPEED * 2.5)
            if self.roll_timer <= 0:
                self.rolling = False
                self.roll_cd = int(self.ROLL_CD_BASE * SKILLS.roll_cooldown_mult())
        if self.roll_cd > 0:
            self.roll_cd -= 1
        if self.grapple_cd > 0:
            self.grapple_cd -= 1

        self.was_on_ground = self.on_ground
        self.vy = min(self.vy + self.GRAVITY, self.MAX_FALL)
        self.on_ground     = False
        self.wall_touching = 0
        self.y += self.vy

        for plat in current_platforms:
            pr = self.rect
            if pr.colliderect(plat):
                if self.vy > 0 and pr.bottom - self.vy <= plat.top + abs(self.vy) + 2:
                    self.y = plat.top - self.H; self.vy = 0; self.on_ground = True
                elif self.vy < 0 and pr.top - self.vy >= plat.bottom - abs(self.vy) - 2:
                    self.y = plat.bottom; self.vy = 1
                # Wall detection
                elif pr.right > plat.left and pr.left < plat.left and abs(pr.right - plat.left) < 12:
                    self.wall_touching =  1
                elif pr.left < plat.right and pr.right > plat.right and abs(pr.left - plat.right) < 12:
                    self.wall_touching = -1

        self.x += self.vx
        self.x  = max(0, min(WORLD_WIDTH - self.W, self.x))

        if self.on_ground and not self.was_on_ground:
            PARTICLES.spawn_dust(self.x + self.W // 2, self.y + self.H)
            self.jumps_left     = 2 if SKILLS.double_jump() else 1
            self.wall_jump_left = SKILLS.wall_jump_count()

        if self.vx != 0 and not self.rolling:
            self.walk_timer += 1
            if self.walk_timer > 8:
                self.walk_frame = (self.walk_frame + 1) % 4
                self.walk_timer = 0

        if self.invincible > 0:      self.invincible = max(0, self.invincible - clock.get_time())
        if self.knife_anim > 0:      self.knife_anim -= 1
        if self.shield_timer > 0:    self.shield_timer -= 1
        if self.speed_boost_timer>0: self.speed_boost_timer -= 1
        if self.dmg_boost_timer > 0: self.dmg_boost_timer -= 1
        if self.pickup_msg_timer > 0:self.pickup_msg_timer -= 1
        if hasattr(self,"stun_timer") and self.stun_timer > 0: self.stun_timer -= 1

    def take_damage(self, amount):
        global screen_shake
        if self.invincible > 0: return
        if self.rolling: return          # i-frames during roll
        if self.shield_timer > 0:
            SFX.play(SFX.shield_hit)
            PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 8)
            screen_shake = 4; return
        armor = SKILLS.armor_reduction()
        dmg   = int(amount * get_diff()["enemy_dmg_mult"] * (1.0 - armor))
        self.hp -= dmg
        self.zone_damage_taken += dmg
        self.total_damage_taken += dmg
        SFX.play(SFX.hit_player)
        PARTICLES.spawn_blood(self.rect.centerx, self.rect.centery, 8)
        screen_shake = 8
        if self.hp <= 0:
            self.hp = 0; self.lives -= 1
            if self.lives > 0: self.hp = self.MAX_HP; self.invincible = 2000
            else: self.alive = False

    def collect_powerup(self,pu):
        msg=pu.apply(self);self.pickup_msg=msg;self.pickup_msg_timer=150

    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)

    def draw(self, surf, cam_x=0):
        sx = int(self.x) - cam_x
        cx = sx + self.W // 2
        cy = int(self.y)
        f  = self.facing
        t  = pygame.time.get_ticks()

        if self.invincible > 0 and (t // 80) % 2 == 0:
            return

        skin = SKINS[current_skin]
        bc   = skin["body"]
        hc   = skin["head"]
        helm = skin["helmet"]
        vest = skin["vest"]
        boot = skin.get("boot", (22, 18, 12))
        glove= skin.get("glove", (40, 32, 22))

        # ── Shield / boost auras ──────────────────────────────────────────────
        if self.shield_timer > 0:
            pulse = abs(math.sin(t * 0.005)) * 30
            sa = pygame.Surface((88, 88), pygame.SRCALPHA)
            pygame.draw.circle(sa, (80, 160, 255, int(35 + pulse)), (44, 44), 42)
            pygame.draw.circle(sa, (140, 200, 255, int(60 + pulse)), (44, 44), 42, 2)
            surf.blit(sa, (cx - 44, cy + 4))
        if self.dmg_boost_timer > 0:
            sa2 = pygame.Surface((74, 74), pygame.SRCALPHA)
            pulse2 = abs(math.sin(t * 0.008)) * 25
            pygame.draw.circle(sa2, (255, 110, 20, int(30 + pulse2)), (37, 37), 35)
            surf.blit(sa2, (cx - 37, cy + 8))

        # ── Ground shadow ──────────────────────────────────────────────────────
        sh = pygame.Surface((self.W + 10, 7), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 70), (0, 0, self.W + 10, 7))
        surf.blit(sh, (cx - self.W // 2 - 5, cy + self.H - 3))

        # ── Walk offsets ──────────────────────────────────────────────────────
        lo = [0, 7, 0, -7][self.walk_frame] if self.vx != 0 else 0

        # ── BOOTS ─────────────────────────────────────────────────────────────
        # Left boot
        pygame.draw.rect(surf, boot, (cx - 11, cy + 45 + lo, 12, 10), border_radius=2)
        pygame.draw.rect(surf, (max(0,boot[0]-10), max(0,boot[1]-10), max(0,boot[2]-10)),
                         (cx - 13, cy + 52 + lo, 15, 4), border_radius=2)
        # Right boot
        pygame.draw.rect(surf, boot, (cx + 1, cy + 45 - lo, 12, 10), border_radius=2)
        pygame.draw.rect(surf, (max(0,boot[0]-10), max(0,boot[1]-10), max(0,boot[2]-10)),
                         (cx - 1, cy + 52 - lo, 15, 4), border_radius=2)

        # ── LEGS / TROUSERS ────────────────────────────────────────────────────
        trouser = bc
        trouser_hi = (min(255,bc[0]+20), min(255,bc[1]+20), min(255,bc[2]+20))
        # Left leg
        pygame.draw.rect(surf, trouser, (cx - 10, cy + 30, 10, 16 + lo), border_radius=2)
        pygame.draw.rect(surf, trouser_hi, (cx - 10, cy + 30, 4, 16 + lo))
        # Right leg
        pygame.draw.rect(surf, trouser, (cx + 1, cy + 30, 10, 16 - lo), border_radius=2)
        pygame.draw.rect(surf, trouser_hi, (cx + 1, cy + 30, 4, 16 - lo))
        # Belt
        pygame.draw.rect(surf, (30, 24, 14), (cx - 11, cy + 29, 22, 5))
        pygame.draw.rect(surf, (55, 44, 28), (cx - 2, cy + 30, 4, 4))  # buckle

        # ── BODY ARMOUR / PLATE CARRIER ───────────────────────────────────────
        vest_dark = (max(0,vest[0]-18), max(0,vest[1]-18), max(0,vest[2]-18))
        vest_hi   = (min(255,vest[0]+22), min(255,vest[1]+22), min(255,vest[2]+22))
        # Main torso
        pygame.draw.rect(surf, vest, (cx - 12, cy + 14, 24, 18), border_radius=3)
        pygame.draw.rect(surf, vest_hi, (cx - 12, cy + 14, 24, 5), border_radius=3)
        pygame.draw.rect(surf, vest_dark, (cx - 12, cy + 28, 24, 4))
        # Front plate (SAPI plate texture)
        pygame.draw.rect(surf, vest_dark, (cx - 8, cy + 16, 16, 14), border_radius=2)
        pygame.draw.rect(surf, vest_hi,   (cx - 8, cy + 16, 16,  3), border_radius=2)
        # Molle webbing lines on vest
        for row_y in range(cy + 19, cy + 30, 4):
            pygame.draw.line(surf, vest_dark, (cx - 7, row_y), (cx + 7, row_y), 1)
        # Shoulder pads
        pygame.draw.rect(surf, vest, (cx - 14, cy + 14, 5, 10), border_radius=2)
        pygame.draw.rect(surf, vest, (cx + 9,  cy + 14, 5, 10), border_radius=2)
        # Collar / neck guard
        pygame.draw.rect(surf, vest_dark, (cx - 5, cy + 11, 10, 5), border_radius=1)
        # Side pouches (admin pouch)
        pygame.draw.rect(surf, vest_dark, (cx - 16, cy + 17, 5, 8), border_radius=1)
        pygame.draw.rect(surf, vest_dark, (cx + 11, cy + 17, 5, 8), border_radius=1)
        # Mag pouches
        for px3 in (cx - 10, cx - 5, cx + 1, cx + 6):
            pygame.draw.rect(surf, vest_dark, (px3, cy + 26, 4, 6), border_radius=1)
            pygame.draw.rect(surf, vest_hi,   (px3, cy + 26, 4, 2))

        # ── NECK ─────────────────────────────────────────────────────────────
        pygame.draw.rect(surf, hc, (cx - 3, cy + 9, 6, 6))

        # ── HEAD ──────────────────────────────────────────────────────────────
        # Face base
        pygame.draw.circle(surf, hc, (cx, cy + 6), 10)
        # Cheek shadow
        pygame.draw.circle(surf, (max(0,hc[0]-20), max(0,hc[1]-20), max(0,hc[2]-20)),
                           (cx + f * 3, cy + 7), 5)
        # Ear
        pygame.draw.ellipse(surf, hc, (cx - f * 11, cy + 3, 5, 7))
        # Balaclava / face wrap if shadow skin
        if current_skin == "shadow":
            pygame.draw.rect(surf, (18, 18, 24), (cx - 9, cy + 3, 18, 8))
            pygame.draw.circle(surf, (18, 18, 24), (cx, cy + 6), 7)
        # Eye socket
        eye_x = cx + f * 4
        pygame.draw.circle(surf, (20, 15, 10), (eye_x, cy + 4), 2)
        # Eye whites
        pygame.draw.circle(surf, (230, 225, 215), (eye_x, cy + 4), 2)
        pygame.draw.circle(surf, (25, 20, 15), (eye_x, cy + 4), 1)
        # Nose
        pygame.draw.line(surf, (max(0,hc[0]-30), max(0,hc[1]-30), max(0,hc[2]-30)),
                         (cx + f * 2, cy + 7), (cx + f * 3, cy + 9), 1)

        # ── HELMET ────────────────────────────────────────────────────────────
        helm_hi   = (min(255,helm[0]+24), min(255,helm[1]+24), min(255,helm[2]+24))
        helm_dark = (max(0,helm[0]-20),   max(0,helm[1]-20),   max(0,helm[2]-20))
        # Helmet dome (ACH / MICH style)
        pygame.draw.arc(surf, helm,
                        pygame.Rect(cx - 13, cy - 4, 26, 20), 0, math.pi, 0)
        pygame.draw.rect(surf, helm, (cx - 13, cy + 4, 26, 8))
        # Dome highlight
        pygame.draw.arc(surf, helm_hi,
                        pygame.Rect(cx - 10, cy - 2, 14, 12), 0.3, math.pi - 0.3, 3)
        # Brim
        pygame.draw.rect(surf, helm_dark, (cx - 14, cy + 10, 28, 3), border_radius=1)
        # NVG mount stub (left front)
        pygame.draw.rect(surf, (35, 35, 42), (cx - f * 8, cy - 2, 4, 5))
        # Suspension pads bump
        pygame.draw.ellipse(surf, helm_dark, (cx - 12, cy + 4, 6, 5))
        pygame.draw.ellipse(surf, helm_dark, (cx + 6,  cy + 4, 6, 5))
        # Camo spots (seeded to position so they don't flicker)
        camo_rng = random.Random(int(self.x) // 20)
        for _ in range(5):
            csx2 = cx + camo_rng.randint(-9, 9)
            csy2 = cy + camo_rng.randint(-2, 9)
            pygame.draw.circle(surf, helm_dark, (csx2, csy2), camo_rng.randint(1, 3))
        # Chin strap
        pygame.draw.line(surf, helm_dark, (cx - 13, cy + 10),
                         (cx - 6, cy + 13), 2)
        pygame.draw.line(surf, helm_dark, (cx + 13, cy + 10),
                         (cx + 6, cy + 13), 2)

        # ── ARMS ──────────────────────────────────────────────────────────────
        arm_col = vest
        # Back arm
        pygame.draw.line(surf, arm_col,
                         (cx - f * 10, cy + 16),
                         (cx - f * 18, cy + 28), 5)
        pygame.draw.circle(surf, glove, (cx - f * 18, cy + 28), 4)
        # Front / gun arm
        gun_y_offset = cy + 22 + int(math.sin(t * 0.004) * 1.5)
        pygame.draw.line(surf, arm_col,
                         (cx + f * 10, cy + 16),
                         (cx + f * 20, gun_y_offset), 5)
        pygame.draw.circle(surf, glove, (cx + f * 20, gun_y_offset), 4)

        # ── WEAPON RENDERING ──────────────────────────────────────────────────
        wx = cx + f * 14
        wy = cy + 21

        if self.weapon == PISTOLE:
            pygame.draw.rect(surf, (62,62,62), (wx-2, wy-3, 16, 8))
            pygame.draw.rect(surf, (85,85,85), (wx-2, wy-3, 16, 3))
            pygame.draw.rect(surf, (48,48,48), (wx+8*f, wy-5, f*10, 3))
            pygame.draw.rect(surf, (38,28,18), (wx-2, wy+5, 7, 9))
            pygame.draw.rect(surf, (58,42,26), (wx-1, wy+6, 5, 7))
            pygame.draw.rect(surf, (52,52,52), (wx+4, wy+3, 4, 5))
            pygame.draw.rect(surf, (195,175,45), (wx+12*f, wy-6, 2, 2))

        elif self.weapon == STURMGEWEHR:
            pygame.draw.rect(surf, (42,42,42), (wx-4, wy-4, 26, 9))
            pygame.draw.rect(surf, (65,65,65), (wx-4, wy-4, 26, 3))
            pygame.draw.rect(surf, (52,52,52), (wx+18*f, wy-3, f*12, 5))
            pygame.draw.rect(surf, (75,75,75), (wx+28*f, wy-4, f*4, 7))
            pygame.draw.rect(surf, (32,22,12), (wx-14*f, wy-3, f*(-10), 8))
            pygame.draw.rect(surf, (58,58,58), (wx+4, wy+5, 8, 11))
            pygame.draw.rect(surf, (32,32,32), (wx, wy-7, 14, 3))
            pygame.draw.rect(surf, (38,28,16), (wx-2, wy+5, 6, 9))

        elif self.weapon == SCHARFSCHUETZE:
            pygame.draw.rect(surf, (38,52,38), (wx-2, wy-2, f*36, 5))
            pygame.draw.rect(surf, (58,76,58), (wx-2, wy-2, f*36, 2))
            pygame.draw.rect(surf, (52,66,52), (wx+30*f, wy-4, f*8, 9))
            pygame.draw.rect(surf, (32,46,32), (wx-6, wy-5, 16, 12))
            pygame.draw.rect(surf, (105,62,22), (wx-18*f, wy-3, f*(-14), 8))
            pygame.draw.rect(surf, (28,28,28), (wx+2, wy-11, 16, 6))
            pygame.draw.circle(surf, (55,155,215), (wx+3, wy-8), 3)
            pygame.draw.circle(surf, (75,195,250), (wx+3, wy-8), 1)
            pygame.draw.circle(surf, (55,155,215), (wx+16, wy-8), 3)
            pygame.draw.circle(surf, (75,195,250), (wx+16, wy-8), 1)
            if self.on_ground:
                pygame.draw.line(surf, (48,62,48), (wx+24*f, wy+3), (wx+20*f, wy+12), 2)
                pygame.draw.line(surf, (48,62,48), (wx+28*f, wy+3), (wx+32*f, wy+12), 2)

        elif self.weapon == SCHROTFLINTE:
            pygame.draw.rect(surf, (68,48,22), (wx, wy-5, f*24, 5))
            pygame.draw.rect(surf, (68,48,22), (wx, wy+1, f*24, 5))
            pygame.draw.rect(surf, (125,72,32), (wx-10*f, wy-6, 14, 13))
            pygame.draw.rect(surf, (48,32,12), (wx+22*f, wy-6, f*3, 5))
            pygame.draw.rect(surf, (48,32,12), (wx+22*f, wy, f*3, 5))
            pygame.draw.rect(surf, (88,52,18), (wx-4, wy+5, 5, 5))

        elif self.weapon == RAKETENWERFER:
            pygame.draw.rect(surf, (52,72,52), (wx-8*f, wy-6, f*40, 13))
            pygame.draw.rect(surf, (72,96,72), (wx-8*f, wy-6, f*40, 4))
            pygame.draw.circle(surf, (18,18,18), (wx-8*f, wy), 6)
            pygame.draw.rect(surf, (38,52,38), (wx+4, wy+7, 7, 10))
            pygame.draw.rect(surf, ROCKET_COL, (wx+28*f, wy-4, f*12, 9))
            pygame.draw.polygon(surf, (255,148,38),
                                [(wx+f*40, wy), (wx+f*34, wy-4), (wx+f*34, wy+4)])

        elif self.weapon == STINGER:
            pygame.draw.rect(surf, (28,82,92), (wx-10*f, wy-5, f*44, 11))
            pygame.draw.rect(surf, (48,118,132), (wx-10*f, wy-5, f*44, 4))
            pygame.draw.circle(surf, CYAN, (wx+32*f, wy), 7)
            pygame.draw.circle(surf, (148,252,252), (wx+32*f, wy), 4)
            pygame.draw.circle(surf, WHITE, (wx+32*f, wy), 2)

        elif self.weapon == MESSER and self.knife_anim == 0:
            pygame.draw.polygon(surf, (195,205,225),
                                [(cx+f*12, cy+28), (cx+f*28, cy+24), (cx+f*12, cy+22)])
            pygame.draw.rect(surf, (98,98,108), (cx+f*8, cy+21, f*5, 10))
            pygame.draw.rect(surf, (88,52,18), (cx+f*0, cy+23, f*9, 7))

        elif self.weapon == FLAMMENWERFER:
            pygame.draw.ellipse(surf, (88,52,18), (wx-22*f, wy-8, 14, 18))
            pygame.draw.ellipse(surf, (75,42,12), (wx-14*f, wy-8, 14, 18))
            pygame.draw.line(surf, (48,48,48), (wx-4*f, wy), (wx+8*f, wy), 4)
            pygame.draw.rect(surf, (52,52,52), (wx+6*f, wy-5, f*16, 10))
            pygame.draw.rect(surf, (38,38,38), (wx+20*f, wy-3, f*5, 6))
            for fi in range(5):
                fangle = math.radians(-25 + fi * 12 + math.sin(t * 0.02 + fi) * 8)
                flen2  = 8 + fi * 3
                fx2    = int(wx + f * (25 + math.cos(fangle) * flen2))
                fy2    = int(wy + math.sin(fangle) * flen2)
                fc     = [(255,235,55),(255,175,18),(255,95,8),(255,215,75),(255,135,12)][fi]
                pygame.draw.circle(surf, fc, (fx2, fy2), max(1, 5 - fi // 2))

        elif self.weapon == EMP_CANNON:
            pygame.draw.rect(surf, (32,68,88), (wx-6*f, wy-5, f*30, 11))
            pygame.draw.rect(surf, (52,102,128), (wx-6*f, wy-5, f*30, 4))
            for ci in range(4):
                coil_x = wx + f * (2 + ci * 6)
                pygame.draw.circle(surf, EMP_COL, (coil_x, wy), 4, 1)
            pygame.draw.circle(surf, (42,168,178), (wx+22*f, wy), 7)
            pygame.draw.circle(surf, (118,228,238), (wx+22*f, wy), 4)
            pygame.draw.circle(surf, WHITE, (wx+22*f, wy), 2)

        # Weapon level badge
        wlv = WSTATS.get_level(self.weapon.name)
        if wlv > 0:
            lf2 = pygame.font.SysFont("consolas", 9, bold=True)
            lb2 = lf2.render(f"LV{wlv}", True, YELLOW)
            surf.blit(lb2, (cx + f * 10, cy + 16))

        # ── HP BAR ────────────────────────────────────────────────────────────
        bw = 50; bx2 = cx - bw // 2; by2 = cy - 14
        pygame.draw.rect(surf, (8, 8, 12), (bx2 - 1, by2 - 1, bw + 2, 8), border_radius=3)
        pygame.draw.rect(surf, DARK, (bx2, by2, bw, 6), border_radius=3)
        hpcolor = GREEN if self.hp > 50 else YELLOW if self.hp > 25 else RED
        hpw = int(bw * self.hp / self.MAX_HP)
        if hpw > 0:
            pygame.draw.rect(surf, hpcolor, (bx2, by2, hpw, 6), border_radius=3)
            shine3 = pygame.Surface((hpw, 2), pygame.SRCALPHA)
            shine3.fill((255, 255, 255, 55))
            surf.blit(shine3, (bx2, by2))
        pygame.draw.rect(surf, (55, 55, 70), (bx2, by2, bw, 6), 1, border_radius=3)

    def draw_grapple(self, surf, cam_x=0):
        if not self.grapple_active: return
        px = self.rect.centerx - cam_x
        py = self.rect.centery
        gx = int(self.grapple_x) - cam_x
        gy = int(self.grapple_y)
        for i in range(12):
            t = i / 11
            rx = int(px + (gx-px)*t)
            ry = int(py + (gy-py)*t + math.sin(t*math.pi)*6)
            pygame.draw.circle(surf, (160,140,80), (rx,ry), 1)
        pygame.draw.circle(surf, (220,200,100), (gx,gy), 5)
        pygame.draw.circle(surf, WHITE, (gx,gy), 2)

        

# ═══════════════════════════════════════════════════
#  FEIND
# ═══════════════════════════════════════════════════
class Enemy:
    W=30;H=52;is_air=False
    ST_PATROL="patrol";ST_CHASE="chase";ST_SHOOT="shoot";ST_FLANK="flank"
    def __init__(self,x,y,hp=50,speed=2.2,shoot_rate=1700):
        diff=get_diff()
        self.x=float(x);self.y=float(y);self.vy=0.0
        self.max_hp=int(hp*diff["enemy_hp_mult"]);self.hp=self.max_hp;self.alive=True
        self.last_shot=0;self.facing=-1
        self.speed=speed*diff["enemy_speed_mult"]
        self.shoot_rate=int(shoot_rate*diff["shoot_rate_mult"])
        self.walk_frame=0;self.walk_timer=0;self.on_ground=False
        self.state=self.ST_PATROL;self.state_timer=0
        self.patrol_dir=-1;self.patrol_timer=0;self.flank_target=0.0
        self.grenade_cd=random.randint(6000,12000);self.last_grenade=-99999
        self.jump_cooldown=0;self.stuck_timer=0;self.last_x=float(x)
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    def _dist(self,player): return math.hypot(player.x-self.x,player.y-self.y)
    def _try_jump(self,target_x):
        if not self.on_ground or self.jump_cooldown>0: return
        dx=target_x-self.x
        for plat in current_platforms:
            if plat.height>60: continue
            in_dir=((dx>0 and plat.left>self.x and plat.left<self.x+250) or
                    (dx<0 and plat.right<self.x+self.W and plat.right>self.x-250))
            if in_dir and plat.top<self.y-30:
                self.vy=-15.0;self.jump_cooldown=30;return
        if self.stuck_timer>25 and self.on_ground:
            self.vy=-14.0;self.jump_cooldown=35;self.stuck_timer=0
    def _move_toward(self,tx,sp=None):
        sp=sp or self.speed;dx=tx-self.x
        if abs(dx)>4:
            self.x+=sp*(1 if dx>0 else -1);self.facing=1 if dx>0 else -1
            self.walk_timer+=1
            if self.walk_timer>8: self.walk_frame=(self.walk_frame+1)%4;self.walk_timer=0
    def _shoot_at(self,player,bullets):
        now=pygame.time.get_ticks()
        if now-self.last_shot<self.shoot_rate: return
        self.last_shot=now
        ox=self.rect.centerx;oy=self.rect.centery
        tx=player.rect.centerx+player.vx*4;ty=player.rect.centery
        self.facing=1 if tx>ox else -1
        angle=math.atan2(ty-oy,tx-ox)+random.uniform(-0.14,0.14)
        dmg=int(10*get_diff()["enemy_dmg_mult"])
        bullets.append(Bullet(ox,oy,math.cos(angle)*11,math.sin(angle)*11,dmg,RED))
        SFX.play(SFX.shoot_pistol)
    def update(self,player,bullets,grenades_list):
        self.vy=min(self.vy+0.7,18);self.y+=self.vy;self.on_ground=False
        for plat in current_platforms:
            r=self.rect
            if r.colliderect(plat) and self.vy>=0:
                if r.bottom-self.vy<=plat.top+abs(self.vy)+2:
                    self.y=plat.top-self.H;self.vy=0;self.on_ground=True
        if self.jump_cooldown>0: self.jump_cooldown-=1
        if abs(self.x-self.last_x)<0.3 and self.on_ground: self.stuck_timer+=1
        else: self.stuck_timer=max(0,self.stuck_timer-2)
        self.last_x=self.x
        dist=self._dist(player);now=pygame.time.get_ticks()
        hp_low=self.hp<self.max_hp*0.35
        if dist<380 and now-self.last_grenade>self.grenade_cd and random.random()<GRENADE_THROW_CHANCE:
            self.last_grenade=now
            grenades_list.append(Grenade(self.rect.centerx,self.rect.top,self.facing))
            SFX.play(SFX.grenade_throw)
        self.state_timer+=1
        if dist>650: self.state=self.ST_PATROL
        elif hp_low and self.state!=self.ST_SHOOT: self.state=self.ST_SHOOT
        elif self.state==self.ST_PATROL and dist<650:
            self.state=self.ST_CHASE if dist>230 else self.ST_SHOOT
        elif self.state==self.ST_CHASE and dist<230:
            self.state=random.choice([self.ST_FLANK,self.ST_SHOOT])
        elif self.state==self.ST_FLANK and (dist<150 or self.state_timer>130):
            self.state=self.ST_SHOOT;self.state_timer=0
        elif self.state==self.ST_SHOOT and self.state_timer>180:
            self.state=random.choice([self.ST_FLANK,self.ST_CHASE]);self.state_timer=0
        if self.state==self.ST_PATROL:
            self.patrol_timer+=1
            if self.patrol_timer>90: self.patrol_dir*=-1;self.patrol_timer=0
            tx=self.x+self.patrol_dir*60;self._move_toward(tx,self.speed*0.6);self._try_jump(tx)
        elif self.state==self.ST_CHASE:
            self._move_toward(player.x,self.speed);self._try_jump(player.x)
        elif self.state==self.ST_FLANK:
            if self.state_timer==1: self.flank_target=player.x+random.choice([-280,-200,200,280])
            self._move_toward(self.flank_target,self.speed*1.2)
            self._try_jump(self.flank_target);self._shoot_at(player,bullets)
        elif self.state==self.ST_SHOOT:
            self._shoot_at(player,bullets)
            if dist<120: self._move_toward(self.x-self.facing*50,self.speed*0.8)
        self.x=max(0,min(WORLD_WIDTH-self.W,self.x))
    def take_damage(self, amount):
        self.hp -= amount
        SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_blood(self.rect.centerx, self.rect.centery)
        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_death_explosion(self.rect.centerx, self.rect.centery)
    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        cx2 = sx + self.W // 2
        cy2 = int(self.y)
        f   = self.facing
        t   = pygame.time.get_ticks()

        # ── Shadow ────────────────────────────────────────────────────────────
        sh = pygame.Surface((self.W+6, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,55), (0,0,self.W+6,6))
        surf.blit(sh, (cx2-self.W//2-3, cy2+self.H-2))

        # ── Walk animation ────────────────────────────────────────────────────
        lo = [0, 7, 0, -7][self.walk_frame]

        # ── Boots ─────────────────────────────────────────────────────────────
        boot_col = (28, 22, 14)
        pygame.draw.rect(surf, boot_col, (cx2-8, cy2+46+lo, 10, 8), border_radius=2)
        pygame.draw.rect(surf, boot_col, (cx2+1, cy2+46-lo, 10, 8), border_radius=2)
        # Boot sole (slightly lighter)
        pygame.draw.rect(surf, (40,32,20), (cx2-9, cy2+52+lo, 12, 3), border_radius=1)
        pygame.draw.rect(surf, (40,32,20), (cx2+0, cy2+52-lo, 12, 3), border_radius=1)

        # ── Legs / trousers ───────────────────────────────────────────────────
        trouser_col  = (80, 55, 40)
        trouser_hi   = (100, 70, 52)
        pygame.draw.rect(surf, trouser_col,  (cx2-7, cy2+34,  7, 14+lo), border_radius=2)
        pygame.draw.rect(surf, trouser_col,  (cx2+1, cy2+34,  7, 14-lo), border_radius=2)
        pygame.draw.rect(surf, trouser_hi,   (cx2-7, cy2+34,  3, 14+lo))
        pygame.draw.rect(surf, trouser_hi,   (cx2+1, cy2+34,  3, 14-lo))

        # ── Body armour / uniform ─────────────────────────────────────────────
        vest_col  = (78, 58, 40)
        vest_hi   = (100, 76, 54)
        vest_shad = (55, 40, 28)
        pygame.draw.rect(surf, vest_col,  (cx2-10, cy2+18, 20, 20), border_radius=3)
        pygame.draw.rect(surf, vest_hi,   (cx2-10, cy2+18, 20,  5), border_radius=3)
        pygame.draw.rect(surf, vest_shad, (cx2-10, cy2+34, 20,  4))
        # Chest rig / pouches
        pygame.draw.rect(surf, (62,46,32), (cx2-8,  cy2+21,  6, 8), border_radius=1)
        pygame.draw.rect(surf, (62,46,32), (cx2+2,  cy2+21,  6, 8), border_radius=1)
        pygame.draw.rect(surf, (75,56,38), (cx2-7,  cy2+22,  4, 6))
        pygame.draw.rect(surf, (75,56,38), (cx2+3,  cy2+22,  4, 6))
        # Shoulder pad
        pygame.draw.rect(surf, vest_hi,   (cx2-11, cy2+18,  4, 8), border_radius=2)
        pygame.draw.rect(surf, vest_hi,   (cx2+7,  cy2+18,  4, 8), border_radius=2)

        # ── Neck ─────────────────────────────────────────────────────────────
        pygame.draw.rect(surf, (160,115,80), (cx2-3, cy2+14, 6, 6))

        # ── Head ──────────────────────────────────────────────────────────────
        skin_col = (175, 128, 88)
        skin_shad= (140, 100, 68)
        pygame.draw.circle(surf, skin_col,  (cx2, cy2+10), 9)
        pygame.draw.circle(surf, skin_shad, (cx2+2*f, cy2+11), 5)  # cheek shadow
        # Ear
        pygame.draw.ellipse(surf, skin_col, (cx2 - f*10, cy2+7, 5, 7))
        # Eye
        eye_x = cx2 + f*4
        pygame.draw.circle(surf, (30,22,14), (eye_x, cy2+9), 2)
        # Mouth (slight grimace)
        pygame.draw.line(surf, (120,80,55), (eye_x-3, cy2+13), (eye_x+1, cy2+14), 1)

        # ── Combat helmet ─────────────────────────────────────────────────────
        helm_col  = (52, 66, 44)
        helm_hi   = (68, 86, 56)
        helm_shad = (36, 46, 30)
        # Helmet dome
        pygame.draw.arc(surf, helm_col,
                        pygame.Rect(cx2-12, cy2-2, 24, 20), 0, math.pi, 10)
        pygame.draw.rect(surf, helm_col,  (cx2-12, cy2+6, 24, 8))
        pygame.draw.rect(surf, helm_hi,   (cx2-12, cy2+6, 24, 3))
        pygame.draw.rect(surf, helm_shad, (cx2-12, cy2+12,24, 2))
        # Brim
        pygame.draw.rect(surf, helm_shad, (cx2-13, cy2+12, 26, 3), border_radius=1)
        # Camo spots
        camo_rng = random.Random(int(self.x)//50)
        for _ in range(4):
            csx = cx2 + camo_rng.randint(-9, 9)
            csy = cy2 + camo_rng.randint(0, 8)
            pygame.draw.circle(surf, helm_shad, (csx,csy), camo_rng.randint(1,3))

        # ── Arms ──────────────────────────────────────────────────────────────
        arm_col = vest_col
        # Left arm (back)
        pygame.draw.line(surf, arm_col, (cx2-10, cy2+20), (cx2-16, cy2+32), 5)
        # Right arm (gun arm)
        gun_y = cy2 + 24 + int(math.sin(t*0.005)*2)
        pygame.draw.line(surf, arm_col, (cx2+10, cy2+20),
                         (cx2+f*18, gun_y), 5)

        # ── Rifle ─────────────────────────────────────────────────────────────
        gun_base_x = cx2 + f*14
        gun_base_y = gun_y - 2
        # Receiver
        pygame.draw.rect(surf, (30,30,30),
                         (gun_base_x, gun_base_y-3, f*18 if f>0 else -f*18, 7))
        # Barrel
        pygame.draw.line(surf, (45,45,45),
                         (gun_base_x + f*14, gun_base_y-1),
                         (gun_base_x + f*26, gun_base_y-1), 3)
        # Muzzle
        pygame.draw.rect(surf, (22,22,22),
                         (gun_base_x + f*24, gun_base_y-3, 4, 5), border_radius=1)
        # Stock
        pygame.draw.rect(surf, (80,55,28),
                         (gun_base_x - f*2, gun_base_y-2, f*(-8) if f>0 else 8, 8),
                         border_radius=1)
        # Magazine
        pygame.draw.rect(surf, (38,38,38),
                         (gun_base_x + f*6, gun_base_y+4, 5, 7), border_radius=1)

        # ── State icon ────────────────────────────────────────────────────────
        icons = {self.ST_CHASE:"!", self.ST_SHOOT:"✕", self.ST_FLANK:"?"}
        icon_cols = {self.ST_CHASE:(240,120,20),
                     self.ST_SHOOT:(220,50,50), self.ST_FLANK:(200,50,200)}
        if self.state in icons:
            pulse2 = abs(math.sin(t*0.01))*3
            if_font = pygame.font.SysFont("consolas",13,bold=True)
            if_surf = if_font.render(icons[self.state], True, icon_cols[self.state])
            surf.blit(if_surf, (cx2-if_surf.get_width()//2, cy2-22-int(pulse2)))

        # ── HP bar ────────────────────────────────────────────────────────────
        bw=36; bx3=cx2-bw//2; by3=cy2-14
        pygame.draw.rect(surf,(10,10,10),(bx3,by3,bw,5),border_radius=2)
        hp_r=self.hp/self.max_hp
        hc=(50,200,80) if hp_r>0.6 else (220,190,50) if hp_r>0.3 else (220,40,40)
        if hp_r>0:
            pygame.draw.rect(surf,hc,(bx3,by3,int(bw*hp_r),5),border_radius=2)
            sh2=pygame.Surface((int(bw*hp_r),2),pygame.SRCALPHA)
            sh2.fill((255,255,255,50)); surf.blit(sh2,(bx3,by3))
        pygame.draw.rect(surf,(60,60,70),(bx3,by3,bw,5),1,border_radius=2)

# ═══════════════════════════════════════════════════
#  JETPACK / TANK / DRONE / HELI / JET / BOSS
#  (kompakter Code, Difficulty-aware)
# ═══════════════════════════════════════════════════
class JetpackSoldier:
    W=28;H=48;is_air=True
    def __init__(self,x,y):
        diff=get_diff()
        self.x=float(x);self.y=float(y);self.vy=0.0
        self.MAX_HP=int(80*diff["enemy_hp_mult"]);self.hp=self.MAX_HP
        self.alive=True;self.facing=-1;self.last_shot=0
        self.shoot_rate=int(1200*diff["shoot_rate_mult"])
        self.hover_y=float(y)-120;self.strafe_timer=0;self.strafe_dir=random.choice([-1,1])
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    def update(self,player,bullets):
        target_vy=(self.hover_y-self.y)*0.05;self.vy+=(target_vy-self.vy)*0.1;self.y+=self.vy
        self.strafe_timer+=1
        if self.strafe_timer>90: self.strafe_dir=random.choice([-1,1]);self.strafe_timer=0
        self.x+=self.strafe_dir*2.5;self.x=max(100,min(WORLD_WIDTH-100,self.x))
        self.facing=1 if player.x>self.x else -1
        now=pygame.time.get_ticks()
        if now-self.last_shot>self.shoot_rate and abs(player.x-self.x)<500:
            self.last_shot=now
            ox=self.rect.centerx;oy=self.rect.centery
            angle=math.atan2(player.rect.centery-oy,player.rect.centerx-ox)+random.uniform(-0.1,0.1)
            dmg=int(10*get_diff()["enemy_dmg_mult"])
            bullets.append(Bullet(ox,oy,math.cos(angle)*12,math.sin(angle)*12,dmg,ORANGE))
            SFX.play(SFX.shoot_rifle)
        if random.random()<0.4: PARTICLES.spawn_smoke(self.x+self.W//2,self.y+self.H)
    def take_damage(self,amount,is_rocket=False):
        self.hp-=amount;SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_blood(self.rect.centerx,self.rect.centery,6)
        if self.hp<=0: self.alive=False;PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery)
    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        cx2 = sx + self.W // 2
        cy2 = int(self.y)
        f   = self.facing
        t   = pygame.time.get_ticks()

        # ── Jetpack exhaust flames ────────────────────────────────────────────
        # Two nozzles — left and right of pack
        for nz_off in (-5, 5):
            fl_len = random.randint(14, 28)
            for fi in range(7):
                t2 = fi / 6
                fc2 = [(255,248,80),(255,192,28),(255,118,8),
                       (220,58,6),(160,32,4),(100,18,2),(50,8,0)][fi]
                fr2 = max(1, int((7-fi)*0.9))
                py2 = int(cy2 + self.H - 4 + fi*fl_len//7)
                fs3 = pygame.Surface((fr2*2+2, fr2*2+2), pygame.SRCALPHA)
                pygame.draw.circle(fs3, (*fc2, 220-fi*28), (fr2+1,fr2+1), fr2)
                surf.blit(fs3, (cx2+nz_off-fr2-1, py2-fr2-1))
            # Heat distortion ring
            ring_s = pygame.Surface((16,6), pygame.SRCALPHA)
            pygame.draw.ellipse(ring_s, (255,150,40,60), (0,0,16,6))
            surf.blit(ring_s, (cx2+nz_off-8, cy2+self.H-4))

        # ── Ground shadow (faint, far below) ──────────────────────────────────
        sh_dist = max(0, GROUND_Y - (cy2 + self.H))
        sh_alpha = max(0, int(55 - sh_dist * 0.12))
        if sh_alpha > 0:
            sh = pygame.Surface((self.W+10, 8), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0,0,0,sh_alpha), (0,0,self.W+10,8))
            surf.blit(sh, (cx2-self.W//2-5, GROUND_Y-5))

        # ── BOOTS ─────────────────────────────────────────────────────────────
        boot_col  = (22, 18, 12)
        boot_sole = (35, 28, 18)
        pygame.draw.rect(surf, boot_col,  (cx2-9, cy2+40, 10, 8), border_radius=2)
        pygame.draw.rect(surf, boot_sole, (cx2-10,cy2+46, 12, 3), border_radius=1)
        pygame.draw.rect(surf, boot_col,  (cx2+1,  cy2+40, 10, 8), border_radius=2)
        pygame.draw.rect(surf, boot_sole, (cx2,    cy2+46, 12, 3), border_radius=1)
        # Boot buckle clasps
        pygame.draw.rect(surf, (55,50,42), (cx2-8, cy2+40, 3, 3))
        pygame.draw.rect(surf, (55,50,42), (cx2+2, cy2+40, 3, 3))

        # ── LEGS ─────────────────────────────────────────────────────────────
        trouser_col = (55, 80, 58)
        trouser_hi  = (72, 102, 75)
        # Left leg
        pygame.draw.rect(surf, trouser_col, (cx2-9,  cy2+28, 9,  13), border_radius=2)
        pygame.draw.rect(surf, trouser_hi,  (cx2-9,  cy2+28, 3,  13))
        # Right leg
        pygame.draw.rect(surf, trouser_col, (cx2+1,  cy2+28, 9,  13), border_radius=2)
        pygame.draw.rect(surf, trouser_hi,  (cx2+1,  cy2+28, 3,  13))
        # Leg pockets
        pygame.draw.rect(surf, (42,62,44),  (cx2-9,  cy2+32, 7,  6), border_radius=1)
        pygame.draw.rect(surf, (42,62,44),  (cx2+3,  cy2+32, 7,  6), border_radius=1)
        # Harness leg straps
        pygame.draw.line(surf, (35,30,20), (cx2-8, cy2+28), (cx2-6, cy2+44), 2)
        pygame.draw.line(surf, (35,30,20), (cx2+8, cy2+28), (cx2+6, cy2+44), 2)

        # ── BODY / FLIGHT SUIT ────────────────────────────────────────────────
        suit_col  = (48, 72, 52)
        suit_hi   = (65, 95, 70)
        suit_dk   = (32, 50, 36)
        pygame.draw.rect(surf, suit_col, (cx2-11, cy2+14, 22, 16), border_radius=3)
        pygame.draw.rect(surf, suit_hi,  (cx2-11, cy2+14, 22,  4), border_radius=3)
        pygame.draw.rect(surf, suit_dk,  (cx2-11, cy2+26, 22,  4))
        # Chest harness X-strap
        pygame.draw.line(surf, (28,24,14), (cx2-10, cy2+15), (cx2+5, cy2+28), 2)
        pygame.draw.line(surf, (28,24,14), (cx2+10, cy2+15), (cx2-5, cy2+28), 2)
        # Center D-ring
        pygame.draw.circle(surf, (55,50,32), (cx2, cy2+22), 3, 1)
        # Chest plate light
        light_pulse = int(128 + abs(math.sin(t*0.008))*127)
        lc = (80, 200, 80) if self.hp > self.MAX_HP*0.5 else (220, 80, 20)
        ls2 = pygame.Surface((6,6), pygame.SRCALPHA)
        pygame.draw.circle(ls2, (*lc, light_pulse), (3,3), 3)
        surf.blit(ls2, (cx2-3, cy2+16))
        # Shoulder pads (streamlined)
        pygame.draw.rect(surf, suit_dk, (cx2-14, cy2+14, 5, 10), border_radius=2)
        pygame.draw.rect(surf, suit_dk, (cx2+9,  cy2+14, 5, 10), border_radius=2)

        # ── JETPACK ───────────────────────────────────────────────────────────
        pack_col  = (38, 42, 52)
        pack_hi   = (55, 60, 75)
        pack_dk   = (24, 26, 34)
        # Main pack body
        pygame.draw.rect(surf, pack_col, (cx2-10, cy2+14, 20, 20), border_radius=3)
        pygame.draw.rect(surf, pack_hi,  (cx2-10, cy2+14, 20,  4), border_radius=3)
        pygame.draw.rect(surf, pack_dk,  (cx2-10, cy2+30, 20,  4))
        # Pack rivet lines
        for rv_y in (cy2+19, cy2+26):
            pygame.draw.line(surf, pack_dk, (cx2-8, rv_y), (cx2+8, rv_y), 1)
        # Fuel tank cylinders (two)
        for tz_off in (-5, 5):
            pygame.draw.rect(surf, pack_dk, (cx2+tz_off-3, cy2+16, 6, 16), border_radius=3)
            pygame.draw.rect(surf, pack_hi,  (cx2+tz_off-3, cy2+16, 6,  4), border_radius=3)
            # Nozzle
            pygame.draw.rect(surf, (28,28,35), (cx2+tz_off-3, cy2+32, 6, 4), border_radius=1)
        # Altitude gauge
        pygame.draw.rect(surf, pack_dk, (cx2-4, cy2+20, 8, 5), border_radius=1)
        gauge_ratio = 1.0 - max(0, min(1, (GROUND_Y-cy2)/400))
        pygame.draw.rect(surf, (80,200,80) if gauge_ratio<0.7 else (220,80,20),
                         (cx2-3, cy2+21, int(6*gauge_ratio), 3))

        # ── NECK ─────────────────────────────────────────────────────────────
        pygame.draw.rect(surf, (175, 128, 88), (cx2-3, cy2+10, 6, 6))
        # Helmet neck guard
        pygame.draw.rect(surf, suit_dk, (cx2-5, cy2+12, 10, 4), border_radius=1)

        # ── HEAD ─────────────────────────────────────────────────────────────
        skin_col = (182, 134, 92)
        pygame.draw.circle(surf, skin_col, (cx2, cy2+6), 10)
        pygame.draw.circle(surf, (145, 105, 72), (cx2+f*3, cy2+7), 5)
        pygame.draw.ellipse(surf, skin_col, (cx2-f*11, cy2+2, 5, 8))
        # Eye
        eye_x2 = cx2 + f*4
        pygame.draw.circle(surf, (228,222,212), (eye_x2, cy2+4), 2)
        pygame.draw.circle(surf, (20, 15, 10), (eye_x2, cy2+4), 1)

        # ── FLIGHT HELMET (FAST/HGU style) ────────────────────────────────────
        helm_col  = (42, 58, 45)
        helm_hi2  = (58, 78, 62)
        helm_dk2  = (28, 40, 30)
        # Shell
        pygame.draw.arc(surf, helm_col,
                        pygame.Rect(cx2-12, cy2-4, 24, 20), 0, math.pi, 0)
        pygame.draw.rect(surf, helm_col, (cx2-12, cy2+6, 24, 6))
        # Dome shine
        pygame.draw.arc(surf, helm_hi2,
                        pygame.Rect(cx2-9, cy2-2, 12, 12), 0.4, math.pi-0.4, 3)
        # Visor — tinted dark
        pygame.draw.rect(surf, (22, 28, 38), (cx2-12, cy2+2, 24, 8))
        pygame.draw.rect(surf, (35, 45, 62), (cx2-12, cy2+2, 24, 3))
        # Visor glint
        pygame.draw.line(surf, (80, 110, 150), (cx2-10, cy2+3), (cx2+4, cy2+3), 1)
        # Brim
        pygame.draw.rect(surf, helm_dk2, (cx2-13, cy2+9, 26, 3), border_radius=1)
        # Comm antenna stub
        pygame.draw.line(surf, (62, 70, 58), (cx2-f*10, cy2-4), (cx2-f*15, cy2-10), 2)
        pygame.draw.circle(surf, (255, 100, 100), (cx2-f*15, cy2-10), 2)
        # Oxygen mask lower face
        pygame.draw.rect(surf, (28, 35, 30), (cx2-8, cy2+8, 16, 5), border_radius=2)
        pygame.draw.circle(surf, (38, 48, 40), (cx2-3, cy2+10), 2)
        pygame.draw.circle(surf, (38, 48, 40), (cx2+3, cy2+10), 2)

        # ── ARMS ─────────────────────────────────────────────────────────────
        arm_col2 = suit_col
        # Left arm
        pygame.draw.line(surf, arm_col2, (cx2-10, cy2+16), (cx2-18, cy2+28), 5)
        pygame.draw.circle(surf, (30,22,12), (cx2-18, cy2+28), 4)
        # Gun arm
        gun_y4 = cy2 + 20 + int(math.sin(t*0.005)*2)
        pygame.draw.line(surf, arm_col2, (cx2+10, cy2+16), (cx2+f*20, gun_y4), 5)
        pygame.draw.circle(surf, (30,22,12), (cx2+f*20, gun_y4), 4)

        # ── SMG / COMPACT RIFLE ────────────────────────────────────────────────
        gx5 = cx2 + f*16; gy5 = gun_y4 - 3
        # Compact receiver
        pygame.draw.rect(surf, (32,32,32), (gx5, gy5-3, f*18 if f>0 else -f*18, 7))
        pygame.draw.rect(surf, (48,48,48), (gx5, gy5-3, f*18 if f>0 else -f*18, 3))
        # Barrel
        pygame.draw.line(surf, (40,40,40),
                         (gx5+f*14, gy5-1), (gx5+f*28, gy5-1), 3)
        # Suppressor
        pygame.draw.rect(surf, (28,28,28), (gx5+f*26, gy5-4, f*8 if f>0 else -f*8, 7), border_radius=1)
        # Magazine
        pygame.draw.rect(surf, (36,36,36), (gx5+f*4, gy5+4, 6, 8), border_radius=1)
        # Stock fold
        pygame.draw.rect(surf, (55,42,22), (gx5-f*2, gy5-2, f*(-6), 6), border_radius=1)

        # ── HP bar ────────────────────────────────────────────────────────────
        bw5 = 38; bx5 = cx2-bw5//2; by5 = int(self.y)-14
        pygame.draw.rect(surf, (8,8,12), (bx5-1,by5-1,bw5+2,7), border_radius=2)
        pygame.draw.rect(surf, DARK, (bx5,by5,bw5,5), border_radius=2)
        hp_r5 = self.hp / self.MAX_HP
        hc5 = (50,210,80) if hp_r5>0.5 else (225,192,48) if hp_r5>0.25 else (218,38,38)
        if hp_r5 > 0:
            pygame.draw.rect(surf, hc5, (bx5,by5,int(bw5*hp_r5),5), border_radius=2)
            sh6 = pygame.Surface((int(bw5*hp_r5),2), pygame.SRCALPHA)
            sh6.fill((255,255,255,48)); surf.blit(sh6,(bx5,by5))
        pygame.draw.rect(surf, (55,80,58),(bx5,by5,bw5,5),1,border_radius=2)
        lf5 = pygame.font.SysFont("consolas",8,bold=True)
        surf.blit(lf5.render("JETPACK",True,(80,200,100)),(cx2-16,by5-10))

class Tank:
    W=80;H=40;SPEED=0.8;SHOOT_RATE=2500;is_air=False
    def __init__(self,x,y):
        diff=get_diff()
        self.x=float(x);self.y=float(y-self.H)
        self.MAX_HP=int(350*diff["enemy_hp_mult"]);self.hp=self.MAX_HP
        self.alive=True;self.facing=-1;self.last_shot=0;self.vy=0.0;self.on_ground=False
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    def update(self,player,bullets):
        self.vy=min(self.vy+0.7,18);self.y+=self.vy;self.on_ground=False
        for plat in current_platforms:
            r=self.rect
            if r.colliderect(plat) and self.vy>=0:
                if r.bottom-self.vy<=plat.top+abs(self.vy)+2:
                    self.y=plat.top-self.H;self.vy=0;self.on_ground=True
        dx=player.x-self.x;self.facing=1 if dx>0 else -1
        if abs(dx)>200: self.x+=self.SPEED*(1 if dx>0 else -1)
        self.x=max(0,min(WORLD_WIDTH-self.W,self.x))
        now=pygame.time.get_ticks()
        if now-self.last_shot>=self.SHOOT_RATE and abs(dx)<700:
            self.last_shot=now;SFX.play(SFX.tank_shot)
            ox=self.rect.centerx+(self.facing*50);oy=int(self.y)+10
            d2=math.hypot(player.rect.centerx-ox,player.rect.centery-oy) or 1
            dmg=int(25*get_diff()["enemy_dmg_mult"])
            bullets.append(Bullet(ox,oy,(player.rect.centerx-ox)/d2*14,(player.rect.centery-oy)/d2*14,dmg,(200,150,50),is_sniper=True))
            PARTICLES.spawn_explosion(ox,oy,scale=0.5)
        if random.random()<0.1: PARTICLES.spawn_smoke(int(self.x)+self.W//2,int(self.y))
    def take_damage(self,amount,is_rocket=False):
        dmg=amount if is_rocket else max(1,amount//4)
        self.hp-=dmg;SFX.play(SFX.hit_enemy);PARTICLES.spawn_sparks(self.rect.centerx,self.rect.centery,6)
        if self.hp<=0:
            self.alive=False;PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=2.5)
            SFX.play(SFX.big_explosion)
    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        cy  = int(self.y)
        f   = self.facing
        W   = self.W
        cx  = sx + W // 2
        tick = pygame.time.get_ticks()

        # ── Shadow ────────────────────────────────────────────────────────────
        sh = pygame.Surface((W+16, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,60), (0,0,W+16,10))
        surf.blit(sh, (sx-8, cy+self.H-4))

        # ── Tracks (left + right, each is a rounded rect with link marks) ────
        for ty_off, track_y in enumerate([cy+22, cy+26]):
            pygame.draw.rect(surf, (28,28,28),   (sx,    track_y, W, 14), border_radius=3)
            pygame.draw.rect(surf, (44,44,44),   (sx,    track_y, W, 14), 1, border_radius=3)
            # Track link segments
            for lx in range(sx+4, sx+W-4, 9):
                pygame.draw.rect(surf, (55,55,55), (lx, track_y+2, 7, 10), border_radius=1)
                pygame.draw.rect(surf, (70,70,70), (lx, track_y+2, 7, 3),  border_radius=1)
        # Drive sprockets
        pygame.draw.circle(surf, (50,50,50), (sx+10,   cy+29), 10)
        pygame.draw.circle(surf, (65,65,65), (sx+10,   cy+29),  7)
        pygame.draw.circle(surf, (50,50,50), (sx+W-10, cy+29), 10)
        pygame.draw.circle(surf, (65,65,65), (sx+W-10, cy+29),  7)
        # Road wheels (3 between)
        for wx_off in (24, 40, 56):
            pygame.draw.circle(surf, (42,42,42), (sx+wx_off, cy+29), 6)
            pygame.draw.circle(surf, (58,58,58), (sx+wx_off, cy+29), 4)

        # ── Hull body ─────────────────────────────────────────────────────────
        # Main hull
        hull_col   = (62, 78, 52)
        hull_hi    = (78, 96, 64)
        hull_shad  = (42, 52, 34)
        pygame.draw.rect(surf, hull_col,  (sx+3,  cy+12, W-6, 20), border_radius=3)
        pygame.draw.rect(surf, hull_hi,   (sx+3,  cy+12, W-6,  5), border_radius=3)
        pygame.draw.rect(surf, hull_shad, (sx+3,  cy+28, W-6,  4), border_radius=3)
        # Glacis plate (angled front)
        glacis_pts = [(sx+W if f>0 else sx, cy+12),
                      (sx+W if f>0 else sx, cy+32),
                      (sx+W-6 if f>0 else sx+6, cy+32),
                      (sx+W-10 if f>0 else sx+10, cy+12)]
        pygame.draw.polygon(surf, hull_shad, glacis_pts)
        # Side skirt armour
        pygame.draw.rect(surf, (50,64,40), (sx+2, cy+18, W-4, 14))
        # Exhaust grill (rear)
        rear_x = sx if f > 0 else sx+W-12
        for gy_off in range(cy+15, cy+28, 4):
            pygame.draw.line(surf, (30,30,30), (rear_x, gy_off), (rear_x+10, gy_off), 2)

        # ── Turret ────────────────────────────────────────────────────────────
        turret_col  = (68, 84, 56)
        turret_hi   = (85, 104, 70)
        # Base ring
        pygame.draw.ellipse(surf, (48,60,38), (cx-22, cy+4, 44, 14))
        # Turret body (hexagonal look)
        pygame.draw.rect(surf, turret_col,  (cx-18, cy-8,  36, 18), border_radius=4)
        pygame.draw.rect(surf, turret_hi,   (cx-18, cy-8,  36,  5), border_radius=4)
        pygame.draw.rect(surf, hull_shad,   (cx-18, cy+7,  36,  3))
        # Commander's hatch
        pygame.draw.ellipse(surf, (55,68,44), (cx-6, cy-12, 12, 8))
        pygame.draw.ellipse(surf, (75,90,60), (cx-4, cy-11,  8, 5))
        # Rangefinder bumps
        for rx_off in (-16, 14):
            pygame.draw.rect(surf, (45,58,36), (cx+rx_off, cy-6, 6, 6), border_radius=1)

        # ── Gun barrel ────────────────────────────────────────────────────────
        blen = 38
        bx1  = cx + (0 if f<0 else 0)
        bx2  = cx + f * blen
        # Mantlet (rounded housing where barrel meets turret)
        pygame.draw.ellipse(surf, (48,62,40), (cx-8, cy-4, 16, 10))
        # Main barrel (two-tone: top lighter)
        pygame.draw.line(surf, (40,52,32), (cx, cy+1), (bx2, cy+1), 7)
        pygame.draw.line(surf, (62,78,52), (cx, cy-2), (bx2, cy-2), 4)
        pygame.draw.line(surf, (80,96,64), (cx, cy-3), (bx2, cy-3), 2)
        # Muzzle brake
        pygame.draw.rect(surf, (35,44,28),
                         (bx2 - (5 if f>0 else 0), cy-5, 7, 12), border_radius=1)
        pygame.draw.rect(surf, (55,68,44),
                         (bx2 - (5 if f>0 else 0), cy-5, 7,  4), border_radius=1)
        # Bore evacuator
        mid_x = cx + f * (blen//2)
        pygame.draw.ellipse(surf, (50,64,40), (mid_x-4, cy-4, 8, 10))

        # ── Muzzle flash when firing ──────────────────────────────────────────
        since = tick - self.last_shot
        if since < 100:
            ratio = 1 - since/100
            mf = pygame.Surface((28,28), pygame.SRCALPHA)
            pygame.draw.circle(mf, (255,220,80, int(180*ratio)), (14,14), int(12*ratio))
            pygame.draw.circle(mf, (255,255,200,int(220*ratio)), (14,14), int(6*ratio))
            surf.blit(mf, (bx2-14, cy-14))

        # ── HP bar ────────────────────────────────────────────────────────────
        bw=70; bx=sx+(W-bw)//2; by=cy-18
        pygame.draw.rect(surf, (10,10,10), (bx,by,bw,8), border_radius=3)
        hp_r = self.hp/self.MAX_HP
        hc = (50,200,80) if hp_r>0.5 else (220,190,50) if hp_r>0.25 else (220,40,40)
        if hp_r > 0:
            pygame.draw.rect(surf, hc, (bx,by,int(bw*hp_r),8), border_radius=3)
            shine = pygame.Surface((int(bw*hp_r), 3), pygame.SRCALPHA)
            shine.fill((255,255,255,50)); surf.blit(shine,(bx,by))
        pygame.draw.rect(surf, (80,80,80), (bx,by,bw,8), 1, border_radius=3)
        lf = pygame.font.SysFont("consolas",9,bold=True)
        surf.blit(lf.render("TANK",True,(180,210,140)), (cx-10, by-12))

class Drone:
    W=36;H=20;SPEED=2.5;SHOOT_RATE=1800;is_air=True
    def __init__(self,x):
        diff=get_diff()
        self.x=float(x);self.y=float(GROUND_Y-200-random.randint(0,80))
        self.MAX_HP=int(45*diff["enemy_hp_mult"]);self.hp=self.MAX_HP
        self.alive=True;self.facing=-1;self.last_shot=0
        self.bob_offset=random.uniform(0,2*math.pi)
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    def update(self,player,bullets):
        self.y+=math.sin(pygame.time.get_ticks()*0.003+self.bob_offset)*0.5
        dx=player.x-self.x;self.facing=1 if dx>0 else -1;dist=abs(dx)
        if dist>300: self.x+=self.SPEED*(1 if dx>0 else -1)
        elif dist<150: self.x-=self.SPEED*0.5*(1 if dx>0 else -1)
        self.x=max(50,min(WORLD_WIDTH-50,self.x))
        now=pygame.time.get_ticks()
        if now-self.last_shot>=self.SHOOT_RATE and dist<500:
            self.last_shot=now
            ox=self.rect.centerx;oy=self.rect.bottom
            angle=math.atan2(player.rect.centery-oy,player.rect.centerx-ox)+random.uniform(-0.1,0.1)
            dmg=int(8*get_diff()["enemy_dmg_mult"])
            bullets.append(Bullet(ox,oy,math.cos(angle)*10,math.sin(angle)*10,dmg,(255,100,100)))
            SFX.play(SFX.shoot_pistol)
    def take_damage(self, amount, is_rocket=False):
        dmg = amount if is_rocket else max(1, amount // 4)
        self.hp -= dmg
        SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 8)
        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_tank_death(self.rect.centerx, self.rect.centery)
            SFX.play(SFX.big_explosion)
    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        cx2 = sx + self.W // 2
        cy2 = int(self.y) + self.H // 2
        t   = pygame.time.get_ticks()
        bob = math.sin(t * 0.004 + self.bob_offset) * 3

        # ── Shadow on ground (faint) ──────────────────────────────────────────
        sh_y = GROUND_Y - 4
        sh_w = max(6, int(self.W * 0.6 * (1 - (cy2/sh_y)*0.5)))
        shsurf = pygame.Surface((sh_w*2, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shsurf, (0,0,0,28), (0,0,sh_w*2,6))
        surf.blit(shsurf, (cx2-sh_w, sh_y))

        # ── Central hex body ──────────────────────────────────────────────────
        body_col  = (40, 44, 60)
        body_hi   = (60, 65, 85)
        body_y    = int(cy2 + bob) - 6
        # Hexagonal body (approximated as two overlapping rects)
        pygame.draw.rect(surf, body_col,  (cx2-10, body_y,    20, 12), border_radius=4)
        pygame.draw.rect(surf, body_col,  (cx2-7,  body_y-3,  14, 18), border_radius=3)
        pygame.draw.rect(surf, body_hi,   (cx2-9,  body_y+1,  18,  3))
        # Panel lines
        pygame.draw.line(surf, (30,32,46), (cx2-8, body_y+6), (cx2+8, body_y+6), 1)

        # ── Sensor ball (underside) ───────────────────────────────────────────
        sensor_y = body_y + 14
        pygame.draw.circle(surf, (28,30,42), (cx2, sensor_y), 5)
        pygame.draw.circle(surf, (60,180,220), (cx2, sensor_y), 3)
        pygame.draw.circle(surf, (200,240,255),(cx2-1,sensor_y-1), 1)

        # ── 4 Arms + spinning rotors ───────────────────────────────────────────
        arm_len = 16; rotor_r = 11
        arm_dirs = [(-1,-1),( 1,-1),(-1, 1),( 1, 1)]
        rotor_spd = t * 0.18
        for dx4, dy4 in arm_dirs:
            ax = cx2 + dx4 * arm_len
            ay = body_y + 4 + dy4 * arm_len
            # Arm tube
            pygame.draw.line(surf, (50,52,68), (cx2, body_y+4), (ax, ay), 3)
            pygame.draw.line(surf, (68,72,90), (cx2, body_y+4), (ax, ay), 1)
            # Motor housing
            pygame.draw.circle(surf, (38,40,55), (ax, ay), 5)
            pygame.draw.circle(surf, (58,62,78), (ax, ay), 3)
            # Rotor blades (2 blades, spinning)
            blade_ang = rotor_spd * dx4 * dy4
            for bk in range(2):
                ba = blade_ang + bk * math.pi
                bx1r = int(ax + math.cos(ba) * rotor_r)
                by1r = int(ay + math.sin(ba) * rotor_r * 0.25)
                bx2r = int(ax - math.cos(ba) * rotor_r)
                by2r = int(ay - math.sin(ba) * rotor_r * 0.25)
                # Blade with motion blur (multiple lines at alpha)
                for blur in range(3):
                    ba2 = ba + blur * 0.18
                    bx1b = int(ax + math.cos(ba2) * rotor_r)
                    by1b = int(ay + math.sin(ba2) * rotor_r * 0.25)
                    bx2b = int(ax - math.cos(ba2) * rotor_r)
                    by2b = int(ay - math.sin(ba2) * rotor_r * 0.25)
                    rsurf = pygame.Surface((rotor_r*4, rotor_r*2+4), pygame.SRCALPHA)
                    alpha = 160 - blur * 50
                    pygame.draw.line(surf,
                                     (160, 165, 185, alpha) if alpha>0 else (0,0,0,0),
                                     (bx1b, by1b), (bx2b, by2b), max(1, 2-blur))

        # ── Blinking LEDs ──────────────────────────────────────────────────────
        led_blink = (t // 400) % 2 == 0
        led_col = (255,30,30) if led_blink else (80,10,10)
        pygame.draw.circle(surf, led_col, (cx2-9, body_y+3), 2)
        led2 = (30,255,80) if not led_blink else (10,80,25)
        pygame.draw.circle(surf, led2, (cx2+9, body_y+3), 2)
        # Navigation light glow
        if led_blink:
            ls = pygame.Surface((10,10), pygame.SRCALPHA)
            pygame.draw.circle(ls, (255,40,40,80), (5,5), 5)
            surf.blit(ls, (cx2-14, body_y-2))

        # ── HP bar ────────────────────────────────────────────────────────────
        bw=32; bx3=cx2-bw//2; by3=int(self.y)-14
        pygame.draw.rect(surf,(10,10,10),(bx3,by3,bw,4))
        hp_r=self.hp/self.MAX_HP
        pygame.draw.rect(surf,(50,200,80) if hp_r>0.5 else (220,40,40),
                         (bx3,by3,int(bw*hp_r),4))
        
class Helicopter:
    W=90;H=35;SPEED=1.5;SHOOT_RATE=1200;is_air=True
    def __init__(self,x):
        diff=get_diff()
        self.x=float(x);self.y=float(GROUND_Y-220-random.randint(0,60))
        self.MAX_HP=int(200*diff["enemy_hp_mult"]);self.hp=self.MAX_HP
        self.alive=True;self.facing=-1;self.last_shot=0;self.rotor_angle=0.0
        self.strafe_dir=random.choice([-1,1]);self.strafe_timer=0
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    def update(self,player,bullets):
        self.rotor_angle+=0.2;dx=player.x-self.x;self.facing=1 if dx>0 else -1
        self.strafe_timer+=1
        if self.strafe_timer>120: self.strafe_dir*=-1;self.strafe_timer=0
        self.x+=self.strafe_dir*self.SPEED;self.x=max(100,min(WORLD_WIDTH-100,self.x))
        self.y+=math.sin(pygame.time.get_ticks()*0.002)*0.3
        now=pygame.time.get_ticks()
        if now-self.last_shot>=self.SHOOT_RATE and abs(dx)<800:
            self.last_shot=now;SFX.play(SFX.shoot_rifle)
            ox=self.rect.centerx;oy=self.rect.bottom+5
            dmg=int(12*get_diff()["enemy_dmg_mult"])
            for i in range(3):
                angle=math.atan2(player.rect.centery-oy,player.rect.centerx-ox)+random.uniform(-0.15,0.15)
                bullets.append(Bullet(ox,oy,math.cos(angle)*13,math.sin(angle)*13,dmg,(255,150,50)))
    def take_damage(self, amount, is_rocket=False):
        dmg = amount if is_rocket else max(1, amount // 3)
        self.hp -= dmg
        SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 8)
        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_air_death(self.rect.centerx, self.rect.centery)
            SFX.play(SFX.big_explosion)
    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        cx2 = sx + self.W // 2
        cy2 = int(self.y) + self.H // 2
        f   = self.facing
        t   = pygame.time.get_ticks()
        bob = math.sin(t * 0.0025) * 2.5

        body_col  = (55, 65, 80)
        body_hi   = (75, 88, 108)
        body_shad = (38, 45, 58)
        accent    = (180, 40, 40)   # red stripe

        # ── Shadow ────────────────────────────────────────────────────────────
        shW = 80
        shsurf = pygame.Surface((shW, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shsurf, (0,0,0,22), (0,0,shW,8))
        surf.blit(shsurf, (cx2-shW//2, GROUND_Y-6))

        base_y = int(cy2 + bob)

        # ── Main fuselage ─────────────────────────────────────────────────────
        # Body (tapered ellipse)
        pygame.draw.ellipse(surf, body_col,  (sx+8,  base_y-12, 62, 26))
        pygame.draw.ellipse(surf, body_hi,   (sx+8,  base_y-12, 62,  8))
        pygame.draw.ellipse(surf, body_shad, (sx+8,  base_y+10, 62,  4))
        # Nose bulge
        nose_x = sx+68 if f>0 else sx+8
        pygame.draw.ellipse(surf, body_col,  (nose_x-10, base_y-10, 20, 20))
        pygame.draw.ellipse(surf, body_hi,   (nose_x-10, base_y-10, 20, 8))

        # ── Cockpit glazing ───────────────────────────────────────────────────
        cock_x = sx+48 if f>0 else sx+18
        pygame.draw.ellipse(surf, (50,160,200,180), (cock_x-11, base_y-9, 22, 16))
        # Canopy frame
        pygame.draw.ellipse(surf, body_col, (cock_x-11, base_y-9, 22, 16), 1)
        # Glint
        pygame.draw.ellipse(surf, (200,240,255), (cock_x-7, base_y-8, 10, 5))

        # ── Red accent stripe ──────────────────────────────────────────────────
        pygame.draw.line(surf, accent, (sx+10, base_y+2), (sx+68, base_y+2), 3)

        # ── Tail boom ─────────────────────────────────────────────────────────
        tail_x1 = sx+10 if f>0 else sx+70
        tail_x2 = sx-24 if f>0 else sx+114
        pygame.draw.line(surf, body_shad, (tail_x1, base_y+2), (tail_x2, base_y+4), 8)
        pygame.draw.line(surf, body_hi,   (tail_x1, base_y+2), (tail_x2, base_y+4), 3)
        # Tail fin
        pygame.draw.polygon(surf, body_col,
                            [(tail_x2,        base_y+4),
                             (tail_x2 + f*4,  base_y-14),
                             (tail_x2 + f*14, base_y+4)])
        pygame.draw.polygon(surf, body_hi,
                            [(tail_x2,        base_y+4),
                             (tail_x2 + f*4,  base_y-14),
                             (tail_x2 + f*10, base_y+4)], 1)

        # ── Tail rotor (side-facing) ───────────────────────────────────────────
        tr_x = tail_x2 + f*3; tr_y = base_y - 4
        pygame.draw.circle(surf, (42,50,62), (tr_x, tr_y), 7)
        tr_ang = t * 0.22
        for bk in range(2):
            ba = tr_ang + bk * math.pi
            for blur in range(3):
                ba2 = ba + blur * 0.25
                lx1 = int(tr_x + math.cos(ba2) * 7)
                ly1 = int(tr_y + math.sin(ba2) * 7)
                lx2 = int(tr_x - math.cos(ba2) * 7)
                ly2 = int(tr_y - math.sin(ba2) * 7)
                a2  = 140 - blur*45
                if a2 > 0:
                    bs2 = pygame.Surface((20,20), pygame.SRCALPHA)
                    pygame.draw.line(surf, (130,138,158), (lx1,ly1),(lx2,ly2),
                                     max(1, 2-blur))

        # ── Skid landing gear ─────────────────────────────────────────────────
        for sk_off in (-18, 18):
            sk_x = cx2 + sk_off
            pygame.draw.line(surf, (45,50,60), (sk_x, base_y+12), (sk_x, base_y+20), 3)
        pygame.draw.line(surf, (45,50,60), (cx2-22, base_y+20), (cx2+22, base_y+20), 3)

        # ── Main rotor ────────────────────────────────────────────────────────
        rotor_ang = self.rotor_angle
        rotor_cx  = cx2; rotor_cy = base_y - 13
        pygame.draw.circle(surf, (50,56,70), (rotor_cx, rotor_cy), 5)
        for bk in range(3):
            ba = rotor_ang + bk * (2*math.pi/3)
            rotor_len = 38
            for blur in range(4):
                ba2 = ba + blur * 0.14
                rx1 = int(rotor_cx + math.cos(ba2) * rotor_len)
                ry1 = int(rotor_cy + math.sin(ba2) * rotor_len * 0.18)
                rx2 = int(rotor_cx - math.cos(ba2) * rotor_len)
                ry2 = int(rotor_cy - math.sin(ba2) * rotor_len * 0.18)
                alpha_r = 200 - blur * 48
                if alpha_r > 0:
                    pygame.draw.line(surf, (160,168,188), (rx1,ry1),(rx2,ry2),
                                     max(1, 3-blur))
        # Rotor disc hint
        disc = pygame.Surface((rotor_len*2+4, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(disc, (150,158,180,18), (0,0,rotor_len*2+4,12))
        surf.blit(disc, (rotor_cx-rotor_len-2, rotor_cy-6))

        # ── Gun pod (underside) ───────────────────────────────────────────────
        gun_x = cx2 + f*10
        pygame.draw.rect(surf, (30,34,44), (gun_x-4, base_y+12, 18, 6), border_radius=2)
        pygame.draw.line(surf, (22,26,34), (gun_x+14, base_y+14), (gun_x+24, base_y+14), 3)

        # ── HP bar ────────────────────────────────────────────────────────────
        bw=80; bx4=cx2-bw//2; by4=int(self.y)-18
        pygame.draw.rect(surf,(10,10,10),(bx4,by4,bw,7),border_radius=3)
        hp_r=self.hp/self.MAX_HP
        hc=(50,200,80) if hp_r>0.5 else (220,190,50) if hp_r>0.25 else (220,40,40)
        if hp_r>0:
            pygame.draw.rect(surf,hc,(bx4,by4,int(bw*hp_r),7),border_radius=3)
            sh2=pygame.Surface((int(bw*hp_r),3),pygame.SRCALPHA)
            sh2.fill((255,255,255,40)); surf.blit(sh2,(bx4,by4))
        pygame.draw.rect(surf,(70,70,80),(bx4,by4,bw,7),1,border_radius=3)
        lf=pygame.font.SysFont("consolas",9,bold=True)
        surf.blit(lf.render("HELI",True,(180,200,220)),(cx2-10,by4-12))

class Jet:
    W=80;H=22;SPEED=6;SHOOT_RATE=2000;is_air=True
    def __init__(self,x):
        diff=get_diff()
        self.x=float(x);self.y=float(GROUND_Y-260-random.randint(0,80))
        self.MAX_HP=int(120*diff["enemy_hp_mult"]);self.hp=self.MAX_HP
        self.alive=True;self.facing=-1;self.last_shot=0;self.vx=-self.SPEED
        self.dive_timer=random.randint(200,400);self.diving=False
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    def update(self,player,bullets):
        self.dive_timer-=1
        if self.dive_timer<=0 and not self.diving: self.diving=True;self.dive_timer=80
        if self.diving:
            self.y=min(self.y+4,GROUND_Y-150)
            if self.dive_timer<=0: self.diving=False;self.dive_timer=random.randint(150,300)
        else: self.y=max(self.y-2,GROUND_Y-300)
        self.x+=self.vx
        if self.x<-200 or self.x>WORLD_WIDTH+200: self.vx*=-1;self.facing*=-1
        now=pygame.time.get_ticks();dist=abs(player.x-self.x)
        if now-self.last_shot>=self.SHOOT_RATE and dist<600:
            self.last_shot=now;SFX.play(SFX.shoot_rifle)
            ox=self.rect.centerx;oy=self.rect.centery
            dmg=int(14*get_diff()["enemy_dmg_mult"])
            for off in [-0.1,0,0.1]:
                angle=math.atan2(player.rect.centery-oy,player.rect.centerx-ox)+off
                bullets.append(Bullet(ox,oy,math.cos(angle)*15,math.sin(angle)*15,dmg,(255,200,50)))
        if random.random()<0.6: PARTICLES.spawn_smoke(int(self.x)+(0 if self.vx<0 else self.W),int(self.y)+10)
    def take_damage(self,amount,is_rocket=False):
        dmg=amount if is_rocket else max(1,amount//5)
        self.hp-=dmg;SFX.play(SFX.hit_enemy);PARTICLES.spawn_sparks(self.rect.centerx,self.rect.centery,6)
        if self.hp<=0:
            self.alive=False;PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=1.5)
            SFX.play(SFX.big_explosion)
    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        cx2 = sx + self.W // 2
        cy2 = int(self.y) + self.H // 2
        f   = 1 if self.vx > 0 else -1
        t   = pygame.time.get_ticks()

        body_col  = (62, 72, 88)
        body_hi   = (88, 100, 118)
        body_shad = (42, 50, 62)
        canopy_col= (50, 150, 195)

        # ── Afterburner cone (behind engine) ──────────────────────────────────
        nozzle_x = cx2 - f * 38
        for fi in range(7):
            ratio = fi / 6
            fl    = int((16 + ratio * 28) + random.randint(0,8))
            fc    = [(255,248,80),(255,195,30),(255,120,10),
                     (220,60,8),(160,35,5),(100,20,2),(50,10,0)][fi]
            fr    = max(1, int((7 - fi) * 1.0))
            end_x = nozzle_x - f * fl
            fs2   = pygame.Surface((fr*2+2, fr*2+2), pygame.SRCALPHA)
            pygame.draw.circle(fs2, (*fc, 220-fi*28), (fr+1,fr+1), fr)
            surf.blit(fs2, (end_x-fr-1, cy2-fr-1))

        # ── Main fuselage ─────────────────────────────────────────────────────
        # Nose cone (pointed)
        nose_x  = cx2 + f * 40
        fuse_pts = [(cx2 - f*38, cy2-6),
                    (cx2 - f*38, cy2+6),
                    (cx2 + f*20, cy2+7),
                    (nose_x,     cy2  ),
                    (cx2 + f*20, cy2-7)]
        pygame.draw.polygon(surf, body_col,  fuse_pts)
        pygame.draw.polygon(surf, body_hi,   fuse_pts, 1)

        # Fuselage highlight (top spine)
        pygame.draw.line(surf, body_hi,
                         (cx2 - f*34, cy2-5), (cx2 + f*22, cy2-5), 2)

        # Intake (on side/belly)
        intake_x = cx2 - f*10
        intake_col = (30,36,46)
        pygame.draw.ellipse(surf, intake_col,    (intake_x-6, cy2+2, 14, 8))
        pygame.draw.ellipse(surf, (22,28,38),    (intake_x-4, cy2+4,  8, 5))
        pygame.draw.ellipse(surf, (50,140,180),  (intake_x-2, cy2+5,  4, 3))  # intake glow

        # ── Cockpit canopy ────────────────────────────────────────────────────
        cock_x = cx2 + f * 18
        pygame.draw.ellipse(surf, canopy_col,    (cock_x-10, cy2-9, 22, 12))
        pygame.draw.ellipse(surf, body_col,      (cock_x-10, cy2-9, 22, 12), 1)
        # Canopy framing lines
        pygame.draw.line(surf, body_shad, (cock_x, cy2-9), (cock_x, cy2+3), 1)
        # Glint
        pygame.draw.ellipse(surf, (200,238,255), (cock_x-6, cy2-8, 9, 5))

        # ── Wings (swept delta-style) ─────────────────────────────────────────
        wing_root_x = cx2 - f*8
        wing_root_y = cy2
        # Lower wing
        pygame.draw.polygon(surf, body_shad,
                            [(wing_root_x,      wing_root_y+4),
                             (wing_root_x-f*32, wing_root_y+22),
                             (wing_root_x+f*14, wing_root_y+22),
                             (wing_root_x+f*10, wing_root_y+4)])
        pygame.draw.polygon(surf, body_col,
                            [(wing_root_x,      wing_root_y-4),
                             (wing_root_x-f*32, wing_root_y-20),
                             (wing_root_x+f*14, wing_root_y-20),
                             (wing_root_x+f*10, wing_root_y-4)])
        # Wing leading-edge highlight
        pygame.draw.line(surf, body_hi,
                         (wing_root_x, wing_root_y-4),
                         (wing_root_x-f*30, wing_root_y-19), 2)

        # ── Tail fins ─────────────────────────────────────────────────────────
        tail_x = cx2 - f*32
        # Vertical stab
        pygame.draw.polygon(surf, body_col,
                            [(tail_x,       cy2+4),
                             (tail_x+f*4,   cy2-18),
                             (tail_x+f*14,  cy2+4)])
        pygame.draw.polygon(surf, body_hi,
                            [(tail_x,       cy2+4),
                             (tail_x+f*4,   cy2-18),
                             (tail_x+f*10,  cy2+4)], 1)
        # Horizontal stab
        pygame.draw.polygon(surf, body_shad,
                            [(tail_x,       cy2+4),
                             (tail_x+f*4,   cy2+14),
                             (tail_x+f*18,  cy2+4)])

        # ── Nav lights ────────────────────────────────────────────────────────
        nl_blink = (t // 500) % 2 == 0
        # Wingtip lights
        for nlx, nlcol in ((cx2-f*28, (255,30,30)), (cx2-f*28, (30,255,60))):
            if nl_blink:
                nls = pygame.Surface((8,8), pygame.SRCALPHA)
                pygame.draw.circle(nls, (*nlcol, 180), (4,4), 4)
                surf.blit(nls, (nlx-4, cy2+16))

        # ── Weapons pylons (two under wing) ───────────────────────────────────
        for wp_off in (6, 18):
            pylon_x = cx2 - f * wp_off
            pygame.draw.rect(surf, (48,54,66), (pylon_x-2, cy2+8, 4, 6))
            # Missile shape
            pygame.draw.rect(surf, (180,80,20), (pylon_x-1, cy2+14, 3, 8), border_radius=1)
            pygame.draw.polygon(surf, (220,120,40),
                                [(pylon_x-1,cy2+14),(pylon_x+2,cy2+14),(pylon_x,cy2+10)])

        # ── HP bar ────────────────────────────────────────────────────────────
        bw=60; bx5=cx2-bw//2; by5=int(self.y)-16
        pygame.draw.rect(surf,(10,10,10),(bx5,by5,bw,5),border_radius=2)
        hp_r=self.hp/self.MAX_HP
        hc=(50,200,80) if hp_r>0.5 else (220,40,40)
        if hp_r>0:
            pygame.draw.rect(surf,hc,(bx5,by5,int(bw*hp_r),5),border_radius=2)
        pygame.draw.rect(surf,(70,70,80),(bx5,by5,bw,5),1,border_radius=2)
        lf=pygame.font.SysFont("consolas",9,bold=True)
        surf.blit(lf.render("JET",True,(180,200,220)),(cx2-8,by5-12))

class ShieldSoldier(Enemy):
    """
    Ground enemy with a breakable energy shield.
    - Shield absorbs ALL bullet damage until depleted.
    - Rockets and grenades deal 50% through shield.
    - Glows blue while shielded.
    """
    W = 32; H = 54; is_air = False

    def __init__(self, x, y, hp=80, speed=2.0, shoot_rate=1800):
        super().__init__(x, y, hp, speed, shoot_rate)
        diff = get_diff()
        self.shield_hp     = int(60 * diff["enemy_hp_mult"])
        self.max_shield_hp = self.shield_hp
        self.shield_broken = False
        self.shield_regen_timer = 0   # frames until regen starts
        self.shield_regen_rate  = 0.3 # hp per frame after delay

    def take_damage(self, amount, is_rocket=False, is_explosion=False):
        SFX.play(SFX.hit_enemy)
        if not self.shield_broken and self.shield_hp > 0:
            # Rockets/explosions punch through at 50%
            bleed = amount * 0.5 if (is_rocket or is_explosion) else 0
            self.shield_hp -= amount
            PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 10)
            if self.shield_hp <= 0:
                self.shield_hp    = 0
                self.shield_broken = True
                self.shield_regen_timer = 240  # 4 seconds
                SFX.play(SFX.big_explosion)
                PARTICLES.spawn_explosion(self.rect.centerx, self.rect.centery, scale=0.6)
            if bleed > 0:
                self.hp -= int(bleed)
        else:
            self.hp -= amount
            PARTICLES.spawn_blood(self.rect.centerx, self.rect.centery)

        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_death_explosion(self.rect.centerx, self.rect.centery)

    def update(self, player, bullets, grenades_list):
        super().update(player, bullets, grenades_list)
        # Shield regeneration
        if self.shield_broken:
            if self.shield_regen_timer > 0:
                self.shield_regen_timer -= 1
            else:
                self.shield_hp = min(self.max_shield_hp,
                                     self.shield_hp + self.shield_regen_rate)
                if self.shield_hp >= self.max_shield_hp:
                    self.shield_broken = False

    def draw(self, surf, cam_x=0):
        super().draw(surf, cam_x)
        sx  = int(self.x) - cam_x
        cx  = sx + self.W // 2
        cy  = int(self.y)
        # Shield bubble
        if not self.shield_broken and self.shield_hp > 0:
            ratio  = self.shield_hp / self.max_shield_hp
            pulse  = abs(math.sin(pygame.time.get_ticks() * 0.006)) * 20
            radius = 36
            s_surf = pygame.Surface((radius*2+4, radius*2+4), pygame.SRCALPHA)
            pygame.draw.circle(s_surf,
                               (80, 160, 255, int(30 + pulse * ratio)),
                               (radius+2, radius+2), radius)
            pygame.draw.circle(s_surf,
                               (140, 210, 255, int(80 * ratio)),
                               (radius+2, radius+2), radius, 2)
            surf.blit(s_surf, (cx - radius - 2, cy + self.H//2 - radius - 2))
            # Shield HP bar (thin, blue, above normal HP bar)
            bw = 40; bx2 = cx - bw//2; by2 = cy - 18
            pygame.draw.rect(surf, (10, 20, 50), (bx2, by2, bw, 4))
            pygame.draw.rect(surf, SHIELD_COL, (bx2, by2, int(bw * ratio), 4))
        elif self.shield_broken and self.shield_hp > 0:
            # Regen indicator — thin bar
            ratio = self.shield_hp / self.max_shield_hp
            bw = 40; bx2 = cx - bw//2; by2 = cy - 18
            pygame.draw.rect(surf, (10, 20, 50), (bx2, by2, bw, 4))
            pygame.draw.rect(surf, (40, 80, 140), (bx2, by2, int(bw * ratio), 4))


# ─────────────────────────────────────────────────────────────────────────────

class SniperEnemy(Enemy):
    """
    Long-range stationary sniper.
    - Shows a red laser dot 1.2 sec before firing (warning).
    - Single high-damage shot, long reload.
    - Prefers elevated platforms, retreats if player too close.
    """
    W = 28; H = 50; is_air = False
    DANGER_RANGE  = 800   # max shoot distance
    RETREAT_RANGE = 180   # runs away if player closer than this

    def __init__(self, x, y, hp=55, speed=1.5, shoot_rate=2800):
        super().__init__(x, y, hp, speed, shoot_rate)
        self.charging      = False
        self.charge_timer  = 0
        self.CHARGE_FRAMES = 72   # 1.2 sec warning
        self.laser_target  = (0, 0)

    def update(self, player, bullets, grenades_list):
        # Override AI to sniper behaviour
        self.vy = min(self.vy + 0.7, 18); self.y += self.vy; self.on_ground = False
        for plat in current_platforms:
            r = self.rect
            if r.colliderect(plat) and self.vy >= 0:
                if r.bottom - self.vy <= plat.top + abs(self.vy) + 2:
                    self.y = plat.top - self.H; self.vy = 0; self.on_ground = True

        dist = math.hypot(player.x - self.x, player.y - self.y)
        self.facing = 1 if player.x > self.x else -1

        # Retreat if too close
        if dist < self.RETREAT_RANGE:
            retreat_x = self.x - self.facing * 120
            self._move_toward(retreat_x, self.speed * 1.4)
            self._try_jump(retreat_x)
            self.charging = False; self.charge_timer = 0
            return

        # Charge shot
        now = pygame.time.get_ticks()
        if dist < self.DANGER_RANGE:
            if not self.charging:
                if now - self.last_shot >= self.shoot_rate:
                    self.charging     = True
                    self.charge_timer = self.CHARGE_FRAMES
                    self.laser_target = (player.rect.centerx, player.rect.centery)
            else:
                self.charge_timer -= 1
                # Update aim (track player during charge but freeze last 20 frames)
                if self.charge_timer > 20:
                    self.laser_target = (player.rect.centerx, player.rect.centery)
                if self.charge_timer <= 0:
                    # FIRE
                    self.charging  = False
                    self.last_shot = now
                    ox = self.rect.centerx; oy = self.rect.centery
                    tx, ty = self.laser_target
                    d = math.hypot(tx - ox, ty - oy) or 1
                    dmg = int(55 * get_diff()["enemy_dmg_mult"])
                    bullets.append(Bullet(ox, oy,
                                          (tx-ox)/d*22, (ty-oy)/d*22,
                                          dmg, SNIPER_COL, is_sniper=True))
                    SFX.play(SFX.shoot_sniper)
                    PARTICLES.spawn_muzzle_flash(ox + self.facing*16, oy, self.facing)
        else:
            self.charging = False
            # Slow patrol toward player
            self._move_toward(player.x, self.speed * 0.5)

    def draw(self, surf, cam_x=0):
        super().draw(surf, cam_x)
        # Draw laser sight when charging
        if self.charging and self.charge_timer > 0:
            cx2 = self.rect.centerx - cam_x
            cy2 = self.rect.centery
            tx, ty = self.laser_target
            sx2 = tx - cam_x
            # Laser line
            charge_ratio = 1.0 - self.charge_timer / 72
            alpha = int(80 + 160 * charge_ratio)
            laser_surf = pygame.Surface((abs(sx2 - cx2) + 4, abs(ty - cy2) + 4), pygame.SRCALPHA)
            ox3 = min(cx2, sx2); oy3 = min(cy2, ty)
            pygame.draw.line(laser_surf, (255, 30, 30, alpha),
                             (cx2 - ox3 + 2, cy2 - oy3 + 2),
                             (sx2 - ox3 + 2, ty - oy3 + 2), 1)
            surf.blit(laser_surf, (ox3 - 2, oy3 - 2))
            # Dot at target
            dot_r = int(3 + charge_ratio * 5)
            ds = pygame.Surface((dot_r*2+2, dot_r*2+2), pygame.SRCALPHA)
            pygame.draw.circle(ds, (255, 30, 30, alpha), (dot_r+1, dot_r+1), dot_r)
            surf.blit(ds, (sx2 - dot_r - 1, ty - dot_r - 1))
            # Crosshair tick marks when nearly fired
            if self.charge_timer < 20:
                for ang in [0, math.pi/2, math.pi, 3*math.pi/2]:
                    ex3 = int(sx2 + math.cos(ang) * 10)
                    ey3 = int(ty  + math.sin(ang) * 10)
                    pygame.draw.line(surf, (255, 80, 80),
                                     (sx2, ty), (ex3, ey3), 1)


# ─────────────────────────────────────────────────────────────────────────────

class KamikazeDrone(Drone):
    """
    Suicide drone — charges directly at the player when close enough.
    Explodes on contact or when HP reaches 0.
    Visual: Sparking, accelerating dive.
    """
    W = 28; H = 18; is_air = True
    DIVE_RANGE   = 320
    DIVE_SPEED   = 11
    EXPLOSION_R  = 100
    EXPLOSION_DMG= 55

    def __init__(self, x):
        super().__init__(x)
        diff = get_diff()
        self.MAX_HP    = int(28 * diff["enemy_hp_mult"])
        self.hp        = self.MAX_HP
        self.diving    = False
        self.dive_vx   = 0.0
        self.dive_vy   = 0.0
        self.spark_timer = 0

    def update(self, player, bullets):
        dist = math.hypot(player.x - self.x, player.y - self.y)

        if not self.diving:
            # Normal patrol (inherited)
            super().update(player, bullets)
            if dist < self.DIVE_RANGE:
                # Begin dive
                self.diving = True
                dx = player.x - self.x; dy = player.y - self.y
                d  = math.hypot(dx, dy) or 1
                self.dive_vx = dx / d * self.DIVE_SPEED
                self.dive_vy = dy / d * self.DIVE_SPEED
        else:
            # Homing dive — continuously re-aim
            dx = player.x - self.x; dy = player.y - self.y
            d  = math.hypot(dx, dy) or 1
            target_vx = dx / d * self.DIVE_SPEED
            target_vy = dy / d * self.DIVE_SPEED
            self.dive_vx += (target_vx - self.dive_vx) * 0.12
            self.dive_vy += (target_vy - self.dive_vy) * 0.12
            self.x += self.dive_vx; self.y += self.dive_vy
            self.spark_timer += 1
            if self.spark_timer % 3 == 0:
                PARTICLES.spawn_sparks(self.x, self.y, 4)
            # Explode on contact
            if dist < 28:
                self._explode()

        # Out-of-bounds
        if self.x < -300 or self.x > WORLD_WIDTH + 300 or self.y > HEIGHT + 100:
            self.alive = False

    def _explode(self):
        self.alive = False
        SFX.play(SFX.big_explosion)
        PARTICLES.spawn_explosion(self.x, self.y, scale=1.2)
        LIGHTS.add_explosion_light(self.x, self.y, scale=2.0)

    def take_damage(self, amount, is_rocket=False):
        self.hp -= amount
        SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 6)
        if self.hp <= 0:
            self._explode()

    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        cx2 = sx + self.W // 2
        cy2 = int(self.y) + self.H // 2
        t   = pygame.time.get_ticks()

        # Diving trail
        if self.diving:
            for i in range(6):
                trail_x = int(cx2 - self.dive_vx * i * 0.6)
                trail_y = int(cy2 - self.dive_vy * i * 0.6)
                ta = max(0, 160 - i * 28)
                ts = pygame.Surface((10, 10), pygame.SRCALPHA)
                pygame.draw.circle(ts, (255, 80, 20, ta), (5, 5), 5 - i // 2)
                surf.blit(ts, (trail_x - 5, trail_y - 5))

        # Body — hexagonal industrial frame
        body_col = (185, 55, 18) if self.diving else (58, 62, 88)
        body_hi  = (220, 80, 30) if self.diving else (78, 84, 110)
        pygame.draw.rect(surf, body_col, (cx2 - 11, cy2 - 7, 22, 14), border_radius=3)
        pygame.draw.rect(surf, body_hi,  (cx2 - 11, cy2 - 7, 22,  4), border_radius=3)
        # Central hex rivet pattern
        pygame.draw.line(surf, (max(0,body_col[0]-30), max(0,body_col[1]-20), max(0,body_col[2]-15)),
                         (cx2 - 8, cy2), (cx2 + 8, cy2), 1)

        # Explosive warhead nose (front-facing based on dive direction)
        if self.diving:
            nose_dir = math.atan2(self.dive_vy, self.dive_vx) if (abs(self.dive_vx)+abs(self.dive_vy)) > 0.1 else math.pi/2
            for ni in range(4):
                nang = nose_dir + (ni - 1.5) * 0.3
                nx   = int(cx2 + math.cos(nang) * 14)
                ny   = int(cy2 + math.sin(nang) * 14)
                pygame.draw.circle(surf, (255, 120, 20), (nx, ny), 3)
            # Danger stripes on body
            for si in range(3):
                stripe_x = cx2 - 8 + si * 6
                sc = (255, 200, 0) if si % 2 == 0 else body_col
                pygame.draw.rect(surf, sc, (stripe_x, cy2 - 7, 5, 14))
        else:
            # Sensor cluster underside
            pygame.draw.circle(surf, (38, 42, 58), (cx2, cy2 + 8), 5)
            pygame.draw.circle(surf, (80, 200, 220), (cx2, cy2 + 8), 3)

        # Four arms + rotors
        arm_dirs = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
        rotor_spd = t * 0.22
        arm_len = 14
        for dx4, dy4 in arm_dirs:
            ax = cx2 + dx4 * arm_len
            ay = cy2 + dy4 * arm_len
            # Carbon-look arm tube
            pygame.draw.line(surf, (42, 44, 60), (cx2, cy2), (ax, ay), 3)
            pygame.draw.line(surf, (62, 66, 85), (cx2, cy2), (ax, ay), 1)
            # Motor housing
            pygame.draw.circle(surf, (32, 34, 48), (ax, ay), 5)
            pygame.draw.circle(surf, (52, 56, 72), (ax, ay), 3)
            # Rotor blur
            for bk in range(2):
                ba = rotor_spd * dx4 * dy4 + bk * math.pi
                rotor_r = 12
                for blur in range(3):
                    ba2  = ba + blur * 0.2
                    bx1r = int(ax + math.cos(ba2) * rotor_r)
                    by1r = int(ay + math.sin(ba2) * rotor_r * 0.28)
                    bx2r = int(ax - math.cos(ba2) * rotor_r)
                    by2r = int(ay - math.sin(ba2) * rotor_r * 0.28)
                    a_rotor = max(0, 170 - blur * 55)
                    if a_rotor > 0:
                        pygame.draw.line(surf, (155, 162, 182),
                                         (bx1r, by1r), (bx2r, by2r), max(1, 2 - blur))

        # LEDs — fast blink when diving, slow otherwise
        blink_rate = 60 if self.diving else 280
        blink_on   = (t // blink_rate) % 2 == 0
        led_col    = (255, 20, 20) if blink_on else (60, 8, 8)
        pygame.draw.circle(surf, led_col, (cx2 - 9, cy2 - 5), 3)
        if blink_on:
            gs_led = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(gs_led, (255, 40, 40, 100), (6, 6), 6)
            surf.blit(gs_led, (cx2 - 15, cy2 - 11))

        # Sparks when diving
        if self.diving and self.spark_timer % 4 == 0:
            for _ in range(3):
                ang5   = random.uniform(0, 6.28)
                sp5    = random.uniform(2, 7)
                PARTICLES.spawn_sparks(self.x, self.y, 4)

        # HP bar
        bw3 = 30; bx3 = cx2 - bw3 // 2; by3 = int(self.y) - 12
        pygame.draw.rect(surf, (10, 10, 14), (bx3, by3, bw3, 4))
        hp_r3 = self.hp / self.MAX_HP
        pygame.draw.rect(surf, RED if hp_r3 < 0.4 else (220, 80, 20),
                         (bx3, by3, int(bw3 * hp_r3), 4))
        if self.diving:
            lf3 = pygame.font.SysFont("consolas", 8, bold=True)
            lt3 = lf3.render("KAMIKAZE", True, (255, 80, 20))
            surf.blit(lt3, (cx2 - lt3.get_width() // 2, by3 - 10))


# ─────────────────────────────────────────────────────────────────────────────

class HeavyGunner(Enemy):
    """
    Slow, heavily armoured ground enemy.
    - Very high HP, reduced by 60% from non-explosive weapons.
    - Fires 5-bullet burst, short cooldown.
    - Stomps ground when player is very close, causing shockwave stun.
    - Has a helmet that must be shot off first (reduces damage taken).
    """
    W = 38; H = 62; is_air = False
    STOMP_RANGE  = 100
    STOMP_CD     = 240   # 4 sec

    def __init__(self, x, y, hp=220, speed=1.4, shoot_rate=900):
        super().__init__(x, y, hp, speed, shoot_rate)
        diff = get_diff()
        self.max_hp     = int(hp * diff["enemy_hp_mult"])
        self.hp         = self.max_hp
        self.helmet_on  = True
        self.helmet_hp  = int(60 * diff["enemy_hp_mult"])
        self.stomp_cd   = 0
        self.stomp_anim = 0
        self.burst_count= 0
        self.burst_cd   = 0

    def take_damage(self, amount, is_rocket=False, is_explosion=False):
        SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 5)
        # Helmet absorbs first
        if self.helmet_on:
            self.helmet_hp -= amount
            if self.helmet_hp <= 0:
                self.helmet_on = False
                SFX.play(SFX.explosion)
                PARTICLES.spawn_explosion(self.rect.centerx, self.rect.top, scale=0.4)
            return   # no HP damage while helmet intact
        # Heavy armour: only 40% dmg from bullets, full from explosives
        real_dmg = amount if (is_rocket or is_explosion) else max(1, int(amount * 0.4))
        self.hp -= real_dmg
        PARTICLES.spawn_blood(self.rect.centerx, self.rect.centery, 5)
        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_death_explosion(self.rect.centerx, self.rect.centery)

    def update(self, player, bullets, grenades_list):
        # Gravity / platform
        self.vy = min(self.vy + 0.7, 18); self.y += self.vy; self.on_ground = False
        for plat in current_platforms:
            r = self.rect
            if r.colliderect(plat) and self.vy >= 0:
                if r.bottom - self.vy <= plat.top + abs(self.vy) + 2:
                    self.y = plat.top - self.H; self.vy = 0; self.on_ground = True

        dist = math.hypot(player.x - self.x, player.y - self.y)
        self.facing = 1 if player.x > self.x else -1
        if self.stomp_cd > 0: self.stomp_cd -= 1
        if self.stomp_anim > 0: self.stomp_anim -= 1
        if self.burst_cd > 0: self.burst_cd -= 1

        # Stomp
        if dist < self.STOMP_RANGE and self.on_ground and self.stomp_cd == 0:
            self.stomp_cd  = self.STOMP_CD
            self.stomp_anim= 20
            SFX.play(SFX.big_explosion)
            PARTICLES.spawn_explosion(self.rect.centerx, self.y + self.H, scale=0.5)
            # Player gets stunned if on ground nearby
            if abs(player.y + player.H - (self.y + self.H)) < 20:
                player.stun_timer = 90  # set on player below

        # Slow march
        if dist > 120:
            self._move_toward(player.x, self.speed)

        # Burst fire
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_rate and dist < 550:
            self.last_shot = now; self.burst_count = 5; self.burst_cd = 0

        if self.burst_count > 0 and self.burst_cd <= 0:
            self.burst_count -= 1; self.burst_cd = 7
            ox = self.rect.centerx; oy = self.rect.centery
            angle = math.atan2(player.rect.centery - oy,
                               player.rect.centerx - ox) + random.uniform(-0.18, 0.18)
            dmg = int(9 * get_diff()["enemy_dmg_mult"])
            bullets.append(Bullet(ox, oy, math.cos(angle)*12, math.sin(angle)*12, dmg, ORANGE))
            SFX.play(SFX.shoot_rifle)

        self.x = max(0, min(WORLD_WIDTH - self.W, self.x))

    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        cx2 = sx + self.W // 2
        cy2 = int(self.y)
        f   = self.facing
        t   = pygame.time.get_ticks()

        # ── Stomp shockwave ──────────────────────────────────────────────────
        if self.stomp_anim > 0:
            r2 = int((20 - self.stomp_anim) * 9)
            sw = pygame.Surface((r2*2+4, r2*2+4), pygame.SRCALPHA)
            ring_a = int(self.stomp_anim * 12)
            pygame.draw.circle(sw, (255, 200, 50, ring_a), (r2+2, r2+2), r2, 4)
            pygame.draw.circle(sw, (255, 140, 20, ring_a//2), (r2+2, r2+2), max(1,r2-6), 2)
            surf.blit(sw, (cx2-r2-2, cy2+self.H-r2-2))

        # ── Ground shadow ────────────────────────────────────────────────────
        sh = pygame.Surface((self.W+14, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,65), (0,0,self.W+14,8))
        surf.blit(sh, (cx2-self.W//2-7, cy2+self.H-3))

        # Walk animation
        lo = [0, 9, 0, -9][self.walk_frame]

        # ── BOOTS — heavy steel-toed ──────────────────────────────────────────
        boot_col  = (20, 16, 10)
        boot_sole = (32, 26, 16)
        # Left boot
        pygame.draw.rect(surf, boot_col,  (cx2-12, cy2+54+lo, 14, 10), border_radius=2)
        pygame.draw.rect(surf, boot_sole, (cx2-14, cy2+61+lo, 18,  4), border_radius=2)
        # Right boot
        pygame.draw.rect(surf, boot_col,  (cx2+0,  cy2+54-lo, 14, 10), border_radius=2)
        pygame.draw.rect(surf, boot_sole, (cx2-2,  cy2+61-lo, 18,  4), border_radius=2)
        # Steel toecap
        pygame.draw.rect(surf, (55, 55, 62), (cx2-13, cy2+54+lo, 6, 8), border_radius=1)
        pygame.draw.rect(surf, (55, 55, 62), (cx2+8,  cy2+54-lo, 6, 8), border_radius=1)

        # ── LEGS — armoured greaves ───────────────────────────────────────────
        trouser_col = (90, 58, 36)
        trouser_hi  = (115, 75, 48)
        trouser_dk  = (62, 38, 22)
        # Left leg
        pygame.draw.rect(surf, trouser_col, (cx2-12, cy2+38, 12, 17+lo), border_radius=2)
        pygame.draw.rect(surf, trouser_hi,  (cx2-12, cy2+38,  4, 17+lo))
        # Right leg
        pygame.draw.rect(surf, trouser_col, (cx2+1,  cy2+38, 12, 17-lo), border_radius=2)
        pygame.draw.rect(surf, trouser_hi,  (cx2+1,  cy2+38,  4, 17-lo))
        # Knee pad armour plates
        pygame.draw.rect(surf, (48, 48, 58), (cx2-13, cy2+42+lo//2, 13, 9), border_radius=2)
        pygame.draw.rect(surf, (68, 68, 80), (cx2-13, cy2+42+lo//2, 13, 3), border_radius=2)
        pygame.draw.rect(surf, (48, 48, 58), (cx2+1,  cy2+42-lo//2, 13, 9), border_radius=2)
        pygame.draw.rect(surf, (68, 68, 80), (cx2+1,  cy2+42-lo//2, 13, 3), border_radius=2)
        # Belt / cummerbund
        pygame.draw.rect(surf, (35, 28, 18), (cx2-13, cy2+36, 26, 5))
        pygame.draw.rect(surf, (58, 46, 28), (cx2-3,  cy2+37,  6, 3))  # buckle

        # ── BODY — heavy plate carrier ────────────────────────────────────────
        vest_col  = (105, 68, 40)
        vest_hi   = (135, 90, 55)
        vest_dk   = (72, 44, 26)
        plate_col = (82, 52, 30)
        plate_hi  = (100, 66, 40)

        # Main torso (wider than normal enemy)
        pygame.draw.rect(surf, vest_col, (cx2-15, cy2+20, 30, 20), border_radius=3)
        pygame.draw.rect(surf, vest_hi,  (cx2-15, cy2+20, 30,  5), border_radius=3)
        pygame.draw.rect(surf, vest_dk,  (cx2-15, cy2+36, 30,  4))

        # Front SAPI plate (thick ceramic)
        pygame.draw.rect(surf, plate_col, (cx2-11, cy2+22, 22, 16), border_radius=2)
        pygame.draw.rect(surf, plate_hi,  (cx2-11, cy2+22, 22,  4), border_radius=2)
        # Plate bolt rivets
        for rv_x, rv_y in [(cx2-9, cy2+36), (cx2+6, cy2+36),
                            (cx2-9, cy2+23), (cx2+6, cy2+23)]:
            pygame.draw.circle(surf, vest_dk, (rv_x, rv_y), 2)
            pygame.draw.circle(surf, vest_hi,  (rv_x, rv_y), 1)

        # Molle webbing strips
        for row_y in range(cy2+26, cy2+36, 3):
            pygame.draw.line(surf, vest_dk, (cx2-10, row_y), (cx2+10, row_y), 1)

        # Heavy shoulder pauldrons
        pygame.draw.rect(surf, vest_col, (cx2-22, cy2+18, 10, 16), border_radius=3)
        pygame.draw.rect(surf, vest_hi,  (cx2-22, cy2+18,  10, 4), border_radius=3)
        pygame.draw.rect(surf, vest_col, (cx2+12, cy2+18, 10, 16), border_radius=3)
        pygame.draw.rect(surf, vest_hi,  (cx2+12, cy2+18, 10,  4), border_radius=3)
        # Pauldron plates
        pygame.draw.rect(surf, plate_col, (cx2-21, cy2+20, 8, 10), border_radius=2)
        pygame.draw.rect(surf, plate_col, (cx2+13, cy2+20, 8, 10), border_radius=2)

        # Side utility pouches
        pygame.draw.rect(surf, vest_dk, (cx2-19, cy2+28,  6, 9), border_radius=1)
        pygame.draw.rect(surf, vest_hi,  (cx2-19, cy2+28,  6, 2))
        pygame.draw.rect(surf, vest_dk, (cx2+13, cy2+28,  6, 9), border_radius=1)
        pygame.draw.rect(surf, vest_hi,  (cx2+13, cy2+28,  6, 2))

        # ── NECK ─────────────────────────────────────────────────────────────
        pygame.draw.rect(surf, (168, 118, 82), (cx2-4, cy2+16, 8, 6))

        # ── HEAD ─────────────────────────────────────────────────────────────
        skin_col  = (172, 122, 84)
        skin_shad = (135, 92, 60)
        pygame.draw.circle(surf, skin_col, (cx2, cy2+10), 13)
        pygame.draw.circle(surf, skin_shad, (cx2+f*4, cy2+11), 7)
        pygame.draw.ellipse(surf, skin_col, (cx2-f*14, cy2+5, 6, 9))
        eye_x = cx2 + f*5
        pygame.draw.circle(surf, (235, 228, 215), (eye_x, cy2+8), 2)
        pygame.draw.circle(surf, (22, 16, 10), (eye_x, cy2+8), 1)
        # Gritted teeth / grimace
        pygame.draw.line(surf, (115, 75, 52), (eye_x-4, cy2+13), (eye_x+2, cy2+14), 1)

        # ── HELMET ────────────────────────────────────────────────────────────
        if self.helmet_on:
            helm_hp_ratio = max(0, self.helmet_hp / int(60 * get_diff()["enemy_hp_mult"]))
            # Helmet damage cracks when low
            helm_col_base = (55, 55, 70) if helm_hp_ratio > 0.4 else (42, 28, 28)
            helm_hi2      = (78, 78, 96) if helm_hp_ratio > 0.4 else (62, 38, 32)
            helm_dk2      = (35, 35, 48)

            # ACH dome
            pygame.draw.arc(surf, helm_col_base,
                            pygame.Rect(cx2-16, cy2-4, 32, 24), 0, math.pi, 0)
            pygame.draw.rect(surf, helm_col_base, (cx2-16, cy2+8, 32, 10))
            # Dome highlight arc
            pygame.draw.arc(surf, helm_hi2,
                            pygame.Rect(cx2-13, cy2-2, 16, 14), 0.4, math.pi-0.4, 3)
            # Brim
            pygame.draw.rect(surf, helm_dk2, (cx2-18, cy2+15, 36, 4), border_radius=1)
            # Suspension bumps
            pygame.draw.ellipse(surf, helm_dk2, (cx2-14, cy2+8,  7, 5))
            pygame.draw.ellipse(surf, helm_dk2, (cx2+7,  cy2+8,  7, 5))
            # Ear protection cups
            pygame.draw.ellipse(surf, helm_dk2, (cx2-20, cy2+4, 6, 10))
            pygame.draw.ellipse(surf, helm_dk2, (cx2+14, cy2+4, 6, 10))
            # Visor bar (ballistic visor)
            pygame.draw.rect(surf, (38, 42, 55), (cx2-14, cy2+2, 28, 8))
            pygame.draw.rect(surf, (52, 60, 75), (cx2-14, cy2+2, 28, 3))
            # Camo spots
            camo_r = random.Random(int(self.x)//55)
            for _ in range(5):
                csx2 = cx2 + camo_r.randint(-12, 12)
                csy2 = cy2 + camo_r.randint(-2, 12)
                pygame.draw.circle(surf, helm_dk2, (csx2, csy2), camo_r.randint(1, 3))
            # Damage cracks
            if helm_hp_ratio < 0.5:
                crack_r = random.Random(7)
                for _ in range(int((1-helm_hp_ratio)*6)):
                    crx = cx2 + crack_r.randint(-13, 13)
                    cry = cy2 + crack_r.randint(-2, 14)
                    pygame.draw.line(surf, (220, 80, 80),
                                     (crx, cry), (crx+crack_r.randint(-4,4), cry+crack_r.randint(-4,4)), 1)
            # Helmet HP indicator
            bw3 = 42; bx3 = cx2-bw3//2; by3 = cy2-22
            pygame.draw.rect(surf, (18, 18, 30), (bx3, by3, bw3, 5), border_radius=2)
            pygame.draw.rect(surf, (80,120,220), (bx3, by3, int(bw3*helm_hp_ratio), 5), border_radius=2)
            pygame.draw.rect(surf, (55, 65, 90), (bx3, by3, bw3, 5), 1, border_radius=2)
            hf3 = pygame.font.SysFont("consolas", 8, bold=True)
            ht4 = hf3.render("HELM", True, (80,120,220))
            surf.blit(ht4, (cx2-ht4.get_width()//2, by3-10))
        else:
            # Helmet blown off — scarred head, bandana
            pygame.draw.rect(surf, (140, 40, 40), (cx2-13, cy2-3, 26, 8))
            pygame.draw.circle(surf, (160, 50, 50), (cx2, cy2-2), 8)
            # Bandana knot
            pygame.draw.circle(surf, (180, 65, 65), (cx2+10, cy2-2), 4)
            # Scar mark
            pygame.draw.line(surf, (220, 100, 100), (cx2-5, cy2+2), (cx2+2, cy2+8), 1)

        # ── ARMS — powered exo-arm sleeves ────────────────────────────────────
        arm_col  = vest_col
        arm_plate= plate_col
        # Left arm
        pygame.draw.line(surf, arm_col, (cx2-15, cy2+22), (cx2-26, cy2+38), 7)
        pygame.draw.rect(surf, arm_plate, (cx2-30, cy2+28, 10, 12), border_radius=2)
        pygame.draw.rect(surf, plate_hi,  (cx2-30, cy2+28, 10,  3), border_radius=2)
        pygame.draw.circle(surf, (38, 28, 16), (cx2-26, cy2+40), 5)  # glove

        # Right gun arm
        gun_y3 = cy2 + 26 + int(math.sin(t*0.005)*2)
        pygame.draw.line(surf, arm_col, (cx2+15, cy2+22), (cx2+f*28, gun_y3), 8)
        pygame.draw.rect(surf, arm_plate, (cx2+f*18, gun_y3-6, 12, 12), border_radius=2)
        pygame.draw.circle(surf, (38, 28, 16), (cx2+f*28, gun_y3), 5)

        # ── MINIGUN / HEAVY MG ────────────────────────────────────────────────
        gun_base_x = cx2 + f * 24
        gun_base_y = gun_y3 - 4
        # Ammo box on back
        pygame.draw.rect(surf, (42, 36, 22), (cx2-f*8, cy2+26, f*(-16), 14))
        pygame.draw.rect(surf, (58, 50, 30), (cx2-f*8, cy2+26, f*(-16),  4))
        # Feed belt
        pygame.draw.line(surf, (180, 150, 40),
                         (cx2-f*8, cy2+32), (gun_base_x-f*6, gun_base_y+4), 2)
        # Gun receiver
        pygame.draw.rect(surf, (28, 28, 28),
                         (gun_base_x, gun_base_y-5, f*28 if f>0 else -f*28, 10))
        pygame.draw.rect(surf, (42, 42, 42),
                         (gun_base_x, gun_base_y-5, f*28 if f>0 else -f*28, 4))
        # Rotating barrel cluster (3 barrels)
        barrel_rot = (t // 40) % 3
        barrel_offsets = [-3, 0, 3]
        for bi, boff in enumerate(barrel_offsets):
            active_barrel = (bi == barrel_rot and self.burst_count > 0)
            b_col = (200, 80, 20) if active_barrel else (48, 48, 48)
            pygame.draw.line(surf, (38, 38, 38),
                             (gun_base_x + f*24, gun_base_y + boff),
                             (gun_base_x + f*46, gun_base_y + boff), 3)
            pygame.draw.line(surf, b_col,
                             (gun_base_x + f*24, gun_base_y + boff),
                             (gun_base_x + f*46, gun_base_y + boff), 1)
        # Muzzle brake
        pygame.draw.rect(surf, (22, 22, 22),
                         (gun_base_x+f*44, gun_base_y-6, f*6 if f>0 else -f*6, 12),
                         border_radius=1)
        # Muzzle flash when bursting
        if self.burst_count > 0:
            mf_a = random.randint(160, 240)
            mfs = pygame.Surface((22, 22), pygame.SRCALPHA)
            pygame.draw.circle(mfs, (255, 200, 60, mf_a), (11,11), 10)
            pygame.draw.circle(mfs, (255, 255, 180, mf_a), (11,11), 5)
            surf.blit(mfs, (gun_base_x+f*46-11, gun_base_y-11))
            PARTICLES.spawn_muzzle_flash(gun_base_x+f*50, gun_base_y, f)

        # ── HP BAR ────────────────────────────────────────────────────────────
        bw4 = 58; bx4 = cx2-bw4//2; by4 = cy2-14
        pygame.draw.rect(surf, (8, 8, 12), (bx4-1, by4-1, bw4+2, 9), border_radius=3)
        pygame.draw.rect(surf, DARK, (bx4, by4, bw4, 7), border_radius=3)
        hp_r4 = self.hp / self.max_hp
        hc4   = (50,210,80) if hp_r4>0.6 else (225,192,48) if hp_r4>0.3 else (218,38,38)
        if hp_r4 > 0:
            pygame.draw.rect(surf, hc4, (bx4, by4, int(bw4*hp_r4), 7), border_radius=3)
            sh5 = pygame.Surface((int(bw4*hp_r4), 3), pygame.SRCALPHA)
            sh5.fill((255,255,255,45)); surf.blit(sh5, (bx4, by4))
        pygame.draw.rect(surf, (65,65,80), (bx4, by4, bw4, 7), 1, border_radius=3)
        lf4 = pygame.font.SysFont("consolas", 9, bold=True)
        surf.blit(lf4.render("HEAVY", True, (255,175,45)), (cx2-14, by4-12))

class MechWalker:
    W = 52; H = 68; is_air = False
    SPEED = 1.2; SHOOT_RATE = 1800
    def __init__(self, x, y):
        diff = get_diff()
        self.x = float(x)
        # Spawn Y was calculated using Enemy.H=52 but Mech.H=68 — correct it:
        self.y = float(y) - (MechWalker.H - 52)
        self.vy = 0.0; self.on_ground = False
        self.MAX_HP = int(280 * diff["enemy_hp_mult"])
        self.hp = self.MAX_HP
        self.alive = True; self.facing = -1
        self.last_shot = 0; self.walk_frame = 0; self.walk_timer = 0
        self.stomp_cd = 0; self.stomp_anim = 0
        self.shoot_rate = int(self.SHOOT_RATE * diff["shoot_rate_mult"])
        self.stun_timer = 0
    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)
    def update(self, player, bullets, rockets):
        if self.stun_timer > 0: self.stun_timer -= 1; return
        self.vy = min(self.vy + 0.7, 18); self.y += self.vy; self.on_ground = False
        for plat in current_platforms:
            r = self.rect
            if r.colliderect(plat) and self.vy >= 0:
                if r.bottom - self.vy <= plat.top + abs(self.vy) + 2:
                    self.y = plat.top - self.H; self.vy = 0; self.on_ground = True
        dx = player.x - self.x; self.facing = 1 if dx > 0 else -1
        if abs(dx) > 80:
            self.x += self.SPEED * get_diff()["enemy_speed_mult"] * self.facing
            self.walk_timer += 1
            if self.walk_timer > 10: self.walk_frame = (self.walk_frame+1)%4; self.walk_timer = 0
        self.x = max(0, min(WORLD_WIDTH - self.W, self.x))
        if self.stomp_cd > 0: self.stomp_cd -= 1
        if self.stomp_anim > 0: self.stomp_anim -= 1
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist < 90 and self.on_ground and self.stomp_cd == 0:
            self.stomp_cd = 180; self.stomp_anim = 20
            SFX.play(SFX.big_explosion)
            PARTICLES.spawn_explosion(self.rect.centerx, self.y + self.H, scale=0.6)
            if abs(player.y + player.H - (self.y + self.H)) < 30:
                player.stun_timer = 60
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_rate and dist < 600:
            self.last_shot = now
            ox = self.rect.centerx; oy = self.rect.centery
            angle = math.atan2(player.rect.centery - oy, player.rect.centerx - ox)
            for off in (-0.12, 0, 0.12):
                dmg = int(14 * get_diff()["enemy_dmg_mult"])
                bullets.append(Bullet(ox, oy, math.cos(angle+off)*13, math.sin(angle+off)*13, dmg, ORANGE))
            SFX.play(SFX.shoot_rifle)
    def take_damage(self, amount, is_rocket=False):
        dmg = amount if is_rocket else max(1, int(amount * 0.5))
        self.hp -= dmg; SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 8)
        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_tank_death(self.rect.centerx, self.rect.centery)
            SFX.play(SFX.big_explosion)
    def draw(self, surf, cam_x=0):
        sx = int(self.x) - cam_x; cx = sx + self.W//2; cy = int(self.y)
        lo = [0,8,0,-8][self.walk_frame]
        # Stomp ring
        if self.stomp_anim > 0:
            r2 = int((20-self.stomp_anim)*8)
            sw = pygame.Surface((r2*2+4,r2*2+4),pygame.SRCALPHA)
            pygame.draw.circle(sw,(255,180,40,int(self.stomp_anim*10)),(r2+2,r2+2),r2,4)
            surf.blit(sw,(cx-r2-2,cy+self.H-r2-2))
        # Shadow
        sh = pygame.Surface((self.W+8,8),pygame.SRCALPHA)
        pygame.draw.ellipse(sh,(0,0,0,65),(0,0,self.W+8,8))
        surf.blit(sh,(cx-self.W//2-4,cy+self.H-3))
        # Legs (hydraulic pistons)
        leg_col=(52,58,72); piston_col=(80,90,105)
        pygame.draw.rect(surf,leg_col,(cx-18,cy+46+lo,12,22),border_radius=2)
        pygame.draw.rect(surf,leg_col,(cx+6, cy+46-lo,12,22),border_radius=2)
        pygame.draw.rect(surf,piston_col,(cx-16,cy+46+lo,8,10))
        pygame.draw.rect(surf,piston_col,(cx+8, cy+46-lo,8,10))
        # Feet
        pygame.draw.rect(surf,(35,38,48),(cx-22,cy+66+lo,22,10),border_radius=3)
        pygame.draw.rect(surf,(35,38,48),(cx+2, cy+66-lo,22,10),border_radius=3)
        # Torso
        torso_col=(45,52,68); torso_hi=(62,72,90)
        pygame.draw.rect(surf,torso_col,(cx-22,cy+16,44,32),border_radius=4)
        pygame.draw.rect(surf,torso_hi, (cx-22,cy+16,44,8), border_radius=4)
        pygame.draw.rect(surf,(32,38,50),(cx-22,cy+40,44,8))
        # Chest vents
        for vi in range(3):
            pygame.draw.rect(surf,(28,32,42),(cx-14+vi*10,cy+22,7,12),border_radius=1)
            pygame.draw.rect(surf,(55,65,85),(cx-14+vi*10,cy+22,7,3))
        # Shoulder cannons
        pygame.draw.rect(surf,(38,44,58),(cx-30,cy+16,12,20),border_radius=3)
        pygame.draw.rect(surf,(38,44,58),(cx+18,cy+16,12,20),border_radius=3)
        pygame.draw.rect(surf,(28,32,42),(cx-34,cy+22,8,8),border_radius=2)
        pygame.draw.rect(surf,(28,32,42),(cx+26,cy+22,8,8),border_radius=2)
        # Head
        pygame.draw.rect(surf,torso_col,(cx-14,cy,28,18),border_radius=4)
        pygame.draw.rect(surf,torso_hi, (cx-14,cy, 28,6), border_radius=4)
        # Visor
        visor_a = int(160+abs(math.sin(pygame.time.get_ticks()*0.007))*95)
        vs = pygame.Surface((24,8),pygame.SRCALPHA)
        pygame.draw.ellipse(vs,(255,80,20,visor_a),(0,0,24,8))
        surf.blit(vs,(cx-12,cy+5))
        # HP bar
        bw=50; bx2=cx-bw//2; by2=cy-14
        pygame.draw.rect(surf,(10,10,14),(bx2,by2,bw,6),border_radius=2)
        hp_r=self.hp/self.MAX_HP
        hc=(50,200,80) if hp_r>0.5 else (220,190,50) if hp_r>0.25 else (220,40,40)
        if hp_r>0: pygame.draw.rect(surf,hc,(bx2,by2,int(bw*hp_r),6),border_radius=2)
        pygame.draw.rect(surf,(55,65,80),(bx2,by2,bw,6),1,border_radius=2)
        lf=pygame.font.SysFont("consolas",9,bold=True)
        surf.blit(lf.render("MECH",True,(100,160,220)),(cx-10,by2-11))

class MortarSoldier(Enemy):
    """Stands far back and lobs slow arcing mortar shells at the player.
    Shell lands with a large explosion. Weak if you get close."""
    W = 34; H = 54; is_air = False
    MORTAR_RANGE_MIN = 280
    MORTAR_RANGE_MAX = 700
    MORTAR_RATE      = 3200   # ms between shots

    def __init__(self, x, y, hp=75, speed=1.2, shoot_rate=3200):
        super().__init__(x, y, hp=hp, speed=speed, shoot_rate=shoot_rate)
        self.mortar_timer = random.randint(1000, 2500)
        self.fire_anim    = 0   # recoil animation

    def update(self, player, bullets, grenades_list):
        # Gravity + platform
        self.vy = min(self.vy + 0.7, 18); self.y += self.vy; self.on_ground = False
        for plat in current_platforms:
            r = self.rect
            if r.colliderect(plat) and self.vy >= 0:
                if r.bottom - self.vy <= plat.top + abs(self.vy) + 2:
                    self.y = plat.top - self.H; self.vy = 0; self.on_ground = True

        dist = math.hypot(player.x - self.x, player.y - self.y)
        self.facing = 1 if player.x > self.x else -1
        if self.fire_anim > 0: self.fire_anim -= 1

        # Retreat if too close
        if dist < self.MORTAR_RANGE_MIN:
            self._move_toward(self.x - self.facing * 80, self.speed * 1.5)
        elif dist > self.MORTAR_RANGE_MAX:
            self._move_toward(player.x, self.speed * 0.8)

        # Fire mortar
        now = pygame.time.get_ticks()
        if (now - self.last_shot >= self.MORTAR_RATE and
                self.MORTAR_RANGE_MIN < dist < self.MORTAR_RANGE_MAX):
            self.last_shot = now
            self.fire_anim = 20
            # Calculate arc: initial velocity to land near player
            dx  = player.rect.centerx - self.rect.centerx
            dy  = player.rect.centery - self.rect.centery
            # Use fixed launch angle, scale speed by distance
            launch_speed = max(8, min(18, abs(dx) / 55))
            vx  = (dx / abs(dx + 0.01)) * launch_speed * 0.72
            vy  = -launch_speed * 1.15
            grenades_list.append(MortarShell(
                self.rect.centerx, self.rect.top,
                vx, vy))
            SFX.play(SFX.shoot_rocket)
            PARTICLES.spawn_muzzle_flash(self.rect.centerx, self.rect.top, self.facing)

        self.x = max(0, min(WORLD_WIDTH - self.W, self.x))

    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        cx  = sx + self.W // 2
        cy  = int(self.y)
        f   = self.facing
        t   = pygame.time.get_ticks()

        # Fire recoil offset
        rc = int(self.fire_anim * 0.6) if self.fire_anim > 0 else 0

        sh = pygame.Surface((self.W+4,6),pygame.SRCALPHA)
        pygame.draw.ellipse(sh,(0,0,0,55),(0,0,self.W+4,6))
        surf.blit(sh,(cx-self.W//2-2,cy+self.H-2))

        lo = [0,7,0,-7][self.walk_frame]
        boot_col=(28,22,14)
        pygame.draw.rect(surf,boot_col,(cx-9,cy+46+lo,10,8),border_radius=2)
        pygame.draw.rect(surf,boot_col,(cx+1,cy+46-lo,10,8),border_radius=2)

        bc = (68,58,42); bc_hi=(88,76,56); bc_dk=(48,40,28)
        pygame.draw.rect(surf,bc,(cx-9,cy+30,9,17+lo),border_radius=2)
        pygame.draw.rect(surf,bc,(cx+1,cy+30,9,17-lo),border_radius=2)
        pygame.draw.rect(surf,bc,(cx-13,cy+14,26,18),border_radius=3)
        pygame.draw.rect(surf,bc_hi,(cx-13,cy+14,26,5),border_radius=3)
        pygame.draw.rect(surf,bc_dk,(cx-13,cy+28,26,4))

        # Mortar tube (big chunky weapon carried at angle)
        tube_angle = math.radians(-55 + rc*2)   # pointed up-ish
        tube_len = 36
        tube_ex  = int(cx + f * math.cos(tube_angle) * tube_len)
        tube_ey  = int(cy + 16 + math.sin(tube_angle) * tube_len - rc*2)
        pygame.draw.line(surf,(38,36,32),(cx+f*8,cy+16+rc),(tube_ex,tube_ey),10)
        pygame.draw.line(surf,(56,52,46),(cx+f*8,cy+16+rc),(tube_ex,tube_ey),5)
        # Bipod
        pygame.draw.line(surf,(42,38,28),(cx+f*4,cy+28),
                         (cx+f*14,cy+self.H),(2))
        pygame.draw.line(surf,(42,38,28),(cx+f*8,cy+28),
                         (cx+f*2, cy+self.H),(2))
        # Muzzle smoke when fired
        if self.fire_anim > 8:
            PARTICLES.spawn_smoke(tube_ex + 20, tube_ey)

        # Arms
        pygame.draw.line(surf,bc,(cx-10,cy+16),(cx-20,cy+28),5)
        pygame.draw.line(surf,bc,(cx+10,cy+16),(cx+f*22,cy+22),5)

        # Neck + head
        pygame.draw.rect(surf,(168,118,82),(cx-3,cy+10,6,6))
        pygame.draw.circle(surf,(175,128,88),(cx,cy+4),10)
        pygame.draw.circle(surf,(140,100,68),(cx+f*3,cy+5),5)
        eye_x = cx+f*4
        pygame.draw.circle(surf,(228,222,212),(eye_x,cy+2),2)
        pygame.draw.circle(surf,(20,15,10),(eye_x,cy+2),1)

        # Helmet
        helm=(52,66,44); helm_hi=(68,86,56)
        pygame.draw.arc(surf,helm,pygame.Rect(cx-12,cy-5,24,18),0,math.pi,0)
        pygame.draw.rect(surf,helm,(cx-12,cy+4,24,8))
        pygame.draw.arc(surf,helm_hi,pygame.Rect(cx-9,cy-3,11,10),0.4,math.pi-0.4,2)
        pygame.draw.rect(surf,(36,46,30),(cx-13,cy+10,26,3),border_radius=1)

        # HP bar
        bw=38; bx3=cx-bw//2; by3=cy-16
        pygame.draw.rect(surf,(10,10,10),(bx3,by3,bw,4))
        hp_r=self.hp/self.max_hp
        pygame.draw.rect(surf,(50,200,80) if hp_r>0.5 else (220,40,40),
                         (bx3,by3,int(bw*hp_r),4))
        lf=pygame.font.SysFont("consolas",8,bold=True)
        surf.blit(lf.render("MORTAR",True,(180,130,50)),(cx-14,by3-10))


class MortarShell:
    """Slow arcing projectile fired by MortarSoldier. Big explosion on land."""
    GRAVITY   = 0.38
    EXPLOSION_R = 145
    DAMAGE      = 55

    def __init__(self, x, y, vx, vy):
        self.x = float(x); self.y = float(y)
        self.vx = vx;      self.vy = vy
        self.alive = True
        self.trail = []
        self.exploded = False
        self.explode_timer = 0

    def get_rect(self):
        return pygame.Rect(self.x - 6, self.y - 6, 12, 12)

    def update(self, player_ref):
        if self.exploded:
            self.explode_timer += 1
            if self.explode_timer > 25: self.alive = False
            return []

        self.vy += self.GRAVITY
        self.x  += self.vx
        self.y  += self.vy

        # Trail smoke
        if len(self.trail) % 3 == 0:
            self.trail.append({"x": self.x, "y": self.y, "age": 0})
        for tr in self.trail: tr["age"] += 1
        self.trail = [tr for tr in self.trail if tr["age"] < 22]

        # Land on ground or platforms
        hits = []
        landed = False
        if self.y >= GROUND_Y - 6:
            self.y = GROUND_Y - 6; landed = True
        for plat in current_platforms:
            if self.get_rect().colliderect(plat) and self.vy > 0:
                landed = True; break

        if self.x < -300 or self.x > WORLD_WIDTH + 300: self.alive = False

        if landed:
            self.exploded = True
            self.vx = self.vy = 0
            SFX.play(SFX.big_explosion)
            PARTICLES.spawn_explosion(self.x, self.y, scale=1.8)
            LIGHTS.add_explosion_light(self.x, self.y, scale=2.0)
            # Damage player
            d = math.hypot(player_ref.rect.centerx - self.x,
                           player_ref.rect.centery - self.y)
            if d < self.EXPLOSION_R:
                hits.append(int(self.DAMAGE * (1 - d / self.EXPLOSION_R)))
        return hits

    def draw(self, surf, cam_x=0):
        sx = int(self.x) - cam_x; sy = int(self.y)
        if self.exploded:
            r = self.explode_timer * 5
            if r > 0:
                es2 = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
                pygame.draw.circle(es2,(255,180,50,max(0,160-self.explode_timer*7)),
                                   (r+2,r+2),r,4)
                surf.blit(es2,(sx-r-2,sy-r-2))
            return
        # Trail
        for tr in self.trail:
            ta = max(0, int((1-tr["age"]/22)*130))
            tr_r = max(1,int((1-tr["age"]/22)*5))
            ts2 = pygame.Surface((tr_r*2+2,tr_r*2+2),pygame.SRCALPHA)
            pygame.draw.circle(ts2,(120,110,100,ta),(tr_r+1,tr_r+1),tr_r)
            surf.blit(ts2,(int(tr["x"])-cam_x-tr_r-1,int(tr["y"])-tr_r-1))
        # Shell body
        angle = math.atan2(self.vy, self.vx)
        cos_a = math.cos(angle); sin_a = math.sin(angle)
        pts = [
            (int(sx + cos_a*10), int(sy + sin_a*10)),
            (int(sx - cos_a*10 + sin_a*4), int(sy - sin_a*10 - cos_a*4)),
            (int(sx - cos_a*10 - sin_a*4), int(sy - sin_a*10 + cos_a*4)),
        ]
        pygame.draw.polygon(surf, (80,76,60), pts)
        pygame.draw.polygon(surf, (100,95,72), pts, 1)
        # Nose
        nose_x = int(sx + cos_a*12); nose_y = int(sy + sin_a*12)
        pygame.draw.circle(surf,(180,70,20),(nose_x,nose_y),4)
        pygame.draw.circle(surf,(220,100,40),(nose_x,nose_y),2)
        # Shadow indicator on ground (where it will land)
        land_x = int(self.x + self.vx * (abs(self.vy)/self.GRAVITY if self.vy > 0 else 0))
        land_sx = land_x - cam_x
        if 0 < land_sx < WIDTH:
            pygame.draw.ellipse(surf,(220,60,20,60),(land_sx-12,GROUND_Y-3,24,5))
            pygame.draw.ellipse(surf,(255,80,20,30),(land_sx-22,GROUND_Y-4,44,7))

class StealthSoldier(Enemy):
    """Becomes invisible when far from player, decloaks to attack.
    Leaves a shimmer distortion while cloaked."""
    W = 30; H = 52; is_air = False
    CLOAK_RANGE   = 380
    UNCLOAK_RANGE = 180

    def __init__(self, x, y, hp=65, speed=3.0, shoot_rate=1400):
        super().__init__(x, y, hp=hp, speed=speed, shoot_rate=shoot_rate)
        self.cloaked       = True
        self.cloak_alpha   = 255   # 30=nearly invisible, 255=fully visible
        self.shimmer_timer = 0
        self.uncloak_timer = 0     # brief reveal flash

    def update(self, player, bullets, grenades_list):
        super().update(player, bullets, grenades_list)
        dist = math.hypot(player.x - self.x, player.y - self.y)
        self.shimmer_timer = (self.shimmer_timer + 1) % 60
        if self.uncloak_timer > 0: self.uncloak_timer -= 1

        # Cloak management
        if dist > self.CLOAK_RANGE and not self.cloaked:
            self.cloaked = True
        elif dist < self.UNCLOAK_RANGE and self.cloaked:
            self.cloaked       = False
            self.uncloak_timer = 45   # flash visible on reveal

        if self.cloaked:
            self.cloak_alpha = max(28, self.cloak_alpha - 12)
        else:
            self.cloak_alpha = min(255, self.cloak_alpha + 18)

    def take_damage(self, amount):
        # Taking damage always decloaks
        self.cloaked       = False
        self.uncloak_timer = 60
        self.cloak_alpha   = 255
        super().take_damage(amount)

    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        cx  = sx + self.W // 2
        cy  = int(self.y)
        t   = pygame.time.get_ticks()
        f   = self.facing

        # Shimmer distortion when cloaked
        if self.cloaked and self.cloak_alpha < 100:
            shim_r = int(20 + math.sin(self.shimmer_timer * 0.21) * 8)
            ss2 = pygame.Surface((shim_r*2+4, shim_r*2+4), pygame.SRCALPHA)
            pygame.draw.ellipse(ss2, (140,200,255, int(self.cloak_alpha*0.5)),
                                (0,0,shim_r*2+4,shim_r*2+4))
            surf.blit(ss2, (cx-shim_r-2, cy+self.H//2-shim_r-2))
            return   # don't draw body if very cloaked

        # Uncloak flash ring
        if self.uncloak_timer > 30:
            ring_r = int((45-self.uncloak_timer)*4)
            if ring_r > 0:
                rs2 = pygame.Surface((ring_r*2+4,ring_r*2+4),pygame.SRCALPHA)
                pygame.draw.circle(rs2,(100,200,255,int((45-self.uncloak_timer)*6)),
                                   (ring_r+2,ring_r+2),ring_r,3)
                surf.blit(rs2,(cx-ring_r-2,cy+self.H//2-ring_r-2))

        # Draw body with alpha
        body_surf = pygame.Surface((self.W+16, self.H+16), pygame.SRCALPHA)
        box = 8; boy = 8

        # Shadow
        pygame.draw.ellipse(body_surf,(0,0,0,40),(box-4,boy+self.H+2,self.W+8,6))

        lo = [0,7,0,-7][self.walk_frame]
        # Boots — dark stealth
        for bk_off, bk_lo in [(-9, lo), (1, -lo)]:
            pygame.draw.rect(body_surf,(18,18,18),(box+self.W//2+bk_off,boy+42+bk_lo,10,8),border_radius=2)
        # Legs — black ops
        leg_col = (22,28,22)
        pygame.draw.rect(body_surf, leg_col, (box+self.W//2-9, boy+28, 9, 15+lo), border_radius=2)
        pygame.draw.rect(body_surf, leg_col, (box+self.W//2+1, boy+28, 9, 15-lo), border_radius=2)
        # Body — dark ops suit
        suit_col = (28,35,28)
        suit_hi  = (42,52,42)
        pygame.draw.rect(body_surf,suit_col,(box+self.W//2-12,boy+12,24,18),border_radius=3)
        pygame.draw.rect(body_surf,suit_hi, (box+self.W//2-12,boy+12,24,5),border_radius=3)
        # Cloaking device on chest (glowing)
        cd_pulse = int(80+abs(math.sin(t*0.007))*100)
        cd_col   = (40,200,100) if not self.cloaked else (40,80,200)
        cds = pygame.Surface((10,10),pygame.SRCALPHA)
        pygame.draw.circle(cds,(*cd_col,cd_pulse),(5,5),5)
        body_surf.blit(cds,(box+self.W//2-5,boy+16))
        # Arms
        pygame.draw.line(body_surf,suit_col,(box+self.W//2-10,boy+14),
                         (box+self.W//2-20,boy+26),5)
        pygame.draw.line(body_surf,suit_col,(box+self.W//2+10,boy+14),
                         (box+self.W//2+20,boy+24),5)
        # Silenced SMG
        gx3=box+self.W//2+f*14; gy3=boy+20
        pygame.draw.rect(body_surf,(30,30,30),(gx3,gy3-3,f*16 if f>0 else -f*16,6))
        pygame.draw.rect(body_surf,(22,22,22),(gx3+f*14,gy3-4,f*8 if f>0 else -f*8,8),border_radius=1)
        pygame.draw.rect(body_surf,(35,25,12),(gx3-f*4,gy3-2,f*(-8),6),border_radius=1)
        # Head
        pygame.draw.rect(body_surf,(18,18,18),(box+self.W//2-3,boy+9,6,5))
        pygame.draw.circle(body_surf,(175,128,88),(box+self.W//2,boy+3),10)
        pygame.draw.circle(body_surf,(140,100,68),(box+self.W//2+f*3,boy+4),5)
        # Full balaclava
        pygame.draw.circle(body_surf,(14,14,22),(box+self.W//2,boy+3),10)
        pygame.draw.rect(body_surf,(14,14,22),(box+self.W//2-9,boy-1,18,8))
        # Night-vision goggles
        nv_col = (20,180,40) if not self.cloaked else (20,80,180)
        for nv_off in (-4, 3):
            nvs = pygame.Surface((9,7),pygame.SRCALPHA)
            pygame.draw.ellipse(nvs,(*nv_col,200),(0,0,9,7))
            body_surf.blit(nvs,(box+self.W//2+nv_off,boy-3))
        # Helmet
        pygame.draw.arc(body_surf,(22,28,22),
                        pygame.Rect(box+self.W//2-12,boy-10,24,18),0,math.pi,0)
        pygame.draw.rect(body_surf,(22,28,22),(box+self.W//2-12,boy+2,24,7))
        # HP bar
        bw = 34; bx4 = box+self.W//2-bw//2; by4 = boy-18
        pygame.draw.rect(body_surf,(10,10,10),(bx4,by4,bw,4))
        hp_r = self.hp/self.max_hp
        pygame.draw.rect(body_surf,(50,200,80) if hp_r>0.5 else (220,40,40),
                         (bx4,by4,int(bw*hp_r),4))
        lf2 = pygame.font.SysFont("consolas",8,bold=True)
        lt2 = lf2.render("STEALTH",True,(60,200,80) if not self.cloaked else (60,80,180))
        body_surf.blit(lt2,(box+self.W//2-lt2.get_width()//2,by4-10))

        body_surf.set_alpha(self.cloak_alpha)
        surf.blit(body_surf,(sx-8, cy-8))

class SuicideBomber(Enemy):
    """Sprints directly at the player, flashing red, then explodes on contact."""
    W = 28; H = 50; is_air = False
    DETECT_RANGE = 500
    RUN_SPEED    = 6.5
    EXPLOSION_R  = 110
    EXPLOSION_DMG= 65

    def __init__(self, x, y, hp=40, speed=None, shoot_rate=99999):
        super().__init__(x, y, hp=hp, speed=speed or self.RUN_SPEED, shoot_rate=99999)
        self.triggered   = False
        self.flash_timer = 0
        self.beep_timer  = 0

    def update(self, player, bullets, grenades_list):
        # Gravity
        self.vy = min(self.vy + 0.7, 18); self.y += self.vy; self.on_ground = False
        for plat in current_platforms:
            r = self.rect
            if r.colliderect(plat) and self.vy >= 0:
                if r.bottom - self.vy <= plat.top + abs(self.vy) + 2:
                    self.y = plat.top - self.H; self.vy = 0; self.on_ground = True

        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist < self.DETECT_RANGE:
            self.triggered = True
        if self.triggered:
            self.flash_timer = (self.flash_timer + 1) % 14
            self.beep_timer  += 1
            if self.beep_timer % 18 == 0:
                SFX.play(SFX.hit_enemy)
            self._move_toward(player.x, self.RUN_SPEED * get_diff()["enemy_speed_mult"])
            self._try_jump(player.x)
            if dist < 32:
                self._explode(player)
        else:
            self._move_toward(self.x + self.patrol_dir * 40, self.speed * 0.4)
            self.patrol_timer += 1
            if self.patrol_timer > 80:
                self.patrol_dir *= -1; self.patrol_timer = 0

    def _explode(self, player):
        self.alive = False
        SFX.play(SFX.big_explosion)
        PARTICLES.spawn_explosion(self.x, self.y, scale=1.4)
        LIGHTS.add_explosion_light(self.x, self.y, scale=2.0)
        d = math.hypot(player.rect.centerx - self.x, player.rect.centery - self.y)
        if d < self.EXPLOSION_R:
            player.take_damage(int(self.EXPLOSION_DMG * (1 - d / self.EXPLOSION_R)))

    def take_damage(self, amount):
        self.hp -= amount
        SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_blood(self.rect.centerx, self.rect.centery)
        if self.hp <= 0:
            self._explode_dummy()

    def _explode_dummy(self):
        self.alive = False
        SFX.play(SFX.explosion)
        PARTICLES.spawn_explosion(self.x, self.y, scale=1.0)
        LIGHTS.add_explosion_light(self.x, self.y, scale=2.0)

    def draw(self, surf, cam_x=0):
        sx  = int(self.x) - cam_x
        cx  = sx + self.W // 2
        cy  = int(self.y)
        t   = pygame.time.get_ticks()
        f   = self.facing

        # Flash red when triggered
        if self.triggered and self.flash_timer < 7:
            flash_s = pygame.Surface((self.W + 16, self.H + 16), pygame.SRCALPHA)
            flash_a = int(120 + abs(math.sin(t * 0.04)) * 100)
            pygame.draw.ellipse(flash_s, (255, 30, 30, flash_a),
                                (0, 0, self.W + 16, self.H + 16))
            surf.blit(flash_s, (sx - 8, cy - 8))

        # Shadow
        sh = pygame.Surface((self.W + 4, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,55), (0,0,self.W+4,6))
        surf.blit(sh, (cx-self.W//2-2, cy+self.H-2))

        lo = [0,7,0,-7][self.walk_frame]
        boot_col = (18, 14, 10)
        pygame.draw.rect(surf, boot_col, (cx-9, cy+42+lo, 10, 8), border_radius=2)
        pygame.draw.rect(surf, boot_col, (cx+1,  cy+42-lo, 10, 8), border_radius=2)
        # Orange legs (hazmat colour)
        oc = (200, 90, 20)
        pygame.draw.rect(surf, oc, (cx-8, cy+28, 8, 15+lo), border_radius=2)
        pygame.draw.rect(surf, oc, (cx+1, cy+28, 8, 15-lo), border_radius=2)
        # Bomb vest
        vest_col = (180, 50, 20) if not self.triggered else \
                   ((255, 30, 30) if self.flash_timer < 7 else (200, 50, 20))
        pygame.draw.rect(surf, vest_col, (cx-12, cy+12, 24, 18), border_radius=3)
        pygame.draw.rect(surf, (220, 80, 30), (cx-12, cy+12, 24, 5), border_radius=3)
        # TNT blocks on vest
        for tx2, ty2 in [(-9, cy+15), (1, cy+15), (-9, cy+22), (1, cy+22)]:
            pygame.draw.rect(surf, (220,20,20), (cx+tx2, ty2, 8, 6), border_radius=1)
            pygame.draw.rect(surf, (255,60,60), (cx+tx2, ty2, 8, 2))
        # Wires
        for wx2 in (cx-5, cx+1, cx+7):
            pygame.draw.line(surf, (255,220,0), (wx2, cy+12), (wx2-1, cy+8), 1)
        # Detonator box
        pygame.draw.rect(surf, (30,30,30), (cx-8, cy+6, 10, 8), border_radius=1)
        pygame.draw.circle(surf,
            (255,30,30) if self.triggered else (30,200,30),
            (cx-3, cy+10), 3)
        # Arms
        pygame.draw.line(surf, oc, (cx-11, cy+14), (cx-20, cy+26), 5)
        pygame.draw.line(surf, oc, (cx+11, cy+14), (cx+20, cy+24), 5)
        pygame.draw.circle(surf, boot_col, (cx-20, cy+26), 4)
        pygame.draw.circle(surf, boot_col, (cx+20, cy+24), 4)
        # Neck + head
        pygame.draw.rect(surf, (175,128,88), (cx-3, cy+9, 6, 5))
        pygame.draw.circle(surf, (175,128,88), (cx, cy+3), 10)
        pygame.draw.circle(surf, (140,100,68), (cx+f*3, cy+4), 5)
        # Balaclava (black)
        pygame.draw.rect(surf, (14,14,14), (cx-9, cy-2, 18, 8))
        pygame.draw.circle(surf, (14,14,14), (cx, cy+2), 8)
        # Eyes (narrow, angry)
        pygame.draw.line(surf, (255,40,40), (cx-6, cy), (cx-2, cy), 2)
        pygame.draw.line(surf, (255,40,40), (cx+2, cy), (cx+6, cy), 2)
        # Helmet / headband
        pygame.draw.rect(surf, (180,30,20), (cx-10, cy-10, 20, 6))
        pygame.draw.rect(surf, (220,50,30), (cx-10, cy-10, 20, 2))

        # Warning text when triggered
        if self.triggered:
            wf = pygame.font.SysFont("consolas", 9, bold=True)
            pulse = abs(math.sin(t*0.015))
            wt = wf.render("⚠ BOOM!", True, (255, int(50+200*pulse), 30))
            surf.blit(wt, (cx-wt.get_width()//2, cy-28))

        # HP bar
        bw = 32; bx3 = cx-bw//2; by3 = cy-18
        pygame.draw.rect(surf,(10,10,10),(bx3,by3,bw,4))
        hp_r = self.hp/self.max_hp
        pygame.draw.rect(surf,(220,40,40),(bx3,by3,int(bw*hp_r),4))

class TurretEnemy:
    """Static defensive turret — placed at zone entry points.
    Rotates to track player, fires fast bursts. Armoured — needs rockets.
    Destroyed by explosives or sustained fire."""
    W = 44; H = 36; is_air = False
    SHOOT_RATE = 600
    RANGE = 700

    def __init__(self, x, y):
        diff = get_diff()
        self.x = float(x); self.y = float(y)
        self.MAX_HP = int(180 * diff["enemy_hp_mult"])
        self.hp = self.MAX_HP
        self.alive = True
        self.barrel_angle = 0.0
        self.last_shot = 0
        self.shoot_rate = int(self.SHOOT_RATE * diff["shoot_rate_mult"])
        self.alert = False
        self.alert_timer = 0
        self.muzzle_flash = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x) - self.W//2, int(self.y) - self.H, self.W, self.H)

    def update(self, player, bullets):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist < self.RANGE:
            self.alert = True
            target_angle = math.atan2(dy, dx)
            diff_angle = target_angle - self.barrel_angle
            while diff_angle > math.pi: diff_angle -= 2*math.pi
            while diff_angle < -math.pi: diff_angle += 2*math.pi
            self.barrel_angle += diff_angle * 0.07
        else:
            self.alert = False
        if self.muzzle_flash > 0: self.muzzle_flash -= 1
        now = pygame.time.get_ticks()
        if self.alert and dist < self.RANGE and now - self.last_shot >= self.shoot_rate:
            self.last_shot = now
            ox = self.rect.centerx; oy = self.rect.centery - 10
            spread = random.uniform(-0.08, 0.08)
            dmg = int(12 * get_diff()["enemy_dmg_mult"])
            bullets.append(Bullet(ox, oy,
                math.cos(self.barrel_angle + spread) * 14,
                math.sin(self.barrel_angle + spread) * 14,
                dmg, (255, 120, 40)))
            SFX.play(SFX.shoot_pistol)
            self.muzzle_flash = 6
            PARTICLES.spawn_muzzle_flash(
                int(ox + math.cos(self.barrel_angle)*22),
                int(oy + math.sin(self.barrel_angle)*22), 1)

    def take_damage(self, amount, is_rocket=False):
        dmg = amount if is_rocket else max(1, int(amount * 0.35))
        self.hp -= dmg
        PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 6)
        SFX.play(SFX.hit_enemy)
        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_tank_death(self.rect.centerx, self.rect.centery)
            SFX.play(SFX.big_explosion)

    def draw(self, surf, cam_x=0):
        sx = int(self.x) - cam_x
        cy = int(self.y)
        t = pygame.time.get_ticks()

        # Shadow
        sh = pygame.Surface((self.W+8, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,55), (0,0,self.W+8,8))
        surf.blit(sh, (sx-self.W//2-4, cy-3))

        # Base plate — heavy concrete block
        base_col = (52, 55, 60)
        base_hi  = (70, 74, 80)
        base_shad= (34, 36, 40)
        pygame.draw.rect(surf, base_col,  (sx-22, cy-14, 44, 14), border_radius=3)
        pygame.draw.rect(surf, base_hi,   (sx-22, cy-14, 44,  4), border_radius=3)
        pygame.draw.rect(surf, base_shad, (sx-22, cy- 4, 44,  4))
        # Bolts on base
        for bx2 in (sx-18, sx-6, sx+6, sx+18):
            pygame.draw.circle(surf, base_shad, (bx2, cy-7), 2)
            pygame.draw.circle(surf, base_hi,   (bx2, cy-7), 1)

        # Rotation ring
        pygame.draw.ellipse(surf, (42, 45, 52), (sx-12, cy-22, 24, 10))
        pygame.draw.ellipse(surf, (60, 64, 72), (sx-10, cy-21, 20, 8))

        # Turret dome
        dome_col  = (48, 58, 48) if not self.alert else (68, 38, 32)
        dome_hi   = (65, 78, 65) if not self.alert else (90, 50, 42)
        pygame.draw.ellipse(surf, dome_col,  (sx-16, cy-34, 32, 20))
        pygame.draw.ellipse(surf, dome_hi,   (sx-16, cy-34, 32,  8))
        pygame.draw.ellipse(surf, (30,36,30),(sx-16, cy-34, 32, 20), 1)
        # Alert indicator LED
        led_col = (255, 30, 30) if self.alert and (t//150)%2==0 else \
                  (50, 200, 50) if not self.alert else (120, 10, 10)
        ls2 = pygame.Surface((8,8),pygame.SRCALPHA)
        pygame.draw.circle(ls2, (*led_col, 220), (4,4), 4)
        surf.blit(ls2, (sx-4, cy-40))
        if self.alert:
            gs2 = pygame.Surface((16,16),pygame.SRCALPHA)
            pygame.draw.circle(gs2, (*led_col, 80), (8,8), 8)
            surf.blit(gs2, (sx-8, cy-44))

        # Barrel
        cos_b = math.cos(self.barrel_angle)
        sin_b = math.sin(self.barrel_angle)
        bx3 = sx; by3 = cy - 24
        blen = 28
        ex2 = int(bx3 + cos_b * blen); ey2 = int(by3 + sin_b * blen)
        pygame.draw.line(surf, (32,40,30), (bx3,by3), (ex2,ey2), 7)
        pygame.draw.line(surf, (52,64,50), (bx3,by3), (ex2,ey2), 3)
        # Muzzle
        pygame.draw.rect(surf, (28,34,26),
                         (ex2-3, ey2-4, 7, 8), border_radius=1)
        # Muzzle flash
        if self.muzzle_flash > 0:
            mf = pygame.Surface((22,22),pygame.SRCALPHA)
            pygame.draw.circle(mf, (255,210,80,self.muzzle_flash*35),(11,11),10)
            surf.blit(mf, (ex2-11, ey2-11))

        # HP bar
        bw = 42; bx4 = sx-bw//2; by4 = cy-52
        pygame.draw.rect(surf,(8,10,6),(bx4,by4,bw,5),border_radius=2)
        hr = self.hp/self.MAX_HP
        hc = (50,200,80) if hr>0.5 else (220,190,50) if hr>0.25 else (220,40,40)
        if hr>0: pygame.draw.rect(surf,hc,(bx4,by4,int(bw*hr),5),border_radius=2)
        pygame.draw.rect(surf,(45,60,44),(bx4,by4,bw,5),1,border_radius=2)
        lf = pygame.font.SysFont("consolas",8,bold=True)
        surf.blit(lf.render("TURRET",True,(180,80,40) if self.alert else (100,140,80)),
                  (sx-14,by4-10))

# ═══════════════════════════════════════════════════
#  V7.0 NEW ENEMY: SNIPER MECH
# ═══════════════════════════════════════════════════
class SniperMechs:
    W = 58; H = 72; is_air = False
    SPEED = 0.9; SHOOT_RATE = 3500; RANGE = 900
    def __init__(self, x, y):
        diff = get_diff()
        self.x = float(x); self.y = float(y - self.H)
        self.MAX_HP = int(320 * diff["enemy_hp_mult"])
        self.hp = self.MAX_HP
        self.alive = True; self.facing = -1
        self.last_shot = 0; self.vy = 0.0; self.on_ground = False
        self.shoot_rate = int(self.SHOOT_RATE * diff["shoot_rate_mult"])
        self.charging = False; self.charge_timer = 0
        self.laser_target = (0, 0)
        self.walk_frame = 0; self.walk_timer = 0
        self.stun_timer = 0
        self.leg_offset = 0.0
        self.shield_hp = int(80 * diff["enemy_hp_mult"])
        self.max_shield_hp = self.shield_hp
        self.shield_broken = False
        self.shield_regen = 0
        self.mech_kills = 0

    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self, player, bullets, grenades_list):
        if self.stun_timer > 0: self.stun_timer -= 1; return
        self.vy = min(self.vy + 0.7, 18); self.y += self.vy; self.on_ground = False
        for plat in current_platforms:
            r = self.rect
            if r.colliderect(plat) and self.vy >= 0:
                if r.bottom - self.vy <= plat.top + abs(self.vy) + 2:
                    self.y = plat.top - self.H; self.vy = 0; self.on_ground = True

        # Shield regen
        if self.shield_broken:
            self.shield_regen += 1
            if self.shield_regen > 300:
                self.shield_hp = min(self.max_shield_hp, self.shield_hp + 0.5)
                if self.shield_hp >= self.max_shield_hp:
                    self.shield_broken = False; self.shield_regen = 0

        dist = math.hypot(player.x - self.x, player.y - self.y)
        self.facing = 1 if player.x > self.x else -1

        # Movement — stays at range
        if dist > self.RANGE * 0.8:
            self.x += self.SPEED * self.facing
            self.walk_timer += 1
            if self.walk_timer > 12: self.walk_frame = (self.walk_frame+1)%4; self.walk_timer=0
        elif dist < 300:
            self.x -= self.SPEED * 1.5 * self.facing

        self.leg_offset = math.sin(pygame.time.get_ticks() * 0.08) * 10

        now = pygame.time.get_ticks()
        if dist < self.RANGE:
            if not self.charging:
                if now - self.last_shot >= self.shoot_rate:
                    self.charging = True; self.charge_timer = 90
                    self.laser_target = (player.rect.centerx, player.rect.centery)
            else:
                self.charge_timer -= 1
                if self.charge_timer > 20:
                    self.laser_target = (player.rect.centerx, player.rect.centery)
                if self.charge_timer <= 0:
                    self.charging = False; self.last_shot = now
                    ox = self.rect.centerx; oy = self.rect.centery - 10
                    tx, ty = self.laser_target
                    d = math.hypot(tx-ox, ty-oy) or 1
                    dmg = int(70 * get_diff()["enemy_dmg_mult"])
                    b = Bullet(ox, oy, (tx-ox)/d*26, (ty-oy)/d*26, dmg, PLASMA_COL, is_sniper=True)
                    bullets.append(b)
                    SFX.play(SFX.shoot_sniper)
                    PARTICLES.spawn_muzzle_flash(ox + self.facing*20, oy, self.facing)
                    # Double shot at low HP
                    if self.hp < self.MAX_HP * 0.4:
                        for off in (-0.15, 0.15):
                            angle = math.atan2(ty-oy, tx-ox) + off
                            bullets.append(Bullet(ox, oy, math.cos(angle)*22,
                                                  math.sin(angle)*22, dmg//2, PLASMA_COL, True))

        self.x = max(0, min(WORLD_WIDTH - self.W, self.x))

    def take_damage(self, amount, is_rocket=False):
        SFX.play(SFX.hit_enemy)
        if not self.shield_broken and self.shield_hp > 0:
            bleed = amount * 0.3 if is_rocket else 0
            self.shield_hp -= amount
            PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 10)
            if self.shield_hp <= 0:
                self.shield_broken = True; self.shield_regen = 0
                PARTICLES.spawn_explosion(self.rect.centerx, self.rect.centery, scale=0.7)
            if bleed > 0: self.hp -= int(bleed)
        else:
            self.hp -= amount if is_rocket else max(1, int(amount * 0.45))
            PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 6)
        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_tank_death(self.rect.centerx, self.rect.centery)
            SFX.play(SFX.big_explosion)
            unlock("mech_slayer")

    def draw(self, surf, cam_x=0):
        sx = int(self.x) - cam_x; cx = sx + self.W//2; cy = int(self.y)
        t = pygame.time.get_ticks()

        # Shadow
        sh = pygame.Surface((self.W+10, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0,0,0,65), (0,0,self.W+10,8))
        surf.blit(sh, (cx-self.W//2-5, cy+self.H-3))

        lo = int(self.leg_offset)

        # Legs — mechanical spider legs
        leg_col = (55, 65, 80); leg_hi = (80, 95, 115); joint_col = (40, 50, 65)
        for side, sign in [(-1, -1), (1, 1)]:
            lx = cx + side * 12
            # Upper leg
            knee_x = cx + side * 28
            knee_y = cy + 52 + lo * sign
            pygame.draw.line(surf, leg_col, (lx, cy+48), (knee_x, knee_y), 7)
            pygame.draw.line(surf, leg_hi,  (lx, cy+48), (knee_x, knee_y), 3)
            # Lower leg
            foot_x = cx + side * 32
            foot_y = cy + self.H - 4
            pygame.draw.line(surf, leg_col, (knee_x, knee_y), (foot_x, foot_y), 6)
            # Knee joint
            pygame.draw.circle(surf, joint_col, (knee_x, knee_y), 6)
            pygame.draw.circle(surf, leg_hi, (knee_x, knee_y), 4)
            # Foot plate
            pygame.draw.rect(surf, (35, 42, 55), (foot_x-10, foot_y-3, 20, 8), border_radius=2)

        # Torso
        tc = (48, 58, 75); tc_hi = (68, 82, 100); tc_dk = (30, 38, 52)
        pygame.draw.rect(surf, tc,    (cx-20, cy+12, 40, 38), border_radius=4)
        pygame.draw.rect(surf, tc_hi, (cx-20, cy+12, 40, 8),  border_radius=4)
        pygame.draw.rect(surf, tc_dk, (cx-20, cy+42, 40, 8))
        # Armor panels
        pygame.draw.rect(surf, tc_dk, (cx-18, cy+16, 16, 22), border_radius=2)
        pygame.draw.rect(surf, tc_dk, (cx+2,  cy+16, 16, 22), border_radius=2)
        pygame.draw.rect(surf, tc_hi, (cx-18, cy+16, 16, 5),  border_radius=2)
        pygame.draw.rect(surf, tc_hi, (cx+2,  cy+16, 16, 5),  border_radius=2)

        # Shield bubble
        if not self.shield_broken and self.shield_hp > 0:
            ratio = self.shield_hp / self.max_shield_hp
            pulse = abs(math.sin(t*0.006))*20
            r2 = 44
            ss2 = pygame.Surface((r2*2+4,r2*2+4), pygame.SRCALPHA)
            pygame.draw.circle(ss2, (80,160,255,int((30+pulse)*ratio)), (r2+2,r2+2), r2)
            pygame.draw.circle(ss2, (140,210,255,int(80*ratio)), (r2+2,r2+2), r2, 2)
            surf.blit(ss2, (cx-r2-2, cy+self.H//2-r2-2))

        # Shoulder cannon arm
        arm_y = cy + 18
        cannon_x = cx + self.facing * 22
        pygame.draw.line(surf, tc, (cx, arm_y), (cannon_x, arm_y+8), 8)
        # Main sniper cannon
        barrel_end = cx + self.facing * 52
        pygame.draw.line(surf, (28, 34, 45), (cannon_x, arm_y+4), (barrel_end, arm_y+4), 7)
        pygame.draw.line(surf, (50, 62, 80), (cannon_x, arm_y+4), (barrel_end, arm_y+4), 3)
        # Muzzle brake
        pygame.draw.rect(surf, (22,28,38), (barrel_end-(5 if self.facing<0 else 0), arm_y, 6, 9), border_radius=1)
        # Scope
        pygame.draw.rect(surf, (38,46,62), (cx+self.facing*10, arm_y-7, self.facing*20 if self.facing>0 else -self.facing*20, 6), border_radius=2)
        pygame.draw.circle(surf, (50,170,220), (cx+self.facing*28, arm_y-4), 4)
        pygame.draw.circle(surf, WHITE, (cx+self.facing*28, arm_y-4), 2)

        # Head unit
        pygame.draw.rect(surf, tc, (cx-16, cy-2, 32, 16), border_radius=3)
        pygame.draw.rect(surf, tc_hi,(cx-16, cy-2, 32, 5), border_radius=3)
        # Visor
        vis_a = int(140+abs(math.sin(t*0.08))*115)
        vs = pygame.Surface((26,8), pygame.SRCALPHA)
        pygame.draw.ellipse(vs, (*PLASMA_COL, vis_a), (0,0,26,8))
        surf.blit(vs, (cx-13, cy+2))
        # Sensor array
        for si in range(3):
            pygame.draw.circle(surf, (40,200,220), (cx-8+si*8, cy-4), 2)
        # Antenna
        pygame.draw.line(surf, (65,80,100), (cx, cy-2), (cx+self.facing*6, cy-16), 2)
        pygame.draw.circle(surf, PLASMA_COL, (cx+self.facing*6, cy-16), 3)

        # Laser charge effect
        if self.charging:
            ratio = 1.0 - self.charge_timer/90
            tx2, ty2 = self.laser_target
            sx2 = tx2 - cam_x
            alpha = int(80+160*ratio)
            laser_s = pygame.Surface((abs(sx2-(cx+self.facing*52))+4, abs(ty2-arm_y)+4), pygame.SRCALPHA)
            ox3 = min(cx+self.facing*52, sx2)
            oy3 = min(arm_y, ty2)
            pygame.draw.line(laser_s, (255,30,255,alpha),
                             (cx+self.facing*52-ox3+2, arm_y-oy3+2),
                             (sx2-ox3+2, ty2-oy3+2), 1)
            surf.blit(laser_s, (ox3-2, oy3-2))
            dot_r = int(3+ratio*6)
            ds = pygame.Surface((dot_r*2+2,dot_r*2+2), pygame.SRCALPHA)
            pygame.draw.circle(ds, (255,50,255,alpha), (dot_r+1,dot_r+1), dot_r)
            surf.blit(ds, (sx2-dot_r-1, ty2-dot_r-1))

        # HP + shield bars
        bw=54; bx=cx-bw//2; by=cy-18
        pygame.draw.rect(surf,(10,10,14),(bx,by,bw,6),border_radius=2)
        hr=self.hp/self.MAX_HP
        pygame.draw.rect(surf,(50,200,80) if hr>0.5 else (220,40,40),(bx,by,int(bw*hr),6),border_radius=2)
        pygame.draw.rect(surf,(10,20,50),(bx,by+7,bw,4),border_radius=2)
        if not self.shield_broken:
            sr2=self.shield_hp/self.max_shield_hp
            pygame.draw.rect(surf,SHIELD_COL,(bx,by+7,int(bw*sr2),4),border_radius=2)
        lf=pygame.font.SysFont("consolas",8,bold=True)
        surf.blit(lf.render("SNIPER-MECH",True,PLASMA_COL),(cx-20,by-11))


# ═══════════════════════════════════════════════════
#  V7.0 NEW ENEMY: RIOT SHIELD SOLDIER
# ═══════════════════════════════════════════════════
class RiotShieldSoldier(Enemy):
    W = 34; H = 56; is_air = False
    def __init__(self, x, y, hp=100, speed=2.2, shoot_rate=1600):
        super().__init__(x, y, hp, speed, shoot_rate)
        diff = get_diff()
        self.shield_side = 1   # which side shield faces
        self.bashing = False
        self.bash_timer = 0
        self.bash_cd = 0
        self.riot_kills = 0

    def take_damage(self, amount, is_rocket=False, is_explosion=False):
        # Front shield blocks 90% of bullets
        if not is_rocket and not is_explosion:
            if self.facing == self.shield_side:
                amount = max(1, int(amount * 0.1))
                PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 8)
                SFX.play(SFX.shield_hit)
            else:
                PARTICLES.spawn_blood(self.rect.centerx, self.rect.centery)
        else:
            PARTICLES.spawn_explosion(self.rect.centerx, self.rect.centery, scale=0.5)
        self.hp -= amount
        SFX.play(SFX.hit_enemy)
        if self.hp <= 0:
            self.alive = False
            PARTICLES.spawn_death_explosion(self.rect.centerx, self.rect.centery)
            self.riot_kills += 1

    def update(self, player, bullets, grenades_list):
        self.shield_side = 1 if player.x > self.x else -1
        if self.bash_cd > 0: self.bash_cd -= 1
        if self.bash_timer > 0:
            self.bash_timer -= 1
            self.bashing = self.bash_timer > 0
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if dist < 60 and self.bash_cd == 0 and self.on_ground:
            self.bash_timer = 20; self.bash_cd = 90; self.bashing = True
            player.take_damage(int(28 * get_diff()["enemy_dmg_mult"]))
            PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 12)
            SFX.play(SFX.hit_player)
        super().update(player, bullets, grenades_list)

    def draw(self, surf, cam_x=0):
        super().draw(surf, cam_x)
        sx = int(self.x) - cam_x; cx = sx + self.W//2; cy = int(self.y)
        f = self.facing; t = pygame.time.get_ticks()
        # Riot shield
        shield_x = cx + f*14
        shield_col = (55,120,200) if not self.bashing else (255,80,80)
        shield_hi  = (90,160,240) if not self.bashing else (255,150,100)
        # Shield body
        pygame.draw.rect(surf, shield_col, (shield_x, cy+4, f*22 if f>0 else -f*22, 44), border_radius=3)
        pygame.draw.rect(surf, shield_hi,  (shield_x, cy+4, f*22 if f>0 else -f*22, 8), border_radius=3)
        pygame.draw.rect(surf, (30,80,150), (shield_x, cy+4, f*22 if f>0 else -f*22, 44), 2, border_radius=3)
        # Shield window
        pygame.draw.rect(surf, (140,200,255,180), (shield_x+(4 if f>0 else 0), cy+10, 14, 18), border_radius=2)
        # POLICE text
        pf = pygame.font.SysFont("consolas", 7, bold=True)
        pt = pf.render("RIOT", True, WHITE)
        surf.blit(pt, (shield_x+(3 if f>0 else 1), cy+32))
        # Bash effect
        if self.bashing:
            bs = pygame.Surface((50,50), pygame.SRCALPHA)
            pygame.draw.circle(bs, (255,100,100,int(abs(math.sin(t*0.3))*150)), (25,25), 22)
            surf.blit(bs, (shield_x-12, cy+8))


# ═══════════════════════════════════════════════════
#  V7.0 NEW ENEMY: FLAMETHROWER TROOPER
# ═══════════════════════════════════════════════════
class FlameTrooper(Enemy):
    W = 32; H = 54; is_air = False
    FLAME_RANGE = 160
    FLAME_RATE  = 60   # ms between flame ticks
    def __init__(self, x, y, hp=90, speed=2.0, shoot_rate=800):
        super().__init__(x, y, hp, speed, shoot_rate)
        self.flame_active = False
        self.flame_timer = 0
        self.last_flame = 0
        self.tank_col = (random.randint(180,220), random.randint(60,90), random.randint(10,30))

    def update(self, player, bullets, grenades_list):
        dist = math.hypot(player.x - self.x, player.y - self.y)
        now = pygame.time.get_ticks()
        self.flame_active = dist < self.FLAME_RANGE
        if self.flame_active and now - self.last_flame > self.FLAME_RATE:
            self.last_flame = now
            dmg = int(6 * get_diff()["enemy_dmg_mult"])
            # Spawn flame particles toward player
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            d = math.hypot(dx,dy) or 1
            for _ in range(4):
                ang = math.atan2(dy,dx) + random.uniform(-0.3,0.3)
                sp = random.uniform(5,10)
                fb = FlameBullet(self.rect.centerx, self.rect.centery,
                                 math.cos(ang)*sp, math.sin(ang)*sp, dmg)
                bullets.append(fb)
            if dist < self.FLAME_RANGE * 0.8:
                player.take_damage(dmg)
            PARTICLES.spawn_ember(self.x, self.y)
        # Don't shoot normal bullets when flaming
        if not self.flame_active:
            super().update(player, bullets, grenades_list)
        else:
            self.vy = min(self.vy + 0.7, 18); self.y += self.vy; self.on_ground = False
            for plat in current_platforms:
                r = self.rect
                if r.colliderect(plat) and self.vy >= 0:
                    if r.bottom - self.vy <= plat.top + abs(self.vy)+2:
                        self.y = plat.top - self.H; self.vy=0; self.on_ground=True
            dx2 = player.x - self.x; self.facing = 1 if dx2>0 else -1
            if abs(dx2) > 80:
                self.x += self.speed * self.facing * 0.8
            self.x = max(0, min(WORLD_WIDTH-self.W, self.x))

    def draw(self, surf, cam_x=0):
        super().draw(surf, cam_x)
        sx = int(self.x)-cam_x; cx = sx+self.W//2; cy = int(self.y)
        f = self.facing; t = pygame.time.get_ticks()
        # Fuel tanks on back
        for tk_off in (-6, 2):
            pygame.draw.ellipse(surf, self.tank_col,
                                (cx-f*16+tk_off, cy+14, 10, 22))
            pygame.draw.ellipse(surf, tuple(min(255,c+30) for c in self.tank_col),
                                (cx-f*16+tk_off, cy+14, 10, 7))
        # Hose
        pygame.draw.line(surf, (40,40,40),
                         (cx-f*8, cy+22), (cx+f*12, cy+22), 3)
        # Nozzle
        pygame.draw.rect(surf, (50,50,50),
                         (cx+f*10, cy+18, f*12 if f>0 else -f*12, 8), border_radius=1)
        # Active flame cone
        if self.flame_active:
            for fi in range(8):
                ratio = fi/7
                fang = math.radians(random.uniform(-25,25))
                flen = int((30+ratio*80) + math.sin(t*0.04+fi)*12)
                fx = cx + int(f*(22+ratio*flen))
                fy = cy + 22 + int(math.sin(fang)*flen*0.4)
                fc = [(255,248,80),(255,200,30),(255,130,10),(255,80,5),
                      (220,50,5),(180,30,3),(130,20,2),(80,10,1)][fi]
                fr = max(1, int((8-fi)*1.1))
                fs2 = pygame.Surface((fr*2+2,fr*2+2), pygame.SRCALPHA)
                pygame.draw.circle(fs2, (*fc,200-fi*20),(fr+1,fr+1),fr)
                surf.blit(fs2,(fx-fr-1,fy-fr-1))
                LIGHTS.add(fx+cam_x, fy, 35, FLAME_COL, 0.6, life=1)


# ═══════════════════════════════════════════════════
#  V7.0 NEW ENEMY: BOMBER JET (ZONE 7-8)
# ═══════════════════════════════════════════════════
class BomberJet(Jet):
    """Slower than Jet but drops cluster bombs on player position."""
    W = 100; H = 28; is_air = True
    SPEED = 3.5; BOMB_RATE = 2800
    def __init__(self, x):
        super().__init__(x)
        diff = get_diff()
        self.MAX_HP = int(180 * diff["enemy_hp_mult"])
        self.hp = self.MAX_HP
        self.vx = -self.SPEED
        self.bomb_timer = random.randint(1000, 2000)
        self.bombs_dropped = []

    def update(self, player, bullets):
        self.bomb_timer -= 1
        now = pygame.time.get_ticks()
        # Move
        self.x += self.vx
        if self.x < -300 or self.x > WORLD_WIDTH+300:
            self.vx *= -1; self.facing *= -1
        # Bob
        self.y += math.sin(pygame.time.get_ticks()*0.002)*0.4
        self.y = max(GROUND_Y-280, min(GROUND_Y-180, self.y))

        if self.bomb_timer <= 0 and abs(player.x-self.x)<500:
            self.bomb_timer = int(self.BOMB_RATE * get_diff()["shoot_rate_mult"])
            # Drop 3 cluster bombs
            for bi in range(3):
                offset = (bi-1)*80
                self.bombs_dropped.append({
                    "x": float(self.rect.centerx + offset),
                    "y": float(self.rect.bottom),
                    "vy": float(random.uniform(4,8)),
                    "exploded": False,
                    "explode_timer": 0,
                })
            SFX.play(SFX.shoot_rocket)

        # Update bombs
        for bm in self.bombs_dropped:
            if bm["exploded"]:
                bm["explode_timer"] += 1
                continue
            bm["y"] += bm["vy"]; bm["vy"] += 0.4
            if bm["y"] >= GROUND_Y - 8:
                bm["exploded"] = True
                SFX.play(SFX.explosion)
                PARTICLES.spawn_explosion(bm["x"], bm["y"], scale=1.2)
                d = math.hypot(player.rect.centerx-bm["x"], player.rect.centery-bm["y"])
                if d < 120:
                    player.take_damage(int(45*(1-d/120)*get_diff()["enemy_dmg_mult"]))
        self.bombs_dropped = [b for b in self.bombs_dropped if b["explode_timer"]<30]

    def draw(self, surf, cam_x=0):
        if not self.alive: return
        sx  = int(self.x) - cam_x
        cx2 = sx + self.W // 2
        cy2 = int(self.y) + self.H // 2
        f   = 1 if self.vx > 0 else -1
        t   = pygame.time.get_ticks()

        body_col  = (28, 32, 38)
        body_hi   = (45, 52, 62)
        body_shad = (18, 20, 26)

        # ── Afterburner glow (two engine pods) ───────────────────────────────
        for eng_off in (-22, 22):
            nozzle_x = cx2 - f * 48
            nozzle_y = cy2 + eng_off
            for fi in range(6):
                ratio = fi / 5
                fl    = int((12 + ratio * 30) + random.randint(0, 8))
                fc    = [(255,248,80),(255,195,30),(255,120,10),
                         (200,55,8),(130,28,4),(60,10,0)][fi]
                fr    = max(1, int((6 - fi) * 0.9))
                end_x = nozzle_x - f * fl
                end_y = nozzle_y
                fs2 = pygame.Surface((fr*2+2, fr*2+2), pygame.SRCALPHA)
                pygame.draw.circle(fs2, (*fc, 210 - fi*28), (fr+1, fr+1), fr)
                surf.blit(fs2, (end_x - fr - 1, end_y - fr - 1))

        # ── B-2 FLYING WING — the whole aircraft IS the wing ─────────────────
        #
        #  Top view projected onto 2D side scroll.
        #  The B-2 has a distinctive W-shaped trailing edge and
        #  a smooth blended leading edge (no separate fuselage).
        #
        #  We draw it as layered polygons:
        #    1. Main wing body (large flat delta)
        #    2. Blended center-body hump
        #    3. Sawtooth trailing edge notches
        #    4. Engine inlet bumps on top
        #    5. Exhaust slots
        #    6. Cockpit blister

        W2 = self.W   # 100
        H2 = self.H   # 28

        # ── 1. Main wing planform (seen from slightly above) ──────────────────
        # Leading edge: smooth swept curve approximated with polygon
        # Trailing edge: W-shaped serrations
        lead_sweep = int(W2 * 0.55)   # how far back the wingtip is
        center_y_offset = -6          # center body is slightly above mid

        # Main wing — large flat rhombus with swept leading edge
        wing_pts = [
            (cx2 + f * int(W2*0.50),  cy2 + center_y_offset),          # nose tip
            (cx2 + f * int(W2*0.22),  cy2 + center_y_offset - H2//2),  # upper inner
            (cx2 - f * int(W2*0.10),  cy2 + center_y_offset - H2//2),  # upper root
            (cx2 - f * int(W2*0.50),  cy2 + center_y_offset - int(H2*0.3)),  # upper tip
            (cx2 - f * int(W2*0.50),  cy2 + center_y_offset + int(H2*0.3)),  # lower tip
            (cx2 - f * int(W2*0.10),  cy2 + center_y_offset + H2//2),  # lower root
            (cx2 + f * int(W2*0.22),  cy2 + center_y_offset + H2//2),  # lower inner
        ]
        pygame.draw.polygon(surf, body_col, wing_pts)
        pygame.draw.polygon(surf, body_hi, wing_pts, 1)

        # ── 2. W-shaped trailing edge ─────────────────────────────────────────
        # Sawtooth serrations on the trailing (rear) edge — B-2 signature
        te_x = cx2 - f * int(W2*0.50)   # trailing edge X
        for notch in range(3):
            ny = cy2 + center_y_offset - int(H2*0.28) + notch * int(H2*0.28)
            notch_depth = int(W2*0.07)
            saw_pts = [
                (te_x,                  ny),
                (te_x + f*notch_depth,  ny + int(H2*0.09)),
                (te_x,                  ny + int(H2*0.18)),
            ]
            pygame.draw.polygon(surf, body_shad, saw_pts)
            pygame.draw.polygon(surf, body_hi, saw_pts, 1)

        # ── 3. Center-body blended hump ───────────────────────────────────────
        # The B-2 has a raised center section where the crew/weapons sit
        hump_pts = [
            (cx2 + f*int(W2*0.48), cy2 + center_y_offset),
            (cx2 + f*int(W2*0.20), cy2 + center_y_offset - int(H2*0.65)),
            (cx2 - f*int(W2*0.05), cy2 + center_y_offset - int(H2*0.65)),
            (cx2 - f*int(W2*0.08), cy2 + center_y_offset - int(H2*0.40)),
            (cx2 + f*int(W2*0.10), cy2 + center_y_offset - int(H2*0.20)),
        ]
        pygame.draw.polygon(surf, body_hi, hump_pts)
        pygame.draw.polygon(surf, (55, 65, 78), hump_pts, 1)

        # ── 4. Engine inlet bumps (two on top of wing) ────────────────────────
        for ei, ei_y_off in enumerate((-10, 10)):
            inp_x = cx2 + f*int(W2*0.05)
            inp_y = cy2 + center_y_offset + ei_y_off
            pygame.draw.ellipse(surf, (38, 44, 54),
                                (inp_x - f*18, inp_y - 5, 36, 10))
            pygame.draw.ellipse(surf, (55, 65, 78),
                                (inp_x - f*18, inp_y - 5, 36, 5))
            # Inlet opening (dark oval)
            pygame.draw.ellipse(surf, (14, 16, 20),
                                (inp_x - f*12, inp_y - 3, 22, 6))

        # ── 5. Exhaust slots (rear, two per engine, recessed) ─────────────────
        for ei2, ei2_y in enumerate((-8, 8)):
            ex_x = cx2 - f*int(W2*0.32)
            ex_y = cy2 + center_y_offset + ei2_y
            # Slot housing
            pygame.draw.rect(surf, (32, 38, 48),
                             (ex_x - 12, ex_y - 4, 22, 8), border_radius=2)
            # Hot exhaust glow
            glow_a = int(60 + abs(math.sin(t*0.05 + ei2))*80)
            gs2 = pygame.Surface((18, 6), pygame.SRCALPHA)
            pygame.draw.ellipse(gs2, (255, 140, 30, glow_a), (0, 0, 18, 6))
            surf.blit(gs2, (ex_x - 10, ex_y - 3))

        # ── 6. Cockpit blister (small bump just behind nose) ──────────────────
        cock_x = cx2 + f*int(W2*0.30)
        cock_y = cy2 + center_y_offset - int(H2*0.55)
        pygame.draw.ellipse(surf, (50, 140, 185),
                            (cock_x - 12, cock_y - 3, 26, 10))
        pygame.draw.ellipse(surf, body_col, (cock_x - 12, cock_y - 3, 26, 10), 1)
        # Glint
        pygame.draw.ellipse(surf, (160, 220, 255),
                            (cock_x - 8, cock_y - 2, 12, 4))

        # ── 7. Surface panel lines ────────────────────────────────────────────
        # Subtle low-observable panel seams
        for pl_i in range(3):
            pl_x1 = cx2 + f*(int(W2*0.40) - pl_i*int(W2*0.22))
            pl_y1 = cy2 + center_y_offset - int(H2*0.45)
            pl_x2 = cx2 + f*(int(W2*0.25) - pl_i*int(W2*0.20))
            pl_y2 = cy2 + center_y_offset + int(H2*0.45)
            pygame.draw.line(surf, (22, 26, 32), (pl_x1, pl_y1), (pl_x2, pl_y2), 1)

        # ── 8. Weapon bay doors (bottom, open during bomb run) ────────────────
        bomb_run_active = len(self.bombs_dropped) > 0
        if bomb_run_active:
            bay_x = cx2 + f*int(W2*0.10)
            bay_y = cy2 + center_y_offset + int(H2*0.42)
            pygame.draw.rect(surf, (8, 10, 14),
                             (bay_x - 14, bay_y, 28, 6), border_radius=1)
            pygame.draw.rect(surf, (40, 50, 62),
                             (bay_x - 14, bay_y, 28, 6), 1, border_radius=1)

        # ── 9. Nav lights ────────────────────────────────────────────────────
        nl_blink = (t // 500) % 2 == 0
        tip_x = cx2 - f*int(W2*0.48)
        # Red/green wingtip position lights
        for nl_off, nl_col in ((-int(H2*0.28), (255,30,30)), (int(H2*0.28), (30,255,80))):
            nl_y = cy2 + center_y_offset + nl_off
            if nl_blink:
                nls = pygame.Surface((8,8), pygame.SRCALPHA)
                pygame.draw.circle(nls, (*nl_col, 200), (4,4), 4)
                surf.blit(nls, (tip_x - 4, nl_y - 4))

        # ── 10. Falling bombs ────────────────────────────────────────────────
        for bm in self.bombs_dropped:
            if bm["exploded"]: continue
            bsx = int(bm["x"]) - cam_x
            bsy = int(bm["y"])

            # B61/B83-style gravity bomb — cylindrical with fins
            bomb_angle = math.atan2(bm["vy"], 0.1)  # tumbling nose-down
            cos_b = math.cos(bomb_angle); sin_b = math.sin(bomb_angle)

            def bpt(along, across):
                return (int(bsx + cos_b*along - sin_b*across),
                        int(bsy + sin_b*along + cos_b*across))

            # Bomb body
            body_bomb = [bpt(-14,-4), bpt(-14,4), bpt(12,4), bpt(14,0), bpt(12,-4)]
            pygame.draw.polygon(surf, (55,52,40), body_bomb)
            pygame.draw.polygon(surf, (75,72,55), body_bomb, 1)
            # Nose cone
            pygame.draw.polygon(surf, (180,70,20),
                [bpt(12,-4), bpt(12,4), bpt(20,0)])
            # Tail fins (4 fins, X pattern — draw 2 visible)
            for fin_sign in (-1, 1):
                fin_pts = [bpt(-14, fin_sign*4), bpt(-22, fin_sign*12), bpt(-10, fin_sign*4)]
                pygame.draw.polygon(surf, (45,42,32), fin_pts)
                pygame.draw.polygon(surf, (65,62,48), fin_pts, 1)
            # Warning stripe
            pygame.draw.line(surf, (220,180,0), bpt(-6,-4), bpt(-6,4), 2)
            pygame.draw.line(surf, (220,180,0), bpt(-2,-4), bpt(-2,4), 2)

            # Ground impact warning shadow
            fall_ratio = min(1.0, bm["y"] / max(1, GROUND_Y))
            wa = int(fall_ratio * 130)
            ws = pygame.Surface((40,10), pygame.SRCALPHA)
            pygame.draw.ellipse(ws, (255,60,20,wa), (0,0,40,10))
            surf.blit(ws, (bsx-20, GROUND_Y-5))

        # ── HP bar ────────────────────────────────────────────────────────────
        bw = 90; bx3 = cx2 - bw//2; by3 = int(self.y) - 18
        pygame.draw.rect(surf, (10,10,10), (bx3,by3,bw,5), border_radius=2)
        hp_r = self.hp / self.MAX_HP
        hc2  = (50,200,80) if hp_r > 0.5 else (220,40,40)
        if hp_r > 0:
            pygame.draw.rect(surf, hc2, (bx3,by3,int(bw*hp_r),5), border_radius=2)
        pygame.draw.rect(surf, (70,70,80), (bx3,by3,bw,5), 1, border_radius=2)
        lf2 = pygame.font.SysFont("consolas", 8, bold=True)
        surf.blit(lf2.render("B-2", True, (160,180,200)), (cx2-8, by3-11))

class Boss:
    W = 80; H = 100; is_air = False

    PHASE2_HP_FRAC = 0.83
    PHASE3_HP_FRAC = 0.66
    PHASE4_HP_FRAC = 0.50
    PHASE5_HP_FRAC = 0.33
    PHASE6_HP_FRAC = 0.16

    def __init__(self, x, y):
        diff = get_diff()
        self.x = float(x); self.y = float(y); self.vy = 0.0
        self.MAX_HP = int(3500 * diff["enemy_hp_mult"])
        self.hp = self.MAX_HP
        self.alive = True
        self.facing = -1
        self.phase = 1
        self._phase_locked = 1
        self.phase_transition_timer = 0
        self.transition_anim = 0

        self.walk_frame = 0; self.walk_timer = 0
        self.on_ground = False
        self.roar_done = False

        self.last_shot = 0
        self.burst_count = 0; self.burst_cd = 0

        self.rocket_timer = 180
        self.summon_timer = 300
        self.shield_active = False
        self.shield_hp = 0
        self.shield_max_hp = int(400 * diff["enemy_hp_mult"])

        self.hover_y = float(y) - 220
        self.emp_timer = 220
        self.mg_burst = 0; self.mg_cd = 0
        self.dash_timer = 160; self.dashing = False; self.dash_vx = 0.0
        self.clone_timer = 400

        self.rage_rockets_timer = 80
        self.stomp_timer = 200; self.stomp_anim = 0
        self.laser_charge = 0; self.laser_firing = False; self.laser_timer = 0
        self.orbital_angle = 0.0

        # V7.0: Phase 5 — clone decoys
        self.clones = []
        self.clone_spawn_timer = 0

        # V7.0: Phase 6 — OMEGA PRIME final form
        self.plasma_orbs = []
        self.plasma_timer = 40
        self.gravity_pull_active = False
        self.gravity_timer = 0
        self.final_rage = False
        self.death_spiral_angle = 0.0
        self.death_countdown = 0

        self.aura_pulse = 0.0
        self.shield_flash = 0
        self._spawn_list = None

    @property
    def rect(self): return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    @property
    def phase2_hp(self): return int(self.MAX_HP * self.PHASE2_HP_FRAC)
    @property
    def phase3_hp(self): return int(self.MAX_HP * self.PHASE3_HP_FRAC)
    @property
    def phase4_hp(self): return int(self.MAX_HP * self.PHASE4_HP_FRAC)
    @property
    def phase5_hp(self): return int(self.MAX_HP * self.PHASE5_HP_FRAC)
    @property
    def phase6_hp(self): return int(self.MAX_HP * self.PHASE6_HP_FRAC)

    def take_damage(self, amount):
        if self.phase == 2 and self.shield_active and self.shield_hp > 0:
            self.shield_hp -= amount
            PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 8)
            SFX.play(SFX.shield_hit)
            if self.shield_hp <= 0:
                self.shield_active = False
                SFX.play(SFX.big_explosion)
                PARTICLES.spawn_explosion(self.rect.centerx, self.rect.centery, scale=1.2)
            return
        if self.phase_transition_timer > 0:
            self.shield_flash = 6; return

        self.hp -= amount
        self.shield_flash = 8
        SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_blood(self.rect.centerx, self.rect.centery)

        thresholds = [
            (1, self.phase2_hp, 2),
            (2, self.phase3_hp, 3),
            (3, self.phase4_hp, 4),
            (4, self.phase5_hp, 5),
            (5, self.phase6_hp, 6),
        ]
        for locked, threshold, new_phase in thresholds:
            if self._phase_locked == locked and self.hp < threshold:
                self.hp = threshold
                self._trigger_phase_change(new_phase)
                return

        if self._phase_locked == 6 and self.hp <= 0:
            self.hp = 0
            self.alive = False
            PARTICLES.spawn_tank_death(self.rect.centerx, self.rect.centery)
            SFX.play(SFX.big_explosion)

    def _trigger_phase_change(self, new_phase):
        global screen_shake
        self._phase_locked = new_phase
        self.phase = new_phase
        self.phase_transition_timer = 180
        self.transition_anim = 180
        screen_shake = 25
        SFX.play(SFX.boss_roar)
        PARTICLES.spawn_explosion(self.rect.centerx, self.rect.centery, scale=4.0)
        if new_phase == 2:
            self.shield_active = True; self.shield_hp = self.shield_max_hp
        if new_phase == 3:
            self.hover_y = self.y - 220
        if new_phase in (4,5,6):
            self.hover_y = self.y - 300
        if new_phase == 5:
            # Spawn 2 decoy clones
            for side in (-1, 1):
                self.clones.append({
                    "x": self.x + side*250, "y": self.y,
                    "hp": int(200*get_diff()["enemy_hp_mult"]),
                    "alive": True, "facing": side,
                    "pulse": random.uniform(0,6.28),
                })
        if new_phase == 6:
            self.final_rage = True
            self.gravity_timer = 0
            screen_shake = 30

    def _do_gravity(self):
        self.vy = min(self.vy+0.7,18); self.y+=self.vy; self.on_ground=False
        for plat in current_platforms:
            r=self.rect
            if r.colliderect(plat) and self.vy>=0:
                if r.bottom-self.vy<=plat.top+abs(self.vy)+2:
                    self.y=plat.top-self.H; self.vy=0; self.on_ground=True

    def update(self, player, bullets, enemy_rockets):
        global screen_shake
        if not self.roar_done: SFX.play(SFX.boss_roar); self.roar_done=True
        self.aura_pulse=(self.aura_pulse+0.04)%(2*math.pi)
        if self.shield_flash>0: self.shield_flash-=1
        if self.transition_anim>0: self.transition_anim-=1
        if self.stomp_anim>0: self.stomp_anim-=1

        if self.phase_transition_timer>0:
            self.phase_transition_timer-=1
            screen_shake=5
            if self.phase>=3: self.y+=(self.hover_y-self.y)*0.04
            return

        diff=get_diff()
        ox=self.rect.centerx; oy=self.rect.centery
        dx=player.x-self.x
        dist=math.hypot(player.rect.centerx-ox,player.rect.centery-oy)

        # ── PHASE 1: Ground brawler ───────────────────────────────────────
        if self.phase==1:
            self._do_gravity()
            sp=2.8*diff["enemy_speed_mult"]
            if abs(dx)>10:
                self.x+=sp*(1 if dx>0 else -1); self.facing=1 if dx>0 else -1
                self.walk_timer+=1
                if self.walk_timer>5: self.walk_frame=(self.walk_frame+1)%4; self.walk_timer=0
            if self.on_ground and abs(dx)>150 and random.random()<0.018: self.vy=-22
            if self.on_ground and abs(dx)<120 and self.stomp_timer<=0:
                self.stomp_anim=20; self.stomp_timer=180; screen_shake=12
                SFX.play(SFX.big_explosion)
                PARTICLES.spawn_explosion(self.rect.centerx,self.y+self.H,scale=0.8)
                if abs(player.y+player.H-(self.y+self.H))<30: player.stun_timer=80
            if self.stomp_timer>0: self.stomp_timer-=1
            now=pygame.time.get_ticks()
            if now-self.last_shot>=int(500*diff["shoot_rate_mult"]) and dist<950:
                self.last_shot=now; self.burst_count=5; self.burst_cd=0
            if self.burst_count>0 and self.burst_cd<=0:
                self.burst_count-=1; self.burst_cd=7
                angle=math.atan2(player.rect.centery-oy,player.rect.centerx-ox)
                for off in (-0.10,0,0.10):
                    bullets.append(Bullet(ox,oy,math.cos(angle+off)*14,math.sin(angle+off)*14,
                                          int(18*diff["enemy_dmg_mult"]),(255,80,80)))
                SFX.play(SFX.shoot_rifle)
            if self.burst_cd>0: self.burst_cd-=1

        # ── PHASE 2: Shield + rockets ─────────────────────────────────────
        elif self.phase==2:
            self._do_gravity()
            sp=3.4*diff["enemy_speed_mult"]
            if abs(dx)>10:
                self.x+=sp*(1 if dx>0 else -1); self.facing=1 if dx>0 else -1
            if not self.shield_active and self.shield_hp<=0:
                self.clone_timer-=1
                if self.clone_timer<=0:
                    self.shield_active=True; self.shield_hp=self.shield_max_hp
                    self.clone_timer=500
            now=pygame.time.get_ticks()
            if now-self.last_shot>=int(380*diff["shoot_rate_mult"]) and dist<1000:
                self.last_shot=now; self.burst_count=7; self.burst_cd=0
            if self.burst_count>0 and self.burst_cd<=0:
                self.burst_count-=1; self.burst_cd=5
                angle=math.atan2(player.rect.centery-oy,player.rect.centerx-ox)
                for off in (-0.16,-0.08,0,0.08,0.16):
                    bullets.append(Bullet(ox,oy,math.cos(angle+off)*15,math.sin(angle+off)*15,
                                          int(20*diff["enemy_dmg_mult"]),(255,60,60)))
            if self.burst_cd>0: self.burst_cd-=1
            self.rocket_timer-=1
            if self.rocket_timer<=0:
                self.rocket_timer=int(190*diff["shoot_rate_mult"])
                d2=math.hypot(player.rect.centerx-ox,player.rect.centery-oy) or 1
                enemy_rockets.append(Rocket(ox,oy,(player.rect.centerx-ox)/d2*12,
                                            (player.rect.centery-oy)/d2*12,
                                            int(42*diff["enemy_dmg_mult"]),ROCKET_COL))
                SFX.play(SFX.shoot_rocket); screen_shake=8

        # ── PHASE 3: Airborne, MG fire ────────────────────────────────────
        elif self.phase==3:
            self.y+=(self.hover_y-self.y)*0.06; self.vy=0
            drift=4.2*diff["enemy_speed_mult"]
            if abs(dx)>80: self.x+=drift*(1 if dx>0 else -1)
            self.facing=1 if dx>0 else -1
            self.dash_timer-=1
            if self.dash_timer<=0 and not self.dashing:
                self.dash_timer=int(180*diff["shoot_rate_mult"]); self.dashing=True
                self.dash_vx=self.facing*26
                PARTICLES.spawn_explosion(ox,oy,scale=1.2); screen_shake=12
            if self.dashing:
                self.x+=self.dash_vx; self.dash_vx*=0.86
                if abs(self.dash_vx)<1.5: self.dashing=False
            now=pygame.time.get_ticks()
            if now-self.last_shot>=int(100*diff["shoot_rate_mult"]):
                self.last_shot=now; self.mg_burst=12; self.mg_cd=0
            if self.mg_burst>0 and self.mg_cd<=0:
                self.mg_burst-=1; self.mg_cd=3
                angle=math.atan2(player.rect.centery-oy,player.rect.centerx-ox)
                bullets.append(Bullet(ox,oy,math.cos(angle+random.uniform(-0.2,0.2))*17,
                                      math.sin(angle+random.uniform(-0.2,0.2))*17,
                                      int(15*diff["enemy_dmg_mult"]),(255,30,30)))
            if self.mg_cd>0: self.mg_cd-=1
            self.emp_timer-=1
            if self.emp_timer<=0:
                self.emp_timer=int(260*diff["shoot_rate_mult"])
                for i in range(18):
                    ang2=(i/18)*2*math.pi
                    bullets.append(Bullet(ox,oy,math.cos(ang2)*13,math.sin(ang2)*13,
                                          int(22*diff["enemy_dmg_mult"]),EMP_COL))
                PARTICLES.spawn_explosion(ox,oy,scale=2.2); screen_shake=16
            self.rocket_timer-=1
            if self.rocket_timer<=0:
                self.rocket_timer=int(220*diff["shoot_rate_mult"])
                for _ in range(5):
                    enemy_rockets.append(Rocket(ox+random.randint(-280,280),oy,
                                                random.uniform(-3,3),9,
                                                int(36*diff["enemy_dmg_mult"]),ROCKET_COL))

        # ── PHASE 4: RAGE ────────────────────────────────────────────────
        elif self.phase==4:
            self.y+=(self.hover_y-self.y)*0.08; self.vy=0
            drift2=6.0*diff["enemy_speed_mult"]
            if abs(dx)>60: self.x+=drift2*(1 if dx>0 else -1)
            self.facing=1 if dx>0 else -1
            self.dash_timer-=1
            if self.dash_timer<=0 and not self.dashing:
                self.dash_timer=int(110*diff["shoot_rate_mult"]); self.dashing=True
                self.dash_vx=self.facing*34; screen_shake=16
            if self.dashing:
                self.x+=self.dash_vx; self.dash_vx*=0.84
                if abs(self.dash_vx)<2.0: self.dashing=False
            self.laser_charge+=1
            if self.laser_charge>int(45*diff["shoot_rate_mult"]) and not self.laser_firing:
                self.laser_firing=True; self.laser_timer=30; self.laser_charge=0
            if self.laser_firing:
                self.laser_timer-=1
                if self.laser_timer%3==0:
                    angle=math.atan2(player.rect.centery-oy,player.rect.centerx-ox)
                    bullets.append(Bullet(ox,oy,math.cos(angle)*20,math.sin(angle)*20,
                                          int(22*diff["enemy_dmg_mult"]),(255,30,255),is_sniper=True))
                if self.laser_timer<=0: self.laser_firing=False
            self.orbital_angle+=0.06
            self.rage_rockets_timer-=1
            if self.rage_rockets_timer<=0:
                self.rage_rockets_timer=int(55*diff["shoot_rate_mult"])
                for i2 in range(8):
                    ang4=(i2/8)*2*math.pi+self.orbital_angle
                    bullets.append(Bullet(ox,oy,math.cos(ang4)*11,math.sin(ang4)*11,
                                          int(16*diff["enemy_dmg_mult"]),(255,50,255)))
                d4=math.hypot(player.rect.centerx-ox,player.rect.centery-oy) or 1
                for _ in range(2):
                    jit=random.uniform(-0.25,0.25)
                    enemy_rockets.append(Rocket(ox,oy,
                                                (player.rect.centerx-ox)/d4*14+jit,
                                                (player.rect.centery-oy)/d4*14+jit,
                                                int(35*diff["enemy_dmg_mult"]),ROCKET_COL))

        # ── PHASE 5: CLONES + PLASMA ──────────────────────────────────────
        elif self.phase==5:
            self.y+=(self.hover_y-self.y)*0.09; self.vy=0
            if abs(dx)>60: self.x+=7*(1 if dx>0 else -1)*diff["enemy_speed_mult"]
            self.facing=1 if dx>0 else -1
            # Update clones
            for clone in self.clones:
                if not clone["alive"]: continue
                cdx=player.x-clone["x"]
                clone["x"]+=3.5*(1 if cdx>0 else -1)*diff["enemy_speed_mult"]
                clone["facing"]=1 if cdx>0 else -1
                clone["pulse"]=(clone["pulse"]+0.06)%(2*math.pi)
                if random.random()<0.015:
                    angle=math.atan2(player.rect.centery-clone["y"],
                                     player.rect.centerx-clone["x"])
                    for off in (-0.2,0,0.2):
                        bullets.append(Bullet(int(clone["x"]),int(clone["y"]),
                                              math.cos(angle+off)*14,math.sin(angle+off)*14,
                                              int(18*diff["enemy_dmg_mult"]),(200,60,255)))
            # Plasma orbs — homing slow projectiles
            self.plasma_timer-=1
            if self.plasma_timer<=0:
                self.plasma_timer=int(55*diff["shoot_rate_mult"])
                self.plasma_orbs.append({
                    "x":float(ox),"y":float(oy),
                    "vx":random.uniform(-5,5),"vy":random.uniform(-5,5),
                    "life":240,"homing":True,
                    "dmg":int(30*diff["enemy_dmg_mult"]),
                })
            for orb in self.plasma_orbs:
                if orb["homing"] and orb["life"]>120:
                    pdx=player.rect.centerx-orb["x"]
                    pdy=player.rect.centery-orb["y"]
                    pd=math.hypot(pdx,pdy) or 1
                    orb["vx"]+=(pdx/pd*8-orb["vx"])*0.06
                    orb["vy"]+=(pdy/pd*8-orb["vy"])*0.06
                orb["x"]+=orb["vx"]; orb["y"]+=orb["vy"]
                orb["life"]-=1
                if math.hypot(player.rect.centerx-orb["x"],player.rect.centery-orb["y"])<22:
                    player.take_damage(orb["dmg"])
                    orb["life"]=0
                    PARTICLES.spawn_explosion(orb["x"],orb["y"],scale=0.8)
                PARTICLES.spawn_neon_spark(orb["x"],orb["y"],PLASMA_COL)
            self.plasma_orbs=[o for o in self.plasma_orbs if o["life"]>0]
            # Still shooting
            now=pygame.time.get_ticks()
            if now-self.last_shot>=int(80*diff["shoot_rate_mult"]):
                self.last_shot=now
                angle=math.atan2(player.rect.centery-oy,player.rect.centerx-ox)
                bullets.append(Bullet(ox,oy,math.cos(angle)*18,math.sin(angle)*18,
                                      int(20*diff["enemy_dmg_mult"]),(255,50,255)))

        # ── PHASE 6: OMEGA PRIME FINAL FORM ──────────────────────────────
        elif self.phase==6:
            self.y+=(self.hover_y-self.y)*0.12; self.vy=0
            # Gravity pull — sucks player in
            self.gravity_timer+=1
            self.gravity_pull_active=(self.gravity_timer%180<60)
            if self.gravity_pull_active:
                pdx=self.rect.centerx-player.rect.centerx
                pdy=self.rect.centery-player.rect.centery
                pd=math.hypot(pdx,pdy) or 1
                pull_str=0.9
                player.vx+=pdx/pd*pull_str
                player.vy+=pdy/pd*pull_str*0.5
                if pd<60: player.take_damage(int(2*diff["enemy_dmg_mult"]))
            # Death spiral bullets
            self.death_spiral_angle+=0.08
            self.rage_rockets_timer-=1
            if self.rage_rockets_timer<=0:
                self.rage_rockets_timer=int(25*diff["shoot_rate_mult"])
                for i3 in range(16):
                    ang5=(i3/16)*2*math.pi+self.death_spiral_angle
                    sp5=8+abs(math.sin(self.death_spiral_angle))*6
                    col5=(255,50,255) if i3%2==0 else (255,200,50)
                    bullets.append(Bullet(ox,oy,math.cos(ang5)*sp5,math.sin(ang5)*sp5,
                                          int(20*diff["enemy_dmg_mult"]),col5))
                # Rocket barrage
                d6=math.hypot(player.rect.centerx-ox,player.rect.centery-oy) or 1
                for _ in range(3):
                    jit2=random.uniform(-0.4,0.4)
                    enemy_rockets.append(Rocket(ox,oy,
                                                (player.rect.centerx-ox)/d6*16+jit2,
                                                (player.rect.centery-oy)/d6*16+jit2,
                                                int(40*diff["enemy_dmg_mult"]),PLASMA_COL))
                SFX.play(SFX.shoot_rocket)
                screen_shake=4
            # Plasma orbs
            self.plasma_timer-=1
            if self.plasma_timer<=0:
                self.plasma_timer=int(30*diff["shoot_rate_mult"])
                for _ in range(3):
                    self.plasma_orbs.append({
                        "x":float(ox+random.randint(-40,40)),
                        "y":float(oy+random.randint(-20,20)),
                        "vx":random.uniform(-7,7),"vy":random.uniform(-7,7),
                        "life":180,"homing":True,
                        "dmg":int(35*diff["enemy_dmg_mult"]),
                    })
            for orb2 in self.plasma_orbs:
                if orb2["homing"]:
                    pdx2=player.rect.centerx-orb2["x"]
                    pdy2=player.rect.centery-orb2["y"]
                    pd2=math.hypot(pdx2,pdy2) or 1
                    orb2["vx"]+=(pdx2/pd2*9-orb2["vx"])*0.09
                    orb2["vy"]+=(pdy2/pd2*9-orb2["vy"])*0.09
                orb2["x"]+=orb2["vx"]; orb2["y"]+=orb2["vy"]
                orb2["life"]-=1
                if math.hypot(player.rect.centerx-orb2["x"],player.rect.centery-orb2["y"])<22:
                    player.take_damage(orb2["dmg"]); orb2["life"]=0
                    PARTICLES.spawn_explosion(orb2["x"],orb2["y"],scale=0.9)
            self.plasma_orbs=[o for o in self.plasma_orbs if o["life"]>0]
            # Summon enemies continuously
            self.summon_timer-=1
            if self.summon_timer<=0:
                self.summon_timer=int(120*diff["shoot_rate_mult"])
                if self._spawn_list is not None:
                    sx3=max(50,min(WORLD_WIDTH-50,self.x+random.choice([-300,300])))
                    gy3=current_platforms[0].top-Enemy.H
                    self._spawn_list.append(Enemy(sx3,gy3,
                        hp=int(100*diff["enemy_hp_mult"]),
                        speed=4.5*diff["enemy_speed_mult"],
                        shoot_rate=int(500*diff["shoot_rate_mult"])))
                    PARTICLES.spawn_explosion(sx3,gy3,scale=0.7)

        self.x=max(50,min(WORLD_WIDTH-self.W-50,self.x))

    def draw(self, surf, cam_x=0):
        sx   = int(self.x) - cam_x
        cx   = sx + self.W // 2
        cy   = int(self.y)
        f    = self.facing
        tick = pygame.time.get_ticks()

        phase_body_col = {1:(160,40,40),2:(200,80,20),3:(90,20,130),
                          4:(160,10,160),5:(40,20,180),6:(100,0,200)}[self.phase]
        glow_col = {1:(255,80,80),2:(255,140,40),3:(220,60,255),
                    4:(255,20,255),5:(80,80,255),6:(200,50,255)}[self.phase]

        # Aura
        aura_r=int(70+self.phase*20+math.sin(self.aura_pulse)*14)
        aura=pygame.Surface((aura_r*2+4,aura_r*2+4),pygame.SRCALPHA)
        aura_a=int(30+self.phase*8+math.sin(self.aura_pulse)*14)
        pygame.draw.ellipse(aura,(*glow_col,aura_a),(0,0,aura_r*2+4,aura_r*2+4))
        surf.blit(aura,(cx-aura_r-2,cy+self.H//2-aura_r-2))

        # Clone decoys (phase 5)
        if self.phase==5:
            for clone in self.clones:
                if not clone["alive"]: continue
                ccx=int(clone["x"])-cam_x; ccy=int(clone["y"])
                pulse2=abs(math.sin(clone["pulse"]))*20
                cs2=pygame.Surface((90,90),pygame.SRCALPHA)
                pygame.draw.ellipse(cs2,(80,40,200,int(40+pulse2)),(0,0,90,90))
                pygame.draw.ellipse(cs2,(140,80,255,int(80+pulse2)),(5,5,80,80),2)
                surf.blit(cs2,(ccx-45,ccy-10))
                # Clone body (simplified boss silhouette)
                pygame.draw.rect(surf,(80,40,200),(ccx-20,ccy,40,45),border_radius=4)
                pygame.draw.rect(surf,(100,60,220),(ccx-20,ccy,40,10),border_radius=4)
                eye_a2=int(160+abs(math.sin(tick*0.12+clone["pulse"]))*90)
                es2=pygame.Surface((14,14),pygame.SRCALPHA)
                pygame.draw.circle(es2,(220,80,255,eye_a2),(7,7),7)
                surf.blit(es2,(ccx-7,ccy+14))
                clone_lf=pygame.font.SysFont("consolas",8,bold=True)
                surf.blit(clone_lf.render("KLON",True,(180,80,255)),(ccx-10,ccy-12))

        # Phase 6: gravity pull vortex
        if self.phase==6 and self.gravity_pull_active:
            for ri in range(6):
                vr=int(30+ri*18+abs(math.sin(tick*0.08+ri))*15)
                va=int(60-ri*8)
                if va>0:
                    vs2=pygame.Surface((vr*2+4,vr*2+4),pygame.SRCALPHA)
                    pygame.draw.circle(vs2,(*glow_col,va),(vr+2,vr+2),vr,2)
                    surf.blit(vs2,(cx-vr-2,cy+self.H//2-vr-2))
            gf=pygame.font.SysFont("consolas",13,bold=True)
            gt=gf.render("⚠ GRAVITATIONSFELD",True,glow_col)
            gt.set_alpha(int(128+abs(math.sin(tick*0.06))*127))
            surf.blit(gt,(cx-gt.get_width()//2,cy-55))

        # Phase 5/6: plasma orbs
        for orb3 in self.plasma_orbs:
            osx=int(orb3["x"])-cam_x; osy=int(orb3["y"])
            pulse3=abs(math.sin(tick*0.1+orb3["x"]*0.01))*5
            r3=int(10+pulse3)
            os2=pygame.Surface((r3*3+2,r3*3+2),pygame.SRCALPHA)
            pygame.draw.circle(os2,(*PLASMA_COL,150),(r3*3//2+1,r3*3//2+1),r3*2)
            pygame.draw.circle(os2,(*PLASMA_GLOW,220),(r3*3//2+1,r3*3//2+1),r3)
            pygame.draw.circle(os2,(255,255,255,200),(r3*3//2+1,r3*3//2+1),r3//2)
            surf.blit(os2,(osx-r3*3//2-1,osy-r3*3//2-1))
            LIGHTS.add(osx+cam_x,osy,30,PLASMA_COL,0.7,life=1)

        # Shield (phase 2)
        if self.phase==2 and self.shield_active and self.shield_hp>0:
            ratio=self.shield_hp/self.shield_max_hp
            pulse4=abs(math.sin(tick*0.006))*28
            shld_r=80
            ss3=pygame.Surface((shld_r*2+4,shld_r*2+4),pygame.SRCALPHA)
            pygame.draw.circle(ss3,(80,160,255,int((35+pulse4)*ratio)),(shld_r+2,shld_r+2),shld_r)
            pygame.draw.circle(ss3,(140,210,255,int(90*ratio)),(shld_r+2,shld_r+2),shld_r,3)
            surf.blit(ss3,(cx-shld_r-2,cy+self.H//2-shld_r-2))

        # Hit flash
        if self.shield_flash>0:
            sf3=pygame.Surface((self.W+16,self.H+16),pygame.SRCALPHA)
            pygame.draw.ellipse(sf3,(255,255,255,self.shield_flash*22),(0,0,self.W+16,self.H+16))
            surf.blit(sf3,(sx-8,cy-8))

        # Phase 3+ wings
        if self.phase>=3:
            flap=int(math.sin(tick*0.07)*14)
            pygame.draw.polygon(surf,phase_body_col,
                [(cx-12,cy+45),(cx-68,cy+16+flap),(cx-74,cy+66+flap),(cx-22,cy+70)])
            pygame.draw.polygon(surf,phase_body_col,
                [(cx+12,cy+45),(cx+68,cy+16+flap),(cx+74,cy+66+flap),(cx+22,cy+70)])

        # Legs (phases 1-2)
        if self.phase<3:
            lo=[0,9,0,-9][self.walk_frame]
            pygame.draw.line(surf,phase_body_col,(cx-12,cy+72),(cx-12,cy+100+lo),14)
            pygame.draw.line(surf,phase_body_col,(cx+12,cy+72),(cx+12,cy+100-lo),14)
            pygame.draw.rect(surf,(30,15,15),pygame.Rect(cx-24,cy+94+lo,20,14))
            pygame.draw.rect(surf,(30,15,15),pygame.Rect(cx+4,cy+94-lo,20,14))

        # Torso
        pygame.draw.rect(surf,phase_body_col,pygame.Rect(cx-26,cy+26,52,50))
        lighter=(min(255,phase_body_col[0]+45),min(255,phase_body_col[1]+22),min(255,phase_body_col[2]+22))
        pygame.draw.rect(surf,lighter,pygame.Rect(cx-20,cy+30,40,20))
        pygame.draw.rect(surf,phase_body_col,pygame.Rect(cx-40,cy+22,18,26),border_radius=5)
        pygame.draw.rect(surf,phase_body_col,pygame.Rect(cx+22,cy+22,18,26),border_radius=5)

        # Phase 5/6: energy wings
        if self.phase>=5:
            wing_a=int(80+abs(math.sin(tick*0.06))*120)
            for wi in range(5):
                wang=(wi/5)*math.pi-math.pi/2
                wlen=55+wi*15+abs(math.sin(tick*0.05+wi))*20
                for side in (-1,1):
                    wx2=int(cx+side*math.cos(wang)*wlen)
                    wy2=int(cy+40+math.sin(wang)*wlen*0.5)
                    ws3=pygame.Surface((8,8),pygame.SRCALPHA)
                    pygame.draw.circle(ws3,(*glow_col,wing_a),(4,4),4)
                    surf.blit(ws3,(wx2-4,wy2-4))
                    if wi>0:
                        prev_wang=((wi-1)/5)*math.pi-math.pi/2
                        prev_wlen=55+(wi-1)*15
                        pwx=int(cx+side*math.cos(prev_wang)*prev_wlen)
                        pwy=int(cy+40+math.sin(prev_wang)*prev_wlen*0.5)
                        pygame.draw.line(surf,(*glow_col,wing_a//2),(pwx,pwy),(wx2,wy2),2)

        # Core
        core_a=int(150+math.sin(tick*0.09)*105)
        core_r=9+self.phase*4
        cs3=pygame.Surface((core_r*2+2,core_r*2+2),pygame.SRCALPHA)
        pygame.draw.circle(cs3,(*glow_col,core_a),(core_r+1,core_r+1),core_r)
        surf.blit(cs3,(cx-core_r-1,cy+34))
        LIGHTS.add(cx+cam_x,cy+38,50,glow_col,0.8,life=1)

        # Arms
        pygame.draw.line(surf,phase_body_col,(cx,cy+32),(cx+f*44,cy+48),10)
        pygame.draw.rect(surf,(30,30,30),pygame.Rect(cx+f*32,cy+44,24,10))

        # Head
        pygame.draw.rect(surf,(140,80,70),pygame.Rect(cx-10,cy+14,20,14))
        pygame.draw.circle(surf,(175,105,85),(cx,cy+10),20)

        # Phase helmet
        helm_col={1:(55,18,18),2:(75,28,8),3:(55,10,80),
                  4:(80,5,90),5:(20,15,100),6:(60,0,120)}[self.phase]
        pygame.draw.arc(surf,helm_col,pygame.Rect(cx-22,cy-14,44,28),0,math.pi,9)
        pygame.draw.rect(surf,helm_col,pygame.Rect(cx-22,cy+4,44,12))

        # Eyes
        eye_col=(255,30,255) if self.phase>=3 else (255,130,20) if self.phase==2 else (255,30,30)
        if self.phase>=5: eye_col=(80,80,255)
        if self.phase==6: eye_col=PLASMA_COL
        eye_a2=int(190+math.sin(tick*0.12)*65)
        for ex2,ey2 in ((cx-16,cy+4),(cx+6,cy+4)):
            es3=pygame.Surface((10,10),pygame.SRCALPHA)
            pygame.draw.circle(es3,(*eye_col,eye_a2),(5,5),5)
            surf.blit(es3,(ex2,ey2))

        # Phase 6: crown of destruction
        if self.phase==6:
            for crown_i in range(8):
                ca3=crown_i/8*2*math.pi+tick*0.07
                cr3=int(26+abs(math.sin(tick*0.08+crown_i))*12)
                cex=int(cx+math.cos(ca3)*cr3)
                cey=int(cy-18+math.sin(ca3)*cr3*0.4)
                cs4=pygame.Surface((12,12),pygame.SRCALPHA)
                pygame.draw.circle(cs4,(255,random.randint(40,140),255,200),(6,6),6)
                surf.blit(cs4,(cex-6,cey-6))
                LIGHTS.add(cex+cam_x,cey,20,PLASMA_COL,0.6,life=1)

        # HP bar — 6-segment
        bw=200; bx2=cx-bw//2; by2=cy-42
        pygame.draw.rect(surf,(18,6,6),(bx2,by2,bw,18),border_radius=5)
        hp_r=self.hp/self.MAX_HP
        bar_col={1:(200,50,50),2:(220,110,20),3:(190,40,220),
                 4:(240,20,240),5:(60,60,220),6:(160,0,255)}[self.phase]
        fw2=int(bw*hp_r)
        if fw2>0:
            pygame.draw.rect(surf,bar_col,(bx2,by2,fw2,18),border_radius=5)
            sh2=pygame.Surface((fw2,5),pygame.SRCALPHA)
            sh2.fill((255,255,255,45)); surf.blit(sh2,(bx2,by2+1))
        pygame.draw.rect(surf,(255,255,255),(bx2,by2,bw,18),1,border_radius=5)
        # Phase segment lines (5 dividers for 6 phases)
        for i in range(1,6):
            lx2=bx2+int(bw*i/6)
            pygame.draw.line(surf,(255,255,255),(lx2,by2),(lx2,by2+18),1)
        lf2=pygame.font.SysFont("consolas",13,bold=True)
        lb2=lf2.render(f"GENERAL OMEGA  ▶ PHASE {self.phase}/6",True,(255,200,50))
        surf.blit(lb2,(cx-lb2.get_width()//2,by2-20))
        if self.phase_transition_timer>0:
            inv_f=pygame.font.SysFont("consolas",14,bold=True)
            inv_t=inv_f.render("PHASE WECHSEL!",True,glow_col)
            inv_t.set_alpha(int(128+abs(math.sin(tick*0.15))*127))
            surf.blit(inv_t,(cx-inv_t.get_width()//2,by2-44))
# ═══════════════════════════════════════════════════
#  SCREEN SHAKE
# ═══════════════════════════════════════════════════
def get_shake_offset():
    global screen_shake
    if screen_shake>0:
        screen_shake=max(0,screen_shake-1)
        if SETTINGS.get("screenshake", True):
            ox=random.randint(-screen_shake,screen_shake)
            oy=random.randint(-screen_shake,screen_shake)
            return ox,oy
    return 0,0

# ═══════════════════════════════════════════════════
#  FONTS & HUD
# ═══════════════════════════════════════════════════
font_big   = pygame.font.SysFont("consolas",28,bold=True)
font_med   = pygame.font.SysFont("consolas",22,bold=True)
font_small = pygame.font.SysFont("consolas",16)
font_tiny  = pygame.font.SysFont("consolas",13)
_FONT_CACHE: dict = {}
def get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont("consolas", size, bold=bold)
    return _FONT_CACHE[key]

# ═══════════════════════════════════════════════════
#  WEAPON WHEEL (GTA-style, hold Q)
# ═══════════════════════════════════════════════════
WHEEL_WEAPONS = [
    PISTOLE, STURMGEWEHR, SCHARFSCHUETZE, SCHROTFLINTE,
    RAKETENWERFER, STINGER, MESSER, FLAMMENWERFER, EMP_CANNON, RAILGUN
]
WHEEL_ICONS = ["🔫","⚡","🎯","💥","🚀","🎯","🔪","🔥","⚡","⚡"]
WHEEL_LABELS = ["Pistole","Sturmgewehr","Scharfschütze","Schrotflinte",
                "Raketenwerfer","Stinger AA","Messer","Flammenwerfer","EMP-Kanone","Railgun"]

class WeaponWheel:
    RADIUS       = 165
    SLOT_RADIUS  = 52
    BG_RADIUS    = 230
    SLOWMO       = 0.18

    def __init__(self):
        self.open     = False
        self.selected = 0
        self.anim     = 0.0
        self.cx       = WIDTH  // 2
        self.cy       = HEIGHT // 2

    def get_slot_pos(self, idx, n):
        angle = math.pi / 2 + (2 * math.pi * idx / n)
        x = self.cx + math.cos(angle) * self.RADIUS
        y = self.cy - math.sin(angle) * self.RADIUS
        return x, y

    def update(self, keys_held, mouse_pos):
        q_down = keys_held[pygame.K_q]
        if q_down and not self.open:
            self.open = True
        elif not q_down and self.open:
            self.open = False
        if self.open:
            self.anim = min(1.0, self.anim + 0.12)
            n = len(WHEEL_WEAPONS)
            best_dist = 9999; best_idx = self.selected
            for i in range(n):
                sx, sy = self.get_slot_pos(i, n)
                d = math.hypot(mouse_pos[0] - sx, mouse_pos[1] - sy)
                if d < best_dist:
                    best_dist = d; best_idx = i
            self.selected = best_idx
        else:
            self.anim = max(0.0, self.anim - 0.18)
        return self.open

    def _draw_weapon_art(self, surf, weapon, cx, cy, scale=1.0):
        """Draw a small pixel-art silhouette of each weapon centered at cx,cy."""
        s = scale
        c = (220, 220, 220)   # base silver
        dc = (140, 140, 140)  # dark detail

        if weapon == PISTOLE:
            # Body
            pygame.draw.rect(surf, c,  (int(cx-10*s), int(cy-4*s),  int(20*s), int(8*s)))
            # Barrel
            pygame.draw.rect(surf, c,  (int(cx+5*s),  int(cy-7*s),  int(12*s), int(4*s)))
            # Grip
            pygame.draw.rect(surf, dc, (int(cx-8*s),  int(cy+4*s),  int(8*s),  int(9*s)))
            # Trigger guard
            pygame.draw.rect(surf, dc, (int(cx-2*s),  int(cy+2*s),  int(4*s),  int(5*s)))

        elif weapon == STURMGEWEHR:
            # Long body
            pygame.draw.rect(surf, c,  (int(cx-18*s), int(cy-4*s),  int(36*s), int(8*s)))
            # Stock
            pygame.draw.rect(surf, dc, (int(cx-18*s), int(cy-6*s),  int(10*s), int(12*s)))
            # Magazine
            pygame.draw.rect(surf, dc, (int(cx-4*s),  int(cy+4*s),  int(8*s),  int(10*s)))
            # Barrel tip
            pygame.draw.rect(surf, c,  (int(cx+18*s), int(cy-2*s),  int(6*s),  int(4*s)))

        elif weapon == SCHARFSCHUETZE:
            # Very long barrel
            pygame.draw.rect(surf, c,  (int(cx-20*s), int(cy-3*s),  int(42*s), int(6*s)))
            # Stock
            pygame.draw.rect(surf, dc, (int(cx-20*s), int(cy-6*s),  int(12*s), int(12*s)))
            # Scope
            pygame.draw.rect(surf, (80,180,255), (int(cx-2*s), int(cy-9*s), int(14*s), int(6*s)))
            pygame.draw.circle(surf, (60,140,220), (int(cx+5*s), int(cy-6*s)), int(4*s))
            # Bipod legs
            pygame.draw.line(surf, dc,
                             (int(cx+10*s), int(cy+3*s)),
                             (int(cx+6*s),  int(cy+12*s)), max(1,int(2*s)))
            pygame.draw.line(surf, dc,
                             (int(cx+14*s), int(cy+3*s)),
                             (int(cx+18*s), int(cy+12*s)), max(1,int(2*s)))

        elif weapon == SCHROTFLINTE:
            # Double-barrel thick
            pygame.draw.rect(surf, c,  (int(cx-14*s), int(cy-6*s),  int(30*s), int(6*s)))
            pygame.draw.rect(surf, c,  (int(cx-14*s), int(cy+1*s),  int(30*s), int(6*s)))
            # Wooden stock
            pygame.draw.rect(surf, (140, 80, 30), (int(cx-18*s), int(cy-8*s), int(12*s), int(16*s)))
            # Barrel end circles
            pygame.draw.circle(surf, dc, (int(cx+16*s), int(cy-3*s)), int(3*s))
            pygame.draw.circle(surf, dc, (int(cx+16*s), int(cy+4*s)), int(3*s))

        elif weapon == RAKETENWERFER:
            # Tube
            pygame.draw.rect(surf, (60, 120, 60), (int(cx-20*s), int(cy-6*s),  int(40*s), int(12*s)))
            # Open back end
            pygame.draw.circle(surf, dc, (int(cx-20*s), int(cy)), int(6*s))
            # Front opening
            pygame.draw.circle(surf, (40,40,40), (int(cx+20*s), int(cy)), int(5*s))
            # Rocket warhead sticking out
            pygame.draw.rect(surf, ROCKET_COL, (int(cx+18*s), int(cy-4*s), int(10*s), int(8*s)))
            pygame.draw.polygon(surf, (255,160,60),
                                [(int(cx+28*s), int(cy)),
                                 (int(cx+22*s), int(cy-4*s)),
                                 (int(cx+22*s), int(cy+4*s))])
            # Grip
            pygame.draw.rect(surf, dc, (int(cx-4*s), int(cy+6*s), int(8*s), int(8*s)))

        elif weapon == STINGER:
            # Thicker tube, cyan tint
            pygame.draw.rect(surf, (30, 100, 100), (int(cx-22*s), int(cy-5*s), int(44*s), int(10*s)))
            # Back cone
            pygame.draw.polygon(surf, dc,
                                [(int(cx-22*s), int(cy-5*s)),
                                 (int(cx-22*s), int(cy+5*s)),
                                 (int(cx-28*s), int(cy))])
            # Front seeker head (cyan)
            pygame.draw.circle(surf, CYAN, (int(cx+22*s), int(cy)), int(6*s))
            pygame.draw.circle(surf, (180,255,255), (int(cx+22*s), int(cy)), int(3*s))
            # Shoulder rest
            pygame.draw.rect(surf, dc, (int(cx-8*s), int(cy+5*s), int(16*s), int(6*s)))

        elif weapon == MESSER:
            # Blade
            pygame.draw.polygon(surf, (200, 210, 230),
                                [(int(cx-14*s), int(cy+3*s)),
                                 (int(cx+16*s), int(cy)),
                                 (int(cx-14*s), int(cy-3*s))])
            # Fuller (groove)
            pygame.draw.line(surf, dc,
                             (int(cx-10*s), int(cy)),
                             (int(cx+10*s), int(cy)), max(1,int(1*s)))
            # Guard
            pygame.draw.rect(surf, dc, (int(cx-16*s), int(cy-6*s), int(5*s), int(12*s)))
            # Handle
            pygame.draw.rect(surf, (100, 60, 20), (int(cx-24*s), int(cy-4*s), int(10*s), int(8*s)))
            pygame.draw.line(surf, (140,90,40),
                             (int(cx-23*s), int(cy-2*s)),
                             (int(cx-16*s), int(cy-2*s)), max(1,int(1*s)))

        elif weapon == FLAMMENWERFER:
            # Tank on back (two cylinders)
            pygame.draw.ellipse(surf, (80,50,20),
                                (int(cx-20*s), int(cy-8*s), int(12*s), int(16*s)))
            pygame.draw.ellipse(surf, (100,65,25),
                                (int(cx-12*s), int(cy-8*s), int(12*s), int(16*s)))
            # Hose
            pygame.draw.line(surf, dc,
                             (int(cx-4*s), int(cy)),
                             (int(cx+8*s), int(cy)), max(2,int(3*s)))
            # Nozzle
            pygame.draw.rect(surf, (60,60,60), (int(cx+8*s), int(cy-4*s), int(14*s), int(8*s)))
            # Flame burst at tip
            for fi in range(5):
                angle_f = math.radians(-30 + fi*15)
                fx = int(cx + (22+fi*3)*s * math.cos(angle_f))
                fy = int(cy + (22+fi*3)*s * math.sin(angle_f))
                fc = [(255,240,80),(255,160,20),(255,80,10),(255,200,50),(255,120,0)][fi]
                pygame.draw.circle(surf, fc, (fx, fy), max(1, int((4-fi//2)*s)))

        elif weapon == EMP_CANNON:
            # Main body
            pygame.draw.rect(surf, (40, 80, 100), (int(cx-16*s), int(cy-5*s), int(32*s), int(10*s)))
            # Coil rings
            for ri in range(4):
                rx = int(cx - 10*s + ri*6*s)
                pygame.draw.circle(surf, EMP_COL, (rx, int(cy)), int(4*s), max(1,int(1*s)))
            # Front emitter dish
            pygame.draw.circle(surf, (60,200,200), (int(cx+16*s), int(cy)), int(6*s))
            pygame.draw.circle(surf, WHITE,        (int(cx+16*s), int(cy)), int(3*s))
            # EMP glow pulse
            pulse_r = int(3*s + abs(math.sin(pygame.time.get_ticks()*0.005))*3*s)
            gs_emp = pygame.Surface((pulse_r*4+4, pulse_r*4+4), pygame.SRCALPHA)
            pygame.draw.circle(gs_emp, (*EMP_COL, 60),
                               (pulse_r*2+2, pulse_r*2+2), pulse_r*2)
            surf.blit(gs_emp, (int(cx+16*s)-pulse_r*2-2, int(cy)-pulse_r*2-2))
            # Back stock
            pygame.draw.rect(surf, (30,60,80), (int(cx-22*s), int(cy-4*s), int(8*s), int(8*s)))

            # ── Level-Upgrade Overlay ─────────────────────────────────────────────
        lv = WSTATS.get_level(weapon.name) if hasattr(weapon, 'name') else 0
        if lv >= 2:
            gold_col = (255, 215, 0) if lv == 3 else (200, 160, 40)
            # Goldener Schimmer-Overlay
            shimmer = pygame.Surface((int(40*s), int(16*s)), pygame.SRCALPHA)
            shimmer.fill((*gold_col, 35))
            surf.blit(shimmer, (int(cx - 20*s), int(cy - 8*s)))
            # Goldene Akzentlinien
            for ai in range(lv):
                lx = int(cx - 12*s + ai * 10*s)
                pygame.draw.line(surf, gold_col,
                                 (lx, int(cy - 7*s)), (lx, int(cy - 3*s)),
                                 max(1, int(1.5*s)))

    def draw(self, surf, player):
        if self.anim <= 0.01:
            return
        n   = len(WHEEL_WEAPONS)
        t   = self.anim
        cx2 = self.cx; cy2 = self.cy

        # ── Dark vignette overlay ─────────────────────────────────────────────
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, int(160 * t)))
        surf.blit(ov, (0, 0))

        # ── Outer decorative ring ─────────────────────────────────────────────
        ring_r = int(self.BG_RADIUS * t)
        if ring_r > 0:
            pygame.draw.circle(surf, (60, 60, 80), (cx2, cy2), ring_r, 1)
            inner_r = max(1, ring_r - 60)
            pygame.draw.circle(surf, (40, 40, 60), (cx2, cy2), inner_r, 1)
            for i in range(n):
                angle = math.pi/2 + (2*math.pi * (i + 0.5) / n)
                ex = int(cx2 + math.cos(angle) * ring_r)
                ey = int(cy2 - math.sin(angle) * ring_r)
                pygame.draw.line(surf, (50, 50, 75), (cx2, cy2), (ex, ey), 1)

        # ── Center hub ────────────────────────────────────────────────────────
        hub_r = int(42 * t)
        if hub_r > 2:
            gs = pygame.Surface((hub_r*4, hub_r*4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (220, 50, 50, int(40*t)), (hub_r*2, hub_r*2), hub_r*2)
            surf.blit(gs, (cx2 - hub_r*2, cy2 - hub_r*2))
            pygame.draw.circle(surf, (18, 14, 26), (cx2, cy2), hub_r)
            pygame.draw.circle(surf, (180, 30, 30), (cx2, cy2), hub_r, 2)
            cf = pygame.font.SysFont("consolas", 11, bold=True)
            ct = cf.render(WHEEL_LABELS[self.selected], True, (220, 200, 200))
            surf.blit(ct, (cx2 - ct.get_width()//2, cy2 - ct.get_height()//2))

        # ── Weapon slots ──────────────────────────────────────────────────────
        label_font = pygame.font.SysFont("consolas", 10, bold=True)
        ammo_font  = pygame.font.SysFont("consolas", 9)

        for i, weapon in enumerate(WHEEL_WEAPONS):
            sx, sy = self.get_slot_pos(i, n)
            anim_sx = cx2 + (sx - cx2) * t
            anim_sy = cy2 + (sy - cy2) * t
            sx_i = int(anim_sx); sy_i = int(anim_sy)

            is_sel    = (i == self.selected)
            is_active = (weapon == player.weapon)
            sr        = int(self.SLOT_RADIUS * t)
            if sr < 3: continue

            # Slot glow for selected
            if is_sel and sr > 6:
                pulse = abs(math.sin(pygame.time.get_ticks() * 0.008)) * 20
                gs2 = pygame.Surface((sr*4, sr*4), pygame.SRCALPHA)
                pygame.draw.circle(gs2, (255, 200, 50, int(55 + pulse)),
                                   (sr*2, sr*2), sr*2)
                surf.blit(gs2, (sx_i - sr*2, sy_i - sr*2))

            # Slot background
            if is_sel:
                bg_col  = (90, 60, 12)
                brd_col = (255, 200, 50)
                brd_w   = 3
            elif is_active:
                bg_col  = (15, 55, 15)
                brd_col = (50, 220, 80)
                brd_w   = 2
            else:
                empty   = weapon.ammo is not None and weapon.ammo == 0
                bg_col  = (10, 10, 28) if not empty else (28, 8, 8)
                brd_col = (55, 55, 90) if not empty else (100, 30, 30)
                brd_w   = 1

            pygame.draw.circle(surf, bg_col,  (sx_i, sy_i), sr)
            pygame.draw.circle(surf, brd_col, (sx_i, sy_i), sr, brd_w)
            if sr > 14:
                pygame.draw.circle(surf, (*brd_col, 60), (sx_i, sy_i), sr - 8, 1)

            # ── Weapon art (clipped to slot) ──────────────────────────────────
            if sr > 20 and t > 0.4:
                # Draw onto a temp surface so art stays inside the circle
                art_size = sr * 2 + 4
                art_surf = pygame.Surface((art_size, art_size), pygame.SRCALPHA)
                # Clip mask
                mask = pygame.Surface((art_size, art_size), pygame.SRCALPHA)
                pygame.draw.circle(mask, (255,255,255,255),
                                   (art_size//2, art_size//2), sr - 3)
                weapon_scale = max(0.3, (sr / self.SLOT_RADIUS) * 0.72)
                self._draw_weapon_art(art_surf, weapon,
                                      art_size//2, art_size//2, weapon_scale)
                art_surf.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
                art_surf.set_alpha(int(255 * min(1.0, (t - 0.4) / 0.4)))
                surf.blit(art_surf, (sx_i - art_size//2, sy_i - art_size//2))

            # Weapon level badge
            lv = WSTATS.get_level(weapon.name)
            if lv > 0 and sr > 20:
                lv_cols = [(80,200,80),(100,180,255),(255,200,50),(255,80,60)]
                lv_f    = pygame.font.SysFont("consolas", 9, bold=True)
                lv_t    = lv_f.render(f"LV{lv}", True, lv_cols[lv])
                surf.blit(lv_t, (sx_i + int(sr*0.55) - lv_t.get_width()//2,
                                  sy_i - int(sr*0.75)))

            # ── Weapon name below slot ────────────────────────────────────────
            if sr > 20 and t > 0.5:
                lbl_col = (255, 200, 50) if is_sel else \
                          (50, 220, 80)  if is_active else \
                          (180, 180, 200)
                # Two-line label: split on space at midpoint
                label   = WHEEL_LABELS[i]
                words   = label.split()
                if len(words) >= 3:
                    mid  = len(words) // 2
                    line1 = " ".join(words[:mid])
                    line2 = " ".join(words[mid:])
                else:
                    line1 = label
                    line2 = ""
                alpha_lbl = int(255 * min(1.0, (t - 0.5) / 0.4))
                t1 = label_font.render(line1, True, lbl_col)
                t1.set_alpha(alpha_lbl)
                surf.blit(t1, (sx_i - t1.get_width()//2, sy_i + sr + 3))
                if line2:
                    t2 = label_font.render(line2, True, lbl_col)
                    t2.set_alpha(alpha_lbl)
                    surf.blit(t2, (sx_i - t2.get_width()//2, sy_i + sr + 14))

            # Ammo indicator
            if weapon.ammo is not None and sr > 24:
                ammo_col = (255, 80, 80) if weapon.ammo == 0 else (160, 160, 200)
                ammo_t   = ammo_font.render(f"{weapon.ammo}/{weapon.max_ammo}",
                                            True, ammo_col)
                ammo_t.set_alpha(int(220 * t))
                surf.blit(ammo_t, (sx_i - ammo_t.get_width()//2, sy_i - sr - 12))

        # ── SLOW MO indicator ─────────────────────────────────────────────────
        if t > 0.5:
            sm_f = pygame.font.SysFont("consolas", 13, bold=True)
            sm_t = sm_f.render("● SLOW  MOTION", True, (100, 200, 255))
            sm_s = pygame.Surface((sm_t.get_width() + 16, sm_t.get_height() + 6),
                                  pygame.SRCALPHA)
            sm_s.fill((0, 0, 0, 100))
            sm_s.blit(sm_t, (8, 3))
            sm_s.set_alpha(int(200 * (t - 0.5) * 2))
            surf.blit(sm_s, (WIDTH//2 - sm_s.get_width()//2, HEIGHT - 65))

WEAPON_WHEEL = WeaponWheel()

WEAPON_KEYS={pygame.K_1:PISTOLE,pygame.K_2:STURMGEWEHR,pygame.K_3:SCHARFSCHUETZE,
             pygame.K_4:SCHROTFLINTE,pygame.K_5:RAKETENWERFER,pygame.K_6:STINGER,
             pygame.K_7:MESSER,pygame.K_8:FLAMMENWERFER,pygame.K_9:EMP_CANNON}
WEAPON_KEYS_EXTRA = {pygame.K_0: RAILGUN}

def draw_weapon_xp_bar(surf, weapon):
    """Kleine XP-Leiste für aktive Waffe."""
    lv=WSTATS.get_level(weapon.name)
    kills=WSTATS.kills.get(weapon.name,0)
    if lv>=3:
        label="MAX";ratio=1.0
    else:
        lo=WEAPON_UPGRADE_KILLS[lv];hi=WEAPON_UPGRADE_KILLS[lv+1]
        ratio=(kills-lo)/(hi-lo) if hi>lo else 1.0
        label=f"LV{lv} → LV{lv+1}"
    bw=160;bx=WIDTH-bw-14;by=96
    pygame.draw.rect(surf,(30,30,50),(bx,by,bw,8))
    col=[(80,200,80),(120,200,255),(255,200,50),(255,80,80)][lv]
    pygame.draw.rect(surf,col,(bx,by,int(bw*ratio),8))
    pygame.draw.rect(surf,GRAY,(bx,by,bw,8),1)
    f=pygame.font.SysFont("consolas",9)
    surf.blit(f.render(label,True,GRAY),(bx,by-10))

class KillFeed:
    """Shows the last few kills in the top-right corner."""
    MAX  = 5
    LIFE = 240   # frames each entry lives

    def __init__(self):
        self.entries = []   # list of {"text":str, "col":tuple, "timer":int}

    def add(self, text, col=(255,200,80)):
        self.entries.append({"text": text, "col": col, "timer": self.LIFE})
        if len(self.entries) > self.MAX:
            self.entries.pop(0)

    def update(self):
        for e in self.entries: e["timer"] -= 1
        self.entries = [e for e in self.entries if e["timer"] > 0]

    def draw(self, surf):
        f2 = pygame.font.SysFont("consolas", 13, bold=True)
        x2 = WIDTH - 280; y2 = 115
        for e in reversed(self.entries):
            alpha6 = min(255, e["timer"] * 4)
            t2 = f2.render(e["text"], True, e["col"])
            bg2 = pygame.Surface((t2.get_width()+16, t2.get_height()+4), pygame.SRCALPHA)
            bg2.fill((0,0,0,int(alpha6*0.55)))
            pygame.draw.rect(bg2,(*e["col"],int(alpha6*0.4)),(0,0,bg2.get_width(),bg2.get_height()),1,border_radius=2)
            bg2.blit(t2,(8,2))
            bg2.set_alpha(alpha6)
            surf.blit(bg2,(x2,y2))
            y2 += t2.get_height() + 5

KILL_FEED = KillFeed()

def draw_hud(surf, player, zone_num, zone_name, enemies_left, air_left):
    tick = pygame.time.get_ticks()
    diff_cfg = get_diff()

    hud_accent = {
        1:(80,200,80), 2:(60,200,80), 3:(200,160,40),
        4:(80,80,220), 5:(120,200,255), 6:(180,40,220),
        7:(255,80,20), 8:(40,180,255),
    }.get(zone_num, (80,200,80))

    fn = pygame.font.SysFont("consolas", 12, bold=True)
    fs = pygame.font.SysFont("consolas", 10)
    f9 = pygame.font.SysFont("consolas", 9)

    def panel(surf, x, y, w, h, accent):
        p = pygame.Surface((w, h), pygame.SRCALPHA)
        p.fill((0, 0, 0, 170))
        pygame.draw.rect(p, (*accent, 200), (0, 0, w, h), 1, border_radius=5)
        pygame.draw.rect(p, (*accent, 255), (0, 0, w, 3), border_radius=5)
        surf.blit(p, (x, y))

    # ── TOP LEFT: Hearts + HP ──────────────────────────────────────────────
    panel(surf, 8, 8, 265, 72, hud_accent)

    # Hearts
    for i in range(player.MAX_LIVES):
        alive = i < player.lives
        hx = 16 + i * 36; hy = 12
        if alive:
            pulse = abs(math.sin(tick * 0.015)) * 4 if player.lives == 1 else 0
            r = int(8 + pulse)
            pygame.draw.circle(surf, (220,40,40), (hx+r-1, hy+r), r)
            pygame.draw.circle(surf, (220,40,40), (hx+r*2+1, hy+r), r)
            pygame.draw.polygon(surf, (220,40,40),
                [(hx, hy+r+2), (hx+r*2, hy+r*3+4), (hx+r*4+2, hy+r+2)])
            pygame.draw.circle(surf, (255,110,110), (hx+r-2, hy+r-2), max(1, r//3))
        else:
            pygame.draw.circle(surf, (55,20,20), (hx+8, hy+8), 8)
            pygame.draw.circle(surf, (55,20,20), (hx+20, hy+8), 8)
            pygame.draw.polygon(surf, (55,20,20),
                [(hx, hy+10), (hx+14, hy+26), (hx+28, hy+10)])

    # HP bar
    hp_ratio = player.hp / player.MAX_HP
    hc = (50,210,80) if hp_ratio > 0.5 else (235,210,45) if hp_ratio > 0.25 else (215,35,35)
    if hp_ratio < 0.25 and (tick//160)%2 == 0:
        hc = (255,65,65)
    bw = 210; bx = 16; by = 48
    pygame.draw.rect(surf, (14,18,12), (bx, by, bw, 16), border_radius=4)
    fw = int(bw * hp_ratio)
    if fw > 0:
        pygame.draw.rect(surf, hc, (bx, by, fw, 16), border_radius=4)
        shine = pygame.Surface((fw, 5), pygame.SRCALPHA)
        shine.fill((255,255,255,50))
        surf.blit(shine, (bx, by+1))
    pygame.draw.rect(surf, (*hud_accent, 120), (bx, by, bw, 16), 1, border_radius=4)
    hp_t = fs.render(f"HP  {player.hp} / {player.MAX_HP}", True, WHITE)
    surf.blit(hp_t, (bx + (bw - hp_t.get_width())//2, by+3))

    if player.shield_timer > 0:
        sw = int(bw * player.shield_timer / 1800)
        pygame.draw.rect(surf, (8,16,40), (bx, by+18, bw, 5), border_radius=2)
        pygame.draw.rect(surf, (70,145,255), (bx, by+18, sw, 5), border_radius=2)

    # ── TOP CENTER: Score ──────────────────────────────────────────────────
    sf_big = pygame.font.SysFont("consolas", 32, bold=True)
    score_str = f"{player.score:,}".replace(",", ".")
    score_t   = sf_big.render(score_str, True, hud_accent)
    pw = score_t.get_width() + 44
    panel(surf, WIDTH//2 - pw//2, 8, pw, 48, hud_accent)
    lbl = fs.render("◈ SCORE", True, tuple(max(0,c-55) for c in hud_accent))
    surf.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 13))
    sh = sf_big.render(score_str, True, tuple(max(0,c-70) for c in hud_accent))
    surf.blit(sh,     (WIDTH//2 - score_t.get_width()//2 + 2, 22))
    surf.blit(score_t,(WIDTH//2 - score_t.get_width()//2,     20))
    diff_t = fs.render(f"[ {diff_cfg['label']} ]", True, diff_cfg["color"])
    surf.blit(diff_t, (WIDTH//2 - diff_t.get_width()//2, 58))

    # ── TOP RIGHT: Zone + enemy counts ────────────────────────────────────
    panel(surf, WIDTH-234, 8, 226, 90, hud_accent)
    zone_t   = fn.render(f"◈ ZONE {zone_num} / {NUM_ZONES}", True, hud_accent)
    short_nm = zone_name.split(":")[-1].strip() if ":" in zone_name else zone_name
    name_t   = fs.render(short_nm[:24], True, (180,180,200))
    enemy_t  = fs.render(f"▣ Boden : {enemies_left}", True, (225,135,135))
    air_t    = fs.render(f"✈ Luft  : {air_left}",    True, (100,215,220))
    surf.blit(zone_t,  (WIDTH-228, 14))
    surf.blit(name_t,  (WIDTH-228, 30))
    surf.blit(enemy_t, (WIDTH-228, 46))
    surf.blit(air_t,   (WIDTH-228, 62))
    # Enemy bar
    total_e = enemies_left + air_left
    eb_w = 210
    pygame.draw.rect(surf, (20,8,8),    (WIDTH-231, 78, eb_w, 8), border_radius=3)
    ratio_e = min(1.0, total_e / max(total_e, 1))
    ec = (45,200,75) if ratio_e < 0.35 else (225,185,45) if ratio_e < 0.70 else (215,38,38)
    if total_e > 0:
        pygame.draw.rect(surf, ec, (WIDTH-231, 78, int(eb_w*ratio_e), 8), border_radius=3)
    pygame.draw.rect(surf, (*hud_accent,80), (WIDTH-231, 78, eb_w, 8), 1, border_radius=3)

    # ── BOTTOM LEFT: Grenades + weapon ────────────────────────────────────
    panel(surf, 8, HEIGHT-72, 310, 64, hud_accent)

    surf.blit(fn.render("💣 GRANATEN", True, hud_accent), (14, HEIGHT-68))
    for i in range(player.GRENADES):
        has = i < player.grenades
        gx2 = 14 + i*18; gy2 = HEIGHT-50
        gc  = hud_accent if has else tuple(max(0,c-80) for c in hud_accent)
        gc_dark = tuple(max(0,c-35) for c in gc)
        pygame.draw.circle(surf, gc_dark, (gx2+6, gy2+6), 6)
        pygame.draw.circle(surf, gc,      (gx2+6, gy2+6), 6, 1)
        if has:
            pygame.draw.circle(surf, gc, (gx2+4, gy2+4), 2)
    ct = fs.render(f"×{player.grenades}", True, hud_accent)
    surf.blit(ct, (14 + player.GRENADES*18 + 4, HEIGHT-50))

    w_cur = player.weapon
    if w_cur.ammo is not None:
        ar = w_cur.ammo / max(1, w_cur.max_ammo)
        wc = (255,80,80) if w_cur.ammo==0 else (255,200,50) if ar<0.35 else hud_accent
        ammo_s = f"{w_cur.ammo}/{w_cur.max_ammo}"
    else:
        wc = hud_accent; ammo_s = "∞"
    wt = fs.render(f"🔫 {w_cur.name[:14]}  {ammo_s}", True, wc)
    surf.blit(wt, (14, HEIGHT-30))
    if w_cur.ammo is not None:
        abw = 160; abx = 150; aby = HEIGHT-28
        pygame.draw.rect(surf, (20,20,28), (abx, aby, abw, 6), border_radius=3)
        afw = int(abw * w_cur.ammo / max(1, w_cur.max_ammo))
        if afw > 0:
            pygame.draw.rect(surf, wc, (abx, aby, afw, 6), border_radius=3)

    # ── BOTTOM CENTER: Controls hint ───────────────────────────────────────
    ctrl = pygame.font.SysFont("consolas", 11).render(
        "WASD · SPACE · Klick:Schießen · G:Granate · Q:Waffenrad · T:Turret · B:Bauen · ESC:Pause",
        True, (65,70,85))
    surf.blit(ctrl, (WIDTH//2 - ctrl.get_width()//2, HEIGHT-14))

    # ── BOTTOM RIGHT: Weapon slots ─────────────────────────────────────────
    weapon_list = [
        (PISTOLE,"1"),(STURMGEWEHR,"2"),(SCHARFSCHUETZE,"3"),
        (SCHROTFLINTE,"4"),(RAKETENWERFER,"5"),(STINGER,"6"),
        (MESSER,"7"),(FLAMMENWERFER,"8"),(EMP_CANNON,"9"),
    ]
    ws_x = WIDTH-234; ws_y = HEIGHT-118
    panel(surf, ws_x, ws_y, 226, 110, hud_accent)

    for i,(w,k) in enumerate(weapon_list):
        col_i = i%5; row_i = i//5
        sx = ws_x+4 + col_i*44; sy = ws_y+4 + row_i*52
        active = player.weapon == w
        empty  = w.ammo is not None and w.ammo == 0
        lv     = WSTATS.get_level(w.name)

        if active:
            bg  = tuple(int(c*0.45) for c in hud_accent)
            brd = hud_accent
        elif empty:
            bg  = (30,8,8); brd = (100,25,25)
        else:
            bg  = (10,14,10); brd = (30,45,28)

        pygame.draw.rect(surf, bg,  (sx, sy, 40, 46), border_radius=3)
        pygame.draw.rect(surf, brd, (sx, sy, 40, 46), 1, border_radius=3)
        if active:
            pygame.draw.rect(surf, brd, (sx, sy, 40, 2), border_radius=3)

        surf.blit(f9.render(f"[{k}]", True, brd),                     (sx+2, sy+2))
        surf.blit(f9.render(w.name[:5], True, WHITE if active else (100,110,100)), (sx+2, sy+14))
        if w.ammo is not None:
            at = f9.render(str(w.ammo), True, (255,80,80) if empty else (150,150,170))
            surf.blit(at, (sx+38-at.get_width(), sy+28))
        if lv > 0:
            pip_cols=[(80,200,80),(100,180,255),(240,188,45)]
            for li in range(lv):
                pygame.draw.circle(surf, pip_cols[min(li,2)], (sx+37-li*6, sy+4), 2)

    # XP bar
    xp_w = 226
    xp_x = ws_x; xp_y = HEIGHT-12
    pygame.draw.rect(surf, (8,16,8), (xp_x, xp_y, xp_w, 6), border_radius=3)
    xp_p = PROGRESSION.xp_progress()
    if xp_p > 0:
        pygame.draw.rect(surf, hud_accent, (xp_x, xp_y, int(xp_w*xp_p), 6), border_radius=3)
    pygame.draw.rect(surf, (*hud_accent,100), (xp_x, xp_y, xp_w, 6), 1, border_radius=3)
    lv_t = f9.render(f"LV {PROGRESSION.level}", True, hud_accent)
    surf.blit(lv_t, (xp_x-lv_t.get_width()-3, xp_y-1))

    draw_weapon_xp_bar(surf, player.weapon)

    # Pickup message
    if player.pickup_msg_timer > 0:
        alpha3  = min(255, player.pickup_msg_timer*5)
        pmf3    = pygame.font.SysFont("consolas",18,bold=True)
        pm3     = pmf3.render(f"✚  {player.pickup_msg}", True, hud_accent)
        ps3     = pygame.Surface((pm3.get_width()+28, pm3.get_height()+14), pygame.SRCALPHA)
        ps3.fill((0,0,0,145))
        pygame.draw.rect(ps3, (*hud_accent,120), (0,0,ps3.get_width(),ps3.get_height()), 1, border_radius=4)
        ps3.blit(pm3,(14,7))
        ps3.set_alpha(alpha3)
        surf.blit(ps3,(WIDTH//2-ps3.get_width()//2, HEIGHT//2-88))

    # Zone 7 lava warning
    if zone_num == 7:
        lava_a2 = int(30+abs(math.sin(tick*0.04))*50)
        lava_warn = pygame.Surface((WIDTH,18),pygame.SRCALPHA)
        lava_warn.fill((255,50,0,lava_a2))
        surf.blit(lava_warn,(0,HEIGHT-22))
        lf4 = pygame.font.SysFont("consolas",10,bold=True)
        lt2 = lf4.render("⚠ VULKANGEBIET — LAVA KONTAKT TÖTET SOFORT",True,(255,120,40))
        lt2.set_alpha(lava_a2*3)
        surf.blit(lt2,(WIDTH//2-lt2.get_width()//2,HEIGHT-20))

    # Zone 8 oxygen
    if zone_num == 8:
        oxy_panel = pygame.Surface((180,18),pygame.SRCALPHA)
        oxy_panel.fill((4,8,20,180))
        pygame.draw.rect(oxy_panel,(40,180,255),(0,0,180,18),1,border_radius=3)
        surf.blit(oxy_panel,(WIDTH//2+130,HEIGHT-66))
        of2 = pygame.font.SysFont("consolas",10,bold=True)
        ot2 = of2.render("O₂ STATION: AKTIV",True,(40,180,255))
        surf.blit(ot2,(WIDTH//2+136,HEIGHT-63))
# ═══════════════════════════════════════════════════
#  WELT
# ═══════════════════════════════════════════════════
_SKY_CACHE: dict = {}
def _draw_gradient_sky(surf, top_col, bot_col, horizon_y=None):
    if horizon_y is None:
        horizon_y = GROUND_Y
    key = (top_col, bot_col, horizon_y)
    if key not in _SKY_CACHE:
        s = pygame.Surface((WIDTH, HEIGHT))
        for y in range(0, horizon_y, 3):
            t = y / max(horizon_y, 1)
            r = int(top_col[0] + (bot_col[0]-top_col[0])*t)
            g = int(top_col[1] + (bot_col[1]-top_col[1])*t)
            b = int(top_col[2] + (bot_col[2]-top_col[2])*t)
            pygame.draw.rect(s, (r,g,b), (0, y, WIDTH, 3))
        _SKY_CACHE[key] = s
    surf.blit(_SKY_CACHE[key], (0, 0))


def _draw_star_field(surf, tick, count=80, alpha=180):
    rng = random.Random(42)
    for i in range(count):
        sx  = rng.randint(0, WIDTH)
        sy  = rng.randint(0, GROUND_Y - 60)
        base_r = rng.randint(1, 2)
        twinkle = abs(math.sin(tick * 0.03 + i * 0.7))
        r       = max(1, int(base_r + twinkle))
        a       = int(alpha * (0.5 + 0.5 * twinkle))
        ss      = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(ss, (220, 225, 255, a), (r+1, r+1), r)
        surf.blit(ss, (sx-r-1, sy-r-1))


def _draw_zone1_city(surf, cam_x, tick):
    par1 = int(cam_x * 0.12)
    par2 = int(cam_x * 0.28)
    par3 = int(cam_x * 0.48)

    # Moon
    pygame.draw.circle(surf, (215, 220, 200), (WIDTH-115, 62), 34)
    moon_glow = pygame.Surface((110,110), pygame.SRCALPHA)
    pygame.draw.circle(moon_glow, (200,208,185,28), (55,55), 55)
    surf.blit(moon_glow, (WIDTH-170, 7))
    pygame.draw.circle(surf, (188,195,172), (WIDTH-108, 56), 12)  # crater

    # Distant skyline layer 1 — deep background
    rng_b = random.Random(11)
    for rx in range(-200, WORLD_WIDTH+400, 55):
        sx2 = rx - par1
        rw  = 38 + (rx*7)%60
        rh  = 80 + (rx*13)%160
        col = (10+rng_b.randint(0,8), 14+rng_b.randint(0,6), 26+rng_b.randint(0,10))
        for offset in range(-WIDTH, WORLD_WIDTH+WIDTH, WIDTH):
            bx2 = sx2+offset
            if -rw-10 < bx2 < WIDTH+10:
                pygame.draw.rect(surf, col, (bx2, GROUND_Y-rh, rw, rh))
                # Antenna
                if (rx*3)%7 == 0:
                    pygame.draw.line(surf, (14,18,30), (bx2+rw//2, GROUND_Y-rh), (bx2+rw//2, GROUND_Y-rh-28), 1)
                    blink = (tick//(30+(rx%20)))%2==0
                    pygame.draw.circle(surf, (255,40,40) if blink else (80,10,10), (bx2+rw//2, GROUND_Y-rh-28), 2)

    # Mid layer — detailed ruined buildings
    win_rng = random.Random(55)
    for rx in range(-100, WORLD_WIDTH+200, 80):
        sx3 = rx - par2
        rw2 = 55 + (rx*9)%75
        rh2 = 100 + (rx*11)%180
        for offset in range(-WIDTH, WORLD_WIDTH+WIDTH, WIDTH):
            bx3 = sx3+offset
            if -rw2-10 < bx3 < WIDTH+10:
                # Building body — two-tone
                base_c = (14+win_rng.randint(0,8), 18+win_rng.randint(0,6), 32+win_rng.randint(0,12))
                side_c = (max(0,base_c[0]-4), max(0,base_c[1]-4), max(0,base_c[2]-6))
                pygame.draw.rect(surf, base_c, (bx3, GROUND_Y-rh2, rw2, rh2))
                pygame.draw.rect(surf, side_c, (bx3+rw2-8, GROUND_Y-rh2, 8, rh2))
                # Rooftop ledge
                pygame.draw.rect(surf, (22,28,44), (bx3-2, GROUND_Y-rh2, rw2+4, 5))
                # Window grid
                for wy2 in range(GROUND_Y-rh2+12, GROUND_Y-10, 22):
                    for wx2 in range(bx3+6, bx3+rw2-6, 16):
                        fl = win_rng.random()
                        if fl > 0.78:
                            wc = (255,230,120)  # warm lit
                        elif fl > 0.62:
                            wc = (45,55,145)    # cold blue
                        elif fl > 0.50:
                            wc = (35,80,35)     # green
                        else:
                            wc = (8,10,18)      # dark
                        pygame.draw.rect(surf, wc, (wx2, wy2, 9, 12))
                        # Window flicker
                        if wc != (8,10,18) and (wx2+wy2+tick//8)%38 < 2:
                            pygame.draw.rect(surf, (8,10,18), (wx2, wy2, 9, 12))
                        # Window frame
                        pygame.draw.rect(surf, (22,26,40), (wx2, wy2, 9, 12), 1)
                # Damage — blown out sections
                if (rx*5)%11 < 4:
                    dmg_y = GROUND_Y-rh2+win_rng.randint(20,rh2-30)
                    dmg_w = win_rng.randint(12,28)
                    pygame.draw.rect(surf, (6,8,14), (bx3+win_rng.randint(0,rw2-dmg_w), dmg_y, dmg_w, 20))

    # Close foreground rubble + barriers
    for rx in range(0, WORLD_WIDTH+200, 130):
        sx4 = rx - par3
        for offset in range(-WIDTH, WORLD_WIDTH+WIDTH, WIDTH):
            bx4 = sx4+offset
            if -60 < bx4 < WIDTH+60:
                rh3 = 14 + (rx*7)%30
                pts2 = [(bx4,GROUND_Y),(bx4+6,GROUND_Y-rh3),(bx4+15,GROUND_Y-rh3+5),
                        (bx4+24,GROUND_Y-rh3-4),(bx4+38,GROUND_Y-rh3+8),(bx4+52,GROUND_Y)]
                pygame.draw.polygon(surf, (25,19,14), pts2)
                # Concrete barrier
                if (rx*3)%9 < 3:
                    pygame.draw.rect(surf, (32,28,24), (bx4+8, GROUND_Y-18, 24, 18), border_radius=2)
                    pygame.draw.rect(surf, (44,38,32), (bx4+8, GROUND_Y-18, 24,  4), border_radius=2)

    # Neon signs
    neon_defs2 = [(180,GROUND_Y-175,NEON_PINK),(540,GROUND_Y-210,NEON_BLUE),(920,GROUND_Y-155,ACID_GREEN)]
    for nx2,ny2,nc2 in neon_defs2:
        sx5 = nx2-par3
        pulse2 = int(35+abs(math.sin(tick*0.05+nx2*0.01))*55)
        gs7 = pygame.Surface((90,45),pygame.SRCALPHA)
        pygame.draw.ellipse(gs7, (*nc2,pulse2), (0,0,90,45))
        surf.blit(gs7,(sx5-45,ny2))
        # Sign box
        pygame.draw.rect(surf, (12,14,20), (sx5-18, ny2-8, 36, 16), border_radius=3)
        pygame.draw.rect(surf, nc2, (sx5-18, ny2-8, 36, 16), 1, border_radius=3)

    # Falling ash
    ash_rng = random.Random(tick//6)
    for _ in range(14):
        ax2 = ash_rng.randint(0,WIDTH); ay2 = ash_rng.randint(0,GROUND_Y)
        ap2 = ash_rng.randint(50,120)
        ss2 = pygame.Surface((3,3),pygame.SRCALPHA)
        pygame.draw.circle(ss2,(195,195,195,ap2),(1,1),1)
        surf.blit(ss2,(ax2,ay2))

    # Distant fire glow on rubble
    for fx2 in (220, 680, 1100):
        fsx = fx2 - par3
        if -50 < fsx < WIDTH+50:
            pulse3 = int(28+abs(math.sin(tick*0.07+fx2*0.005))*40)
            fire_s = pygame.Surface((55,30),pygame.SRCALPHA)
            pygame.draw.ellipse(fire_s,(255,95,15,pulse3),(0,0,55,30))
            surf.blit(fire_s,(fsx-27,GROUND_Y-18))


def _draw_zone2_forest(surf, cam_x, tick):
    par1 = int(cam_x * 0.16)
    par2 = int(cam_x * 0.32)
    par3 = int(cam_x * 0.52)

    # Fog layer
    fog2 = pygame.Surface((WIDTH,90),pygame.SRCALPHA)
    fog2.fill((75,115,65,22))
    surf.blit(fog2,(0,GROUND_Y-230))

    # Far tree canopy — silhouette layer
    tree_rng2 = random.Random(14)
    for tx2 in range(-250, WORLD_WIDTH+250, 65):
        sx6 = tx2-par1
        if -120 < sx6 < WIDTH+120:
            h2 = 95+(tx2*9)%90
            sway2 = math.sin(tick*0.014+tx2*0.045)*4
            # Trunk
            tk_col = (32,18,8)
            pygame.draw.rect(surf,tk_col,(int(sx6+sway2)+18,GROUND_Y-h2+55,10,h2-55))
            # Bark texture lines
            for bi2 in range(3):
                bly = GROUND_Y-h2+60+bi2*12
                pygame.draw.line(surf,(24,14,6),(int(sx6+sway2)+18,bly),(int(sx6+sway2)+22,bly+8),1)
            # Three canopy layers
            dg2 = (8+tree_rng2.randint(0,12), 40+tree_rng2.randint(0,22), 8)
            for layer2,(rw3,rh4,up2,al2) in enumerate([(58,62,0,210),(66,52,20,170),(50,42,38,140)]):
                cs5 = pygame.Surface((rw3*2,rh4*2),pygame.SRCALPHA)
                col2 = (dg2[0]+layer2*10, min(dg2[1]+layer2*12,100), dg2[2]+layer2*5, al2)
                pygame.draw.ellipse(cs5,col2,(0,0,rw3*2,rh4*2))
                surf.blit(cs5,(int(sx6+sway2)+20-rw3,GROUND_Y-h2-up2))
            # Moss/vine hanging
            if (tx2*7)%5==0:
                for vi in range(3):
                    vx2 = int(sx6+sway2)+15+vi*8
                    pygame.draw.line(surf,(22,55,18),(vx2,GROUND_Y-h2+10),(vx2+tree_rng2.randint(-3,3),GROUND_Y-h2+28),1)

    # Mid undergrowth ferns
    for fx3 in range(0, WIDTH+120, 38):
        fh2 = 14+(fx3*3)%22
        fc3 = (28+fx3%16, 62+fx3%20, 20)
        for i2 in range(6):
            ang2 = -0.9+i2*0.36+math.sin(tick*0.012+fx3*0.05)*0.08
            ex4 = int(fx3+math.cos(ang2)*fh2*1.5)
            ey4 = int(GROUND_Y-math.sin(ang2)*fh2)
            pygame.draw.line(surf,fc3,(fx3,GROUND_Y),(ex4,ey4),2)

    # Light rays — god rays
    for i3 in range(4):
        ray_x2 = 160+i3*350-par2//5
        ray_w2 = 55+i3*18
        ray_s = pygame.Surface((ray_w2,GROUND_Y),pygame.SRCALPHA)
        a3 = int(10+abs(math.sin(tick*0.018+i3))*16)
        pygame.draw.polygon(ray_s,(175,215,135,a3),[(0,0),(ray_w2,0),(ray_w2-22,GROUND_Y),(22,GROUND_Y)])
        surf.blit(ray_s,(ray_x2,0))

    # Floating spores / fireflies
    ff_rng2 = random.Random(tick//18)
    for _ in range(10):
        ffx2 = ff_rng2.randint(0,WIDTH); ffy2 = ff_rng2.randint(GROUND_Y-200,GROUND_Y-30)
        ff_a2 = ff_rng2.randint(55,185)
        ffs2 = pygame.Surface((9,9),pygame.SRCALPHA)
        fc4 = (175,255,115) if ff_rng2.random()>0.4 else (255,230,115)
        pygame.draw.circle(ffs2,(*fc4,ff_a2),(4,4),3)
        surf.blit(ffs2,(ffx2,ffy2))

    # Root structures at ground
    for rx2 in range(0,WIDTH,95):
        for ri in range(3):
            rang = -0.5+ri*0.5
            rx3 = rx2+par3%90
            ex5 = int(rx3+math.cos(rang)*22)
            ey5 = int(GROUND_Y-2+math.sin(abs(rang))*8)
            pygame.draw.line(surf,(32,20,10),(rx3,GROUND_Y),(ex5,ey5),2)


def _draw_zone3_desert(surf, cam_x, tick):
    par1 = int(cam_x * 0.14)
    par2 = int(cam_x * 0.32)

    # Sun with corona
    sun_x = WIDTH-95; sun_y = 72
    pygame.draw.circle(surf,(255,228,88),(sun_x,sun_y),46)
    for ri2 in range(3):
        corona_s = pygame.Surface((200,200),pygame.SRCALPHA)
        corona_a = int(28-ri2*8)
        pygame.draw.circle(corona_s,(255,210,55,corona_a),(100,100),90+ri2*20)
        surf.blit(corona_s,(sun_x-100,sun_y-100))
    # Sun rays
    for ri3 in range(16):
        ang3 = (ri3/16)*2*math.pi
        ray_len2 = 60+abs(math.sin(tick*0.02+ri3))*15
        ex6 = int(sun_x+math.cos(ang3)*ray_len2)
        ey6 = int(sun_y+math.sin(ang3)*ray_len2)
        ray_a2 = int(35+abs(math.sin(tick*0.025+ri3))*25)
        rs2 = pygame.Surface((4,4),pygame.SRCALPHA)
        pygame.draw.circle(rs2,(255,220,80,ray_a2),(2,2),2)
        surf.blit(rs2,(ex6-2,ey6-2))

    # Heat shimmer bands
    for i4 in range(4):
        hy2 = GROUND_Y-25-i4*22
        wave2 = int(math.sin(tick*0.09+i4*1.4)*5)
        haze2 = pygame.Surface((WIDTH,10),pygame.SRCALPHA)
        haze2.fill((205,172,80,16+i4*6))
        surf.blit(haze2,(wave2,hy2))

    # Far dunes — layered
    for layer3 in range(3):
        l_col = [(115,82,36),(128,92,42),(138,100,48)][layer3]
        l_par = int(cam_x*(0.10+layer3*0.08))
        for dx2 in range(-300,WORLD_WIDTH+300,200+layer3*40):
            sx7 = dx2-l_par
            dh2 = 45+(dx2*11+layer3*30)%100
            sway3 = math.sin(tick*0.006+dx2*0.003)*3
            pts3 = [(sx7,GROUND_Y),(sx7+55,GROUND_Y-dh2+18+int(sway3)),
                    (sx7+120,GROUND_Y-dh2),(sx7+195,GROUND_Y-dh2+32+int(sway3)),(sx7+240,GROUND_Y)]
            pygame.draw.polygon(surf,l_col,pts3)
            pygame.draw.line(surf,tuple(min(255,c+18) for c in l_col),
                             (sx7+55,GROUND_Y-dh2+18),(sx7+120,GROUND_Y-dh2),2)

    # Sand ripples at ground
    for i5 in range(0,WIDTH,18):
        wave3 = int(math.sin((i5+tick*0.35)*0.10)*3)
        pygame.draw.line(surf,(148,108,48),(i5,GROUND_Y-5+wave3),(i5+18,GROUND_Y-5+wave3),1)

    # Dead tree / cactus silhouettes
    for cx3 in (180,480,820,1140):
        sx8 = cx3-par2
        if -30<sx8<WIDTH+30:
            # Cactus
            pygame.draw.rect(surf,(55,72,28),(sx8-4,GROUND_Y-55,8,55))
            pygame.draw.rect(surf,(55,72,28),(sx8-14,GROUND_Y-42,10,6))
            pygame.draw.rect(surf,(55,72,28),(sx8+4,GROUND_Y-36,10,6))

    # Dust devil
    dd_x2 = int((WIDTH//2+math.sin(tick*0.02)*220)-par2//4)
    for i6 in range(10):
        t11 = i6/10
        ddr2 = int(3+t11*26)
        ddy2 = GROUND_Y-int(t11*140)
        dds2 = pygame.Surface((ddr2*2+2,ddr2*2+2),pygame.SRCALPHA)
        pygame.draw.circle(dds2,(188,158,88,int(48*(1-t11))),(ddr2+1,ddr2+1),ddr2)
        surf.blit(dds2,(dd_x2-ddr2-1,ddy2-ddr2-1))


def _draw_zone4_base(surf, cam_x, tick):
    par1 = int(cam_x * 0.18)
    _draw_star_field(surf, tick, count=65, alpha=135)

    # Fortress structures
    forts2 = [(0,230,205),(305,215,220),(610,255,185),(920,220,240),(1220,210,195)]
    for rx4,rw4,rh5 in forts2:
        sx9 = rx4-par1
        for offset in range(-WIDTH,WORLD_WIDTH+WIDTH,WIDTH):
            bx5 = sx9+offset
            if -rw4-10<bx5<WIDTH+10:
                # Main block
                pygame.draw.rect(surf,(8,10,24),(bx5,GROUND_Y-rh5,rw4,rh5))
                pygame.draw.rect(surf,(18,20,38),(bx5,GROUND_Y-rh5,rw4,rh5),2)
                # Side shading
                pygame.draw.rect(surf,(5,6,18),(bx5+rw4-12,GROUND_Y-rh5,12,rh5))
                # Battlements
                for zx2 in range(bx5,bx5+rw4-14,24):
                    pygame.draw.rect(surf,(14,12,30),(zx2,GROUND_Y-rh5-14,16,15))
                    pygame.draw.rect(surf,(22,20,42),(zx2,GROUND_Y-rh5-14,16,4))
                # Lit windows
                rng5 = random.Random(rx4)
                for wy3 in range(GROUND_Y-rh5+16,GROUND_Y-10,35):
                    for wx3 in range(bx5+14,bx5+rw4-14,28):
                        fl2 = (wx3*13+wy3*7+tick//8)%24
                        on2 = (wx3+wy3)%52<28 and fl2>2
                        wc2 = (48,48,148) if on2 else DARK
                        pygame.draw.rect(surf,wc2,(wx3,wy3,13,17))
                        if on2: pygame.draw.rect(surf,(62,62,180),(wx3,wy3,13,4))
                # Watch tower on top
                if rw4>180:
                    tx4 = bx5+rw4//2
                    pygame.draw.rect(surf,(12,14,28),(tx4-12,GROUND_Y-rh5-32,24,20))
                    pygame.draw.rect(surf,(18,22,38),(tx4-14,GROUND_Y-rh5-34,28,6))
                    # Spotlight
                    sl2 = pygame.Surface((60,10),pygame.SRCALPHA)
                    sl_ang2 = math.sin(tick*0.016+rx4*0.002)*0.6
                    sl_x2 = int(tx4+math.sin(sl_ang2)*80)
                    sl_pts2 = [(tx4-8,GROUND_Y-rh5-28),(tx4+8,GROUND_Y-rh5-28),(sl_x2+18,GROUND_Y-10),(sl_x2-18,GROUND_Y-10)]
                    sl_surf2 = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
                    pygame.draw.polygon(sl_surf2,(255,255,200,12),sl_pts2)
                    surf.blit(sl_surf2,(0,0))
                    pygame.draw.circle(surf,(255,255,180),(tx4,GROUND_Y-rh5-28),5)

    # Barbed wire
    for wx4 in range(0,WIDTH,10):
        wy4 = GROUND_Y-10
        pygame.draw.line(surf,(75,75,85),(wx4,wy4),(wx4+10,wy4+random.randint(-2,2)),1)
    for wx5 in range(5,WIDTH,26):
        pygame.draw.line(surf,(92,92,102),(wx5,GROUND_Y-14),(wx5+5,GROUND_Y-7),1)

    # Sandbag positions
    for sbx in (180,440,760,1050):
        sx10 = sbx-par1
        if -60<sx10<WIDTH+60:
            for sbi in range(5):
                pygame.draw.ellipse(surf,(88,75,48),(sx10+sbi*14-35,GROUND_Y-14,16,10))
                pygame.draw.ellipse(surf,(105,90,58),(sx10+sbi*14-35,GROUND_Y-14,16,4))


def _draw_zone5_arctic(surf, cam_x, tick):
    par1 = int(cam_x * 0.16)
    par2 = int(cam_x * 0.35)

    # Aurora borealis — rich multi-layer
    aurora_cols2 = [(45,195,95),(85,75,215),(50,180,180),(120,55,200)]
    for i7,ac2 in enumerate(aurora_cols2):
        al3 = pygame.Surface((WIDTH,HEIGHT//2),pygame.SRCALPHA)
        a_v2 = int(18+math.sin(tick*0.018+i7*1.4)*14)
        ox4 = int(math.sin(tick*0.009+i7)*200)
        oy4 = int(math.cos(tick*0.012+i7*0.7)*30)
        # Curtain-like aurora shape
        for strip in range(8):
            sx11 = ox4+i7*180-40+strip*35
            aw2  = 55+strip*8
            ah2  = int(HEIGHT//3+math.sin(tick*0.015+strip)*40)
            aurora_strip = pygame.Surface((aw2,ah2),pygame.SRCALPHA)
            a_strip = max(0, int((a_v2-strip*1.5)*(1-strip/12)))
            pygame.draw.ellipse(aurora_strip,(*ac2,a_strip),(0,0,aw2,ah2))
            surf.blit(aurora_strip,(sx11,10+oy4+strip*8))

    # Ice mountains — multi-layer
    for layer4 in range(3):
        l_par2 = int(cam_x*(0.12+layer4*0.10))
        l_bright = [165,182,200][layer4]
        for mx2 in range(-300,WORLD_WIDTH+300,220+layer4*30):
            sx12 = mx2-l_par2
            h3   = 100+(mx2*11+layer4*55)%145
            sway4 = math.sin(tick*0.005+mx2*0.002+layer4)*2
            pts4  = [(sx12,GROUND_Y),(sx12+155,GROUND_Y),(sx12+78,GROUND_Y-h3)]
            col3  = (l_bright-layer4*18, l_bright+5-layer4*10, l_bright+20-layer4*5)
            pygame.draw.polygon(surf,col3,pts4)
            # Snow cap
            cap2 = [(sx12+40+int(sway4),GROUND_Y-h3+45),(sx12+78,GROUND_Y-h3),(sx12+118-int(sway4),GROUND_Y-h3+45)]
            pygame.draw.polygon(surf,(228,240,252),cap2)
            # Shadow face
            shad2 = [(sx12+78,GROUND_Y-h3),(sx12+155,GROUND_Y),(sx12+78,GROUND_Y-h3+48)]
            shad_col2 = tuple(max(0,c-28) for c in col3)
            pygame.draw.polygon(surf,shad_col2,shad2)
            # Ice cliff cracks
            if layer4==0 and h3>120:
                crack_r2 = random.Random(mx2)
                for _ in range(2):
                    crx2 = sx12+crack_r2.randint(40,100)
                    cry2 = GROUND_Y-crack_r2.randint(30,h3-20)
                    pygame.draw.line(surf,tuple(max(0,c-40) for c in col3),
                                     (crx2,cry2),(crx2+crack_r2.randint(-8,8),cry2+crack_r2.randint(8,20)),1)

    # Drifting snow
    snow_rng2 = random.Random(tick//4)
    for _ in range(22):
        spx2 = snow_rng2.randint(0,WIDTH); spy2 = snow_rng2.randint(0,GROUND_Y)
        sps2 = pygame.Surface((7,7),pygame.SRCALPHA)
        sa4  = snow_rng2.randint(75,210)
        pygame.draw.circle(sps2,(228,238,252,sa4),(3,3),2)
        surf.blit(sps2,(spx2,spy2))

    # Ice crystals at ground
    for cx4 in range(0,WIDTH,70):
        cy5 = GROUND_Y-6
        cx5 = cx4+par2%65
        for ci3 in range(4):
            ang4 = ci3*math.pi/2+math.sin(tick*0.005+cx4*0.02)*0.1
            ex7  = int(cx5+math.cos(ang4)*8)
            ey7  = int(cy5+math.sin(ang4)*4)
            pygame.draw.line(surf,(188,210,235),(cx5,cy5),(ex7,ey7),1)

    # Blizzard overlay
    bliz_a = int(18+abs(math.sin(tick*0.02))*12)
    bliz = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
    bliz.fill((220,232,248,bliz_a))
    surf.blit(bliz,(0,0))


def _draw_zone6_omega(surf, cam_x, tick):
    par1 = int(cam_x * 0.18)
    _draw_star_field(surf, tick, count=120, alpha=115)

    # Void nebula in sky
    for ni in range(3):
        neb_s = pygame.Surface((300,200),pygame.SRCALPHA)
        neb_x = 150+ni*380; neb_y = 80+ni*40
        neb_c = [(80,10,100),(30,5,80),(100,15,60)][ni]
        neb_a = int(18+math.sin(tick*0.015+ni)*10)
        pygame.draw.ellipse(neb_s,(*neb_c,neb_a),(0,0,300,200))
        surf.blit(neb_s,(neb_x-150,neb_y-100))

    # Omega fortress spires
    spires2 = [(0,275,255),(365,258,285),(742,285,235),(1080,265,295),(1430,258,248)]
    for rx5,rw5,rh6 in spires2:
        sx13 = rx5-par1
        for offset in range(-WIDTH,WORLD_WIDTH+WIDTH,WIDTH):
            bx6 = sx13+offset
            if -rw5-10<bx6<WIDTH+10:
                # Main body
                pygame.draw.rect(surf,(12,6,22),(bx6,GROUND_Y-rh6,rw5,rh6))
                pygame.draw.rect(surf,(28,14,48),(bx6,GROUND_Y-rh6,rw5,rh6),2)
                # Side shadow
                pygame.draw.rect(surf,(8,4,16),(bx6+rw5-14,GROUND_Y-rh6,14,rh6))
                # Spire tip
                pygame.draw.polygon(surf,(18,8,32),
                                    [(bx6+rw5//2-14,GROUND_Y-rh6),(bx6+rw5//2,GROUND_Y-rh6-34),(bx6+rw5//2+14,GROUND_Y-rh6)])
                pygame.draw.polygon(surf,(35,15,58),
                                    [(bx6+rw5//2-6,GROUND_Y-rh6),(bx6+rw5//2,GROUND_Y-rh6-34),(bx6+rw5//2+6,GROUND_Y-rh6)])
                # Red-lit windows
                rng6 = random.Random(rx5)
                for wy5 in range(GROUND_Y-rh6+16,GROUND_Y-10,35):
                    for wx6 in range(bx6+14,bx6+rw5-14,28):
                        fl3 = (wx6*13+wy5*7+tick//8)%24
                        on3 = (wx6+wy5)%50<26 and fl3>2
                        wc3 = (130,15,15) if on3 else DARK
                        pygame.draw.rect(surf,wc3,(wx6,wy5,13,17))
                        if on3: pygame.draw.rect(surf,(160,25,25),(wx6,wy5,13,4))
                # Glowing energy lines
                if (rx5*3)%7<3:
                    el_y = GROUND_Y-rh6+rng6.randint(20,rh6-20)
                    el_a = int(55+abs(math.sin(tick*0.04+rx5*0.01))*80)
                    el_s = pygame.Surface((rw5,3),pygame.SRCALPHA)
                    el_s.fill((150,10,180,el_a))
                    surf.blit(el_s,(bx6,el_y))

    # Lava glow ground
    lava_a2 = int(32+abs(math.sin(tick*0.045))*48)
    lava2 = pygame.Surface((WIDTH,38),pygame.SRCALPHA)
    lava2.fill((210,38,6,lava_a2))
    surf.blit(lava2,(0,GROUND_Y-18))
    # Lava cracks
    lava_rng = random.Random(tick//12)
    for _ in range(5):
        lx2 = lava_rng.randint(0,WIDTH); ly2 = GROUND_Y-lava_rng.randint(4,16)
        lw2 = lava_rng.randint(20,60)
        lava_c = pygame.Surface((lw2,4),pygame.SRCALPHA)
        lava_c.fill((255,80,10,int(100+lava_rng.random()*80)))
        surf.blit(lava_c,(lx2,ly2))

    # Lightning
    if (tick//18)%55<2:
        lx3 = random.randint(50,WIDTH-50); ly3 = 0
        pts5 = [(lx3,ly3)]
        for seg2 in range(10):
            lx3 += random.randint(-32,32); ly3 += GROUND_Y//10
            pts5.append((lx3,ly3))
        pygame.draw.lines(surf,(225,32,32),False,pts5,2)
        ls2 = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        pygame.draw.lines(ls2,(225,32,32,65),False,pts5,7)
        surf.blit(ls2,(0,0))

    # Omega watermark
    omega_a2 = int(8+abs(math.sin(tick*0.022))*14)
    omega_f2 = pygame.font.SysFont("consolas",130,bold=True)
    omega_t2 = omega_f2.render("Ω",True,(185,22,22))
    ow2 = pygame.Surface((omega_t2.get_width(),omega_t2.get_height()),pygame.SRCALPHA)
    ow2.blit(omega_t2,(0,0)); ow2.set_alpha(omega_a2)
    surf.blit(ow2,(WIDTH//2-ow2.get_width()//2,HEIGHT//2-ow2.get_height()//2))

def _draw_zone7_volcanic(surf, cam_x, tick):
    par1 = int(cam_x * 0.10)
    par2 = int(cam_x * 0.25)
    par3 = int(cam_x * 0.45)

    # Ember rain
    ember_rng = random.Random(tick//4)
    for _ in range(20):
        ex=ember_rng.randint(0,WIDTH); ey=ember_rng.randint(0,GROUND_Y)
        ea=ember_rng.randint(80,200); er=ember_rng.randint(1,3)
        es=pygame.Surface((er*2+2,er*2+2),pygame.SRCALPHA)
        ec=random.choice([(255,180,20),(255,100,10),(255,220,80)])
        pygame.draw.circle(es,(*ec,ea),(er+1,er+1),er)
        surf.blit(es,(ex,ey))

    # Distant volcano silhouettes — layer 1
    vol_rng=random.Random(11)
    for vx2 in range(-200,WORLD_WIDTH+200,340):
        sx2=vx2-par1
        vh=120+(vx2*7)%160
        vw=200+(vx2*3)%120
        vc=(18+vol_rng.randint(0,8),5+vol_rng.randint(0,4),3)
        pts=[(sx2,GROUND_Y),(sx2+vw//2,GROUND_Y-vh),(sx2+vw,GROUND_Y)]
        pygame.draw.polygon(surf,vc,pts)
        # Lava glow at peak
        peak_a=int(45+abs(math.sin(tick*0.04+vx2*0.002))*80)
        ps=pygame.Surface((60,60),pygame.SRCALPHA)
        pygame.draw.ellipse(ps,(255,80,10,peak_a),(0,0,60,40))
        surf.blit(ps,(sx2+vw//2-30,GROUND_Y-vh-25))
        # Eruption particles
        if (vx2*3+tick//30)%90<3:
            for _ in range(5):
                ep=ember_rng.randint(0,20)
                PARTICLES.spawn_ember(sx2+vw//2+random.randint(-20,20)+cam_x,
                                       GROUND_Y-vh+random.randint(-10,5))

    # Mid-ground rocky terrain with lava cracks
    for rx2 in range(-100,WORLD_WIDTH+200,180):
        sx3=rx2-par2
        rh2=18+(rx2*5)%35
        rw2=160+(rx2*9)%80
        pygame.draw.polygon(surf,(35,14,6),
            [(sx3,GROUND_Y),(sx3+rw2//3,GROUND_Y-rh2),
             (sx3+rw2*2//3,GROUND_Y-rh2+8),(sx3+rw2,GROUND_Y)])
        # Lava crack glow
        lava_a2=int(60+abs(math.sin(tick*0.055+rx2*0.003))*80)
        for ci in range(3):
            cx2=sx3+rng2_internal(rx2,ci,rw2)
            ls2=pygame.Surface((8,4),pygame.SRCALPHA)
            ls2.fill((255,80,0,lava_a2))
            surf.blit(ls2,(cx2,GROUND_Y-rh2+4+ci*4))

    # Lava river at ground level
    lava_col2=(200,45,5)
    for lx2 in range(0,WIDTH+20,20):
        wave2=int(math.sin((lx2+tick*2)*0.05)*4)
        la3=int(140+abs(math.sin((lx2+tick)*0.03))*80)
        ls3=pygame.Surface((22,12),pygame.SRCALPHA)
        ls3.fill((*lava_col2,la3))
        surf.blit(ls3,(lx2-1,GROUND_Y-8+wave2))
        # Lava glow
        if lx2%60==0:
            LIGHTS.add(lx2+cam_x,GROUND_Y,45,LAVA_COL,0.5,life=1)

    # Smoke columns rising from ground
    for sx4 in range(0,WIDTH+80,120):
        sx5=sx4+par3%120
        for si in range(8):
            t2=si/7
            smoke_y=GROUND_Y-int(t2*200)
            smoke_r=int(12+t2*28)
            smoke_a=int((1-t2)*55)
            sway2=int(math.sin(tick*0.012+sx4*0.03+si*0.5)*14)
            ss2=pygame.Surface((smoke_r*2+2,smoke_r*2+2),pygame.SRCALPHA)
            pygame.draw.circle(ss2,(55,42,35,smoke_a),(smoke_r+1,smoke_r+1),smoke_r)
            surf.blit(ss2,(sx5+sway2-smoke_r-1,smoke_y-smoke_r-1))

    # Distant eruption flash
    erupt_cycle=(tick//120)%3
    if (tick%120)<25:
        ea2=int(min(80,(tick%120)*5))
        ef=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        ef.fill((255,60,0,ea2))
        surf.blit(ef,(0,0))

def _draw_zone8_space(surf, cam_x, tick):
    par1 = int(cam_x * 0.06)
    par2 = int(cam_x * 0.18)
    par3 = int(cam_x * 0.38)

    # Deep space nebula
    for ni in range(4):
        neb_s=pygame.Surface((400,280),pygame.SRCALPHA)
        neb_x=80+ni*420; neb_y=50+ni*35
        neb_cols=[(60,10,100),(20,5,80),(80,15,60),(10,40,120)]
        nc=neb_cols[ni]
        na=int(14+math.sin(tick*0.012+ni)*8)
        pygame.draw.ellipse(neb_s,(*nc,na),(0,0,400,280))
        surf.blit(neb_s,(neb_x-par1//3,neb_y))

    # Stars (two parallax layers)
    star_rng=random.Random(77)
    for i in range(200):
        sx2=star_rng.randint(0,WIDTH*3)
        sy2=star_rng.randint(0,int(HEIGHT*0.8))
        layer=star_rng.randint(1,2)
        par_off=par1//layer
        ssx=(sx2-par_off)%WIDTH
        tw=abs(math.sin(tick*0.025+i*0.7))
        sa=int(tw*200)
        if sa<10: continue
        sr=max(1,star_rng.randint(1,3) if tw>0.7 else 1)
        ss=pygame.Surface((sr*2+2,sr*2+2),pygame.SRCALPHA)
        sc=(200+star_rng.randint(0,55),210+star_rng.randint(0,45),255)
        pygame.draw.circle(ss,(*sc,sa),(sr+1,sr+1),sr)
        surf.blit(ss,(ssx-sr-1,sy2-sr-1))

    # Space station structure — background modules
    for mx in range(-100,WORLD_WIDTH+200,280):
        sx3=mx-par2
        # Module connector
        pygame.draw.line(surf,(25,32,48),(sx3-60,GROUND_Y-180),(sx3+60,GROUND_Y-180),4)
        # Module boxes
        for boff in (-55,55):
            pygame.draw.rect(surf,(18,26,42),(sx3+boff-22,GROUND_Y-205,44,48),border_radius=3)
            pygame.draw.rect(surf,(28,40,62),(sx3+boff-22,GROUND_Y-205,44,12),border_radius=3)
            # Solar panels
            for sp in range(3):
                pygame.draw.rect(surf,(20,80,180),
                    (sx3+boff-30,GROUND_Y-228+sp*12,60,9),border_radius=1)
                pygame.draw.rect(surf,(30,120,220),
                    (sx3+boff-30,GROUND_Y-228+sp*12,60,3),border_radius=1)
                pygame.draw.line(surf,(14,20,32),
                    (sx3+boff,GROUND_Y-228),(sx3+boff,GROUND_Y-205),2)
            # Blinking light
            blink=(tick//20+mx)%30<15
            bl_col=(255,50,50) if blink else (80,10,10)
            bls=pygame.Surface((8,8),pygame.SRCALPHA)
            pygame.draw.circle(bls,(*bl_col,200),(4,4),4)
            surf.blit(bls,(sx3+boff-4,GROUND_Y-200))

    # Foreground station floor panels
    for px in range(0,WIDTH+80,48):
        panel_x=px+par3%48
        for row in range(2):
            py=GROUND_Y-row*18
            col3=(22,30,46) if (panel_x//48+row)%2==0 else (28,38,58)
            pygame.draw.rect(surf,col3,(panel_x-2,py-16,50,18))
            pygame.draw.rect(surf,(35,48,72),(panel_x-2,py-16,50,4))
            pygame.draw.rect(surf,(14,20,32),(panel_x-2,py-16,50,18),1)

    # Planet in background — moves very slowly
    planet_x=int(WIDTH*0.75-par1*0.08); planet_y=int(HEIGHT*0.2)
    planet_r=90
    ps2=pygame.Surface((planet_r*2+4,planet_r*2+4),pygame.SRCALPHA)
    pygame.draw.circle(ps2,(28,80,155,210),(planet_r+2,planet_r+2),planet_r)
    # Atmosphere
    pygame.draw.circle(ps2,(60,130,200,40),(planet_r+2,planet_r+2),planet_r+12)
    # Continent blobs
    cont_rng=random.Random(42)
    for _ in range(6):
        cx3=cont_rng.randint(20,planet_r*2-20)
        cy3=cont_rng.randint(20,planet_r*2-20)
        cr3=cont_rng.randint(8,24)
        if math.hypot(cx3-(planet_r+2),cy3-(planet_r+2))<planet_r-cr3:
            pygame.draw.circle(ps2,(40,155,62,190),(cx3+2,cy3+2),cr3)
    # Cloud bands
    pygame.draw.ellipse(ps2,(180,210,255,50),(4,planet_r-12,planet_r*2-4,24))
    pygame.draw.ellipse(ps2,(180,210,255,35),(8,planet_r+18,planet_r*2-16,16))
    # Terminator shadow
    shad_s=pygame.Surface((planet_r*2+4,planet_r*2+4),pygame.SRCALPHA)
    pygame.draw.circle(shad_s,(0,0,20,130),(planet_r+32,planet_r+2),planet_r)
    ps2.blit(shad_s,(0,0))
    surf.blit(ps2,(planet_x-planet_r-2,planet_y-planet_r-2))

    # Holographic warning strips
    for wx2 in (80,WIDTH-80):
        for wy2 in range(GROUND_Y-160,GROUND_Y,22):
            sc=(0,180,255) if (wy2//22+tick//8)%2==0 else (0,80,120)
            pygame.draw.line(surf,sc,(wx2,wy2),(wx2,wy2+18),2)
    # HUD-style scan line on floor
    scan_y2=(tick*3)%48
    ss3=pygame.Surface((WIDTH,2),pygame.SRCALPHA)
    ss3.fill((0,150,255,30))
    surf.blit(ss3,(0,GROUND_Y-scan_y2))

def rng2_internal(seed, i, max_val):
    return (seed*31+i*17)%max(1,max_val)

_BG_CACHE: dict = {}
_BG_CACHE_CAM: dict = {}

def draw_world(surf, zone_cfg, cam_x, tick=0):
    zn = zone_cfg.get("zone_num", 1)
    top_c, bot_c = ZONE_SKY.get(zn, ((20,25,45),(40,55,90)))
    _draw_gradient_sky(surf, top_c, bot_c)

    last_cam = _BG_CACHE_CAM.get(zn, -9999)
    if zn not in _BG_CACHE or abs(cam_x - last_cam) > 120:
        bg = pygame.Surface((WIDTH, HEIGHT))
        if   zn == 1: _draw_zone1_city(bg, cam_x, tick)
        elif zn == 2: _draw_zone2_forest(bg, cam_x, tick)
        elif zn == 3: _draw_zone3_desert(bg, cam_x, tick)
        elif zn == 4: _draw_zone4_base(bg, cam_x, tick)
        elif zn == 5: _draw_zone5_arctic(bg, cam_x, tick)
        elif zn == 6: _draw_zone6_omega(bg, cam_x, tick)
        elif zn == 7: _draw_zone7_volcanic(bg, cam_x, tick)
        elif zn == 8: _draw_zone8_space(bg, cam_x, tick)
        _BG_CACHE[zn] = bg
        _BG_CACHE_CAM[zn] = cam_x

    surf.blit(_BG_CACHE[zn], (0, 0))

    gc_base, gc_light, gc_shadow = ZONE_GROUND.get(zn, ((60,48,32),(88,68,42),(42,30,20)))
    for plat in current_platforms:
        sr = pygame.Rect(plat.x - cam_x, plat.y, plat.width, plat.height)
        if -plat.width - 10 < sr.x < WIDTH + 10:
            pygame.draw.rect(surf, gc_base, sr)
            pygame.draw.rect(surf, gc_light, (sr.x, sr.y, sr.width, 4))
            pygame.draw.rect(surf, gc_shadow, (sr.x, sr.y+sr.height-4, sr.width, 4))
            pygame.draw.rect(surf, gc_shadow, sr, 1)

# ═══════════════════════════════════════════════════
#  CUTSCENE
# ═══════════════════════════════════════════════════
def show_cutscene(zone_before):
    lines = STORY.get(zone_before, [])
    if not lines:
        return

    # Zone-specific colour palettes for panels
    zone_palettes = {
        0: {"sky": (18, 28, 48),   "accent": (180, 30, 30),  "ground": (42, 32, 22)},
        1: {"sky": (12, 18, 32),   "accent": (80, 130, 220), "ground": (55, 42, 30)},
        2: {"sky": (12, 32, 14),   "accent": (55, 185, 65),  "ground": (30, 55, 22)},
        3: {"sky": (72, 48, 22),   "accent": (220, 165, 40), "ground": (125, 88, 40)},
        4: {"sky": (8,  8,  22),   "accent": (120, 30, 200), "ground": (35, 35, 48)},
        5: {"sky": (140,170,205),  "accent": (80, 200, 220), "ground": (175,195,218)},
    }
    pal = zone_palettes.get(zone_before, zone_palettes[0])

    f_title  = pygame.font.SysFont("consolas", 16, bold=True)
    f_text   = pygame.font.SysFont("consolas", 19, bold=True)
    f_hint   = pygame.font.SysFont("consolas", 13)
    f_label  = pygame.font.SysFont("consolas", 11)
    f_zone   = pygame.font.SysFont("consolas", 42, bold=True)

    tick = 0
    char_index = 0
    current_line = 0
    line_timer = 0
    displayed = [""]
    done = False
    scan_y = 0.0  # CRT scanline position

    while not done:
        tick += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    if current_line < len(lines):
                        displayed = list(lines); current_line = len(lines)
                    else:
                        done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                done = True

        # Typing effect
        line_timer += 1
        if current_line < len(lines):
            line = lines[current_line]
            if char_index < len(line):
                if line_timer % 4 == 0:
                    char_index += 1
                    displayed[current_line] = line[:char_index]
            else:
                if line_timer > 120:
                    current_line += 1; char_index = 0; line_timer = 0
                    if current_line < len(lines):
                        displayed.append("")

        # ── Background: gradient sky ──────────────────────────────────────────
        sky_t = pal["sky"]; sky_b = tuple(min(255, c + 30) for c in pal["sky"])
        for py in range(0, HEIGHT, 4):
            t5 = py / HEIGHT
            r5 = int(sky_t[0] + (sky_b[0]-sky_t[0])*t5)
            g5 = int(sky_t[1] + (sky_b[1]-sky_t[1])*t5)
            b5 = int(sky_t[2] + (sky_b[2]-sky_t[2])*t5)
            pygame.draw.rect(screen, (r5, g5, b5), (0, py, WIDTH, 4))

        # Stars / dust particles in bg
        rng_bg = random.Random(42)
        for i in range(70):
            sx3 = rng_bg.randint(0, WIDTH)
            sy3 = rng_bg.randint(0, int(HEIGHT * 0.65))
            sa3 = int(60 + abs(math.sin(tick * 0.025 + i * 0.8)) * 110)
            ss3 = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(ss3, (200, 210, 230, sa3), (1, 1), 1)
            screen.blit(ss3, (sx3, sy3))

        # Ground silhouette (zone-specific)
        gnd = pal["ground"]
        ground_pts = [(0, HEIGHT)]
        steps = 24
        for gi in range(steps + 1):
            gx3 = int(gi * WIDTH / steps)
            gh3 = int(HEIGHT - 80 - abs(math.sin(gi * 0.6 + zone_before)) * 55
                      - (gi * 7) % 60)
            ground_pts.append((gx3, gh3))
        ground_pts.append((WIDTH, HEIGHT))
        pygame.draw.polygon(screen, gnd, ground_pts)
        pygame.draw.rect(screen, tuple(min(255, c + 18) for c in gnd),
                         (0, HEIGHT - 80, WIDTH, 80))

        # ── Left: animated soldier portrait ──────────────────────────────────
        port_x = 105; port_y = HEIGHT // 2 - 10

        # Portrait frame
        pf_rect = pygame.Rect(18, port_y - 115, 175, 230)
        pf_surf = pygame.Surface((pf_rect.w, pf_rect.h), pygame.SRCALPHA)
        # Gradient fill
        for py2 in range(pf_rect.h):
            t6 = py2 / pf_rect.h
            a6 = int(220 - t6 * 60)
            pygame.draw.line(pf_surf, (4, 6, 12, a6), (0, py2), (pf_rect.w, py2))
        # Accent border
        pygame.draw.rect(pf_surf, pal["accent"], (0, 0, pf_rect.w, pf_rect.h), 2, border_radius=4)
        pygame.draw.rect(pf_surf, tuple(min(255, c + 40) for c in pal["accent"]),
                         (0, 0, pf_rect.w, 3), border_radius=4)
        screen.blit(pf_surf, (pf_rect.x, pf_rect.y))

        # "INTEL" label on portrait frame
        il = f_label.render("◈ INTEL", True, pal["accent"])
        screen.blit(il, (pf_rect.x + 6, pf_rect.y + 5))

        # Draw detailed soldier (facing right, slightly animated)
        pcx = port_x; pcy = port_y + 30
        skin = SKINS[current_skin]
        bc2  = skin["body"]; hc2 = skin["head"]; helm2 = skin["helmet"]; vest2 = skin["vest"]
        boot2= skin.get("boot", (22,18,12))
        anim_breath = int(math.sin(tick * 0.04) * 2)

        # Shadow
        sh2 = pygame.Surface((44, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(sh2, (0, 0, 0, 60), (0, 0, 44, 8))
        screen.blit(sh2, (pcx - 22, pcy + 55))
        # Boots
        pygame.draw.rect(screen, boot2, (pcx - 10, pcy + 45, 11, 10), border_radius=2)
        pygame.draw.rect(screen, boot2, (pcx + 1,  pcy + 45, 11, 10), border_radius=2)
        # Legs
        pygame.draw.rect(screen, bc2, (pcx - 10, pcy + 28, 10, 18), border_radius=2)
        pygame.draw.rect(screen, bc2, (pcx + 1,  pcy + 28, 10, 18), border_radius=2)
        pygame.draw.rect(screen, (28, 22, 12), (pcx - 11, pcy + 27, 22, 4))  # belt
        # Vest / body
        vest_hi2 = tuple(min(255, c+22) for c in vest2)
        vest_dk2 = tuple(max(0, c-18) for c in vest2)
        pygame.draw.rect(screen, vest2, (pcx - 12, pcy + 12, 24, 18 + anim_breath), border_radius=3)
        pygame.draw.rect(screen, vest_hi2, (pcx - 12, pcy + 12, 24, 5), border_radius=3)
        pygame.draw.rect(screen, vest_dk2, (pcx - 8, pcy + 14, 16, 14), border_radius=2)
        for row_y2 in range(pcy + 17, pcy + 27, 4):
            pygame.draw.line(screen, vest_dk2, (pcx-7, row_y2), (pcx+7, row_y2), 1)
        # Pouches
        pygame.draw.rect(screen, vest_dk2, (pcx - 15, pcy + 15, 5, 8), border_radius=1)
        pygame.draw.rect(screen, vest_dk2, (pcx + 10, pcy + 15, 5, 8), border_radius=1)
        # Arms
        pygame.draw.line(screen, vest2, (pcx - 10, pcy + 14), (pcx - 18, pcy + 28), 5)
        pygame.draw.line(screen, vest2, (pcx + 10, pcy + 14), (pcx + 18, pcy + 26), 5)
        pygame.draw.circle(screen, boot2, (pcx - 18, pcy + 28), 4)
        pygame.draw.circle(screen, boot2, (pcx + 18, pcy + 26), 4)
        # Rifle
        pygame.draw.rect(screen, (40, 40, 40), (pcx + 14, pcy + 20, 24, 7))
        pygame.draw.rect(screen, (60, 60, 60), (pcx + 14, pcy + 20, 24, 2))
        pygame.draw.rect(screen, (35, 25, 12), (pcx + 8, pcy + 22, 8, 9))
        # Neck
        pygame.draw.rect(screen, hc2, (pcx - 3, pcy + 8, 6, 6))
        # Head
        helm_hi2 = tuple(min(255, c+22) for c in helm2)
        helm_dk2 = tuple(max(0, c-18) for c in helm2)
        pygame.draw.circle(screen, hc2, (pcx, pcy + 4), 10)
        pygame.draw.circle(screen, tuple(max(0,c-22) for c in hc2), (pcx + 3, pcy + 5), 5)
        pygame.draw.ellipse(screen, hc2, (pcx + 8, pcy + 1, 5, 7))
        pygame.draw.circle(screen, (20, 15, 10), (pcx + 4, pcy + 2), 2)
        # Helmet
        pygame.draw.arc(screen, helm2, pygame.Rect(pcx-13, pcy-6, 26, 20), 0, math.pi, 0)
        pygame.draw.rect(screen, helm2, (pcx - 13, pcy + 4, 26, 7))
        pygame.draw.arc(screen, helm_hi2, pygame.Rect(pcx-10, pcy-4, 13, 11), 0.3, math.pi-0.3, 3)
        pygame.draw.rect(screen, helm_dk2, (pcx - 14, pcy + 9, 28, 3), border_radius=1)
        camo_rng2 = random.Random(99)
        for _ in range(5):
            csx3 = pcx + camo_rng2.randint(-9, 9)
            csy3 = pcy + camo_rng2.randint(-4, 8)
            pygame.draw.circle(screen, helm_dk2, (csx3, csy3), camo_rng2.randint(1, 2))

        # Rank chevrons on arm
        for chev_i in range(2):
            chev_y = pcy + 17 + chev_i * 4
            pygame.draw.line(screen, pal["accent"],
                             (pcx - 14, chev_y + 2), (pcx - 10, chev_y), 1)
            pygame.draw.line(screen, pal["accent"],
                             (pcx - 10, chev_y), (pcx - 6, chev_y + 2), 1)

        # ── Right: text panel ─────────────────────────────────────────────────
        tp_x = 220; tp_w = WIDTH - tp_x - 28
        tp_rect = pygame.Rect(tp_x, 55, tp_w, HEIGHT - 130)
        tp_surf = pygame.Surface((tp_rect.w, tp_rect.h), pygame.SRCALPHA)
        for py3 in range(tp_rect.h):
            t7 = py3 / tp_rect.h
            a7 = int(210 - t7 * 55)
            pygame.draw.line(tp_surf, (4, 6, 12, a7), (0, py3), (tp_rect.w, py3))
        pygame.draw.rect(tp_surf, pal["accent"], (0, 0, tp_rect.w, tp_rect.h), 2, border_radius=4)
        pygame.draw.rect(tp_surf, tuple(min(255, c+40) for c in pal["accent"]),
                         (0, 0, tp_rect.w, 3), border_radius=4)
        screen.blit(tp_surf, (tp_rect.x, tp_rect.y))

        # Panel header
        header_label = "VOREINSATZ-BRIEFING" if zone_before == 0 else f"LAGEBERICT — NACH ZONE {zone_before}"
        hl = f_title.render(header_label, True, pal["accent"])
        screen.blit(hl, (tp_x + 14, 64))
        pygame.draw.line(screen, pal["accent"],
                         (tp_x + 10, 86), (tp_x + tp_w - 10, 86), 1)

        # Decorative zone number watermark
        if zone_before > 0:
            wm = f_zone.render(f"Z{zone_before}", True, pal["accent"])
            wm.set_alpha(18)
            screen.blit(wm, (WIDTH - wm.get_width() - 38, HEIGHT - wm.get_height() - 55))

        # Status indicators (top-right of text panel)
        status_items = [
            (f"SCHWIERIGKEIT: {get_diff()['label']}", get_diff()["color"]),
            (f"SOLDAT: {SKINS[current_skin]['label']}", (180, 180, 200)),
        ]
        for si2, (slabel, scol) in enumerate(status_items):
            st2 = f_label.render(slabel, True, scol)
            screen.blit(st2, (tp_x + tp_w - st2.get_width() - 14, 65 + si2 * 14))

        # Text lines with typewriter effect
        for i, line in enumerate(displayed):
            if i >= len(lines): break
            # Active line highlight
            if i == current_line and (tick // 20) % 2 == 0:
                hl_surf = pygame.Surface((tp_w - 28, 26), pygame.SRCALPHA)
                hl_surf.fill((*pal["accent"], 18))
                screen.blit(hl_surf, (tp_x + 14, 98 + i * 48))
            col = WHITE if i < current_line else (225, 222, 210)
            # Line number
            ln = f_label.render(f"{i+1:02d}", True, tuple(max(0,c-80) for c in pal["accent"]))
            screen.blit(ln, (tp_x + 14, 103 + i * 48))
            # Main text
            t_surf2 = f_text.render(line, True, col)
            screen.blit(t_surf2, (tp_x + 38, 100 + i * 48))

        # Typing cursor
        if current_line < len(lines) and (tick // 14) % 2 == 0:
            ci2 = min(current_line, len(displayed) - 1)
            cx_pos2 = tp_x + 38 + f_text.size(displayed[ci2])[0]
            cur_surf = f_text.render("▌", True, pal["accent"])
            screen.blit(cur_surf, (cx_pos2, 100 + ci2 * 48))

        # ── CRT scanline overlay ──────────────────────────────────────────────
        scan_y = (scan_y + 2.5) % HEIGHT
        scan_surf = pygame.Surface((WIDTH, 3), pygame.SRCALPHA)
        scan_surf.fill((255, 255, 255, 12))
        screen.blit(scan_surf, (0, int(scan_y)))
        # Static noise at top
        for _ in range(5):
            nx2 = random.randint(tp_x + 14, tp_x + tp_w - 14)
            ny2 = random.randint(96, 104)
            nd  = random.randint(1, 4)
            pygame.draw.rect(screen, (200, 200, 200), (nx2, ny2, nd, 1))

        # Corner decoration marks
        for corner_x, corner_y, cx_dir, cy_dir in [
            (16, 53, 1, 1), (WIDTH-28, 53, -1, 1),
            (16, HEIGHT-128, 1, -1), (WIDTH-28, HEIGHT-128, -1, -1)
        ]:
            pygame.draw.line(screen, pal["accent"],
                             (corner_x, corner_y), (corner_x + cx_dir * 14, corner_y), 2)
            pygame.draw.line(screen, pal["accent"],
                             (corner_x, corner_y), (corner_x, corner_y + cy_dir * 14), 2)

        # Continue hint
        if current_line >= len(lines):
            hint_alpha2 = int(128 + abs(math.sin(tick * 0.06)) * 127)
            hint = f_hint.render("▶  ENTER / SPACE — Weiter", True, pal["accent"])
            hs2 = pygame.Surface((hint.get_width() + 24, hint.get_height() + 10), pygame.SRCALPHA)
            hs2.fill((0, 0, 0, 100))
            pygame.draw.rect(hs2, pal["accent"], (0, 0, hs2.get_width(), hs2.get_height()), 1, border_radius=3)
            hs2.blit(hint, (12, 5))
            hs2.set_alpha(hint_alpha2)
            screen.blit(hs2, (WIDTH // 2 - hs2.get_width() // 2, HEIGHT - 58))

        pygame.display.flip()
        clock.tick(FPS)
# ═══════════════════════════════════════════════════
#  PAUSE MENÜ
# ═══════════════════════════════════════════════════
def show_pause_menu(player):
    """Zeigt Pause-Menü. Gibt 'resume','menu','quit' zurück."""
    global current_skin
    SFX.play(SFX.pause)
    f_title=pygame.font.SysFont("consolas",40,bold=True)
    f_sub  =pygame.font.SysFont("consolas",18)

    class PauseBtn:
        def __init__(self,text,x,y,w=220,h=44):
            self.text=text;self.rect=pygame.Rect(x-w//2,y-h//2,w,h)
            self.hovered=False;self.font=pygame.font.SysFont("consolas",18,bold=True)
        def draw(self,surf):
            bg=(120,25,25) if self.hovered else (40,12,12)
            brd=(200,50,50) if self.hovered else (80,25,25)
            tc=WHITE if self.hovered else (180,140,140)
            pygame.draw.rect(surf,bg,self.rect,border_radius=5)
            pygame.draw.rect(surf,brd,self.rect,2,border_radius=5)
            t=self.font.render(self.text,True,tc)
            surf.blit(t,(self.rect.centerx-t.get_width()//2,self.rect.centery-t.get_height()//2))
        def update(self,pos): self.hovered=self.rect.collidepoint(pos)
        def clicked(self,pos): return self.rect.collidepoint(pos)

    cx=WIDTH//2
    btns=[PauseBtn("▶  WEITER",       cx,205),
          PauseBtn("◉  SKIN",         cx,258),
          PauseBtn("⚙  EINSTELLUNGEN",cx,311),
          PauseBtn("⌂  HAUPTMENÜ",    cx,364),
          PauseBtn("✕  BEENDEN",      cx,417)]

    # Skin-Auswahl
    skin_keys=list(SKINS.keys()); skin_idx=skin_keys.index(current_skin)
    achieved=load_achievements()
    tick=0

    while True:
        tick+=1; mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: return "resume"
                if event.key==pygame.K_LEFT:
                    skin_idx=(skin_idx-1)%len(skin_keys)
                    current_skin=skin_keys[skin_idx]
                if event.key==pygame.K_RIGHT:
                    skin_idx=(skin_idx+1)%len(skin_keys)
                    sk=SKINS[skin_keys[skin_idx]]
                    if sk["unlock"] is None or sk["unlock"] in achieved:
                        current_skin=skin_keys[skin_idx]
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if btns[0].clicked((mx,my)): return "resume"
                if btns[1].clicked((mx,my)):
                    # Skin wechseln (nächster freigeschaltener)
                    for _ in range(len(skin_keys)):
                        skin_idx=(skin_idx+1)%len(skin_keys)
                        sk=SKINS[skin_keys[skin_idx]]
                        if sk["unlock"] is None or sk["unlock"] in achieved:
                            current_skin=skin_keys[skin_idx]; break
                if btns[2].clicked((mx,my)): show_settings_menu()
                if btns[3].clicked((mx,my)): return "menu"
                if btns[4].clicked((mx,my)): pygame.quit();sys.exit()

        # Halbtransparentes Overlay über Spielfeld
        overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        overlay.fill((0,0,0,160)); screen.blit(overlay,(0,0))

        t=f_title.render("— PAUSE —",True,WHITE)
        screen.blit(t,(WIDTH//2-t.get_width()//2,140))

        # Aktiver Skin
        sk=SKINS[current_skin]
        st=f_sub.render(f"Skin: {sk['label']}  —  {sk['desc']}",True,GRAY)
        screen.blit(st,(WIDTH//2-st.get_width()//2,185))
        # Kleiner Skin-Preview (Farbrechteck)
        pygame.draw.rect(screen,sk["body"],(WIDTH//2-20,205,40,20),border_radius=3)

        # Schwierigkeitsgrad
        diff_cfg=get_diff()
        dt=f_sub.render(f"Schwierigkeit: {diff_cfg['label']}",True,diff_cfg["color"])
        screen.blit(dt,(WIDTH//2-dt.get_width()//2,228))

        for b in btns: b.update((mx,my));b.draw(screen)

        # Steuerung Hinweis
        hint=f_sub.render("ESC: Weiterspielen  |  ← → : Skin wechseln",True,(80,80,100))
        screen.blit(hint,(WIDTH//2-hint.get_width()//2,HEIGHT-30))

        pygame.display.flip();clock.tick(FPS)

# ═══════════════════════════════════════════════════
#  MENÜ
# ═══════════════════════════════════════════════════
def draw_menu_bg(surf, tick):
    # Deep military dark base
    surf.fill((4, 6, 10))

    # Subtle hex grid overlay
    hex_size = 38
    hex_col  = (12, 18, 12)
    for hy in range(-hex_size, HEIGHT+hex_size, int(hex_size*1.74)):
        for hx in range(-hex_size, WIDTH+hex_size, hex_size*2):
            offset_x = hex_size if (hy//int(hex_size*1.74))%2==1 else 0
            for angle_i in range(6):
                ang5 = math.pi/6 + angle_i*math.pi/3
                ang6 = math.pi/6 + (angle_i+1)*math.pi/3
                pygame.draw.line(surf, hex_col,
                                 (int(hx+offset_x+math.cos(ang5)*hex_size),
                                  int(hy+math.sin(ang5)*hex_size)),
                                 (int(hx+offset_x+math.cos(ang6)*hex_size),
                                  int(hy+math.sin(ang6)*hex_size)), 1)

    # Animated scan line
    scan_y2 = int((tick * 2.2) % HEIGHT)
    scan_s2 = pygame.Surface((WIDTH, 3), pygame.SRCALPHA)
    scan_s2.fill((40, 90, 40, 22))
    surf.blit(scan_s2, (0, scan_y2))

    # Stars
    rng_m = random.Random(42)
    for i8 in range(50):
        sx14 = rng_m.randint(0, WIDTH); sy14 = rng_m.randint(0, HEIGHT//3)
        tw3  = abs(math.sin(tick*0.025+i8*0.9))
        sa5  = int(tw3*120)
        if sa5 > 8:
            ss5 = pygame.Surface((4,4),pygame.SRCALPHA)
            pygame.draw.circle(ss5,(200,220,200,sa5),(2,2),1)
            surf.blit(ss5,(sx14,sy14))

    # City silhouette base
    for rx6,rw6,rh7 in [(0,115,175),(130,88,128),(248,148,198),(455,98,158),(610,128,188),(782,108,143),(945,138,168),(1108,118,138),(1280,95,162)]:
        pygame.draw.rect(surf,(7,10,16),(rx6,HEIGHT-rh7,rw6,rh7))
    # Ground line
    pygame.draw.rect(surf,(10,16,10),(0,HEIGHT-40,WIDTH,40))
    pygame.draw.rect(surf,(18,28,18),(0,HEIGHT-40,WIDTH,2))

    # Red/green accent glow at base
    for gx2 in range(0,WIDTH,180):
        glow_c2 = (180,25,25) if (gx2//180)%3!=0 else (25,120,35)
        gs8 = pygame.Surface((80,30),pygame.SRCALPHA)
        pulse4 = int(20+abs(math.sin(tick*0.04+gx2*0.01))*28)
        pygame.draw.ellipse(gs8,(*glow_c2,pulse4),(0,0,80,30))
        surf.blit(gs8,(gx2-10,HEIGHT-55))

    # Corner tactical brackets
    blen = 32
    for (bcx,bcy),(bsx,bsy) in [((0,0),(1,1)),((WIDTH,0),(-1,1)),((0,HEIGHT),(1,-1)),((WIDTH,HEIGHT),(-1,-1))]:
        pygame.draw.line(surf,(35,80,35),(bcx,bcy),(bcx+bsx*blen,bcy),2)
        pygame.draw.line(surf,(35,80,35),(bcx,bcy),(bcx,bcy+bsy*blen),2)

    # Centre crosshair watermark
    ch_a2 = int(8+abs(math.sin(tick*0.02))*10)
    ch_r2 = 120
    ch_s2 = pygame.Surface((ch_r2*2+4,ch_r2*2+4),pygame.SRCALPHA)
    pygame.draw.circle(ch_s2,(35,75,35,ch_a2),(ch_r2+2,ch_r2+2),ch_r2,1)
    pygame.draw.line(ch_s2,(35,75,35,ch_a2),(ch_r2-30+2,ch_r2+2),(ch_r2+30+2,ch_r2+2),1)
    pygame.draw.line(ch_s2,(35,75,35,ch_a2),(ch_r2+2,ch_r2-30+2),(ch_r2+2,ch_r2+30+2),1)
    surf.blit(ch_s2,(WIDTH//2-ch_r2-2,HEIGHT//2-ch_r2-2))


class MenuButton:
    def __init__(self, text, x, y, w=270, h=52):
        self.text    = text
        self.rect    = pygame.Rect(x-w//2, y-h//2, w, h)
        self.hovered = False
        self.font    = pygame.font.SysFont("consolas", 19, bold=True)
        self._hover_t= 0

    def draw(self, surf):
        t12 = self._hover_t
        # Background
        bg2   = (18, 40, 18) if not self.hovered else (32, 68, 28)
        brd2  = (45, 95, 42) if not self.hovered else (80, 185, 65)
        tc2   = (120, 180, 110) if not self.hovered else (200, 255, 185)

        # Glow when hovered
        if self.hovered:
            gs9 = pygame.Surface((self.rect.w+16,self.rect.h+16),pygame.SRCALPHA)
            gl_a = int(28+abs(math.sin(pygame.time.get_ticks()*0.01))*22)
            pygame.draw.rect(gs9,(65,155,50,gl_a),(0,0,self.rect.w+16,self.rect.h+16),border_radius=7)
            surf.blit(gs9,(self.rect.x-8,self.rect.y-8))

        pygame.draw.rect(surf, bg2,  self.rect, border_radius=5)
        pygame.draw.rect(surf, brd2, self.rect, 2, border_radius=5)
        # Top edge highlight
        pygame.draw.rect(surf, tuple(min(255,c+30) for c in brd2),
                         (self.rect.x+2, self.rect.y+1, self.rect.w-4, 1))
        # Active indicator bar
        if self.hovered:
            pygame.draw.rect(surf, (80,185,65),
                             (self.rect.x+3, self.rect.y+self.rect.h-3, self.rect.w-6, 2), border_radius=1)

        # Tactical prefix ◈
        prefix = "◈ "
        pf_col = (55,130,50) if not self.hovered else (100,220,80)
        pf_t   = self.font.render(prefix, True, pf_col)
        btn_t  = self.font.render(self.text, True, tc2)
        total_w = pf_t.get_width() + btn_t.get_width()
        bx7 = self.rect.centerx - total_w//2
        by7 = self.rect.centery - btn_t.get_height()//2
        surf.blit(pf_t,  (bx7, by7))
        surf.blit(btn_t, (bx7+pf_t.get_width(), by7))

        # Corner marks
        for cmx,cmy in [(self.rect.x+2,self.rect.y+2),(self.rect.right-8,self.rect.y+2),
                         (self.rect.x+2,self.rect.bottom-8),(self.rect.right-8,self.rect.bottom-8)]:
            pygame.draw.rect(surf, brd2, (cmx,cmy,6,1))
            pygame.draw.rect(surf, brd2, (cmx,cmy,1,6))

    def update(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

def show_settings_menu():
    s = load_settings()
    f_title = pygame.font.SysFont("consolas", 34, bold=True)
    f_lbl   = pygame.font.SysFont("consolas", 14)
    f_val   = pygame.font.SysFont("consolas", 14, bold=True)
    f_hint  = pygame.font.SysFont("consolas", 12)

    FPS_OPTIONS = [30, 60, 120, 144, 0]
    FPS_LABELS  = ["30", "60", "120", "144", "UNL"]
    RES_OPTIONS = ["fullscreen", "1280x720", "1920x1080", "1600x900"]

    rows = [
        {"label": "Master-Lautstaerke", "key": "master_volume", "type": "slider"},
        {"label": "SFX-Lautstaerke",    "key": "sfx_volume",    "type": "slider"},
        {"label": "FPS-Limit",          "key": "fps_cap",       "type": "cycle",
         "options": FPS_OPTIONS, "labels": FPS_LABELS},
        {"label": "Aufloesung",         "key": "resolution",    "type": "cycle",
         "options": RES_OPTIONS, "labels": RES_OPTIONS},
        {"label": "Screenshake",        "key": "screenshake",   "type": "toggle"},
        {"label": "Partikel",           "key": "particles",     "type": "toggle"},
        {"label": "FPS anzeigen",       "key": "show_fps",      "type": "toggle"},
    ]

    SLIDER_W = 260; SLIDER_X = WIDTH//2 + 100
    ROW_Y    = 120; ROW_H    = 52
    back     = MenuButton("ZURUECK / SPEICHERN", WIDTH//2, HEIGHT-58, w=300, h=46)
    dragging = None; tick = 0

    def sli_rect(ri):
        return pygame.Rect(SLIDER_X, ROW_Y + ri*ROW_H + 18, SLIDER_W, 12)

    while True:
        tick += 1; mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); import sys; sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                save_settings(s); apply_settings(s); return
            if event.type == pygame.MOUSEBUTTONUP:   dragging = None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.clicked((mx,my)): save_settings(s); apply_settings(s); return
                for ri, row in enumerate(rows):
                    ry = ROW_Y + ri*ROW_H
                    if row["type"] == "slider" and sli_rect(ri).collidepoint(mx,my):
                        dragging = ri
                    elif row["type"] == "toggle":
                        if pygame.Rect(SLIDER_X, ry+14, 62, 24).collidepoint(mx,my):
                            s[row["key"]] = not s[row["key"]]
                    elif row["type"] == "cycle":
                        opts = row["options"]
                        ci2  = opts.index(s[row["key"]]) if s[row["key"]] in opts else 0
                        btn_l = pygame.Rect(SLIDER_X,      ry+14, 36, 24)
                        btn_r = pygame.Rect(SLIDER_X+224,  ry+14, 36, 24)
                        if btn_l.collidepoint(mx,my):
                            s[row["key"]] = opts[(ci2-1) % len(opts)]
                        if btn_r.collidepoint(mx,my):
                            s[row["key"]] = opts[(ci2+1) % len(opts)]

        if dragging is not None:
            row = rows[dragging]
            sr  = sli_rect(dragging)
            val = max(0.0, min(1.0, (mx - sr.x) / sr.width))
            s[row["key"]] = round(val, 2)

        draw_menu_bg(screen, tick)
        t2 = f_title.render("EINSTELLUNGEN", True, YELLOW)
        screen.blit(t2, (WIDTH//2 - t2.get_width()//2, 28))
        pygame.draw.line(screen, (100,80,20), (WIDTH//2-220,68),(WIDTH//2+220,68),1)

        for ri, row in enumerate(rows):
            ry = ROW_Y + ri*ROW_H
            # Row bg
            rb = pygame.Surface((WIDTH-80, ROW_H-6), pygame.SRCALPHA)
            rb.fill((8,14,8,140) if ri%2==0 else (10,18,10,110))
            pygame.draw.rect(rb,(30,55,28),(0,0,WIDTH-80,ROW_H-6),1,border_radius=3)
            screen.blit(rb,(40, ry))

            # Label
            lt2 = f_lbl.render(row["label"], True, (160,210,155))
            screen.blit(lt2, (60, ry+16))

            if row["type"] == "slider":
                val = s[row["key"]]
                sr  = sli_rect(ri)
                # Track
                pygame.draw.rect(screen,(18,28,18),sr,border_radius=5)
                # Fill
                fw2 = int(sr.width * val)
                if fw2>0: pygame.draw.rect(screen,(60,180,55),(sr.x,sr.y,fw2,sr.height),border_radius=5)
                pygame.draw.rect(screen,(40,85,38),sr,1,border_radius=5)
                # Knob
                kx = sr.x + fw2
                pygame.draw.circle(screen,WHITE,(kx,sr.centery),8)
                pygame.draw.circle(screen,(60,180,55),(kx,sr.centery),6)
                vt = f_val.render(f"{int(val*100)}%", True, WHITE)
                screen.blit(vt,(sr.right+12, ry+16))

            elif row["type"] == "toggle":
                on = s[row["key"]]
                br2 = pygame.Rect(SLIDER_X, ry+14, 62, 24)
                pygame.draw.rect(screen,(30,90,28) if on else (40,28,28),br2,border_radius=12)
                pygame.draw.rect(screen,(60,180,55) if on else (120,40,40),br2,2,border_radius=12)
                kx2 = br2.x+(br2.width-14) if on else br2.x+2
                pygame.draw.circle(screen,WHITE,(kx2+7,br2.centery),9)
                vt2 = f_val.render("AN" if on else "AUS", True,
                                   (80,220,70) if on else (180,60,60))
                screen.blit(vt2,(SLIDER_X+72, ry+16))

            elif row["type"] == "cycle":
                opts  = row["options"]
                lbls  = row["labels"]
                ci3   = opts.index(s[row["key"]]) if s[row["key"]] in opts else 0
                btn_l2 = pygame.Rect(SLIDER_X,     ry+14, 36, 24)
                btn_r2 = pygame.Rect(SLIDER_X+224, ry+14, 36, 24)
                for br3, lbl3 in ((btn_l2,"◀"),(btn_r2,"▶")):
                    hov2 = br3.collidepoint(mx,my)
                    pygame.draw.rect(screen,(35,65,30) if hov2 else (18,36,15),br3,border_radius=4)
                    pygame.draw.rect(screen,(60,140,50),br3,1,border_radius=4)
                    lt3 = f_val.render(lbl3, True, WHITE)
                    screen.blit(lt3,(br3.centerx-lt3.get_width()//2,
                                    br3.centery-lt3.get_height()//2))
                vt3 = f_val.render(lbls[ci3], True, YELLOW)
                screen.blit(vt3,(SLIDER_X+42, ry+16))

        back.update((mx,my)); back.draw(screen)
        hint3 = f_hint.render("ESC: Speichern & Schliessen", True, (38,72,35))
        screen.blit(hint3,(WIDTH//2-hint3.get_width()//2, HEIGHT-18))
        pygame.display.flip()
        clock.tick(60)

def show_main_menu():
    btns = [MenuButton("SPIELEN",       WIDTH//2, 255),
            MenuButton("SCHWIERIGKEIT", WIDTH//2, 318),
            MenuButton("SKINS",         WIDTH//2, 381),
            MenuButton("HIGHSCORES",    WIDTH//2, 444),
            MenuButton("ACHIEVEMENTS",  WIDTH//2, 507),
            MenuButton("STEUERUNG",     WIDTH//2, 570),
            MenuButton("EINSTELLUNGEN", WIDTH//2, 633),]
    sf4 = pygame.font.SysFont("consolas", 58, bold=True)
    tf2 = pygame.font.SysFont("consolas", 15)
    tf3 = pygame.font.SysFont("consolas", 12)
    tick = 0
    while True:
        tick += 1
        mx2, my2 = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btns[0].clicked((mx2,my2)): return "play"
                if btns[1].clicked((mx2,my2)): show_difficulty_select()
                if btns[2].clicked((mx2,my2)): show_skin_select()
                if btns[3].clicked((mx2,my2)): show_highscores()
                if btns[4].clicked((mx2,my2)): show_achievements()
                if btns[5].clicked((mx2,my2)): show_controls()
                if btns[6].clicked((mx2,my2)): show_settings_menu()
        draw_menu_bg(screen, tick)

        # Title with layered glow
        title_str = "PROJEKT FRONTLINE"
        # Outer glow
        for g_off, g_a in [(6,18),(4,32),(2,55)]:
            gs10 = sf4.render(title_str, True, (30,90,25))
            gs10.set_alpha(g_a)
            screen.blit(gs10,(WIDTH//2-gs10.get_width()//2+g_off, 68+g_off))
        # Shadow
        sh7 = sf4.render(title_str, True, (8,28,8))
        screen.blit(sh7,(WIDTH//2-sh7.get_width()//2+3, 72))
        # Main title
        t13 = sf4.render(title_str, True, (75,200,60))
        screen.blit(t13,(WIDTH//2-t13.get_width()//2, 68))
        # Subtitle bar
        sub_bar = pygame.Surface((t13.get_width()+40, 2), pygame.SRCALPHA)
        sub_bar.fill((60,150,50,180))
        screen.blit(sub_bar,(WIDTH//2-t13.get_width()//2-20, 135))

        # Version / subtitle
        alpha4 = int(170+abs(math.sin(tick*0.045))*85)
        sub2 = tf2.render("[ TAKTISCHER 2D-SHOOTER  v7.0 ]", True, (55,120,50))
        sub2.set_alpha(alpha4)
        screen.blit(sub2,(WIDTH//2-sub2.get_width()//2, 142))

        # Info line
        diff_cfg2 = get_diff(); sk2 = SKINS[current_skin]
        info2 = tf3.render(f"◈  Schwierigkeit: {diff_cfg2['label']}   |   Soldat: {sk2['label']}", True, (42,85,40))
        screen.blit(info2,(WIDTH//2-info2.get_width()//2, 162))

        # Buttons
        for b2 in btns:
            b2.update((mx2,my2)); b2.draw(screen)

        # Footer controls hint
        hint2 = tf3.render("WASD:Bewegen  SPACE:Springen  LMB:Schiessen  G:Granate  1-9:Waffe  Q:Waffenrad  ESC:Pause", True, (28,55,28))
        screen.blit(hint2,(WIDTH//2-hint2.get_width()//2, HEIGHT-18))

        # Version stamp
        ver_t = tf3.render("v6.0", True, (22,45,22))
        screen.blit(ver_t,(WIDTH-ver_t.get_width()-10, HEIGHT-ver_t.get_height()-6))

        pygame.display.flip(); clock.tick(FPS)


def show_difficulty_select():
    global current_difficulty
    f1 = pygame.font.SysFont("consolas", 32, bold=True)
    f2 = pygame.font.SysFont("consolas", 14)
    f3 = pygame.font.SysFont("consolas", 12)
    back = MenuButton("◀  ZURÜCK", WIDTH//2, HEIGHT-58, w=210, h=46)
    tick = 0
    while True:
        tick += 1
        mx3, my3 = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.clicked((mx3,my3)): return
                for i9, key2 in enumerate(["easy","normal","hard"]):
                    bx8 = WIDTH//2-310+i9*218; by8 = HEIGHT//2-60
                    if pygame.Rect(bx8, by8, 200, 155).collidepoint(mx3,my3):
                        current_difficulty = key2
        draw_menu_bg(screen, tick)

        # Header
        t14 = f1.render("SCHWIERIGKEITSGRAD", True, (75,200,60))
        screen.blit(t14,(WIDTH//2-t14.get_width()//2, 58))
        pygame.draw.line(screen,(45,105,40),(WIDTH//2-230,98),(WIDTH//2+230,98),1)
        sub3 = f3.render("Wähle deine Herausforderung", True, (38,80,35))
        screen.blit(sub3,(WIDTH//2-sub3.get_width()//2,106))

        for i10, key3 in enumerate(["easy","normal","hard"]):
            cfg3    = DIFFICULTY_SETTINGS[key3]
            bx9     = WIDTH//2-310+i10*218; by9 = HEIGHT//2-60
            is_sel2 = (current_difficulty == key3)
            col4    = cfg3["color"]
            hovered = pygame.Rect(bx9,by9,200,155).collidepoint(mx3,my3)

            # Card background
            card_s = pygame.Surface((200,155),pygame.SRCALPHA)
            for py7 in range(155):
                t15 = py7/155
                base_a = 200 if is_sel2 else 150
                r7 = int((col4[0]*0.15) + (hovered*8))
                g7 = int((col4[1]*0.15) + (hovered*8))
                b7 = int((col4[2]*0.15) + (hovered*8))
                pygame.draw.line(card_s,(r7,g7,b7,int(base_a-t15*50)),(0,py7),(200,py7))
            pygame.draw.rect(card_s, col4, (0,0,200,155), 2 if not is_sel2 else 3, border_radius=6)
            if is_sel2:
                pygame.draw.rect(card_s, tuple(min(255,c+50) for c in col4), (0,0,200,3), border_radius=6)
            screen.blit(card_s,(bx9,by9))

            # Selected glow
            if is_sel2:
                gs11 = pygame.Surface((220,175),pygame.SRCALPHA)
                gl_a2 = int(30+abs(math.sin(tick*0.06))*22)
                pygame.draw.rect(gs11,(*col4,gl_a2),(0,0,220,175),border_radius=8)
                screen.blit(gs11,(bx9-10,by9-10))

            # Label
            lf6 = pygame.font.SysFont("consolas",22,bold=True)
            lt6 = lf6.render(cfg3["label"],True,col4 if not is_sel2 else WHITE)
            screen.blit(lt6,(bx9+100-lt6.get_width()//2, by9+14))

            # Divider
            pygame.draw.line(screen, tuple(max(0,c-30) for c in col4),
                             (bx9+12,by9+42),(bx9+188,by9+42),1)

            # Stats
            stat_lines = [
                f"Feind-HP   ×{cfg3['enemy_hp_mult']:.1f}",
                f"Feind-Speed ×{cfg3['enemy_speed_mult']:.1f}",
                f"Score-Mult  ×{cfg3['score_mult']:.1f}",
            ]
            for si3,(sl2) in enumerate(stat_lines):
                st3 = f3.render(sl2,True,tuple(min(255,c+40) for c in col4))
                screen.blit(st3,(bx9+12,by9+52+si3*18))

            # Description
            for di,dl in enumerate(cfg3["desc"].split("—")):
                dt2 = f3.render(dl.strip(),True,(145,145,155) if not is_sel2 else (200,200,210))
                screen.blit(dt2,(bx9+100-dt2.get_width()//2,by9+118+di*14))

            # Check mark
            if is_sel2:
                cf2 = pygame.font.SysFont("consolas",18,bold=True)
                ct3 = cf2.render("✓ AKTIV",True,col4)
                screen.blit(ct3,(bx9+100-ct3.get_width()//2,by9+138))

        back.update((mx3,my3)); back.draw(screen)
        pygame.display.flip(); clock.tick(FPS)


def show_achievements():
    achieved2 = load_achievements()
    back = MenuButton("◀  ZURÜCK", WIDTH//2, HEIGHT-58, w=210, h=46)
    tick = 0
    while True:
        tick += 1; mx4,my4 = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.clicked((mx4,my4)): return
        draw_menu_bg(screen,tick)
        f4 = pygame.font.SysFont("consolas",32,bold=True)
        f5 = pygame.font.SysFont("consolas",13)
        t16 = f4.render("ACHIEVEMENTS",True,(75,200,60))
        screen.blit(t16,(WIDTH//2-t16.get_width()//2,42))
        pygame.draw.line(screen,(45,105,40),(WIDTH//2-260,85),(WIDTH//2+260,85),1)
        keys2 = list(ACHIEVEMENTS_DEF.keys())
        for idx2,key4 in enumerate(keys2):
            col_idx2=idx2%4; row_idx2=idx2//4
            x2=WIDTH//2-595+col_idx2*305; y2=100+row_idx2*102
            cfg4=ACHIEVEMENTS_DEF[key4]
            unlocked2=key4 in achieved2
            panel2=pygame.Surface((290,88),pygame.SRCALPHA)
            for py8 in range(88):
                t17=py8/88
                if unlocked2:
                    pygame.draw.line(panel2,(12,32,12,int(200-t17*55)),(0,py8),(290,py8))
                else:
                    pygame.draw.line(panel2,(8,8,14,int(180-t17*50)),(0,py8),(290,py8))
            brd3=(65,135,55) if unlocked2 else (28,40,28)
            pygame.draw.rect(panel2,brd3,(0,0,290,88),1,border_radius=5)
            if unlocked2:
                pygame.draw.rect(panel2,brd3,(0,0,290,3),border_radius=5)
                # Check badge
                cb=pygame.Surface((18,18),pygame.SRCALPHA)
                pygame.draw.circle(cb,(55,140,45,200),(9,9),9)
                pygame.draw.circle(cb,(75,185,60,240),(9,9),7)
                cf3=pygame.font.SysFont("consolas",11,bold=True)
                ct4=cf3.render("✓",True,WHITE)
                cb.blit(ct4,(9-ct4.get_width()//2,9-ct4.get_height()//2))
                panel2.blit(cb,(268,4))
            icon_f2=pygame.font.SysFont("segoe ui emoji",22)
            icon_t2=icon_f2.render(cfg4["icon"],True,WHITE if unlocked2 else (45,50,45))
            panel2.blit(icon_t2,(10,10))
            nf2=pygame.font.SysFont("consolas",13,bold=True)
            nt2=nf2.render(cfg4["name"],True,(180,235,165) if unlocked2 else (40,50,40))
            panel2.blit(nt2,(44,12))
            dt3=f5.render(cfg4["desc"],True,(110,150,105) if unlocked2 else (30,38,30))
            panel2.blit(dt3,(12,48))
            if not unlocked2:
                lk2=f5.render("— GESPERRT —",True,(28,38,28)); panel2.blit(lk2,(12,66))
            screen.blit(panel2,(x2,y2))
        count2=len(achieved2); total2=len(ACHIEVEMENTS_DEF)
        pf2=pygame.font.SysFont("consolas",13)
        prog2=pf2.render(f"Freigeschaltet: {count2}/{total2}   ({int(count2/total2*100)}%)",True,(45,95,40))
        screen.blit(prog2,(WIDTH//2-prog2.get_width()//2,HEIGHT-80))
        # Progress bar
        pb_w=320; pb_x=WIDTH//2-pb_w//2; pb_y=HEIGHT-62
        pygame.draw.rect(screen,(12,22,12),(pb_x,pb_y,pb_w,8),border_radius=4)
        pygame.draw.rect(screen,(55,145,45),(pb_x,pb_y,int(pb_w*count2/max(total2,1)),8),border_radius=4)
        pygame.draw.rect(screen,(35,80,32),(pb_x,pb_y,pb_w,8),1,border_radius=4)
        back.update((mx4,my4)); back.draw(screen)
        pygame.display.flip(); clock.tick(FPS)


def show_skin_select():
    global current_skin
    achieved3=load_achievements()
    skin_keys2=list(SKINS.keys())
    idx2=skin_keys2.index(current_skin)
    back=MenuButton("◀  ZURÜCK",WIDTH//2,HEIGHT-58,w=210,h=46)
    tick=0
    while True:
        tick+=1; mx5,my5=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if back.clicked((mx5,my5)): return
                for i11,key5 in enumerate(skin_keys2):
                    bx10=WIDTH//2-340+i11*230; by10=HEIGHT//2-80
                    if pygame.Rect(bx10,by10,210,180).collidepoint(mx5,my5):
                        sk3=SKINS[key5]
                        if sk3["unlock"] is None or sk3["unlock"] in achieved3:
                            current_skin=key5; idx2=i11
        draw_menu_bg(screen,tick)
        f6=pygame.font.SysFont("consolas",32,bold=True)
        f7=pygame.font.SysFont("consolas",13)
        t18=f6.render("CHARAKTER-SKIN",True,(75,200,60))
        screen.blit(t18,(WIDTH//2-t18.get_width()//2,42))
        pygame.draw.line(screen,(45,105,40),(WIDTH//2-230,85),(WIDTH//2+230,85),1)
        sub4=pygame.font.SysFont("consolas",12).render("Klicke auf einen Skin um ihn auszuwählen",True,(32,68,30))
        screen.blit(sub4,(WIDTH//2-sub4.get_width()//2,94))

        for i12,key6 in enumerate(skin_keys2):
            sk4=SKINS[key6]
            bx11=WIDTH//2-340+i12*230; by11=HEIGHT//2-80
            is_sel3=(key6==current_skin)
            hovered2=pygame.Rect(bx11,by11,210,180).collidepoint(mx5,my5)
            unlocked3=sk4["unlock"] is None or sk4["unlock"] in achieved3
            col5=sk4["body"] if unlocked3 else (20,24,20)

            # Card
            card_s2=pygame.Surface((210,180),pygame.SRCALPHA)
            for py9 in range(180):
                t19=py9/180
                r8=int(col5[0]*0.18+(hovered2*6))
                g8=int(col5[1]*0.18+(hovered2*6))
                b8=int(col5[2]*0.18+(hovered2*6))
                pygame.draw.line(card_s2,(r8,g8,b8,int(200-t19*60)),(0,py9),(210,py9))
            brd4=(85,175,68) if is_sel3 else ((55,88,50) if (unlocked3 and hovered2) else ((40,65,38) if unlocked3 else (20,28,20)))
            pygame.draw.rect(card_s2,brd4,(0,0,210,180),2,border_radius=6)
            if is_sel3:
                pygame.draw.rect(card_s2,brd4,(0,0,210,3),border_radius=6)
            screen.blit(card_s2,(bx11,by11))

            # Glow on selected
            if is_sel3:
                gs12=pygame.Surface((230,200),pygame.SRCALPHA)
                gl_a3=int(25+abs(math.sin(tick*0.06))*20)
                pygame.draw.rect(gs12,(*col5,gl_a3),(0,0,230,200),border_radius=8)
                screen.blit(gs12,(bx11-10,by11-10))

            # Soldier preview — detailed
            pcx2=bx11+105; pcy2=by11+85
            bc4=sk4["body"]; hc4=sk4["head"]; helm4=sk4["helmet"]; vest4=sk4["vest"]
            boot4=sk4.get("boot",(22,18,12))
            bc4_hi=tuple(min(255,c+22) for c in bc4)
            bc4_dk=tuple(max(0,c-18) for c in bc4)
            # Boots
            pygame.draw.rect(screen,boot4,(pcx2-9,pcy2+44,10,9),border_radius=2)
            pygame.draw.rect(screen,boot4,(pcx2+1,pcy2+44,10,9),border_radius=2)
            # Legs
            pygame.draw.rect(screen,bc4,(pcx2-9,pcy2+30,9,15),border_radius=2)
            pygame.draw.rect(screen,bc4,(pcx2+1,pcy2+30,9,15),border_radius=2)
            # Belt
            pygame.draw.rect(screen,(28,22,12),(pcx2-10,pcy2+29,20,4))
            # Vest
            pygame.draw.rect(screen,vest4,(pcx2-11,pcy2+13,22,18),border_radius=3)
            pygame.draw.rect(screen,bc4_hi,(pcx2-11,pcy2+13,22,5),border_radius=3)
            pygame.draw.rect(screen,bc4_dk,(pcx2-8,pcy2+15,16,14),border_radius=2)
            # Pouches
            pygame.draw.rect(screen,bc4_dk,(pcx2-14,pcy2+16,5,8),border_radius=1)
            pygame.draw.rect(screen,bc4_dk,(pcx2+9,pcy2+16,5,8),border_radius=1)
            # Arms
            pygame.draw.line(screen,vest4,(pcx2-10,pcy2+15),(pcx2-18,pcy2+27),5)
            pygame.draw.line(screen,vest4,(pcx2+10,pcy2+15),(pcx2+18,pcy2+25),5)
            pygame.draw.circle(screen,boot4,(pcx2-18,pcy2+27),4)
            pygame.draw.circle(screen,boot4,(pcx2+18,pcy2+25),4)
            # Rifle
            pygame.draw.rect(screen,(38,38,38),(pcx2+14,pcy2+19,22,6))
            pygame.draw.line(screen,(50,50,50),(pcx2+30,pcy2+20),(pcx2+40,pcy2+20),2)
            # Neck
            pygame.draw.rect(screen,hc4,(pcx2-3,pcy2+9,6,6))
            # Head
            pygame.draw.circle(screen,hc4,(pcx2,pcy2+5),10)
            pygame.draw.circle(screen,tuple(max(0,c-22) for c in hc4),(pcx2+3,pcy2+6),5)
            eye_x3=pcx2+4
            pygame.draw.circle(screen,(228,222,212),(eye_x3,pcy2+3),2)
            pygame.draw.circle(screen,(20,15,10),(eye_x3,pcy2+3),1)
            # Helmet
            helm_hi3=tuple(min(255,c+22) for c in helm4)
            helm_dk3=tuple(max(0,c-18) for c in helm4)
            pygame.draw.arc(screen,helm4,pygame.Rect(pcx2-12,pcy2-6,24,18),0,math.pi,0)
            pygame.draw.rect(screen,helm4,(pcx2-12,pcy2+4,24,7))
            pygame.draw.arc(screen,helm_hi3,pygame.Rect(pcx2-9,pcy2-4,11,10),0.4,math.pi-0.4,2)
            pygame.draw.rect(screen,helm_dk3,(pcx2-13,pcy2+9,26,3),border_radius=1)
            camo_r2=random.Random(i12*77)
            for _ in range(4):
                csx4=pcx2+camo_r2.randint(-9,9); csy4=pcy2+camo_r2.randint(-4,8)
                pygame.draw.circle(screen,helm_dk3,(csx4,csy4),camo_r2.randint(1,2))
            # Rank chevrons
            for chev_i2 in range(min(3, i12+1)):
                chev_y2=pcy2+17+chev_i2*4
                ch_col=(80,180,65) if unlocked3 else (35,45,35)
                pygame.draw.line(screen,ch_col,(pcx2-13,chev_y2+2),(pcx2-9,chev_y2),1)
                pygame.draw.line(screen,ch_col,(pcx2-9,chev_y2),(pcx2-5,chev_y2+2),1)

            # Labels
            lf7=pygame.font.SysFont("consolas",13,bold=True)
            lt7=lf7.render(sk4["label"],True,(175,240,155) if unlocked3 else (30,38,30))
            screen.blit(lt7,(bx11+105-lt7.get_width()//2,by11+142))
            if not unlocked3:
                lk3=f7.render("GESPERRT",True,(28,38,28))
                screen.blit(lk3,(bx11+105-lk3.get_width()//2,by11+158))
            elif is_sel3:
                ct5=lf7.render("✓ AKTIV",True,(75,200,60))
                screen.blit(ct5,(bx11+105-ct5.get_width()//2,by11+158))
            # Unlock hint
            if sk4.get("unlock") and not unlocked3:
                uf=pygame.font.SysFont("consolas",10)
                ut=uf.render(f"Freisch: {sk4['unlock']}",True,(28,38,28))
                screen.blit(ut,(bx11+105-ut.get_width()//2,by11+168))

        # Description
        sk5=SKINS[current_skin]
        dt4=f7.render(sk5["desc"],True,(55,110,48))
        screen.blit(dt4,(WIDTH//2-dt4.get_width()//2,HEIGHT-84))
        back.update((mx5,my5)); back.draw(screen)
        pygame.display.flip(); clock.tick(FPS)


def show_highscores():
    scores2=load_highscores()
    back=MenuButton("◀  ZURÜCK",WIDTH//2,HEIGHT-58,w=210,h=46)
    tick=0
    while True:
        tick+=1; mx6,my6=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if back.clicked((mx6,my6)): return
        draw_menu_bg(screen,tick)
        f8=pygame.font.SysFont("consolas",34,bold=True)
        f9=pygame.font.SysFont("consolas",17)
        f10=pygame.font.SysFont("consolas",12)
        t20=f8.render("HIGHSCORES",True,(75,200,60))
        screen.blit(t20,(WIDTH//2-t20.get_width()//2,42))
        pygame.draw.line(screen,(45,105,40),(WIDTH//2-210,84),(WIDTH//2+210,84),1)

        # Table header
        hdr2=f10.render("  #    NAME             SCORE    ZONE   SCHWIERIGKEIT",True,(45,95,42))
        screen.blit(hdr2,(WIDTH//2-hdr2.get_width()//2,100))
        pygame.draw.line(screen,(28,60,26),(WIDTH//2-290,116),(WIDTH//2+290,116),1)

        medal_cols=[(255,215,50),(190,195,210),(180,120,40)]
        if not scores2:
            n2=f9.render("Noch keine Einträge!",True,(35,65,32))
            screen.blit(n2,(WIDTH//2-n2.get_width()//2,160))
        else:
            for i13,s2 in enumerate(scores2[:10]):
                row_y2=126+i13*32
                # Row background
                row_bg=pygame.Surface((590,28),pygame.SRCALPHA)
                row_a=120 if i13%2==0 else 80
                row_bg.fill((10,22,10,row_a))
                if i13<3:
                    row_bg.fill((*medal_cols[i13],25))
                pygame.draw.rect(row_bg,(28,55,25),(0,0,590,28),1,border_radius=3)
                screen.blit(row_bg,(WIDTH//2-295,row_y2))

                # Rank
                if i13<3:
                    medal_f=pygame.font.SysFont("consolas",16,bold=True)
                    medal_t=medal_f.render(f"#{i13+1}",True,medal_cols[i13])
                    screen.blit(medal_t,(WIDTH//2-288,row_y2+5))
                else:
                    rk_t=f10.render(f"#{i13+1}",True,(45,85,40))
                    screen.blit(rk_t,(WIDTH//2-288,row_y2+8))

                col6=medal_cols[i13] if i13<3 else (120,175,110)
                diff_label2=DIFFICULTY_SETTINGS.get(s2.get("diff","normal"),{}).get("label","Normal")
                row_t=f9.render(f"   {s2['name']:<13}  {s2['score']:>8}    Z{s2['zone']}    {diff_label2}",True,col6)
                screen.blit(row_t,(WIDTH//2-285,row_y2+5))
        back.update((mx6,my6)); back.draw(screen)
        pygame.display.flip(); clock.tick(FPS)


def show_controls():
    back=MenuButton("◀  ZURÜCK",WIDTH//2,HEIGHT-58,w=210,h=46)
    ctrls2=[("A / D","Bewegen links/rechts"),("LEERTASTE / W","Springen"),
           ("LINKSKLICK","Schiessen"),("G","Granate werfen"),
           ("T","Geschütz aufstellen (max 2)"),("ESC","PAUSE-MENÜ"),
           ("Q (halten)","Waffen-Rad (Slow-Motion)"),
           ("1","Pistole (15 DMG)"),("2","Sturmgewehr (Auto, 8 DMG)"),
           ("3","Scharfschütze (55 DMG, lang)"),("4","Schrotflinte (8×18 DMG)"),
           ("5","Raketenwerfer → Tanks"),("6","Stinger AA → Luft"),
           ("7","Messer (Nahkampf)"),("8","Flammenwerfer (Auto)"),
           ("9","EMP-Kanone (betäubt Mech.)"),
           ("KILLS","→ Waffe levelt auf (LV3 = +75% DMG)"),
           ("POWERUPS","Medkit / Schild / Speed / 2×DMG")]
    tick=0
    kf2=pygame.font.SysFont("consolas",14,bold=True)
    vf2=pygame.font.SysFont("consolas",13)
    tf4=pygame.font.SysFont("consolas",30,bold=True)
    f11=pygame.font.SysFont("consolas",12)
    while True:
        tick+=1; mx7,my7=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if back.clicked((mx7,my7)): return
        draw_menu_bg(screen,tick)
        t21=tf4.render("STEUERUNG",True,(75,200,60))
        screen.blit(t21,(WIDTH//2-t21.get_width()//2,30))
        pygame.draw.line(screen,(45,105,40),(WIDTH//2-210,68),(WIDTH//2+210,68),1)

        # Two columns
        mid=len(ctrls2)//2
        for col7 in range(2):
            col_x2 = WIDTH//2-590 if col7==0 else WIDTH//2+18
            col_ctrls = ctrls2[:mid] if col7==0 else ctrls2[mid:]
            # Column header
            ch2=f11.render("TASTE" if col7==0 else "TASTE",True,(35,75,32))
            screen.blit(ch2,(col_x2,74))
            pygame.draw.line(screen,(25,55,22),(col_x2,88),(col_x2+555,88),1)
            for i14,(k2,v2) in enumerate(col_ctrls):
                row_y3=96+i14*30
                # Row bg
                row_bg2=pygame.Surface((555,26),pygame.SRCALPHA)
                row_bg2.fill((8,18,8,100 if i14%2==0 else 65))
                pygame.draw.rect(row_bg2,(22,45,20),(0,0,555,26),1,border_radius=2)
                screen.blit(row_bg2,(col_x2,row_y3))
                # Key badge
                kb=pygame.Surface((kf2.size(k2)[0]+14,22),pygame.SRCALPHA)
                kb.fill((18,42,16,200))
                pygame.draw.rect(kb,(45,100,40),(0,0,kb.get_width(),22),1,border_radius=3)
                kb.blit(kf2.render(k2,True,(95,195,75)),(7,2))
                screen.blit(kb,(col_x2+4,row_y3+2))
                screen.blit(vf2.render(v2,True,(115,160,108)),(col_x2+165,row_y3+5))
        back.update((mx7,my7)); back.draw(screen)
        pygame.display.flip(); clock.tick(FPS)

# ═══════════════════════════════════════════════════
#  LEVELMAP
# ═══════════════════════════════════════════════════
ZONE_MAP_INFO = {
    1: {"name": "STADT",      "icon": "🏙", "color": (80,120,180)},
    2: {"name": "WALD",       "icon": "🌲", "color": (50,120,50)},
    3: {"name": "WÜSTE",      "icon": "🏜", "color": (180,130,40)},
    4: {"name": "BASIS",      "icon": "🏭", "color": (80,80,120)},
    5: {"name": "ARKTIS",     "icon": "❄",  "color": (140,180,220)},
    6: {"name": "OMEGA",      "icon": "💀", "color": (120,30,150)},
    7: {"name": "VULKAN",     "icon": "🌋", "color": (255,80,20)},
    8: {"name": "ORBIT",      "icon": "🚀", "color": (40,180,255)},
}

PERKS_STORE = {
    "hp_up_1":      {"name":"Vitalität I",      "desc":"+20 Max-HP dauerhaft",        "cost":1,"col":(50,200,80),  "cat":"survival"},
    "hp_up_2":      {"name":"Vitalität II",     "desc":"+40 Max-HP dauerhaft",        "cost":2,"col":(50,200,80),  "cat":"survival","req":"hp_up_1"},
    "hp_up_3":      {"name":"Vitalität III",    "desc":"+60 Max-HP dauerhaft",        "cost":4,"col":(50,200,80),  "cat":"survival","req":"hp_up_2"},
    "dmg_up_1":     {"name":"Waffenmeister I",  "desc":"+20% Schaden dauerhaft",      "cost":1,"col":(220,80,40),  "cat":"combat"},
    "dmg_up_2":     {"name":"Waffenmeister II", "desc":"+35% Schaden dauerhaft",      "cost":2,"col":(220,80,40),  "cat":"combat","req":"dmg_up_1"},
    "speed_up":     {"name":"Schnellläufer",    "desc":"+15% Bewegung dauerhaft",     "cost":1,"col":(80,160,255), "cat":"mobility"},
    "extra_life":   {"name":"Extra Leben",      "desc":"+1 Leben pro Spiel",          "cost":3,"col":(255,215,50), "cat":"survival"},
    "grenade_up":   {"name":"Granatenexperte",  "desc":"Start mit +3 Granaten",       "cost":1,"col":(80,200,80),  "cat":"combat"},
    "ammo_up":      {"name":"Munitionsgurt",    "desc":"Raketen +3 Magazin",          "cost":2,"col":(255,160,30), "cat":"combat"},
    "regen_perk":   {"name":"Kampfregen",       "desc":"HP regen bei niedrigem HP",   "cost":2,"col":(50,200,80),  "cat":"survival"},
    "crit_up":      {"name":"Präzisionsschütze","desc":"20% Chance auf Krit x2",      "cost":3,"col":(255,80,80),  "cat":"combat"},
    "shield_start": {"name":"Notfallschild",    "desc":"Start jede Zone mit Schild",  "cost":4,"col":(80,140,255), "cat":"survival"},
}

def show_skill_tree():
    f_title  = pygame.font.SysFont("consolas", 32, bold=True)
    f_branch = pygame.font.SysFont("consolas", 14, bold=True)
    f_perk   = pygame.font.SysFont("consolas", 11, bold=True)
    f_desc   = pygame.font.SysFont("consolas", 10)
    f_pts    = pygame.font.SysFont("consolas", 20, bold=True)
    f_hint   = pygame.font.SysFont("consolas", 12)

    branches   = list(SKILL_TREE.keys())
    CARD_W     = 178
    CARD_H     = 58
    BRANCH_X   = [int(WIDTH * 0.13), int(WIDTH * 0.38),
                  int(WIDTH * 0.63), int(WIDTH * 0.88)]
    PERK_Y_START = 148
    PERK_SPACING = 66
    tick       = 0
    done       = False
    notif_msg  = ""
    notif_timer= 0

    def perk_rect(bi, pi):
        return pygame.Rect(BRANCH_X[bi] - CARD_W // 2,
                           PERK_Y_START + pi * PERK_SPACING,
                           CARD_W, CARD_H)

    while not done:
        tick += 1
        if notif_timer > 0: notif_timer -= 1
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); import sys; sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_perk = False
                for bi, bkey in enumerate(branches):
                    for pi, perk in enumerate(SKILL_TREE[bkey]["perks"]):
                        if perk_rect(bi, pi).collidepoint(mx, my):
                            clicked_perk = True
                            ok, reason = SKILLS.can_unlock(perk["id"])
                            if ok:
                                SKILLS.unlock(perk["id"])
                                SFX.play(SFX.level_up)
                                notif_msg = f"✓ {perk['name']} freigeschaltet!"
                                notif_timer = 150
                            else:
                                notif_msg = f"✗ {reason}"
                                notif_timer = 100
                if not clicked_perk:
                    close_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 62, 200, 46)
                    if close_btn.collidepoint(mx, my):
                        done = True

        # ── Background ──
        draw_menu_bg(screen, tick)

        # ── Title ──
        t = f_title.render("◈  SKILL-BAUM  ◈", True, YELLOW)
        screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 22))
        pygame.draw.line(screen, (100, 80, 20),
                         (WIDTH // 2 - 260, 62), (WIDTH // 2 + 260, 62), 1)

        pts_col = (100, 220, 80) if SKILLS.points > 0 else (130, 130, 140)
        pts_t = f_pts.render(f"Verfügbare Punkte:  {SKILLS.points}", True, pts_col)
        screen.blit(pts_t, (WIDTH // 2 - pts_t.get_width() // 2, 70))

        total_unlocked = len(SKILLS.unlocked)
        total_perks = sum(len(b["perks"]) for b in SKILL_TREE.values())
        prog_t = f_hint.render(f"Freigeschaltet: {total_unlocked} / {total_perks}", True, (55, 90, 50))
        screen.blit(prog_t, (WIDTH // 2 - prog_t.get_width() // 2, 96))

        # ── Branch columns ──
        for bi, bkey in enumerate(branches):
            bdata = SKILL_TREE[bkey]
            col   = bdata["color"]
            bx    = BRANCH_X[bi]
            num_perks = len(bdata["perks"])

            # Column header
            hdr = pygame.Surface((CARD_W, 38), pygame.SRCALPHA)
            hdr.fill((*col, 50))
            pygame.draw.rect(hdr, col, (0, 0, CARD_W, 38), 2, border_radius=4)
            screen.blit(hdr, (bx - CARD_W // 2, 108))
            ht = f_branch.render(f"{bdata['icon']}  {bdata['label']}", True, col)
            screen.blit(ht, (bx - ht.get_width() // 2, 118))

            # Vertical connector line
            line_top = 146
            line_bot = PERK_Y_START + (num_perks - 1) * PERK_SPACING + CARD_H // 2
            pygame.draw.line(screen, (*col, 55), (bx, line_top), (bx, line_bot), 1)

            for pi, perk in enumerate(bdata["perks"]):
                r = perk_rect(bi, pi)
                unlocked  = SKILLS.has(perk["id"])
                can_buy, reason = SKILLS.can_unlock(perk["id"])
                hov = r.collidepoint(mx, my)

                # Connector dot
                dot_col = col if unlocked else ((180, 180, 200) if can_buy else (40, 45, 55))
                pygame.draw.circle(screen, dot_col, (bx, r.centery), 5)
                if unlocked:
                    pygame.draw.circle(screen, col, (bx, r.centery), 3)

                # Requirement arrow
                req = perk.get("requires")
                if req:
                    # Find the previous perk position
                    for pi2, p2 in enumerate(bdata["perks"]):
                        if p2["id"] == req:
                            r2 = perk_rect(bi, pi2)
                            arc_col = col if SKILLS.has(req) else (45, 50, 65)
                            pygame.draw.line(screen, arc_col,
                                             (bx, r2.centery + CARD_H // 2 + 2),
                                             (bx, r.centery - CARD_H // 2 - 2), 1)

                # Card background
                if unlocked:      bg = (*col, 65)
                elif can_buy:     bg = (12, 20, 12, 180) if not hov else (*col, 40)
                else:             bg = (8, 8, 14, 155)

                card = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
                card.fill(bg)
                brd = col if (unlocked or can_buy) else (38, 38, 52)
                brd_w = 2 if (unlocked or hov) else 1
                pygame.draw.rect(card, brd, (0, 0, CARD_W, CARD_H), brd_w, border_radius=4)
                if unlocked:
                    pygame.draw.rect(card, col, (0, 0, CARD_W, 3), border_radius=4)
                    ck = f_perk.render("✓", True, col)
                    card.blit(ck, (CARD_W - 14, 3))

                nc = col if unlocked else (WHITE if can_buy else (55, 55, 70))
                card.blit(f_perk.render(perk["name"], True, nc), (7, 5))
                card.blit(f_desc.render(perk["desc"], True, (155, 155, 175)), (7, 20))

                if unlocked:
                    ct = f_desc.render("AKTIV", True, col)
                elif can_buy:
                    ct = f_desc.render(f"Kosten: {perk['cost']} Pkt.", True, YELLOW)
                else:
                    ct = f_desc.render(reason[:24], True, (85, 55, 55))
                card.blit(ct, (7, 38))

                # Hover glow
                if hov and can_buy and not unlocked:
                    gs = pygame.Surface((CARD_W + 12, CARD_H + 12), pygame.SRCALPHA)
                    pygame.draw.rect(gs, (*col, 35), (0, 0, CARD_W + 12, CARD_H + 12),
                                     border_radius=6)
                    screen.blit(gs, (r.x - 6, r.y - 6))

                screen.blit(card, (r.x, r.y))

        # ── Notification ──
        if notif_timer > 0:
            alpha_n = min(255, notif_timer * 4)
            n_col = (100, 220, 80) if notif_msg.startswith("✓") else (220, 80, 80)
            nf = pygame.font.SysFont("consolas", 16, bold=True)
            nt = nf.render(notif_msg, True, n_col)
            ns = pygame.Surface((nt.get_width() + 24, nt.get_height() + 10), pygame.SRCALPHA)
            ns.fill((0, 0, 0, 140))
            pygame.draw.rect(ns, n_col, (0, 0, ns.get_width(), ns.get_height()), 1, border_radius=3)
            ns.blit(nt, (12, 5))
            ns.set_alpha(alpha_n)
            screen.blit(ns, (WIDTH // 2 - ns.get_width() // 2, HEIGHT // 2 - 55))

        # ── Close button ──
        cb_r = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 62, 200, 46)
        cb_hov = cb_r.collidepoint(mx, my)
        pygame.draw.rect(screen, (32, 62, 26) if cb_hov else (16, 38, 12), cb_r, border_radius=5)
        pygame.draw.rect(screen, (65, 155, 48) if cb_hov else (40, 90, 32), cb_r, 2, border_radius=5)
        ct2 = f_hint.render("◈  WEITER  →  (ESC)", True, (175, 235, 155))
        screen.blit(ct2, (cb_r.centerx - ct2.get_width() // 2,
                          cb_r.centery - ct2.get_height() // 2))

        hint2 = f_hint.render("Klick: Fähigkeit kaufen  |  ESC: Schliessen", True, (40, 75, 38))
        screen.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, HEIGHT - 18))

        pygame.display.flip()
        clock.tick(FPS)

def show_level_map(completed_zone, next_zone):
    """Zeigt Übersichtskarte zwischen den Zonen."""
    achieved = load_achievements()
    f_title  = pygame.font.SysFont("consolas", 36, bold=True)
    f_sub    = pygame.font.SysFont("consolas", 16, bold=True)
    f_tiny   = pygame.font.SysFont("consolas", 13)
    f_hint   = pygame.font.SysFont("consolas", 14)

    # Animationsvariablen
    tick     = 0
    anim_in  = 0.0   # 0→1 Einblende
    line_progress = 0.0   # Fortschritt der Verbindungslinie

    # Positionen der Zonen auf der Karte
    node_positions = {}
    total = NUM_ZONES
    map_w = WIDTH - 200
    map_x = 100
    map_y = HEIGHT // 2

    for i in range(1, total + 1):
        t = (i - 1) / (total - 1)
        # Leichte Wellenform
        wave = math.sin(t * math.pi) * -80
        x = int(map_x + t * map_w)
        y = int(map_y + wave)
        node_positions[i] = (x, y)

    done = False
    while not done:
        tick += 1
        dt = clock.tick(FPS) / 1000
        anim_in = min(1.0, anim_in + dt * 1.8)
        if anim_in >= 1.0:
            line_progress = min(1.0, line_progress + dt * 0.9)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                done = True

        # ── Hintergrund ───────────────────────────────────────────────────────
        screen.fill((5, 8, 18))
        # Sterne
        rng_s = random.Random(42)
        for i in range(80):
            sx = rng_s.randint(0, WIDTH)
            sy = rng_s.randint(0, HEIGHT)
            tw = abs(math.sin(tick * 0.02 + i * 0.9))
            star_s = pygame.Surface((3, 3), pygame.SRCALPHA)
            pygame.draw.circle(star_s, (200, 220, 255, int(tw * 180)), (1, 1), 1)
            screen.blit(star_s, (sx, sy))

        # ── Titel ─────────────────────────────────────────────────────────────
        title_alpha = int(min(255, anim_in * 400))
        t_surf = f_title.render("KAMPAGNEN-KARTE", True, YELLOW)
        t_surf.set_alpha(title_alpha)
        screen.blit(t_surf, (WIDTH // 2 - t_surf.get_width() // 2, 45))
        pygame.draw.line(screen, (100, 80, 30),
                         (WIDTH//2 - 260, 88), (WIDTH//2 + 260, 88), 1)

        # ── Verbindungslinien ─────────────────────────────────────────────────
        for i in range(1, total):
            x1, y1 = node_positions[i]
            x2, y2 = node_positions[i + 1]
            # Bereits abgeschlossene Strecken
            if i < completed_zone:
                pygame.draw.line(screen, (80, 200, 80), (x1, y1), (x2, y2), 3)
            # Aktuelle Strecke (animiert)
            elif i == completed_zone and line_progress < 1.0:
                ex = int(x1 + (x2 - x1) * line_progress)
                ey = int(y1 + (y2 - y1) * line_progress)
                pygame.draw.line(screen, (80, 200, 80), (x1, y1), (x1, y1), 3)
                if line_progress > 0:
                    pygame.draw.line(screen, (80, 200, 80), (x1, y1), (ex, ey), 3)
                    # Leuchtspitze
                    glow_s = pygame.Surface((20, 20), pygame.SRCALPHA)
                    pygame.draw.circle(glow_s, (100, 255, 100, 180), (10, 10), 8)
                    screen.blit(glow_s, (ex - 10, ey - 10))
                pygame.draw.line(screen, (40, 50, 40), (ex, ey), (x2, y2), 2)
            elif i == completed_zone and line_progress >= 1.0:
                pygame.draw.line(screen, (80, 200, 80), (x1, y1), (x2, y2), 3)
            else:
                pygame.draw.line(screen, (35, 40, 55), (x1, y1), (x2, y2), 2)

        # ── Zonen-Knoten ──────────────────────────────────────────────────────
        for zn in range(1, total + 1):
            x, y     = node_positions[zn]
            info     = ZONE_MAP_INFO[zn]
            col      = info["color"]
            cleared  = f"zone_{zn}" in achieved
            is_done  = (zn <= completed_zone)
            is_next  = (zn == next_zone)
            is_curr  = (zn == completed_zone)

            # Node-Delay-Animation
            node_delay = (zn - 1) / total
            node_alpha = max(0.0, min(1.0, (anim_in - node_delay * 0.5) * 3))
            if node_alpha <= 0:
                continue

            node_r = 30
            if is_next:
                # Pulsieren für nächste Zone
                pulse = abs(math.sin(tick * 0.06)) * 8
                node_r = int(30 + pulse)
                # Glow
                gs_n = pygame.Surface((node_r * 4, node_r * 4), pygame.SRCALPHA)
                pygame.draw.circle(gs_n, (*col, int(50 * node_alpha)),
                                   (node_r * 2, node_r * 2), node_r * 2)
                screen.blit(gs_n, (x - node_r * 2, y - node_r * 2))

            # Hintergrundkreis
            pygame.draw.circle(screen,
                               col if is_done else (20, 25, 40),
                               (x, y), node_r)
            # Rand
            border_col = (255, 220, 50) if is_next else \
                         (80, 220, 80)  if is_done else \
                         (60, 65, 90)
            border_w = 3 if is_next else 2
            pygame.draw.circle(screen, border_col, (x, y), node_r, border_w)

            # Zonen-Nummer
            num_f = pygame.font.SysFont("consolas", 18, bold=True)
            num_t = num_f.render(str(zn), True,
                                 WHITE if is_done else (80, 85, 110))
            num_t.set_alpha(int(255 * node_alpha))
            screen.blit(num_t, (x - num_t.get_width() // 2,
                                y - num_t.get_height() // 2))

            # Häkchen bei abgeschlossenen
            if cleared and is_done:
                ck_f = pygame.font.SysFont("consolas", 12, bold=True)
                ck   = ck_f.render("✓", True, (100, 255, 100))
                screen.blit(ck, (x + node_r - 8, y - node_r - 2))

            # Name unter dem Knoten
            name_t = f_sub.render(info["name"], True,
                                  YELLOW if is_next else
                                  (80, 220, 80) if is_done else GRAY)
            name_t.set_alpha(int(255 * node_alpha))
            screen.blit(name_t, (x - name_t.get_width() // 2, y + node_r + 6))

            # "NÄCHSTES ZIEL" Label
            if is_next:
                lbl = f_tiny.render("▼ NÄCHSTES ZIEL", True, YELLOW)
                lbl_alpha = int(128 + abs(math.sin(tick * 0.05)) * 127)
                lbl.set_alpha(lbl_alpha)
                screen.blit(lbl, (x - lbl.get_width() // 2, y - node_r - 22))

            # "BEFREIT" Label für abgeschlossene Zone
            if is_curr:
                done_lbl = f_tiny.render("BEFREIT!", True, (80, 255, 120))
                screen.blit(done_lbl, (x - done_lbl.get_width() // 2,
                                       y + node_r + 22))

        # ── Score-Anzeige ─────────────────────────────────────────────────────
        score_f = pygame.font.SysFont("consolas", 20, bold=True)
        score_t = score_f.render(f"Zonen befreit: {completed_zone} / {NUM_ZONES}",
                                 True, GRAY)
        screen.blit(score_t, (WIDTH // 2 - score_t.get_width() // 2, HEIGHT - 85))

        # ── Weiter-Hinweis ────────────────────────────────────────────────────
        hint_alpha = int(128 + abs(math.sin(tick * 0.05)) * 127)
        hint = f_hint.render("[ SPACE / ENTER — Weiter ]", True, (150, 150, 100))
        hint_s = pygame.Surface((hint.get_width() + 20, hint.get_height() + 8),
                                pygame.SRCALPHA)
        hint_s.fill((0, 0, 0, 80))
        hint_s.blit(hint, (10, 4))
        hint_s.set_alpha(hint_alpha)
        screen.blit(hint_s, (WIDTH // 2 - hint_s.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()

def show_zone_intro(zone_num, zone_name):
    zone_accents={
        1:(80,200,80),2:(60,200,80),3:(200,160,40),4:(80,80,220),
        5:(120,200,255),6:(180,40,220),7:(255,80,20),8:(40,180,255),
    }
    accent=zone_accents.get(zone_num,(80,200,80))
    f1=pygame.font.SysFont("consolas",62,bold=True)
    f2=pygame.font.SysFont("consolas",26)
    f3=pygame.font.SysFont("consolas",14)
    f_diff=pygame.font.SysFont("consolas",18)

    # Zone flavor text
    flavor={
        1:"Stadtgebiet — Nacht",   2:"Waldgebiet — Dämmerung",
        3:"Wüstenfront — Tag",     4:"Militärbasis — Nacht",
        5:"Arktiszone — Blizzard", 6:"Festung Omega — Nacht",
        7:"Vulkanfront — Eruption",8:"Orbit-Station — Vakuum",
    }.get(zone_num,"")

    diff_cfg=get_diff()

    for frame in range(200):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN: frame=200; break
            if event.type==pygame.MOUSEBUTTONDOWN: frame=200; break

        # Alpha curve: fade in 0-40, hold 40-160, fade out 160-200
        if frame<40: alpha=int(frame/40*255)
        elif frame<160: alpha=255
        else: alpha=int((200-frame)/40*255)
        alpha=max(0,min(255,alpha))

        screen.fill((0,0,0))

        # Animated background lines
        for i in range(8):
            line_y=int((HEIGHT//2-160)+i*50+math.sin(frame*0.06+i)*8)
            la=int(12+abs(math.sin(frame*0.04+i*0.7))*20)
            ls=pygame.Surface((WIDTH,2),pygame.SRCALPHA)
            ls.fill((*accent,la))
            screen.blit(ls,(0,line_y))

        # Glitch blocks
        if frame%12<3:
            for _ in range(4):
                gx=random.randint(0,WIDTH-80); gy=random.randint(HEIGHT//4,HEIGHT*3//4)
                gw=random.randint(20,80); gh=random.randint(2,8)
                gs2=pygame.Surface((gw,gh),pygame.SRCALPHA)
                gs2.fill((*accent,random.randint(20,60)))
                screen.blit(gs2,(gx,gy))

        s=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)

        # Zone number — large
        z_str=f"ZONE {zone_num}"
        z_shadow=f1.render(z_str,True,tuple(max(0,c-60) for c in accent))
        z_text=f1.render(z_str,True,accent)
        scale3=1.0+abs(math.sin(frame*0.04))*0.025
        z_scaled=pygame.transform.scale(z_text,
            (int(z_text.get_width()*scale3),int(z_text.get_height()*scale3)))
        z_shadow_s=pygame.transform.scale(z_shadow,
            (int(z_shadow.get_width()*scale3),int(z_shadow.get_height()*scale3)))
        bx2=WIDTH//2-z_scaled.get_width()//2
        by2=HEIGHT//2-80

        # Glow behind text
        gls=pygame.Surface((z_scaled.get_width()+60,z_scaled.get_height()+20),pygame.SRCALPHA)
        gl_a=int(alpha*0.25)
        pygame.draw.ellipse(gls,(*accent,gl_a),(0,0,gls.get_width(),gls.get_height()))
        s.blit(gls,(bx2-30,by2-10))
        s.blit(z_shadow_s,(bx2+3,by2+3))
        s.blit(z_scaled,(bx2,by2))

        # Separator line
        line_w=int(z_scaled.get_width()*0.8)
        pygame.draw.line(s,(*accent,alpha),
                         (WIDTH//2-line_w//2,HEIGHT//2+8),
                         (WIDTH//2+line_w//2,HEIGHT//2+8),2)

        # Zone name
        n=zone_name.split(":")[-1].strip() if ":" in zone_name else zone_name
        nt=f2.render(n,True,WHITE)
        s.blit(nt,(WIDTH//2-nt.get_width()//2,HEIGHT//2+18))

        # Flavor
        ft=f3.render(flavor,True,tuple(min(200,c+30) for c in tuple(max(0,cc-30) for cc in accent)))
        s.blit(ft,(WIDTH//2-ft.get_width()//2,HEIGHT//2+52))

        # Difficulty
        dt2=f_diff.render(f"[{diff_cfg['label']}]",True,diff_cfg["color"])
        s.blit(dt2,(WIDTH//2-dt2.get_width()//2,HEIGHT//2+76))

        # Corner brackets
        bl=24
        for (bcx,bcy),(bsx2,bsy2) in [
            ((WIDTH//2-line_w//2-20,HEIGHT//2-60),(1,1)),
            ((WIDTH//2+line_w//2+20,HEIGHT//2-60),(-1,1)),
            ((WIDTH//2-line_w//2-20,HEIGHT//2+100),(1,-1)),
            ((WIDTH//2+line_w//2+20,HEIGHT//2+100),(-1,-1))]:
            pygame.draw.line(s,(*accent,alpha),(bcx,bcy),(bcx+bsx2*bl,bcy),2)
            pygame.draw.line(s,(*accent,alpha),(bcx,bcy),(bcx,bcy+bsy2*bl),2)

        s.set_alpha(alpha)
        screen.blit(s,(0,0))
        pygame.display.flip()
        clock.tick(FPS)

def show_name_input(score,zone):
    name="";cur=0
    confirm=MenuButton("EINTRAGEN  >",WIDTH//2,HEIGHT//2+100,w=260,h=50)
    tf=pygame.font.SysFont("consolas",36,bold=True);inf=pygame.font.SysFont("consolas",30,bold=True)
    tick=0
    while True:
        tick+=1;cur+=1;mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_RETURN and name.strip(): save_highscore(name.strip()[:12],score,zone);return
                elif event.key==pygame.K_BACKSPACE: name=name[:-1]
                elif len(name)<12 and event.unicode.isprintable(): name+=event.unicode
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if confirm.clicked((mx,my)) and name.strip(): save_highscore(name.strip()[:12],score,zone);return
        draw_menu_bg(screen,tick)
        t=tf.render("HIGHSCORE EINTRAGEN",True,YELLOW);screen.blit(t,(WIDTH//2-t.get_width()//2,HEIGHT//2-200))
        sc=inf.render(f"Score: {score}   |   Zone {zone}",True,WHITE);screen.blit(sc,(WIDTH//2-sc.get_width()//2,HEIGHT//2-140))
        ir=pygame.Rect(WIDTH//2-150,HEIGHT//2-30,300,54)
        pygame.draw.rect(screen,(30,30,50),ir,border_radius=6);pygame.draw.rect(screen,(100,100,160),ir,2,border_radius=6)
        cursor="|" if cur%40<20 else ""
        it=inf.render(name+cursor,True,WHITE);screen.blit(it,(ir.centerx-it.get_width()//2,ir.centery-it.get_height()//2))
        confirm.update((mx,my));confirm.draw(screen)
        pygame.display.flip();clock.tick(FPS)

def show_gameover(score,zone):
    retry=MenuButton("NOCHMAL VERSUCHEN",WIDTH//2,HEIGHT//2+60,w=280,h=50)
    menu=MenuButton("HAUPTMENUE",WIDTH//2,HEIGHT//2+125,w=260,h=50)
    tick=0;f1=pygame.font.SysFont("consolas",60,bold=True);f2=pygame.font.SysFont("consolas",22)
    while True:
        tick+=1;mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return "menu"
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if retry.clicked((mx,my)): return "retry"
                if menu.clicked((mx,my)): return "menu"
        draw_menu_bg(screen,tick)
        t1=f1.render("GAME OVER",True,RED);t2=f2.render(f"Score: {score}   |   Zone {zone} erreicht",True,GRAY)
        screen.blit(t1,(WIDTH//2-t1.get_width()//2,HEIGHT//2-120))
        screen.blit(t2,(WIDTH//2-t2.get_width()//2,HEIGHT//2-40))
        retry.update((mx,my));menu.update((mx,my));retry.draw(screen);menu.draw(screen)
        pygame.display.flip();clock.tick(FPS)

def show_win(score):
    hs=MenuButton("HIGHSCORE SPEICHERN",WIDTH//2,HEIGHT//2+55,w=300,h=50)
    menu=MenuButton("HAUPTMENUE",WIDTH//2,HEIGHT//2+120,w=260,h=50)
    tick=0;f1=pygame.font.SysFont("consolas",44,bold=True)
    f2=pygame.font.SysFont("consolas",24);f3=pygame.font.SysFont("consolas",18)
    while True:
        tick+=1;mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if hs.clicked((mx,my)): return "highscore"
                if menu.clicked((mx,my)): return "menu"
        draw_menu_bg(screen,tick)
        t1=f1.render("SIEG! ALLE ZONEN BEFREIT!",True,GREEN)
        t2=f2.render(f"Finaler Score: {score}",True,YELLOW)
        t3=f3.render("General besiegt — Festung Omega ist gefallen!",True,WHITE)
        screen.blit(t1,(WIDTH//2-t1.get_width()//2,HEIGHT//2-140))
        screen.blit(t2,(WIDTH//2-t2.get_width()//2,HEIGHT//2-70))
        screen.blit(t3,(WIDTH//2-t3.get_width()//2,HEIGHT//2-30))
        hs.update((mx,my));menu.update((mx,my));hs.draw(screen);menu.draw(screen)
        pygame.display.flip();clock.tick(FPS)

# ═══════════════════════════════════════════════════
#  BOSS CUTSCENE (revised — no "phase 1 of 3" text)
# ═══════════════════════════════════════════════════
def show_boss_cutscene():
    """
    Cinematic 4-act boss intro:
    Act 0 – Blackout + red lightning + Ω symbol
    Act 1 – Transmission panel with typewriter dialogue
    Act 2 – Boss silhouette reveal with camera shake
    Act 3 – Phase announcement + fade to battle
    """
    clock_cut = pygame.time.Clock()
    tick  = 0
    act   = 0
    act_t = 0   # frames since act start

    lines = [
        "Soldat… du hast es weit gebracht.",
        "Sechs Zonen. Meine besten Generäle.",
        "Alle gefallen. Wegen dir.",
        "Jetzt stehe ich dir selbst gegenüber.",
        "Ich bin GENERAL OMEGA.",
        "Und du WIRST scheitern.",
    ]
    displayed   = [""]
    line_idx    = 0
    char_idx    = 0
    line_timer  = 0

    f_omega  = pygame.font.SysFont("consolas", 130, bold=True)
    f_huge   = pygame.font.SysFont("consolas", 58,  bold=True)
    f_big    = pygame.font.SysFont("consolas", 28,  bold=True)
    f_med    = pygame.font.SysFont("consolas", 19,  bold=True)
    f_small  = pygame.font.SysFont("consolas", 14)
    f_tiny   = pygame.font.SysFont("consolas", 11)

    shake_x = shake_y = 0
    scan_y  = 0.0
    static_lines = [(random.randint(0,WIDTH), random.randint(0,HEIGHT//3),
                     random.randint(2,6)) for _ in range(80)]

    # Lightning bolts (pre-generated for act 0)
    def gen_lightning(x1, y1, x2, y2, segments=10):
        pts = [(x1, y1)]
        for i in range(1, segments):
            t2 = i / segments
            bx2 = int(x1 + (x2-x1)*t2 + random.randint(-40,40))
            by2 = int(y1 + (y2-y1)*t2 + random.randint(-20,20))
            pts.append((bx2,by2))
        pts.append((x2,y2))
        return pts

    lightning_bolts = [gen_lightning(random.randint(0,WIDTH), 0,
                                     random.randint(0,WIDTH), HEIGHT//2)
                       for _ in range(5)]

    # Particle accumulator for EMP ring
    emp_ring_particles = []

    while True:
        tick  += 1
        act_t += 1
        clock_cut.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                    return

        # ── Act transitions ───────────────────────────────────────────────────
        if act == 0 and act_t > 110:
            act = 1; act_t = 0; SFX.play(SFX.boss_roar)
            lightning_bolts = [gen_lightning(random.randint(0,WIDTH), 0,
                                             random.randint(0,WIDTH), HEIGHT//2)
                               for _ in range(5)]
        elif act == 1:
            # Typewriter
            line_timer += 1
            if line_idx < len(lines):
                line2 = lines[line_idx]
                if char_idx < len(line2):
                    if line_timer % 2 == 0:
                        char_idx += 1
                        displayed[line_idx] = line2[:char_idx]
                else:
                    if line_timer > 55:
                        line_idx += 1; char_idx = 0; line_timer = 0
                        if line_idx < len(lines): displayed.append("")
            else:
                if act_t > len(lines)*75 + 90:
                    act = 2; act_t = 0
                    SFX.play(SFX.big_explosion)
                    for i in range(40):
                        ang2 = (i/40)*2*math.pi
                        emp_ring_particles.append({
                            "x": float(WIDTH//2 + math.cos(ang2)*60),
                            "y": float(HEIGHT//2 + math.sin(ang2)*60),
                            "vx": math.cos(ang2)*7, "vy": math.sin(ang2)*7,
                            "life": random.randint(30,55), "col": EMP_COL
                        })
        elif act == 2:
            shake_x = random.randint(-10,10) if act_t < 80 else 0
            shake_y = random.randint(-10,10) if act_t < 80 else 0
            if act_t == 40: SFX.play(SFX.boss_roar)
            if act_t > 200: act = 3; act_t = 0
        elif act == 3:
            if act_t > 90: return

        # ── EMP ring update ───────────────────────────────────────────────────
        for ep in emp_ring_particles:
            ep["x"] += ep["vx"]; ep["y"] += ep["vy"]
            ep["vx"] *= 0.92;    ep["vy"] *= 0.92
            ep["life"] -= 1
        emp_ring_particles = [ep for ep in emp_ring_particles if ep["life"]>0]

        scan_y = (scan_y + 3.0) % HEIGHT

        # ══════════════════════════════════════════════════════════════════════
        #  DRAW
        # ══════════════════════════════════════════════════════════════════════
        base = pygame.Surface((WIDTH, HEIGHT))
        base.fill((3, 1, 8))

        # ── ACT 0 ─────────────────────────────────────────────────────────────
        if act == 0:
            # Pulsing red vignette
            pulse = abs(math.sin(tick*0.07))*0.5 + 0.5
            vig = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for edge in range(5):
                ea = int(pulse * (28 + edge*12))
                pygame.draw.rect(vig, (180,0,0,ea),
                                 (edge*18, edge*12, WIDTH-edge*36, HEIGHT-edge*24), 3)
            base.blit(vig, (0,0))

            # Lightning bolts
            if act_t % 18 < 4:
                for bolt in lightning_bolts[:2 + tick%3]:
                    pygame.draw.lines(base, (220,30,30), False, bolt, 2)
                    # Glow
                    for pt in bolt[::2]:
                        gs2 = pygame.Surface((20,20), pygame.SRCALPHA)
                        pygame.draw.circle(gs2, (255,60,60,60), (10,10), 10)
                        base.blit(gs2, (pt[0]-10, pt[1]-10))
                # White flash
                if act_t % 18 < 2:
                    fl = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
                    fl.fill((255,255,255,55))
                    base.blit(fl,(0,0))

            # Omega symbol — grows in
            oa = min(255, act_t*4)
            scale_o = min(1.0, act_t/80)
            ot = f_omega.render("Ω", True, (160,18,18))
            if scale_o < 1.0:
                sw2 = max(1, int(ot.get_width()*scale_o))
                sh2 = max(1, int(ot.get_height()*scale_o))
                ot  = pygame.transform.scale(ot, (sw2, sh2))
            ot.set_alpha(oa)
            base.blit(ot, (WIDTH//2-ot.get_width()//2,
                           HEIGHT//2-ot.get_height()//2))
            # Glow behind Ω
            for gr in range(3):
                gs3 = pygame.Surface((300+gr*80, 200+gr*50), pygame.SRCALPHA)
                ga  = int(oa*0.15*scale_o)
                pygame.draw.ellipse(gs3, (180,10,10,ga),
                                    (0,0,300+gr*80,200+gr*50))
                base.blit(gs3, (WIDTH//2-(300+gr*80)//2,
                                HEIGHT//2-(200+gr*50)//2))

            # "INCOMING TRANSMISSION…" text fade in
            if act_t > 55:
                trans_a = min(255,(act_t-55)*8)
                tt2 = f_small.render("▶▶▶  EINGEHENDE ÜBERTRAGUNG  ◀◀◀", True, (140,15,15))
                tt2.set_alpha(trans_a)
                base.blit(tt2,(WIDTH//2-tt2.get_width()//2, HEIGHT-70))

        # ── ACT 1: Transmission Panel ─────────────────────────────────────────
        elif act == 1:
            # Scanline background
            for sy2 in range(0, HEIGHT, 6):
                t3 = sy2/HEIGHT
                r3 = int(4+t3*8); g3 = int(2+t3*4); b3 = int(12+t3*18)
                pygame.draw.rect(base,(r3,g3,b3),(0,sy2,WIDTH,3))

            # Noise flicker
            if tick%12 < 2:
                noise_s = pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
                for _ in range(200):
                    nx3 = random.randint(0,WIDTH); ny3 = random.randint(0,HEIGHT)
                    pygame.draw.rect(noise_s,(200,0,0,random.randint(10,40)),
                                     (nx3,ny3,random.randint(1,8),1))
                base.blit(noise_s,(0,0))

            # Main panel — dark glass with red border
            pw2 = WIDTH-80; ph2 = HEIGHT-100
            panel = pygame.Surface((pw2, ph2), pygame.SRCALPHA)
            for py2 in range(ph2):
                t4 = py2/ph2
                pygame.draw.line(panel,(4,2,10,int(210-t4*60)),
                                 (0,py2),(pw2,py2))
            pygame.draw.rect(panel,(160,12,12),(0,0,pw2,ph2),2,border_radius=6)
            pygame.draw.rect(panel,(200,20,20),(0,0,pw2,4),border_radius=6)
            # Corner marks
            for (cx3,cy3,cdx,cdy) in [(0,0,1,1),(pw2,0,-1,1),(0,ph2,1,-1),(pw2,ph2,-1,-1)]:
                pygame.draw.line(panel,(180,15,15),(cx3,cy3),(cx3+cdx*22,cy3),2)
                pygame.draw.line(panel,(180,15,15),(cx3,cy3),(cx3,cy3+cdy*22),2)
            base.blit(panel,(40,50))

            # Panel header bar
            hdr_s = pygame.Surface((pw2,32), pygame.SRCALPHA)
            hdr_s.fill((140,10,10,180))
            base.blit(hdr_s,(40,50))
            hdr_t = f_small.render(
                "◈ FEIND-ÜBERTRAGUNG  |  VERSCHLÜSSELT  |  QUELLE: FESTUNG OMEGA",
                True,(255,180,180))
            base.blit(hdr_t,(52,60))
            # Signal strength bars
            for si2 in range(5):
                sh3 = 4+si2*4
                scol = (140,10,10) if si2 > 3 else (200,20,20)
                pygame.draw.rect(base, scol,
                                 (WIDTH-70+si2*10, 72-sh3, 7, sh3))

            # ── Boss portrait (left half) ─────────────────────────────────────
            bpx = 120; bpy = HEIGHT//2 + 10
            # Shadow under figure
            sh4 = pygame.Surface((90,16),pygame.SRCALPHA)
            pygame.draw.ellipse(sh4,(0,0,0,80),(0,0,90,16))
            base.blit(sh4,(bpx-45,bpy+58))

            # Legs
            leg_sway = int(math.sin(tick*0.04)*3)
            pygame.draw.line(base,(100,16,16),(bpx-10,bpy+20),(bpx-12+leg_sway,bpy+58),10)
            pygame.draw.line(base,(100,16,16),(bpx+10,bpy+20),(bpx+12-leg_sway,bpy+58),10)
            # Boots
            pygame.draw.rect(base,(55,8,8),pygame.Rect(bpx-20,bpy+52,20,12),border_radius=3)
            pygame.draw.rect(base,(55,8,8),pygame.Rect(bpx+2, bpy+52,20,12),border_radius=3)

            # Body / chest armour
            pygame.draw.rect(base,(120,14,14),pygame.Rect(bpx-24,bpy-26,48,50),border_radius=4)
            pygame.draw.rect(base,(150,20,20),pygame.Rect(bpx-24,bpy-26,48,10),border_radius=4)
            pygame.draw.rect(base,(80,8,8),   pygame.Rect(bpx-18,bpy-22,36,38),border_radius=3)
            # Chest energy core
            core_a = int(140+abs(math.sin(tick*0.09))*115)
            cs4 = pygame.Surface((18,18),pygame.SRCALPHA)
            pygame.draw.circle(cs4,(255,50,255,core_a),(9,9),9)
            pygame.draw.circle(cs4,(255,140,255,core_a//2),(9,9),14)
            base.blit(cs4,(bpx-9,bpy-8))
            # Shoulder pads
            pygame.draw.rect(base,(110,12,12),pygame.Rect(bpx-38,bpy-22,18,22),border_radius=4)
            pygame.draw.rect(base,(110,12,12),pygame.Rect(bpx+20,bpy-22,18,22),border_radius=4)
            pygame.draw.rect(base,(140,18,18),pygame.Rect(bpx-38,bpy-22,18,6),border_radius=4)
            pygame.draw.rect(base,(140,18,18),pygame.Rect(bpx+20,bpy-22,18,6),border_radius=4)
            # Arms
            arm_angle = math.sin(tick*0.035)*0.25
            pygame.draw.line(base,(100,14,14),(bpx-20,bpy-16),
                             (int(bpx-44+math.cos(arm_angle)*8),
                              int(bpy+16+math.sin(arm_angle)*8)),8)
            pygame.draw.line(base,(100,14,14),(bpx+20,bpy-16),
                             (int(bpx+44-math.cos(arm_angle)*8),
                              int(bpy+16+math.sin(arm_angle)*8)),8)

            # Neck
            pygame.draw.rect(base,(90,60,55),pygame.Rect(bpx-7,bpy-38,14,14))
            # Head
            pygame.draw.circle(base,(175,105,85),(bpx,bpy-46),22)
            # Full face helmet — phase 1 style
            pygame.draw.arc(base,(55,10,10),pygame.Rect(bpx-26,bpy-72,52,32),0,math.pi,8)
            pygame.draw.rect(base,(45,8,8),pygame.Rect(bpx-26,bpy-56,52,16))
            # Glowing visor slit
            vis_a2 = int(160+abs(math.sin(tick*0.10))*95)
            vs3 = pygame.Surface((34,10),pygame.SRCALPHA)
            pygame.draw.ellipse(vs3,(220,20,20,vis_a2),(0,0,34,10))
            base.blit(vs3,(bpx-17,bpy-54))
            # Glint on visor
            pygame.draw.line(base,(255,120,120),(bpx-12,bpy-53),(bpx+2,bpy-53),1)
            # Helmet spikes
            for sk2_off in (-18,-8,2,12):
                pygame.draw.polygon(base,(80,12,8),
                                    [(bpx+sk2_off,   bpy-70),
                                     (bpx+sk2_off+5, bpy-86),
                                     (bpx+sk2_off+10,bpy-70)])
            # Eye glow outside visor
            ey_a2 = int(120+abs(math.sin(tick*0.11))*135)
            for ex2_off in (-10,8):
                es3 = pygame.Surface((14,14),pygame.SRCALPHA)
                pygame.draw.circle(es3,(255,25,25,ey_a2),(7,7),7)
                base.blit(es3,(bpx+ex2_off-7,bpy-56))

            # Rank medals
            for mi in range(3):
                pygame.draw.circle(base,(200,160,20),(bpx-14+mi*8,bpy-18),4)
                pygame.draw.circle(base,(255,210,50),(bpx-14+mi*8,bpy-18),3)

            # Vertical accent line between portrait and text
            pygame.draw.line(base,(140,12,12),(240,60),(240,HEIGHT-55),1)
            # Glitch flicker on portrait
            if tick%22<2:
                gl_s = pygame.Surface((160,HEIGHT-110),pygame.SRCALPHA)
                gl_s.fill((255,0,0,12))
                base.blit(gl_s,(55,55))

            # ── Text side ────────────────────────────────────────────────────
            for i2, line3 in enumerate(displayed):
                if i2 >= len(lines): break
                done3 = (i2 < line_idx)
                col3  = (245,220,220) if done3 else (255,255,255)
                # Line number
                ln3 = f_tiny.render(f"{i2+1:02d}", True,(100,18,18))
                base.blit(ln3,(258,95+i2*52))
                # Highlight active line
                if i2 == line_idx:
                    hl3 = pygame.Surface((WIDTH-310,28),pygame.SRCALPHA)
                    hl3.fill((160,12,12,22))
                    base.blit(hl3,(275,92+i2*52))
                t_surf3 = f_med.render(line3, True, col3)
                base.blit(t_surf3,(278,93+i2*52))
            # Cursor
            if line_idx < len(lines) and (tick//14)%2==0:
                ci3 = min(line_idx,len(displayed)-1)
                cur_x = 278+f_med.size(displayed[ci3])[0]
                cur_t = f_med.render("▌",True,(200,40,40))
                base.blit(cur_t,(cur_x,93+ci3*52))

            # ── CRT scanline ─────────────────────────────────────────────────
            scan_y2 = (scan_y + tick*1.5)%HEIGHT
            sc2 = pygame.Surface((WIDTH,3),pygame.SRCALPHA)
            sc2.fill((255,255,255,10))
            base.blit(sc2,(0,int(scan_y2)))
            # Horizontal noise lines
            if tick%8 < 2:
                for _ in range(3):
                    ny4 = random.randint(60,HEIGHT-60)
                    nl2 = pygame.Surface((random.randint(40,200),2),pygame.SRCALPHA)
                    nl2.fill((255,100,100,random.randint(20,60)))
                    base.blit(nl2,(random.randint(260,WIDTH-80),ny4))

            # Continue hint when done
            if line_idx >= len(lines):
                hint_a = int(128+abs(math.sin(tick*0.06))*127)
                ht3 = f_small.render("[ SPACE ]  Weiter", True,(200,40,40))
                hs3 = pygame.Surface((ht3.get_width()+20,ht3.get_height()+10),pygame.SRCALPHA)
                hs3.fill((0,0,0,120))
                pygame.draw.rect(hs3,(160,12,12),(0,0,hs3.get_width(),hs3.get_height()),1,border_radius=3)
                hs3.blit(ht3,(10,5))
                hs3.set_alpha(hint_a)
                base.blit(hs3,(WIDTH//2-hs3.get_width()//2,HEIGHT-58))

        # ── ACT 2: Boss Reveal ────────────────────────────────────────────────
        elif act == 2:
            # Dark red gradient
            for sy3 in range(0,HEIGHT,4):
                t5 = sy3/HEIGHT
                pygame.draw.rect(base,(int(8+t5*18),int(2+t5*4),int(18+t5*8)),
                                 (0,sy3,WIDTH,4))

            # EMP ring particles
            for ep in emp_ring_particles:
                ep_a = int(ep["life"]/55*220)
                if ep_a<4: continue
                es4 = pygame.Surface((10,10),pygame.SRCALPHA)
                pygame.draw.circle(es4,(*ep["col"],ep_a),(5,5),5)
                base.blit(es4,(int(ep["x"])-5,int(ep["y"])-5))

            # Radial shockwave rings
            for ri2 in range(3):
                r3 = int(act_t*8 + ri2*60)
                if r3 > 800: continue
                ra3 = max(0,int(180-act_t*2))
                rs3 = pygame.Surface((r3*2+4,r3*2+4),pygame.SRCALPHA)
                pygame.draw.circle(rs3,(255,20,20,ra3),(r3+2,r3+2),r3,3)
                base.blit(rs3,(WIDTH//2-r3-2,HEIGHT//2-r3-2))

            # "GENERAL OMEGA" text — builds in
            if act_t > 20:
                scale3 = min(1.0,(act_t-20)/35)
                gt3 = f_huge.render("GENERAL  OMEGA", True,(220,18,18))
                if scale3 < 1.0:
                    gt3 = pygame.transform.scale(gt3,
                                                  (max(1,int(gt3.get_width()*scale3)),
                                                   max(1,int(gt3.get_height()*scale3))))
                # Shadow
                sh5 = f_huge.render("GENERAL  OMEGA", True,(80,4,4))
                sh5_s = pygame.transform.scale(sh5,gt3.get_size())
                base.blit(sh5_s,(WIDTH//2-gt3.get_width()//2+4,HEIGHT//2-80+4))
                base.blit(gt3,(WIDTH//2-gt3.get_width()//2,HEIGHT//2-80))
                # Glow
                gl3 = pygame.Surface((gt3.get_width()+40,gt3.get_height()+20),pygame.SRCALPHA)
                pygame.draw.rect(gl3,(220,15,15,int(30*scale3)),
                                 (0,0,gl3.get_width(),gl3.get_height()),border_radius=5)
                base.blit(gl3,(WIDTH//2-gl3.get_width()//2,HEIGHT//2-90))

            # Phase warning
            if act_t > 80:
                pw_a = min(255,(act_t-80)*7)
                pw_t = f_big.render("3 KAMPFPHASEN  —  KEINE GNADE", True,(255,180,60))
                pw_t.set_alpha(pw_a)
                base.blit(pw_t,(WIDTH//2-pw_t.get_width()//2,HEIGHT//2+10))
                # Decorative line
                pygame.draw.line(base,(200,140,20),
                                 (WIDTH//2-260,HEIGHT//2+6),(WIDTH//2+260,HEIGHT//2+6),1)

            if act_t > 130:
                sub4 = f_small.render("Phase 1 von 3  —  KAMPF BEGINNT", True,(180,60,60))
                sub4.set_alpha(min(255,(act_t-130)*8))
                base.blit(sub4,(WIDTH//2-sub4.get_width()//2,HEIGHT//2+52))

            # Red screen border flash
            if act_t < 80:
                border_a = max(0,int(180-act_t*2))
                pygame.draw.rect(base,(220,15,15),(0,0,WIDTH,HEIGHT),6)
                fl4 = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
                fl4.fill((220,15,15,border_a//4))
                base.blit(fl4,(0,0))

        # ── ACT 3: Fade to battle ─────────────────────────────────────────────
        elif act == 3:
            fade_a = min(255,act_t*4)
            fd3 = pygame.Surface((WIDTH,HEIGHT))
            fd3.fill((0,0,0))
            fd3.set_alpha(fade_a)
            base.blit(fd3,(0,0))

        screen.blit(base,(shake_x, shake_y))
        pygame.display.flip()

class AmbushSystem:
    """Triggers scripted enemy waves when the player crosses X thresholds."""
    def __init__(self, ambushes):
        # ambushes = list of {"trigger_x": int, "enemies": [(cls, x, y), ...], "fired": False}
        self.ambushes = [dict(a, fired=False) for a in ambushes]
        self.active_msg = ""
        self.msg_timer  = 0

    def check(self, player_x, enemy_list, diff):
        for amb in self.ambushes:
            if amb["fired"]: continue
            if player_x > amb["trigger_x"]:
                amb["fired"] = True
                self.active_msg = "⚠ VERSTÄRKUNG!"
                self.msg_timer  = 180
                SFX.play(SFX.boss_roar)
                for (cls, ex3, ey3) in amb["enemies"]:
                    e2 = cls(ex3, ey3,
                             hp=int(70 * diff["enemy_hp_mult"]),
                             speed=3.5 * diff["enemy_speed_mult"],
                             shoot_rate=int(900 * diff["shoot_rate_mult"]))
                    enemy_list.append(e2)
                    PARTICLES.spawn_explosion(ex3, ey3, scale=0.8)

    def update(self):
        if self.msg_timer > 0: self.msg_timer -= 1

    def draw(self, surf):
        if self.msg_timer <= 0: return
        alpha5 = min(255, self.msg_timer * 4)
        f2 = pygame.font.SysFont("consolas", 28, bold=True)
        t2 = f2.render(self.active_msg, True, (255, 60, 60))
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.012)) * 6
        s2 = pygame.Surface((t2.get_width()+24, t2.get_height()+12), pygame.SRCALPHA)
        s2.fill((0, 0, 0, 130))
        pygame.draw.rect(s2,(255,40,40),(0,0,s2.get_width(),s2.get_height()),2,border_radius=4)
        s2.blit(t2,(12,6))
        s2.set_alpha(alpha5)
        surf.blit(s2,(WIDTH//2-s2.get_width()//2, int(HEIGHT//2-80-pulse)))

class AirstrikeEvent:
    """Randomly triggers an airstrike warning, then rains bullets from above."""
    COOLDOWN = 900   # frames between strikes
    WARNING  = 120   # frames of warning before hit

    def __init__(self):
        self.timer     = self.COOLDOWN
        self.state     = "idle"   # idle, warning, striking
        self.warn_x    = 0
        self.strike_timer = 0
        self.bullets_fired = 0

    def update(self, player, enemy_bullets_list, zone_num):
        if zone_num < 4: return   # only in zones 4+
        if self.state == "idle":
            self.timer -= 1
            if self.timer <= 0:
                self.state    = "warning"
                self.warn_x   = int(player.x + random.randint(-200, 200))
                self.warn_x   = max(100, min(WORLD_WIDTH-100, self.warn_x))
                self.timer    = self.WARNING
                SFX.play(SFX.shoot_stinger)

        elif self.state == "warning":
            self.timer -= 1
            if self.timer <= 0:
                self.state = "striking"; self.strike_timer = 60; self.bullets_fired = 0

        elif self.state == "striking":
            self.strike_timer -= 1
            self.bullets_fired += 1
            if self.bullets_fired % 4 == 0:
                bx3 = self.warn_x + random.randint(-55, 55)
                b2  = Bullet(bx3, -20, random.uniform(-1.5,1.5), 16,
                             int(14 * get_diff()["enemy_dmg_mult"]),
                             (255, 80, 80))
                enemy_bullets_list.append(b2)
                PARTICLES.spawn_bullet_impact(bx3, GROUND_Y-5, (255,80,80))
            if self.strike_timer <= 0:
                self.state = "idle"; self.timer = self.COOLDOWN

    def draw(self, surf, cam_x=0):
        if self.state == "warning":
            blink3 = (pygame.time.get_ticks() // 80) % 2 == 0
            sx3 = self.warn_x - cam_x
            if -100 < sx3 < WIDTH + 100:
                # Warning cone from top
                alpha7 = int(80 + (1 - self.timer/self.WARNING) * 140)
                ws2 = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.polygon(ws2,(255,40,40,int(alpha7*0.3)),
                    [(sx3-8,0),(sx3+8,0),(sx3+55,GROUND_Y),(sx3-55,GROUND_Y)])
                surf.blit(ws2,(0,0))
                # Warning line
                if blink3:
                    pygame.draw.line(surf,(255,40,40),(sx3-60,0),(sx3-60,HEIGHT),1)
                    pygame.draw.line(surf,(255,40,40),(sx3+60,0),(sx3+60,HEIGHT),1)
                # Warning text
                wf2 = pygame.font.SysFont("consolas",18,bold=True)
                wt2 = wf2.render("⚠ LUFTANGRIFF!", True,(255,50,50))
                wt2.set_alpha(int(alpha7*1.5))
                surf.blit(wt2,(sx3-wt2.get_width()//2, 15))
                # Crosshair
                ch_r2=int(30+(1-self.timer/self.WARNING)*25)
                pygame.draw.circle(surf,(255,40,40),(sx3,GROUND_Y-ch_r2*2),ch_r2,2)
                for ch_off2 in range(0,360,45):
                    ca = math.radians(ch_off2)
                    pygame.draw.line(surf,(255,40,40),
                        (sx3+int(math.cos(ca)*ch_r2),GROUND_Y-ch_r2*2+int(math.sin(ca)*ch_r2)),
                        (sx3+int(math.cos(ca)*(ch_r2+10)),GROUND_Y-ch_r2*2+int(math.sin(ca)*(ch_r2+10))),1)

AIRSTRIKE = AirstrikeEvent()

class DropshipEvent:
    """A dropship flies across and drops 3-5 enemies mid-zone."""
    COOLDOWN = 1800   # frames between events
    def __init__(self):
        self.timer  = random.randint(600, 1200)
        self.active = False
        self.ship_x = float(-200)
        self.ship_y = float(GROUND_Y - 280)
        self.dir    = 1
        self.drops  = []       # pending drop positions
        self.dropped= []       # already dropped (x positions)
        self.drop_timer = 0
        self.msg_timer  = 0

    def start(self, zone_num):
        if zone_num < 3: return
        self.active   = True
        self.dir      = random.choice([-1, 1])
        self.ship_x   = float(-300) if self.dir==1 else float(WORLD_WIDTH+300)
        self.ship_y   = float(GROUND_Y - random.randint(220, 300))
        n_drops       = 2 + zone_num // 2
        spacing       = 220
        cx4           = WORLD_WIDTH // 2 + random.randint(-400, 400)
        self.drops    = [cx4 + i*spacing - n_drops*spacing//2
                         for i in range(n_drops)]
        self.dropped  = []
        self.drop_timer= 0
        self.msg_timer = 180
        SFX.play(SFX.shoot_rocket)

    def update(self, player, enemy_list, zone_num):
        if zone_num < 3:
            return
        if not self.active:
            self.timer -= 1
            if self.timer <= 0:
                self.timer = self.COOLDOWN + random.randint(-200, 200)
                self.start(zone_num)
            return
        if self.msg_timer > 0: self.msg_timer -= 1

        # Move ship
        self.ship_x += self.dir * 5.5
        self.drop_timer += 1

        # Drop enemies at defined X positions
        for dx5 in list(self.drops):
            if ((self.dir == 1 and self.ship_x >= dx5) or
                (self.dir == -1 and self.ship_x <= dx5)):
                self.drops.remove(dx5)
                self.dropped.append(dx5)
                # Spawn enemy falling from sky
                gy4 = current_platforms[0].top - Enemy.H
                diff = get_diff()
                e3 = random.choice([Enemy, ShieldSoldier])(
                    dx5, self.ship_y + 30,
                    hp    = int(65  * diff["enemy_hp_mult"]),
                    speed = 3.2  * diff["enemy_speed_mult"],
                    shoot_rate = int(1000 * diff["shoot_rate_mult"]))
                e3.vy = 6.0   # falling
                enemy_list.append(e3)
                PARTICLES.spawn_explosion(dx5, int(self.ship_y)+30, scale=0.5)
                SFX.play(SFX.big_explosion)

        # Done when ship exits screen
        if (self.dir == 1 and self.ship_x > WORLD_WIDTH + 400) or \
           (self.dir == -1 and self.ship_x < -400):
            self.active = False

    def draw(self, surf, cam_x=0):
        if self.msg_timer > 0:
            alpha9=min(255,self.msg_timer*3)
            df2=pygame.font.SysFont("consolas",22,bold=True)
            dt2=df2.render("⚠ VERSTÄRKUNGS-DROPSHIP",True,(255,140,30))
            ds2=pygame.Surface((dt2.get_width()+24,dt2.get_height()+12),pygame.SRCALPHA)
            ds2.fill((0,0,0,120))
            pygame.draw.rect(ds2,(255,140,30),(0,0,ds2.get_width(),ds2.get_height()),2,border_radius=4)
            ds2.blit(dt2,(12,6)); ds2.set_alpha(alpha9)
            surf.blit(ds2,(WIDTH//2-ds2.get_width()//2,14))

        if not self.active: return
        sx6 = int(self.ship_x) - cam_x
        sy6 = int(self.ship_y)
        if -300 < sx6 < WIDTH+300:
            f2  = -self.dir
            # Body
            body_pts=[
                (sx6-80,sy6+8),(sx6+80,sy6+8),
                (sx6+90,sy6+24),(sx6-90,sy6+24)]
            pygame.draw.polygon(surf,(42,52,68),body_pts)
            pygame.draw.polygon(surf,(62,76,95),body_pts,1)
            # Cockpit
            pygame.draw.ellipse(surf,(50,150,190),(sx6+f2*30,sy6+2,30,18))
            pygame.draw.ellipse(surf,(80,200,240),(sx6+f2*30,sy6+2,30,9))
            # Wings
            pygame.draw.polygon(surf,(32,40,55),
                [(sx6-80,sy6+8),(sx6-110,sy6+30),(sx6-50,sy6+20)])
            pygame.draw.polygon(surf,(32,40,55),
                [(sx6+80,sy6+8),(sx6+110,sy6+30),(sx6+50,sy6+20)])
            # Engines
            for eng_off in (-55,0,55):
                pygame.draw.ellipse(surf,(28,32,42),(sx6+eng_off-10,sy6+20,20,10))
                # Exhaust
                for _ in range(3):
                    ex4=sx6+eng_off+random.randint(-5,5)
                    ey4=sy6+30+random.randint(0,14)
                    es3=pygame.Surface((8,8),pygame.SRCALPHA)
                    pygame.draw.circle(es3,(255,180,40,random.randint(80,180)),(4,4),4)
                    surf.blit(es3,(ex4-4,ey4-4))
            # Drop indicators
            for dx6 in self.drops:
                dsx=dx6-cam_x
                if 0<dsx<WIDTH:
                    pygame.draw.line(surf,(255,140,30,100),(dsx,sy6+30),(dsx,GROUND_Y),1)
                    pygame.draw.ellipse(surf,(255,100,20),(dsx-14,GROUND_Y-3,28,5))

DROPSHIP = DropshipEvent()

# ═══════════════════════════════════════════════════
#  ZONE SPIELEN
# ═══════════════════════════════════════════════════
def play_zone(zone_num, player):
    global current_platforms, screen_shake
    cfg = ZONES[zone_num]
    current_platforms = cfg["platforms"]
 
    # ── Reset player for zone ──
    player.x = 100.0
    player.y = float(current_platforms[0].top - Player.H)
    player.vx = player.vy = 0.0
    player.hp = player.MAX_HP
    player.invincible = 1500
    player.shield_timer = 0
    player.zone_damage_taken = 0
    player.knife_only_zone = True
    player.stun_timer = 0        # NEW
    player.turrets = []          # NEW
    player.sandbags = []
 
    screen_shake = 0
    PARTICLES.particles.clear()
    ammo_bonus = 1.25 if SKILLS.extra_ammo() else 1.0
    RAKETENWERFER.ammo = int(RAKETENWERFER.max_ammo * ammo_bonus)
    STINGER.ammo       = int(STINGER.max_ammo * ammo_bonus)
    EMP_CANNON.ammo    = int(EMP_CANNON.max_ammo * ammo_bonus) if EMP_CANNON.max_ammo else None
    FLAMMENWERFER.ammo = FLAMMENWERFER.max_ammo if FLAMMENWERFER.max_ammo else None
    COMBO.count = 0
    COMBO.timer = 0
 
    WEATHER.set_zone(zone_num)
    ENV_SYSTEM.spawn_for_zone(zone_num, current_platforms)
    camera = Camera()
    camera.x = 0.0
    is_boss_zone = (zone_num == NUM_ZONES)
 
    # ── Spawn all enemy types ──
    # V7: zones 7-8 get elite enemy variants
    zone_elite = zone_num >= 7
    enemies = [Enemy(ex, ey,
                     hp=int(cfg["enemy_hp"] * (1.4 if zone_elite else 1.0)),
                     speed=cfg["enemy_speed"] * (1.1 if zone_elite else 1.0),
                     shoot_rate=int(cfg["enemy_shoot_rate"] * (0.8 if zone_elite else 1.0)))
               for ex, ey in cfg["enemy_positions"]]
 
    tanks = [Tank(tx2, ty2) for tx2, ty2 in cfg.get("tank_positions", [])]
 
    jetpack_soldiers = [JetpackSoldier(jx, jy)
                        for jx, jy in cfg.get("jetpack_positions", [])]
 
    air_enemies = []
    for etype, ex2 in cfg.get("air_enemies", []):
        if etype == "drone":       air_enemies.append(Drone(ex2))
        elif etype == "helicopter": air_enemies.append(Helicopter(ex2))
        elif etype == "jet":        air_enemies.append(Jet(ex2))
 
    # NEW enemy types
    shield_soldiers = [ShieldSoldier(sx, sy,
                                     hp=cfg["enemy_hp"],
                                     speed=cfg["enemy_speed"],
                                     shoot_rate=cfg["enemy_shoot_rate"])
                       for sx, sy in cfg.get("shield_positions", [])]
 
    snipers = [SniperEnemy(sx, sy, hp=55, speed=1.5, shoot_rate=2800)
               for sx, sy in cfg.get("sniper_positions", [])]
 
    heavy_gunners = [HeavyGunner(hx, hy, hp=220, speed=1.4, shoot_rate=900)
                     for hx, hy in cfg.get("heavy_positions", [])]
    
    mech_walkers = [MechWalker(mx_pos, my_pos)
                for mx_pos, my_pos in cfg.get("mech_positions", [])]
    
    turret_enemies = [TurretEnemy(tx_pos, ty_pos)
                      for tx_pos, ty_pos in cfg.get("turret_positions", [])]
    
    def _spawn_x(val):
        """Accept either a bare x int or an (x, y) tuple — always return x."""
        return val[0] if isinstance(val, (tuple, list)) else val

    riot_soldiers = [RiotShieldSoldier(
                        _spawn_x(rv),
                        current_platforms[0].top - RiotShieldSoldier.H,
                        hp=cfg["enemy_hp"], speed=cfg["enemy_speed"],
                        shoot_rate=cfg["enemy_shoot_rate"])
                     for rv in cfg.get("riot_positions", [])]

    flame_troopers = [FlameTrooper(
                        _spawn_x(fv),
                        current_platforms[0].top - FlameTrooper.H,
                        hp=cfg["enemy_hp"], speed=cfg["enemy_speed"],
                        shoot_rate=cfg["enemy_shoot_rate"])
                      for fv in cfg.get("flame_trooper_positions", [])]
    bomber_jets    = [BomberJet(bx) for bx in cfg.get("bomber_jet_positions", [])]
    BASE_BUILD.reset()
 
    kamikaze_drones = [KamikazeDrone(kx)
                       for kx in cfg.get("kamikaze_positions", [])]
    suicide_bombers  = [SuicideBomber(bx2, current_platforms[0].top - SuicideBomber.H)
                        for bx2 in cfg.get("bomber_positions", [])]
    stealth_soldiers = [StealthSoldier(sx2, sy2)
                        for sx2, sy2 in cfg.get("stealth_positions", [])]
    mortar_soldiers  = [MortarSoldier(mx2, my2)
                        for mx2, my2 in cfg.get("mortar_positions", [])]
    sniper_mechs = [SniperMechs(sx, sy) for sx, sy in cfg.get("sniper_mech_positions", [])]
    mortar_shells    = []   # live shells in the air

    # Ambush triggers per zone
    GY2 = current_platforms[0].top - Enemy.H
    _ambush_defs = {
        3: [{"trigger_x": 1500, "enemies": [(Enemy,1600,GY2),(Enemy,1700,GY2),(Enemy,1650,GY2)]}],
        4: [{"trigger_x": 1200, "enemies": [(Enemy,1300,GY2),(ShieldSoldier,1350,GY2)]},
            {"trigger_x": 2500, "enemies": [(HeavyGunner,2600,GY2),(Enemy,2500,GY2),(Enemy,2700,GY2)]}],
        5: [{"trigger_x": 1000, "enemies": [(StealthSoldier,1100,GY2),(StealthSoldier,1200,GY2)]},
            {"trigger_x": 2400, "enemies": [(SuicideBomber,2500,GY2),(SuicideBomber,2600,GY2),(Enemy,2450,GY2)]}],
        6: [{"trigger_x": 800,  "enemies": [(HeavyGunner,900,GY2),(ShieldSoldier,1000,GY2)]},
            {"trigger_x": 1800, "enemies": [(MortarSoldier,1900,GY2),(StealthSoldier,1850,GY2)]},
            {"trigger_x": 3000, "enemies": [(SuicideBomber,3100,GY2),(SuicideBomber,3200,GY2),
                                             (HeavyGunner,3150,GY2)]}],
    }
    ambush_system = AmbushSystem(_ambush_defs.get(zone_num, []))
 
    boss = Boss(WORLD_WIDTH - 400, current_platforms[0].top - Boss.H) if is_boss_zone else None
    # Zones 7-8: start boss at a lower HP threshold so transitions come faster/harder
    if boss and zone_num >= 7:
        boss.MAX_HP = int(boss.MAX_HP * 1.35)
        boss.hp = boss.MAX_HP
    if boss:
        boss._spawn_list = enemies
    if is_boss_zone:
        show_boss_cutscene()
    powerups = spawn_powerups(cfg)
 
    # ── Projectile / object lists ──
    bullets = []
    flame_bullets = []    # NEW
    emp_bullets = []      # NEW
    enemy_bullets = []
    grenades = []
    enemy_grenades = []
    player_rockets = []
    enemy_rockets = []
    drops = []            # NEW
    tick = 0
    slow_mo_accum = 0.0   # fractional frame accumulator for slow-mo

    first_kill_done = False
    tank_killed = False
 
    show_zone_intro(zone_num, cfg["name"])
 
    # ══════════════════════════════════════════════
    #  MAIN GAME LOOP
    # ══════════════════════════════════════════════
    while True:
        LIGHTS.clear()
        tick += 1
        clock.tick(FPS)
        cam_x = int(camera.x)
 
        # ── Weapon wheel slow-mo: control tick rate ───────────────────────────
        keys_held  = pygame.key.get_pressed()
        mouse_pos  = pygame.mouse.get_pos()
        wheel_open = WEAPON_WHEEL.update(keys_held, mouse_pos)

        time_scale = WEAPON_WHEEL.SLOWMO if wheel_open else 1.0
        slow_mo_accum += time_scale
        # Only run game-logic frames proportionally; always run rendering
        run_logic = slow_mo_accum >= 1.0
        if run_logic:
            slow_mo_accum -= 1.0

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    result = show_pause_menu(player)
                    if result == "menu":   return "menu"
                # Number keys still work as shortcuts
                if event.key in WEAPON_KEYS and not wheel_open:
                    player.weapon = WEAPON_KEYS[event.key]
                if event.key == pygame.K_g:
                    player.throw_grenade(grenades)
                # V7.0 Base building
                if event.key == pygame.K_b:
                    BASE_BUILD.build_mode = not BASE_BUILD.build_mode
                if BASE_BUILD.build_mode:
                    build_map = {
                        pygame.K_1:"wall", pygame.K_2:"mg_nest",
                        pygame.K_3:"mine",  pygame.K_4:"barrier",
                        pygame.K_5:"heal_pad",
                    }
                    if event.key in build_map:
                        BASE_BUILD.selected_build = build_map[event.key]
                    if event.key == pygame.K_f:
                        BASE_BUILD.place(BASE_BUILD.selected_build, player)
                if event.key == pygame.K_t:
                    max_t = SKILLS.max_turrets()
                    if len([t for t in player.turrets if t.alive]) < max_t:
                        tx3 = player.rect.centerx
                        ty3 = player.rect.bottom - DeployedTurret.H
                        player.turrets.append(DeployedTurret(tx3, ty3))
                        SFX.play(SFX.pickup)
                if event.key == pygame.K_c:
                    if len([s for s in player.sandbags if s.alive]) < 3:
                        player.sandbags.append(
                            SandbagCover(player.rect.centerx, player.rect.bottom))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not wheel_open:
                    player.shoot(bullets, player_rockets, cam_x)
                else:
                    # Confirm selection on click while wheel is open
                    player.weapon = WHEEL_WEAPONS[WEAPON_WHEEL.selected]
                    SFX.play(SFX.pickup)

            # Q released → apply selected weapon
            if event.type == pygame.KEYUP and event.key == pygame.K_q:
                player.weapon = WHEEL_WEAPONS[WEAPON_WHEEL.selected]
                SFX.play(SFX.pickup)

       # ── Player stun / movement (skip when slow-mo frame not due) ─────────
        if not run_logic:
            camera.update(player.x + player.W // 2)
        elif player.stun_timer > 0:
            player.stun_timer -= 1
            camera.update(player.x + player.W // 2)
        else:
            player.handle_input(keys_held, bullets, player_rockets, cam_x)

        if run_logic:
            # ── Route special weapon bullets ──
            next_bullets = []
            for b in bullets:
                if isinstance(b, (EMPBullet, FlameBullet)):
                    next_bullets.append(b)
                    continue
                if player.weapon == FLAMMENWERFER:
                    flame_bullets.append(FlameBullet(b.x, b.y, b.vx, b.vy, b.damage))
                elif player.weapon == EMP_CANNON:
                    emp_bullets.append(EMPBullet(b.x, b.y, b.vx, b.vy, b.damage))
                else:
                    next_bullets.append(b)
            bullets = next_bullets
 
        player.update()
        camera.update(player.x + player.W // 2)
        WEATHER.update()
        COMBO.update()
        ACHIEV_NOTIF.update()
        WSTATS.update_notifs()
 
        if player.score >= 10000:
            unlock("score_10k")
 
        # ── Update all enemies ──
        all_targets_for_emp = (enemies + shield_soldiers + snipers +
                                heavy_gunners + mech_walkers + tanks + jetpack_soldiers +
                                air_enemies + kamikaze_drones +
                                ([boss] if boss and boss.alive else []))
 
        ambush_system.check(player.x, enemies, get_diff())
        ambush_system.update()
        DROPSHIP.update(player, enemies, zone_num)
        AIRSTRIKE.update(player, enemy_bullets, zone_num)

        for e in enemies:
            eb = []; e.update(player, eb, enemy_grenades); enemy_bullets.extend(eb)
        for ss2 in shield_soldiers:
            eb = []; ss2.update(player, eb, enemy_grenades); enemy_bullets.extend(eb)
        for sn in snipers:
            eb = []; sn.update(player, eb, enemy_grenades); enemy_bullets.extend(eb)
        for hg in heavy_gunners:
            eb = []; hg.update(player, eb, enemy_grenades); enemy_bullets.extend(eb)
        for mw in mech_walkers:
            mb = []; mr = []
            mw.update(player, mb, mr)
            enemy_bullets.extend(mb)
            enemy_rockets.extend(mr)
        for te in turret_enemies:
            if te.alive:
                tb2 = []
                te.update(player, tb2)
                enemy_bullets.extend(tb2)
        for t in tanks:
            tb = []; t.update(player, tb); enemy_bullets.extend(tb)
        for j in jetpack_soldiers:
            jb = []; j.update(player, jb); enemy_bullets.extend(jb)
        for a in air_enemies:
            ab = []; a.update(player, ab); enemy_bullets.extend(ab)
        for kd in kamikaze_drones:
            if kd.alive: kd.update(player, [])
        for sb in suicide_bombers:
            if sb.alive: sb.update(player, [], [])
        for ss3 in stealth_soldiers:
            if ss3.alive:
                ssb = []; ss3.update(player, ssb, []); enemy_bullets.extend(ssb)
        for ms in mortar_soldiers:
            if ms.alive:
                msb = []; ms.update(player, msb, mortar_shells); enemy_bullets.extend(msb)

        # V7.0 NEW ENEMIES UPDATE
        for sm in sniper_mechs:
            if sm.alive:
                smb=[]; sm.update(player, smb, []); enemy_bullets.extend(smb)
        for rs in riot_soldiers:
            if rs.alive:
                rsb=[]; rs.update(player, rsb, []); enemy_bullets.extend(rsb)
        for ft in flame_troopers:
            if ft.alive:
                ftb=[]; ft.update(player, ftb, []); enemy_bullets.extend(ftb)
        for bj in bomber_jets:
            if bj.alive: bj.update(player, [])
        BASE_BUILD.update(
            enemies+shield_soldiers+snipers+heavy_gunners+mech_walkers+
            sniper_mechs+riot_soldiers+flame_troopers+tanks,
            bullets, player)

        for msh in mortar_shells:
            hits2 = msh.update(player)
            for h in hits2: player.take_damage(h)
        if boss and boss.alive:
            bb = []; boss.update(player, bb, enemy_rockets); enemy_bullets.extend(bb)
 
        # Turrets update
        all_ground_enemies = ([e for e in enemies if e.alive] +
                              [ss2 for ss2 in shield_soldiers if ss2.alive] +
                              [sn for sn in snipers if sn.alive] +
                              [hg for hg in heavy_gunners if hg.alive] +
                              [t for t in tanks if t.alive])
        for turret in player.turrets:
            turret.update(all_ground_enemies, bullets)
 
        all_air = [a for a in air_enemies + jetpack_soldiers + kamikaze_drones if a.alive]
 
        # ── Update projectiles ──
        for b in bullets:        b.update()
        for fb in flame_bullets: fb.update()
        for eb2 in emp_bullets:  eb2.update()
        for r in player_rockets: r.update(all_air)
        for d in drops:          d.update()
 
        # Sniper trails
        for b in bullets:
            if b.alive and b.is_sniper:
                PARTICLES.spawn_sniper_trail(b.x - b.vx*3, b.y - b.vy*3, b.x, b.y)
 
        # ── Kill helper ──
        def do_enemy_kill(e_obj, is_air_type=False, is_tank_type=False, is_boss_type=False):
            nonlocal first_kill_done, tank_killed
            COMBO.kill()
            bonus    = COMBO.score_bonus()
            diff_mult= get_diff()["score_mult"]
 
            if is_boss_type:   pts = int(2000 * diff_mult)
            elif is_tank_type: pts = int(300 * zone_num * diff_mult)
            elif is_air_type:  pts = int(200 * zone_num * diff_mult)
            else:              pts = int(100 * zone_num * bonus * diff_mult)
 
            player.score += pts
            intensity = 120 if is_boss_type else 80 if is_tank_type else 40
            KILL_FLASH.trigger(intensity)
            kill_name = type(e_obj).__name__.replace("Soldier","").replace("Enemy","").replace("Walker","Mech")
            kill_col2 = (255,80,80) if is_boss_type else \
                        (255,160,40) if is_tank_type else \
                        (80,200,255) if is_air_type else (255,215,60)
            KILL_FEED.add(f"✕  {kill_name}  +{pts}", kill_col2)
            DMG_NUMBERS.add(e_obj.rect.centerx, e_obj.rect.top - 10, pts, is_kill=True)
 
            leveled = WSTATS.add_kill(player.weapon.name)
            if leveled:
                SFX.play(SFX.level_up)
                if WSTATS.get_level(player.weapon.name) == 3: unlock("weapon_max")
 
            if not first_kill_done: unlock("first_blood"); first_kill_done = True
            xp_gain = 200 if is_boss_type else 80 if is_tank_type else \
                      50 if is_air_type else 20
            xp_gain = int(xp_gain * get_diff()["score_mult"])
            # Lifesteal
            if SKILLS.lifesteal_pct() > 0:
                heal_amt = max(1, int(pts * SKILLS.lifesteal_pct()))
                player.hp = min(player.MAX_HP, player.hp + heal_amt)
            leveled2 = PROGRESSION.add_xp(xp_gain)
            PROGRESSION.add_kill()
            XP_NOTIF.add_xp(xp_gain, leveled2)
            if is_tank_type and not tank_killed: unlock("tank_killer"); tank_killed = True
            if is_air_type:
                player.air_kills += 1
                if player.air_kills >= 10: unlock("air_ace")
 
            # NEW: drop on kill
            drop = maybe_drop(e_obj.rect.centerx, e_obj.rect.bottom)
            if drop:
                drops.append(drop)
 
        # ══════════════════════════════════════════
        #  HIT DETECTION — regular bullets
        # ══════════════════════════════════════════
        def process_bullet(b):
            if not b.alive: return
            # vs normal enemies
            for e in enemies:
                if not e.alive: continue
                if b.get_rect().colliderect(e.rect):
                    crit = SKILLS.crit_chance() > 0 and random.random() < SKILLS.crit_chance()
                    dmg  = b.damage * (2 if crit else 1)
                    e.take_damage(dmg); b.alive = False
                    DMG_NUMBERS.add(e.rect.centerx, e.rect.top, dmg, is_kill=crit)
                    if not e.alive: do_enemy_kill(e); return
            # vs shield soldiers
            for ss2 in shield_soldiers:
                if not ss2.alive: continue
                if b.get_rect().colliderect(ss2.rect):
                    ss2.take_damage(b.damage); b.alive = False
                    DMG_NUMBERS.add(ss2.rect.centerx, ss2.rect.top, b.damage)
                    if not ss2.alive: do_enemy_kill(ss2); return
            # vs snipers
            for sn in snipers:
                if not sn.alive: continue
                if b.get_rect().colliderect(sn.rect):
                    sn.take_damage(b.damage); b.alive = False
                    DMG_NUMBERS.add(sn.rect.centerx, sn.rect.top, b.damage)
                    if not sn.alive: do_enemy_kill(sn); return
            # vs heavy gunners
            for hg in heavy_gunners:
                if not hg.alive: continue
                if b.get_rect().colliderect(hg.rect):
                    hg.take_damage(b.damage); b.alive = False
                    DMG_NUMBERS.add(hg.rect.centerx, hg.rect.top, b.damage)
                    if not hg.alive: do_enemy_kill(hg); return
            
            for mw in mech_walkers:
                if not mw.alive: continue
                if b.get_rect().colliderect(mw.rect):
                    mw.take_damage(b.damage); b.alive = False
                    DMG_NUMBERS.add(mw.rect.centerx, mw.rect.top, b.damage)
                    if not mw.alive: do_enemy_kill(mw, is_tank_type=True); return

            for te in turret_enemies:
                if not te.alive: continue
                if b.get_rect().colliderect(te.rect):
                    te.take_damage(b.damage, is_rocket=False); b.alive = False
                    DMG_NUMBERS.add(te.rect.centerx, te.rect.top, b.damage)
                    if not te.alive: do_enemy_kill(te, is_tank_type=True); return

            # vs tanks
            for t in tanks:
                if not t.alive: continue
                if b.get_rect().colliderect(t.rect):
                    t.take_damage(b.damage, is_rocket=False); b.alive = False
                    DMG_NUMBERS.add(t.rect.centerx, t.rect.top, b.damage)
                    if not t.alive: do_enemy_kill(t, is_tank_type=True); return
            # vs jetpack
            for j in jetpack_soldiers:
                if not j.alive: continue
                if b.get_rect().colliderect(j.rect):
                    j.take_damage(b.damage); b.alive = False
                    if not j.alive: do_enemy_kill(j, is_air_type=True); return
            # vs air
            for a in air_enemies:
                if not a.alive: continue
                if b.get_rect().colliderect(a.rect):
                    a.take_damage(b.damage); b.alive = False
                    if not a.alive: do_enemy_kill(a, is_air_type=True); return
            # vs kamikaze
            for kd in kamikaze_drones:
                if not kd.alive: continue
                if b.get_rect().colliderect(kd.rect):
                    kd.take_damage(b.damage); b.alive = False
                    if not kd.alive: do_enemy_kill(kd, is_air_type=True); return

            for sb in suicide_bombers:
                if not sb.alive: continue
                if b.get_rect().colliderect(sb.rect):
                    sb.take_damage(b.damage); b.alive = False
                    DMG_NUMBERS.add(sb.rect.centerx,sb.rect.top,b.damage)
                    if not sb.alive: do_enemy_kill(sb); return
            for ss3 in stealth_soldiers:
                if not ss3.alive: continue
                if b.get_rect().colliderect(ss3.rect):
                    ss3.take_damage(b.damage); b.alive = False
                    DMG_NUMBERS.add(ss3.rect.centerx,ss3.rect.top,b.damage)
                    if not ss3.alive: do_enemy_kill(ss3); return
            for ms in mortar_soldiers:
                if not ms.alive: continue
                if b.get_rect().colliderect(ms.rect):
                    ms.take_damage(b.damage); b.alive = False
                    DMG_NUMBERS.add(ms.rect.centerx,ms.rect.top,b.damage)
                    if not ms.alive: do_enemy_kill(ms); return

            for sm in sniper_mechs:
                if not sm.alive: continue
                if b.get_rect().colliderect(sm.rect):
                    sm.take_damage(b.damage, is_rocket=isinstance(b,Rocket))
                    b.alive=False
                    DMG_NUMBERS.add(sm.rect.centerx,sm.rect.top,b.damage)
                    if not sm.alive: do_enemy_kill(sm,is_tank_type=True); return
            for rs in riot_soldiers:
                if not rs.alive: continue
                if b.get_rect().colliderect(rs.rect):
                    rs.take_damage(b.damage)
                    b.alive=False
                    DMG_NUMBERS.add(rs.rect.centerx,rs.rect.top,b.damage)
                    if not rs.alive:
                        do_enemy_kill(rs)
                        if rs.riot_kills>=10: unlock("riot_breaker")
                    return
            for ft in flame_troopers:
                if not ft.alive: continue
                if b.get_rect().colliderect(ft.rect):
                    ft.take_damage(b.damage)
                    b.alive=False
                    DMG_NUMBERS.add(ft.rect.centerx,ft.rect.top,b.damage)
                    if not ft.alive: do_enemy_kill(ft); return
            for bj in bomber_jets:
                if not bj.alive: continue
                if b.get_rect().colliderect(bj.rect):
                    bj.take_damage(b.damage, is_rocket=isinstance(b,Rocket))
                    b.alive=False
                    if not bj.alive: do_enemy_kill(bj,is_air_type=True); return

            # vs boss
            if boss and boss.alive and b.get_rect().colliderect(boss.rect):
                boss.take_damage(b.damage); b.alive = False
                if not boss.alive: do_enemy_kill(boss, is_boss_type=True)

            # Environmental hazard — bullets hitting sandbags already handled above
            # Wall impact sparks
            if b.alive:
                if b.x <= 5 or b.x >= WORLD_WIDTH - 5:
                    b.alive = False
                    PARTICLES.spawn_bullet_impact(b.x, b.y, b.color) 
 
        for b in bullets: process_bullet(b)
 
        # ── Flame bullets hit detection ──
        for fb in flame_bullets:
            if not fb.alive: continue
            for e in (enemies + shield_soldiers + snipers + heavy_gunners):
                if not e.alive: continue
                if fb.get_rect().colliderect(e.rect):
                    e.take_damage(fb.damage)
                    fb.alive = False
                    if not e.alive: do_enemy_kill(e)
                    break
 
        # ── EMP bullets hit detection ──
        for eb2 in emp_bullets:
            if not eb2.alive: continue
            # Trigger on any enemy contact
            for t in (tanks + list(air_enemies)):
                if not t.alive: continue
                if eb2.get_rect().colliderect(t.rect):
                    eb2.trigger_emp(all_targets_for_emp, screen_shake)
                    screen_shake = 10
                    break
            # Also trigger on ground contact (after travel distance)
            if eb2.alive and eb2.y >= GROUND_Y - 10:
                eb2.trigger_emp(all_targets_for_emp, screen_shake)
 
        # ── Kamikaze contact damage ──
        for kd in kamikaze_drones:
            if kd.alive and kd.diving:
                if kd.rect.colliderect(player.rect):
                    player.take_damage(kd.EXPLOSION_DMG)
                    kd._explode()
 
        # ── Rockets ──
        for r in player_rockets:
            if not r.alive: continue
            all_tgts = (enemies + shield_soldiers + snipers + heavy_gunners +
                        tanks + jetpack_soldiers + air_enemies + kamikaze_drones +
                        turret_enemies +
                        ([boss] if boss and boss.alive else []))
            for tgt in all_tgts:
                if not tgt.alive: continue
                if r.get_rect().colliderect(tgt.rect):
                    hits = r.explode(all_tgts)
                    ENV_SYSTEM.take_explosion_damage(r.x, r.y, r.explosion_r, r.damage)
                    screen_shake = 12
                    for (t2, dmg) in hits:
                        if not t2.alive: continue
                        if isinstance(t2, (Tank, Helicopter, Jet)):
                            t2.take_damage(dmg, is_rocket=True)
                        elif isinstance(t2, (ShieldSoldier, HeavyGunner)):
                            t2.take_damage(dmg, is_rocket=True, is_explosion=True)
                        else:
                            t2.take_damage(dmg)
                        if not t2.alive:
                            do_enemy_kill(t2,
                                is_air_type=isinstance(t2, (Helicopter,Jet,JetpackSoldier,Drone,KamikazeDrone)),
                                is_tank_type=isinstance(t2, Tank),
                                is_boss_type=isinstance(t2, Boss))
                    break
 
        # ── Knife ──
        if player.knife_anim > 0:
            kr = player.get_knife_hit_rect()
            for e in enemies + shield_soldiers + snipers + heavy_gunners:
                if e.alive and kr.colliderect(e.rect):
                    e.take_damage(int(MESSER.damage * player.dmg_mult))
                    if not e.alive: do_enemy_kill(e)
 
        # ── Enemy bullets hit player ──
        for b in enemy_bullets:
            b.update()
            if b.alive and b.get_rect().colliderect(player.rect):
                player.take_damage(b.damage)
                b.alive = False
 
        # ── Enemy rockets ──
        for r in enemy_rockets:
            r.update()
            if r.alive and r.get_rect().colliderect(player.rect):
                player.take_damage(60)
                r.alive = False
                screen_shake = 10
 
        # ── Grenades ──
        all_grenade_targets = ([e for e in enemies if e.alive] +
                               [ss2 for ss2 in shield_soldiers if ss2.alive] +
                               [sn for sn in snipers if sn.alive] +
                               [hg for hg in heavy_gunners if hg.alive] +
                               [t for t in tanks if t.alive] +
                               [j for j in jetpack_soldiers if j.alive] +
                               ([boss] if boss and boss.alive else []))
        for g in grenades + enemy_grenades:
            ghits = g.update(all_grenade_targets)
            for (tgt, dmg) in ghits:
                if isinstance(tgt, Tank):
                    tgt.take_damage(dmg, is_rocket=False)
                elif isinstance(tgt, (ShieldSoldier, HeavyGunner)):
                    tgt.take_damage(dmg, is_rocket=False, is_explosion=True)
                else:
                    tgt.take_damage(dmg)
                if not tgt.alive:
                    do_enemy_kill(tgt,
                        is_tank_type=isinstance(tgt, Tank),
                        is_boss_type=isinstance(tgt, Boss))
        for g in enemy_grenades:
            if g.exploded:
                dist = math.hypot(player.rect.centerx - g.x, player.rect.centery - g.y)
                if dist < g.EXPLOSION_R:
                    player.take_damage(int(g.DAMAGE * (1 - dist / g.EXPLOSION_R)))
 
        # ── Power-ups ──
        for pu in powerups:
            pu.update()
            if pu.alive and pu.rect.colliderect(player.rect):
                player.collect_powerup(pu)
 
        # ── Drops ──
        for d in drops:
            if d.alive and d.rect.colliderect(player.rect):
                msg = d.apply(player)
                player.pickup_msg = msg
                player.pickup_msg_timer = 120
 
        # ── Filter dead objects ──
        bullets          = [b  for b  in bullets          if b.alive]
        flame_bullets    = [fb for fb in flame_bullets    if fb.alive]
        emp_bullets      = [eb2 for eb2 in emp_bullets    if eb2.alive]
        enemy_bullets    = [b  for b  in enemy_bullets    if b.alive]
        player_rockets   = [r  for r  in player_rockets   if r.alive]
        enemy_rockets    = [r  for r  in enemy_rockets     if r.alive]
        grenades         = [g  for g  in grenades          if g.alive]
        enemy_grenades   = [g  for g  in enemy_grenades    if g.alive]
        # Kill any enemy that fell out of the world
        for e in enemies:
            if e.y > HEIGHT + 200: e.alive = False
        for ss2 in shield_soldiers:
            if ss2.y > HEIGHT + 200: ss2.alive = False
        for sn in snipers:
            if sn.y > HEIGHT + 200: sn.alive = False
        for hg in heavy_gunners:
            if hg.y > HEIGHT + 200: hg.alive = False
        for mw in mech_walkers:
            if mw.y > HEIGHT + 200: mw.alive = False
        for t in tanks:
            if t.y > HEIGHT + 200: t.alive = False
        for j in jetpack_soldiers:
            if j.y > HEIGHT + 200: j.alive = False

        enemies          = [e  for e  in enemies           if e.alive]
        shield_soldiers  = [ss2 for ss2 in shield_soldiers if ss2.alive]
        snipers          = [sn for sn in snipers            if sn.alive]
        heavy_gunners    = [hg for hg in heavy_gunners      if hg.alive]
        mech_walkers     = [mw for mw in mech_walkers        if mw.alive]
        turret_enemies   = [te for te in turret_enemies       if te.alive]
        kamikaze_drones  = [kd for kd in kamikaze_drones    if kd.alive]
        suicide_bombers  = [sb for sb in suicide_bombers     if sb.alive]
        stealth_soldiers = [ss3 for ss3 in stealth_soldiers  if ss3.alive]
        mortar_soldiers  = [ms for ms in mortar_soldiers      if ms.alive]
        mortar_shells    = [msh for msh in mortar_shells      if msh.alive]
        sniper_mechs     = [sm for sm in sniper_mechs    if sm.alive]
        riot_soldiers    = [rs for rs in riot_soldiers   if rs.alive]
        flame_troopers   = [ft for ft in flame_troopers  if ft.alive]
        bomber_jets      = [bj for bj in bomber_jets     if bj.alive]
        tanks            = [t  for t  in tanks              if t.alive]
        jetpack_soldiers = [j  for j  in jetpack_soldiers   if j.alive]
        air_enemies      = [a  for a  in air_enemies        if a.alive]
        powerups         = [p  for p  in powerups           if p.alive]
        drops            = [d  for d  in drops              if d.alive]
        player.turrets   = [t  for t  in player.turrets     if t.alive]
 
        if not player.alive:
            return "gameover"
 
        # ── Zone clear check ──
        all_dead = (not enemies and not shield_soldiers and not snipers and
                    not heavy_gunners and not mech_walkers and not kamikaze_drones and
                    not tanks and not jetpack_soldiers and not air_enemies and
                    not suicide_bombers and not stealth_soldiers and not mortar_soldiers and
                    not sniper_mechs and not riot_soldiers and
                    not flame_troopers and not bomber_jets)
 
        if all_dead:
            unlock(f"zone_{zone_num}")
            PROGRESSION.add_zone()
            zone_xp = zone_num * 300
            lev3 = PROGRESSION.add_xp(zone_xp)
            XP_NOTIF.add_xp(zone_xp, lev3)
            if player.zone_damage_taken == 0: unlock("no_damage")
            if player.knife_only_zone:        unlock("knife_only")
            if zone_num == NUM_ZONES:         unlock("all_zones")
            if current_difficulty == "hard" and zone_num == NUM_ZONES: unlock("hard_clear")
            if is_boss_zone:
                if boss is None or not boss.alive:
                    SFX.play(SFX.zone_clear)
                    return "win"
            else:
                SFX.play(SFX.zone_clear)
            ZONE_CLEAR_FX.trigger()
            player.score += int(300 * zone_num * get_diff()["score_mult"])
            for _ in range(160):
                clock.tick(FPS)
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                ZONE_CLEAR_FX.update()
                clear_surf = pygame.Surface((WIDTH, HEIGHT))
                draw_world(clear_surf, cfg, cam_x, tick)
                player.draw(clear_surf, cam_x)
                screen.fill(DARK)
                screen.blit(clear_surf, (0, 0))
                ZONE_CLEAR_FX.draw(screen)
                pygame.display.flip()
            return "next_zone"
 
        # ══════════════════════════════════════════
        #  DRAWING
        # ══════════════════════════════════════════
        ox2, oy2 = get_shake_offset()
        game_surf = pygame.Surface((WIDTH, HEIGHT))
        draw_world(game_surf, cfg, cam_x, tick)
 
        # Power-ups & drops
        for pu in powerups:
            pu.draw(game_surf, cam_x)
            if pu.alive:
                cfg2 = PowerUp.TYPES[pu.kind]
                LIGHTS.add(pu.x, pu.y, 40, cfg2["color"], 0.3, life=1)
        for d in drops:
            d.draw(game_surf, cam_x)

        ENV_SYSTEM.update()
        ENV_SYSTEM.draw(game_surf, cam_x)
        ENV_SYSTEM.take_bullet_damage(bullets, enemy_bullets)
        PARTICLES.update()
        PARTICLES.draw(game_surf, cam_x)
        LIGHTS.draw(game_surf, cam_x)
 
        # Projectiles
        for g in grenades + enemy_grenades: g.draw(game_surf, cam_x)
        for r in player_rockets + enemy_rockets: r.draw(game_surf, cam_x)
        for fb in flame_bullets: fb.draw(game_surf, cam_x)
        for eb2 in emp_bullets:  eb2.draw(game_surf, cam_x)
 
        for b in bullets + enemy_bullets:
            b.draw(game_surf, cam_x)
            if b.alive and random.random() < 0.25:
                LIGHTS.add(b.x, b.y, 22, b.color, 0.5, life=1)
 
        # Enemies
        for e in enemies:
            if camera.in_view(e.x): e.draw(game_surf, cam_x)
        for ss2 in shield_soldiers:
            if camera.in_view(ss2.x): ss2.draw(game_surf, cam_x)
        for sn in snipers:
            if camera.in_view(sn.x): sn.draw(game_surf, cam_x)
        for hg in heavy_gunners:
            if camera.in_view(hg.x): hg.draw(game_surf, cam_x)
        for mw in mech_walkers:
            if camera.in_view(mw.x): mw.draw(game_surf, cam_x)
        for te in turret_enemies:
            if camera.in_view(te.x): te.draw(game_surf, cam_x)
        for t in tanks:
            if camera.in_view(t.x): t.draw(game_surf, cam_x)
        for j in jetpack_soldiers:
            if camera.in_view(j.x): j.draw(game_surf, cam_x)
        for a in air_enemies:
            if camera.in_view(a.x): a.draw(game_surf, cam_x)
        for kd in kamikaze_drones:
            if camera.in_view(kd.x): kd.draw(game_surf, cam_x)
        for sb in suicide_bombers:
            if camera.in_view(sb.x): sb.draw(game_surf, cam_x)
        for ss3 in stealth_soldiers:
            if camera.in_view(ss3.x): ss3.draw(game_surf, cam_x)
        for ms in mortar_soldiers:
            if camera.in_view(ms.x): ms.draw(game_surf, cam_x)
        for msh in mortar_shells:
            msh.draw(game_surf, cam_x)
        for sm in sniper_mechs:
            if camera.in_view(sm.x): sm.draw(game_surf, cam_x)
        for rs in riot_soldiers:
            if camera.in_view(rs.x): rs.draw(game_surf, cam_x)
        for ft in flame_troopers:
            if camera.in_view(ft.x): ft.draw(game_surf, cam_x)
        for bj in bomber_jets:
            if camera.in_view(bj.x): bj.draw(game_surf, cam_x)
        if boss and boss.alive and camera.in_view(boss.x):
            boss.draw(game_surf, cam_x)
 
        # Turrets
        for turret in player.turrets:
            if camera.in_view(turret.x): turret.draw(game_surf, cam_x)

        for sb in player.sandbags:
            sb.draw(game_surf, cam_x)

        # Sandbag bullet blocking
        for sb in player.sandbags:
            if not sb.alive: continue
            for b in bullets + enemy_bullets:
                if b.alive and b.get_rect().colliderect(sb.rect):
                    sb.take_damage(b.damage); b.alive = False
            for r in player_rockets + enemy_rockets:
                if r.alive and r.get_rect().colliderect(sb.rect):
                    sb.take_damage(50, is_rocket=True); r.alive = False

        player.sandbags = [s for s in player.sandbags if s.alive]
 
        # Ambient zone particles
        if tick % 8 == 0:
            zn2 = zone_num
            if zn2 == 1:   # City — floating ash
                PARTICLES.spawn_smoke(random.randint(0, WIDTH) + cam_x,
                                      random.randint(GROUND_Y-300, GROUND_Y-50))
            elif zn2 == 2: # Forest — fireflies
                PARTICLES.spawn_neon_spark(
                    random.randint(0, WIDTH) + cam_x,
                    random.randint(GROUND_Y-200, GROUND_Y-40),
                    (80, 255, 120))
            elif zn2 == 3: # Desert — dust
                PARTICLES.spawn_dust(random.randint(0, WIDTH) + cam_x, GROUND_Y-10)
            elif zn2 == 5: # Arctic — ice crystals
                PARTICLES.spawn_ice_crystal(
                    random.randint(0, WIDTH) + cam_x,
                    random.randint(GROUND_Y-180, GROUND_Y-20))
            elif zn2 == 6: # Omega — embers
                PARTICLES.spawn_ember(
                    random.randint(0, WIDTH) + cam_x,
                    random.randint(GROUND_Y-100, GROUND_Y-10))
        

        BASE_BUILD.draw(game_surf, cam_x)
        # Player
        player.draw(game_surf, cam_x)
        player.draw_grapple(game_surf, cam_x)
        if player.shield_timer > 0:
            LIGHTS.add(player.rect.centerx, player.rect.centery, 60, (80,160,255), 0.4, life=1)
        if player.dmg_boost_timer > 0:
            LIGHTS.add(player.rect.centerx, player.rect.centery, 50, (255,120,20), 0.35, life=1)
 
        # Stun overlay
        if player.stun_timer > 0:
            stun_s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            stun_s.fill((200, 200, 50, 30))
            game_surf.blit(stun_s, (0, 0))
 
        DMG_NUMBERS.update()
        DMG_NUMBERS.draw(game_surf, cam_x)
        WEATHER.draw_front(game_surf)
 
        screen.fill(DARK)
        LIGHTS.draw_ambient(game_surf, zone_num)
        LIGHTS.draw_volumetric_fog(game_surf, zone_num, cam_x, tick)
        screen.blit(game_surf, (ox2, oy2))
        KILL_FLASH.update(); KILL_FLASH.draw(screen)
        draw_vignette(screen, player)
        ZONE_CLEAR_FX.update(); ZONE_CLEAR_FX.draw(screen)
 
        # HUD
        el = (len(enemies) + len(shield_soldiers) + len(snipers) +
              len(heavy_gunners) + len(tanks) + len(jetpack_soldiers) +
              len(sniper_mechs) + len(riot_soldiers) + len(flame_troopers))
        al = (len(air_enemies) + len(kamikaze_drones) + len(bomber_jets) +
              (1 if boss and boss.alive and is_boss_zone else 0))
        BASE_BUILD.draw_hud(screen, player, BASE_BUILD.build_mode)
        # Build mode hint
        if BASE_BUILD.build_mode:
            bm_hint = font_tiny.render("[F] Platzieren  [B] Baumodus aus", True, (80,200,80))
            screen.blit(bm_hint,(WIDTH//2-bm_hint.get_width()//2, HEIGHT-36))
        else:
            bm_hint2 = font_tiny.render("[B] Baumodus", True, (40,100,40))
            screen.blit(bm_hint2,(12, HEIGHT-36))
        MINIMAP.draw(screen, player, enemies + shield_soldiers + snipers + heavy_gunners,
                     tanks, air_enemies + kamikaze_drones, jetpack_soldiers, boss, powerups, cam_x)
        COMBO.draw(screen)
        # Score streak ring
        if COMBO.count >= 3:
            ring_a3 = int(40 + abs(math.sin(pygame.time.get_ticks()*0.012))*60)
            ring_r3 = 44 + COMBO.count * 3
            rs3     = pygame.Surface((ring_r3*2+4, ring_r3*2+4), pygame.SRCALPHA)
            ring_col3 = (255,80,80) if COMBO.count>=10 else \
                        (255,165,30) if COMBO.count>=5 else (255,220,60)
            pygame.draw.circle(rs3,(*ring_col3,ring_a3),(ring_r3+2,ring_r3+2),ring_r3,3)
            px3 = player.rect.centerx - cam_x
            py3 = player.rect.centery
            screen.blit(rs3,(px3-ring_r3-2+ox2, py3-ring_r3-2+oy2))
        WSTATS.draw_notifs(screen)
        ACHIEV_NOTIF.draw(screen)
        KILL_FEED.update(); KILL_FEED.draw(screen)
        XP_NOTIF.update(); XP_NOTIF.draw(screen)
        ambush_system.draw(screen)
        AIRSTRIKE.draw(screen, cam_x)
        DROPSHIP.draw(game_surf, cam_x)
        WEAPON_WHEEL.draw(screen, player)
 
        # Turret counter HUD
        active_turrets = len([t for t in player.turrets if t.alive])
        tf2 = pygame.font.SysFont("consolas", 12, bold=True)
        tt  = tf2.render(f"[T] TURRETS: {active_turrets}/2", True,
                         GREEN if active_turrets > 0 else GRAY)
        screen.blit(tt, (WIDTH // 2 - tt.get_width() // 2, HEIGHT - 36))
 
        ctrl = font_tiny.render(
            "WASD:Bewegen  SPACE:Springen  Klick:Schiessen  G:Granate  T:Geschütz  Q:Waffenrad  ESC:Pause",
            True, (90, 90, 110))
        screen.blit(ctrl, (WIDTH // 2 - ctrl.get_width() // 2, HEIGHT - 20))

        if SETTINGS.get("show_fps", False):
            fps_font = pygame.font.SysFont("consolas", 14, bold=True)
            fps_text = fps_font.render(f"FPS: {int(clock.get_fps())}", True, (0, 255, 100))
            screen.blit(fps_text, (WIDTH - fps_text.get_width() - 8, 8))

        pygame.display.flip()

# ═══════════════════════════════════════════════════
#  VICTORY CUTSCENE — polished jet escape to space
# ═══════════════════════════════════════════════════
def show_victory_cutscene():
    """
    5-Act victory sequence:
    Act 1 (0-180)   – Victory fanfare, cheering troops, confetti
    Act 2 (180-380) – Player walks to jet, boards, countdown
    Act 3 (380-620) – Jet blasts off through clouds and atmosphere
    Act 4 (620-900) – Space, Earth receding, stars, aurora
    Act 5 (900-1000)– Credits roll, fade to black
    """
    clock_vic = pygame.time.Clock()
    tick      = 0

    # ── Pre-generate static assets ──────────────────────────────────────────
    stars_vic = [(random.randint(0,WIDTH), random.randint(0,HEIGHT),
                  random.uniform(0.8,2.8), random.uniform(0,6.28))
                 for _ in range(280)]

    confetti = [{"x": float(random.randint(0,WIDTH)),
                 "y": float(random.randint(-400,0)),
                 "vx": random.uniform(-3,3),
                 "vy": random.uniform(1.5,6),
                 "col": random.choice([
                     (255,215,50),(50,220,80),(55,180,255),
                     (255,80,80),(210,80,255),(255,255,255),
                     (255,160,30),(50,255,220),(255,120,180)]),
                 "sz": random.randint(5,14),
                 "rot": random.uniform(0,360),
                 "rs": random.uniform(-14,14)}
                for _ in range(180)]

    fireworks = []

    # Jet state
    jet_x = float(WIDTH*0.65); jet_y = float(HEIGHT-118)
    jet_vx = 0.0;              jet_vy = 0.0
    jet_angle_deg = 0.0
    jet_scale  = 1.3
    jet_trail  = []   # list of (x,y,age) for smoke trail

    # Player walk state
    pl_x = 80.0; pl_y = float(HEIGHT - 90)
    pl_boarded = False

    # Crowd soldiers
    crowd_left  = [60+i*62  for i in range(6)]
    crowd_right = [WIDTH-60-i*62 for i in range(6)]

    # Ground explosion/firework spawner
    ground_fireworks = []

    f_ultra  = pygame.font.SysFont("consolas", 75, bold=True)
    f_huge2  = pygame.font.SysFont("consolas", 48, bold=True)
    f_big2   = pygame.font.SysFont("consolas", 30, bold=True)
    f_med2   = pygame.font.SysFont("consolas", 20, bold=True)
    f_small2 = pygame.font.SysFont("consolas", 15)
    f_tiny2  = pygame.font.SysFont("consolas", 12)

    def get_act2():
        if tick < 180: return 1
        if tick < 380: return 2
        if tick < 620: return 3
        if tick < 900: return 4
        return 5

    # ── Drawing helpers ──────────────────────────────────────────────────────
    def draw_sky_gradient(surf2, top2, bot2):
        for sy4 in range(0, HEIGHT, 4):
            t6 = sy4/HEIGHT
            r6 = int(top2[0]+(bot2[0]-top2[0])*t6)
            g6 = int(top2[1]+(bot2[1]-top2[1])*t6)
            b6 = int(top2[2]+(bot2[2]-top2[2])*t6)
            pygame.draw.rect(surf2,(r6,g6,b6),(0,sy4,WIDTH,4))

    def draw_crowd_soldier(surf2, sx5, sy5, frame, facing5=1):
        arm_lift2 = int(math.sin(frame*0.28)*22)
        col5 = (48,82,44)
        # Boots
        pygame.draw.rect(surf2,(22,16,10),(sx5-6,sy5+45,10,9),border_radius=2)
        pygame.draw.rect(surf2,(22,16,10),(sx5+2, sy5+45,10,9),border_radius=2)
        # Legs
        pygame.draw.line(surf2,col5,(sx5-5,sy5+28),(sx5-6,sy5+45),6)
        pygame.draw.line(surf2,col5,(sx5+5,sy5+28),(sx5+6,sy5+45),6)
        # Belt
        pygame.draw.rect(surf2,(28,22,12),(sx5-9,sy5+27,18,4))
        # Body
        pygame.draw.rect(surf2,col5,(sx5-9,sy5+10,18,20),border_radius=2)
        pygame.draw.rect(surf2,(62,98,56),(sx5-9,sy5+10,18,5),border_radius=2)
        # Arms raised in celebration
        pygame.draw.line(surf2,col5,(sx5-9,sy5+14),
                         (sx5-26,sy5+2-arm_lift2),5)
        pygame.draw.line(surf2,col5,(sx5+9,sy5+14),
                         (sx5+26,sy5+2-arm_lift2),5)
        # Rifle pointing up
        pygame.draw.line(surf2,(38,38,38),
                         (sx5+26,sy5+2-arm_lift2),
                         (sx5+26,sy5-28-arm_lift2),3)
        # Head
        pygame.draw.circle(surf2,(182,134,92),(sx5,sy5+2),11)
        # Helmet
        pygame.draw.arc(surf2,(44,60,38),
                        pygame.Rect(sx5-13,sy5-12,26,20),0,math.pi,0)
        pygame.draw.rect(surf2,(44,60,38),(sx5-13,sy5+2,26,8))
        pygame.draw.arc(surf2,(62,84,54),
                        pygame.Rect(sx5-10,sy5-10,12,12),0.4,math.pi-0.4,2)
        # Cheer exclamation
        if (frame+int(sx5*0.1))%28 < 14:
            cf3 = pygame.font.SysFont("consolas",9,bold=True)
            ct4 = cf3.render("!", True,(255,215,50))
            surf2.blit(ct4,(sx5-3,sy5-30-arm_lift2))

    def draw_player_hero(surf2, px5, py5, frame):
        skin = SKINS[current_skin]
        lo3  = int(math.sin(frame*0.35)*9)
        cx6  = int(px5); cy6 = int(py5)
        # Boots
        pygame.draw.rect(surf2,skin.get("boot",(22,18,12)),
                         (cx6-9,cy6+44,10,9),border_radius=2)
        pygame.draw.rect(surf2,skin.get("boot",(22,18,12)),
                         (cx6+1, cy6+44+lo3,10,9),border_radius=2)
        # Legs
        pygame.draw.rect(surf2,skin["body"],(cx6-9,cy6+28,9,17),border_radius=2)
        pygame.draw.rect(surf2,skin["body"],(cx6+1, cy6+28+lo3,9,17),border_radius=2)
        pygame.draw.rect(surf2,(28,22,12),(cx6-10,cy6+27,20,4))
        # Vest
        vest2  = skin["vest"]
        vest2_hi = tuple(min(255,c+22) for c in vest2)
        pygame.draw.rect(surf2,vest2,(cx6-11,cy6+12,22,18),border_radius=3)
        pygame.draw.rect(surf2,vest2_hi,(cx6-11,cy6+12,22,5),border_radius=3)
        pygame.draw.rect(surf2,tuple(max(0,c-18) for c in vest2),
                         (cx6-8,cy6+14,16,14),border_radius=2)
        # Arms
        pygame.draw.line(surf2,vest2,(cx6-10,cy6+14),(cx6-20,cy6+28),5)
        pygame.draw.line(surf2,vest2,(cx6+10,cy6+14),(cx6+20,cy6+26),5)
        # Head
        pygame.draw.circle(surf2,skin["head"],(cx6,cy6+3),10)
        pygame.draw.circle(surf2,
                           tuple(max(0,c-22) for c in skin["head"]),(cx6+3,cy6+4),5)
        # Helmet
        pygame.draw.arc(surf2,skin["helmet"],
                        pygame.Rect(cx6-12,cy6-8,24,18),0,math.pi,0)
        pygame.draw.rect(surf2,skin["helmet"],(cx6-12,cy6+2,24,8))
        # Gun (slung on back)
        pygame.draw.rect(surf2,(38,38,38),(cx6+12,cy6+16,18,5))

    def draw_jet_detailed(surf2, jx6, jy6, ang6=0.0, sc6=1.0, exhaust6=True):
        cos6 = math.cos(ang6); sin6 = math.sin(ang6)
        def rp(px6,py6):
            rx4 = (px6-jx6)*cos6-(py6-jy6)*sin6+jx6
            ry4 = (px6-jx6)*sin6+(py6-jy6)*cos6+jy6
            return (int(rx4),int(ry4))
        s6 = sc6
        # Afterburner
        if exhaust6:
            nozzle6 = rp(jx6-72*s6, jy6+8*s6)
            for fi3 in range(8):
                t7 = fi3/7
                fl4 = int((20+(1-t7)*40)*s6) + random.randint(0,int(14*s6))
                fc3 = [(255,248,80),(255,195,30),(255,120,10),(220,60,8),
                       (160,35,5),(100,20,2),(50,10,0),(20,5,0)][fi3]
                fr4 = max(1,int((9-fi3)*s6))
                ep2 = rp(jx6-(72+fi3*fl4//7)*s6, jy6+8*s6)
                fs4 = pygame.Surface((fr4*2+2,fr4*2+2),pygame.SRCALPHA)
                pygame.draw.circle(fs4,(*fc3,220-fi3*22),(fr4+1,fr4+1),fr4)
                surf2.blit(fs4,(ep2[0]-fr4-1,ep2[1]-fr4-1))
            # Second smaller nozzle (vectored thrust)
            ep3 = rp(jx6-68*s6, jy6+14*s6)
            for fi4 in range(5):
                fl5 = int((10+(4-fi4)*8)*s6)
                fc4 = [(255,200,50),(255,130,15),(220,70,10),(160,40,5),(80,15,2)][fi4]
                fr5 = max(1,int((5-fi4)*s6))
                ep4 = rp(jx6-(68+fi4*fl5//5)*s6, jy6+14*s6)
                fs5 = pygame.Surface((fr5*2+2,fr5*2+2),pygame.SRCALPHA)
                pygame.draw.circle(fs5,(*fc4,200-fi4*35),(fr5+1,fr5+1),fr5)
                surf2.blit(fs5,(ep4[0]-fr5-1,ep4[1]-fr5-1))

        # Wings (large delta)
        lw2  = [rp(jx6-8*s6, jy6+8*s6),  rp(jx6-55*s6,jy6+42*s6),
                rp(jx6+18*s6,jy6+42*s6), rp(jx6+24*s6,jy6+14*s6)]
        rw2  = [rp(jx6-8*s6, jy6+8*s6),  rp(jx6-55*s6,jy6-28*s6),
                rp(jx6+18*s6,jy6-28*s6), rp(jx6+24*s6,jy6+2*s6)]
        pygame.draw.polygon(surf2,(52,68,86),lw2)
        pygame.draw.polygon(surf2,(52,68,86),rw2)
        # Wing leading edge highlight
        pygame.draw.line(surf2,(80,105,130),lw2[0],lw2[1],2)
        pygame.draw.line(surf2,(80,105,130),rw2[0],rw2[1],2)
        # Wing tip lights
        pygame.draw.circle(surf2,(255,30,30),lw2[1],int(4*s6))
        pygame.draw.circle(surf2,(30,255,80),rw2[1],int(4*s6))

        # Fuselage
        body2 = [rp(jx6-68*s6,jy6+10*s6), rp(jx6-38*s6,jy6-10*s6),
                 rp(jx6+52*s6,jy6-10*s6), rp(jx6+94*s6,jy6+2*s6),
                 rp(jx6+52*s6,jy6+16*s6), rp(jx6-38*s6,jy6+18*s6)]
        pygame.draw.polygon(surf2,(62,82,105),body2)
        # Top stripe
        stripe2 = [rp(jx6-60*s6,jy6+2*s6),  rp(jx6-38*s6,jy6-8*s6),
                   rp(jx6+52*s6,jy6-8*s6),  rp(jx6+52*s6,jy6-4*s6),
                   rp(jx6-38*s6,jy6-4*s6),  rp(jx6-60*s6,jy6+6*s6)]
        pygame.draw.polygon(surf2,(75,98,122),stripe2)
        # Fuselage outline
        pygame.draw.polygon(surf2,(85,110,138),body2,1)
        # Speed lines on body
        for sl2 in range(3):
            sp6 = rp(jx6+(sl2*16-10)*s6, jy6-2*s6)
            ep5 = rp(jx6+(sl2*16-24)*s6, jy6-2*s6)
            pygame.draw.line(surf2,(100,130,158),sp6,ep5,1)

        # Cockpit
        cp2 = [rp(jx6+8*s6, jy6-10*s6),  rp(jx6+38*s6,jy6-16*s6),
               rp(jx6+58*s6,jy6-10*s6),  rp(jx6+42*s6,jy6+4*s6),
               rp(jx6+12*s6,jy6+4*s6)]
        pygame.draw.polygon(surf2,(68,182,222),cp2)
        pygame.draw.polygon(surf2,(95,215,250),cp2,1)
        # Canopy frame
        mid_cp = rp(jx6+33*s6,jy6-6*s6)
        pygame.draw.line(surf2,(50,140,175),cp2[0],cp2[4],1)
        pygame.draw.line(surf2,(50,140,175),mid_cp,cp2[3],1)
        # Glint
        gl4 = [rp(jx6+12*s6,jy6-12*s6),rp(jx6+28*s6,jy6-16*s6),
               rp(jx6+32*s6,jy6-14*s6),rp(jx6+18*s6,jy6-11*s6)]
        pygame.draw.polygon(surf2,(180,235,255,160),gl4) if len(gl4)==4 else None

        # Tail fins
        tf_v = [rp(jx6-58*s6,jy6+8*s6),rp(jx6-72*s6,jy6-16*s6),
                rp(jx6-40*s6,jy6+8*s6)]
        tf_h1 = [rp(jx6-58*s6,jy6+8*s6),rp(jx6-72*s6,jy6+32*s6),
                 rp(jx6-42*s6,jy6+16*s6)]
        tf_h2 = [rp(jx6-58*s6,jy6+8*s6),rp(jx6-72*s6,jy6-12*s6),
                 rp(jx6-42*s6,jy6+4*s6)]
        pygame.draw.polygon(surf2,(48,62,80),tf_v)
        pygame.draw.polygon(surf2,(48,62,80),tf_h1)
        pygame.draw.polygon(surf2,(48,62,80),tf_h2)

        # Missiles under wings
        for msl_off, msl_y_off in [(-30*s6,28*s6),(4*s6,28*s6),
                                    (-30*s6,-22*s6),(4*s6,-22*s6)]:
            mp1 = rp(jx6+msl_off,     jy6+msl_y_off)
            mp2 = rp(jx6+msl_off-22*s6,jy6+msl_y_off)
            pygame.draw.line(surf2,(155,70,18),mp1,mp2,int(4*s6))
            pygame.draw.circle(surf2,(200,100,30),mp1,int(3*s6))

        # Nose pitot tube
        nose6 = rp(jx6+100*s6,jy6+2*s6)
        nbase6= rp(jx6+90*s6, jy6+2*s6)
        pygame.draw.line(surf2,(100,120,140),nbase6,nose6,2)

    done2 = False
    while not done2 and tick < 1050:
        tick += 1
        clock_vic.tick(FPS)
        act2 = get_act2()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN,pygame.K_SPACE,pygame.K_ESCAPE):
                    done2 = True

        # ── Update confetti ─────────────────────────────────────────────────
        for c in confetti:
            c["x"]+=c["vx"]; c["y"]+=c["vy"]
            c["vy"]+=0.06;   c["rot"]+=c["rs"]
            if c["y"]>HEIGHT+30:
                c["y"]=float(random.randint(-180,-5))
                c["x"]=float(random.randint(0,WIDTH))
                c["vy"]=random.uniform(1.5,5)

        # ── Update fireworks ────────────────────────────────────────────────
        if act2==1 and tick%22==0:
            fx5=random.randint(60,WIDTH-60); fy5=random.randint(50,HEIGHT//2-40)
            col6 = random.choice([(255,215,50),(50,220,80),(60,175,255),
                                   (255,80,80),(215,75,255),(255,255,200)])
            for _ in range(44):
                ang5=random.uniform(0,6.28); sp5=random.uniform(2,14)
                fireworks.append({"x":float(fx5),"y":float(fy5),
                                   "vx":math.cos(ang5)*sp5,"vy":math.sin(ang5)*sp5,
                                   "life":random.randint(28,60),"max_life":60,"col":col6})
            SFX.play(SFX.explosion)
        if act2==2 and tick%45==0:
            gx5=random.randint(100,WIDTH-100)
            ground_fireworks.append({"x":float(gx5),"y":float(HEIGHT-88),"timer":0})

        for fw in fireworks:
            fw["x"]+=fw["vx"]; fw["y"]+=fw["vy"]
            fw["vy"]+=0.10; fw["vx"]*=0.95; fw["life"]-=1
        fireworks=[fw for fw in fireworks if fw["life"]>0]

        for gfw in ground_fireworks:
            gfw["timer"]+=1
            if gfw["timer"]%6==0:
                ang6b=random.uniform(-math.pi,-0.2)
                sp6b=random.uniform(4,12)
                fireworks.append({"x":gfw["x"],"y":gfw["y"],
                                   "vx":math.cos(ang6b)*sp6b,
                                   "vy":math.sin(ang6b)*sp6b,
                                   "life":random.randint(22,48),"max_life":48,
                                   "col":random.choice([(255,215,50),(255,80,80),(50,200,255)])})
        ground_fireworks=[gfw for gfw in ground_fireworks if gfw["timer"]<80]

        # ── Act 2: player walk ──────────────────────────────────────────────
        if act2==2 and not pl_boarded:
            pl_x+=3.8
            if pl_x >= jet_x-38:
                pl_boarded=True

        # ── Act 3: jet launch ───────────────────────────────────────────────
        if act2>=3:
            if act2==3 and tick==380: SFX.play(SFX.shoot_rocket)
            jet_vy -= 0.55
            jet_vx += 0.18
            jet_angle_deg = max(-50.0, jet_angle_deg-0.75)
            jet_x += jet_vx; jet_y += jet_vy
            # Jet trail
            if tick%2==0:
                jet_trail.append({"x":jet_x, "y":jet_y,
                                   "age":0,
                                   "col":(180+random.randint(-30,30),
                                          80+random.randint(-20,20),
                                          20+random.randint(-10,10))})
            for tr in jet_trail: tr["age"]+=1
            jet_trail=[tr for tr in jet_trail if tr["age"]<40]

        # ══════════════════════════════════════════════════════════════════════
        #  DRAW
        # ══════════════════════════════════════════════════════════════════════
        screen.fill((3,5,12))

        # ── Sky gradient ────────────────────────────────────────────────────
        if act2<=2:
            sky_top2=(22,38,70); sky_bot2=(80,135,200)
        elif act2==3:
            t_a3  = max(0,min(1,(tick-380)/220))
            sky_top2=(int(22+t_a3*(2-22)),int(38+t_a3*(1-38)),int(70+t_a3*(12-70)))
            sky_bot2=(int(80+t_a3*(8-80)),int(135+t_a3*(4-135)),int(200+t_a3*(22-200)))
        else:
            sky_top2=(2,1,8); sky_bot2=(5,3,14)
        draw_sky_gradient(screen, sky_top2, sky_bot2)

        # ── Stars ───────────────────────────────────────────────────────────
        star_fade2 = max(0,min(255,int((tick-400)*2.5)))
        if star_fade2>0:
            for sx6,sy5,sr3,sph2 in stars_vic:
                tw3=abs(math.sin(tick*0.032+sph2))
                sa6=int(star_fade2*(0.4+0.6*tw3))
                if sa6<5: continue
                r_s=max(1,int(sr3*(0.8+0.2*tw3)))
                ss4=pygame.Surface((r_s*2+2,r_s*2+2),pygame.SRCALPHA)
                pygame.draw.circle(ss4,(215,228,255,sa6),(r_s+1,r_s+1),r_s)
                screen.blit(ss4,(int(sx6)-r_s,int(sy5)-r_s))

        # Aurora (act 4)
        if act2==4:
            aurora_cols3=[(45,210,95),(80,70,220),(50,188,188),(120,50,210)]
            t_au=max(0,min(1,(tick-620)/260))
            for i_au,ac3 in enumerate(aurora_cols3):
                au_a=int(t_au*(20+math.sin(tick*0.018+i_au*1.4)*12))
                if au_a<=0: continue
                for strip2 in range(7):
                    sx7=int(i_au*200+strip2*50+math.sin(tick*0.01+strip2)*60)-200
                    aw3=62+strip2*10
                    ah3=int(HEIGHT//3+math.sin(tick*0.012+strip2)*50)
                    aus=pygame.Surface((aw3,ah3),pygame.SRCALPHA)
                    pygame.draw.ellipse(aus,(*ac3,au_a),(0,0,aw3,ah3))
                    screen.blit(aus,(sx7,14+strip2*8))

        # ── Clouds (act 3) ──────────────────────────────────────────────────
        if act2==3:
            t_cl2=max(0,min(1,(tick-380)/200))
            cloud_defs=[(WIDTH*0.15,HEIGHT*0.32,95),(WIDTH*0.50,HEIGHT*0.25,115),
                        (WIDTH*0.78,HEIGHT*0.40,80),(WIDTH*0.08,HEIGHT*0.52,65),
                        (WIDTH*0.90,HEIGHT*0.58,70)]
            for cx7,cy7,cr3 in cloud_defs:
                cloud_y2=cy7+t_cl2*HEIGHT*0.85
                if cloud_y2>HEIGHT+cr3: continue
                ca3=int(max(0,min(190,(1-t_cl2)*190)))
                for b_off,(bx7,by7,br3) in enumerate([(-cr3*0.5,0,cr3*0.65),
                                                       (0,-cr3*0.3,cr3*0.85),
                                                       (cr3*0.5,0,cr3*0.62)]):
                    bxf=int(cx7+bx7); byf=int(cloud_y2+by7); brf=max(1,int(br3))
                    cs5=pygame.Surface((brf*2+2,brf*2+2),pygame.SRCALPHA)
                    pygame.draw.circle(cs5,(232,242,255,ca3),(brf+1,brf+1),brf)
                    screen.blit(cs5,(bxf-brf-1,byf-brf-1))

        # ── Earth (act 4) ────────────────────────────────────────────────────
        if act2==4:
            t_sp2=max(0,min(1,(tick-620)/260))
            er3=max(1,int(240*(1-t_sp2*0.58)))
            ey3=int(HEIGHT*0.74+t_sp2*HEIGHT*0.22)
            # Atmosphere
            atm3=pygame.Surface((er3*2+60,er3*2+60),pygame.SRCALPHA)
            pygame.draw.circle(atm3,(75,135,255,32),(er3+30,er3+30),er3+28)
            pygame.draw.circle(atm3,(120,180,255,18),(er3+30,er3+30),er3+50)
            screen.blit(atm3,(WIDTH//2-er3-30,ey3-er3-30))
            # Ocean
            es5=pygame.Surface((er3*2+4,er3*2+4),pygame.SRCALPHA)
            pygame.draw.circle(es5,(30,95,200,235),(er3+2,er3+2),er3)
            # Land
            for lm2_off,lm2_w,lm2_h in [(-38,58,44),(20,40,30),(-8,24,55),(30,18,22)]:
                if lm2_w>0 and lm2_h>0:
                    pygame.draw.ellipse(es5,(40,148,52,225),
                                        (er3+2+lm2_off,er3+2-lm2_h//2,lm2_w,lm2_h))
            # Ice caps
            pygame.draw.ellipse(es5,(230,242,255,200),(er3-30,er3-er3+5,60,20))
            pygame.draw.ellipse(es5,(230,242,255,200),(er3-25,er3+er3-20,50,18))
            # Cloud bands
            pygame.draw.ellipse(es5,(225,235,255,100),(er3-55,er3-8,110,20))
            pygame.draw.ellipse(es5,(225,235,255,80), (er3+10,er3+28,80,14))
            screen.blit(es5,(WIDTH//2-er3-2,ey3-er3-2))
            # Terminator line shadow
            shad3=pygame.Surface((er3*2+4,er3*2+4),pygame.SRCALPHA)
            pygame.draw.circle(shad3,(0,0,30,90),(er3+2+er3//3,er3+2),er3)
            screen.blit(shad3,(WIDTH//2-er3-2,ey3-er3-2))

        # ── Ground + runway (acts 1-2) ───────────────────────────────────────
        if act2<=2:
            gy5=HEIGHT-88
            # Grass
            pygame.draw.rect(screen,(25,55,20),(0,gy5,WIDTH,88))
            pygame.draw.rect(screen,(35,72,28),(0,gy5,WIDTH,8))
            # Concrete pad
            pygame.draw.rect(screen,(52,50,48),(int(WIDTH*0.38),gy5,int(WIDTH*0.56),88))
            pygame.draw.rect(screen,(62,60,58),(int(WIDTH*0.38),gy5,int(WIDTH*0.56),6))
            # Runway centerline dashes
            for rdx2 in range(int(WIDTH*0.42),WIDTH,80):
                pygame.draw.rect(screen,(195,190,145),(rdx2,gy5+38,55,6))
            # Runway edge lights
            for rex in range(int(WIDTH*0.40),WIDTH-10,45):
                blink2=(tick//15+rex)%20<10
                bcol2=(255,200,50) if blink2 else (80,60,15)
                pygame.draw.circle(screen,bcol2,(rex,gy5+4),3)
                pygame.draw.circle(screen,bcol2,(rex,gy5+84),3)
            # Hangar
            pygame.draw.rect(screen,(28,32,40),(int(WIDTH*0.82),gy5-100,175,100))
            pygame.draw.arc(screen,(28,32,40),
                            pygame.Rect(int(WIDTH*0.82),gy5-140,175,88),0,math.pi,0)
            pygame.draw.rect(screen,(36,42,52),(int(WIDTH*0.82),gy5-100,175,4))
            pygame.draw.line(screen,(40,48,60),(int(WIDTH*0.82)+88,gy5-100),
                             (int(WIDTH*0.82)+88,gy5-122),2)
            pygame.draw.circle(screen,(255,80,80),(int(WIDTH*0.82)+88,gy5-125),4)
            # Control tower
            pygame.draw.rect(screen,(22,28,38),(38,gy5-140,30,140))
            pygame.draw.rect(screen,(30,38,52),(22,gy5-155,62,22),border_radius=3)
            # Tower windows
            for tw_y in range(gy5-148,gy5-30,24):
                pygame.draw.rect(screen,(60,140,200),(30,tw_y,14,16))
                pygame.draw.rect(screen,(80,180,240),(30,tw_y,14,4))
            # Rotating beacon on tower
            beacon_ang=tick*0.08
            bx8=int(53+math.cos(beacon_ang)*18); by8=int(gy5-158)
            pygame.draw.circle(screen,(255,220,50),(bx8,by8),5)
            bs5=pygame.Surface((20,20),pygame.SRCALPHA)
            pygame.draw.circle(bs5,(255,220,50,80),(10,10),10)
            screen.blit(bs5,(bx8-10,by8-10))

        # ── Jet trail (acts 3+) ──────────────────────────────────────────────
        for tr in jet_trail:
            tr_a=max(0,int((1-tr["age"]/40)*180))
            if tr_a<4: continue
            tr_r=max(1,int((1-tr["age"]/40)*14))
            ts5=pygame.Surface((tr_r*2+2,tr_r*2+2),pygame.SRCALPHA)
            pygame.draw.circle(ts5,(*tr["col"],tr_a),(tr_r+1,tr_r+1),tr_r)
            screen.blit(ts5,(int(tr["x"])-tr_r-1,int(tr["y"])-tr_r-1))

        # ── Confetti (acts 1-3) ──────────────────────────────────────────────
        if act2<=3:
            conf_a2=255 if act2<=2 else max(0,int(255-(tick-380)*1.8))
            for c in confetti:
                cs6=pygame.Surface((c["sz"],c["sz"]//2+3),pygame.SRCALPHA)
                cs6.fill((*c["col"],conf_a2))
                rot3=pygame.transform.rotate(cs6,c["rot"])
                screen.blit(rot3,(int(c["x"])-rot3.get_width()//2,
                                  int(c["y"])-rot3.get_height()//2))

        # ── Fireworks ───────────────────────────────────────────────────────
        for fw in fireworks:
            fa4=max(0,min(255,int(fw["life"]/fw["max_life"]*255)))
            if fa4<5: continue
            fw_r=max(1,int(fw["life"]/fw["max_life"]*5))
            fs6=pygame.Surface((fw_r*2+2,fw_r*2+2),pygame.SRCALPHA)
            pygame.draw.circle(fs6,(*fw["col"],fa4),(fw_r+1,fw_r+1),fw_r)
            screen.blit(fs6,(int(fw["x"])-fw_r,int(fw["y"])-fw_r))

        # ── ACT 1: Victory fanfare ───────────────────────────────────────────
        if act2==1:
            gy6=HEIGHT-88
            for i3,spx4 in enumerate(crowd_left):
                draw_crowd_soldier(screen,spx4,gy6,tick+i3*22,1)
            for i3,spx5 in enumerate(crowd_right):
                draw_crowd_soldier(screen,spx5,gy6,tick+i3*18+30,-1)
            # Jet on runway
            draw_jet_detailed(screen,int(jet_x),int(jet_y),exhaust6=False)
            # SIEG banner
            if tick>18:
                ba2=min(255,(tick-18)*6)
                bsc2=1.0+abs(math.sin(tick*0.035))*0.055
                bt3=f_ultra.render("SIEG!",True,(255,215,50))
                bsh3=f_ultra.render("SIEG!",True,(100,58,0))
                bts2=pygame.transform.scale(bt3,(int(bt3.get_width()*bsc2),
                                                   int(bt3.get_height()*bsc2)))
                bss2=pygame.transform.scale(bsh3,(int(bsh3.get_width()*bsc2),
                                                    int(bsh3.get_height()*bsc2)))
                bts2.set_alpha(ba2); bss2.set_alpha(ba2)
                bx9=WIDTH//2-bts2.get_width()//2
                by9=HEIGHT//3-bts2.get_height()//2
                # Glow behind title
                gls=pygame.Surface((bts2.get_width()+60,bts2.get_height()+30),pygame.SRCALPHA)
                pygame.draw.ellipse(gls,(255,200,30,int(ba2*0.18)),
                                    (0,0,gls.get_width(),gls.get_height()))
                screen.blit(gls,(bx9-30,by9-15))
                screen.blit(bss2,(bx9+4,by9+4))
                screen.blit(bts2,(bx9,by9))
            if tick>50:
                sub5=f_med2.render("General Omega ist gefallen!  Die Welt ist frei.",True,WHITE)
                sub5.set_alpha(min(255,(tick-50)*5))
                screen.blit(sub5,(WIDTH//2-sub5.get_width()//2,HEIGHT//3+88))
            if tick>100:
                sub6=f_small2.render("Mission erfüllt.  Alle 6 Zonen befreit.",True,(180,210,180))
                sub6.set_alpha(min(255,(tick-100)*6))
                screen.blit(sub6,(WIDTH//2-sub6.get_width()//2,HEIGHT//3+120))

        # ── ACT 2: Board the jet ─────────────────────────────────────────────
        elif act2==2:
            gy7=HEIGHT-88
            for i3 in range(2):
                draw_crowd_soldier(screen,crowd_left[i3],gy7,tick+i3*20)
            draw_jet_detailed(screen,int(jet_x),int(jet_y),exhaust6=False)
            if not pl_boarded:
                draw_player_hero(screen,pl_x,pl_y,tick)
            else:
                # Player boarding ladder animation
                if (tick-380)%20<10:
                    ls4=f_tiny2.render("EINSTEIGEN...",True,(100,200,100))
                    screen.blit(ls4,(int(jet_x)-40,int(jet_y)-40))
            t_rem2=max(0,380-tick)
            if t_rem2<100:
                ct6=f_huge2.render("ABFLUG!",True,YELLOW)
                ct6.set_alpha(min(255,(100-t_rem2)*6))
                screen.blit(ct6,(WIDTH//2-ct6.get_width()//2,HEIGHT//4))
                # Countdown ring
                countdown_ratio=(100-t_rem2)/100
                for cr_r,cr_a_mult in [(55,0.6),(40,0.9),(28,1.2)]:
                    cr_s=pygame.Surface((cr_r*2+4,cr_r*2+4),pygame.SRCALPHA)
                    pygame.draw.arc(cr_s,(255,200,50,int(200*cr_a_mult)),
                                    (0,0,cr_r*2+4,cr_r*2+4),
                                    -math.pi/2,-math.pi/2+countdown_ratio*2*math.pi,
                                    max(1,int(cr_r*0.18)))
                    screen.blit(cr_s,(WIDTH//2-cr_r-2,HEIGHT//4+78-cr_r-2))
            else:
                st6=f_small2.render("Mission erfüllt.  Zeit zu verschwinden, Soldat.",
                                     True,(200,210,230))
                screen.blit(st6,(WIDTH//2-st6.get_width()//2,55))

        # ── ACT 3: Launch ────────────────────────────────────────────────────
        elif act2==3:
            if -300<jet_x<WIDTH+400 and -400<jet_y<HEIGHT+150:
                draw_jet_detailed(screen,int(jet_x),int(jet_y),
                                  ang6=math.radians(jet_angle_deg),
                                  sc6=jet_scale, exhaust6=True)
            st7=f_med2.render("Du verlässt das Schlachtfeld...",True,(190,205,225))
            st7.set_alpha(min(255,(tick-380)*4))
            screen.blit(st7,(WIDTH//2-st7.get_width()//2,52))
            # Sonic boom ring
            if 390<tick<420:
                boom_r=int((tick-390)*28)
                bs6=pygame.Surface((boom_r*2+4,boom_r*2+4),pygame.SRCALPHA)
                pygame.draw.circle(bs6,(255,255,255,max(0,100-(tick-390)*4)),
                                   (boom_r+2,boom_r+2),boom_r,4)
                screen.blit(bs6,(int(jet_x)-boom_r-2,int(jet_y)-boom_r-2))

        # ── ACT 4: Space ─────────────────────────────────────────────────────
        elif act2==4:
            if jet_y>-300:
                draw_jet_detailed(screen,int(jet_x),int(jet_y),
                                  ang6=math.radians(jet_angle_deg),
                                  sc6=max(0.2,jet_scale*(1-(tick-620)/400)),
                                  exhaust6=True)
            credits=[
                (640, "Die Erde ist frei.",               f_huge2,(255,215,50)),
                (700, "General Omega ist Geschichte.",    f_med2, (255,255,255)),
                (760, "Sechs Zonen. Ein Held.",           f_med2, (200,215,235)),
                (820, "Du bist eine Legende, Soldat.",    f_med2, (180,200,220)),
                (875, "Danke fürs Spielen — v6.0",        f_small2,(130,145,165)),
            ]
            for st8,line4,fnt3,col7 in credits:
                if tick>=st8:
                    la3=min(255,(tick-st8)*7)
                    lt3=fnt3.render(line4,True,col7)
                    lt3.set_alpha(la3)
                    cy8=HEIGHT//2-110+credits.index((st8,line4,fnt3,col7))*56
                    screen.blit(lt3,(WIDTH//2-lt3.get_width()//2,cy8))

        # ── ACT 5 / Final fade ───────────────────────────────────────────────
        if tick>900:
            fa5=min(255,(tick-900)*6)
            fd3=pygame.Surface((WIDTH,HEIGHT))
            fd3.fill((0,0,0)); fd3.set_alpha(fa5)
            screen.blit(fd3,(0,0))

        # ── Atmosphere glow band ─────────────────────────────────────────────
        if 250<tick<650:
            ga2=min(55,max(0,int((tick-250)*0.32)))
            atm4=pygame.Surface((WIDTH,70),pygame.SRCALPHA)
            atm4.fill((80,145,230,ga2))
            screen.blit(atm4,(0,HEIGHT-70))

        # Skip hint
        ht4=f_tiny2.render("SPACE — Überspringen",True,(55,60,80))
        screen.blit(ht4,(WIDTH//2-ht4.get_width()//2,HEIGHT-18))

        pygame.display.flip()

# ═══════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════
def main():
    global FPS
    while True:
        cap = SETTINGS.get("fps_cap", 60)
        FPS = cap if cap and cap > 0 else 9999
        action=show_main_menu()
        if action!="play": continue

        WSTATS.reset();COMBO.__init__()
        player=Player(100,GROUND_Y-Player.H)
        game_state="play";zone=1
        show_cutscene(0)

        while game_state=="play" and zone<=NUM_ZONES:
            result=play_zone(zone,player)
            if result=="quit":       pygame.quit();sys.exit()
            elif result=="menu":     game_state="menu"
            elif result=="gameover":
                choice=show_gameover(player.score,zone)
                if choice=="retry":
                    WSTATS.reset();player=Player(100,GROUND_Y-Player.H);zone=1;show_cutscene(0)
                else: game_state="menu"
            elif result=="next_zone":
                show_level_map(zone, zone + 1)
                SKILLS.earn(3)
                show_skill_tree()
                show_cutscene(zone)
            elif result=="win":      game_state="win"
            zone += 1

            if game_state == "win":
                w = show_win(player.score)
                if w == "highscore":
                    show_name_input(player.score, zone)
                    show_highscores()

if __name__=="__main__":
    main()
