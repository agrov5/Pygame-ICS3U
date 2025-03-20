import pygame, sys, math, random, time

from pygame import Vector2, sprite
from pygame import mixer
from pygame.draw import rect

global dt

pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Burger Cat")
is_menu = True

class Player():
    global dt
    def __init__(self):
        self.is_dead = False
        self.health = 100
        self.position = pygame.Vector2()
        w, h = pygame.display.get_surface().get_size()
        self.position.xy = w / 2, h / 5
        self.velocity = pygame.Vector2()
        self.rotation = pygame.Vector2()
        self.offset = pygame.Vector2()
        self.drag = 120
        self.gravity_scale = 150
        self.allowy = False
        self.player_sprite = pygame.image.load('data/images/Burger Cat.png').convert_alpha()
        self.player_sprite = pygame.transform.scale(self.player_sprite, (50, 60))
        self.rect = pygame.Rect(self.position.x,self.position.y, 10,10)

    def move(self):
        self.gravity()
        self.air_resistance()
        self.wall_detection()
        self.position.x -= self.velocity.x * dt
        self.position.y -= self.velocity.y * dt
        self.rect = pygame.Rect(self.position.x,self.position.y, 50,60)

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
            self.position.x = 800
        if(self.position.x > 800):
            self.position.x = 0
        if self.allowy == True:
            if(self.position.y < 0):
                self.position.y = 800
            if(self.position.y > 800):
                self.position.y = 0

    def check_state(self):
        global is_menu
        if(self.is_dead == True):
            is_menu = True
            Menu(screen)

    def collision_detection(self, level_builder):  
        self.curr_level = 0

        for i in range(len(level_builder.enemies)):
            other = level_builder.enemies[i]
            for rect in level_builder.enemies[i].rectlist:
                if self.rect.colliderect(rect):
                    self.is_dead = True
        if self.allowy == False:
            if(self.position.y > 850):
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
        screen.blit(self.player_sprite, self.blit_position())

    def blit_position(self):
        return (self.position.x - (self.player_sprite.get_width() / 2), self.position.y - (self.player_sprite.get_height() / 2))

    def add_force(self, vector, magnitude):
        self.velocity.x += vector.x * magnitude
        self.velocity.y += vector.y * magnitude

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

class LevelBuilder:
    def __init__(self):
        self.refills = []
        self.enemies = []
        self.killed = 0
        self.more_enemies = 0

    def spawn_enemies1(self):
        rand = random.randint(1 + self.more_enemies, 3 + self.more_enemies)
        sound = mixer.Sound("data/audio/Spawn.wav")
        sound.set_volume(0.1)
        sound.play()
        for i in range(rand):
            random_pos = random.randint(0, 760)
            position = Vector2()
            position.x = random_pos
            position.y = -30
            enemy = Enemy1(position)
            self.enemies.append(enemy)

    def draw(self, screen):
        for i in range(len(self.refills)):
            self.refills[i].draw(screen) 
        
        enemies_copy = self.enemies.copy()
        for i in range(len(enemies_copy)):
            enemies_copy[i].draw(screen)    
            if(enemies_copy[i].position.y > 850):
                self.enemies.remove(enemies_copy[i])
            
class Game:
    def __init__(self, screen):
        global wave_num
        self.screen = screen
        self.size = None
        self.width = None
        self.height = None
        self.background_color = 240, 240, 240
        self.player = Player()
        self.level_builder = LevelBuilder()
        self.menu = Menu(screen)
        self.clock = pygame.time.Clock()
        wave_num = 1
        self.last_level = 0
        self.level1()

    def level1(self):
        global is_menu
        global wave_num
        self.last_level = 1
        wave_num = 1
        self.menu.new_wave(wave_num)
        self.level_builder.enemies = []
        next_time = time.time()
        elapsed_time = time.time()
        min_time = 5
        max_time = 10
        enemiy_iteration = 0
        timenow = pygame.time.get_ticks()
        timenow1 = pygame.time.get_ticks()  
        self.handle_dt()   
        while ((not is_menu) or (wave_num == 1)):
            self.handle_dt()
            self.clear_screen()
            
            self.level_builder.draw(screen)

            keys = pygame.key.get_pressed()
            thrust_force = 500  # You can adjust this to make flying stronger or weaker

            if keys[pygame.K_w]:
                self.player.add_force(Vector2(0, 1), thrust_force * dt)
            if keys[pygame.K_s]:
                self.player.add_force(Vector2(0, -1), thrust_force * dt)
            if keys[pygame.K_a]:
                self.player.add_force(Vector2(1, 0), thrust_force * dt)
            if keys[pygame.K_d]:
                self.player.add_force(Vector2(-1, 0), thrust_force * dt)

            self.player.move()
            self.player.collision_detection(self.level_builder)
            self.player.check_state()
            self.player.draw(self.screen)

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 10)
            text = self.font.render("Goal: Survive for " + str(30 - abs(int((pygame.time.get_ticks() - timenow)/1000))) + " seconds", False, (0,0,0))
            screen.blit(text, (20,20))

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
                print("YOU WON")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.player.hit()  # like player uses a sword

    
    def clear_screen(self):
        self.screen.fill(self.background_color)

    def handle_dt(self):
        global dt
        dt = self.clock.tick() / 1000

class Menu():
    def __init__(self, screen):
        self.background_color = 240, 240, 240
        self.screen = screen
        self.update()

    def update(self):
        global is_menu
        pygame.font.init()

        while is_menu:
            self.clear_screen()

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 70)
            text = self.font.render("Burger Cat", False, (100,100,100))
            screen.blit(text, (170, 180))

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("By: Akshit & Aryan", False, (0, 0, 139))
            screen.blit(text, (300, 285))

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 50)
            text = self.font.render("Click To Play", False, (200,200,200))
            screen.blit(text, (230,340 + (math.sin(time.time() * 10) * 5)))
            pygame.display.flip()
            self.handle_events()

    def clear_screen(self):
        self.screen.fill(self.background_color)
            
    def handle_events(self):
        global is_menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                is_menu = False
                Game(screen)

    def new_wave(self, wave_num):
        global is_wave
        pygame.font.init()
    
        is_wave = True

        while is_wave:
            self.clear_screen()
            
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 70)
            text = self.font.render("Wave " + str(wave_num), False, (100,100,100))
            screen.blit(text, (250, 200))

            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 50)
            text = self.font.render("Goal: Survive for 30s", False, (200,200,200))
            screen.blit(text, (80,340 + (math.sin(time.time() * 10) * 5)))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    is_wave = False
                    break
            pygame.display.flip()

global instance
instance = None

mixer.init()
mixer.music.load("data/audio/music.mp3")
mixer.music.set_volume(0.01)
mixer.music.play(-1)

while(True):
    if(is_menu):
        instance = Menu(screen)
    else:
        instance = Game(screen)
