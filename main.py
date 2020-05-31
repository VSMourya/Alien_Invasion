import os
import random
import time
import pygame

pygame.font.init()

W,H = 750,750
WIN = pygame.display.set_mode((W,H))
pygame.display.set_caption("Mission 'SAVE THE EARTH' ")


RED_SPACESHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets","ship_red_small.png")),(50,50))
GREEN_SPACESHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets","ship_green_small.png")),(50,50))
BLUE_SPACESHIP = pygame.image.load(os.path.join("assets","ship_blue_small.png"))

# main player ship
YELLOW_SPACESHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets","ship_yellow.png")),(70,86))
# YELLOW_SPACESHIP = pygame.image.load(os.path.join("assets","ship_yellow.png"))


#lasers

RED_LASER = pygame.image.load(os.path.join("assets","laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","laser_yellow.png"))

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","background-2.jpg")),(W,H))


class Laser:

    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img,(self.x,self.y))

    def move(self,vel):
        self.y += vel

    def off_screen(self,height):
        return not (self.y <= height and self.y >= 0)

    def collision(self,obj):
        return collide(self,obj)

class Ship:

    COOLDOWN = 5

    def __init__(self,x,y,health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.lasers = []
        self.ship_Img = None
        self.laser_Img = None
        self.coolDownCounter = 0

    def draw(self,window):
        window.blit(self.ship_Img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(H):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_Img.get_width()

    def get_height(self):
        return self.ship_Img.get_height()


    def shoot(self):
        if self.coolDownCounter == 0:
            laser = Laser(self.x,self.y,self.laser_Img)
            self.lasers.append(laser)
            self.coolDownCounter = 1

    def cooldown(self):
        if self.coolDownCounter >= self.COOLDOWN:
            self.coolDownCounter = 0
        elif self.coolDownCounter > 0:
            self.coolDownCounter += 1



class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x,y,health)
        self.ship_Img = YELLOW_SPACESHIP
        self.laser_Img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_Img)
        self.max_health = health
        self.score = 0
        self.snaps = 5

    def thanosSnap(self,enemies):

        n = len(enemies)
        half  = len(enemies)//2

        if self.snaps:
            if n >= half:
                enemies.pop()
                n-=1
            self.snaps -= 1
        print(f"HIT : {n , len(enemies)}")
        # return True if self.snaps != 0 else False



    def move_lasers(self,vel,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(H):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        self.score += 1
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)


    def draw(self,window):
        super().draw(window)
        self.healthBar(window)

    def healthBar(self,window):
        pygame.draw.rect(window, (255, 0, 0),(self.x, self.y + self.ship_Img.get_height() + 10, self.ship_Img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_Img.get_height() + 10, self.ship_Img.get_width() * (self.health/self.max_health), 10))



class Enemy(Ship):


    COLOR_MAP = {
        "red": (RED_SPACESHIP, RED_LASER),
        "green": (GREEN_SPACESHIP, GREEN_LASER),
        "blue": (BLUE_SPACESHIP, BLUE_LASER)
    }

    def __init__(self,x,y,color,health= 100):
        super().__init__(x,y,health)
        self.ship_Img, self.laser_Img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_Img)

    def move(self,vel):
        self.y += vel


    def shoot(self):
        if self.coolDownCounter == 0:
            laser = Laser(self.x-10,self.y,self.laser_Img)
            self.lasers.append(laser)
            self.coolDownCounter = 1


def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y

    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None

def main():
    running = True
    FPS = 80
    level = 1
    lives = 5
    mainFont = pygame.font.SysFont("ProductSans",30)
    lostFont = pygame.font.SysFont("ProductSans",60)
    player  = Player(320,500)
    clock = pygame.time.Clock()

    lost = False
    enemies = []

    wave_length = 5
    enemy_vel = 1

    laser_velocity = 5
    player_velocity = 5

    lost = False
    lost_count = 0

    def showWindow():
        WIN.blit(BG,(0,0))
        livesLabel = mainFont.render(f"Lives : {lives}",1,(255,255,255))
        scoreLabel = mainFont.render(f"Score : {player.score}",1,(255,255,255))
        # levelsLabel = mainFont.render(f"Levelsssss : {level}",1,(255,255,255))


        WIN.blit(livesLabel,(10,10))
        # WIN.blit(levelsLabel,(W - levelsLabel.get_width() - 10,10))
        WIN.blit(scoreLabel,(W - scoreLabel.get_width() - 10,10))

        player.draw(WIN)

        if lost:
            lost_label = lostFont.render("You Lost !!",1,(255,255,255))
            WIN.blit(lost_label,(W/2 - lost_label.get_width()/2,350))


        for enemy in enemies:
            enemy.draw(WIN)

        pygame.display.update()

    while running:
        clock.tick(FPS)
        showWindow()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS*5:
                running = False
            else:
                continue

        if len(enemies) == 0:
            level+=1
            wave_length += 10
            for i in range(wave_length):
                enemy = Enemy(random.randrange(40 ,W-100),random.randrange(-1500,-100),random.choice(["red","green","blue"]))
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()



        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_velocity > 0: #LEFT
            player.x -= player_velocity
        if keys[pygame.K_d] and player.x + player_velocity + player.get_width() < W:
            player.x += player_velocity
        if keys[pygame.K_w] and player.y - player_velocity > 0: #LEFT
            player.y -= player_velocity
        if keys[pygame.K_s] and player.y + player_velocity + player.get_height() + 15 < H:
            player.y += player_velocity
        if keys[pygame.K_RETURN]:
            player.shoot()
        if keys[pygame.K_SPACE]:
            player.thanosSnap(enemies)
            player.draw(WIN)

        print(len(enemies)," ", enemies)

        for enemy in enemies[:]:


            enemy.move(enemy_vel)
            enemy.move_lasers(laser_velocity,player)

            if random.randrange(0,120) == 1:
                enemy.shoot()

            if collide(enemy,player):
                player.health -= 10
                enemies.remove(enemy)

            if enemy.y + enemy.get_height() > H:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-laser_velocity,enemies)

def mainMenu():

    titleFont = pygame.font.SysFont("comicsans", 60)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = titleFont.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (W/2 - title_label.get_width()/2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()





if __name__ == '__main__':
    mainMenu()



# start from 1:07:20

