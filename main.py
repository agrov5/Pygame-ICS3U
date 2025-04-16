import pygame, sys, math, random, time, os

from pygame import Vector2, sprite
from pygame import mixer
from pygame.draw import rect

global dt

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()

info = pygame.display.Info() 
screen_width,screen_height = info.current_w,info.current_h

screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Burger Cat")
favicon = pygame.image.load("data/images/Burger Cat.png")
pygame.display.set_icon(favicon)

is_menu = True

class Explosion():
    global dt
    def __init__(self, position, size):
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.width = size

    def draw(self, screen):
        pygame.draw.circle(screen, (220, 0, 0), self.position, self.width)
        pygame.draw.circle(screen, (255, 153, 51), self.position, self.width - (self.width / 2))
    
    def scale_down(self):
        if(self.width > 0):
            self.width -= dt * 80


class TimeBubble(pygame.sprite.Sprite):
    global dt
    def __init__(self, position):
        pygame.sprite.Sprite.__init__(self)
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.width = 60
        self.rect = pygame.Rect(self.position.x - self.width, self.position.y - self.width, self.width*2, self.width*2)
        self.allow = True

    def draw(self, screen):
        pygame.draw.circle(screen, (0, 51, 220), self.position, self.width)
        pygame.draw.circle(screen, (200, 200, 255), self.position, self.width - (self.width / 2))
        self.rect = pygame.Rect(self.position.x - self.width, self.position.y - self.width, self.width*2, self.width*2)
    
    def scale_down(self):
        if(self.width > 0):
            self.width -= dt * 8 
    
    def stop_player(self, player):
        player.position = self.position
        player.velocity.x = 0
        player.velocity.y = 0
        player.is_dead = False
        self.allow = False

class RocketBullet():
    def __init__(self, position, angle, speed=5):
        self.position = Vector2()
        self.position.x, self.position.y = position.x, position.y
        self.rect = pygame.Rect(self.position.x, self.position.y, 5, 5)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.distance_traveled = 0
        self.max_distance = 300
    
    def move(self):
        self.position.x += self.dx
        self.position.y += self.dy
        self.rect.topleft = (self.position.x, self.position.y)
        self.distance_traveled += math.hypot(self.dx, self.dy)
    
    def draw(self, screen):
        pygame.draw.rect(screen, (225, 0, 0), self.rect)

    def has_exploded(self):
        return self.distance_traveled >= self.max_distance

class Rocket():
    def __init__(self, position):
        self.position = Vector2(position)
        self.rocket_sprite = pygame.image.load('data/images/Rocket.png').convert_alpha()
        self.rocket_sprite = pygame.transform.scale(self.rocket_sprite, (40, 20))
        self.angle = 0
        self.rockets = []
        self.explosions = []
        self.is_flipped = False
        self.rocket_count = 15
        self.num_bullets = 5
        pygame.font.init()
        self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 300)
        self.refresh_sprite()
        mixer.init()

    def render_current_ammo(self, screen):
        text = self.font.render(str(self.rocket_count), False, (200,200,200))
        text_width, text_height = self.font.size(str(self.rocket_count))
        screen.blit(text, (screen_width/2-text_width/2,screen_height/2-text_height/2))
    
    def shoot(self):
        if self.rocket_count > 0:
            sound = mixer.Sound("data/audio/Firework.mp3")
            sound.set_volume(0.2)
            sound.play()
            
            mouse_x, mouse_y = pygame.mouse.get_pos()
            angle = math.atan2(mouse_y - self.position.y, mouse_x - self.position.x)
            rocket = RocketBullet(self.position, angle, speed=5)
            self.rockets.append(rocket)
            self.rocket_count -= 1
        else:
            sound = mixer.Sound("data/audio/CantShoot.wav")
            sound.set_volume(0.08)
            sound.play()
    
    def update(self, screen):
        new_rockets = []
        for rocket in self.rockets:
            if rocket.has_exploded():
                self.explode(rocket.position)
            else:
                rocket.move()
                rocket.draw(screen)
                new_rockets.append(rocket)
        self.rockets = new_rockets
        
        new_explosions = []
        for bullet in self.explosions:
            bullet.move()
            bullet.draw(screen)
            if not bullet.has_exploded():
                new_explosions.append(bullet)
        self.explosions = new_explosions
    
    def explode(self, position):
        explosion_sound = mixer.Sound("data/audio/Explosion.mp3")
        explosion_sound.set_volume(0.01)
        explosion_sound.play()
        
        for i in range(self.num_bullets):  
            angle = i * (2*math.pi/self.num_bullets)
            bullet = RocketBullet(position, angle, speed=5)
            self.explosions.append(bullet)
    
    def draw(self, screen):
        rotated_sprite = pygame.transform.rotate(self.rocket_sprite, -math.degrees(self.angle))
        screen.blit(rotated_sprite, (self.position.x - rotated_sprite.get_width() / 2, self.position.y - rotated_sprite.get_height() / 2))
        self.update(screen)

    def refresh_sprite(self):
        self.rocket_sprite = pygame.image.load('data/images/Rocket.png').convert_alpha()
        self.rocket_sprite = pygame.transform.scale(self.rocket_sprite, (40, 20))
        self.rocket_sprite = pygame.transform.rotate(self.rocket_sprite, -math.degrees(self.angle))

    def set_position(self, position):
        self.position = position
    
    def set_rotation(self, degrees):
        self.refresh_sprite()
        self.rocket_sprite = pygame.transform.rotate(self.rocket_sprite, degrees)
          
    def blit_position(self):
        return self.position.x - (self.rocket_sprite.get_width() / 2), self.position.y + (self.rocket_sprite.get_height() / 2)

