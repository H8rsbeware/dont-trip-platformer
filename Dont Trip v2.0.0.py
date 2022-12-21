import sys
import random
import time
import pygame
import pygame.sprite
from pygame.locals import *


FPS = 30

WINHEIGHT = 840
WINWIDTH = 480
MIDDLE = WINWIDTH / 2

STARTPOS = {'x':260, 'y':780}
CHARSIZE = 64,64
ACC = 0.8
FRIC = -0.12
HIGHJUMP = 18
SMALLJUMP = 8


WHITE = (255,255,255)
BLACK = (  0,  0,  0)
LGREY = (191,189,184)
DGREY = ( 48, 48, 48)

TITLEGRAVITY = 50
DEADZONE = 11
DEGREE = 0.5

DEBUG = False
vec = pygame.math.Vector2

PLATTYPE = ['Break', 'Standard', 'Move', 'Raise']
WALKCYCLE = ['Images/left1.png', 'Images/left3.png', 'Images/left1.png', 'Images/left2.png']
STARTCOUNT = 0

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.pos = vec((STARTPOS['x'], STARTPOS['y']))
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.walk = False
        self.jump = False
        self.last_update = 0
        self.last_direction = "Left"
        self.index = 0
        self.load()
        self.animation()
        self.score = 0

        self.image = self.right_walk[self.index]
        print(f"Start Image = {self.image}.")
        self.surf = self.image
        self.rect = self.surf.get_rect()

        #self.redraw = False

    def load(self):
        self.left_walk = []
        self.right_walk = []
        self.right_walk.append(pygame.transform.scale(pygame.transform.flip(pygame.image.load('Images/left1.png'), True, False), CHARSIZE))
        self.right_walk.append(pygame.transform.scale(pygame.transform.flip(pygame.image.load('Images/left3.png'), True, False), CHARSIZE))
        self.right_walk.append(pygame.transform.scale(pygame.transform.flip(pygame.image.load('Images/left1.png'), True, False), CHARSIZE))
        self.right_walk.append(pygame.transform.scale(pygame.transform.flip(pygame.image.load('Images/left2.png'), True, False), CHARSIZE))
        self.left_walk.append(pygame.transform.scale(pygame.image.load('Images/left1.png'), CHARSIZE))
        self.left_walk.append(pygame.transform.scale(pygame.image.load('Images/left3.png'), CHARSIZE))
        self.left_walk.append(pygame.transform.scale(pygame.image.load('Images/left1.png'), CHARSIZE))
        self.left_walk.append(pygame.transform.scale(pygame.image.load('Images/left2.png'), CHARSIZE))

    def move(self):
        self.acc = vec(0,0.5)
        keypress = pygame.key.get_pressed()

        if keypress[K_LEFT] or keypress[K_a]:
            self.acc.x = -ACC
            self.last_direction = "Left"
        if keypress[K_RIGHT] or keypress[K_d]:
            self.acc.x= ACC
            self.last_direction = "Right"

        self.acc.x += self.vel.x * FRIC
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WINWIDTH + 24:
            self.pos.x = -24
        if self.pos.x < -24:
            self.pos.x = WINWIDTH + 24

        self.rect.midbottom = self.pos

    def jumpup(self):
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        if collisions and not self.jump:
            self.jump = True
            self.vel.y = -HIGHJUMP

    def cancel_jumpup(self):
        if self.jump:
            if self.vel.y < -SMALLJUMP:
                self.vel.y = -SMALLJUMP

    def update(self):
        self.animation()
        self.move()

        if 0 > P1.vel.x > -0.6:
            P1.vel.x = 0
        if 0 < P1.vel.x < 0.6:
            P1.vel.x = 0
        collisions = pygame.sprite.spritecollide(self, platforms, False)

        if P1.vel.y > 0:
            if collisions:
                if self.pos.y < collisions[0].rect.bottom:
                    if collisions[0].point:
                        collisions[0].point = False
                        self.score += 1
                    self.jump = False
                    self.pos.y = collisions[0].rect.top + 1
                    self.vel.y = 0

    def animation(self):
        now = pygame.time.get_ticks()
        #RIGHT
        if self.vel.x != 0:
            self.walk = True
        else:
            self.walk = False
        if DEBUG:
            print(self.walk, self.vel.x)
        if self.walk:

            if now - self.last_update > 100:
                self.last_update = now
                self.index = (self.index + 1) % len(self.left_walk)

                if self.vel.x > 0:

                    self.image = self.right_walk[self.index]
                else:

                    self.image = self.left_walk[self.index]
                self.surf = self.image
                self.rect = self.image.get_rect()
                self.rect.midbottom = self.pos

        if not self.walk:
            if now - self.last_update > 100:
                self.last_update = now
                if self.last_direction == "Right":
                    self.image = self.right_walk[0]
                else:
                    self.image = self.left_walk[0]
                self.surf = self.image
                self.rect = self.image.get_rect()
                self.rect.midbottom = self.pos
        self.mask = pygame.mask.from_surface(self.image)


