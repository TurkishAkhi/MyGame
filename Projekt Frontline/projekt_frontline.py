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
WORLD_WIDTH    = 4200
screen         = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PROJEKT FRONTLINE  v6.0")
clock          = pygame.time.Clock()
FPS            = 60

RED        = (220, 50,  50)
GREEN      = (50,  200, 80)
YELLOW     = (240, 210, 50)
WHITE      = (255, 255, 255)
GRAY       = (150, 150, 150)
DARK       = (20,  20,  20)
ORANGE     = (240, 130, 30)
CYAN       = (50,  220, 220)
BULLET_COL = (255, 240, 100)
SNIPER_COL = (100, 220, 255)
ROCKET_COL = (255, 100, 30)
GRENADE_COL= (80,  160, 80)

GROUND_Y            = HEIGHT - 80
HIGHSCORE_FILE      = "frontline_scores.json"
ACHIEVEMENTS_FILE   = "frontline_achievements.json"
CAMERA_LERP         = 0.10
PARTICLE_FRICTION   = 0.97
GRENADE_THROW_CHANCE= 0.005
NUM_ZONES           = 6

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

# ═══════════════════════════════════════════════════
#  SPIELER-SKINS
# ═══════════════════════════════════════════════════
SKINS = {
    "standard": {
        "label":    "Standardsoldat",
        "body":     (50,  90,  50),
        "head":     (200, 160, 110),
        "helmet":   (40,  60,  40),
        "vest":     (35,  65,  35),
        "desc":     "Klassische Uniform",
        "unlock":   None,
    },
    "desert": {
        "label":    "Wüstenkämpfer",
        "body":     (160, 120, 60),
        "head":     (210, 170, 120),
        "helmet":   (140, 100, 50),
        "vest":     (150, 110, 55),
        "desc":     "Tarnung für die Wüste",
        "unlock":   None,
    },
    "arctic": {
        "label":    "Arktis-Ranger",
        "body":     (200, 210, 220),
        "head":     (220, 215, 205),
        "helmet":   (190, 200, 210),
        "vest":     (195, 205, 215),
        "desc":     "Weisse Tarnung — Kälteresistent",
        "unlock":   "zone_5",
    },
    "shadow": {
        "label":    "Schattenkrieger",
        "body":     (30,  30,  40),
        "head":     (60,  50,  45),
        "helmet":   (20,  20,  30),
        "vest":     (25,  25,  35),
        "desc":     "Nacht-Ops Spezialist — freischalten: alle Zonen",
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
    0: ["SITUATION KRITISCH.",
        "Der feindliche General 'OMEGA' hat sechs strategische Zonen besetzt.",
        "Du bist der einzige Soldat, der tief genug eingedrungen ist.",
        "Befreie jede Zone. Besiege den General.",
        "Viel Glück, Soldat. Du wirst es brauchen."],
    1: ["Gut gemacht. Die Stadt ist gesichert.",
        "Unsere Aufklärer melden feindliche Truppenbewegungen im Wald.",
        "Sie setzen Drohnen ein – Augen am Himmel.",
        "Halte Deckung und beweg dich schnell."],
    2: ["Der Wald gehört wieder uns.",
        "WARNUNG: Feindliche Panzerdivisionen in der Wüste gesichtet.",
        "Normale Waffen richten gegen Panzer kaum Schaden an.",
        "Nutze den Raketenwerfer [5] – er ist dein bester Freund gegen Stahl."],
    3: ["Wüstenfront überwältigt. Beeindruckend.",
        "Die feindliche Militärbasis liegt direkt vor dir.",
        "Helikopter patroullieren den Luftraum.",
        "Der Stinger [6] macht kurzen Prozess mit allem, das fliegt."],
    4: ["Militärbasis gefallen. Der Feind ist demoralisiert.",
        "Aber General OMEGA hat seine Eliteeinheiten in die Arktis verlegt.",
        "Jetpack-Soldaten, Jets, Panzer – alles auf einmal.",
        "Bleib beweglich. Bleib am Leben."],
    5: ["Arktis gesichert. Nur noch ein Ziel.",
        "FESTUNG OMEGA. Letztes Bollwerk des Generals.",
        "Er wartet auf dich. Drei Kampfphasen. Keine Gnade.",
        "Das ist dein Moment, Soldat. Ende es."],
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
def make_sound(freq=440, duration=0.1, volume=0.3, wave="square", decay=True):
    sr = 44100; n = int(sr * duration); buf = bytearray(n * 2)
    for i in range(n):
        t = i / sr; env = (1 - i / n) if decay else 1.0
        if   wave == "square": v = 1 if math.sin(2*math.pi*freq*t) > 0 else -1
        elif wave == "noise":  v = random.uniform(-1, 1)
        else:                  v = math.sin(2*math.pi*freq*t)
        sample = max(-32768, min(32767, int(v * env * volume * 32767)))
        buf[i*2] = sample & 0xFF; buf[i*2+1] = (sample >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))

class SoundManager:
    def __init__(self):
        self.enabled = True
        try:
            self.shoot_pistol  = make_sound(800,  0.08, 0.25, "square")
            self.shoot_rifle   = make_sound(600,  0.06, 0.20, "square")
            self.shoot_sniper  = make_sound(300,  0.18, 0.35, "square")
            self.shoot_shotgun = make_sound(400,  0.12, 0.30, "noise")
            self.shoot_rocket  = make_sound(200,  0.15, 0.35, "square")
            self.shoot_stinger = make_sound(500,  0.10, 0.30, "square")
            self.knife_slash   = make_sound(900,  0.05, 0.20, "square")
            self.explosion     = make_sound(120,  0.35, 0.40, "noise")
            self.big_explosion = make_sound(80,   0.50, 0.50, "noise")
            self.hit_player    = make_sound(200,  0.12, 0.30, "noise")
            self.hit_enemy     = make_sound(500,  0.07, 0.20, "square")
            self.jump          = make_sound(350,  0.10, 0.15, "sine")
            self.grenade_throw = make_sound(450,  0.08, 0.15, "square")
            self.zone_clear    = make_sound(880,  0.50, 0.30, "sine", decay=False)
            self.boss_roar     = make_sound(80,   0.40, 0.35, "noise")
            self.tank_shot     = make_sound(150,  0.20, 0.40, "noise")
            self.pickup        = make_sound(660,  0.15, 0.25, "sine")
            self.shield_hit    = make_sound(300,  0.10, 0.20, "square")
            self.level_up      = make_sound(550,  0.30, 0.30, "sine", decay=False)
            self.achievement   = make_sound(440,  0.40, 0.25, "sine", decay=False)
            self.pause         = make_sound(300,  0.08, 0.15, "square")
        except Exception:
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
        s=pygame.Surface((self.size*2+2,self.size*2+2),pygame.SRCALPHA)
        if self.kind=="rain":
            pygame.draw.line(s,(180,200,255,self.alpha),(self.size,0),(self.size-1,self.size*3),1)
        elif self.kind=="snow":
            pygame.draw.circle(s,(230,240,255,self.alpha),(self.size+1,self.size+1),self.size)
        elif self.kind=="dust":
            pygame.draw.ellipse(s,(200,170,100,self.alpha//2),(0,0,self.size*2+2,self.size+2))
        elif self.kind=="embers":
            pygame.draw.circle(s,(255,140,30,self.alpha),(self.size+1,self.size+1),self.size)
        surf.blit(s,(int(self.x)-self.size-1,int(self.y)-self.size-1))

class WeatherSystem:
    ZONE_WEATHER={1:"rain",2:"fog",3:"dust",4:"embers",5:"snow",6:"rain"}
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
class Particle:
    __slots__=("x","y","vx","vy","life","max_life","color","size","gravity")
    def __init__(self,x,y,vx,vy,life,color,size=3,gravity=0.15):
        self.x=float(x);self.y=float(y);self.vx=vx;self.vy=vy
        self.life=life;self.max_life=life;self.color=color;self.size=size;self.gravity=gravity
    def update(self):
        self.x+=self.vx;self.y+=self.vy;self.vy+=self.gravity;self.vx*=PARTICLE_FRICTION;self.life-=1
    def draw(self,surf,cam_x=0):
        r=max(1,int(self.size*self.life/self.max_life))
        pygame.draw.circle(surf,self.color,(int(self.x)-cam_x,int(self.y)),r)
    @property
    def alive(self): return self.life>0

class ParticleSystem:
    def __init__(self): self.particles=[]
    def _p(self,*a,**kw): self.particles.append(Particle(*a,**kw))
    def spawn_muzzle_flash(self,x,y,d):
        for _ in range(8):
            a=random.uniform(-0.4,0.4);s=random.uniform(3,9)
            c=random.choice([(255,240,100),(255,180,50),(255,255,200)])
            self._p(x,y,math.cos(a)*s*d,math.sin(a)*s,random.randint(4,10),c,random.randint(2,5),0)
    def spawn_blood(self,x,y,count=12):
        for _ in range(count):
            a=random.uniform(0,2*math.pi);s=random.uniform(1,6)
            c=random.choice([(180,20,20),(220,40,40),(240,60,60)])
            self._p(x,y,math.cos(a)*s,math.sin(a)*s-2,random.randint(15,30),c,random.randint(2,5))
    def spawn_explosion(self,x,y,scale=1.0):
        for _ in range(int(40*scale)):
            a=random.uniform(0,2*math.pi);s=random.uniform(2,12*scale)
            c=random.choice([(255,200,50),(255,120,20),(255,60,10),(200,200,200)])
            self._p(x,y,math.cos(a)*s,math.sin(a)*s-3,random.randint(20,45),c,random.randint(4,max(4,int(8*scale))),0.25)
        for _ in range(int(20*scale)):
            a=random.uniform(0,2*math.pi);s=random.uniform(0.5,3)
            self._p(x,y,math.cos(a)*s,math.sin(a)*s-4,random.randint(35,60),(80,80,80),random.randint(6,12),-0.05)
    def spawn_dust(self,x,y):
        for _ in range(5): self._p(x,y,random.uniform(-2,2),random.uniform(-3,-1),random.randint(8,18),(120,100,70),random.randint(2,4))
    def spawn_shell(self,x,y,d):
        self._p(x,y,-d*random.uniform(2,5),random.uniform(-4,-1),random.randint(20,35),(200,180,50),3)
    def spawn_sparks(self,x,y,count=10):
        for _ in range(count):
            a=random.uniform(0,2*math.pi);s=random.uniform(2,8)
            c=random.choice([(255,200,50),(255,255,100),(200,200,200)])
            self._p(x,y,math.cos(a)*s,math.sin(a)*s,random.randint(5,15),c,2,0.3)
    def spawn_smoke(self,x,y):
        self._p(x,y,random.uniform(-1,1),random.uniform(-2,-0.5),random.randint(20,40),(100,100,100),random.randint(4,8),-0.02)
    def spawn_pickup(self,x,y,color):
        for _ in range(12):
            a=random.uniform(0,2*math.pi);s=random.uniform(1,5)
            self._p(x,y,math.cos(a)*s,math.sin(a)*s-2,random.randint(20,35),color,random.randint(2,4))
    def update(self):
        self.particles=[p for p in self.particles if p.alive]
        for p in self.particles: p.update()
    def draw(self,surf,cam_x=0):
        for p in self.particles: p.draw(surf,cam_x)

PARTICLES=ParticleSystem()
screen_shake=0
_spotlight_surf=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)

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
        bg=pygame.Surface((self.W+4,self.H+4),pygame.SRCALPHA);bg.fill((0,0,0,160))
        surf.blit(bg,(self.X-2,self.Y-2))
        pygame.draw.rect(surf,GRAY,(self.X,self.Y,self.W,self.H),1)
        vw=int(WIDTH*self.SCALE);cx=int(cam_x*self.SCALE)
        pygame.draw.rect(surf,(80,80,80,100),(self.X+cx,self.Y,vw,self.H))
        pygame.draw.line(surf,(80,70,55),(self.X,self.Y+self.H-6),(self.X+self.W,self.Y+self.H-6),2)
        for e in enemies:
            pygame.draw.circle(surf,RED,(self.X+int(e.x*self.SCALE),self.Y+self.H-8),2)
        for t in tanks:
            tx=self.X+int(t.x*self.SCALE)
            pygame.draw.rect(surf,(180,120,20),(tx-3,self.Y+self.H-10,6,4))
        for a in air_enemies+jetpack_soldiers:
            pygame.draw.circle(surf,CYAN,(self.X+int(a.x*self.SCALE),self.Y+8),2)
        if boss and boss.alive:
            bx=self.X+int(boss.x*self.SCALE)
            r=3+int(abs(math.sin(pygame.time.get_ticks()*0.005))*2)
            pygame.draw.circle(surf,ORANGE,(bx,self.Y+self.H//2),r)
        for p in powerups:
            if p.alive:
                pygame.draw.circle(surf,YELLOW,(self.X+int(p.x*self.SCALE),self.Y+self.H-8),2)
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

    def can_shoot(self,weapon_name=""):
        if self.ammo is not None and self.ammo<=0: return False
        fr=int(self.fire_rate*WSTATS.get_fire_rate_mult(weapon_name))
        return pygame.time.get_ticks()-self.last_shot>=fr

    def shoot_toward(self,ox,oy,tx,ty,facing=1,dmg_mult=1.0):
        if not self.can_shoot(self.name): return []
        self.last_shot=pygame.time.get_ticks()
        if self.ammo is not None: self.ammo-=1
        if self.sound: SFX.play(self.sound)
        if self.is_knife: return [("melee",ox,oy,facing)]
        dx=tx-ox;dy=ty-oy;dist=math.hypot(dx,dy) or 1
        results=[]
        # Weapon upgrade bonus
        wdmg=int(self.damage*dmg_mult*WSTATS.get_dmg_mult(self.name))
        if self.is_shotgun:
            for _ in range(8):
                angle=math.atan2(dy,dx)+random.uniform(-0.3,0.3)
                results.append(Bullet(ox,oy,math.cos(angle)*self.bullet_speed,math.sin(angle)*self.bullet_speed,wdmg,self.color))
            PARTICLES.spawn_muzzle_flash(ox+(1 if dx>0 else -1)*16,oy,1 if dx>0 else -1)
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

# ═══════════════════════════════════════════════════
#  PROJEKTILE
# ═══════════════════════════════════════════════════
class Bullet:
    RADIUS=5
    def __init__(self,x,y,vx,vy,damage,color,is_sniper=False):
        self.x=float(x);self.y=float(y);self.vx=vx;self.vy=vy
        self.damage=damage;self.color=color;self.alive=True;self.is_sniper=is_sniper
    def update(self):
        self.x+=self.vx;self.y+=self.vy
        if self.x<-200 or self.x>WORLD_WIDTH+200 or self.y<-300 or self.y>HEIGHT+100: self.alive=False
    def draw(self,surf,cam_x=0):
        r=7 if self.is_sniper else self.RADIUS
        pygame.draw.circle(surf,self.color,(int(self.x)-cam_x,int(self.y)),r)
    def get_rect(self):
        r=7 if self.is_sniper else self.RADIUS
        return pygame.Rect(self.x-r,self.y-r,r*2,r*2)

class Rocket:
    RADIUS=6
    def __init__(self,x,y,vx,vy,damage,color,is_stinger=False):
        self.x=float(x);self.y=float(y);self.vx=vx;self.vy=vy
        self.damage=damage;self.color=color;self.alive=True
        self.is_stinger=is_stinger;self.explosion_r=160 if not is_stinger else 120
        self.homing_target=None
    def update(self,air_targets=None):
        if self.is_stinger and air_targets:
            if self.homing_target is None or not self.homing_target.alive:
                best=None;best_d=9999
                for t in air_targets:
                    d=math.hypot(t.x-self.x,t.y-self.y)
                    if d<best_d: best_d=d;best=t
                self.homing_target=best
            if self.homing_target and self.homing_target.alive:
                tx=self.homing_target.x;ty=self.homing_target.y
                dx=tx-self.x;dy=ty-self.y;dist=math.hypot(dx,dy) or 1
                spd=math.hypot(self.vx,self.vy)
                self.vx+=(dx/dist*spd-self.vx)*0.08;self.vy+=(dy/dist*spd-self.vy)*0.08
        self.x+=self.vx;self.y+=self.vy;PARTICLES.spawn_smoke(self.x,self.y)
        if self.x<-200 or self.x>WORLD_WIDTH+200 or self.y<-400 or self.y>HEIGHT+100: self.alive=False
    def explode(self,targets):
        self.alive=False;SFX.play(SFX.big_explosion);PARTICLES.spawn_explosion(self.x,self.y,scale=2.0)
        hits=[]
        for t in targets:
            d=math.hypot(t.x-self.x,t.y-self.y)
            if d<=self.explosion_r: hits.append((t,int(self.damage*(1-d/self.explosion_r))))
        return hits
    def draw(self,surf,cam_x=0):
        sx=int(self.x)-cam_x;sy=int(self.y)
        angle=math.atan2(self.vy,self.vx)
        col=CYAN if self.is_stinger else ROCKET_COL
        pygame.draw.circle(surf,col,(sx,sy),self.RADIUS)
        pygame.draw.line(surf,(255,200,50),(sx,sy),(int(sx-math.cos(angle)*18),int(sy-math.sin(angle)*18)),3)
    def get_rect(self):
        return pygame.Rect(self.x-self.RADIUS,self.y-self.RADIUS,self.RADIUS*2,self.RADIUS*2)

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
        for e in enemies:
            d=math.hypot(e.x-self.x,e.y-self.y)
            if d<=self.EXPLOSION_R:
                hits.append((e,int(self.DAMAGE*(1-d/self.EXPLOSION_R))))
                self.hits_in_explosion+=1
        if self.hits_in_explosion>=3: unlock("grenade_multi")
        return hits
    def draw(self,surf,cam_x=0):
        sx=int(self.x)-cam_x
        if not self.exploded:
            pygame.draw.circle(surf,GRENADE_COL,(sx,int(self.y)),self.RADIUS)
            if (pygame.time.get_ticks()//200)%2==0: pygame.draw.circle(surf,RED,(sx,int(self.y)),3)

# ═══════════════════════════════════════════════════
#  ZONEN
# ═══════════════════════════════════════════════════
current_platforms=[]

def make_zones():
    WW=WORLD_WIDTH;GY=GROUND_Y
    return {
        1:{"name":"ZONE 1: ZERSTOERTE STADT","sky":(28,38,58),"ground":(65,52,38),
           "enemy_hp":50,"enemy_speed":2.2,"enemy_shoot_rate":1700,
           "air_enemies":[],"powerup_count":4,
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
        2:{"name":"ZONE 2: WALD","sky":(18,42,20),"ground":(35,62,25),
           "enemy_hp":70,"enemy_speed":2.8,"enemy_shoot_rate":1300,
           "air_enemies":[("drone",1200),("drone",2400)],"powerup_count":4,
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(200,GY-100,100,18),pygame.Rect(370,GY-155,90,18),
               pygame.Rect(530,GY-100,100,18),pygame.Rect(700,GY-200,80,18),
               pygame.Rect(860,GY-140,120,18),pygame.Rect(1040,GY-220,90,18),
               pygame.Rect(1550,GY-80,70,18),pygame.Rect(1850,GY-130,120,18),
               pygame.Rect(2050,GY-200,90,18),pygame.Rect(2750,GY-150,130,18),
               pygame.Rect(3150,GY-150,130,18)],
           "enemy_positions":[(800,GY-52),(1100,GY-52),(1500,GY-52),(1700,GY-52),
               (2000,GY-52),(2300,GY-52),(2600,GY-52),(2900,GY-52),(700,GY-222),(2050,GY-222)]},
        3:{"name":"ZONE 3: WUESTENFRONT","sky":(80,55,30),"ground":(140,100,50),
           "enemy_hp":85,"enemy_speed":2.5,"enemy_shoot_rate":1400,
           "air_enemies":[("drone",1500),("drone",2800),("drone",3500)],"powerup_count":5,
           "tank_positions":[(1800,GY-52),(3000,GY-52)],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(300,GY-90,120,18),pygame.Rect(550,GY-160,100,18),
               pygame.Rect(800,GY-110,130,18),pygame.Rect(1300,GY-130,140,18),
               pygame.Rect(1800,GY-140,120,18),pygame.Rect(2300,GY-160,130,18),
               pygame.Rect(2850,GY-130,140,18),pygame.Rect(3100,GY-200,100,18)],
           "enemy_positions":[(600,GY-52),(950,GY-52),(1300,GY-52),(1650,GY-52),
               (2000,GY-52),(2350,GY-52),(2700,GY-52),(3050,GY-52),(1050,GY-222),(2600,GY-262)]},
        4:{"name":"ZONE 4: MILITAERBASIS","sky":(12,12,28),"ground":(42,42,52),
           "enemy_hp":110,"enemy_speed":3.0,"enemy_shoot_rate":1000,
           "air_enemies":[("helicopter",1600),("helicopter",3200)],"powerup_count":5,
           "tank_positions":[(2200,GY-52),(3400,GY-52)],
           "jetpack_positions":[(1400,GY-52),(2600,GY-52)],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(180,GY-120,100,18),pygame.Rect(520,GY-140,110,18),
               pygame.Rect(920,GY-180,130,18),pygame.Rect(1100,GY-260,100,18),
               pygame.Rect(1480,GY-110,150,18),pygame.Rect(1900,GY-240,90,18),
               pygame.Rect(2280,GY-220,100,18),pygame.Rect(2880,GY-290,120,18),
               pygame.Rect(3250,GY-130,150,18)],
           "enemy_positions":[(600,GY-52),(900,GY-52),(1200,GY-52),(1550,GY-52),
               (1800,GY-52),(2100,GY-52),(2400,GY-52),(2700,GY-52),(3000,GY-52),
               (1100,GY-282),(2880,GY-312)]},
        5:{"name":"ZONE 5: ARKTIS","sky":(160,190,220),"ground":(200,220,240),
           "enemy_hp":130,"enemy_speed":3.2,"enemy_shoot_rate":900,
           "air_enemies":[("jet",2000),("jet",3500),("helicopter",1200)],"powerup_count":6,
           "tank_positions":[(1600,GY-52),(2800,GY-52),(3800,GY-52)],
           "jetpack_positions":[(900,GY-52),(2200,GY-52),(3300,GY-52)],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(220,GY-100,110,18),pygame.Rect(620,GY-130,120,18),
               pygame.Rect(860,GY-220,100,18),pygame.Rect(1350,GY-240,90,18),
               pygame.Rect(1850,GY-270,100,18),pygame.Rect(2350,GY-280,90,18),
               pygame.Rect(2850,GY-230,110,18),pygame.Rect(3400,GY-250,100,18)],
           "enemy_positions":[(700,GY-52),(1000,GY-52),(1350,GY-52),(1700,GY-52),
               (2050,GY-52),(2400,GY-52),(2750,GY-52),(3100,GY-52),(3450,GY-52),
               (860,GY-242),(2350,GY-302),(3400,GY-272)]},
        6:{"name":"ZONE 6: FESTUNG OMEGA","sky":(8,5,18),"ground":(30,25,45),
           "enemy_hp":150,"enemy_speed":3.5,"enemy_shoot_rate":800,
           "air_enemies":[("jet",1800),("jet",3000),("helicopter",2400),("helicopter",3800)],
           "powerup_count":7,
           "tank_positions":[(1200,GY-52),(2500,GY-52),(3700,GY-52)],
           "jetpack_positions":[(800,GY-52),(2000,GY-52),(3200,GY-52)],
           "platforms":[pygame.Rect(0,GY,WW,80),
               pygame.Rect(200,GY-130,110,18),pygame.Rect(620,GY-160,120,18),
               pygame.Rect(880,GY-260,100,18),pygame.Rect(1380,GY-280,90,18),
               pygame.Rect(1900,GY-300,100,18),pygame.Rect(2420,GY-310,90,18),
               pygame.Rect(2940,GY-270,110,18),pygame.Rect(3460,GY-290,100,18),
               pygame.Rect(3720,GY-160,130,18)],
           "enemy_positions":[(600,GY-52),(950,GY-52),(1300,GY-52),(1650,GY-52),
               (2000,GY-52),(2350,GY-52),(2700,GY-52),(3050,GY-52),(3400,GY-52),(3800,GY-52),
               (880,GY-282),(1900,GY-322),(3460,GY-312)]},
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
        self.MAX_HP=100+diff["player_hp_bonus"]
        self.x=float(x);self.y=float(y);self.vx=0.0;self.vy=0.0
        self.on_ground=False;self.was_on_ground=False;self.facing=1
        self.lives=self.MAX_LIVES;self.hp=self.MAX_HP
        self.grenades=self.GRENADES;self.weapon=PISTOLE
        self.invincible=0;self.alive=True
        self.score=0;self.walk_frame=0;self.walk_timer=0;self.knife_anim=0
        self.shield_timer=0;self.speed_boost_timer=0;self.dmg_boost_timer=0
        self.pickup_msg="";self.pickup_msg_timer=0
        self.total_damage_taken=0   # für "no_damage" achievement
        self.zone_damage_taken=0
        self.knife_only_zone=True   # für "knife_only" achievement
        self.air_kills=0            # für "air_ace" achievement

    @property
    def SPEED(self): return int(self.BASE_SPEED*(1.5 if self.speed_boost_timer>0 else 1))
    @property
    def dmg_mult(self): return 2.0 if self.dmg_boost_timer>0 else 1.0

    def handle_input(self,keys,bullets,rockets,cam_x):
        self.vx=0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  self.vx=-self.SPEED;self.facing=-1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.vx= self.SPEED;self.facing= 1
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.vy=self.JUMP_FORCE;SFX.play(SFX.jump)
        if self.weapon.auto and pygame.mouse.get_pressed()[0]:
            self._fire(bullets,rockets,cam_x)

    def shoot(self,bullets,rockets,cam_x):
        if not self.weapon.auto: self._fire(bullets,rockets,cam_x)

    def _fire(self,bullets,rockets,cam_x):
        mx,my=pygame.mouse.get_pos();tx=mx+cam_x;ty=my
        ox=self.rect.centerx;oy=self.rect.centery
        self.facing=1 if tx>ox else -1
        results=self.weapon.shoot_toward(ox,oy,tx,ty,self.facing,self.dmg_mult)
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
        self.was_on_ground=self.on_ground
        self.vy=min(self.vy+self.GRAVITY,self.MAX_FALL)
        self.on_ground=False;self.y+=self.vy
        for plat in current_platforms:
            pr=self.rect
            if pr.colliderect(plat):
                if self.vy>0 and pr.bottom-self.vy<=plat.top+abs(self.vy)+2:
                    self.y=plat.top-self.H;self.vy=0;self.on_ground=True
                elif self.vy<0 and pr.top-self.vy>=plat.bottom-abs(self.vy)-2:
                    self.y=plat.bottom;self.vy=1
        self.x+=self.vx;self.x=max(0,min(WORLD_WIDTH-self.W,self.x))
        if self.on_ground and not self.was_on_ground:
            PARTICLES.spawn_dust(self.x+self.W//2,self.y+self.H)
        if self.vx!=0:
            self.walk_timer+=1
            if self.walk_timer>8: self.walk_frame=(self.walk_frame+1)%4;self.walk_timer=0
        if self.invincible>0: self.invincible=max(0,self.invincible-clock.get_time())
        if self.knife_anim>0: self.knife_anim-=1
        if self.shield_timer>0:      self.shield_timer-=1
        if self.speed_boost_timer>0: self.speed_boost_timer-=1
        if self.dmg_boost_timer>0:   self.dmg_boost_timer-=1
        if self.pickup_msg_timer>0:  self.pickup_msg_timer-=1

    def take_damage(self,amount):
        global screen_shake
        if self.invincible>0: return
        if self.shield_timer>0:
            SFX.play(SFX.shield_hit);PARTICLES.spawn_sparks(self.rect.centerx,self.rect.centery,8)
            screen_shake=4;return
        dmg=int(amount*get_diff()["enemy_dmg_mult"])
        self.hp-=dmg;self.zone_damage_taken+=dmg;self.total_damage_taken+=dmg
        SFX.play(SFX.hit_player);PARTICLES.spawn_blood(self.rect.centerx,self.rect.centery,8)
        screen_shake=8
        if self.hp<=0:
            self.hp=0;self.lives-=1
            if self.lives>0: self.hp=self.MAX_HP;self.invincible=2000
            else: self.alive=False

    def collect_powerup(self,pu):
        msg=pu.apply(self);self.pickup_msg=msg;self.pickup_msg_timer=150

    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)

    def draw(self,surf,cam_x=0):
        sx=int(self.x)-cam_x;cx=sx+self.W//2;cy=int(self.y);f=self.facing
        if self.invincible>0 and (pygame.time.get_ticks()//100)%2==0: return
        skin=SKINS[current_skin]
        bc=skin["body"];hc=skin["head"];helm=skin["helmet"];vest=skin["vest"]

        if self.shield_timer>0:
            pulse=abs(math.sin(pygame.time.get_ticks()*0.005))*30
            sa=pygame.Surface((80,80),pygame.SRCALPHA)
            pygame.draw.circle(sa,(80,160,255,int(40+pulse)),(40,40),38)
            surf.blit(sa,(cx-40,cy-10))
        if self.dmg_boost_timer>0:
            sa=pygame.Surface((70,70),pygame.SRCALPHA)
            pygame.draw.circle(sa,(255,120,20,40),(35,35),33)
            surf.blit(sa,(cx-35,cy-5))

        sh=pygame.Surface((self.W+8,6),pygame.SRCALPHA)
        pygame.draw.ellipse(sh,(0,0,0,80),(0,0,self.W+8,6))
        surf.blit(sh,(cx-self.W//2-4,cy+self.H-2))
        pygame.draw.circle(surf,hc,(cx,cy+10),10)
        pygame.draw.arc(surf,helm,pygame.Rect(cx-12,cy+2,24,16),0,math.pi,5)
        pygame.draw.rect(surf,helm,pygame.Rect(cx-12,cy+6,24,6))
        pygame.draw.rect(surf,bc,pygame.Rect(cx-10,cy+20,20,20))
        pygame.draw.rect(surf,vest,pygame.Rect(cx-8,cy+21,16,18))
        lo=[0,6,0,-6][self.walk_frame] if self.vx!=0 else 0
        pygame.draw.line(surf,bc,(cx-5,cy+40),(cx-5,cy+55+lo),5)
        pygame.draw.line(surf,bc,(cx+5,cy+40),(cx+5,cy+55-lo),5)
        arm_end_x=cx+f*18;arm_end_y=cy+28
        if self.weapon==MESSER and self.knife_anim>0:
            progress=self.knife_anim/15.0
            arm_end_x=cx+f*int(18+30*progress);arm_end_y=cy+int(28-10*progress)
            pygame.draw.line(surf,(200,200,200),(arm_end_x,arm_end_y),(arm_end_x+f*20,arm_end_y-5),3)
        pygame.draw.line(surf,bc,(cx,cy+22),(arm_end_x,arm_end_y),4)
        if   self.weapon==PISTOLE:       pygame.draw.rect(surf,(60,60,60),pygame.Rect(cx+f*10,cy+25,14,5))
        elif self.weapon==STURMGEWEHR:   pygame.draw.rect(surf,(40,40,40),pygame.Rect(cx+f*10,cy+24,22,6))
        elif self.weapon==SCHARFSCHUETZE:
            pygame.draw.rect(surf,(30,50,30),pygame.Rect(cx+f*10,cy+23,30,5))
            pygame.draw.rect(surf,(70,100,70),pygame.Rect(cx+f*32,cy+21,6,3))
        elif self.weapon==SCHROTFLINTE:  pygame.draw.rect(surf,(80,60,30),pygame.Rect(cx+f*8,cy+24,20,7))
        elif self.weapon==RAKETENWERFER:
            pygame.draw.rect(surf,(60,60,60),pygame.Rect(cx+f*8,cy+22,28,8))
            pygame.draw.circle(surf,(80,80,80),(cx+f*36,cy+26),5)
        elif self.weapon==STINGER:
            pygame.draw.rect(surf,(40,80,80),pygame.Rect(cx+f*8,cy+20,32,8))
            pygame.draw.circle(surf,CYAN,(cx+f*40,cy+24),4)
        elif self.weapon==MESSER and self.knife_anim==0:
            pygame.draw.line(surf,(200,200,200),(cx+f*12,cy+26),(cx+f*26,cy+22),3)

        # Waffen-Level Badge
        wlv=WSTATS.get_level(self.weapon.name)
        if wlv>0:
            lf=pygame.font.SysFont("consolas",9,bold=True)
            lb=lf.render(f"LV{wlv}",True,YELLOW)
            surf.blit(lb,(cx+f*10,cy+16))

        bw=50;bx=cx-bw//2;by=cy-12
        pygame.draw.rect(surf,DARK,(bx,by,bw,6))
        hpcolor=GREEN if self.hp>50 else YELLOW if self.hp>25 else RED
        pygame.draw.rect(surf,hpcolor,(bx,by,int(bw*self.hp/self.MAX_HP),6))
        pygame.draw.rect(surf,GRAY,(bx,by,bw,6),1)

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
    def take_damage(self,amount):
        self.hp-=amount;SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_blood(self.rect.centerx,self.rect.centery)
        if self.hp<=0:
            self.alive=False;PARTICLES.spawn_blood(self.rect.centerx,self.rect.centery,20)
    def draw(self,surf,cam_x=0):
        sx=int(self.x)-cam_x;cx=sx+self.W//2;cy=int(self.y);f=self.facing
        sc={self.ST_PATROL:(150,150,150),self.ST_CHASE:(240,120,20),
            self.ST_SHOOT:(220,50,50),self.ST_FLANK:(200,50,200)}.get(self.state,(200,200,200))
        pygame.draw.circle(surf,sc,(cx,cy-18),4)
        bc=(120,50,40)
        pygame.draw.circle(surf,(190,140,100),(cx,cy+10),9)
        pygame.draw.rect(surf,(80,30,30),pygame.Rect(cx-10,cy+4,20,14))
        pygame.draw.rect(surf,bc,pygame.Rect(cx-9,cy+19,18,18))
        lo=[0,5,0,-5][self.walk_frame]
        pygame.draw.line(surf,bc,(cx-4,cy+37),(cx-4,cy+52+lo),5)
        pygame.draw.line(surf,bc,(cx+4,cy+37),(cx+4,cy+52-lo),5)
        pygame.draw.line(surf,bc,(cx,cy+21),(cx+f*16,cy+27),4)
        pygame.draw.rect(surf,(50,50,50),pygame.Rect(cx+f*8,cy+24,14,4))
        bw=40;bx=cx-bw//2;by=cy-10
        pygame.draw.rect(surf,DARK,(bx,by,bw,5))
        hp_r=self.hp/self.max_hp
        hc=(50,200,80) if hp_r>0.6 else YELLOW if hp_r>0.3 else RED
        pygame.draw.rect(surf,hc,(bx,by,int(bw*hp_r),5))

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
    def draw(self,surf,cam_x=0):
        sx=int(self.x)-cam_x;cx=sx+self.W//2;cy=int(self.y);f=self.facing
        pygame.draw.rect(surf,(60,80,60),pygame.Rect(cx-8,cy+15,16,22))
        fl=random.randint(8,18)
        pygame.draw.polygon(surf,ORANGE,[(cx-4,cy+37),(cx+4,cy+37),(cx,cy+37+fl)])
        pygame.draw.circle(surf,(200,155,105),(cx,cy+8),9)
        pygame.draw.rect(surf,(40,80,40),pygame.Rect(cx-9,cy+17,18,18))
        pygame.draw.line(surf,(50,90,50),(cx,cy+19),(cx+f*16,cy+25),4)
        pygame.draw.rect(surf,(40,40,40),pygame.Rect(cx+f*6,cy+22,12,4))
        bw=36;bx=cx-bw//2;by=cy-8
        pygame.draw.rect(surf,DARK,(bx,by,bw,5))
        pygame.draw.rect(surf,(50,200,80) if self.hp/self.MAX_HP>0.6 else RED,(bx,by,int(bw*self.hp/self.MAX_HP),5))

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
    def draw(self,surf,cam_x=0):
        sx=int(self.x)-cam_x;cy=int(self.y);f=self.facing
        pygame.draw.rect(surf,(40,40,40),pygame.Rect(sx,cy+28,self.W,14))
        for i in range(sx,sx+self.W,10): pygame.draw.line(surf,(60,60,60),(i,cy+28),(i,cy+42),2)
        pygame.draw.circle(surf,(50,50,50),(sx+10,cy+35),8);pygame.draw.circle(surf,(50,50,50),(sx+self.W-10,cy+35),8)
        pygame.draw.rect(surf,(80,90,60),pygame.Rect(sx+4,cy+14,self.W-8,20))
        pygame.draw.rect(surf,(90,100,70),pygame.Rect(sx+20,cy+4,40,14))
        pygame.draw.line(surf,(60,70,50),(sx+40,cy+10),(sx+40+f*30,cy+10),6)
        bw=70;bx=sx+(self.W-bw)//2;by=cy-14
        pygame.draw.rect(surf,DARK,(bx,by,bw,7))
        hp_r=self.hp/self.MAX_HP
        pygame.draw.rect(surf,(50,200,80) if hp_r>0.5 else YELLOW if hp_r>0.25 else RED,(bx,by,int(bw*hp_r),7))
        pygame.draw.rect(surf,GRAY,(bx,by,bw,7),1)
        lf=pygame.font.SysFont("consolas",10,bold=True);lb=lf.render("TANK",True,(200,200,100))
        surf.blit(lb,(sx+(self.W-lb.get_width())//2,by-12))

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
    def take_damage(self,amount,is_rocket=False):
        self.hp-=amount;SFX.play(SFX.hit_enemy);PARTICLES.spawn_sparks(self.rect.centerx,self.rect.centery,4)
        if self.hp<=0: self.alive=False;PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=0.8)
    def draw(self,surf,cam_x=0):
        sx=int(self.x)-cam_x;cx=sx+self.W//2;cy=int(self.y)+self.H//2
        pygame.draw.rect(surf,(60,60,80),pygame.Rect(sx+8,cy-6,20,12),border_radius=4)
        t=pygame.time.get_ticks()
        for angle in [t*0.05,t*0.05+math.pi/2]:
            rx=int(math.cos(angle)*16);ry=int(math.sin(angle)*4)
            pygame.draw.line(surf,(180,180,200),(cx-rx,cy-6+ry),(cx+rx,cy-6-ry),2)
        pygame.draw.circle(surf,(40,40,40),(cx,cy+6),4);pygame.draw.circle(surf,RED,(cx,cy+6),2)
        bw=30;bx=cx-bw//2;by=int(self.y)-10
        pygame.draw.rect(surf,DARK,(bx,by,bw,4))
        pygame.draw.rect(surf,(50,200,80) if self.hp/self.MAX_HP>0.5 else RED,(bx,by,int(bw*self.hp/self.MAX_HP),4))

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
    def take_damage(self,amount,is_rocket=False):
        dmg=amount if is_rocket else max(1,amount//3)
        self.hp-=dmg;SFX.play(SFX.hit_enemy);PARTICLES.spawn_sparks(self.rect.centerx,self.rect.centery,8)
        if self.hp<=0:
            self.alive=False;PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=1.8)
            SFX.play(SFX.big_explosion)
    def draw(self,surf,cam_x=0):
        sx=int(self.x)-cam_x;cx=sx+self.W//2;cy=int(self.y)+self.H//2
        pygame.draw.ellipse(surf,(80,80,100),pygame.Rect(sx+10,cy-12,60,24))
        pygame.draw.ellipse(surf,(60,180,220),pygame.Rect(sx+14,cy-8,22,16))
        pygame.draw.rect(surf,(70,70,90),pygame.Rect(sx+60,cy-4,28,8))
        for angle in [self.rotor_angle,self.rotor_angle+math.pi]:
            pygame.draw.line(surf,(160,160,180),(sx+self.W-4,cy),(sx+self.W-4+int(math.cos(angle)*10),cy+int(math.sin(angle)*10)),2)
        for angle in [self.rotor_angle*1.5+i*math.pi/2 for i in range(4)]:
            rx=int(math.cos(angle)*38);ry=int(math.sin(angle)*6)
            pygame.draw.line(surf,(180,180,200),(cx-rx,cy-14+ry),(cx+rx,cy-14-ry),3)
        bw=80;bx=cx-bw//2;by=int(self.y)-14
        pygame.draw.rect(surf,DARK,(bx,by,bw,7))
        hp_r=self.hp/self.MAX_HP
        pygame.draw.rect(surf,(50,200,80) if hp_r>0.5 else YELLOW if hp_r>0.25 else RED,(bx,by,int(bw*hp_r),7))
        pygame.draw.rect(surf,GRAY,(bx,by,bw,7),1)
        lf=pygame.font.SysFont("consolas",10,bold=True);lb=lf.render("HELI",True,(200,200,100))
        surf.blit(lb,(cx-lb.get_width()//2,by-12))

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
    def draw(self,surf,cam_x=0):
        sx=int(self.x)-cam_x;cx=sx+self.W//2;cy=int(self.y)+self.H//2;f=1 if self.vx>0 else -1
        pts=[(sx,cy+4),(sx+f*20,cy-2),(sx+f*60,cy-2),(sx+f*self.W,cy+2),(sx+f*60,cy+8),(sx+f*20,cy+8)]
        pygame.draw.polygon(surf,(60,80,80),pts)
        pygame.draw.ellipse(surf,(60,200,220),pygame.Rect(sx+f*10-5,cy-6,22,12))
        wing_x=sx+f*35
        pygame.draw.polygon(surf,(50,70,70),[(wing_x,cy+2),(wing_x+f*10,cy+20),(wing_x+f*30,cy+2)])
        tail_x=sx+(0 if f>0 else self.W)
        pygame.draw.polygon(surf,ORANGE,[(tail_x,cy-4),(tail_x,cy+4),(tail_x-f*random.randint(10,25),cy)])
        bw=60;bx=cx-bw//2;by=int(self.y)-14
        pygame.draw.rect(surf,DARK,(bx,by,bw,5))
        pygame.draw.rect(surf,(50,200,80) if self.hp/self.MAX_HP>0.5 else RED,(bx,by,int(bw*self.hp/self.MAX_HP),5))
        lf=pygame.font.SysFont("consolas",10,bold=True);lb=lf.render("JET",True,(200,200,100))
        surf.blit(lb,(cx-lb.get_width()//2,by-12))

class Boss:
    W=60;H=80;SPEED=1.8;SHOOT_RATE=700;BURST_SIZE=3;is_air=False
    def __init__(self,x,y):
        diff=get_diff()
        self.x=float(x);self.y=float(y);self.vy=0.0
        self.MAX_HP=int(500*diff["enemy_hp_mult"]);self.hp=self.MAX_HP
        self.alive=True;self.last_shot=0;self.facing=-1
        self.phase=1;self.walk_frame=0;self.walk_timer=0
        self.jump_timer=0;self.roar_done=False;self.on_ground=False;self.summon_timer=600
    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    def update(self,player,bullets,enemy_rockets):
        if not self.roar_done: SFX.play(SFX.boss_roar);self.roar_done=True
        if self.hp<self.MAX_HP*0.66: self.phase=max(self.phase,2)
        if self.hp<self.MAX_HP*0.33: self.phase=3
        self.vy=min(self.vy+0.7,18);self.y+=self.vy;self.on_ground=False
        for plat in current_platforms:
            r=self.rect
            if r.colliderect(plat) and self.vy>=0:
                if r.bottom-self.vy<=plat.top+abs(self.vy)+2:
                    self.y=plat.top-self.H;self.vy=0;self.on_ground=True
        dx=player.x-self.x;sp=self.SPEED*(1+self.phase*0.2)*get_diff()["enemy_speed_mult"]
        if abs(dx)>10:
            self.x+=sp*(1 if dx>0 else -1);self.facing=1 if dx>0 else -1
            self.walk_timer+=1
            if self.walk_timer>6: self.walk_frame=(self.walk_frame+1)%4;self.walk_timer=0
        if self.phase>=2:
            self.jump_timer+=1
            if self.jump_timer>200 and self.on_ground: self.vy=-22;self.jump_timer=0
        if self.phase==3:
            self.summon_timer-=1
            if self.summon_timer<=0:
                self.summon_timer=300
                ox=self.rect.centerx;oy=self.rect.centery
                dx2=player.rect.centerx-ox;dy2=player.rect.centery-oy
                d=math.hypot(dx2,dy2) or 1
                enemy_rockets.append(Rocket(ox,oy,dx2/d*10,dy2/d*10,35,ROCKET_COL))
                SFX.play(SFX.shoot_rocket)
        self.x=max(0,min(WORLD_WIDTH-self.W,self.x))
        now=pygame.time.get_ticks();rate=int(self.SHOOT_RATE//self.phase*get_diff()["shoot_rate_mult"])
        if now-self.last_shot>=rate and abs(dx)<800:
            self.last_shot=now;spread=self.BURST_SIZE+self.phase;SFX.play(SFX.shoot_rifle)
            ox=self.rect.centerx;oy=self.rect.centery
            dmg=int(15*get_diff()["enemy_dmg_mult"])
            for i in range(spread):
                off=(i-spread//2)*0.07
                dx2=player.rect.centerx-ox;dy2=player.rect.centery-oy
                dist=math.hypot(dx2,dy2) or 1
                angle=math.atan2(dy2,dx2)+off
                bullets.append(Bullet(ox,oy+i*8-spread*4,math.cos(angle)*13,math.sin(angle)*13,dmg,(255,80,80)))
                PARTICLES.spawn_muzzle_flash(ox+self.facing*25,oy,self.facing)
    def take_damage(self,amount):
        self.hp-=amount;PARTICLES.spawn_blood(self.rect.centerx,self.rect.centery,6)
        if self.hp<=0:
            self.alive=False;PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=3.0)
            SFX.play(SFX.big_explosion)
    def draw(self,surf,cam_x=0):
        sx=int(self.x)-cam_x;cx=sx+self.W//2;cy=int(self.y);f=self.facing
        pc={1:(140,40,40),2:(180,30,30),3:(220,20,20)}.get(self.phase,(140,40,40))
        if self.phase>=2:
            aura=pygame.Surface((120,120),pygame.SRCALPHA)
            pulse=abs(math.sin(pygame.time.get_ticks()*0.003))*40
            col=(255,50,50) if self.phase==3 else (200,80,20)
            pygame.draw.circle(aura,(*col,int(20+pulse)),(60,60),60)
            surf.blit(aura,(cx-60,cy-10))
        pygame.draw.circle(surf,(200,145,105),(cx,cy+14),14)
        pygame.draw.rect(surf,(60,20,20),pygame.Rect(cx-16,cy+6,32,20))
        pygame.draw.rect(surf,pc,pygame.Rect(cx-15,cy+28,30,28))
        lo=[0,7,0,-7][self.walk_frame]
        pygame.draw.line(surf,pc,(cx-7,cy+56),(cx-7,cy+80+lo),8)
        pygame.draw.line(surf,pc,(cx+7,cy+56),(cx+7,cy+80-lo),8)
        pygame.draw.line(surf,pc,(cx,cy+30),(cx+f*26,cy+38),6)
        pygame.draw.rect(surf,(30,30,30),pygame.Rect(cx+f*16,cy+32,28,8))
        bw=120;bx=cx-bw//2;by=cy-22
        pygame.draw.rect(surf,DARK,(bx,by,bw,12))
        hc=(255,50,50) if self.phase==3 else (220,100,20) if self.phase==2 else (200,50,50)
        pygame.draw.rect(surf,hc,(bx,by,int(bw*self.hp/self.MAX_HP),12))
        pygame.draw.rect(surf,WHITE,(bx,by,bw,12),1)
        lf=pygame.font.SysFont("consolas",13,bold=True)
        lb=lf.render(f"GENERAL  [PHASE {self.phase}]",True,(255,200,50))
        surf.blit(lb,(cx-lb.get_width()//2,by-18))

# ═══════════════════════════════════════════════════
#  SCREEN SHAKE
# ═══════════════════════════════════════════════════
def get_shake_offset():
    global screen_shake
    if screen_shake>0:
        ox=random.randint(-screen_shake,screen_shake)
        oy=random.randint(-screen_shake,screen_shake)
        screen_shake=max(0,screen_shake-1);return ox,oy
    return 0,0

# ═══════════════════════════════════════════════════
#  FONTS & HUD
# ═══════════════════════════════════════════════════
font_big   = pygame.font.SysFont("consolas",28,bold=True)
font_med   = pygame.font.SysFont("consolas",22,bold=True)
font_small = pygame.font.SysFont("consolas",16)
font_tiny  = pygame.font.SysFont("consolas",13)

WEAPON_KEYS={pygame.K_1:PISTOLE,pygame.K_2:STURMGEWEHR,pygame.K_3:SCHARFSCHUETZE,
             pygame.K_4:SCHROTFLINTE,pygame.K_5:RAKETENWERFER,pygame.K_6:STINGER,pygame.K_7:MESSER}

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

def draw_hud(surf,player,zone_num,zone_name,enemies_left,air_left):
    panel=pygame.Surface((430,132),pygame.SRCALPHA);panel.fill((0,0,0,160))
    surf.blit(panel,(8,8))
    for i in range(player.MAX_LIVES):
        col=RED if i<player.lives else (50,20,20)
        pygame.draw.circle(surf,col,(28+i*28,28),9);pygame.draw.circle(surf,col,(40+i*28,28),9)
        pygame.draw.polygon(surf,col,[(20+i*28,32),(48+i*28,32),(34+i*28,47)])
    pygame.draw.rect(surf,DARK,(14,52,200,14))
    hr=player.hp/player.MAX_HP;hc=GREEN if hr>0.5 else YELLOW if hr>0.25 else RED
    pygame.draw.rect(surf,hc,(14,52,int(200*hr),14));pygame.draw.rect(surf,GRAY,(14,52,200,14),1)
    surf.blit(font_tiny.render(f"HP {player.hp}/{player.MAX_HP}",True,WHITE),(220,53))
    if player.shield_timer>0:
        sw=int(200*player.shield_timer/1800)
        pygame.draw.rect(surf,(40,80,150),(14,68,200,6))
        pygame.draw.rect(surf,(80,160,255),(14,68,sw,6))
        surf.blit(font_tiny.render("SCHILD",True,(80,160,255)),(220,67))
    weapons_row1=[(PISTOLE,"[1]"),(STURMGEWEHR,"[2]"),(SCHARFSCHUETZE,"[3]"),(SCHROTFLINTE,"[4]")]
    weapons_row2=[(RAKETENWERFER,"[5]"),(STINGER,"[6]"),(MESSER,"[7]")]
    for i,(w,label) in enumerate(weapons_row1):
        col=YELLOW if player.weapon==w else GRAY
        ammo_str=f"({w.ammo})" if w.ammo is not None else ""
        lv_str=f"Lv{WSTATS.get_level(w.name)}" if WSTATS.get_level(w.name)>0 else ""
        surf.blit(font_tiny.render(f"{label}{w.name[:7]}{ammo_str}{lv_str}",True,col),(14+i*100,78))
    for i,(w,label) in enumerate(weapons_row2):
        col=YELLOW if player.weapon==w else GRAY
        ammo_str=f"({w.ammo})" if w.ammo is not None else ""
        surf.blit(font_tiny.render(f"{label}{w.name[:10]}{ammo_str}",True,col),(14+i*130,92))
    surf.blit(font_tiny.render(f"Granaten: {'X '*player.grenades}",True,ORANGE),(14,108))
    boosts=[]
    if player.speed_boost_timer>0: boosts.append(("SPEED",(200,100,255)))
    if player.dmg_boost_timer>0:   boosts.append(("2xDMG",(255,120,20)))
    for i,(b,bc) in enumerate(boosts):
        surf.blit(font_tiny.render(b,True,bc),(220+i*60,78))
    sc=font_med.render(f"SCORE: {player.score}",True,YELLOW)
    surf.blit(sc,(WIDTH//2-sc.get_width()//2,14))
    # Schwierigkeitsgrad-Anzeige
    diff_cfg=get_diff()
    df=font_tiny.render(diff_cfg["label"],True,diff_cfg["color"])
    surf.blit(df,(WIDTH//2-df.get_width()//2,34))
    zt=font_small.render(f"ZONE {zone_num}/{NUM_ZONES}",True,WHITE)
    nt=font_tiny.render(zone_name,True,GRAY)
    et=font_tiny.render(f"Boden: {enemies_left}",True,(255,150,150))
    at=font_tiny.render(f"Luft:  {air_left}",True,CYAN)
    surf.blit(zt,(WIDTH-zt.get_width()-14,14));surf.blit(nt,(WIDTH-nt.get_width()-14,38))
    surf.blit(et,(WIDTH-et.get_width()-14,56));surf.blit(at,(WIDTH-at.get_width()-14,72))
    draw_weapon_xp_bar(surf,player.weapon)
    if player.pickup_msg_timer>0:
        alpha=min(255,player.pickup_msg_timer*4)
        pm=font_med.render(f"+ {player.pickup_msg}",True,YELLOW)
        ps=pygame.Surface((pm.get_width()+20,pm.get_height()+10),pygame.SRCALPHA)
        ps.fill((0,0,0,100));ps.blit(pm,(10,5));ps.set_alpha(alpha)
        surf.blit(ps,(WIDTH//2-ps.get_width()//2,HEIGHT//2-80))

# ═══════════════════════════════════════════════════
#  WELT
# ═══════════════════════════════════════════════════
def draw_world(surf,zone_cfg,cam_x,tick=0):
    sky=zone_cfg["sky"];surf.fill(sky);par_off=int(cam_x*0.35)
    WEATHER.draw_behind(surf)

    if sky==(28,38,58):
        pygame.draw.circle(surf,(220,220,200),(900,60),28)
        pygame.draw.circle(surf,(28,38,58),(912,54),20)
        for i in range(4):
            cx2=(i*380+par_off//2)%WIDTH+100;cy2=40+i*15
            pygame.draw.ellipse(surf,(38,48,68),(cx2,cy2,180,40))
        for rx,rw,rh in [(0,100,200),(130,80,150),(260,120,220),(450,90,170),(620,130,200),(820,100,160),(1010,110,190)]:
            sx=rx-par_off
            if -200<sx<WIDTH+200:
                pygame.draw.rect(surf,(18,24,38),(sx,GROUND_Y-rh,rw,rh))
                for wy in range(GROUND_Y-rh+15,GROUND_Y-10,28):
                    for wx in range(sx+8,sx+rw-8,18):
                        lit=(wx+wy*3+tick//12)%40
                        wc=YELLOW if lit<12 and (wx+wy)%55<28 else (8,10,18)
                        pygame.draw.rect(surf,wc,(wx,wy,9,13))
    elif sky==(18,42,20):
        for layer in range(3):
            scale=0.6+layer*0.2
            for tx in range(-200,WORLD_WIDTH+200,int(85/scale)):
                sx=int(tx*scale)-par_off//2
                if -150<sx<WIDTH+150:
                    h=int((150+(tx*9)%90)*scale)
                    dg=(int(8+(tx*3)%18),int(40+(tx*5)%20),8)
                    col=(min(dg[0]+layer*10,255),min(dg[1]+layer*15,255),min(dg[2]+layer*5,255))
                    pygame.draw.polygon(surf,col,[(sx+int(18*scale),GROUND_Y-h),(sx+int(43*scale),GROUND_Y-h-int(65*scale)),(sx+int(68*scale),GROUND_Y-h)])
                    pygame.draw.rect(surf,(40,22,12),(sx+int(35*scale),GROUND_Y-h+5,int(14*scale),h-5))
    elif sky==(80,55,30):
        pygame.draw.circle(surf,(255,220,80),(WIDTH-80,60),40)
        for dx2 in range(-100,WORLD_WIDTH+100,200):
            sx=dx2-par_off
            if -200<sx<WIDTH+200:
                h=60+(dx2*7)%80
                pygame.draw.ellipse(surf,(120,90,40),(sx,GROUND_Y-h,200,h*2))
        for i in range(0,WIDTH,25):
            wave=int(math.sin((i+tick*0.4)*0.08)*4)
            pygame.draw.line(surf,(150,110,50),(i,GROUND_Y-4+wave),(i+25,GROUND_Y-4+wave),1)
    elif sky==(12,12,28):
        for i in range(60):
            sx2=(i*137+23)%WIDTH;sy2=(i*97+11)%(HEIGHT//2-20)
            pygame.draw.circle(surf,(220,220,255),(sx2,sy2),1)
        for rx,rw,rh in [(0,220,195),(270,200,215),(530,240,175),(810,210,230),(1080,200,185)]:
            sx=rx-par_off
            if -300<sx<WIDTH+300:
                pygame.draw.rect(surf,(10,10,25),(sx,GROUND_Y-rh,rw,rh))
                for wy in range(GROUND_Y-rh+20,GROUND_Y-10,35):
                    for wx in range(sx+12,sx+rw-12,25):
                        fl=(wx*13+wy*7+tick//8)%22
                        wc=(50,50,150) if (wx+wy)%50<25 and fl>2 else DARK
                        pygame.draw.rect(surf,wc,(wx,wy,12,16))
        for i in range(2):
            lx=(i*900+300)%WORLD_WIDTH;ls=lx-cam_x
            if -200<ls<WIDTH+200:
                angle_r=math.sin(tick*0.015+i*2.1)*0.5
                ex=int(ls+math.sin(angle_r)*300);ey=GROUND_Y-20
                _spotlight_surf.fill((0,0,0,0))
                pygame.draw.polygon(_spotlight_surf,(255,255,200,18),[(ls,0),(ls-40,0),(ex-25,ey),(ex+25,ey),(ls+40,0)])
                surf.blit(_spotlight_surf,(0,0))
                pygame.draw.circle(surf,(255,255,180),(ls,0),8)
    elif sky==(160,190,220):
        for i in range(3):
            nl=pygame.Surface((WIDTH,HEIGHT//2),pygame.SRCALPHA)
            a3=int(20+math.sin(tick*0.02+i)*15)
            col3=[(50,200,100),(100,80,220),(50,180,180)][i]
            ox3=int(math.sin(tick*0.008+i)*200)
            pygame.draw.ellipse(nl,(*col3,a3),(ox3+i*200,20,300,HEIGHT//3))
            surf.blit(nl,(0,0))
        for mx in range(-100,WORLD_WIDTH+100,280):
            sx=mx-par_off
            if -300<sx<WIDTH+300:
                h=100+(mx*11)%120
                pygame.draw.polygon(surf,(170,190,215),[(sx,GROUND_Y),(sx+160,GROUND_Y),(sx+80,GROUND_Y-h)])
                pygame.draw.polygon(surf,(210,230,250),[(sx+45,GROUND_Y-h+35),(sx+80,GROUND_Y-h),(sx+115,GROUND_Y-h+35)])
    elif sky==(8,5,18):
        for rx,rw,rh in [(0,260,240),(320,240,270),(680,270,220),(1000,250,280),(1320,240,230),(1660,270,260)]:
            sx=rx-par_off
            if -300<sx<WIDTH+300:
                pygame.draw.rect(surf,(15,8,25),(sx,GROUND_Y-rh,rw,rh))
                pygame.draw.rect(surf,(35,18,50),(sx,GROUND_Y-rh,rw,rh),2)
                for zx in range(sx,sx+rw-10,25): pygame.draw.rect(surf,(20,10,35),(zx,GROUND_Y-rh-10,15,12))
                for wy in range(GROUND_Y-rh+20,GROUND_Y-10,35):
                    for wx in range(sx+12,sx+rw-12,26):
                        fl=(wx*13+wy*7+tick//8)%22
                        wc=(130,20,20) if (wx+wy)%48<24 and fl>2 else DARK
                        pygame.draw.rect(surf,wc,(wx,wy,12,16))

    for plat in current_platforms:
        sr=pygame.Rect(plat.x-cam_x,plat.y,plat.width,plat.height)
        if -plat.width<sr.x<WIDTH+plat.width:
            g=zone_cfg["ground"]
            pygame.draw.rect(surf,g,sr)
            light=(min(g[0]+40,255),min(g[1]+35,255),min(g[2]+20,255))
            dark=(max(g[0]-15,0),max(g[1]-12,0),max(g[2]-8,0))
            if plat.height<=60:
                pygame.draw.rect(surf,light,(sr.x,sr.y,sr.width,4))
                pygame.draw.rect(surf,dark,(sr.x,sr.y+sr.height-4,sr.width,4))
            else:
                pygame.draw.rect(surf,light,sr,3)

# ═══════════════════════════════════════════════════
#  CUTSCENE
# ═══════════════════════════════════════════════════
def show_cutscene(zone_before):
    lines=STORY.get(zone_before,[])
    if not lines: return
    f_title=pygame.font.SysFont("consolas",20,bold=True)
    f_text=pygame.font.SysFont("consolas",18)
    f_hint=pygame.font.SysFont("consolas",14)
    tick=0;done=False;char_index=0;current_line=0;line_timer=0;displayed=[""]
    while not done:
        tick+=1
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN,pygame.K_SPACE,pygame.K_ESCAPE):
                    if current_line<len(lines): displayed=[l for l in lines];current_line=len(lines)
                    else: done=True
            if event.type==pygame.MOUSEBUTTONDOWN: done=True
        line_timer+=1
        if current_line<len(lines):
            line=lines[current_line]
            if char_index<len(line):
                if line_timer%2==0: char_index+=1;displayed[current_line]=line[:char_index]
            else:
                if line_timer>40:
                    current_line+=1;char_index=0;line_timer=0
                    if current_line<len(lines): displayed.append("")
        screen.fill((5,5,15))
        for i in range(20):
            pygame.draw.circle(screen,(30,30,60),((i*137+tick*2)%WIDTH,(i*97+tick)%HEIGHT),1)
        panel=pygame.Surface((WIDTH-100,HEIGHT-100),pygame.SRCALPHA);panel.fill((0,0,0,180))
        screen.blit(panel,(50,50))
        pygame.draw.rect(screen,(80,20,20),(50,50,WIDTH-100,HEIGHT-100),2)
        title_text="EINWEISUNG" if zone_before==0 else f"BERICHT — NACH ZONE {zone_before}"
        title=f_title.render(title_text,True,(220,80,80))
        screen.blit(title,(WIDTH//2-title.get_width()//2,75))
        pygame.draw.line(screen,(80,30,30),(80,105),(WIDTH-80,105),1)
        cx2=160;cy2=HEIGHT//2+20
        pygame.draw.circle(screen,(60,70,60),(cx2,cy2-60),22)
        pygame.draw.rect(screen,(50,65,50),pygame.Rect(cx2-20,cy2-40,40,50))
        pygame.draw.line(screen,(50,65,50),(cx2-20,cy2-35),(cx2-45,cy2-20),5)
        pygame.draw.line(screen,(50,65,50),(cx2+20,cy2-35),(cx2+45,cy2-20),5)
        pygame.draw.arc(screen,(40,55,40),pygame.Rect(cx2-24,cy2-88,48,32),0,math.pi,6)
        pygame.draw.rect(screen,(40,55,40),pygame.Rect(cx2-24,cy2-72,48,12))
        pygame.draw.circle(screen,(200,230,200),(cx2-7,cy2-62),4)
        pygame.draw.circle(screen,(200,230,200),(cx2+7,cy2-62),4)
        for i,line in enumerate(displayed):
            if i>=len(lines): break
            col=WHITE if i<current_line else (220,220,180)
            t=f_text.render(line,True,col);screen.blit(t,(230,130+i*42))
        if current_line<len(lines) and (tick//15)%2==0:
            cursor=f_text.render("_",True,(200,200,100))
            ci=min(current_line,len(displayed)-1)
            tx2=230+f_text.size(displayed[ci])[0] if ci<len(displayed) else 230
            screen.blit(cursor,(tx2,130+ci*42))
        if current_line>=len(lines):
            hint=f_hint.render("[ ENTER / SPACE — Weiter ]",True,(150,150,100))
            hs=pygame.Surface((hint.get_width()+20,hint.get_height()+8),pygame.SRCALPHA)
            hs.fill((0,0,0,80));hs.blit(hint,(10,4));hs.set_alpha(int(128+abs(math.sin(tick*0.05))*127))
            screen.blit(hs,(WIDTH//2-hs.get_width()//2,HEIGHT-75))
        pygame.display.flip();clock.tick(FPS)

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
    btns=[PauseBtn("▶  WEITER",   cx,240),
          PauseBtn("◉  SKIN",     cx,295),
          PauseBtn("⌂  HAUPTMENÜ",cx,350),
          PauseBtn("✕  BEENDEN",  cx,405)]

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
                if btns[2].clicked((mx,my)): return "menu"
                if btns[3].clicked((mx,my)): pygame.quit();sys.exit()

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
def draw_menu_bg(surf,tick):
    surf.fill((8,12,22))
    for i in range(60):
        x=(i*137+tick//3)%WIDTH;y=(i*97+tick//5)%(HEIGHT//2)
        r=1+i%2;a=100+(tick*2+i*30)%155
        s=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
        pygame.draw.circle(s,(200,220,255,a),(r,r),r);surf.blit(s,(x,y))
    for rx,rw,rh in [(0,120,180),(130,90,130),(240,150,200),(450,100,160),(600,130,190),(780,110,150),(940,140,170),(1100,120,140)]:
        pygame.draw.rect(surf,(12,18,30),(rx,HEIGHT-rh,rw,rh))
    pygame.draw.rect(surf,(18,24,36),(0,HEIGHT-40,WIDTH,40))
    glow=pygame.Surface((400,300),pygame.SRCALPHA)
    pulse=abs(math.sin(tick*0.02))*30
    pygame.draw.ellipse(glow,(200,30,30,int(18+pulse)),(0,0,400,300))
    surf.blit(glow,(WIDTH//2-200,HEIGHT//2-100))

class MenuButton:
    def __init__(self,text,x,y,w=260,h=50):
        self.text=text;self.rect=pygame.Rect(x-w//2,y-h//2,w,h)
        self.hovered=False;self.font=pygame.font.SysFont("consolas",20,bold=True)
    def draw(self,surf):
        bg=(180,30,30) if self.hovered else (55,15,15)
        brd=(220,60,60) if self.hovered else (100,30,30)
        tc=WHITE if self.hovered else (200,160,160)
        if self.hovered:
            gs=pygame.Surface((self.rect.w+10,self.rect.h+10),pygame.SRCALPHA)
            pygame.draw.rect(gs,(220,50,50,55),(0,0,self.rect.w+10,self.rect.h+10),border_radius=8)
            surf.blit(gs,(self.rect.x-5,self.rect.y-5))
        pygame.draw.rect(surf,bg,self.rect,border_radius=6)
        pygame.draw.rect(surf,brd,self.rect,2,border_radius=6)
        t=self.font.render(self.text,True,tc)
        surf.blit(t,(self.rect.centerx-t.get_width()//2,self.rect.centery-t.get_height()//2))
    def update(self,pos): self.hovered=self.rect.collidepoint(pos)
    def clicked(self,pos): return self.rect.collidepoint(pos)

def show_difficulty_select():
    global current_difficulty
    f1=pygame.font.SysFont("consolas",36,bold=True)
    f2=pygame.font.SysFont("consolas",15)
    back=MenuButton("< ZURUECK",WIDTH//2,HEIGHT-55,w=200,h=44)
    tick=0
    while True:
        tick+=1;mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if back.clicked((mx,my)): return
                for i,key in enumerate(["easy","normal","hard"]):
                    bx=WIDTH//2-300+i*200;by=HEIGHT//2
                    if pygame.Rect(bx-80,by-40,160,80).collidepoint(mx,my):
                        current_difficulty=key
        draw_menu_bg(screen,tick)
        t=f1.render("SCHWIERIGKEITSGRAD",True,YELLOW)
        screen.blit(t,(WIDTH//2-t.get_width()//2,100))
        pygame.draw.line(screen,(100,80,30),(WIDTH//2-220,148),(WIDTH//2+220,148),2)
        for i,key in enumerate(["easy","normal","hard"]):
            cfg=DIFFICULTY_SETTINGS[key]
            bx=WIDTH//2-300+i*200;by=HEIGHT//2
            is_sel=(current_difficulty==key)
            col=cfg["color"]
            border_w=3 if is_sel else 1
            pygame.draw.rect(screen,col if is_sel else (40,40,50),(bx-80,by-40,160,80),border_radius=8)
            pygame.draw.rect(screen,col,(bx-80,by-40,160,80),border_w,border_radius=8)
            lf=pygame.font.SysFont("consolas",20,bold=True)
            lt=lf.render(cfg["label"],True,WHITE if is_sel else col)
            screen.blit(lt,(bx-lt.get_width()//2,by-35))
            for j,line in enumerate(cfg["desc"].split("—")):
                dt=f2.render(line.strip(),True,GRAY if not is_sel else WHITE)
                screen.blit(dt,(bx-dt.get_width()//2,by-5+j*18))
            if is_sel:
                check=lf.render("✓",True,col)
                screen.blit(check,(bx-check.get_width()//2,by+30))
        back.update((mx,my));back.draw(screen)
        pygame.display.flip();clock.tick(FPS)

def show_achievements():
    achieved=load_achievements()
    back=MenuButton("< ZURUECK",WIDTH//2,HEIGHT-55,w=200,h=44)
    tick=0
    while True:
        tick+=1;mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if back.clicked((mx,my)): return
        draw_menu_bg(screen,tick)
        f1=pygame.font.SysFont("consolas",34,bold=True)
        f2=pygame.font.SysFont("consolas",14)
        t=f1.render("ACHIEVEMENTS",True,YELLOW);screen.blit(t,(WIDTH//2-t.get_width()//2,45))
        pygame.draw.line(screen,(100,80,30),(WIDTH//2-250,88),(WIDTH//2+250,88),2)
        keys=list(ACHIEVEMENTS_DEF.keys())
        for idx,key in enumerate(keys):
            col_idx=idx%4;row_idx=idx//4
            x=WIDTH//2-580+col_idx*300;y=105+row_idx*100
            cfg=ACHIEVEMENTS_DEF[key]
            unlocked=key in achieved
            panel=pygame.Surface((280,85),pygame.SRCALPHA)
            panel.fill((30,30,50,180) if unlocked else (15,15,20,140))
            pygame.draw.rect(panel,YELLOW if unlocked else (60,60,80),(0,0,280,85),1,border_radius=6)
            if unlocked: pygame.draw.circle(panel,YELLOW,(264,14),8)
            icon_f=pygame.font.SysFont("segoe ui emoji",24)
            icon_t=icon_f.render(cfg["icon"],True,WHITE if unlocked else GRAY)
            panel.blit(icon_t,(10,10))
            nf=pygame.font.SysFont("consolas",14,bold=True)
            nt=nf.render(cfg["name"],True,WHITE if unlocked else GRAY)
            panel.blit(nt,(44,12))
            dt=f2.render(cfg["desc"],True,GRAY);panel.blit(dt,(12,48))
            if not unlocked:
                lock=f2.render("GESPERRT",True,(80,80,80));panel.blit(lock,(12,66))
            screen.blit(panel,(x,y))
        count=len(achieved);total=len(ACHIEVEMENTS_DEF)
        prog=f2.render(f"Freigeschaltet: {count}/{total}",True,GRAY)
        screen.blit(prog,(WIDTH//2-prog.get_width()//2,HEIGHT-80))
        back.update((mx,my));back.draw(screen)
        pygame.display.flip();clock.tick(FPS)

def show_skin_select():
    global current_skin
    achieved=load_achievements()
    skin_keys=list(SKINS.keys())
    idx=skin_keys.index(current_skin)
    back=MenuButton("< ZURUECK",WIDTH//2,HEIGHT-55,w=200,h=44)
    tick=0
    while True:
        tick+=1;mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if back.clicked((mx,my)): return
                for i,key in enumerate(skin_keys):
                    bx=WIDTH//2-300+i*200;by=HEIGHT//2-20
                    if pygame.Rect(bx-80,by-60,160,120).collidepoint(mx,my):
                        sk=SKINS[key]
                        if sk["unlock"] is None or sk["unlock"] in achieved:
                            current_skin=key;idx=i
        draw_menu_bg(screen,tick)
        f1=pygame.font.SysFont("consolas",34,bold=True)
        f2=pygame.font.SysFont("consolas",14)
        t=f1.render("CHARAKTER-SKIN",True,YELLOW);screen.blit(t,(WIDTH//2-t.get_width()//2,45))
        pygame.draw.line(screen,(100,80,30),(WIDTH//2-220,88),(WIDTH//2+220,88),2)
        for i,key in enumerate(skin_keys):
            sk=SKINS[key]
            bx=WIDTH//2-300+i*200;by=HEIGHT//2-20
            is_sel=(key==current_skin)
            unlocked=sk["unlock"] is None or sk["unlock"] in achieved
            col=sk["body"] if unlocked else (50,50,60)
            panel=pygame.Surface((160,120),pygame.SRCALPHA)
            panel.fill((*col,60) if unlocked else (15,15,20,100))
            border_col=WHITE if is_sel else (col if unlocked else (50,50,60))
            pygame.draw.rect(panel,border_col,(0,0,160,120),2 if not is_sel else 3,border_radius=8)
            # Mini-Soldat Preview
            pcx=80;pcy=50
            pygame.draw.circle(panel,sk["head"],(pcx,pcy-15),10)
            pygame.draw.rect(panel,sk["helmet"],pygame.Rect(pcx-10,pcy-24,20,10))
            pygame.draw.rect(panel,sk["body"],pygame.Rect(pcx-8,pcy-5,16,18))
            pygame.draw.rect(panel,sk["vest"],pygame.Rect(pcx-6,pcy-4,12,14))
            lf=pygame.font.SysFont("consolas",12,bold=True)
            lt=lf.render(sk["label"],True,WHITE if unlocked else GRAY)
            panel.blit(lt,(80-lt.get_width()//2,78))
            if not unlocked:
                lk=f2.render("GESPERRT",True,(80,80,80));panel.blit(lk,(80-lk.get_width()//2,96))
            if is_sel:
                ct=lf.render("✓ AKTIV",True,YELLOW);panel.blit(ct,(80-ct.get_width()//2,96))
            screen.blit(panel,(bx-80,by-60))
        # Beschreibung aktiver Skin
        sk=SKINS[current_skin]
        dt=f2.render(sk["desc"],True,GRAY);screen.blit(dt,(WIDTH//2-dt.get_width()//2,HEIGHT//2+90))
        back.update((mx,my));back.draw(screen)
        pygame.display.flip();clock.tick(FPS)

def show_main_menu():
    btns=[MenuButton("SPIELEN",WIDTH//2,240),
          MenuButton("SCHWIERIGKEIT",WIDTH//2,300),
          MenuButton("SKINS",WIDTH//2,360),
          MenuButton("HIGHSCORES",WIDTH//2,420),
          MenuButton("ACHIEVEMENTS",WIDTH//2,480),
          MenuButton("STEUERUNG",WIDTH//2,540)]
    sf=pygame.font.SysFont("consolas",55,bold=True);tf=pygame.font.SysFont("consolas",16)
    tick=0
    while True:
        tick+=1;mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: pygame.quit();sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if btns[0].clicked((mx,my)): return "play"
                if btns[1].clicked((mx,my)): show_difficulty_select()
                if btns[2].clicked((mx,my)): show_skin_select()
                if btns[3].clicked((mx,my)): show_highscores()
                if btns[4].clicked((mx,my)): show_achievements()
                if btns[5].clicked((mx,my)): show_controls()
        draw_menu_bg(screen,tick)
        sh=sf.render("PROJEKT FRONTLINE",True,(90,10,10))
        screen.blit(sh,(WIDTH//2-sh.get_width()//2+3,60))
        t1=sf.render("PROJEKT FRONTLINE",True,(220,50,50))
        screen.blit(t1,(WIDTH//2-t1.get_width()//2,57))
        alpha=180+int(abs(math.sin(tick*0.04))*75)
        sub=tf.render("[ TAKTISCHER 2D-SHOOTER  v6.0 ]",True,(min(255,alpha),min(255,alpha//2),50))
        screen.blit(sub,(WIDTH//2-sub.get_width()//2,120))
        # Aktuelle Einstellungen
        diff_cfg=get_diff();sk=SKINS[current_skin]
        info=tf.render(f"Schwierigkeit: {diff_cfg['label']}   |   Skin: {sk['label']}",True,GRAY)
        screen.blit(info,(WIDTH//2-info.get_width()//2,142))
        hint=tf.render("WASD: Bewegen | SPACE: Springen | Klick: Schiessen | G: Granate | 1-7: Waffe | ESC: Pause",True,(70,70,90))
        screen.blit(hint,(WIDTH//2-hint.get_width()//2,HEIGHT-20))
        for b in btns: b.update((mx,my));b.draw(screen)
        pygame.display.flip();clock.tick(FPS)

def show_highscores():
    scores=load_highscores();back=MenuButton("< ZURUECK",WIDTH//2,HEIGHT-55,w=200,h=44)
    tick=0
    while True:
        tick+=1;mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if back.clicked((mx,my)): return
        draw_menu_bg(screen,tick)
        f1=pygame.font.SysFont("consolas",38,bold=True);f2=pygame.font.SysFont("consolas",18)
        t=f1.render("HIGHSCORES",True,YELLOW);screen.blit(t,(WIDTH//2-t.get_width()//2,50))
        pygame.draw.line(screen,(100,80,30),(WIDTH//2-200,96),(WIDTH//2+200,96),2)
        h=f2.render(f"{'#':<3}  {'NAME':<13}  {'SCORE':>8}  ZONE  SCHWIERIGKEIT",True,(200,200,100))
        screen.blit(h,(WIDTH//2-h.get_width()//2,110))
        if not scores:
            n=pygame.font.SysFont("consolas",17).render("Noch keine Eintraege!",True,GRAY)
            screen.blit(n,(WIDTH//2-n.get_width()//2,160))
        else:
            for i,s in enumerate(scores[:10]):
                col=YELLOW if i==0 else (WHITE if i<3 else GRAY)
                diff_label=DIFFICULTY_SETTINGS.get(s.get("diff","normal"),{}).get("label","Normal")
                row=f2.render(f"{i+1:<3}  {s['name']:<13}  {s['score']:>8}  Zone {s['zone']}  {diff_label}",True,col)
                screen.blit(row,(WIDTH//2-row.get_width()//2,140+i*30))
        back.update((mx,my));back.draw(screen)
        pygame.display.flip();clock.tick(FPS)

def show_controls():
    back=MenuButton("< ZURUECK",WIDTH//2,HEIGHT-50,w=200,h=44)
    ctrls=[("A/D","Bewegen"),("LEERTASTE","Springen"),("LINKSKLICK","Schiessen"),
           ("G","Granate"),("ESC","PAUSE-MENÜ"),
           ("1","Pistole (15 DMG)"),("2","Sturmgewehr (Auto)"),("3","Scharfschuetze"),
           ("4","Schrotflinte"),("5","Raketenwerfer → Tanks"),
           ("6","Stinger → Luft"),("7","Messer (Nahkampf)"),
           ("KILLS","= Waffe levelt auf (bis LV3, +25% DMG)"),
           ("POWERUPS","= Medkit/Schild/Speed/2xDMG")]
    tick=0;kf=pygame.font.SysFont("consolas",15,bold=True);vf=pygame.font.SysFont("consolas",14)
    tf=pygame.font.SysFont("consolas",32,bold=True)
    while True:
        tick+=1;mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if back.clicked((mx,my)): return
        draw_menu_bg(screen,tick)
        t=tf.render("STEUERUNG",True,YELLOW);screen.blit(t,(WIDTH//2-t.get_width()//2,28))
        pygame.draw.line(screen,(100,80,30),(WIDTH//2-200,72),(WIDTH//2+200,72),2)
        for i,(k,v) in enumerate(ctrls):
            col_x=WIDTH//2-390 if i<7 else WIDTH//2+30
            row_y=80+(i%7)*34
            screen.blit(kf.render(k,True,(240,200,60)),(col_x,row_y))
            screen.blit(vf.render(v,True,(180,180,180)),(col_x+150,row_y+2))
        back.update((mx,my));back.draw(screen)
        pygame.display.flip();clock.tick(FPS)

def show_zone_intro(zone_num,zone_name):
    f1=pygame.font.SysFont("consolas",50,bold=True);f2=pygame.font.SysFont("consolas",22)
    for alpha in list(range(0,256,8))+[255]*20+list(range(255,0,-8)):
        screen.fill((0,0,0))
        s=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        t1=f1.render(f"ZONE {zone_num}",True,RED)
        n=zone_name.split(":")[1].strip() if ":" in zone_name else zone_name
        t2=f2.render(n,True,WHITE)
        # Schwierigkeitsanzeige
        diff_cfg=get_diff()
        t3=pygame.font.SysFont("consolas",18).render(diff_cfg["label"],True,diff_cfg["color"])
        s.set_alpha(alpha)
        s.blit(t1,(WIDTH//2-t1.get_width()//2,HEIGHT//2-60))
        s.blit(t2,(WIDTH//2-t2.get_width()//2,HEIGHT//2+10))
        s.blit(t3,(WIDTH//2-t3.get_width()//2,HEIGHT//2+45))
        screen.blit(s,(0,0));pygame.display.flip();clock.tick(30)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()

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
#  ZONE SPIELEN
# ═══════════════════════════════════════════════════
def play_zone(zone_num,player):
    global current_platforms,screen_shake
    cfg=ZONES[zone_num];current_platforms=cfg["platforms"]
    player.x=100.0;player.y=float(current_platforms[0].top-Player.H)
    player.vx=player.vy=0.0;player.hp=player.MAX_HP
    player.invincible=1500;player.shield_timer=0
    player.zone_damage_taken=0;player.knife_only_zone=True
    screen_shake=0;PARTICLES.particles.clear()
    RAKETENWERFER.ammo=RAKETENWERFER.max_ammo;STINGER.ammo=STINGER.max_ammo
    COMBO.count=0;COMBO.timer=0

    WEATHER.set_zone(zone_num)
    camera=Camera();camera.x=0.0
    is_boss_zone=(zone_num==NUM_ZONES)

    enemies=[Enemy(ex,ey,hp=cfg["enemy_hp"],speed=cfg["enemy_speed"],
                   shoot_rate=cfg["enemy_shoot_rate"]) for ex,ey in cfg["enemy_positions"]]
    tanks=[Tank(tx2,ty2) for tx2,ty2 in cfg.get("tank_positions",[])]
    jetpack_soldiers=[JetpackSoldier(jx,jy) for jx,jy in cfg.get("jetpack_positions",[])]
    air_enemies=[]
    for etype,ex2 in cfg.get("air_enemies",[]):
        if etype=="drone":        air_enemies.append(Drone(ex2))
        elif etype=="helicopter": air_enemies.append(Helicopter(ex2))
        elif etype=="jet":        air_enemies.append(Jet(ex2))

    boss=Boss(WORLD_WIDTH-400,current_platforms[0].top-Boss.H) if is_boss_zone else None
    powerups=spawn_powerups(cfg)

    first_kill_done=False
    tank_killed=False

    bullets=[];enemy_bullets=[];grenades=[];enemy_grenades=[]
    player_rockets=[];enemy_rockets=[];tick=0
    paused=False

    show_zone_intro(zone_num,cfg["name"])

    while True:
        tick+=1;clock.tick(FPS);cam_x=int(camera.x)

        for event in pygame.event.get():
            if event.type==pygame.QUIT: return "quit"
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    result=show_pause_menu(player)
                    if result=="menu": return "menu"
                    elif result=="resume": pass
                if event.key in WEAPON_KEYS: player.weapon=WEAPON_KEYS[event.key]
                if event.key==pygame.K_g: player.throw_grenade(grenades)
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                player.shoot(bullets,player_rockets,cam_x)

        keys=pygame.key.get_pressed()
        player.handle_input(keys,bullets,player_rockets,cam_x)
        player.update();camera.update(player.x+player.W//2)
        WEATHER.update();COMBO.update();ACHIEV_NOTIF.update()
        WSTATS.update_notifs()

        # Score-Achievement
        if player.score>=10000: unlock("score_10k")

        # Feinde updaten
        for e in enemies:
            eb=[];e.update(player,eb,enemy_grenades);enemy_bullets.extend(eb)
        for t in tanks:
            tb=[];t.update(player,tb);enemy_bullets.extend(tb)
        for j in jetpack_soldiers:
            jb=[];j.update(player,jb);enemy_bullets.extend(jb)
        for a in air_enemies:
            ab=[];a.update(player,ab);enemy_bullets.extend(ab)
        if boss and boss.alive:
            bb=[];boss.update(player,bb,enemy_rockets);enemy_bullets.extend(bb)

        all_air=[a for a in air_enemies+jetpack_soldiers if a.alive]
        for b in bullets: b.update()
        for r in player_rockets: r.update(all_air)

        # ── Treffer: Spieler-Kugeln ──
        def do_enemy_kill(e_obj, is_air_type=False, is_tank_type=False, is_boss_type=False):
            nonlocal first_kill_done, tank_killed
            COMBO.kill()
            bonus=COMBO.score_bonus()
            diff_mult=get_diff()["score_mult"]
            if is_boss_type: player.score+=int(2000*diff_mult)
            elif is_tank_type: player.score+=int(300*zone_num*diff_mult)
            elif is_air_type: player.score+=int(200*zone_num*diff_mult)
            else: player.score+=int(100*zone_num*bonus*diff_mult)
            # Waffen-Kill registrieren
            leveled=WSTATS.add_kill(player.weapon.name)
            if leveled:
                SFX.play(SFX.level_up)
                if WSTATS.get_level(player.weapon.name)==3: unlock("weapon_max")
            if not first_kill_done: unlock("first_blood");first_kill_done=True
            if is_tank_type and not tank_killed: unlock("tank_killer");tank_killed=True
            if is_air_type:
                player.air_kills+=1
                if player.air_kills>=10: unlock("air_ace")

        for b in bullets:
            if not b.alive: continue
            hit=False
            for e in enemies:
                if not e.alive: continue
                if b.get_rect().colliderect(e.rect):
                    e.take_damage(b.damage);hit=True;b.alive=False
                    if not e.alive: do_enemy_kill(e);break
            if hit: continue
            for t in tanks:
                if not t.alive: continue
                if b.get_rect().colliderect(t.rect):
                    t.take_damage(b.damage,is_rocket=False);hit=True;b.alive=False
                    if not t.alive: do_enemy_kill(t,is_tank_type=True);break
            if hit: continue
            for j in jetpack_soldiers:
                if not j.alive: continue
                if b.get_rect().colliderect(j.rect):
                    j.take_damage(b.damage);hit=True;b.alive=False
                    if not j.alive: do_enemy_kill(j,is_air_type=True);break
            if hit: continue
            for a in air_enemies:
                if not a.alive: continue
                if b.get_rect().colliderect(a.rect):
                    a.take_damage(b.damage);hit=True;b.alive=False
                    if not a.alive: do_enemy_kill(a,is_air_type=True);break
            if hit: continue
            if boss and boss.alive and b.get_rect().colliderect(boss.rect):
                boss.take_damage(b.damage);b.alive=False
                if not boss.alive: do_enemy_kill(boss,is_boss_type=True)

        # Raketen
        for r in player_rockets:
            if not r.alive: continue
            all_targets=enemies+tanks+jetpack_soldiers+air_enemies+([boss] if boss and boss.alive else [])
            for tgt in all_targets:
                if not tgt.alive: continue
                if r.get_rect().colliderect(tgt.rect):
                    hits=r.explode(all_targets)
                    for (t2,dmg) in hits:
                        if not t2.alive: continue
                        if isinstance(t2,(Tank,Helicopter,Jet)): t2.take_damage(dmg,is_rocket=True)
                        else: t2.take_damage(dmg)
                        if not t2.alive:
                            do_enemy_kill(t2,
                                is_air_type=isinstance(t2,(Helicopter,Jet,JetpackSoldier,Drone)),
                                is_tank_type=isinstance(t2,Tank),
                                is_boss_type=isinstance(t2,Boss))
                    screen_shake=12;break

        # Messer
        if player.knife_anim>0:
            kr=player.get_knife_hit_rect()
            for e in enemies:
                if e.alive and kr.colliderect(e.rect):
                    e.take_damage(int(MESSER.damage*player.dmg_mult))
                    if not e.alive: do_enemy_kill(e)

        # Feind-Projektile
        for b in enemy_bullets:
            b.update()
            if b.alive and b.get_rect().colliderect(player.rect):
                player.take_damage(b.damage);b.alive=False
        for r in enemy_rockets:
            r.update()
            if r.alive and r.get_rect().colliderect(player.rect):
                player.take_damage(60);r.alive=False;screen_shake=10

        # Granaten
        all_ground_targets=[e for e in enemies if e.alive]+[t for t in tanks if t.alive]+\
                            [j for j in jetpack_soldiers if j.alive]+([boss] if boss and boss.alive else [])
        for g in grenades+enemy_grenades:
            ghits=g.update(all_ground_targets)
            for (tgt,dmg) in ghits:
                if isinstance(tgt,Tank): tgt.take_damage(dmg,is_rocket=False)
                else: tgt.take_damage(dmg)
                if not tgt.alive:
                    do_enemy_kill(tgt,is_tank_type=isinstance(tgt,Tank),is_boss_type=isinstance(tgt,Boss))
        for g in enemy_grenades:
            if g.exploded:
                dist=math.hypot(player.rect.centerx-g.x,player.rect.centery-g.y)
                if dist<g.EXPLOSION_R: player.take_damage(int(g.DAMAGE*(1-dist/g.EXPLOSION_R)))

        # Power-Ups
        for pu in powerups:
            pu.update()
            if pu.alive and pu.rect.colliderect(player.rect): player.collect_powerup(pu)

        # Filtern
        bullets=[b for b in bullets if b.alive]
        enemy_bullets=[b for b in enemy_bullets if b.alive]
        player_rockets=[r for r in player_rockets if r.alive]
        enemy_rockets=[r for r in enemy_rockets if r.alive]
        grenades=[g for g in grenades if g.alive]
        enemy_grenades=[g for g in enemy_grenades if g.alive]
        enemies=[e for e in enemies if e.alive]
        tanks=[t for t in tanks if t.alive]
        jetpack_soldiers=[j for j in jetpack_soldiers if j.alive]
        air_enemies=[a for a in air_enemies if a.alive]
        powerups=[p for p in powerups if p.alive]

        if not player.alive: return "gameover"

        all_dead=not enemies and not tanks and not jetpack_soldiers and not air_enemies
        if all_dead:
            # Zone-Achievements
            unlock(f"zone_{zone_num}")
            if player.zone_damage_taken==0: unlock("no_damage")
            if player.knife_only_zone: unlock("knife_only")
            if zone_num==NUM_ZONES: unlock("all_zones")
            if current_difficulty=="hard" and zone_num==NUM_ZONES: unlock("hard_clear")
            if is_boss_zone:
                if boss is None or not boss.alive: SFX.play(SFX.zone_clear);return "win"
            else:
                SFX.play(SFX.zone_clear)
                player.score+=int(300*zone_num*get_diff()["score_mult"]); return "next_zone"

        # ── ZEICHNEN ──
        ox2,oy2=get_shake_offset()
        game_surf=pygame.Surface((WIDTH,HEIGHT))
        draw_world(game_surf,cfg,cam_x,tick)
        for pu in powerups: pu.draw(game_surf,cam_x)
        PARTICLES.update();PARTICLES.draw(game_surf,cam_x)
        for g in grenades+enemy_grenades: g.draw(game_surf,cam_x)
        for r in player_rockets+enemy_rockets: r.draw(game_surf,cam_x)
        for b in bullets+enemy_bullets: b.draw(game_surf,cam_x)
        for e in enemies:
            if camera.in_view(e.x): e.draw(game_surf,cam_x)
        for t in tanks:
            if camera.in_view(t.x): t.draw(game_surf,cam_x)
        for j in jetpack_soldiers:
            if camera.in_view(j.x): j.draw(game_surf,cam_x)
        for a in air_enemies:
            if camera.in_view(a.x): a.draw(game_surf,cam_x)
        if boss and boss.alive and camera.in_view(boss.x): boss.draw(game_surf,cam_x)
        player.draw(game_surf,cam_x)
        WEATHER.draw_front(game_surf)
        screen.fill(DARK);screen.blit(game_surf,(ox2,oy2))

        el=len(enemies)+len(tanks)+len(jetpack_soldiers)
        al=len(air_enemies)+(1 if boss and boss.alive and is_boss_zone else 0)
        draw_hud(screen,player,zone_num,cfg["name"],el,al)
        MINIMAP.draw(screen,player,enemies,tanks,air_enemies,jetpack_soldiers,boss,powerups,cam_x)
        COMBO.draw(screen)
        WSTATS.draw_notifs(screen)
        ACHIEV_NOTIF.draw(screen)

        ctrl=font_tiny.render("WASD: Bewegen | SPACE: Springen | Klick: Schiessen | G: Granate | 1-7: Waffe | ESC: Pause",
                              True,(90,90,110))
        screen.blit(ctrl,(WIDTH//2-ctrl.get_width()//2,HEIGHT-20))
        pygame.display.flip()

# ═══════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════
def main():
    while True:
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
                show_cutscene(zone);zone+=1
            elif result=="win":      game_state="win"

        if game_state=="win":
            show_cutscene(NUM_ZONES-1)
            w=show_win(player.score)
            if w=="highscore": show_name_input(player.score,zone);show_highscores()

if __name__=="__main__":
    main()
