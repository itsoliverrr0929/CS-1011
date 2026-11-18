# Adler Vuong

import tkinter, math, time, random, ctypes, pygame

pygame.mixer.init()
pygame.mixer.set_num_channels(16)

pygame.mixer.music.load("bkm.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(loops=-1)

gunSound = pygame.mixer.Sound("shot.mp3")
gunSound.set_volume(0.5)


playerHitSound = pygame.mixer.Sound("playerHit.mp3")
playerHitSound.set_volume(5.0)

root = tkinter.Tk()
root.geometry("1280x720")

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

root.configure(bg='blue')
root.title('CS1010 - Game')

canvas = tkinter.Canvas(root, width = 1280, height = 720, bg = "#74b560")
canvas.pack(expand = True, fill = tkinter.BOTH)

# Player Code
playerPosition = {"x": 0, "y": 0}
playerVelocity = {"x": 1400, "y": 900}
playerAmmo = 6

PLAYER_RADIUS_SIZE = 20
PLAYER_COLOR = "#db7f1d"
PLAYER_OUTLINE_COLOR = "#9c7734"
PLAYER_MAX_AMMO = 6
PLAYER_RELOAD_TIME = 1

projectilesPerShot = 1
projectileSpread = 0.01

# Player shape. It's a circle.
player = canvas.create_oval(
    playerPosition["x"] - PLAYER_RADIUS_SIZE,
    playerPosition["y"] - PLAYER_RADIUS_SIZE,
    playerPosition["x"] + PLAYER_RADIUS_SIZE,
    playerPosition["y"] + PLAYER_RADIUS_SIZE,
    fill = PLAYER_COLOR,
    outline = PLAYER_OUTLINE_COLOR,
    width = 6,
    tags = "playerGroup"
    )

playerEmptyAmmoSlice = canvas.create_arc(
    playerPosition["x"] - PLAYER_RADIUS_SIZE - 3,
    playerPosition["y"] - PLAYER_RADIUS_SIZE - 3,
    playerPosition["x"] + PLAYER_RADIUS_SIZE + 3,
    playerPosition["y"] + PLAYER_RADIUS_SIZE + 3,
    start = 0,
    extent = 0,
    style = tkinter.PIESLICE,
    fill = "#575757",
    outline = "",
    width = 0,
    tags = "playerGroup"
)

# Player healthbar setup
canvas.create_rectangle(-3, -3, 200, 50, fill = "#351A0D", outline = "#1A0202", width = 6)
healthLabel = tkinter.Label(root, text = "Health:", anchor = "nw", bg = "#351A0D", fg="#dadada", font = ("Impact", 20))
healthLabel.place(relx=0.008, rely=0.008, anchor="nw")

maxHealth = 3
healthAmount = 3
healthPoints = [
    canvas.create_rectangle(160, 17, 180, 37, fill="#ff3333", outline="#bb0000", width = "3"),
    canvas.create_rectangle(130, 17, 150, 37, fill="#ff3333", outline="#bb0000", width = "3"),
    canvas.create_rectangle(100, 17, 120, 37, fill="#ff3333", outline="#bb0000", width = "3")
]

pointsLabel = tkinter.Label(root, text = "[0000]", anchor="ne", bg="#351A0D", fg="#dadada", font = ("Impact", 20), padx=10, pady=10)
pointsLabel.place(relx=1, rely=0, anchor="ne")
points = 0
nextPointLevel = 10
level = 1


def gameOver():
    global pauseRenderLoop
    pauseRenderLoop = True
    print("Game over")
    return

def decreasePlayerHealth():
    global healthAmount
    healthAmount -= 1
    canvas.itemconfig(healthPoints[healthAmount], fill="#929292", outline="#555555")
    if(healthAmount <= 0):
        gameOver()

def increasePlayerHealth():
    global healthAmount
    if(healthAmount >= maxHealth):
        return
    canvas.itemconfig(healthPoints[healthAmount], fill="#ff3333", outline="#bb0000")
    healthAmount += 1

gunAngle = 0
gunPoints = None

# The gun point data. Angles and distances for getGunPoints()
gunPointAngles = [
    math.atan2(-5, PLAYER_RADIUS_SIZE + 5),
    math.atan2(-5, PLAYER_RADIUS_SIZE + 20),
    math.atan2(5, PLAYER_RADIUS_SIZE + 20),
    math.atan2(5, PLAYER_RADIUS_SIZE + 5)
]
gunPointDistances = [
    math.sqrt(math.pow(-5, 2) + math.pow(PLAYER_RADIUS_SIZE + 5, 2)),
    math.sqrt(math.pow(-5, 2) + math.pow(PLAYER_RADIUS_SIZE + 20, 2)),
    math.sqrt(math.pow(5, 2) + math.pow(PLAYER_RADIUS_SIZE + 20, 2)),
    math.sqrt(math.pow(5, 2) + math.pow(PLAYER_RADIUS_SIZE + 5, 2))
]

# Gets 4 points for the gun polygon from gunAngle and playerPosition
def getGunPoints():
    return [
        playerPosition["x"] + math.cos(gunPointAngles[0] + gunAngle) * gunPointDistances[0],
        playerPosition["y"] + math.sin(gunPointAngles[0] + gunAngle) * gunPointDistances[0],

        playerPosition["x"] + math.cos(gunPointAngles[1] + gunAngle) * gunPointDistances[1],
        playerPosition["y"] + math.sin(gunPointAngles[1] + gunAngle) * gunPointDistances[1],

        playerPosition["x"] + math.cos(gunPointAngles[2] + gunAngle) * gunPointDistances[2],
        playerPosition["y"] + math.sin(gunPointAngles[2] + gunAngle) * gunPointDistances[2],

        playerPosition["x"] + math.cos(gunPointAngles[3] + gunAngle) * gunPointDistances[3],
        playerPosition["y"] + math.sin(gunPointAngles[3] + gunAngle) * gunPointDistances[3]
    ]

gunPoints = getGunPoints()

# Gun shape. A polygon, since rectangles can't be rotated otherwise.
gun = canvas.create_polygon(
    gunPoints,
    fill = "#444444",
    outline = "#000000",
    width = 3,
    tags = "playerGroup"
    )
    

projectiles = []
projectileDamage = 1
bulletRicochetAmount = 0
doPiercingRounds = False

timeBetweenEnemies = 2
timeSinceLastEnemy = 2
enemyPool = ["normal", "normal", "bruiser", "speedy"]

# enemy shape instance, position, velocity, health, type
enemies = []


# Max health, speed, radius, color, outlineColor, points/kill
ENEMY_TYPES = {
    "normal": [2, 250, 20, "#aa2222", "#550000", 1],
    "bruiser": [3, 150, 30, "#4222aa", "#260e76", 3],
    "speedy": [1, 400, 15, "#279466", "#1f6f6a", 2],
    "ranger": [1, 200, 17, "#D5D159", "#b66d3a", 3],
    "bullet": [1, 0, 3, "#E43232", "#411D1D", 0],
    "BOSS": [20, 150, 70, "#9622aa", "#55004E", 10]
}

# Boss enemy stuff
def createBossEnemy():
    BOSS_DATA = ENEMY_TYPES["BOSS"]
    enemy = canvas.create_oval(
        root.winfo_width() / 2 - BOSS_DATA[2],
        -100 - BOSS_DATA[2],
        root.winfo_width() / 2 + BOSS_DATA[2],
        -100 + BOSS_DATA[2],
        fill = BOSS_DATA[3],
        outline = BOSS_DATA[4],
        width = 6,
        tags = "enemy"
    )
    enemies.append({
        "instance": enemy,
        "position": {"x": root.winfo_width() / 2, "y": -100},
        "velocity": {"x": 0, "y": 0},
        "health": BOSS_DATA[0],
        "type": "BOSS",
        "dashCooldown": 1
    })

def handleBossSpecialBehavior(enemy, dt):
    enemy["dashCooldown"] -= dt
    if(enemy["dashCooldown"] <= 0.5):
        enemy["velocity"] = {
            "x": 0,
            "y": 0
        }
    if(enemy["dashCooldown"] <= 0):
        enemy["dashCooldown"] += 3
        playerAngle = math.atan2(playerPosition["y"] - enemy["position"]["y"], playerPosition["x"] - enemy["position"]["x"])
        moveTowardsPlayerVelocity = {
            "x": math.cos(playerAngle) * 1000,
            "y": math.sin(playerAngle) * 1000
        }
        enemy["velocity"]["x"] += moveTowardsPlayerVelocity["x"]
        enemy["velocity"]["y"] += moveTowardsPlayerVelocity["y"]

def handleRangerBulletBehavior(bullet, dt):
    bullet["position"]["x"] += math.cos(bullet["angle"]) * 600 * dt
    bullet["position"]["y"] += math.sin(bullet["angle"]) * 600 * dt

def createRangerBullet(pos):
    BULLET_DATA = ENEMY_TYPES["bullet"]
    bullet = canvas.create_oval(
        root.winfo_width() / 2 - BULLET_DATA[2],
        -100 - BULLET_DATA[2],
        root.winfo_width() / 2 + BULLET_DATA[2],
        -100 + BULLET_DATA[2],
        fill = BULLET_DATA[3],
        outline = BULLET_DATA[4],
        width = 6,
        tags = "enemy"
    )

    angle = math.atan2(playerPosition["y"] - pos["y"], playerPosition["x"] - pos["x"])

    enemies.append({
        "instance": bullet,
        "position": pos,
        "velocity": {"x": math.cos(angle), "y": math.sin(angle)},
        "angle": angle,
        "health": BULLET_DATA[0],
        "type": "bullet"
    })

def handleRangerSpecialBehavior(enemy, dt):
    if(not "shotCooldown" in enemy):
        enemy["shotCooldown"] = 5.0
    enemy["shotCooldown"] -= dt

    if(enemy["shotCooldown"] <= 0.0):
        enemy["shotCooldown"] = 5.0
        createRangerBullet({"x": enemy["position"]["x"], "y": enemy["position"]["y"]})

    

# Activation functions for the pos / neg effects
def bulletHeckActivate():
    global projectilesPerShot, projectileSpread
    projectilesPerShot += 1
    projectileSpread += 0.05

def piercingRoundsActivate():
    global doPiercingRounds
    doPiercingRounds = True
    
def highCaliberActivate():
    global projectileDamage
    projectileDamage += 1

def bandageActivate():
    increasePlayerHealth()

def ammoBoxActivate():
    global PLAYER_MAX_AMMO
    PLAYER_MAX_AMMO += 1

def ricochetBulletsActivate():
    global bulletRicochetAmount
    bulletRicochetAmount += 3

def onQuickloaderActivate():
    global PLAYER_RELOAD_TIME
    PLAYER_RELOAD_TIME *= 0.8


def reinforcementsActivate():
    global timeBetweenEnemies
    timeBetweenEnemies *= 0.8

def cardioActivate():
    global ENEMY_TYPES
    ENEMY_TYPES["normal"][1] += 25
    ENEMY_TYPES["speedy"][1] += 30
    ENEMY_TYPES["bruiser"][1] += 25

def myopiaActivate():
    global projectileSpread
    projectileSpread += 0.1

def steelskinActivate():
    global ENEMY_TYPES
    ENEMY_TYPES["normal"][0] += 1
    ENEMY_TYPES["bruiser"][0] += 2
    ENEMY_TYPES["speedy"][0] += 1

electricFenceActive = False
def electricFenceActivate():
    global electricFenceActive
    electricFenceActive = True

misfireChance = 0.0
def misfireActivate():
    global misfireChance
    misfireChance += 0.03

critChance = 0.0
critMultiplier = 2.0
critAdditive = 0.0

def shatterboltActivate():
    global critChance
    critChance += 0.1

momentumActive = False
def momentumActivate():
    global momentumActive
    momentumActive = True

def superheatedActivate():
    global critMultiplier
    critMultiplier += 0.5

def keenEyeActivate():
    global critMultiplier
    critMultiplier += 0.5

def heatHazeActivate():
    global enemyPool
    enemyPool.append("bruiser")
    enemyPool.append("speedy")
    enemyPool.append("bruiser")
    enemyPool.append("speedy")
    enemyPool.append("normal")
    enemyPool.append("ranger")


gunKnockback = 500
def rocketPropulsionActivate():
    global gunKnockback
    gunKnockback += 50

# Positive / Negative effects on level up
# Each is an array of arrays. Each index is a level of effect.
# The higher the level, the stronger the positive / negative effect.
# Higher level effects are rarer.
EFFECT_LEVELS = 1
usedEffects = []
positiveLevelEffects = [
    [ # lv. 1 effects
        {
            "name": "Bullet Heck",
            "description": "+1 bullets per shot",
            "onActivate": bulletHeckActivate
        },
        {
            "name": "Bandage",
            "description": "Restore +1 health",
            "onActivate": bandageActivate
        }
    ],
    [ # lv. 2 effects
        {
            "name": "Piercing Rounds",
            "description": "Bullets that kill enemies don't get destroyed.",
            "onActivate": piercingRoundsActivate
        },
        {
            "name": "High Caliber",
            "description": "Bullets deal more damage.",
            "onActivate": highCaliberActivate
        },
        {
            "name": "Ammo Box",
            "description": "Can hold more ammo.",
            "onActivate": ammoBoxActivate
        },
        {
            "name": "Quickloader",
            "description": "Lower reload time.",
            "onActivate": onQuickloaderActivate
        },
        {
            "name": "Superheated",
            "description": "Critical hits deal more damage",
            "onActivate": superheatedActivate,
            "prerequisite": "Shatterbolt"
        },
        {
            "name": "Keen Eye",
            "description": "Critical hits are more likely",
            "onActivate": keenEyeActivate,
            "prerequisite": "Shatterbolt"
        }
    ],
    [ # lv. 3 effects
        {
            "name": "Ricochet Bullets",
            "description": "+3 bullet screen bounces",
            "onActivate": ricochetBulletsActivate
        },
        {
            "name": "Shatterbolt",
            "description": "Bullets have a chance to do critical hits",
            "onActivate": shatterboltActivate,
            "antiprerequisite": "Shatterbolt"
        },
        {
            "name": "Momentum",
            "description": "Every consecutive critical hit increases damage while the streak lasts",
            "onActivate": momentumActivate,
            "prerequisite": "Shatterbolt",
            "antiprerequisite": "Momentum"
        }
    ]
]
negativeLevelEffects = [
    [ # lv. 1 effects
        {
            "name": "Reinforcements",
            "description": "Enemies spawn faster",
            "onActivate": reinforcementsActivate
        },
        {
            "name": "Cardio",
            "description": "Enemies move faster",
            "onActivate": cardioActivate
        }
    ],
    [ # lv. 2 effects
        {
            "name": "Myopia",
            "description": "Bullets become less accurate",
            "onActivate": myopiaActivate
        },
        {
            "name": "Steelskin",
            "description": "Enemies gain more health",
            "onActivate": steelskinActivate
        },
        {
            "name": "Rocket Propulsion",
            "description": "Increased gun recoil. This seems like a bad idea.",
            "onActivate": rocketPropulsionActivate
        }
    ],
    [ # lv. 3 effects
        {
            "name": "Electric Fence",
            "description": "The edge of the screen is damaging",
            "onActivate": electricFenceActivate
        },
        {
            "name": "Misfire",
            "description": "Every time you fire, there's a small chance for the gun to jam and eject all your ammo.",
            "onActivate": misfireActivate
        },
        {
            "name": "Heat Haze",
            "description": "Rarer enemies join the field.",
            "onActivate": heatHazeActivate
        }
    ]
]

cardRarities = [
    {
        "bkColor": "#444444",
        "weight": 10
    },
    {
        "bkColor": "#444488",
        "weight": 6
    },
    {
        "bkColor": "#346834",
        "weight": 4
    },
    {
        "bkColor": "#733A73",
        "weight": 2
    },
    {
        "bkColor": "#663232",
        "weight": 1
    }
]



def pickRandomEffects():
    WEIGHTS = [0,0,0,1,1,2]
    level = random.choice(WEIGHTS)

    randomPosEffect = random.choice(positiveLevelEffects[level])
    while(("prerequisite" in randomPosEffect and not randomPosEffect["prerequisite"] in usedEffects) or ("antiprerequisite" in randomPosEffect and randomPosEffect["antiprerequisite"] in usedEffects)):
        randomPosEffect = random.choice(positiveLevelEffects[level])

    randomNegEffect = random.choice(negativeLevelEffects[level])
    while(("prerequisite" in randomNegEffect and not randomNegEffect["prerequisite"] in usedEffects) or ("antiprerequisite" in randomNegEffect and randomNegEffect["antiprerequisite"] in usedEffects)):
        randomNegEffect = random.choice(negativeLevelEffects[level])
    
    return [randomPosEffect, randomNegEffect, cardRarities[level]]

def createEffectSelections():
    windowWidth = root.winfo_width()
    windowHeight = root.winfo_height()
    # Cards should take 70% of the screen, with 5% padding between each
    effect1 = pickRandomEffects()
    leftCardMargin = tkinter.Frame(root, bg=effect1[2]["bkColor"], padx=10, pady=10)
    leftCardMargin.place(relx = 0.25, rely = 0.5, anchor="center")
    leftCardPos = tkinter.LabelFrame(leftCardMargin, text=effect1[0]["name"], bg="#111111", fg="#eeeeee", highlightcolor="#111111", highlightbackground="#111111", width=windowWidth * 0.2, height = windowHeight * 0.4, font=("sans-serif", 22))
    leftCardPos.pack_propagate(False)
    leftCardPos.pack()
    leftCardPosTitle = tkinter.Label(leftCardPos, text=effect1[0]["description"], font=("sans-serif", 18), wraplength=windowWidth * 0.19, justify="left")
    leftCardPosTitle.pack()

    leftCardNeg = tkinter.LabelFrame(leftCardMargin, text=effect1[1]["name"], bg="#111111", fg="#eeeeee", highlightcolor="#111111", highlightbackground="#111111", width=windowWidth * 0.2, height = windowHeight * 0.4, font=("sans-serif", 22))
    leftCardNeg.pack_propagate(False)
    leftCardNeg.pack()
    leftCardNegTitle = tkinter.Label(leftCardNeg, text=effect1[1]["description"], font=("sans-serif", 18), wraplength=windowWidth * 0.19, justify="left")
    leftCardNegTitle.pack()

    def onLeftFrameClick(_position):
        global pauseRenderLoop, lastTime, usedEffects
        usedEffects.append(effect1[0]["name"])
        usedEffects.append(effect1[1]["name"])
        leftCardMargin.destroy()
        middleCardMargin.destroy()
        rightCardMargin.destroy()
        effect1[0]["onActivate"]()
        effect1[1]["onActivate"]()
        pauseRenderLoop = False
        lastTime = time.time()
        root.after(16, renderLoop)
    
    leftCardMargin.bind("<Button-1>", onLeftFrameClick)
    leftCardPos.bind("<Button-1>", onLeftFrameClick)
    leftCardNeg.bind("<Button-1>", onLeftFrameClick)
    leftCardPosTitle.bind("<Button-1>", onLeftFrameClick)
    leftCardNegTitle.bind("<Button-1>", onLeftFrameClick)

    effect2 = pickRandomEffects()
    middleCardMargin = tkinter.Frame(root, bg=effect2[2]["bkColor"], padx=10, pady=10)
    middleCardMargin.place(relx = 0.5, rely = 0.5, anchor="center")
    middleCardPos = tkinter.LabelFrame(middleCardMargin, text=effect2[0]["name"], bg="#111111", fg="#eeeeee", highlightcolor="#111111", highlightbackground="#111111", width=windowWidth * 0.2, height = windowHeight * 0.4, font=("sans-serif", 22))
    middleCardPos.pack_propagate(False)
    middleCardPos.pack()
    middleCardPosTitle = tkinter.Label(middleCardPos, text=effect2[0]["description"], font=("sans-serif", 18), wraplength=windowWidth * 0.19, justify="left")
    middleCardPosTitle.pack()

    middleCardNeg = tkinter.LabelFrame(middleCardMargin, text=effect2[1]["name"], bg="#111111", fg="#eeeeee", highlightcolor="#111111", highlightbackground="#111111", width=windowWidth * 0.2, height = windowHeight * 0.4, font=("sans-serif", 22))
    middleCardNeg.pack_propagate(False)
    middleCardNeg.pack()
    middleCardNegTitle = tkinter.Label(middleCardNeg, text=effect2[1]["description"], font=("sans-serif", 18), wraplength=windowWidth * 0.19, justify="left")
    middleCardNegTitle.pack()

    def onMiddleFrameClick(_position):
        global pauseRenderLoop, lastTime, usedEffects
        usedEffects.append(effect2[0]["name"])
        usedEffects.append(effect2[1]["name"])
        leftCardMargin.destroy()
        middleCardMargin.destroy()
        rightCardMargin.destroy()
        effect2[0]["onActivate"]()
        effect2[1]["onActivate"]()
        pauseRenderLoop = False
        lastTime = time.time()
        root.after(16, renderLoop)
    
    middleCardMargin.bind("<Button-1>", onMiddleFrameClick)
    middleCardPos.bind("<Button-1>", onMiddleFrameClick)
    middleCardNeg.bind("<Button-1>", onMiddleFrameClick)
    middleCardPosTitle.bind("<Button-1>", onMiddleFrameClick)
    middleCardNegTitle.bind("<Button-1>", onMiddleFrameClick)

    effect3 = pickRandomEffects()
    rightCardMargin = tkinter.Frame(root, bg=effect3[2]["bkColor"], padx=10, pady=10)
    rightCardMargin.place(relx = 0.75, rely = 0.5, anchor="center")
    rightCardPos = tkinter.LabelFrame(rightCardMargin, text=effect3[0]["name"], bg="#111111", fg="#eeeeee", highlightcolor="#111111", highlightbackground="#111111", width=windowWidth * 0.2, height = windowHeight * 0.4, font=("sans-serif", 22))
    rightCardPos.pack_propagate(False)
    rightCardPos.pack()
    rightCardPosTitle = tkinter.Label(rightCardPos, text=effect3[0]["description"], font=("sans-serif", 18), wraplength=windowWidth * 0.19, justify="left")
    rightCardPosTitle.pack()

    rightCardNeg = tkinter.LabelFrame(rightCardMargin, text=effect3[1]["name"], bg="#111111", fg="#eeeeee", highlightcolor="#111111", highlightbackground="#111111", width=windowWidth * 0.2, height = windowHeight * 0.4, font=("sans-serif", 22))
    rightCardNeg.pack_propagate(False)
    rightCardNeg.pack()
    rightCardNegTitle = tkinter.Label(rightCardNeg, text=effect3[1]["description"], font=("sans-serif", 18), wraplength=windowWidth * 0.19, justify="left")
    rightCardNegTitle.pack()
    def onRightFrameClick(_position):
        global pauseRenderLoop, lastTime, usedEffects
        usedEffects.append(effect3[0]["name"])
        usedEffects.append(effect3[1]["name"])
        leftCardMargin.destroy()
        middleCardMargin.destroy()
        rightCardMargin.destroy()
        effect3[0]["onActivate"]()
        effect3[1]["onActivate"]()
        pauseRenderLoop = False
        lastTime = time.time()
        root.after(16, renderLoop)

    
    rightCardMargin.bind("<Button-1>", onRightFrameClick)
    rightCardPos.bind("<Button-1>", onRightFrameClick)
    rightCardNeg.bind("<Button-1>", onRightFrameClick)
    rightCardPosTitle.bind("<Button-1>", onRightFrameClick)
    rightCardNegTitle.bind("<Button-1>", onRightFrameClick)

def triggerPickEffect():
    global pauseRenderLoop
    pauseRenderLoop = True
    createEffectSelections()

def createEnemy(type, position):
    if not type in ENEMY_TYPES:
        print("Invalid enemy type: ", type)
        return
    enemy = canvas.create_oval(
        position["x"] - ENEMY_TYPES[type][2],
        position["y"] - ENEMY_TYPES[type][2],
        position["x"] + ENEMY_TYPES[type][2],
        position["y"] + ENEMY_TYPES[type][2],
        fill = ENEMY_TYPES[type][3],
        outline = ENEMY_TYPES[type][4],
        width = 6,
        tags = "enemy"
    )
    enemies.append({
        "instance": enemy,
        "position": position,
        "velocity": {"x": 0, "y": 0},
        "health": ENEMY_TYPES[type][0],
        "type": type
    })

def doBulletCritEffects(pos):
    createParticleBurst(
        random.randint(3,7),
        {
            "x": pos["x"],
            "y": pos["y"]
        },
        "#ffe41a",
        0,
        math.tau, 5, 4, 0.2)
    createParticleBurst(
        random.randint(3,7),
        {
            "x": pos["x"],
            "y": pos["y"]
        },
        "#0f0f0f",
        0,
        math.tau, 5, 4, 0.2)

def handleBulletCollision(projectileIndex):
    global points, nextPointLevel, level, critAdditive
    projectile = projectiles[projectileIndex]
    i = 0
    while i < len(enemies):
        enemy = enemies[i]
        # Using the pythagorean theorem to determine if enemies are colliding.
        # Just assume the radius of bullets are 0 to simplify collision calculations.
        enemyRadius = ENEMY_TYPES[enemy["type"]][2]
        distance = math.sqrt(math.pow(enemy["position"]["x"] - projectile[1]["x"], 2) + math.pow(enemy["position"]["y"] - projectile[1]["y"], 2))
        if(distance <= enemyRadius):
            playerHitSound.play().set_volume(random.random() + 5.0)
            # Collide!
            dmg = projectileDamage
            if(random.random() < critChance):
                dmg *= critMultiplier + critAdditive
                if(momentumActive):
                    critAdditive += 0.1
                doBulletCritEffects(projectile[1])
            else:
                critAdditive = 0

            
            enemy["health"] -= dmg
            if(enemy["health"] <= 0):
                # dead enemy
                points += ENEMY_TYPES[enemy["type"]][5]
                if(points >= nextPointLevel):
                    nextPointLevel += 10 + level * 2
                    level += 1
                    triggerPickEffect()
                    if(level % 10 == 0):
                        createBossEnemy()
                
                pointsLabel.config(text=f"{points:04d}")
                canvas.delete(enemy["instance"])

                createParticleBurst(random.randint(10, 15), enemy["position"], ENEMY_TYPES[enemy["type"]][4], 0, math.tau, 4, 3, 0.15)

                enemies.pop(i)

                if(not doPiercingRounds):
                    canvas.delete(projectile[0])
                    if(projectileIndex < len(projectiles)):
                        projectiles.pop(projectileIndex)
            else:
                # Knock back enemy
                enemy["velocity"]["x"] += projectile[2]["x"] * 4
                enemy["velocity"]["y"] += projectile[2]["y"] * 4
                i += 1
                canvas.delete(projectile[0])
                if(projectileIndex < len(projectiles)):
                    projectiles.pop(projectileIndex)
        else:
            i += 1

def handlePlayerEnemyCollision(enemy):
    minDistanceToCollide = PLAYER_RADIUS_SIZE + ENEMY_TYPES[enemy["type"]][2]
    distance = math.sqrt(math.pow(enemy["position"]["x"] - playerPosition["x"], 2) + math.pow(enemy["position"]["y"] - playerPosition["y"], 2))
    if(distance < minDistanceToCollide):
        decreasePlayerHealth()
        playerVelocity["x"] += math.cos(math.atan2(playerPosition["y"] - enemy["position"]["y"], playerPosition["x"] - enemy["position"]["x"])) * 500
        playerVelocity["y"] += math.sin(math.atan2(playerPosition["y"] - enemy["position"]["y"], playerPosition["x"] - enemy["position"]["x"])) * 500
        if(enemy["type"] == "bullet"):
            canvas.delete(enemy["instance"])
            createParticleBurst(random.randint(10, 15), enemy["position"], ENEMY_TYPES[enemy["type"]][4], 0, math.tau, 4, 3, 0.15)
            enemies.pop(enemies.index(enemy))

def moveCenterTo(itemID, targetCX, targetCY):
    percentage = 1 - playerAmmo / PLAYER_MAX_AMMO
    topLeftXOffset = -math.cos(min(max(percentage, 0.25), 0.5) * 2 * math.pi) * PLAYER_RADIUS_SIZE + 6
    topLeftYOffset = math.sin(min(0.25, percentage) * 2 * math.pi) * PLAYER_RADIUS_SIZE + 6
    
    canvas.moveto(itemID, round(targetCX - topLeftXOffset), round(targetCY - topLeftYOffset))

particles = []
def createParticle(position, color, velocity, lifetime):
    randSize = random.randint(1, 3)
    particleInstance = canvas.create_rectangle(
        position["x"] - randSize,
        position["y"] - randSize,
        position["x"] + randSize,
        position["y"] + randSize,
        fill = color,
        outline = ""
    )
    particles.append({
        "instance": particleInstance,
        "velocity": velocity,
        "remainingLifetime": lifetime
    })

def createParticleBurst(amount, position, color, angle, spread, strength, strengthSpread, lifetime):
    for i in range(amount):
        angle = random.uniform(angle - spread, angle + spread)
        strength = random.uniform(strength - strengthSpread, strength + strengthSpread)
        velocity = {
            "x": math.cos(angle) * strength,
            "y": math.sin(angle) * strength
        }
        createParticle(position, color, velocity, lifetime)


currentReloadTime = 0
inReloadState = False

pauseRenderLoop = False
# Used to calculate dt
lastTime = time.time()
# Main rendering loop! All frame-by-frame calculations go here, like movement.
def renderLoop():
    global lastTime, timeSinceLastEnemy, inReloadState, playerAmmo, currentReloadTime

    windowWidth = root.winfo_width()
    windowHeight = root.winfo_height()
    
    # 1. Calculate delta time (time elapsed in seconds since the last frame)
    # Delta (dt) is useful to make sure that things like movement are consistent across machines.
    # Regardless of the speed of machine (ex. a slower machine where frames take longer), the output
    # should be generally the same.
    currentTime = time.time()
    dt = currentTime - lastTime
    lastTime = currentTime

    if(inReloadState):
        canvas.itemconfigure(playerEmptyAmmoSlice, fill="#4444aa")
        currentReloadTime = max(0, currentReloadTime - dt)
        if(currentReloadTime == 0):
            inReloadState = False
            playerAmmo = PLAYER_MAX_AMMO
            canvas.itemconfigure(playerEmptyAmmoSlice, fill="#575757")

    # Updating the player and polygon positions by base player velocity
    playerPosition["x"] += playerVelocity["x"] * dt
    playerPosition["y"] += playerVelocity["y"] * dt
    canvas.moveto(player, playerPosition["x"] - PLAYER_RADIUS_SIZE - 3, playerPosition["y"] - PLAYER_RADIUS_SIZE - 3)
    canvas.itemconfigure(playerEmptyAmmoSlice, extent = min((1 - playerAmmo / PLAYER_MAX_AMMO) * 360, 359.9))
    moveCenterTo(playerEmptyAmmoSlice, playerPosition["x"] + 1, playerPosition["y"] + 1)

    # Constraining player positions to the screen bounds.
    if(playerPosition["x"] < 0):
        playerPosition["x"] = 0
        playerVelocity["x"] *= -1
        print(electricFenceActive)
        if(electricFenceActive): decreasePlayerHealth()
    if(playerPosition["y"] < 0):
        playerPosition["y"] = 0
        playerVelocity["y"] *= -1
        if(electricFenceActive): decreasePlayerHealth()
    if(playerPosition["x"] > windowWidth):
        playerPosition["x"] = windowWidth
        playerVelocity["x"] *= -1
        if(electricFenceActive): decreasePlayerHealth()
    if(playerPosition["y"] > windowHeight):
        playerPosition["y"] = windowHeight
        playerVelocity["y"] *= -1
        if(electricFenceActive): decreasePlayerHealth()

    # Updating projectile positions and culling if out of bounds
    i = 0
    while(i < len(projectiles)):
        proj = projectiles[i]
        canvas.move(proj[0], proj[2]["x"], proj[2]["y"])
        proj[1]["x"] += proj[2]["x"]
        proj[1]["y"] += proj[2]["y"]
        if(proj[1]["x"] < 0 or proj[1]["x"] > windowWidth or proj[1]["y"] < 0 or proj[1]["y"] > windowHeight):
            if(proj[3] < bulletRicochetAmount):
                proj[3] += 1
                if(proj[1]["x"] < 0):
                    proj[1]["x"] = 0
                    proj[2]["x"] *= -1
                elif(proj[1]["x"] > windowWidth):
                    proj[1]["x"] = windowWidth
                    proj[2]["x"] *= -1
                
                if(proj[1]["y"] < 0):
                    proj[1]["y"] = 0
                    proj[2]["y"] *= -1
                elif(proj[1]["y"] > windowHeight):
                    proj[1]["y"] = windowHeight
                    proj[2]["y"] *= -1
            else:
                canvas.delete(proj[0])
                projectiles.pop(i)
        else: # Determine if colliding with any enemy. If so, decrease health by 1 and handle knockback.
            handleBulletCollision(i)
            i += 1

    # Updating the polygon points with (gasp) trigonometry to point towards the mouse
    gunPoints = getGunPoints()
    canvas.coords(gun, *gunPoints)

    # Player velocity decays by 0.6 per frame
    playerVelocity["x"] = playerVelocity["x"] * math.pow(0.01, dt)
    playerVelocity["y"] = playerVelocity["y"] * math.pow(0.01, dt)
    if(abs(playerVelocity["x"]) < 1): 
        playerVelocity["x"] = 0
        playerPosition["x"] = round(playerPosition["x"])
    if(abs(playerVelocity["y"]) < 1):
        playerVelocity["y"] = 0
        playerPosition["y"] = round(playerPosition["y"])


    # handling enemy codes
    timeSinceLastEnemy -= dt
    if(timeSinceLastEnemy < 0):
        # Creating an enemy from enemyPool every timeBetweenEnemies seconds.
        timeSinceLastEnemy += timeBetweenEnemies
        randomRadius = random.randint(700, 800)
        randomAngle = random.uniform(0, 2 * math.pi)
        createEnemy(
            random.choice(enemyPool),
            {
                "x": root.winfo_width() * 0.5 + (math.cos(randomAngle) * randomRadius),
                "y": root.winfo_height() * 0.5 + (math.sin(randomAngle) * randomRadius)
            }
        )

    # Move enemies towards player depending on their speed.
    for enemy in enemies:
        playerAngle = math.atan2(playerPosition["y"] - enemy["position"]["y"], playerPosition["x"] - enemy["position"]["x"])
        moveTowardsPlayerVelocity = {
            "x": math.cos(playerAngle) * ENEMY_TYPES[enemy["type"]][1],
            "y": math.sin(playerAngle) * ENEMY_TYPES[enemy["type"]][1]
        }
        enemy["velocity"]["x"] += moveTowardsPlayerVelocity["x"] * dt
        enemy["velocity"]["y"] += moveTowardsPlayerVelocity["y"] * dt
        enemy["position"]["x"] += enemy["velocity"]["x"] * dt
        enemy["position"]["y"] += enemy["velocity"]["y"] * dt
        canvas.moveto(
            enemy["instance"],
            enemy["position"]["x"] - ENEMY_TYPES[enemy["type"]][2] - 3,
            enemy["position"]["y"] - ENEMY_TYPES[enemy["type"]][2] - 6
        )
        handlePlayerEnemyCollision(enemy)
        enemy["velocity"]["x"] *= pow(0.01, dt)
        enemy["velocity"]["y"] *= pow(0.01, dt)

        if(enemy["type"] == "BOSS"):
            handleBossSpecialBehavior(enemy, dt)
        elif(enemy["type"] == "bullet"):
            handleRangerBulletBehavior(enemy, dt)
        elif(enemy["type"] == "ranger"):
            handleRangerSpecialBehavior(enemy, dt)

    i = 0
    while(i < len(particles)):
        particles[i]["remainingLifetime"] -= dt
        canvas.move(particles[i]["instance"], particles[i]["velocity"]["x"], particles[i]["velocity"]["y"])
        particles[i]["velocity"]["x"] *= 0.9
        particles[i]["velocity"]["y"] *= 0.9
        if(particles[i]["remainingLifetime"] <= 0):
            canvas.delete(particles[i]["instance"])
            particles.pop(i)
            i -= 1
        i += 1
    canvas.update_idletasks()

    if(not pauseRenderLoop):
        root.after(10, renderLoop)

def createProjectile(position, velocity):
    projectile = canvas.create_oval(
        position["x"] - 5,
        position["y"] - 5,
        position["x"] + 5,
        position["y"] + 5,
        fill = "#352461"
    )
    projectiles.append(
        [projectile, position, velocity, 0]
    )

# Firing function
def doFire():
    global playerAmmo
    if(playerAmmo > 0):
        gunSound.play().set_volume(random.random() * 0.5 + 0.5)
        playerVelocity["x"] -= math.cos(gunAngle) * gunKnockback
        playerVelocity["y"] -= math.sin(gunAngle) * gunKnockback
        for i in range(projectilesPerShot):
            angleOffset = random.uniform(-projectileSpread / 2, projectileSpread / 2)
            createProjectile(
                {
                    "x": playerPosition["x"] + math.cos(gunAngle) * 30,
                    "y": playerPosition["y"] + math.sin(gunAngle) * 30
                },
                {
                    "x": math.cos(gunAngle + angleOffset) * 20,
                    "y": math.sin(gunAngle + angleOffset) * 20
                }
            )
        
            createParticleBurst(
                random.randint(3,7),
                {
                    "x": playerPosition["x"] + math.cos(gunAngle) * 30,
                    "y": playerPosition["y"] + math.sin(gunAngle) * 30
                },
                "#b93e29",
                math.atan2(math.sin(gunAngle + angleOffset), math.cos(gunAngle + angleOffset)),
                0.25, 5, 4, 0.2)
            createParticleBurst(
                random.randint(3,7),
                {
                    "x": playerPosition["x"] + math.cos(gunAngle) * 30,
                    "y": playerPosition["y"] + math.sin(gunAngle) * 30
                },
                "#dd802f",
                math.atan2(math.sin(gunAngle + angleOffset), math.cos(gunAngle + angleOffset)),
                0.25, 5, 4, 0.2)
        playerAmmo -= 1


# Keypress handler
def handleKeypress(ev):
    global playerAmmo, inReloadState, currentReloadTime
    if(ev.keysym == "z"): # Firing
        doFire()
        if(random.random() < misfireChance):
            playerAmmo = 0
    if(ev.keysym == "x" and not inReloadState):
        inReloadState = True
        currentReloadTime = PLAYER_RELOAD_TIME
        playerAmmo = 0

# Stored mouse position.
mousePosition = {"x": 0, "y": 0}
def handleMousemove(ev):
    # Assigns mousePosition to the mouse position and getting the angle relative to player
    global gunAngle
    mousePosition["x"] = ev.x
    mousePosition["y"] = ev.y
    gunAngle = math.atan2(
        mousePosition["y"] - playerPosition["y"],
        mousePosition["x"] - playerPosition["x"]
    )

# Assigning binds to key and mousemove
root.bind("<Key>", handleKeypress)
root.bind("<Motion>", handleMousemove)

# Starting the render loop
root.after(16, renderLoop)
root.mainloop()