class Player():
    global dt
    def __init__(self):
        self.is_dead = False
        self.score = 0
        self.health = 100
        self.position = pygame.Vector2()
        w, h = screen_width, screen_height
        self.position.xy = w / 2, h / 5
        self.velocity = pygame.Vector2()
        self.rotation = pygame.Vector2()
        self.offset = pygame.Vector2()
        self.rocket = Rocket(self.position)
        self.drag = 100
        self.gravity_scale = 250
        self.allowy = False
        self.player_sprite = pygame.image.load('data/images/Burger Cat.png').convert_alpha()
        self.player_sprite = pygame.transform.scale(self.player_sprite, (70, 84))
        self.elytra_sprite = pygame.image.load('data/images/Elytra.png').convert_alpha()
        self.elytra_sprite = pygame.transform.scale(self.elytra_sprite, (100, 100))
        self.rect = self.player_sprite.get_rect()
        self.rect.topleft = (self.position.x, self.position.y)
        self.rocket.set_position(self.position)
        
        self.arrow_img = pygame.image.load('data/images/Arrow.png').convert_alpha()
        self.arrow_img = pygame.transform.scale(self.arrow_img, (40, 40))

    def move(self):
        self.gravity()
        self.air_resistance()
        self.wall_detection()
        self.position.x -= self.velocity.x * dt
        self.position.y -= self.velocity.y * dt
        self.rect = pygame.Rect(self.position.x,self.position.y, 50,60)
    
    
    def handle_rocket(self):
        self.rocket.set_position(self.position)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.position.x, mouse_y - self.position.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.rocket.set_rotation(angle)

        if(self.offset.x > 0):
            self.offset.x = rel_x if rel_x < 4 else 4
        else:
            self.offset.x = rel_x if rel_x > -4 else -4
        if(self.offset.y > 0):
            self.offset.y = rel_y if rel_y < 4 else 4
        else:
            self.offset.y = rel_y if rel_y > -4 else -4

    def gravity(self):
        self.velocity.y -= self.gravity_scale * dt

    def air_resistance(self):
        if(self.velocity.y > 0):
            self.velocity.y -= self.drag * dt
        if(self.velocity.x > 0):
            self.velocity.x -= (self.drag - 50) * dt
        else:
            self.velocity.x += (self.drag - 50) * dt

    def wall_detection(self):
        if(self.position.x < 0):
            self.position.x = screen_width
        if(self.position.x > screen_width):
            self.position.x = 0
        if self.allowy == True:
            if(self.position.y < 0):
                self.position.y = screen_height-30
            if(self.position.y > screen_height):
                self.position.y = 0

    def get_score(self):
        return self.score

    def check_state(self, last_level):
        global is_menu
        if(self.is_dead == True):
            old_highscore_value = open("data/serialisation/highscore.csv", "r").readline()
            try:
                if(self.score > int(old_highscore_value)):
                    highscore_value = open("data/serialisation/highscore.csv", "w")
                    highscore_value.write(str(self.score))
                    highscore_value.close()
            except:
                pass
            is_menu = True
            Menu(screen, last_level)

    def collision_detection(self, level_builder):
        for i in range(len(level_builder.refills)):
            other = level_builder.refills[i]
            if(self.get_left() < other.get_right() and self.get_right() > other.get_left() and self.get_top() < other.get_bottom() and self.get_bottom() > other.get_top()):
                self.rocket.rocket_count += 1
                level_builder.populate_refill()
                self.score += 1
        
        self.curr_level = 0

        for i in range(len(level_builder.enemies)):
            other = level_builder.enemies[i]
            for rect in level_builder.enemies[i].rectlist:
                if self.rect.colliderect(rect):
                    self.is_dead = True
        if self.allowy == False:
            if(self.position.y > screen_height-10):
                self.is_dead = True
    
    def health_collision_detection(self, level_builder):
        for i in range(len(level_builder.refills)):
            other = level_builder.refills[i]
            if(self.get_left() < other.get_right() and self.get_right() > other.get_left() and self.get_top() < other.get_bottom() and self.get_bottom() > other.get_top()):
                self.rocket.rocket_count += 1
                level_builder.populate_refill()
                self.score += 1

        for i in range(len(level_builder.enemies)):
            other = level_builder.enemies[i]
            for rect in level_builder.enemies[i].rectlist:
                if self.rect.colliderect(rect):
                    self.health -= 10
            for rect in level_builder.enemies[i].bombs:
                if(self.rect.colliderect(rect)):
                    self.health -= 10
                    exp_pos = Vector2()
                    exp_pos.x = rect.x 
                    exp_pos.y = rect.y - 20
                    explosion = Explosion(exp_pos, 100)
                    level_builder.enemies[i].explosions.append(explosion)
                    level_builder.enemies[i].bombs.remove(rect)

                    rel_x, rel_y = exp_pos.x - self.position.x, exp_pos.y - self.position.y
                    vector = Vector2()
                    vector.xy = rel_x, rel_y
                    mag = vector.magnitude()
                    vector.xy /= mag
                    self.velocity.y = 0
                    self.velocity.x = 0
                    self.add_force(vector, 400)
                    break
        if self.allowy == False:
            if(self.position.y > 850):
                w, h = pygame.display.get_surface().get_size()
                self.position.xy = w / 2, h / 5
                self.health -= 10
            if(self.health<=0):
                self.is_dead = True
    
    def get_right(self):
        return self.position.x + (self.player_sprite.get_width() / 2)

    def get_left(self):
        return self.position.x - (self.player_sprite.get_width() / 2)
    
    def get_top(self):
        return self.position.y - (self.player_sprite.get_height() / 2)
    
    def get_bottom(self):
        return self.position.y + (self.player_sprite.get_height() / 2)

    def draw(self, screen):
        screen.blit(self.elytra_sprite, (self.blit_position()[0] - (self.player_sprite.get_width() / 4), self.blit_position()[1]))
        screen.blit(self.player_sprite, self.blit_position())
        self.rocket.draw(screen)
        
        if self.position.y < 0:
            arrow_x = self.position.x - (self.arrow_img.get_width() / 2)
            arrow_y = 0
            screen.blit(self.arrow_img, (arrow_x, arrow_y))
            
            #Display height above "y" under arrow
            font = pygame.font.SysFont(None, 20)
            height_text = font.render(str(int(abs(self.position.y))) + " px", True, (0, 0, 0))
            screen.blit(height_text, (arrow_x, arrow_y + self.arrow_img.get_height()))
        
    def blit_position(self):
        return (self.position.x - (self.player_sprite.get_width() / 2), self.position.y - (self.player_sprite.get_height() / 2))

    def shoot(self):
        if(self.rocket.rocket_count <= 0):
            return
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.position.x, mouse_y - self.position.y
        vector = Vector2()
        vector.xy = rel_x, rel_y
        mag = vector.magnitude()
        vector.xy /= mag
        self.velocity.y = 0
        self.velocity.x = 0
        self.add_force(vector, 500)

    def add_force(self, vector, magnitude):
        self.velocity.x += vector.x * magnitude
        self.velocity.y += vector.y * magnitude

