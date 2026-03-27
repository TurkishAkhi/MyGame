import pygame
import sys
import math
import json
import os
import random

# -----------------------------------------
#  PROJEKT FRONTLINE  -  v4.0
#  NEU: 6 Zonen, Tanks, Drohnen, Jets,
#       Helikopter, Jetpack-Soldaten,
#       Schrotflinte, Raketenwerfer,
#       Stinger, Messer/Nahkampf
# -----------------------------------------

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1200, 600
WORLD_WIDTH   = 4200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PROJEKT FRONTLINE  v4.0")
clock = pygame.time.Clock()
FPS   = 60

# -- Farben --
RED        = (220, 50,  50)
GREEN      = (50,  200, 80)
YELLOW     = (240, 210, 50)
WHITE      = (255, 255, 255)
GRAY       = (150, 150, 150)
DARK       = (20,  20,  20)
ORANGE     = (240, 130, 30)
BLUE       = (50,  120, 220)
CYAN       = (50,  220, 220)
PURPLE     = (160, 50,  220)
BULLET_COL = (255, 240, 100)
SNIPER_COL = (100, 220, 255)
ROCKET_COL = (255, 100, 30)
GRENADE_COL= (80,  160, 80)

GROUND_Y       = HEIGHT - 80
HIGHSCORE_FILE = "frontline_scores.json"

# -- Konstanten --
CAMERA_LERP         = 0.10
PARTICLE_FRICTION   = 0.97
GRENADE_THROW_CHANCE= 0.005


# ================================================
#  SOUND-SYSTEM
# ================================================
def make_sound(freq=440, duration=0.1, volume=0.3, wave="square", decay=True):
    sr = 44100; n = int(sr * duration); buf = bytearray(n * 2)
    for i in range(n):
        t = i / sr; env = (1 - i / n) if decay else 1.0
        if   wave == "square": v = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
        elif wave == "noise":  v = random.uniform(-1, 1)
        else:                  v = math.sin(2 * math.pi * freq * t)
        sample = max(-32768, min(32767, int(v * env * volume * 32767)))
        buf[i*2] = sample & 0xFF; buf[i*2+1] = (sample >> 8) & 0xFF
    return pygame.mixer.Sound(buffer=bytes(buf))

class SoundManager:
    def __init__(self):
        self.enabled = True
        try:
            self.shoot_pistol   = make_sound(800,  0.08, 0.25, "square")
            self.shoot_rifle    = make_sound(600,  0.06, 0.20, "square")
            self.shoot_sniper   = make_sound(300,  0.18, 0.35, "square")
            self.shoot_shotgun  = make_sound(400,  0.12, 0.30, "noise")
            self.shoot_rocket   = make_sound(200,  0.15, 0.35, "square")
            self.shoot_stinger  = make_sound(500,  0.10, 0.30, "square")
            self.knife_slash    = make_sound(900,  0.05, 0.20, "square")
            self.explosion      = make_sound(120,  0.35, 0.40, "noise")
            self.big_explosion  = make_sound(80,   0.50, 0.50, "noise")
            self.hit_player     = make_sound(200,  0.12, 0.30, "noise")
            self.hit_enemy      = make_sound(500,  0.07, 0.20, "square")
            self.jump           = make_sound(350,  0.10, 0.15, "sine")
            self.grenade_throw  = make_sound(450,  0.08, 0.15, "square")
            self.zone_clear     = make_sound(880,  0.50, 0.30, "sine", decay=False)
            self.boss_roar      = make_sound(80,   0.40, 0.35, "noise")
            self.tank_shot      = make_sound(150,  0.20, 0.40, "noise")
            self.helicopter     = make_sound(180,  0.30, 0.15, "square")
        except Exception:
            self.enabled = False

    def play(self, sound):
        if self.enabled and sound is not None:
            try: sound.play()
            except Exception: pass

SFX = SoundManager()


# ================================================
#  PARTIKEL
# ================================================
class Particle:
    __slots__ = ("x","y","vx","vy","life","max_life","color","size","gravity")
    def __init__(self, x, y, vx, vy, life, color, size=3, gravity=0.15):
        self.x=float(x); self.y=float(y); self.vx=vx; self.vy=vy
        self.life=life; self.max_life=life; self.color=color; self.size=size; self.gravity=gravity
    def update(self):
        self.x+=self.vx; self.y+=self.vy; self.vy+=self.gravity; self.vx*=PARTICLE_FRICTION; self.life-=1
    def draw(self, surf, cam_x=0):
        r = max(1, int(self.size * self.life / self.max_life))
        pygame.draw.circle(surf, self.color, (int(self.x)-cam_x, int(self.y)), r)
    @property
    def alive(self): return self.life > 0

class ParticleSystem:
    def __init__(self): self.particles = []
    def spawn_muzzle_flash(self, x, y, direction):
        for _ in range(8):
            a=random.uniform(-0.4,0.4); spd=random.uniform(3,9)
            col=random.choice([(255,240,100),(255,180,50),(255,255,200)])
            self.particles.append(Particle(x,y,math.cos(a)*spd*direction,math.sin(a)*spd,random.randint(4,10),col,random.randint(2,5),0))
    def spawn_blood(self, x, y, count=12):
        for _ in range(count):
            a=random.uniform(0,2*math.pi); spd=random.uniform(1,6)
            col=random.choice([(180,20,20),(220,40,40),(240,60,60)])
            self.particles.append(Particle(x,y,math.cos(a)*spd,math.sin(a)*spd-2,random.randint(15,30),col,random.randint(2,5)))
    def spawn_explosion(self, x, y, scale=1.0):
        count = int(40 * scale)
        for _ in range(count):
            a=random.uniform(0,2*math.pi); spd=random.uniform(2,12*scale)
            col=random.choice([(255,200,50),(255,120,20),(255,60,10),(200,200,200)])
            self.particles.append(Particle(x,y,math.cos(a)*spd,math.sin(a)*spd-3,random.randint(20,45),col,random.randint(4,int(8*scale)),0.25))
        for _ in range(int(20*scale)):
            a=random.uniform(0,2*math.pi); spd=random.uniform(0.5,3)
            self.particles.append(Particle(x,y,math.cos(a)*spd,math.sin(a)*spd-4,random.randint(35,60),(80,80,80),random.randint(6,12),-0.05))
    def spawn_dust(self, x, y):
        for _ in range(5):
            self.particles.append(Particle(x,y,random.uniform(-2,2),random.uniform(-3,-1),random.randint(8,18),(120,100,70),random.randint(2,4)))
    def spawn_shell(self, x, y, direction):
        self.particles.append(Particle(x,y,-direction*random.uniform(2,5),random.uniform(-4,-1),random.randint(20,35),(200,180,50),3))
    def spawn_sparks(self, x, y, count=10):
        for _ in range(count):
            a=random.uniform(0,2*math.pi); spd=random.uniform(2,8)
            col=random.choice([(255,200,50),(255,255,100),(200,200,200)])
            self.particles.append(Particle(x,y,math.cos(a)*spd,math.sin(a)*spd,random.randint(5,15),col,2,0.3))
    def spawn_smoke(self, x, y):
        self.particles.append(Particle(x,y,random.uniform(-1,1),random.uniform(-2,-0.5),random.randint(20,40),(100,100,100),random.randint(4,8),-0.02))
    def update(self):
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles: p.update()
    def draw(self, surf, cam_x=0):
        for p in self.particles: p.draw(surf, cam_x)

PARTICLES = ParticleSystem()
screen_shake = 0
_spotlight_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)


# ================================================
#  HIGHSCORE
# ================================================
def load_highscores():
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f: return json.load(f)
    return []

def save_highscore(name, score, zone):
    scores = load_highscores()
    scores.append({"name": name, "score": score, "zone": zone})
    scores.sort(key=lambda x: x["score"], reverse=True)
    with open(HIGHSCORE_FILE, "w") as f: json.dump(scores[:10], f)


# ================================================
#  KAMERA
# ================================================
class Camera:
    def __init__(self): self.x = 0.0
    def update(self, target_x):
        goal = target_x - WIDTH // 2
        self.x += (goal - self.x) * CAMERA_LERP
        self.x = max(0, min(WORLD_WIDTH - WIDTH, self.x))
    def in_view(self, wx, margin=300): return -margin < wx - self.x < WIDTH + margin


# ================================================
#  WAFFEN  (7 Waffen + Messer)
# ================================================
class Weapon:
    def __init__(self, name, damage, fire_rate, bullet_speed, color,
                 auto=False, is_sniper=False, is_rocket=False, is_stinger=False,
                 is_shotgun=False, is_knife=False, ammo=None, sound=None):
        self.name=name; self.damage=damage; self.fire_rate=fire_rate
        self.bullet_speed=bullet_speed; self.color=color
        self.auto=auto; self.is_sniper=is_sniper; self.is_rocket=is_rocket
        self.is_stinger=is_stinger; self.is_shotgun=is_shotgun; self.is_knife=is_knife
        self.sound=sound; self.last_shot=0
        self.max_ammo = ammo
        self.ammo = ammo  # None = unendlich

    def can_shoot(self):
        if self.ammo is not None and self.ammo <= 0: return False
        return pygame.time.get_ticks() - self.last_shot >= self.fire_rate

    def shoot_toward(self, ox, oy, tx, ty):
        if not self.can_shoot(): return []
        self.last_shot = pygame.time.get_ticks()
        if self.ammo is not None: self.ammo -= 1
        if self.sound: SFX.play(self.sound)
        dx=tx-ox; dy=ty-oy; dist=math.hypot(dx,dy) or 1
        results = []

        if self.is_knife:
            # Nahkampf: kein Projektil, sofort Schaden im Bereich
            return [("melee", ox, oy, self.facing if hasattr(self,'facing') else 1)]

        if self.is_shotgun:
            # 8 Schrotkugeln mit Streuung
            for _ in range(8):
                angle = math.atan2(dy, dx) + random.uniform(-0.3, 0.3)
                vx = math.cos(angle) * self.bullet_speed
                vy = math.sin(angle) * self.bullet_speed
                results.append(Bullet(ox, oy, vx, vy, self.damage, self.color))
            PARTICLES.spawn_muzzle_flash(ox + (1 if dx>0 else -1)*16, oy, 1 if dx>0 else -1)
        elif self.is_rocket or self.is_stinger:
            vx = dx/dist * self.bullet_speed; vy = dy/dist * self.bullet_speed
            results.append(Rocket(ox, oy, vx, vy, self.damage, self.color,
                                  is_stinger=self.is_stinger))
        else:
            vx = dx/dist * self.bullet_speed; vy = dy/dist * self.bullet_speed
            PARTICLES.spawn_muzzle_flash(ox+(1 if vx>0 else -1)*16, oy, 1 if vx>0 else -1)
            PARTICLES.spawn_shell(ox, oy, 1 if vx>0 else -1)
            results.append(Bullet(ox, oy, vx, vy, self.damage, self.color, self.is_sniper))
        return results

_ps = SFX.shoot_pistol  if SFX.enabled else None
_rs = SFX.shoot_rifle   if SFX.enabled else None
_ss = SFX.shoot_sniper  if SFX.enabled else None
_sg = SFX.shoot_shotgun if SFX.enabled else None
_rk = SFX.shoot_rocket  if SFX.enabled else None
_st = SFX.shoot_stinger if SFX.enabled else None
_kn = SFX.knife_slash   if SFX.enabled else None

PISTOLE        = Weapon("Pistole",        15,  500, 14, BULLET_COL, auto=False, sound=_ps)
STURMGEWEHR    = Weapon("Sturmgewehr",     8,   120, 18, ORANGE,    auto=True,  sound=_rs)
SCHARFSCHUETZE = Weapon("Scharfschuetze", 55, 1200, 28, SNIPER_COL,auto=False, is_sniper=True, sound=_ss)
SCHROTFLINTE   = Weapon("Schrotflinte",   18,  800, 16, YELLOW,    auto=False, is_shotgun=True, sound=_sg)
RAKETENWERFER  = Weapon("Raketenwerfer",  120, 1500,12, ROCKET_COL,auto=False, is_rocket=True, ammo=6, sound=_rk)
STINGER        = Weapon("Stinger AA",     150, 2000,16, CYAN,      auto=False, is_stinger=True,ammo=4, sound=_st)
MESSER         = Weapon("Messer",         35,  400, 0,  RED,       auto=False, is_knife=True,  sound=_kn)