class Platform(pygame.sprite.Sprite):
    def __init__(self): # x, y, px, py, type:str
        super().__init__()
        self.x = random.randint(64, WINWIDTH-64)
        self.y = random.randint(64, WINHEIGHT-32)
        self.surf = pygame.Surface((random.choice((96, 128)), 32))
        self.surf.fill(LGREY)
        self.rect = self.surf.get_rect(center=(self.x, self.y))
        self.moverange = 0
        self.movetype = None
        self.type = "Standard"
        self.time = 0
        #Scoring
        self.point = True

        randomNum = random.randint(0, 7)
        if randomNum == 7:
            self.type = "Move"
        elif randomNum == 6:
            self.type = "Break"

        if self.type == "Break":
            self.collapser = True
        else:
            self.collapser = False

        if self.type == "Move":
            self.movement = True
            self.calcMoverange()
        else:
            self.movement = False

    def move(self):
        if self.movetype == "Right":
            if self.x < self.moverange:
                self.x += 4
            else:
                self.moverange = self.x - random.randint(100, 200)
                self.movetype = "Left"
        elif self.movetype == "Left":
            if self.x> self.moverange:
                self.x -= 4
            else:
                self.moverange = self.x + random.randint(100, 200)
                self.movetype = "Right"
        self.rect.x = self.x

    def collapse(self):
        collisions = pygame.sprite.collide_rect(self, P1)
        self.surf.fill(DGREY)
        if collisions:
            movementPattern = ['ux', 'uy', 'dx', 'dy']
            if movementPattern[(self.time % len(movementPattern))] == 'ux':
                self.x += 1
            elif movementPattern[(self.time % len(movementPattern))] == 'uy':
                self.y += 1
                self.x -= 1
            elif movementPattern[(self.time % len(movementPattern))] == 'dx':
                self.x -= 1
                self.y -= 1
            elif movementPattern[(self.time % len(movementPattern))] == 'dy':
                self.x += 1
                self.y -= 1
            self.rect.x = self.x

            self.time += 1

            if self.time > 18:
                self.time = 0
                self.kill()
                
    def calcMoverange(self):
        if self.x > 240:
            self.moverange = self.x - 200
            self.movetype = "Left"
        else:
            self.moverange = self.x + 200
            self.movetype = "Right"

    def update(self):
        if self.movement:
            self.move()
        if self.collapser:
            self.collapse()

class Base(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('Images/base.png')
        self.surf = self.image
        self.rect = self.surf.get_rect(center=(MIDDLE, WINHEIGHT-10))
        self.point = 0


def main():
    global CLOCK, DISPLAY, FONT, LAV, RAV, inGameBG
    pygame.init()

    CLOCK = pygame.time.Clock()
    DISPLAY = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption("Don't Trip")
    FONT = pygame.font.Font('./Fonts/UbuntuMono-B.ttf', 32)

    pygame.mixer.music.load('Music/ExtraLoop.wav')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(loops=-1, start=0.0)

    showStartScreen()
    inGameBG = getBackground()

    while True:
        runGame()

def runGame():
    global P1, all_sprites, platforms

    #Class Declaration
    P1 = Player(STARTPOS['x'], STARTPOS['y'])
    Base1 = Base()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(Base1)
    all_sprites.add(P1)
    platforms = pygame.sprite.Group()
    platforms.add(Base1)

    #Init Generation
    for x in range(random.randint(5, 6)):
        pl = Platform()
        platforms.add(pl)
        all_sprites.add(pl)

    #Game loop
    while True:
        #Event Listener
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    P1.jumpup()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    P1.cancel_jumpup()

        DISPLAY.fill(inGameBG)
        platform_gen()

        #Score
        scoreFont = pygame.font.Font("Fonts/UbuntuMono-B.ttf", 35)
        scoreSurf = scoreFont.render(str(P1.score), True, (BLACK))


        #Sprite Updates
        for entity in all_sprites:
            if DEBUG:
                print(entity.surf, entity.rect)
            DISPLAY.blit(entity.surf, entity.rect)
            entity.update()

        #Screen Scroll
        if P1.rect.top <= WINHEIGHT / 3:
            P1.pos.y += abs(P1.vel.y)
            for platform in platforms:
                platform.rect.y += abs(P1.vel.y)
                if platform.rect.top >= WINHEIGHT:
                    platform.kill()

        #Death Check
        if P1.pos.y > WINHEIGHT + 96:
            for x in all_sprites:
                x.kill()
                time.sleep(1)
                showGameOver()

        DISPLAY.blit(scoreSurf, (WINWIDTH / 2, 20))
        pygame.display.update()
        CLOCK.tick(FPS)

#######

#Background Things
def ranRGB():
    return random.randint(100,200)

def getBackground():
    return (ranRGB(),ranRGB(),ranRGB())

#Termination
def terminate():
    pygame.quit()
    sys.exit()

#Event Checker
def checkEvents():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()
    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0] == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