class Refill:
    def __init__(self, position):
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.rocket_sprite = pygame.image.load('data/images/Rocket.png').convert_alpha()
        self.rocket_sprite = pygame.transform.scale(self.rocket_sprite, (60, 30))
        self.rocket_sprite = pygame.transform.rotate(self.rocket_sprite, 90)

    def draw(self, screen):
        screen.blit(self.rocket_sprite, self.position)
    
    def get_right(self):
        return self.position.x + 30

    def get_left(self):
        return self.position.x 
    
    def get_top(self):
        return self.position.y
    
    def get_bottom(self):
        return self.position.y + 40

class Wall:
    global dt
    def __init__(self, position, index):
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.rect = pygame.Rect(self.position, (60,20))
        self.rectlist = [self.rect]    
        self.health = 5 
        self.wallindex = index

    def draw(self, screen):
        pygame.draw.rect(screen,(0,0,0),self.rect)
    
    def collision_detection(self,enemies, wallist):
        for i in range(len(enemies)):
            for rect in enemies[i].rectlist:
                if self.rect.colliderect(rect):
                    self.health -= 1
                enemies[i].rectlist.remove(rect)
        
        wallist = list(wallist)
        if(self.health<=0):
            wallist.remove(wallist[self.wallindex])
        
class Enemy1:
    global dt
    def __init__(self, position):
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.gravity_scale = random.randint(20, 40)

        self.xOffset = 0
        self.yOffset = 0
         
        rand = random.randint(0, 2)
        self.enemy_sprite = None

        if(rand == 0):
            self.enemy_sprite = pygame.image.load('data/images/Shell.png').convert_alpha()
            self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, (40, 40))
            self.xOffset = 40
            self.yOffset = 40
        elif(rand == 1):
            self.enemy_sprite = pygame.image.load('data/images/Fish.png').convert_alpha()
            self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, (30, 50))
            self.xOffset = 30
            self.yOffset = 50
        else:
            self.enemy_sprite = pygame.image.load('data/images/Bone.png').convert_alpha()
            self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, (30, 50))
            self.xOffset = 30
            self.yOffset = 50
        
        self.recter = pygame.Rect(self.position,(self.xOffset,self.yOffset))
        self.rectlist = [self.recter]
        self.timenow = 0 #ignore this
        

    def draw(self, screen):
        screen.blit(self.enemy_sprite, self.position)
        self.gravity()

    def gravity(self):
        self.position.y += self.gravity_scale * dt
        self.gravity_scale += 1
        self.recter = pygame.Rect(self.position,(self.xOffset,self.yOffset))
        self.rectlist = [self.recter]
    
    def get_right(self):
        return self.position.x + self.xOffset

    def get_left(self):
        return self.position.x - self.xOffset
    
    def get_top(self):
        return self.position.y - self.yOffset
    
    def get_bottom(self):
        return self.position.y + self.yOffset

class Enemy2:
    global dt
    def __init__(self, position):
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.gravity_scale = 0
        self.enemy_sprite = pygame.image.load('data/images/Fish.png').convert_alpha()
        self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, (30, 50))
        self.enemy_sprite = pygame.transform.rotate(self.enemy_sprite, 90)
        self.xOffset = 30
        self.yOffset = 50
        self.rect = pygame.Rect(self.position, (30,50))
        self.rectlist = [self.rect]
        self.rotated_surface = self.enemy_sprite
        self.timenow = 0 #ignore this

    def draw(self, screen):
        screen.blit(self.rotated_surface, self.position)
    
    def move(self, targetx, targety):
        oldCenter = self.position
        angle = math.atan2(targety - self.position.y, targetx - self.position.x)
        angle = angle * 180/ math.pi
        rot_image = pygame.transform.rotate(self.enemy_sprite, 360 - angle)
        self.rotated_surface = rot_image
        self.position = oldCenter
        angle = math.atan2(targety - self.position.y, targetx - self.position.x)
        self.dx = math.cos(angle) * 2
        self.dy = math.sin(angle) * 2
        self.position.x += self.dx * 0.4
        self.position.y += self.dy * 0.4
        self.rect = pygame.Rect(self.position, (30,50))
        self.rectlist = [self.rect]
    
    def gravity(self):
        self.position.y += self.gravity_scale * dt