ALL_WEAPONS = [PISTOLE, STURMGEWEHR, SCHARFSCHUETZE, SCHROTFLINTE, RAKETENWERFER, STINGER, MESSER]


# ================================================
#  KUGEL
# ================================================
class Bullet:
    RADIUS = 5
    def __init__(self, x, y, vx, vy, damage, color, is_sniper=False):
        self.x=float(x); self.y=float(y); self.vx=vx; self.vy=vy
        self.damage=damage; self.color=color; self.alive=True; self.is_sniper=is_sniper
    def update(self):
        self.x+=self.vx; self.y+=self.vy
        if self.x<-200 or self.x>WORLD_WIDTH+200: self.alive=False
        if self.y<-300 or self.y>HEIGHT+100: self.alive=False
    def draw(self, surf, cam_x=0):
        sx=int(self.x)-cam_x; r=7 if self.is_sniper else self.RADIUS
        pygame.draw.circle(surf, self.color, (sx, int(self.y)), r)
    def get_rect(self):
        r=7 if self.is_sniper else self.RADIUS
        return pygame.Rect(self.x-r, self.y-r, r*2, r*2)


# ================================================
#  RAKETE / STINGER-RAKETE
# ================================================
class Rocket:
    RADIUS = 6
    def __init__(self, x, y, vx, vy, damage, color, is_stinger=False):
        self.x=float(x); self.y=float(y); self.vx=vx; self.vy=vy
        self.damage=damage; self.color=color; self.alive=True
        self.is_stinger=is_stinger
        self.explosion_r = 160 if not is_stinger else 120
        self.homing_target = None  # Stinger verfolgt Luftziele

    def update(self, air_targets=None):
        # Stinger: Homing auf nächstes Luftziel
        if self.is_stinger and air_targets:
            if self.homing_target is None or not self.homing_target.alive:
                best = None; best_d = 9999
                for t in air_targets:
                    d = math.hypot(t.x - self.x, t.y - self.y)
                    if d < best_d: best_d = d; best = t
                self.homing_target = best
            if self.homing_target and self.homing_target.alive:
                tx = self.homing_target.x; ty = self.homing_target.y
                dx = tx - self.x; dy = ty - self.y
                dist = math.hypot(dx, dy) or 1
                spd = math.hypot(self.vx, self.vy)
                self.vx += (dx/dist * spd - self.vx) * 0.08
                self.vy += (dy/dist * spd - self.vy) * 0.08
        self.x += self.vx; self.y += self.vy
        PARTICLES.spawn_smoke(self.x, self.y)
        if self.x < -200 or self.x > WORLD_WIDTH+200: self.alive = False
        if self.y < -400 or self.y > HEIGHT+100: self.alive = False

    def explode(self, targets):
        self.alive = False
        SFX.play(SFX.big_explosion)
        PARTICLES.spawn_explosion(self.x, self.y, scale=2.0)
        hits = []
        for t in targets:
            d = math.hypot(t.x - self.x, t.y - self.y)
            if d <= self.explosion_r:
                hits.append((t, int(self.damage * (1 - d/self.explosion_r))))
        return hits

    def draw(self, surf, cam_x=0):
        sx = int(self.x) - cam_x; sy = int(self.y)
        angle = math.atan2(self.vy, self.vx)
        col = CYAN if self.is_stinger else ROCKET_COL
        pygame.draw.circle(surf, col, (sx, sy), self.RADIUS)
        tx = int(sx - math.cos(angle)*18); ty = int(sy - math.sin(angle)*18)
        pygame.draw.line(surf, (255,200,50), (sx,sy), (tx,ty), 3)

    def get_rect(self):
        return pygame.Rect(self.x-self.RADIUS, self.y-self.RADIUS, self.RADIUS*2, self.RADIUS*2)