#Platform Things
def platform_gen():
    while len(platforms) < 7:
        width = random.choice((96,128))
        p = Platform()
        C = True
        while C:
            p = Platform()
            p.rect.center = (random.randrange(64, WINWIDTH-64), random.randrange(-50, 0))
            C = check(p, platforms)
        platforms.add(p)
        all_sprites.add(p)

def check(platform, members):
    if pygame.sprite.spritecollideany(platform,members):
        return True
    else:
        for member in members:
            if member == platform:
                continue
            if (abs(platform.rect.top - member.rect.bottom) < 50 and (abs(platform.rect.bottom - member.rect.top) < 50)):
                return True
        C = False


#Over engineered start menu
def showStartScreen():
    titleFont = pygame.font.Font('Fonts/UbuntuMono-B.ttf', 50)
    titleSurf = titleFont.render("Don't Trip", True, BLACK)
    subtitleText = pygame.font.Font('Fonts/UbuntuMono-BI.ttf', 30)
    subtitleSurf = subtitleText.render("Press any key to start", True, DGREY)
    bgColour = (getBackground())
    x = 0
    y = 0
    degree = 0
    change = False
    while True:
        DISPLAY.fill(bgColour)
        fallRect = titleSurf.get_rect()
        fallRect.center = (MIDDLE, x)
        DISPLAY.blit(titleSurf, fallRect)
        if x >= 840:
            y += 1
            x = 0
        elif y == 2 and x == 350:
            if checkEvents():
                pygame.event.get()
                return
            if degree < DEADZONE and change is False:
                degree += DEGREE
            elif degree == DEADZONE and change is False:
                degree += -DEGREE
                change = True
            elif degree == -DEADZONE and change is True:
                degree += DEGREE
                change = False
            elif degree > -DEADZONE and change is True:
                degree += -DEGREE

            rotatedSubtitle = pygame.transform.rotate(subtitleSurf, degree)
            rotatedRect = rotatedSubtitle.get_rect()
            rotatedRect.center = (MIDDLE, 450)
            DISPLAY.blit(rotatedSubtitle, rotatedRect)
        else:
            x += TITLEGRAVITY
        pygame.display.update()
        CLOCK.tick(FPS)

def showGameOver():
    gameFont = pygame.font.Font('Fonts/UbuntuMono-B.ttf', 50)
    gameSurf = gameFont.render("You Tripped!", True, BLACK)
    gameRect = gameSurf.get_rect(center=(MIDDLE, 350))
    subgameText = pygame.font.Font('Fonts/UbuntuMono-BI.ttf', 30)
    subgameSurf = subgameText.render("Press any key to restart", True, DGREY)
    scoreText = pygame.font.Font('Fonts/UbuntuMono-R.ttf', 40)
    scoreSurf = scoreText.render(f"Score: {P1.score}", True, DGREY)
    scoreRect = scoreSurf.get_rect(center=(MIDDLE, 550))
    bgColour = (getBackground())

    degree = 0
    change = False

    while True:
        DISPLAY.fill(bgColour)
        DISPLAY.blit(gameSurf, gameRect)
        DISPLAY.blit(scoreSurf, scoreRect)

        if checkEvents():
            pygame.event.get()
            pygame.mixer.music.pause()
            pygame.mixer.music.unload()
            main()
            return
        if degree < DEADZONE and change is False:
            degree += DEGREE
        elif degree == DEADZONE and change is False:
            degree += -DEGREE
            change = True
        elif degree == -DEADZONE and change is True:
            degree += DEGREE
            change = False
        elif degree > -DEADZONE and change is True:
            degree += -DEGREE
        rotatedSubgame = pygame.transform.rotate(subgameSurf, degree)
        rotatedRect = rotatedSubgame.get_rect(center=(MIDDLE,450))
        DISPLAY.blit(rotatedSubgame, rotatedRect)

        pygame.display.update()
        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()