class Enemy3:
    global dt
    def __init__(self, position, direction):
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.speed = 2
        self.position1 = Vector2()
        self.laserect_pos = Vector2()
        self.gravity_scale = 0
        self.direction = direction 
        self.enemy_sprite = pygame.image.load('data/images/Shell.png').convert_alpha()
        self.enemy_sprite_size = (40, 40)
        self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, self.enemy_sprite_size)
        self.enemy_sprite1 = pygame.transform.scale(self.enemy_sprite, self.enemy_sprite_size)

        if self.direction == "y-axis":
            self.enemy_sprite = pygame.transform.rotate(self.enemy_sprite, 90)
            self.enemy_sprite1 = pygame.transform.rotate(self.enemy_sprite, 180)
            self.position1.y = position.y
            self.laserect = pygame.Surface((screen_width, 10))
            self.laserect_pos.x = self.position.x + self.enemy_sprite_size[0]
            self.laserect_pos.y = self.position.y + 1*self.enemy_sprite_size[1]//4
            if self.position.x == 0:
                self.position1.x = position.x + screen_width - self.enemy_sprite_size[0]
            self.rect2 = pygame.Rect(self.laserect_pos,(screen_width, self.enemy_sprite_size[1]//2))
        elif self.direction == "x-axis":
            self.enemy_sprite = pygame.transform.rotate(self.enemy_sprite, 0)
            self.enemy_sprite1 = pygame.transform.rotate(self.enemy_sprite, 180)
            self.position1.x = position.x
            self.laserect = pygame.Surface((10, screen_height))
            self.laserect_pos.x = self.position.x + 1*self.enemy_sprite_size[0]//4
            self.laserect_pos.y = self.position.y + self.enemy_sprite_size[1]
            if self.position.y == 0:
                self.position1.y = position.y + screen_height - self.enemy_sprite_size[1]
            self.rect2 = pygame.Rect(self.laserect_pos,(self.enemy_sprite_size[0]//2, screen_height))

        self.rect = pygame.Rect(self.position, self.enemy_sprite_size)
        self.rect1 = pygame.Rect(self.position1, self.enemy_sprite_size)
        self.rectlist = [self.rect,self.rect1,self.rect2]
        self.laserect.fill((255, 0, 0))
        self.xOffset = 40
        self.yOffset = 40
        self.count = 0
        self.traveled_distance = 0
        self.first_spawn = True
        self.timenow = pygame.time.get_ticks()

    def draw(self, screen):
        if self.first_spawn:
            screen.blit(self.enemy_sprite, self.position)
            sound = mixer.Sound("data/audio/laser-charge.mp3")
            sound.set_volume(0.1)
            sound.play()
            screen.blit(self.laserect, self.laserect_pos)
            screen.blit(self.enemy_sprite1, self.position1)
            self.first_spawn = False
        else:
            screen.blit(self.enemy_sprite, self.position)
            screen.blit(self.laserect, self.laserect_pos)
            screen.blit(self.enemy_sprite1, self.position1)
    
    def move(self):
        if self.direction == "y-axis":
            if self.position.y <= 100:
                self.count = 0
            elif self.position.y >= screen_height - 100:
                self.count = 1
            if self.count == 0:
                self.position.y += self.speed
                self.position1.y += self.speed
            elif self.count == 1:
                self.position.y -= self.speed
                self.position1.y -= self.speed
            self.traveled_distance += self.speed
            self.laserect_pos.x = self.position.x + self.enemy_sprite_size[0]
            self.laserect_pos.y = self.position.y + 1*self.enemy_sprite_size[1]//4
            self.rect2 = pygame.Rect(self.laserect_pos, (screen_width, self.enemy_sprite_size[1]//2))
        elif self.direction == "x-axis":
            if self.position.x <= 100:
                self.count = 0
            elif self.position.x >= screen_width - 100:
                self.count = 1
            if self.count == 0:
                self.position.x += self.speed
                self.position1.x += self.speed
            elif self.count == 1:
                self.position.x -= self.speed
                self.position1.x -= self.speed
            self.traveled_distance += self.speed
            self.laserect_pos.x = self.position.x + 1*self.enemy_sprite_size[0]//4
            self.laserect_pos.y = self.position.y + self.enemy_sprite_size[1]
            self.rect2 = pygame.Rect(self.laserect_pos,(self.enemy_sprite_size[0]//2, screen_height))

        self.rect = pygame.Rect(self.position, self.enemy_sprite_size)
        self.rect1 = pygame.Rect(self.position1, self.enemy_sprite_size)
        self.rectlist = [self.rect,self.rect1,self.rect2]
    
    def gravity(self):
        self.position.y += 0

class Enemy4:
    global dt
    def __init__(self, position):
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.gravity_scale = 0
        self.enemy_sprite = pygame.image.load('data/images/Bone.png').convert_alpha()
        self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, (30, 50))
        self.bomb_img = pygame.transform.scale(pygame.image.load('data/images/Grenade.png').convert_alpha(), (30, 50))
        self.rect = pygame.Rect(self.position,(30,50))
        self.speed = random.randrange(1, 4)
        self.interval = random.randrange(1,10)
        self.rectlist = [self.rect]
        self.xOffset = 30
        self.yOffset = 50
        self.bombs = []
        self.explosions = []
        self.count = 0
        self.timenow = pygame.time.get_ticks()

    def draw(self, screen):
        self.move()
        screen.blit(self.enemy_sprite, self.position)

        explosions_copy = self.explosions.copy()
        for i in range(len(explosions_copy)):
            if(explosions_copy[i].width <= 1):
                self.rectlist.remove(self.rectlist[i])
                self.explosions.remove(explosions_copy[i])
                break
            explosions_copy[i].scale_down()
            explosions_copy[i].width -= 10
            explosions_copy[i].draw(screen)
        
        for bomb in self.bombs:
            screen.blit(self.bomb_img, (bomb.x-15,bomb.y))
    
    def move(self):
        if self.position.x <= 0:
            self.count = 0
        elif self.position.x >= screen_width - 30:
            self.count = 1
        if self.count == 0:
            self.position.x += self.speed
        elif self.count == 1:
            self.position.x -= self.speed
        self.rect = pygame.Rect(self.position,(30, 50))
        self.rectlist = [self.rect]
        self.drop_bombs()
    
    def drop_bombs(self):
        if abs(int((pygame.time.get_ticks() - self.timenow)/1000)) >= self.interval:
            bomb = pygame.Rect(self.rect.centerx, self.rect.bottom, 20, 20)
            self.bombs.append(bomb)
            self.timenow = pygame.time.get_ticks()
        for bomb in self.bombs:
            bomb.y += 5
        
        self.reach_end()
    
    def reach_end(self):
        bombs_copy = self.bombs.copy()
        for bomb in bombs_copy:
            if bomb.y >= screen_height:
                # Create an explosion at the bomb's location
                exp_pos = Vector2()
                exp_pos.x = bomb.x 
                exp_pos.y = bomb.y - 20
                explosion = Explosion(exp_pos, 100)
                self.explosions.append(explosion)
                self.rectlist.append(pygame.Rect(exp_pos.x, exp_pos.y, 100, 100))
                self.bombs.remove(bomb)

class LevelBuilder:
    def __init__(self):
        self.refills = []
        self.enemies = []
        self.killed = 0
        self.more_enemies = 0
        
    def populate_refill(self):
        self.refills = []
        sound = mixer.Sound("data/audio/Reload.wav")
        sound.set_volume(0.1)
        sound.play()
        for i in range(2):
            pos = Vector2()
            pos.x = random.randint(100, 700)
            pos.y = random.randint(100, 500)
            refill = Refill(pos)
            self.refills.append(refill)

    def spawn_enemies1(self):
        rand = random.randint(1 + self.more_enemies, 3 + self.more_enemies)
        sound = mixer.Sound("data/audio/Spawn.wav")
        sound.set_volume(0.1)
        sound.play()
        for i in range(rand):
            random_pos = random.randint(100, screen_width-100)
            position = Vector2()
            position.x = random_pos
            position.y = screen_height/12
            enemy = Enemy1(position)
            self.enemies.append(enemy)
    
    def spawn_enemies2(self):
        rand = 5
        sound = mixer.Sound("data/audio/Spawn.wav")
        sound.set_volume(0.1)
        sound.play()
        for i in range(rand):
            options = [(0,random.randint(0,screen_height)), (random.randint(0,screen_width),0), (screen_width,random.randint(0,screen_height)), (random.randint(0,screen_width),screen_height)]
            choose = random.randint(0,3)
            position = Vector2()
            position.x = options[choose][0]
            position.y = options[choose][1]
            enemy = Enemy2(position)
            self.enemies.append(enemy)
    
    def spawn_enemies3(self):
        rand = random.randint(1, 4)
        sound = mixer.Sound("data/audio/Spawn.wav")
        sound.set_volume(0.1)
        sound.play()
        for i in range(rand):
            options = [(0, 0), (0, 0), (0, screen_height), (screen_width, 0)]
            choose = random.randint(0,3)
            position = Vector2()
            position.x = options[choose][0]
            position.y = options[choose][1]
            match choose:
                case 0:
                    enemy = Enemy3(position,"y-axis")
                case 1:
                    enemy = Enemy3(position,"x-axis")
                case 2:
                    enemy = Enemy3(position,"y-axis")
                case 3:
                    enemy = Enemy3(position,"x-axis")
            self.enemies.append(enemy)
    
    def spawn_enemies4(self):
        rand = 5
        sound = mixer.Sound("data/audio/Spawn.wav")
        sound.set_volume(0.1)
        sound.play()
        for i in range(rand):
            random_pos = random.randint(0, screen_width)
            position = Vector2()
            position.x = random_pos
            position.y = 0
            enemy = Enemy4(position)
            self.enemies.append(enemy)
    
    def collision_detection(self, rocket, obj_type, wavenum):
        enemies_copy = self.enemies.copy()
        for i in range(0, len(enemies_copy)):
            if wavenum == 2:
                if obj_type == "rocket":
                    if (enemies_copy[i].rectlist[0].colliderect(rocket.rect)):
                        self.killed += 1
                        self.enemies.remove(enemies_copy[i])    # Original inside: enemies_copy[i].rectlist.remove(rect)
                        break
                elif obj_type == "time bubble":
                    if (enemies_copy[i].rectlist[0].colliderect(rocket.rect)):
                        self.killed += 1
                        self.enemies.remove(enemies_copy[i])
                        break
            elif wavenum == 4:
                for rect in self.enemies[i].bombs:
                    if(rect.colliderect(rocket.rect)):
                        exp_pos = Vector2()
                        exp_pos.x = rect.x 
                        exp_pos.y = rect.y - 20
                        explosion = Explosion(exp_pos, 100)
                        self.enemies[i].explosions.append(explosion)
                        self.enemies[i].bombs.remove(rect)
                        break

    def draw(self, screen):
        for i in range(len(self.refills)):
            self.refills[i].draw(screen) 
        
        enemies_copy = self.enemies.copy()
        for i in range(len(enemies_copy)):
            enemies_copy[i].draw(screen)    
            if(enemies_copy[i].position.y > 850):
                self.enemies.remove(enemies_copy[i])
            
class Game:
    def __init__(self, screen, last_level):
        global wave_num
        self.screen = screen
        self.size = None
        self.width = None
        self.height = None
        self.background_color = 240, 240, 240
        self.player = Player()
        self.level_builder = LevelBuilder()
        self.last_level = last_level
        self.menu = Menu(screen, self.last_level)
        self.clock = pygame.time.Clock()
        self.score = 0
        wave_num = 1
        self.bg_img = pygame.image.load('data/images/end_bg.jpg').convert_alpha()
        self.bg_img = pygame.transform.scale(self.bg_img, (screen_width, screen_height))

        self.cloud1 = pygame.image.load('data/images/cloud-1.png').convert_alpha()
        self.cloud1 = pygame.transform.scale(self.cloud1, (400, 80))
        self.cloud2 = pygame.image.load('data/images/cloud-2.png').convert_alpha()
        self.cloud2 = pygame.transform.scale(self.cloud1, (200, 80))
        self.cloud3 = pygame.image.load('data/images/cloud-3.png').convert_alpha()
        self.cloud3 = pygame.transform.scale(self.cloud1, (200, 80))
        self.cloud4 = pygame.image.load('data/images/cloud-4.png').convert_alpha()
        self.cloud4 = pygame.transform.scale(self.cloud1, (400, 80))
        self.clouds = [] 

        for _ in range(8):
            cloud_img = random.choice([self.cloud1, self.cloud2, self.cloud3, self.cloud4])
            self.clouds.append([cloud_img, random.randint(0, screen_width), screen_height - random.randint(100, 200), random.uniform(0.1, 0.5)])

        self.go_to_last_level()

    def go_to_last_level(self):
        ([self.level1, self.level2, self.level3, self.level4])[self.last_level - 1]()

    def level1(self):
        global is_menu
        global wave_num
        self.last_level = 1
        wave_num = 1
        self.menu.new_wave(wave_num)
        self.level_builder.populate_refill()
        self.level_builder.enemies = []
        next_time = time.time()
        elapsed_time = time.time()
        min_time = 5
        max_time = 10
        enemiy_iteration = 0
        timenow = pygame.time.get_ticks()
        timenow1 = pygame.time.get_ticks()
        self.handle_dt()    #its here, because we want to essentially "reset" it so that, in two lines, it will ahve a valeus close to 0, makgi nthe palyer nto move, no matter how logn the user waits in menu
        while ((not is_menu) or (wave_num == 1)):
            self.handle_dt()
            self.clear_screen()

            self.player.rocket.render_current_ammo(screen)
            
            self.level_builder.draw(screen)
            self.player.move()
            self.player.handle_rocket()
            self.player.collision_detection(self.level_builder)
            self.player.check_state(self.last_level)
            self.player.draw(self.screen)

            self.score = self.player.get_score()

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("Goal: Survive for " + str(30 - abs(int((pygame.time.get_ticks() - timenow)/1000))) + " seconds", False, (0, 0, 0))
            text_width, text_height = self.font.size("Goal: Survive for " + str(30 - abs(int((pygame.time.get_ticks() - timenow)/1000))) + " seconds")
            screen.blit(text, (screen_width/10 - text_width/2, 0))

            pygame.display.flip()
            self.handle_events()

            elapsed_time = time.time()
            if(elapsed_time > next_time):
                next_time = elapsed_time + random.randint(min_time, max_time)
                self.level_builder.spawn_enemies1()
                enemiy_iteration += 1
                if(enemiy_iteration > 5 and min_time > 1):
                    min_time -= 1
                    max_time -= 1
                    enemiy_iteration = 0
            if abs(int((pygame.time.get_ticks() - timenow1)/1000)) >= 10:
                self.level_builder.more_enemies += 2
                timenow1 = pygame.time.get_ticks()
            if abs(int((pygame.time.get_ticks() - timenow)/1000)) >= 30:   
                self.player.rocket.rocket_count += 5
                self.last_level = 2
                self.go_to_last_level()

    def level2(self):
        global is_menu, wave_num
        self.last_level = 2
        wave_num = 2
        w, h = pygame.display.get_surface().get_size()
        self.player.position.xy = w / 2, h / 5
        self.menu.new_wave(wave_num)
        self.player.is_dead = False
        self.level_builder.enemies = []
        self.level_builder.populate_refill()
        self.level_builder.killed = 0
        next_time = time.time()
        elapsed_time = time.time()
        min_time, max_time = 5, 10
        enemy_iteration = 0
        eject_cooldown = 0 
        stuck_in_timebubble = False
        tb_pos = Vector2(random.randint(10, screen_width-10), random.randint(10, screen_height-10))
        tb = TimeBubble(tb_pos)
        tb.allow = True
        
        timenow = pygame.time.get_ticks()
        self.handle_dt()
        while not is_menu or wave_num == 2:
            self.handle_dt()
            self.clear_screen()
            
            self.player.rocket.render_current_ammo(screen)
            
            enemies_copy = self.level_builder.enemies.copy()
            for i in range(len(enemies_copy) - 1):
                if not enemies_copy[i].rectlist[0].colliderect(tb.rect):
                    self.level_builder.enemies[i].move(self.player.position.x, self.player.position.y)
            
            self.level_builder.draw(screen)
            
            if tb.allow:
                self.player.move()
                self.player.collision_detection(self.level_builder)
            self.player.handle_rocket()
            
            self.player.check_state(self.last_level)
            
            for rocket in self.player.rocket.rockets:
                self.level_builder.collision_detection(rocket, "rocket", 2)
            
            for bullet in self.player.rocket.explosions:
                self.level_builder.collision_detection(bullet, "rocket", 2)
            
            if abs((pygame.time.get_ticks() - timenow) / 1000) >= 15:
                tb_pos = Vector2(random.randint(10, screen_width-10), random.randint(10, screen_height-10))
                tb = TimeBubble(tb_pos)
                timenow = pygame.time.get_ticks()
            
            if tb.width <= 1:
                tb.allow = True
                stuck_in_timebubble = False
                tb.kill()
            else:
                tb.scale_down()
                if tb.rect.colliderect(self.player.rect):
                    if pygame.time.get_ticks() > eject_cooldown:
                        eject_cooldown = 0
                        stuck_in_timebubble = True
                        tb.stop_player(self.player)
                        tb.allow = False
                    else:
                        tb.allow = True
                        stuck_in_timebubble = False
                else:
                    tb.allow = True
                    stuck_in_timebubble = False
                tb.draw(screen)
            
            self.player.draw(self.screen)
            self.score = self.player.get_score()

            if stuck_in_timebubble:
                font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
                escape_text = font.render("Press E to escape!", True, (0, 0, 0))
                text_width, text_height = font.size("Press E to escape!")
                screen.blit(escape_text, (screen_width/70, screen_height - 3*text_height/2))

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("Goal: Kill " + str(10 - self.level_builder.killed) + " enemies", False, (0, 0, 0))
            text_width, text_height = self.font.size("Goal: Kill " + str(10 - self.level_builder.killed) + " enemies")
            screen.blit(text, (screen_width/70, text_height/2))
            
            pygame.display.flip()
            self.handle_events()
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e] and stuck_in_timebubble and eject_cooldown == 0:
                stuck_in_timebubble = False
                eject_cooldown = pygame.time.get_ticks() + 3000  
                tb.allow = True 
            
            elapsed_time = time.time()
            if elapsed_time > next_time:
                next_time = elapsed_time + random.randint(min_time, max_time)
                self.level_builder.spawn_enemies2()
                enemy_iteration += 1
                if enemy_iteration > 5 and min_time > 1:
                    min_time -= 1
                    max_time -= 1
                    enemy_iteration = 0
            
            if self.level_builder.killed == 10:
                self.player.rocket.rocket_count += 2
                self.last_level = 3
                self.go_to_last_level()

    def level3(self):
        global is_menu
        global wave_num
        self.last_level = 3
        wave_num = 3
        self.menu.new_wave(wave_num)
        self.level_builder.enemies = []
        self.level_builder.populate_refill()
        self.level_builder.killed = 0
        next_time = time.time() + 3
        elapsed_time = time.time()
        min_time = 5
        max_time = 10
        enemiy_iteration = 0
        w, h = pygame.display.get_surface().get_size()
        self.player.position.xy = w / 2, h / 5
        self.player.draw(screen) 
        self.player.allowy = True
        timenow = pygame.time.get_ticks()
        self.handle_dt()    #its here, because we want to essentially "reset" it so that, in two lines, it will ahve a valeus close to 0, makgi nthe palyer nto move, no matter how logn the user waits in menu
        while ((not is_menu) or (wave_num == 3)):
            self.handle_dt()
            self.clear_screen()

            self.player.rocket.render_current_ammo(screen)
            
            enemies_copy = self.level_builder.enemies.copy()
            for i in range(0, len(enemies_copy)):
                enemies_copy[i].move()   
                if enemies_copy[i].traveled_distance > 500 - (len(enemies_copy) - 1) * 100:
                    self.level_builder.enemies.remove(enemies_copy[i])
                #if abs(int((pygame.time.get_ticks() - self.level_builder.enemies[i-1].timenow)/1000)) >= 5:
                    #self.level_builder.enemies.remove(self.level_builder.enemies[i-1])
            
            self.level_builder.draw(screen)
            self.player.move()
            self.player.handle_rocket()
            self.player.collision_detection(self.level_builder)
            self.player.check_state(self.last_level)
            
            self.player.draw(self.screen)
            self.score = self.player.get_score()

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("Goal: Avoid the lasers for " + str(30 - abs(int((pygame.time.get_ticks() - timenow)/1000))) + " seconds", False, (0, 0, 0))
            text_width, text_height = self.font.size("Goal: Avoid the lasers for " + str(30 - abs(int((pygame.time.get_ticks() - timenow)/1000))) + " seconds")
            screen.blit(text, (screen_width/70, text_height/2))

            text = self.font.render("Tip: You can fall through the bottom now!", False, (0, 0, 0))
            text_width, text_height = self.font.size("Tip: You can fall through the bottom now!")
            screen.blit(text, (screen_width/70, screen_height - 3*text_height/2))
            
            pygame.display.flip()
            self.handle_events()

            elapsed_time = time.time()
            if(elapsed_time > next_time):
                next_time = elapsed_time + random.randint(min_time, max_time)
                self.level_builder.spawn_enemies3()
                enemiy_iteration += 1
                if(enemiy_iteration > 5 and min_time > 1):
                    min_time -= 1
                    max_time -= 1
                    enemiy_iteration = 0
            if abs(int((pygame.time.get_ticks() - timenow)/1000)) >= 30:
                self.player.rocket.rocket_count += 2
                self.last_level = 4
                self.go_to_last_level()

    def level4(self):
        global is_menu
        global wave_num
        self.last_level = 4
        wave_num = 4
        self.menu.new_wave(wave_num)
        self.level_builder.populate_refill()
        self.level_builder.enemies = []
        self.player.health = 100
        self.player.rocket.rocket_count += 10
        next_time = time.time()
        elapsed_time = time.time()
        min_time = 5
        max_time = 10
        enemiy_iteration = 0
        timenow = pygame.time.get_ticks()
        self.handle_dt()    #its here, because we want to essentially "reset" it so that, in two lines, it will ahve a valeus close to 0, makgi nthe palyer nto move, no matter how logn the user waits in menu
        while ((not is_menu) or (wave_num == 4)):
            self.handle_dt()
            self.clear_screen()

            self.player.rocket.render_current_ammo(screen)
            
            self.level_builder.draw(screen)
            self.player.move()
            self.player.handle_rocket()
            self.player.health_collision_detection(self.level_builder)
            self.player.check_state(last_level)
            self.player.draw(self.screen)
            
            for rocket in self.player.rocket.rockets:
                self.level_builder.collision_detection(rocket, "rocket", 4)
            
            for bullet in self.player.rocket.explosions:
                self.level_builder.collision_detection(bullet, "rocket", 4)

            self.score = self.player.get_score()

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("Goal: Survive for " + str(60 - abs(int((pygame.time.get_ticks() - timenow)/1000))) + " seconds", False, (0, 0, 0))
            text_width, text_height = self.font.size("Goal: Survive for " + str(60 - abs(int((pygame.time.get_ticks() - timenow)/1000))) + " seconds")
            screen.blit(text, (screen_width/10 - text_width/2, 0))
            
            # Health Bar
            max_health = 100
            bar_width = int(screen_width * 0.15)
            bar_height = int(screen_height * 0.02)
            health_ratio = self.player.health / max_health

            font_size = int(screen_height * 0.03)
            font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", font_size)
            label = font.render("Health", True, (0, 0, 0))
            screen.blit(label, (20, screen_height - bar_height - 50))

            bg_rect = pygame.Rect(20, screen_height - bar_height - 20, bar_width, bar_height)
            fill_rect = pygame.Rect(20, screen_height - bar_height - 20, int(bar_width * health_ratio), bar_height)

            pygame.draw.rect(screen, (50, 50, 50), bg_rect)
            pygame.draw.rect(screen, (200, 0, 0), fill_rect)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect, 2)

            pygame.display.flip()
            self.handle_events()


            elapsed_time = time.time()
            if(elapsed_time > next_time):
                next_time = elapsed_time + random.randint(min_time, max_time)
                self.level_builder.spawn_enemies4()
                enemiy_iteration += 1
                if(enemiy_iteration > 5 and min_time > 1):
                    min_time -= 1
                    max_time -= 1
                    enemiy_iteration = 0
            if abs(int((pygame.time.get_ticks() - timenow)/1000)) >= 60:
                self.player.rocket.rocket_count += 2
                self.last_level = 5
                self.go_to_last_level()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.player.shoot()      
                self.player.rocket.shoot()     

    def clear_screen(self):
        self.screen.fill(self.background_color)
        #screen.blit(self.bg_img, (0, 0))

        for cloud in self.clouds:
            surf, x, y, speed = cloud
            x += speed  
            if x > screen_width:  # if off screen
                x = -surf.get_width()  # go to left
                y = random.randint(screen_height - 180, screen_height - 120)  
                speed = random.uniform(0.3, 1.0) 
            cloud[1], cloud[2], cloud[3] = x, y, speed  
            screen.blit(surf, (x, y))

    def handle_dt(self):
        global dt
        dt = self.clock.tick() / 1000

class Menu():
    def __init__(self, screen, last_level):
        self.background_color = 240, 240, 240
        self.screen = screen
        self.bg_img = pygame.image.load('data/images/end_bg.jpg').convert_alpha()
        self.bg_img = pygame.transform.scale(self.bg_img, (screen_width, screen_height))
        self.last_level = last_level
        self.update()

    def update(self):
        global is_menu
        pygame.font.init()
    
        sound = mixer.Sound("data/audio/Error.wav")
        sound.set_volume(0.05)
        sound.play()

        while is_menu:
            self.clear_screen()

            logo = pygame.image.load('data/images/Burger Cat.png').convert_alpha()
            logo = pygame.transform.scale(logo, (120, 140))
            screen.blit(logo, (screen_width/2 -100, screen_height/2 - 250))

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 70)
            text = self.font.render("Burger Cat", False, (100,100,100))
            text_width, text_height = self.font.size("Burger Cat")
            screen.blit(text, (screen_width/2 - text_width/2, screen_height/2 - 120))

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("By: Akshit E. & Aryan G.", False, (0, 0, 139))
            text_width, text_height = self.font.size("By: Akshit E. & Aryan G.")
            screen.blit(text, (screen_width/2 - text_width/2, screen_height/2 + 80))

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 50)
            text = self.font.render("Click To Play", False, (200,200,200))
            text_width, text_height = self.font.size("Click To Play")
            screen.blit(text, (screen_width/2 - text_width/2, 400 + (math.sin(time.time() * 10) * 5)))

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 30)
            highscore_value = open("data/serialisation/highscore.csv", "r").readline()
            highscore = self.font.render("Highscore: " + str(highscore_value), False, (180,180,180))
            text_width, text_height = self.font.size("Highscore: " + str(highscore_value))
            screen.blit(highscore, (screen_width/2 - text_width/2, 460 + (math.sin(time.time() * 10) * 5)))
            pygame.display.flip()
            self.handle_events()

    def clear_screen(self):
        self.screen.fill(self.background_color)
        #screen.blit(self.bg_img, (0, 0))
            
    def handle_events(self):
        global is_menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                is_menu = False
                Game(screen, self.last_level)

    def new_wave(self, wave_num):
        global is_wave
        pygame.font.init()
    
        is_wave = True
        goals = ["Survive for 30s", "Kill 10 Enemies.", "Avoid the Lasers", "Survive for 60s", "Kill the Boss"]

        screen.blit(self.bg_img, (0, 0))
        while is_wave:
            self.clear_screen()
            
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 70)
            text = self.font.render("Wave " + str(wave_num), False, (100,100,100))
            text_width, text_height = self.font.size("Wave " + str(wave_num))
            screen.blit(text, (screen_width/2 - text_width/2, screen_height/2 - 20))

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 50)
            text = self.font.render("Goal: " + goals[wave_num -1], False, (200,200,200))
            text_width, text_height = self.font.size("Goal: " + goals[wave_num -1])
            screen.blit(text, (screen_width/2 - text_width/2, 320 + (math.sin(time.time() * 10) * 5)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    is_wave = False
                    break
            pygame.display.flip()

global instance
instance = None

mixer.init()
mixer.music.load("data/audio/music-rizzlas.mp3")
mixer.music.set_volume(0.06)
mixer.music.play(-1)
last_level = 4

while(True):
    if(is_menu):
        instance = Menu(screen, last_level)
    else:
        instance = Game(screen, last_level) 
        last_level = instance.last_level