# ================================================
#  GRANATE
# ================================================
class Grenade:
    RADIUS=8; GRAVITY=0.4; EXPLOSION_R=130; DAMAGE=60; FUSE_MS=2000
    def __init__(self, x, y, direction):
        self.x=float(x); self.y=float(y); self.vx=direction*10; self.vy=-14
        self.alive=True; self.exploded=False
        self.spawn=pygame.time.get_ticks(); self.explode_time=0
    def update(self, enemies):
        if self.exploded:
            if pygame.time.get_ticks()-self.explode_time > 400: self.alive=False
            return []
        self.vy+=self.GRAVITY; self.x+=self.vx; self.y+=self.vy
        if self.y>=GROUND_Y-self.RADIUS:
            self.y=GROUND_Y-self.RADIUS; self.vy=-self.vy*0.4; self.vx*=0.6
            PARTICLES.spawn_dust(self.x,self.y)
        for plat in current_platforms:
            gr=pygame.Rect(self.x-self.RADIUS,self.y-self.RADIUS,self.RADIUS*2,self.RADIUS*2)
            if gr.colliderect(plat) and self.vy>0 and self.y-self.vy<=plat.top+4:
                self.y=plat.top-self.RADIUS; self.vy=-self.vy*0.4; self.vx*=0.6
        if pygame.time.get_ticks()-self.spawn>=self.FUSE_MS:
            return self._explode(enemies)
        return []
    def _explode(self, enemies):
        self.exploded=True; self.explode_time=pygame.time.get_ticks()
        SFX.play(SFX.explosion); PARTICLES.spawn_explosion(self.x,self.y)
        hits=[]
        for e in enemies:
            d=math.hypot(e.x-self.x, e.y-self.y)
            if d<=self.EXPLOSION_R: hits.append((e, int(self.DAMAGE*(1-d/self.EXPLOSION_R))))
        return hits
    def draw(self, surf, cam_x=0):
        sx=int(self.x)-cam_x
        if not self.exploded:
            pygame.draw.circle(surf,GRENADE_COL,(sx,int(self.y)),self.RADIUS)
            if (pygame.time.get_ticks()//200)%2==0:
                pygame.draw.circle(surf,RED,(sx,int(self.y)),3)


# ================================================
#  ZONEN  –  6 Zonen
# ================================================
current_platforms = []

def make_zones():
    WW = WORLD_WIDTH; GY = GROUND_Y
    return {
        1: {
            "name":"ZONE 1: ZERSTOERTE STADT",
            "sky":(28,38,58),"ground":(65,52,38),
            "enemy_hp":50,"enemy_speed":2.2,"enemy_shoot_rate":1700,
            "air_enemies": [],
            "platforms":[
                pygame.Rect(0,GY,WW,80),
                pygame.Rect(260,GY-110,140,18), pygame.Rect(460,GY-170,110,18),
                pygame.Rect(700,GY-120,130,18), pygame.Rect(880,GY-210,100,18),
                pygame.Rect(1050,GY-150,150,18),pygame.Rect(1250,GY-250,120,18),
                pygame.Rect(1500,GY-130,200,18),pygame.Rect(1800,GY-170,110,18),
                pygame.Rect(1980,GY-240,100,18),pygame.Rect(2150,GY-130,130,18),
                pygame.Rect(2350,GY-190,110,18),pygame.Rect(2520,GY-260,130,18),
                pygame.Rect(2700,GY-140,150,18),pygame.Rect(2950,GY-200,130,18),
            ],
            "enemy_positions":[
                (900,GY-52),(1200,GY-52),(1550,GY-52),(1850,GY-52),
                (2200,GY-52),(2500,GY-52),(2750,GY-52),
                (880,GY-230),(1250,GY-272),(1980,GY-262),(2520,GY-282),
            ],
        },
        2: {
            "name":"ZONE 2: WALD",
            "sky":(18,42,20),"ground":(35,62,25),
            "enemy_hp":70,"enemy_speed":2.8,"enemy_shoot_rate":1300,
            "air_enemies": [("drone", 1200), ("drone", 2400)],
            "platforms":[
                pygame.Rect(0,GY,WW,80),
                pygame.Rect(200,GY-100,100,18), pygame.Rect(370,GY-155,90,18),
                pygame.Rect(530,GY-100,100,18), pygame.Rect(700,GY-200,80,18),
                pygame.Rect(860,GY-140,120,18), pygame.Rect(1040,GY-220,90,18),
                pygame.Rect(1220,GY-160,100,18),pygame.Rect(1420,GY-80,70,18),
                pygame.Rect(1550,GY-80,70,18),  pygame.Rect(1680,GY-80,70,18),
                pygame.Rect(1850,GY-130,120,18),pygame.Rect(2050,GY-200,90,18),
                pygame.Rect(2220,GY-130,110,18),pygame.Rect(2400,GY-190,100,18),
                pygame.Rect(2580,GY-260,90,18), pygame.Rect(2750,GY-150,130,18),
                pygame.Rect(2950,GY-220,110,18),pygame.Rect(3150,GY-150,130,18),
            ],
            "enemy_positions":[
                (800,GY-52),(1100,GY-52),(1500,GY-52),(1700,GY-52),
                (2000,GY-52),(2300,GY-52),(2600,GY-52),(2900,GY-52),
                (700,GY-222),(1040,GY-242),(2050,GY-222),(2580,GY-282),(3150,GY-172),
            ],
        },
        3: {
            "name":"ZONE 3: WUESTENFRONT",
            "sky":(80,55,30),"ground":(140,100,50),
            "enemy_hp":85,"enemy_speed":2.5,"enemy_shoot_rate":1400,
            "air_enemies": [("drone", 1500), ("drone", 2800), ("drone", 3500)],
            "platforms":[
                pygame.Rect(0,GY,WW,80),
                pygame.Rect(300,GY-90,120,18),  pygame.Rect(550,GY-160,100,18),
                pygame.Rect(800,GY-110,130,18),  pygame.Rect(1050,GY-200,90,18),
                pygame.Rect(1300,GY-130,140,18), pygame.Rect(1550,GY-220,100,18),
                pygame.Rect(1800,GY-140,120,18), pygame.Rect(2050,GY-210,90,18),
                pygame.Rect(2300,GY-160,130,18), pygame.Rect(2600,GY-240,110,18),
                pygame.Rect(2850,GY-130,140,18), pygame.Rect(3100,GY-200,100,18),
                pygame.Rect(3400,GY-150,130,18),
            ],
            "enemy_positions":[
                (600,GY-52),(950,GY-52),(1300,GY-52),(1650,GY-52),
                (2000,GY-52),(2350,GY-52),(2700,GY-52),(3050,GY-52),(3400,GY-52),
                (550,GY-182),(1050,GY-222),(2600,GY-262),(3100,GY-222),
            ],
            # Tanks in Zone 3
            "tank_positions": [(1800, GY-52), (3000, GY-52)],
        },
        4: {
            "name":"ZONE 4: MILITAERBASIS",
            "sky":(12,12,28),"ground":(42,42,52),
            "enemy_hp":110,"enemy_speed":3.0,"enemy_shoot_rate":1000,
            "air_enemies": [("helicopter", 1600), ("helicopter", 3200)],
            "platforms":[
                pygame.Rect(0,GY,WW,80),
                pygame.Rect(180,GY-120,100,18), pygame.Rect(350,GY-200,80,18),
                pygame.Rect(520,GY-140,110,18), pygame.Rect(720,GY-100,150,18),
                pygame.Rect(920,GY-180,130,18), pygame.Rect(1100,GY-260,100,18),
                pygame.Rect(1280,GY-180,120,18),pygame.Rect(1480,GY-110,150,18),
                pygame.Rect(1720,GY-160,110,18),pygame.Rect(1900,GY-240,90,18),
                pygame.Rect(2070,GY-160,120,18),pygame.Rect(2280,GY-220,100,18),
                pygame.Rect(2500,GY-130,130,18),pygame.Rect(2700,GY-210,100,18),
                pygame.Rect(2880,GY-290,120,18),pygame.Rect(3050,GY-210,110,18),
                pygame.Rect(3250,GY-130,150,18),
            ],
            "enemy_positions":[
                (600,GY-52),(900,GY-52),(1200,GY-52),(1550,GY-52),
                (1800,GY-52),(2100,GY-52),(2400,GY-52),(2700,GY-52),(3000,GY-52),
                (350,GY-222),(1100,GY-282),(1900,GY-262),(2700,GY-232),(2880,GY-312),
            ],
            "tank_positions": [(2200, GY-52), (3400, GY-52)],
            "jetpack_positions": [(1400, GY-52), (2600, GY-52)],
        },
        5: {
            "name":"ZONE 5: ARKTIS",
            "sky":(160,190,220),"ground":(200,220,240),
            "enemy_hp":130,"enemy_speed":3.2,"enemy_shoot_rate":900,
            "air_enemies": [("jet", 2000), ("jet", 3500), ("helicopter", 1200)],
            "platforms":[
                pygame.Rect(0,GY,WW,80),
                pygame.Rect(220,GY-100,110,18), pygame.Rect(420,GY-180,90,18),
                pygame.Rect(620,GY-130,120,18), pygame.Rect(860,GY-220,100,18),
                pygame.Rect(1100,GY-150,130,18),pygame.Rect(1350,GY-240,90,18),
                pygame.Rect(1600,GY-170,110,18),pygame.Rect(1850,GY-270,100,18),
                pygame.Rect(2100,GY-190,120,18),pygame.Rect(2350,GY-280,90,18),
                pygame.Rect(2600,GY-150,130,18),pygame.Rect(2850,GY-230,110,18),
                pygame.Rect(3100,GY-170,120,18),pygame.Rect(3400,GY-250,100,18),
            ],
            "enemy_positions":[
                (700,GY-52),(1000,GY-52),(1350,GY-52),(1700,GY-52),
                (2050,GY-52),(2400,GY-52),(2750,GY-52),(3100,GY-52),(3450,GY-52),
                (420,GY-202),(860,GY-242),(1350,GY-262),(2350,GY-302),(3400,GY-272),
            ],
            "tank_positions": [(1600, GY-52), (2800, GY-52), (3800, GY-52)],
            "jetpack_positions": [(900, GY-52), (2200, GY-52), (3300, GY-52)],
        },
        6: {
            "name":"ZONE 6: FESTUNG OMEGA",
            "sky":(8,5,18),"ground":(30,25,45),
            "enemy_hp":150,"enemy_speed":3.5,"enemy_shoot_rate":800,
            "air_enemies": [("jet",1800),("jet",3000),("helicopter",2400),("helicopter",3800)],
            "platforms":[
                pygame.Rect(0,GY,WW,80),
                pygame.Rect(200,GY-130,110,18), pygame.Rect(400,GY-220,90,18),
                pygame.Rect(620,GY-160,120,18), pygame.Rect(880,GY-260,100,18),
                pygame.Rect(1120,GY-180,130,18),pygame.Rect(1380,GY-280,90,18),
                pygame.Rect(1640,GY-200,110,18),pygame.Rect(1900,GY-300,100,18),
                pygame.Rect(2160,GY-220,120,18),pygame.Rect(2420,GY-310,90,18),
                pygame.Rect(2680,GY-180,130,18),pygame.Rect(2940,GY-270,110,18),
                pygame.Rect(3200,GY-200,120,18),pygame.Rect(3460,GY-290,100,18),
                pygame.Rect(3720,GY-160,130,18),
            ],
            "enemy_positions":[
                (600,GY-52),(950,GY-52),(1300,GY-52),(1650,GY-52),
                (2000,GY-52),(2350,GY-52),(2700,GY-52),(3050,GY-52),(3400,GY-52),(3800,GY-52),
                (400,GY-242),(880,GY-282),(1380,GY-302),(1900,GY-322),(2420,GY-332),(3460,GY-312),
            ],
            "tank_positions": [(1200,GY-52),(2500,GY-52),(3700,GY-52)],
            "jetpack_positions": [(800,GY-52),(2000,GY-52),(3200,GY-52)],
        },
    }

ZONES = make_zones()
NUM_ZONES = 6


# ================================================
#  SPIELER
# ================================================
class Player:
    W=32; H=56; SPEED=5; JUMP_FORCE=-16; GRAVITY=0.7
    MAX_FALL=18; MAX_LIVES=3; MAX_HP=100; GRENADES=5

    def __init__(self, x, y):
        self.x=float(x); self.y=float(y); self.vx=0.0; self.vy=0.0
        self.on_ground=False; self.was_on_ground=False; self.facing=1
        self.lives=self.MAX_LIVES; self.hp=self.MAX_HP
        self.grenades=self.GRENADES; self.weapon=PISTOLE
        self.invincible=0; self.alive=True
        self.score=0; self.walk_frame=0; self.walk_timer=0
        self.knife_anim=0  # Messer-Animationstimer

    def handle_input(self, keys, bullets, rockets, cam_x):
        self.vx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  self.vx=-self.SPEED; self.facing=-1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: self.vx= self.SPEED; self.facing= 1
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.vy=self.JUMP_FORCE; SFX.play(SFX.jump)
        if self.weapon.auto and pygame.mouse.get_pressed()[0]:
            self._fire(bullets, rockets, cam_x)

    def shoot(self, bullets, rockets, cam_x):
        if not self.weapon.auto:
            self._fire(bullets, rockets, cam_x)

    def _fire(self, bullets, rockets, cam_x):
        mx, my = pygame.mouse.get_pos()
        tx=mx+cam_x; ty=my
        ox=self.rect.centerx; oy=self.rect.centery
        self.facing = 1 if tx > ox else -1
        results = self.weapon.shoot_toward(ox, oy, tx, ty)
        for r in results:
            if isinstance(r, Bullet):   bullets.append(r)
            elif isinstance(r, Rocket): rockets.append(r)
            elif isinstance(r, tuple) and r[0] == "melee":
                self.knife_anim = 15

    def get_knife_hit_rect(self):
        return pygame.Rect(
            self.rect.centerx + self.facing*5,
            self.rect.centery - 10,
            50, 30
        )

    def throw_grenade(self, grenades):
        if self.grenades > 0:
            grenades.append(Grenade(self.rect.centerx, self.rect.top, self.facing))
            self.grenades -= 1; SFX.play(SFX.grenade_throw)

    def update(self):
        global screen_shake
        self.was_on_ground = self.on_ground
        self.vy = min(self.vy + self.GRAVITY, self.MAX_FALL)
        self.on_ground = False
        self.y += self.vy
        for plat in current_platforms:
            pr = self.rect
            if pr.colliderect(plat):
                if self.vy>0 and pr.bottom-self.vy<=plat.top+abs(self.vy)+2:
                    self.y=plat.top-self.H; self.vy=0; self.on_ground=True
                elif self.vy<0 and pr.top-self.vy>=plat.bottom-abs(self.vy)-2:
                    self.y=plat.bottom; self.vy=1
        self.x += self.vx
        self.x = max(0, min(WORLD_WIDTH-self.W, self.x))
        if self.on_ground and not self.was_on_ground:
            PARTICLES.spawn_dust(self.x+self.W//2, self.y+self.H)
        if self.vx != 0:
            self.walk_timer += 1
            if self.walk_timer > 8:
                self.walk_frame=(self.walk_frame+1)%4; self.walk_timer=0
                if random.random()<0.3 and self.on_ground:
                    PARTICLES.spawn_dust(self.x+self.W//2, self.y+self.H)
        if self.invincible > 0: self.invincible=max(0,self.invincible-clock.get_time())
        if self.knife_anim > 0: self.knife_anim -= 1

    def take_damage(self, amount):
        global screen_shake
        if self.invincible > 0: return
        self.hp -= int(amount)
        SFX.play(SFX.hit_player); PARTICLES.spawn_blood(self.rect.centerx,self.rect.centery,8)
        screen_shake = 8
        if self.hp <= 0:
            self.hp = 0; self.lives -= 1
            if self.lives > 0: self.hp=self.MAX_HP; self.invincible=2000
            else: self.alive=False

    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)

    def draw(self, surf, cam_x=0):
        sx=int(self.x)-cam_x; cx=sx+self.W//2; cy=int(self.y); f=self.facing
        if self.invincible>0 and (pygame.time.get_ticks()//100)%2==0: return
        bc=(50,90,50)
        sh=pygame.Surface((self.W+8,6),pygame.SRCALPHA)
        pygame.draw.ellipse(sh,(0,0,0,80),(0,0,self.W+8,6))
        surf.blit(sh,(cx-self.W//2-4,cy+self.H-2))
        pygame.draw.circle(surf,(200,160,110),(cx,cy+10),10)
        pygame.draw.arc(surf,(40,60,40),pygame.Rect(cx-12,cy+2,24,16),0,math.pi,5)
        pygame.draw.rect(surf,(40,60,40),pygame.Rect(cx-12,cy+6,24,6))
        pygame.draw.rect(surf,bc,pygame.Rect(cx-10,cy+20,20,20))
        lo=[0,6,0,-6][self.walk_frame] if self.vx!=0 else 0
        pygame.draw.line(surf,bc,(cx-5,cy+40),(cx-5,cy+55+lo),5)
        pygame.draw.line(surf,bc,(cx+5,cy+40),(cx+5,cy+55-lo),5)
        # Waffe / Messer-Animation
        arm_end_x = cx+f*18; arm_end_y = cy+28
        if self.weapon == MESSER and self.knife_anim > 0:
            progress = self.knife_anim / 15.0
            arm_end_x = cx + f * int(18 + 30 * progress)
            arm_end_y = cy + int(28 - 10 * progress)
            pygame.draw.line(surf,(200,200,200),(arm_end_x,arm_end_y),(arm_end_x+f*20,arm_end_y-5),3)
        pygame.draw.line(surf,bc,(cx,cy+22),(arm_end_x,arm_end_y),4)
        if self.weapon==PISTOLE:
            pygame.draw.rect(surf,(60,60,60),pygame.Rect(cx+f*10,cy+25,14,5))
        elif self.weapon==STURMGEWEHR:
            pygame.draw.rect(surf,(40,40,40),pygame.Rect(cx+f*10,cy+24,22,6))
        elif self.weapon==SCHARFSCHUETZE:
            pygame.draw.rect(surf,(30,50,30),pygame.Rect(cx+f*10,cy+23,30,5))
            pygame.draw.rect(surf,(70,100,70),pygame.Rect(cx+f*32,cy+21,6,3))
        elif self.weapon==SCHROTFLINTE:
            pygame.draw.rect(surf,(80,60,30),pygame.Rect(cx+f*8,cy+24,20,7))
        elif self.weapon==RAKETENWERFER:
            pygame.draw.rect(surf,(60,60,60),pygame.Rect(cx+f*8,cy+22,28,8))
            pygame.draw.circle(surf,(80,80,80),(cx+f*36,cy+26),5)
        elif self.weapon==STINGER:
            pygame.draw.rect(surf,(40,80,80),pygame.Rect(cx+f*8,cy+20,32,8))
            pygame.draw.circle(surf,CYAN,(cx+f*40,cy+24),4)
        elif self.weapon==MESSER:
            if self.knife_anim==0:
                pygame.draw.line(surf,(200,200,200),(cx+f*12,cy+26),(cx+f*26,cy+22),3)
        bw=50; bx=cx-bw//2; by=cy-12
        pygame.draw.rect(surf,DARK,(bx,by,bw,6))
        hc=GREEN if self.hp>50 else YELLOW if self.hp>25 else RED
        pygame.draw.rect(surf,hc,(bx,by,int(bw*self.hp/self.MAX_HP),6))
        pygame.draw.rect(surf,GRAY,(bx,by,bw,6),1)


# ================================================
#  FEIND (Infanterie)
# ================================================
class Enemy:
    W=30; H=52
    ST_PATROL="patrol"; ST_CHASE="chase"; ST_SHOOT="shoot"; ST_FLANK="flank"

    def __init__(self, x, y, hp=50, speed=2.2, shoot_rate=1700):
        self.x=float(x); self.y=float(y); self.vy=0.0
        self.max_hp=hp; self.hp=hp; self.alive=True
        self.last_shot=0; self.facing=-1
        self.speed=speed; self.shoot_rate=shoot_rate
        self.walk_frame=0; self.walk_timer=0; self.on_ground=False
        self.state=self.ST_PATROL; self.state_timer=0
        self.patrol_dir=-1; self.patrol_timer=0
        self.flank_target=0.0
        self.grenade_cd=random.randint(6000,12000); self.last_grenade=-99999
        self.jump_cooldown=0; self.stuck_timer=0; self.last_x=float(x)

    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    def _dist(self, player): return math.hypot(player.x-self.x, player.y-self.y)

    def _try_jump(self, target_x):
        if not self.on_ground or self.jump_cooldown>0: return
        dx=target_x-self.x
        for plat in current_platforms:
            if plat.h>60: continue
            in_dir=((dx>0 and plat.left>self.x and plat.left<self.x+250) or
                    (dx<0 and plat.right<self.x+self.W and plat.right>self.x-250))
            if in_dir and plat.top<self.y-30:
                self.vy=-15.0; self.jump_cooldown=30; SFX.play(SFX.jump); return
        if self.stuck_timer>25 and self.on_ground:
            self.vy=-14.0; self.jump_cooldown=35; SFX.play(SFX.jump); self.stuck_timer=0

    def _move_toward(self, tx, sp=None):
        sp=sp or self.speed; dx=tx-self.x
        if abs(dx)>4:
            self.x+=sp*(1 if dx>0 else -1); self.facing=1 if dx>0 else -1
            self.walk_timer+=1
            if self.walk_timer>8: self.walk_frame=(self.walk_frame+1)%4; self.walk_timer=0

    def _shoot_at(self, player, bullets):
        now=pygame.time.get_ticks()
        if now-self.last_shot<self.shoot_rate: return
        self.last_shot=now
        ox=self.rect.centerx; oy=self.rect.centery
        tx=player.rect.centerx+player.vx*4; ty=player.rect.centery
        self.facing=1 if tx>ox else -1
        dx=tx-ox; dy=ty-oy; dist=math.hypot(dx,dy) or 1
        angle=math.atan2(dy,dx)+random.uniform(-0.14,0.14)
        vx=math.cos(angle)*11; vy=math.sin(angle)*11
        bullets.append(Bullet(ox,oy,vx,vy,10,RED))
        SFX.play(SFX.shoot_pistol)

    def update(self, player, bullets, grenades_list):
        self.vy=min(self.vy+0.7,18); self.y+=self.vy; self.on_ground=False
        for plat in current_platforms:
            r=self.rect
            if r.colliderect(plat) and self.vy>=0:
                if r.bottom-self.vy<=plat.top+abs(self.vy)+2:
                    self.y=plat.top-self.H; self.vy=0; self.on_ground=True
        if self.jump_cooldown>0: self.jump_cooldown-=1
        if abs(self.x-self.last_x)<0.3 and self.on_ground:
            self.stuck_timer+=1
        else:
            self.stuck_timer=max(0,self.stuck_timer-2)
        self.last_x=self.x
        dist=self._dist(player); now=pygame.time.get_ticks()
        hp_low=self.hp<self.max_hp*0.35
        if (dist<380 and now-self.last_grenade>self.grenade_cd and
                random.random()<GRENADE_THROW_CHANCE):
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
            self.state=self.ST_SHOOT; self.state_timer=0
        elif self.state==self.ST_SHOOT and self.state_timer>180:
            self.state=random.choice([self.ST_FLANK,self.ST_CHASE]); self.state_timer=0
        if self.state==self.ST_PATROL:
            self.patrol_timer+=1
            if self.patrol_timer>90: self.patrol_dir*=-1; self.patrol_timer=0
            tx=self.x+self.patrol_dir*60
            self._move_toward(tx,self.speed*0.6); self._try_jump(tx)
        elif self.state==self.ST_CHASE:
            self._move_toward(player.x,self.speed); self._try_jump(player.x)
        elif self.state==self.ST_FLANK:
            if self.state_timer==1:
                self.flank_target=player.x+random.choice([-280,-200,200,280])
            self._move_toward(self.flank_target,self.speed*1.2)
            self._try_jump(self.flank_target); self._shoot_at(player,bullets)
        elif self.state==self.ST_SHOOT:
            self._shoot_at(player,bullets)
            if dist<120: self._move_toward(self.x-self.facing*50,self.speed*0.8)
        self.x=max(0,min(WORLD_WIDTH-self.W,self.x))

    def take_damage(self, amount):
        self.hp-=amount; SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_blood(self.rect.centerx,self.rect.centery)
        if self.hp<=0:
            self.alive=False
            PARTICLES.spawn_blood(self.rect.centerx,self.rect.centery,20)

    def draw(self, surf, cam_x=0):
        sx=int(self.x)-cam_x; cx=sx+self.W//2; cy=int(self.y); f=self.facing
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
        bw=40; bx=cx-bw//2; by=cy-10
        pygame.draw.rect(surf,DARK,(bx,by,bw,5))
        hp_r=self.hp/self.max_hp
        hc=(50,200,80) if hp_r>0.6 else YELLOW if hp_r>0.3 else RED
        pygame.draw.rect(surf,hc,(bx,by,int(bw*hp_r),5))


# ================================================
#  JETPACK-SOLDAT
# ================================================
class JetpackSoldier:
    W=28; H=48; MAX_HP=80

    def __init__(self, x, y):
        self.x=float(x); self.y=float(y); self.vy=0.0; self.vx=0.0
        self.hp=self.MAX_HP; self.alive=True; self.facing=-1
        self.last_shot=0; self.shoot_rate=1200
        self.hover_y=float(y)-120  # Ziel-Höhe
        self.strafe_timer=0; self.strafe_dir=random.choice([-1,1])

    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    @property
    def is_air(self): return True

    def update(self, player, bullets):
        # Schwebt auf hover_y
        target_vy = (self.hover_y - self.y) * 0.05
        self.vy += (target_vy - self.vy) * 0.1
        self.y += self.vy
        # Seitwärtsbewegung
        self.strafe_timer += 1
        if self.strafe_timer > 90:
            self.strafe_dir = random.choice([-1,1]); self.strafe_timer=0
        self.x += self.strafe_dir * 2.5
        self.x = max(100, min(WORLD_WIDTH-100, self.x))
        # Schießen
        self.facing = 1 if player.x > self.x else -1
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_rate and abs(player.x-self.x) < 500:
            self.last_shot=now
            ox=self.rect.centerx; oy=self.rect.centery
            tx=player.rect.centerx; ty=player.rect.centery
            dx=tx-ox; dy=ty-oy; dist=math.hypot(dx,dy) or 1
            angle=math.atan2(dy,dx)+random.uniform(-0.1,0.1)
            bullets.append(Bullet(ox,oy,math.cos(angle)*12,math.sin(angle)*12,10,ORANGE))
            SFX.play(SFX.shoot_rifle)
        # Jetpack-Partikel
        if random.random()<0.4:
            PARTICLES.spawn_smoke(self.x+self.W//2, self.y+self.H)

    def take_damage(self, amount):
        self.hp -= amount; SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_blood(self.rect.centerx,self.rect.centery,6)
        if self.hp <= 0:
            self.alive=False
            PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery)

    def draw(self, surf, cam_x=0):
        sx=int(self.x)-cam_x; cx=sx+self.W//2; cy=int(self.y); f=self.facing
        # Jetpack
        pygame.draw.rect(surf,(60,80,60),pygame.Rect(cx-8,cy+15,16,22))
        pygame.draw.rect(surf,(100,120,80),pygame.Rect(cx-6,cy+17,12,18))
        # Flamme
        fl=random.randint(8,18)
        pygame.draw.polygon(surf,ORANGE,[(cx-4,cy+37),(cx+4,cy+37),(cx,cy+37+fl)])
        pygame.draw.polygon(surf,YELLOW,[(cx-2,cy+37),(cx+2,cy+37),(cx,cy+37+fl//2)])
        # Körper
        pygame.draw.circle(surf,(200,155,105),(cx,cy+8),9)
        pygame.draw.rect(surf,(40,80,40),pygame.Rect(cx-9,cy+17,18,18))
        pygame.draw.line(surf,(50,90,50),(cx,cy+19),(cx+f*16,cy+25),4)
        pygame.draw.rect(surf,(40,40,40),pygame.Rect(cx+f*6,cy+22,12,4))
        bw=36; bx=cx-bw//2; by=cy-8
        pygame.draw.rect(surf,DARK,(bx,by,bw,5))
        hp_r=self.hp/self.MAX_HP
        hc=(50,200,80) if hp_r>0.6 else YELLOW if hp_r>0.3 else RED
        pygame.draw.rect(surf,hc,(bx,by,int(bw*hp_r),5))


# ================================================
#  TANK
# ================================================
class Tank:
    W=80; H=40; MAX_HP=350; SPEED=0.8; SHOOT_RATE=2500

    def __init__(self, x, y):
        self.x=float(x); self.y=float(y)-self.H+10
        self.hp=self.MAX_HP; self.alive=True; self.facing=-1
        self.last_shot=0; self.vy=0.0; self.on_ground=False
        self.move_timer=0; self.move_dir=-1

    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    @property
    def is_air(self): return False

    def update(self, player, bullets):
        self.vy=min(self.vy+0.7,18); self.y+=self.vy; self.on_ground=False
        for plat in current_platforms:
            r=self.rect
            if r.colliderect(plat) and self.vy>=0:
                if r.bottom-self.vy<=plat.top+abs(self.vy)+2:
                    self.y=plat.top-self.H+10; self.vy=0; self.on_ground=True
        dx=player.x-self.x
        self.facing=1 if dx>0 else -1
        if abs(dx)>200:
            self.x+=self.SPEED*(1 if dx>0 else -1)
        self.x=max(0,min(WORLD_WIDTH-self.W,self.x))
        # Schießen
        now=pygame.time.get_ticks()
        if now-self.last_shot>=self.SHOOT_RATE and abs(dx)<700:
            self.last_shot=now
            SFX.play(SFX.tank_shot)
            ox=self.rect.centerx+(self.facing*50)
            oy=int(self.y)+10
            tx=player.rect.centerx; ty=player.rect.centery
            d2=math.hypot(tx-ox,ty-oy) or 1
            spd=14
            vx=(tx-ox)/d2*spd; vy=(ty-oy)/d2*spd
            bullets.append(Bullet(ox,oy,vx,vy,25,(200,150,50),is_sniper=True))
            PARTICLES.spawn_explosion(ox,oy,scale=0.5)
        # Rauch aus Schornstein
        if random.random()<0.1:
            PARTICLES.spawn_smoke(int(self.x)+self.W//2,int(self.y))

    def take_damage(self, amount, is_rocket=False):
        dmg = amount if is_rocket else amount // 4  # Tank ist resistent gegen Kugeln
        self.hp -= dmg; SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_sparks(self.rect.centerx, self.rect.centery, 6)
        if self.hp<=0:
            self.alive=False
            PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=2.5)
            SFX.play(SFX.big_explosion)

    def draw(self, surf, cam_x=0):
        sx=int(self.x)-cam_x; cy=int(self.y); f=self.facing
        # Ketten
        pygame.draw.rect(surf,(40,40,40),pygame.Rect(sx,cy+28,self.W,14))
        for i in range(sx,sx+self.W,10):
            pygame.draw.line(surf,(60,60,60),(i,cy+28),(i,cy+42),2)
        pygame.draw.circle(surf,(50,50,50),(sx+10,cy+35),8)
        pygame.draw.circle(surf,(50,50,50),(sx+self.W-10,cy+35),8)
        # Rumpf
        pygame.draw.rect(surf,(80,90,60),pygame.Rect(sx+4,cy+14,self.W-8,20))
        # Turm
        pygame.draw.rect(surf,(90,100,70),pygame.Rect(sx+20,cy+4,40,14))
        # Kanone
        cannon_x=sx+40+(f*30); cannon_y=cy+10
        pygame.draw.line(surf,(60,70,50),(sx+40,cy+10),(cannon_x,cannon_y),6)
        # Schornstein
        pygame.draw.rect(surf,(60,60,50),pygame.Rect(sx+30,cy,8,6))
        # HP
        bw=70; bx=sx+(self.W-bw)//2; by=cy-14
        pygame.draw.rect(surf,DARK,(bx,by,bw,7))
        hp_r=self.hp/self.MAX_HP
        hc=(50,200,80) if hp_r>0.5 else YELLOW if hp_r>0.25 else RED
        pygame.draw.rect(surf,hc,(bx,by,int(bw*hp_r),7))
        pygame.draw.rect(surf,GRAY,(bx,by,bw,7),1)
        lf=pygame.font.SysFont("consolas",10,bold=True)
        lb=lf.render("TANK",True,(200,200,100))
        surf.blit(lb,(sx+(self.W-lb.get_width())//2,by-12))


# ================================================
#  DROHNE
# ================================================
class Drone:
    W=36; H=20; MAX_HP=45; SPEED=2.5; SHOOT_RATE=1800

    def __init__(self, x):
        self.x=float(x); self.y=float(GROUND_Y-200-random.randint(0,80))
        self.hp=self.MAX_HP; self.alive=True; self.facing=-1
        self.last_shot=0; self.vx=-self.SPEED; self.vy=0.0
        self.bob_offset=random.uniform(0,2*math.pi)

    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    @property
    def is_air(self): return True

    def update(self, player, bullets):
        # Schweben + Bob
        self.y += math.sin(pygame.time.get_ticks()*0.003+self.bob_offset)*0.5
        dx=player.x-self.x
        self.facing=1 if dx>0 else -1
        # Auf Spieler zufliegen
        dist=abs(dx)
        if dist > 300:
            self.x += self.SPEED*(1 if dx>0 else -1)
        elif dist < 150:
            self.x -= self.SPEED*0.5*(1 if dx>0 else -1)
        self.x=max(50,min(WORLD_WIDTH-50,self.x))
        # Schießen
        now=pygame.time.get_ticks()
        if now-self.last_shot>=self.SHOOT_RATE and dist<500:
            self.last_shot=now
            ox=self.rect.centerx; oy=self.rect.bottom
            tx=player.rect.centerx; ty=player.rect.centery
            d2=math.hypot(tx-ox,ty-oy) or 1
            angle=math.atan2(ty-oy,tx-ox)+random.uniform(-0.1,0.1)
            bullets.append(Bullet(ox,oy,math.cos(angle)*10,math.sin(angle)*10,8,(255,100,100)))
            SFX.play(SFX.shoot_pistol)

    def take_damage(self, amount, is_rocket=False):
        self.hp-=amount; SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_sparks(self.rect.centerx,self.rect.centery,4)
        if self.hp<=0:
            self.alive=False
            PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=0.8)

    def draw(self, surf, cam_x=0):
        sx=int(self.x)-cam_x; cx=sx+self.W//2; cy=int(self.y)+self.H//2
        # Körper
        pygame.draw.rect(surf,(60,60,80),pygame.Rect(sx+8,cy-6,20,12),border_radius=4)
        # Rotorblätter
        t=pygame.time.get_ticks()
        for angle in [t*0.05, t*0.05+math.pi/2]:
            rx=int(math.cos(angle)*16); ry=int(math.sin(angle)*4)
            pygame.draw.line(surf,(180,180,200),(cx-rx,cy-6+ry),(cx+rx,cy-6-ry),2)
        # Kamera
        pygame.draw.circle(surf,(40,40,40),(cx,cy+6),4)
        pygame.draw.circle(surf,RED,(cx,cy+6),2)
        # Arme
        pygame.draw.line(surf,(80,80,100),(sx+4,cy),(sx+8,cy-4),2)
        pygame.draw.line(surf,(80,80,100),(sx+self.W-4,cy),(sx+self.W-8,cy-4),2)
        bw=30; bx=cx-bw//2; by=int(self.y)-10
        pygame.draw.rect(surf,DARK,(bx,by,bw,4))
        hp_r=self.hp/self.MAX_HP
        pygame.draw.rect(surf,(50,200,80) if hp_r>0.5 else RED,(bx,by,int(bw*hp_r),4))


# ================================================
#  HELIKOPTER
# ================================================
class Helicopter:
    W=90; H=35; MAX_HP=200; SPEED=1.5; SHOOT_RATE=1200

    def __init__(self, x):
        self.x=float(x); self.y=float(GROUND_Y-220-random.randint(0,60))
        self.hp=self.MAX_HP; self.alive=True; self.facing=-1
        self.last_shot=0; self.rotor_angle=0.0
        self.strafe_dir=random.choice([-1,1]); self.strafe_timer=0

    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    @property
    def is_air(self): return True

    def update(self, player, bullets):
        self.rotor_angle+=0.2
        dx=player.x-self.x
        self.facing=1 if dx>0 else -1
        # Seitwärts manövrieren
        self.strafe_timer+=1
        if self.strafe_timer>120: self.strafe_dir*=-1; self.strafe_timer=0
        self.x+=self.strafe_dir*self.SPEED
        self.x=max(100,min(WORLD_WIDTH-100,self.x))
        # Leichtes Bob
        self.y+=math.sin(pygame.time.get_ticks()*0.002)*0.3
        # Schießen (Salve)
        now=pygame.time.get_ticks()
        if now-self.last_shot>=self.SHOOT_RATE and abs(dx)<800:
            self.last_shot=now
            SFX.play(SFX.shoot_rifle)
            ox=self.rect.centerx; oy=self.rect.bottom+5
            tx=player.rect.centerx; ty=player.rect.centery
            for i in range(3):
                d2=math.hypot(tx-ox,ty-oy) or 1
                angle=math.atan2(ty-oy,tx-ox)+random.uniform(-0.15,0.15)
                bullets.append(Bullet(ox,oy,math.cos(angle)*13,math.sin(angle)*13,12,(255,150,50)))

    def take_damage(self, amount, is_rocket=False):
        dmg = amount if is_rocket else amount // 3
        self.hp-=dmg; SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_sparks(self.rect.centerx,self.rect.centery,8)
        if self.hp<=0:
            self.alive=False
            PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=1.8)
            SFX.play(SFX.big_explosion)

    def draw(self, surf, cam_x=0):
        sx=int(self.x)-cam_x; cx=sx+self.W//2; cy=int(self.y)+self.H//2
        # Rumpf
        pygame.draw.ellipse(surf,(80,80,100),pygame.Rect(sx+10,cy-12,60,24))
        # Cockpit
        pygame.draw.ellipse(surf,(60,180,220),pygame.Rect(sx+14,cy-8,22,16))
        # Heckausleger
        pygame.draw.rect(surf,(70,70,90),pygame.Rect(sx+60,cy-4,28,8))
        # Heckrotor
        hr_x=sx+self.W-4; hr_y=cy
        for angle in [self.rotor_angle, self.rotor_angle+math.pi]:
            pygame.draw.line(surf,(160,160,180),(hr_x,hr_y),
                             (hr_x+int(math.cos(angle)*10),hr_y+int(math.sin(angle)*10)),2)
        # Hauptrotor
        for angle in [self.rotor_angle*1.5+i*math.pi/2 for i in range(4)]:
            rx=int(math.cos(angle)*38); ry=int(math.sin(angle)*6)
            pygame.draw.line(surf,(180,180,200),(cx-rx,cy-14+ry),(cx+rx,cy-14-ry),3)
        # Waffen
        pygame.draw.rect(surf,(50,50,60),pygame.Rect(sx+20,cy+8,14,6))
        pygame.draw.rect(surf,(50,50,60),pygame.Rect(sx+56,cy+8,14,6))
        bw=80; bx=cx-bw//2; by=int(self.y)-14
        pygame.draw.rect(surf,DARK,(bx,by,bw,7))
        hp_r=self.hp/self.MAX_HP
        hc=(50,200,80) if hp_r>0.5 else YELLOW if hp_r>0.25 else RED
        pygame.draw.rect(surf,hc,(bx,by,int(bw*hp_r),7))
        pygame.draw.rect(surf,GRAY,(bx,by,bw,7),1)
        lf=pygame.font.SysFont("consolas",10,bold=True)
        lb=lf.render("HELI",True,(200,200,100))
        surf.blit(lb,(cx-lb.get_width()//2,by-12))


# ================================================
#  JET
# ================================================
class Jet:
    W=80; H=22; MAX_HP=120; SPEED=6; SHOOT_RATE=2000

    def __init__(self, x):
        self.x=float(x); self.y=float(GROUND_Y-260-random.randint(0,80))
        self.hp=self.MAX_HP; self.alive=True; self.facing=-1
        self.last_shot=0; self.vx=-self.SPEED
        self.dive_timer=random.randint(200,400); self.diving=False

    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)
    @property
    def is_air(self): return True

    def update(self, player, bullets):
        # Jet fliegt hin und her, macht gelegentlich Sturzflug
        self.dive_timer-=1
        if self.dive_timer<=0 and not self.diving:
            self.diving=True; self.dive_timer=80
        if self.diving:
            self.y=min(self.y+4, GROUND_Y-150)
            if self.dive_timer<=0: self.diving=False; self.dive_timer=random.randint(150,300)
        else:
            self.y=max(self.y-2, GROUND_Y-300)
        self.x+=self.vx
        # Umkehren am Rand
        if self.x<-200 or self.x>WORLD_WIDTH+200:
            self.vx*=-1; self.facing*=-1
        # Schießen im Vorbeiflug
        now=pygame.time.get_ticks()
        dist=abs(player.x-self.x)
        if now-self.last_shot>=self.SHOOT_RATE and dist<600:
            self.last_shot=now
            SFX.play(SFX.shoot_rifle)
            ox=self.rect.centerx; oy=self.rect.centery
            tx=player.rect.centerx; ty=player.rect.centery
            d2=math.hypot(tx-ox,ty-oy) or 1
            for off in [-0.1,0,0.1]:
                angle=math.atan2(ty-oy,tx-ox)+off
                bullets.append(Bullet(ox,oy,math.cos(angle)*15,math.sin(angle)*15,14,(255,200,50)))
        # Nachbrenner-Partikel
        if random.random()<0.6:
            PARTICLES.spawn_smoke(int(self.x)+(-self.W//2 if self.vx>0 else self.W),int(self.y)+10)

    def take_damage(self, amount, is_rocket=False):
        dmg = amount if is_rocket else amount // 5  # Jet sehr resistent gegen Kugeln
        self.hp-=dmg; SFX.play(SFX.hit_enemy)
        PARTICLES.spawn_sparks(self.rect.centerx,self.rect.centery,6)
        if self.hp<=0:
            self.alive=False
            PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=1.5)
            SFX.play(SFX.big_explosion)

    def draw(self, surf, cam_x=0):
        sx=int(self.x)-cam_x; cx=sx+self.W//2; cy=int(self.y)+self.H//2
        f=1 if self.vx>0 else -1
        # Rumpf
        pts=[(sx,cy+4),(sx+f*20,cy-2),(sx+f*60,cy-2),(sx+f*self.W,cy+2),
             (sx+f*60,cy+8),(sx+f*20,cy+8)]
        pygame.draw.polygon(surf,(60,80,80),pts)
        # Cockpit
        pygame.draw.ellipse(surf,(60,200,220),pygame.Rect(sx+f*10-5,cy-6,22,12))
        # Flügel
        wing_x=sx+f*35
        pygame.draw.polygon(surf,(50,70,70),[(wing_x,cy+2),(wing_x+f*10,cy+20),(wing_x+f*30,cy+2)])
        pygame.draw.polygon(surf,(50,70,70),[(wing_x,cy-2),(wing_x+f*10,cy-18),(wing_x+f*30,cy-2)])
        # Nachbrenner-Flamme
        tail_x=sx+(0 if f>0 else self.W)
        fl=random.randint(10,25)
        pygame.draw.polygon(surf,ORANGE,[(tail_x,cy-4),(tail_x,cy+4),(tail_x-f*fl,cy)])
        bw=60; bx=cx-bw//2; by=int(self.y)-14
        pygame.draw.rect(surf,DARK,(bx,by,bw,5))
        hp_r=self.hp/self.MAX_HP
        pygame.draw.rect(surf,(50,200,80) if hp_r>0.5 else RED,(bx,by,int(bw*hp_r),5))
        lf=pygame.font.SysFont("consolas",10,bold=True)
        lb=lf.render("JET",True,(200,200,100))
        surf.blit(lb,(cx-lb.get_width()//2,by-12))


# ================================================
#  BOSS  (finaler Boss in Zone 6)
# ================================================
class Boss:
    W=60; H=80; MAX_HP=500; SPEED=1.8; SHOOT_RATE=700; BURST_SIZE=3

    def __init__(self, x, y):
        self.x=float(x); self.y=float(y); self.vy=0.0
        self.hp=self.MAX_HP; self.alive=True
        self.last_shot=0; self.facing=-1
        self.phase=1; self.walk_frame=0; self.walk_timer=0
        self.jump_timer=0; self.roar_done=False; self.on_ground=False
        self.summon_timer=600; self.rockets_fired=0

    @property
    def rect(self): return pygame.Rect(int(self.x),int(self.y),self.W,self.H)

    def update(self, player, bullets, enemy_rockets):
        if not self.roar_done: SFX.play(SFX.boss_roar); self.roar_done=True
        if self.hp<self.MAX_HP*0.66: self.phase=max(self.phase,2)
        if self.hp<self.MAX_HP*0.33: self.phase=3
        self.vy=min(self.vy+0.7,18); self.y+=self.vy; self.on_ground=False
        for plat in current_platforms:
            r=self.rect
            if r.colliderect(plat) and self.vy>=0:
                if r.bottom-self.vy<=plat.top+abs(self.vy)+2:
                    self.y=plat.top-self.H; self.vy=0; self.on_ground=True
        dx=player.x-self.x; sp=self.SPEED*(1+self.phase*0.2)
        if abs(dx)>10:
            self.x+=sp*(1 if dx>0 else -1); self.facing=1 if dx>0 else -1
            self.walk_timer+=1
            if self.walk_timer>6: self.walk_frame=(self.walk_frame+1)%4; self.walk_timer=0
        if self.phase>=2:
            self.jump_timer+=1
            if self.jump_timer>200 and self.on_ground: self.vy=-22; self.jump_timer=0
        # Raketen in Phase 3
        if self.phase==3:
            self.summon_timer-=1
            if self.summon_timer<=0:
                self.summon_timer=300
                ox=self.rect.centerx; oy=self.rect.centery
                tx=player.rect.centerx; ty=player.rect.centery
                dx2=tx-ox; dy2=ty-oy; d=math.hypot(dx2,dy2) or 1
                enemy_rockets.append(Rocket(ox,oy,dx2/d*10,dy2/d*10,35,ROCKET_COL))
                SFX.play(SFX.shoot_rocket)
        self.x=max(0,min(WORLD_WIDTH-self.W,self.x))
        now=pygame.time.get_ticks()
        rate=self.SHOOT_RATE//(self.phase)
        if now-self.last_shot>=rate and abs(dx)<800:
            self.last_shot=now
            spread=self.BURST_SIZE+self.phase
            SFX.play(SFX.shoot_rifle)
            ox=self.rect.centerx; oy=self.rect.centery
            tx=player.rect.centerx; ty=player.rect.centery
            for i in range(spread):
                off=(i-spread//2)*0.07
                dx2=tx-ox; dy2=ty-oy; dist=math.hypot(dx2,dy2) or 1
                angle=math.atan2(dy2,dx2)+off
                vx=math.cos(angle)*13; vy=math.sin(angle)*13
                bullets.append(Bullet(ox,oy+i*8-spread*4,vx,vy,15,(255,80,80)))
                PARTICLES.spawn_muzzle_flash(ox+self.facing*25,oy,self.facing)

    def take_damage(self, amount):
        self.hp-=amount; PARTICLES.spawn_blood(self.rect.centerx,self.rect.centery,6)
        if self.hp<=0:
            self.alive=False
            PARTICLES.spawn_explosion(self.rect.centerx,self.rect.centery,scale=3.0)
            SFX.play(SFX.big_explosion)

    def draw(self, surf, cam_x=0):
        sx=int(self.x)-cam_x; cx=sx+self.W//2; cy=int(self.y); f=self.facing
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
        bw=120; bx=cx-bw//2; by=cy-22
        pygame.draw.rect(surf,DARK,(bx,by,bw,12))
        hc=(255,50,50) if self.phase==3 else (220,100,20) if self.phase==2 else (200,50,50)
        pygame.draw.rect(surf,hc,(bx,by,int(bw*self.hp/self.MAX_HP),12))
        pygame.draw.rect(surf,WHITE,(bx,by,bw,12),1)
        lf=pygame.font.SysFont("consolas",13,bold=True)
        lb=lf.render(f"GENERAL  [PHASE {self.phase}]",True,(255,200,50))
        surf.blit(lb,(cx-lb.get_width()//2,by-18))


# ================================================
#  SCREEN SHAKE
# ================================================
def get_shake_offset():
    global screen_shake
    if screen_shake>0:
        ox=random.randint(-screen_shake,screen_shake)
        oy=random.randint(-screen_shake,screen_shake)
        screen_shake=max(0,screen_shake-1); return ox,oy
    return 0,0


# ================================================
#  FONTS & HUD
# ================================================
font_big   = pygame.font.SysFont("consolas",28,bold=True)
font_med   = pygame.font.SysFont("consolas",22,bold=True)
font_small = pygame.font.SysFont("consolas",16)
font_tiny  = pygame.font.SysFont("consolas",13)

WEAPON_KEYS = {
    pygame.K_1: PISTOLE, pygame.K_2: STURMGEWEHR, pygame.K_3: SCHARFSCHUETZE,
    pygame.K_4: SCHROTFLINTE, pygame.K_5: RAKETENWERFER,
    pygame.K_6: STINGER, pygame.K_7: MESSER,
}

def draw_hud(surf, player, zone_num, zone_name, enemies_left, air_left):
    panel=pygame.Surface((420,130),pygame.SRCALPHA); panel.fill((0,0,0,160))
    surf.blit(panel,(8,8))
    # Leben
    for i in range(player.MAX_LIVES):
        col=RED if i<player.lives else (50,20,20)
        pygame.draw.circle(surf,col,(28+i*28,28),9)
        pygame.draw.circle(surf,col,(40+i*28,28),9)
        pygame.draw.polygon(surf,col,[(20+i*28,32),(48+i*28,32),(34+i*28,47)])
    # HP
    pygame.draw.rect(surf,DARK,(14,52,200,14))
    hr=player.hp/player.MAX_HP; hc=GREEN if hr>0.5 else YELLOW if hr>0.25 else RED
    pygame.draw.rect(surf,hc,(14,52,int(200*hr),14)); pygame.draw.rect(surf,GRAY,(14,52,200,14),1)
    surf.blit(font_tiny.render(f"HP {player.hp}",True,WHITE),(220,53))
    # Waffen (2 Zeilen)
    weapons_row1=[(PISTOLE,"[1]"),(STURMGEWEHR,"[2]"),(SCHARFSCHUETZE,"[3]"),(SCHROTFLINTE,"[4]")]
    weapons_row2=[(RAKETENWERFER,"[5]"),(STINGER,"[6]"),(MESSER,"[7]")]
    for i,(w,label) in enumerate(weapons_row1):
        col=YELLOW if player.weapon==w else GRAY
        ammo_str=f"({w.ammo})" if w.ammo is not None else ""
        surf.blit(font_tiny.render(f"{label}{w.name[:8]}{ammo_str}",True,col),(14+i*100,72))
    for i,(w,label) in enumerate(weapons_row2):
        col=YELLOW if player.weapon==w else GRAY
        ammo_str=f"({w.ammo})" if w.ammo is not None else ""
        surf.blit(font_tiny.render(f"{label}{w.name[:10]}{ammo_str}",True,col),(14+i*130,88))
    surf.blit(font_tiny.render(f"Granaten: {'X '*player.grenades}",True,ORANGE),(14,106))
    # Score
    sc=font_med.render(f"SCORE: {player.score}",True,YELLOW)
    surf.blit(sc,(WIDTH//2-sc.get_width()//2,14))
    # Rechts: Zone + Feinde
    zt=font_small.render(f"ZONE {zone_num}/{NUM_ZONES}",True,WHITE)
    nt=font_tiny.render(zone_name,True,GRAY)
    et=font_tiny.render(f"Boden: {enemies_left}",True,(255,150,150))
    at=font_tiny.render(f"Luft:  {air_left}",True,CYAN)
    surf.blit(zt,(WIDTH-zt.get_width()-14,14))
    surf.blit(nt,(WIDTH-nt.get_width()-14,38))
    surf.blit(et,(WIDTH-et.get_width()-14,56))
    surf.blit(at,(WIDTH-at.get_width()-14,72))
    # Tipp: Raketenwerfer gegen Tanks
    if enemies_left > 0 or air_left > 0:
        tip_col=(200,200,100)
        surf.blit(font_tiny.render("[5] Raketenwerfer → Tanks  |  [6] Stinger → Luft",True,tip_col),
                  (WIDTH//2-180,HEIGHT-36))


# ================================================
#  WELT ZEICHNEN
# ================================================
def draw_world(surf, zone_cfg, cam_x, tick=0):
    sky=zone_cfg["sky"]; surf.fill(sky); par_off=int(cam_x*0.35)

    # Zone 1: Stadt
    if sky==(28,38,58):
        for rx,rw,rh in [(0,100,200),(130,80,150),(260,120,220),(450,90,170),
                          (620,130,200),(820,100,160),(1010,110,190),(1200,90,140),
                          (1380,120,210),(1580,100,180),(1780,90,160),(1950,130,220)]:
            sx=rx-par_off
            if -200<sx<WIDTH+200:
                dmg=(rx*7+17)%3==0
                col=(18,24,38) if not dmg else (25,18,15)
                pygame.draw.rect(surf,col,(sx,GROUND_Y-rh,rw,rh))
                if dmg:
                    pygame.draw.polygon(surf,sky,[(sx+rw-20,GROUND_Y-rh),(sx+rw,GROUND_Y-rh),(sx+rw,GROUND_Y-rh+25)])
                for wy in range(GROUND_Y-rh+15,GROUND_Y-10,28):
                    for wx in range(sx+8,sx+rw-8,18):
                        lit=(wx+wy*3+tick//12)%40
                        wc=YELLOW if lit<12 and (wx+wy)%55<28 else DARK
                        pygame.draw.rect(surf,wc,(wx,wy,9,13))
        for i in range(8):
            rx=(i*430+200)%WORLD_WIDTH; sx=rx-cam_x
            if -50<sx<WIDTH+50:
                t2=(tick+i*80)%200; sy=GROUND_Y-80-t2; a=max(0,80-t2//2)
                sm=pygame.Surface((30+t2//5,20+t2//8),pygame.SRCALPHA)
                pygame.draw.ellipse(sm,(80,80,80,a),(0,0,30+t2//5,20+t2//8))
                surf.blit(sm,(sx-15,sy))

    # Zone 2: Wald
    elif sky==(18,42,20):
        for tx in range(-200,WORLD_WIDTH+200,85):
            sx=tx-par_off
            if -150<sx<WIDTH+150:
                h=150+(tx*9)%90; dg=(8+(tx*3)%18,45+(tx*5)%28,8)
                pygame.draw.polygon(surf,dg,[(sx+18,GROUND_Y-h),(sx+43,GROUND_Y-h-65),(sx+68,GROUND_Y-h)])
                pygame.draw.rect(surf,(40,22,12),(sx+35,GROUND_Y-h+5,16,h-10))
        for i in range(0,WIDTH,14):
            ry=(tick*4+i*7)%HEIGHT
            pygame.draw.line(surf,(60,100,70),(i,ry),(i-3,ry+18),1)

    # Zone 3: Wüste
    elif sky==(80,55,30):
        # Sanddünen im Hintergrund
        for dx in range(-100,WORLD_WIDTH+100,200):
            sx=dx-par_off
            if -200<sx<WIDTH+200:
                h=60+(dx*7)%80
                pygame.draw.ellipse(surf,(120,90,40),(sx,GROUND_Y-h,180,h*2))
        # Hitzewellen-Effekt (Boden)
        for i in range(0,WIDTH,20):
            wave=int(math.sin((i+tick*0.3)*0.1)*3)
            pygame.draw.line(surf,(150,110,50),(i,GROUND_Y-5+wave),(i+20,GROUND_Y-5+wave),2)

    # Zone 4: Militärbasis (Nacht)
    elif sky==(12,12,28):
        for i in range(50):
            sx2=(i*137+23)%WIDTH; sy2=(i*97+11)%(HEIGHT//2-20)
            a2=120+(math.sin(tick*0.05+i)*50)
            s2=pygame.Surface((3,3),pygame.SRCALPHA)
            pygame.draw.circle(s2,(220,220,255,int(a2)),(1,1),1); surf.blit(s2,(sx2,sy2))
        for rx,rw,rh in [(0,220,195),(270,200,215),(530,240,175),(810,210,230),
                          (1080,200,185),(1340,230,200),(1620,200,195),(1900,240,185)]:
            sx=rx-par_off
            if -300<sx<WIDTH+300:
                pygame.draw.rect(surf,(10,10,25),(sx,GROUND_Y-rh,rw,rh))
        for i in range(3):
            lx=(i*1200+600)%WORLD_WIDTH; ls=lx-cam_x
            if -200<ls<WIDTH+200:
                angle_r=math.sin(tick*0.018+i*2.1)*0.5
                ex=int(ls+math.sin(angle_r)*300); ey=GROUND_Y-20
                _spotlight_surf.fill((0,0,0,0))
                points=[(ls,0),(ls-40,0),(ex-25,ey),(ex+25,ey),(ls+40,0)]
                pygame.draw.polygon(_spotlight_surf,(255,255,200,18),points)
                surf.blit(_spotlight_surf,(0,0))
                pygame.draw.circle(surf,(255,255,180),(ls,0),8)

    # Zone 5: Arktis
    elif sky==(160,190,220):
        # Schneeberge
        for mx in range(-100,WORLD_WIDTH+100,300):
            sx=mx-par_off
            if -300<sx<WIDTH+300:
                h=120+(mx*11)%100
                pygame.draw.polygon(surf,(180,200,220),[(sx,GROUND_Y),(sx+150,GROUND_Y),(sx+75,GROUND_Y-h)])
                pygame.draw.polygon(surf,(230,240,255),[(sx+50,GROUND_Y-h+30),(sx+75,GROUND_Y-h),(sx+100,GROUND_Y-h+30)])
        # Schneeflocken
        for i in range(30):
            fx=(i*173+tick*2)%WIDTH; fy=(i*97+tick*3)%HEIGHT
            pygame.draw.circle(surf,WHITE,(fx,fy),2)

    # Zone 6: Festung (Nacht, Rot)
    elif sky==(8,5,18):
        for i in range(80):
            sx2=(i*137+23)%WIDTH; sy2=(i*97+11)%(HEIGHT//2)
            a2=80+(math.sin(tick*0.04+i)*40)
            pygame.draw.circle(surf,(220,100,100,int(a2)),(sx2,sy2),1)
        for rx,rw,rh in [(0,250,220),(300,220,250),(620,260,200),(920,240,260),
                          (1200,220,210),(1500,250,240),(1800,220,220),(2100,260,250)]:
            sx=rx-par_off
            if -300<sx<WIDTH+300:
                pygame.draw.rect(surf,(15,8,25),(sx,GROUND_Y-rh,rw,rh))
                pygame.draw.rect(surf,(30,15,45),(sx,GROUND_Y-rh,rw,rh),2)
                # Rote Fenster
                for wy in range(GROUND_Y-rh+20,GROUND_Y-10,35):
                    for wx in range(sx+12,sx+rw-12,26):
                        fl=(wx*13+wy*7+tick//8)%22
                        wc=(120,20,20) if (wx+wy)%48<24 and fl>2 else DARK
                        pygame.draw.rect(surf,wc,(wx,wy,12,16))

    # Plattformen zeichnen
    for plat in current_platforms:
        sr=pygame.Rect(plat.x-cam_x,plat.y,plat.w,plat.h)
        if -plat.w<sr.x<WIDTH+plat.w:
            if plat.h>60:
                pygame.draw.rect(surf,zone_cfg["ground"],sr)
                g=zone_cfg["ground"]
                pygame.draw.rect(surf,(min(g[0]+25,255),min(g[1]+20,255),min(g[2]+12,255)),sr,3)
            else:
                g=zone_cfg["ground"]
                edge_col=(min(g[0]+40,255),min(g[1]+35,255),min(g[2]+20,255))
                pygame.draw.rect(surf,g,sr); pygame.draw.rect(surf,edge_col,sr,3)
                for bx2 in range(sr.x+12,sr.x+sr.w,22):
                    pygame.draw.line(surf,(max(g[0]-10,0),max(g[1]-8,0),max(g[2]-5,0)),
                                     (bx2,sr.y),(bx2,sr.y+sr.h),1)


# ================================================
#  MENUE
# ================================================
def draw_menu_bg(surf, tick):
    surf.fill((8,12,22))
    for i in range(60):
        x=(i*137+tick//3)%WIDTH; y=(i*97+tick//5)%(HEIGHT//2)
        r=1+i%2; a=100+(tick*2+i*30)%155
        s=pygame.Surface((r*2,r*2),pygame.SRCALPHA)
        pygame.draw.circle(s,(200,220,255,a),(r,r),r); surf.blit(s,(x,y))
    for rx,rw,rh in [(0,120,180),(130,90,130),(240,150,200),(450,100,160),
                      (600,130,190),(780,110,150),(940,140,170),(1100,120,140)]:
        pygame.draw.rect(surf,(12,18,30),(rx,HEIGHT-rh,rw,rh))
    pygame.draw.rect(surf,(18,24,36),(0,HEIGHT-40,WIDTH,40))
    glow=pygame.Surface((400,300),pygame.SRCALPHA)
    pulse=abs(math.sin(tick*0.02))*30
    pygame.draw.ellipse(glow,(200,30,30,int(18+pulse)),(0,0,400,300))
    surf.blit(glow,(WIDTH//2-200,HEIGHT//2-100))

class MenuButton:
    def __init__(self,text,x,y,w=260,h=50):
        self.text=text; self.rect=pygame.Rect(x-w//2,y-h//2,w,h)
        self.hovered=False; self.font=pygame.font.SysFont("consolas",20,bold=True)
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

def show_main_menu():
    btns=[MenuButton("SPIELEN",WIDTH//2,270),MenuButton("HIGHSCORES",WIDTH//2,335),
          MenuButton("STEUERUNG",WIDTH//2,400),MenuButton("BEENDEN",WIDTH//2,465)]
    sf=pygame.font.SysFont("consolas",60,bold=True); tf=pygame.font.SysFont("consolas",18)
    tick=0
    while True:
        tick+=1; mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if btns[0].clicked((mx,my)): return "play"
                if btns[1].clicked((mx,my)): return "highscores"
                if btns[2].clicked((mx,my)): return "controls"
                if btns[3].clicked((mx,my)): pygame.quit(); sys.exit()
        draw_menu_bg(screen,tick)
        sh=sf.render("PROJEKT FRONTLINE",True,(90,10,10))
        screen.blit(sh,(WIDTH//2-sh.get_width()//2+3,78))
        t1=sf.render("PROJEKT FRONTLINE",True,(220,50,50))
        screen.blit(t1,(WIDTH//2-t1.get_width()//2,75))
        alpha=180+int(abs(math.sin(tick*0.04))*75)
        sub=tf.render("[ TAKTISCHER 2D-SHOOTER  v4.0 ]",True,(min(255,alpha),min(255,alpha//2),50))
        screen.blit(sub,(WIDTH//2-sub.get_width()//2,148))
        hint=tf.render("WASD/Pfeile: Bewegen  |  SPACE: Springen  |  Klick: Schiessen  |  G: Granate  |  1-7: Waffe",True,(70,70,90))
        screen.blit(hint,(WIDTH//2-hint.get_width()//2,HEIGHT-22))
        for b in btns: b.update((mx,my)); b.draw(screen)
        pygame.display.flip(); clock.tick(FPS)

def show_highscores():
    scores=load_highscores(); back=MenuButton("< ZURUECK",WIDTH//2,HEIGHT-60,w=200,h=44)
    tick=0
    while True:
        tick+=1; mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if back.clicked((mx,my)): return
        draw_menu_bg(screen,tick)
        tf=pygame.font.SysFont("consolas",40,bold=True); rf=pygame.font.SysFont("consolas",20)
        t=tf.render("HIGHSCORES",True,YELLOW); screen.blit(t,(WIDTH//2-t.get_width()//2,55))
        pygame.draw.line(screen,(100,80,30),(WIDTH//2-200,105),(WIDTH//2+200,105),2)
        h=rf.render(f"{'#':<4}  {'NAME':<13}  {'SCORE':>8}  ZONE",True,(200,200,100))
        screen.blit(h,(WIDTH//2-h.get_width()//2,118))
        if not scores:
            n=pygame.font.SysFont("consolas",17).render("Noch keine Eintraege!",True,GRAY)
            screen.blit(n,(WIDTH//2-n.get_width()//2,180))
        else:
            for i,s in enumerate(scores[:10]):
                col=YELLOW if i==0 else (WHITE if i<3 else GRAY)
                row=rf.render(f"{i+1:<4}  {s['name']:<13}  {s['score']:>8}  Zone {s['zone']}",True,col)
                screen.blit(row,(WIDTH//2-row.get_width()//2,150+i*30))
        back.update((mx,my)); back.draw(screen)
        pygame.display.flip(); clock.tick(FPS)

def show_controls():
    back=MenuButton("< ZURUECK",WIDTH//2,HEIGHT-55,w=200,h=44)
    ctrls=[
        ("A/D  oder  Pfeile","Bewegen"),("LEERTASTE","Springen"),
        ("LINKSKLICK","Schiessen (zur Maus)"),("G","Granate werfen"),
        ("1","Pistole  (15 DMG)"),("2","Sturmgewehr  (8 DMG, Auto)"),
        ("3","Scharfschuetze  (55 DMG)"),("4","Schrotflinte  (18x8 DMG)"),
        ("5","Raketenwerfer  (120 DMG) → Tanks!"),
        ("6","Stinger AA  (150 DMG) → Luft!"),
        ("7","Messer  (35 DMG, Nahkampf)"),("ESC","Menue"),
    ]
    tick=0; kf=pygame.font.SysFont("consolas",16,bold=True); vf=pygame.font.SysFont("consolas",15)
    tf=pygame.font.SysFont("consolas",36,bold=True)
    while True:
        tick+=1; mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if back.clicked((mx,my)): return
        draw_menu_bg(screen,tick)
        t=tf.render("STEUERUNG",True,YELLOW); screen.blit(t,(WIDTH//2-t.get_width()//2,35))
        pygame.draw.line(screen,(100,80,30),(WIDTH//2-200,82),(WIDTH//2+200,82),2)
        for i,(k,v) in enumerate(ctrls):
            screen.blit(kf.render(k,True,(240,200,60)),(WIDTH//2-380,92+i*36))
            screen.blit(vf.render(v,True,(180,180,180)),(WIDTH//2-30,96+i*36))
        back.update((mx,my)); back.draw(screen)
        pygame.display.flip(); clock.tick(FPS)

def show_zone_intro(zone_num, zone_name):
    f1=pygame.font.SysFont("consolas",50,bold=True); f2=pygame.font.SysFont("consolas",22)
    for alpha in list(range(0,256,8))+[255]*20+list(range(255,0,-8)):
        screen.fill((0,0,0))
        s=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        t1=f1.render(f"ZONE {zone_num}",True,RED)
        n=zone_name.split(":")[1].strip() if ":" in zone_name else zone_name
        t2=f2.render(n,True,WHITE)
        s.set_alpha(alpha)
        s.blit(t1,(WIDTH//2-t1.get_width()//2,HEIGHT//2-50))
        s.blit(t2,(WIDTH//2-t2.get_width()//2,HEIGHT//2+20))
        screen.blit(s,(0,0)); pygame.display.flip(); clock.tick(30)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()

def show_name_input(score, zone):
    name=""; cur=0
    confirm=MenuButton("EINTRAGEN  >",WIDTH//2,HEIGHT//2+100,w=260,h=50)
    tf=pygame.font.SysFont("consolas",36,bold=True); inf=pygame.font.SysFont("consolas",30,bold=True)
    tick=0
    while True:
        tick+=1; cur+=1; mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_RETURN and name.strip(): save_highscore(name.strip()[:12],score,zone); return
                elif event.key==pygame.K_BACKSPACE: name=name[:-1]
                elif len(name)<12 and event.unicode.isprintable(): name+=event.unicode
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if confirm.clicked((mx,my)) and name.strip(): save_highscore(name.strip()[:12],score,zone); return
        draw_menu_bg(screen,tick)
        t=tf.render("HIGHSCORE EINTRAGEN",True,YELLOW); screen.blit(t,(WIDTH//2-t.get_width()//2,HEIGHT//2-200))
        sc=inf.render(f"Score: {score}   |   Zone {zone}",True,WHITE); screen.blit(sc,(WIDTH//2-sc.get_width()//2,HEIGHT//2-140))
        ir=pygame.Rect(WIDTH//2-150,HEIGHT//2-30,300,54)
        pygame.draw.rect(screen,(30,30,50),ir,border_radius=6)
        pygame.draw.rect(screen,(100,100,160),ir,2,border_radius=6)
        cursor="|" if cur%40<20 else ""
        it=inf.render(name+cursor,True,WHITE); screen.blit(it,(ir.centerx-it.get_width()//2,ir.centery-it.get_height()//2))
        confirm.update((mx,my)); confirm.draw(screen)
        pygame.display.flip(); clock.tick(FPS)

def show_gameover(score, zone):
    retry=MenuButton("NOCHMAL VERSUCHEN",WIDTH//2,HEIGHT//2+60,w=280,h=50)
    menu=MenuButton("HAUPTMENUE",WIDTH//2,HEIGHT//2+125,w=260,h=50)
    tick=0; f1=pygame.font.SysFont("consolas",60,bold=True); f2=pygame.font.SysFont("consolas",22)
    while True:
        tick+=1; mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: return "menu"
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if retry.clicked((mx,my)): return "retry"
                if menu.clicked((mx,my)): return "menu"
        draw_menu_bg(screen,tick)
        t1=f1.render("GAME OVER",True,RED); t2=f2.render(f"Score: {score}   |   Zone {zone} erreicht",True,GRAY)
        screen.blit(t1,(WIDTH//2-t1.get_width()//2,HEIGHT//2-120))
        screen.blit(t2,(WIDTH//2-t2.get_width()//2,HEIGHT//2-40))
        retry.update((mx,my)); menu.update((mx,my)); retry.draw(screen); menu.draw(screen)
        pygame.display.flip(); clock.tick(FPS)

def show_win(score):
    hs=MenuButton("HIGHSCORE SPEICHERN",WIDTH//2,HEIGHT//2+55,w=300,h=50)
    menu=MenuButton("HAUPTMENUE",WIDTH//2,HEIGHT//2+120,w=260,h=50)
    tick=0; f1=pygame.font.SysFont("consolas",44,bold=True)
    f2=pygame.font.SysFont("consolas",24); f3=pygame.font.SysFont("consolas",18)
    while True:
        tick+=1; mx,my=pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if hs.clicked((mx,my)): return "highscore"
                if menu.clicked((mx,my)): return "menu"
        draw_menu_bg(screen,tick)
        t1=f1.render("SIEG! ALLE ZONEN BEFREIT!",True,GREEN)
        t2=f2.render(f"Finaler Score: {score}",True,YELLOW)
        t3=f3.render("General besiegt - Festung Omega gefallen!",True,WHITE)
        screen.blit(t1,(WIDTH//2-t1.get_width()//2,HEIGHT//2-140))
        screen.blit(t2,(WIDTH//2-t2.get_width()//2,HEIGHT//2-70))
        screen.blit(t3,(WIDTH//2-t3.get_width()//2,HEIGHT//2-30))
        hs.update((mx,my)); menu.update((mx,my)); hs.draw(screen); menu.draw(screen)
        pygame.display.flip(); clock.tick(FPS)


# ================================================
#  ZONE SPIELEN
# ================================================
def play_zone(zone_num, player):
    global current_platforms, screen_shake
    cfg=ZONES[zone_num]
    current_platforms=cfg["platforms"]
    player.x=100.0; player.y=float(current_platforms[0].top-Player.H)
    player.vx=player.vy=0.0; player.hp=player.MAX_HP
    player.invincible=1500; screen_shake=0; PARTICLES.particles.clear()
    # Waffen-Munition zurücksetzen
    RAKETENWERFER.ammo=RAKETENWERFER.max_ammo
    STINGER.ammo=STINGER.max_ammo

    camera=Camera(); camera.x=0.0
    is_boss_zone=(zone_num==NUM_ZONES)

    # Bodenfeinde
    enemies=[Enemy(ex,ey,hp=cfg["enemy_hp"],speed=cfg["enemy_speed"],
                   shoot_rate=cfg["enemy_shoot_rate"]) for ex,ey in cfg["enemy_positions"]]

    # Tanks
    tanks=[]
    for tx2,ty2 in cfg.get("tank_positions",[]):
        tanks.append(Tank(tx2,ty2))

    # Jetpack-Soldaten
    jetpack_soldiers=[]
    for jx,jy in cfg.get("jetpack_positions",[]):
        jetpack_soldiers.append(JetpackSoldier(jx,jy))

    # Luftfeinde (Drohnen, Helis, Jets)
    air_enemies=[]
    for etype,ex2 in cfg.get("air_enemies",[]):
        if etype=="drone":      air_enemies.append(Drone(ex2))
        elif etype=="helicopter": air_enemies.append(Helicopter(ex2))
        elif etype=="jet":      air_enemies.append(Jet(ex2))

    # Boss
    boss=Boss(WORLD_WIDTH-400,current_platforms[0].top-Boss.H) if is_boss_zone else None

    bullets=[]; enemy_bullets=[]; grenades=[]; enemy_grenades=[]
    player_rockets=[]; enemy_rockets=[]; tick=0

    show_zone_intro(zone_num,cfg["name"])

    while True:
        tick+=1; clock.tick(FPS); cam_x=int(camera.x)

        for event in pygame.event.get():
            if event.type==pygame.QUIT: return "quit"
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE: return "menu"
                if event.key in WEAPON_KEYS: player.weapon=WEAPON_KEYS[event.key]
                if event.key==pygame.K_g: player.throw_grenade(grenades)
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                player.shoot(bullets, player_rockets, cam_x)

        keys=pygame.key.get_pressed()
        player.handle_input(keys, bullets, player_rockets, cam_x)
        player.update(); camera.update(player.x+player.W//2)

        # Alle Luftziele für Stinger
        all_air=[a for a in air_enemies+jetpack_soldiers if a.alive]

        # Feinde updaten
        for e in enemies:
            eb=[]; e.update(player,eb,enemy_grenades); enemy_bullets.extend(eb)
        for t in tanks:
            tb=[]; t.update(player,tb); enemy_bullets.extend(tb)
        for j in jetpack_soldiers:
            jb=[]; j.update(player,jb); enemy_bullets.extend(jb)
        for a in air_enemies:
            ab=[]; a.update(player,ab); enemy_bullets.extend(ab)
        if boss and boss.alive:
            bb=[]; boss.update(player,bb,enemy_rockets); enemy_bullets.extend(bb)

        # Spieler-Kugeln updaten & Treffer
        for b in bullets: b.update()
        for r in player_rockets: r.update(all_air)

        for b in bullets:
            if not b.alive: continue
            hit=False
            # Infanterie
            for e in enemies:
                if b.get_rect().colliderect(e.rect):
                    e.take_damage(b.damage); hit=True; b.alive=False
                    if not e.alive: player.score+=100*zone_num; break
            if not hit:
                for t in tanks:
                    if b.get_rect().colliderect(t.rect):
                        t.take_damage(b.damage,is_rocket=False); hit=True; b.alive=False
                        if not t.alive: player.score+=300*zone_num; break
            if not hit:
                for j in jetpack_soldiers:
                    if b.get_rect().colliderect(j.rect):
                        j.take_damage(b.damage); hit=True; b.alive=False
                        if not j.alive: player.score+=150*zone_num; break
            if not hit:
                for a in air_enemies:
                    if b.get_rect().colliderect(a.rect):
                        a.take_damage(b.damage); hit=True; b.alive=False
                        if not a.alive: player.score+=200*zone_num; break
            if not hit and boss and boss.alive:
                if b.get_rect().colliderect(boss.rect):
                    boss.take_damage(b.damage); b.alive=False
                    if not boss.alive: player.score+=2000

        # Raketen
        for r in player_rockets:
            if not r.alive: continue
            all_targets=(enemies+tanks+jetpack_soldiers+air_enemies+
                         ([boss] if boss and boss.alive else []))
            for tgt in all_targets:
                if r.get_rect().colliderect(tgt.rect):
                    hits=r.explode(all_targets)
                    for (t2,dmg) in hits:
                        is_r=(isinstance(t2,Tank) or isinstance(t2,Helicopter) or isinstance(t2,Jet))
                        if isinstance(t2,Tank): t2.take_damage(dmg,is_rocket=True)
                        elif isinstance(t2,Helicopter): t2.take_damage(dmg,is_rocket=True)
                        elif isinstance(t2,Jet): t2.take_damage(dmg,is_rocket=True)
                        else: t2.take_damage(dmg)
                        if not t2.alive:
                            if isinstance(t2,Boss): player.score+=2000
                            elif isinstance(t2,Tank): player.score+=300*zone_num
                            elif isinstance(t2,(Helicopter,Jet)): player.score+=400*zone_num
                            else: player.score+=150*zone_num
                    screen_shake=12
                    break

        # Messer-Nahkampf
        if player.knife_anim>0:
            kr=player.get_knife_hit_rect()
            for e in enemies:
                if kr.colliderect(e.rect):
                    e.take_damage(MESSER.damage)
                    if not e.alive: player.score+=100*zone_num

        # Feind-Kugeln & Raketen
        for b in enemy_bullets:
            b.update()
            if b.alive and b.get_rect().colliderect(player.rect):
                player.take_damage(b.damage); b.alive=False
        for r in enemy_rockets:
            r.update()
            if r.alive and r.get_rect().colliderect(player.rect):
                player.take_damage(60); r.alive=False; screen_shake=10

        # Granaten
        all_ground_targets=[e for e in enemies if e.alive]+\
                            [t for t in tanks if t.alive]+\
                            [j for j in jetpack_soldiers if j.alive]+\
                            ([boss] if boss and boss.alive else [])
        for g in grenades+enemy_grenades:
            hits=g.update(all_ground_targets)
            for (tgt,dmg) in hits:
                if isinstance(tgt,Tank): tgt.take_damage(dmg,is_rocket=False)
                else: tgt.take_damage(dmg)
                if not tgt.alive:
                    player.score+=(2000 if isinstance(tgt,Boss) else
                                   300*zone_num if isinstance(tgt,Tank) else 100*zone_num)

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

        if not player.alive: return "gameover"

        # Zonen-Ende prüfen
        all_dead=(not enemies and not tanks and not jetpack_soldiers and not air_enemies)
        if all_dead:
            if is_boss_zone:
                if boss is None or not boss.alive: SFX.play(SFX.zone_clear); return "win"
            else:
                SFX.play(SFX.zone_clear); player.score+=300*zone_num; return "next_zone"

        # ── Zeichnen ──
        ox,oy=get_shake_offset()
        game_surf=pygame.Surface((WIDTH,HEIGHT))
        draw_world(game_surf,cfg,cam_x,tick)
        PARTICLES.update(); PARTICLES.draw(game_surf,cam_x)
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

        screen.fill(DARK); screen.blit(game_surf,(ox,oy))
        el=len(enemies)+len(tanks)+len(jetpack_soldiers)
        al=len(air_enemies)+(1 if boss and boss.alive and is_boss_zone else 0)
        draw_hud(screen,player,zone_num,cfg["name"],el,al)
        ctrl=font_tiny.render(
            "WASD: Bewegen | SPACE: Springen | Klick: Schiessen | G: Granate | 1-7: Waffe",
            True,(90,90,110))
        screen.blit(ctrl,(WIDTH//2-ctrl.get_width()//2,HEIGHT-20))
        pygame.display.flip()


# ================================================
#  MAIN
# ================================================
def main():
    while True:
        action=show_main_menu()
        if action=="highscores": show_highscores(); continue
        if action=="controls":   show_controls();   continue
        player=Player(100,GROUND_Y-Player.H)
        game_state="play"; zone=1
        while game_state=="play" and zone<=NUM_ZONES:
            result=play_zone(zone,player)
            if result=="quit":       pygame.quit(); sys.exit()
            elif result=="menu":     game_state="menu"
            elif result=="gameover":
                choice=show_gameover(player.score,zone)
                if choice=="retry": player=Player(100,GROUND_Y-Player.H); zone=1
                else:               game_state="menu"
            elif result=="next_zone": zone+=1
            elif result=="win":       game_state="win"
        if game_state=="win":
            w=show_win(player.score)
            if w=="highscore": show_name_input(player.score,zone); show_highscores()

if __name__=="__main__":
    main()