import pygame
import random #level selection
import time
import os

def loadImage(string, width, height):
    image = pygame.image.load(os.path.join("textures", string+".png"))
    image = pygame.transform.scale(image, (width, height))
    return image

def loadLevels():
    levelFile = open("levels.txt")
    level = []
    y=0
    for line in levelFile:
        if line == "\n":
            Game.levels.append(level)
            y=0
            level = []
        else:
            for x in range(len(line)):
                if line[x] == "N":
                    level.append(Block(x, y))
            y+=1
    levelFile.close()

def collides(self, other):
        r = self.__class__.radius + other.__class__.radius
        dx = self.x-other.x
        dy = self.y-other.y
        if abs(dx)<r and abs(dy)<r:
            return True
        else:
            return False

def darken(color):
    return (max(0,color[0]-50),max(0,color[1]-50),max(0,color[2]-50))

class Game():

    levels = []
    image = loadImage("background", 1280, 720)

    def __init__(self):
        self.characters = []
        self.blocks = random.choice(Game.levels)
        self.over = 0 #game.over

    def addCharacter(self, character):
        self.characters.insert(random.randint(0,len(self.characters)), character)

    def update(self):
        gameDisplay.blit(Game.image, (0, 0)) #some people draw in update :()
        pressed = pygame.key.get_pressed()
        for character in self.characters:
            character.update(pressed) #after proj move maybe?
            for projectile in character.projectiles:
                projectile.update()
        self.characters = [c for c in self.characters if c.hp>0]
        if len(self.characters)<=1:
            self.over += 2
        if pressed[pygame.K_r]:
            self.over+=11
        if self.over>0:
            self.over-=1

    def draw(self):
        for block in self.blocks:
            block.draw()
        for character in self.characters:
            character.draw() #after proj draw?
        for character in self.characters:
            for projectile in character.projectiles:
                projectile.draw()

class Block():

    radius = 40
    image = loadImage("block", radius*2, radius*2)

    def __init__(self, x, y):
        r=Block.radius
        self.x = x*2*r + r
        self.y = y*2*r + r

    def draw(self):
        r = Block.radius
        color = (100,100,100)
        gameDisplay.blit(Block.image, (self.x-r, self.y-r))
        #pygame.draw.rect(gameDisplay, color, (self.x-r, self.y-r, r*2, r*2), 0)

loadLevels()

class Character():

    movementSpeed = 2
    radius = 20
    hp = 1

    def __init__(self, x, y, color, colorName):
        self.x, self.y = x,y
        self.color = color
        self.colorName = colorName
        self.dx, self.dy = (0,0) #current step (used by Character.move)
        self.hp = Character.hp
        self.projectiles = []
        self.weaponCd = 0
        self.ammo=20
        self.invis = 0
        self.image = loadImage(self.colorName+"_player", Character.radius*2, Character.radius*2)

    def update(self):
        self.weaponCd = max(0, self.weaponCd-1)
        
        # COLLIDE
        self.x+=self.dx
        self.y+=self.dy
        for block in game.blocks:
            #weak physics
            if collides(self, block):
                self.x-=self.dx
                print("only y")
                for block2 in game.blocks:
                    if collides(self, block):
                        self.y-=self.dy
                        self.x+=self.dx
                        print("no wait only x")
                        break
                break
            """
            #badass physics
            if collides(self, block):
                self.x-=dx
                self.y-=dy
                signX = dx//spd
                signY = dy//spd
                for i in range(Character.movementSpeed):
                    self.x+=signX
                    if collides(self, block):
                        self.x-=signX
                    self.y+=signY
                    if collides(self, block):
                        self.y-=signY
            """
                

        # EDGES
        r=Character.radius
        if self.x<0+r:
            self.x=0+r
        if self.x>1280-r:
            self.x=1280-r
        if self.y<0+r:
            self.y=0+r
        if self.y>720-r:
            self.y=720-r

    def is_dead(self):
        return self.hp<=0

    def draw(self):
        if self.invis:
            self.invis-=1
            return
        r = Character.radius
        color = self.color
        if self.weaponCd:
            color = darken(color)
        gameDisplay.blit(self.image, (self.x-r, self.y-r))
        #pygame.draw.rect(gameDisplay, color, (self.x-r, self.y-r, r*2, r*2), 0)

class Player(Character):

    def __init__(self, x, y, color, colorName, controls, block_coords=0):
        if block_coords:
            x = x*Block.radius*2 + Block.radius
            y = y*Block.radius*2 + Block.radius
        super(Player, self).__init__(x, y, color, colorName)
        self.controls = controls

    def update (self, pressed):
        controls = self.controls
        pressed=list(pressed)
        # KEYS
        self.dx=0
        self.dy=0
        spd=Character.movementSpeed
        if pressed[controls["left"]]:
            self.dx-=spd
        if pressed[controls["right"]]:
            self.dx+=spd
        if pressed[controls["up"]]:
            self.dy-=spd
        if pressed[controls["down"]]:
            self.dy+=spd

        super(Player, self).update()

        if pressed[controls["shoot"]] and self.weaponCd==0:
            if (self.dx==0 and self.dy==0):
                self.projectiles.insert(0,SmokeBomb(self))
                self.weaponCd = 60
            elif self.ammo>0:
                self.projectiles.append(Bullet(self))
                self.ammo-=0
                self.weaponCd = 60
                self.invis = 0

        if pressed[controls["summon"]] and self.weaponCd==0:
            if (self.dx==0 and self.dy==0):
                
                fake = FakePlayer(self)
                game.addCharacter(fake)
                self.weaponCd = 60
            else:
                game.addCharacter(Zombie(self))
                self.invis=60
                self.weaponCd = 60

class FakePlayer(Player):

    def __init__(self, owner):
        super(FakePlayer, self).__init__(owner.x, owner.y, owner.color, owner.colorName, owner.controls.copy())
        self.owner = owner
        self.controls["right"], self.controls["left"] = (self.controls["left"], self.controls["right"])
        self.controls["up"], self.controls["down"] = (self.controls["down"], self.controls["up"])
        self.weaponCd = 60
        self.age = 0

    def update(self, pressed):
        super(FakePlayer, self).update(pressed)
        self.age+=1
        if self.age>=150 or self.owner.is_dead():
            self.hp=0

class Bullet():

    radius = 8

    def __init__(self, owner):
        self.owner = owner
        self.color = self.owner.color
        self.x = self.owner.x
        self.y = self.owner.y
        self.xv = self.owner.dx*8
        self.yv = self.owner.dy*8
        print("bullet inited")

    def update(self):
        self.x += self.xv
        self.y += self.yv

        r = Bullet.radius
        if self.x<0+r or self.x>1300-r or self.y<0+r or self.y>700-r:
            self.explode()
        for block in game.blocks:
            if collides(self, block):
                self.explode()

        for character in game.characters:
            if character==self.owner:
                continue

            if collides(self, character):
                self.explode()
                character.hp-=1
                print("hit")
                break
            """
            for proj in character.projectiles:
                if collides(self, proj):
                    proj.explode()
                    self.explode()
                    print("clash")
                    break
            """

    def explode(self): #visual
        if self in self.owner.projectiles:
            self.owner.projectiles.remove(self)
        r=Bullet.radius*3
        pygame.draw.rect(gameDisplay, (255,255,0), (self.x-r,self.y-r,r*2,r*2), 5)
    
    def draw(self):
        r = Bullet.radius
        pygame.draw.rect(gameDisplay, self.color, (self.x-r, self.y-r, r*2, r*2), 0)

class SmokeBomb():
    def __init__(self, owner):
        self.owner = owner
        self.color = self.owner.color
        self.colorName = self.owner.colorName
        self.x = self.owner.x
        self.y = self.owner.y
        self.r = self.owner.__class__.radius
        self.dir = 1
        self.age = 0 #aka weaponcd (for cd imagery)
        self.image = loadImage(self.colorName+"_smoke", Character.radius*2*8, Character.radius*2*8)
        #print("smoke inited")

    def update(self):
        self.age+=1
        self.r+=Character.movementSpeed*self.dir
        if self.r >= Player.radius*8:
            self.dir = -2
        if self.r <= 0:
            self.owner.projectiles.remove(self)

    def draw(self):
        r = self.r
        color = self.color
        if self.age<60:
            color = darken(color)

        surf = pygame.Surface((self.r*2, self.r*2), pygame.SRCALPHA, 32)
        surf = surf.convert_alpha()
        #image = pygame.transform.scale(self.image, (self.r*2, self.r*2))
        surf.blit(self.image, (self.r-Character.radius*8, self.r-Character.radius*8))
        gameDisplay.blit(surf, (self.x-self.r, self.y-self.r))
        #pygame.draw.rect(gameDisplay, color, (self.x-r, self.y-r, r*2, r*2), 0)

class Zombie(Character):
    def __init__(self, owner):
        super(Zombie, self).__init__(owner.x, owner.y, owner.color, owner.colorName)
        self.owner = owner
        self.dx = self.owner.dx
        self.dy = self.owner.dy
        self.age = 0
        print("zombie inited")

    def update(self, pressed):
        super(Zombie, self).update()
        self.age+=1
        if self.age>=60 or self.owner.is_dead():
            self.hp=0
            self.explode()

    def explode(self): #visual
        r=Zombie.radius
        pygame.draw.rect(gameDisplay, (255,0,0), (self.x-r,self.y-r,r*2,r*2), 8)

game = Game()

def addPlayers(game): #maybe rename arg
    p=pygame
    game.addCharacter(Player(0,4, color=(255,0,0), colorName="red", block_coords=1,
    controls={"left":p.K_a, "right":p.K_d, "up":p.K_w, "down":p.K_s, "shoot":p.K_SPACE ,"summon":p.K_e})) 
    game.addCharacter(Player(15,4, color=(0,0,255), colorName="blue", block_coords=1, 
    controls={"left":p.K_LEFT, "right":p.K_RIGHT, "up":p.K_UP, "down":p.K_DOWN, "shoot":p.K_o, "summon":p.K_p}))

addPlayers(game)

gameDisplay = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
jump_out = False
while jump_out == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jump_out = True
    gameDisplay.fill((150,150,150))

    if game.over > 300:
        game = Game()
        addPlayers(game)

    game.update()
    game.draw()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()