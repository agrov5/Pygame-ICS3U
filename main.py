'''
ICS3U Pygame Assignment
Names: Akshit Erukulla, Aryan Grover
Date Started: February 18, 2024
Date Completed: April 18, 2025
Course Code: ICS3U
Program Title: Burger Cat Game
Description: This program is a 2D flying game where the player controls a cat that can shoot rockets for flying, passing the levels, and defeating the enemies. The player can also collect refill rockets. The game features various enemy types, special abiltiies, and a scoring system. The player must navigate through levels while avoiding obstacles and defeating different types of enemies, increasing in difficulty, to progress.
'''

# Importing necessary libraries
import pygame, sys, math, random, time, os
from pygame import Vector2, sprite
from pygame import mixer
from pygame.draw import rect

global dt   # Delta time

os.environ['SDL_VIDEO_CENTERED'] = '1'   # Centering the game window on the screen

pygame.init()  # Initialize Pygame

# Get screen dimensions and set up screen accordingly
info = pygame.display.Info() 
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width, screen_height))

# Set window title and icon
pygame.display.set_caption("Burger Cat")
favicon = pygame.image.load("data/images/Burger Cat.png")
pygame.display.set_icon(favicon)

class Explosion:
    """
    A simple explosion to imitate creeper exploding.

    Inputs:
        position (Vector2): Where the explosion starts.
        size (float): The initial radius of the explosion.

    Made by: Akshit and Aryan
    """
    def __init__(self, position, size):
        """
        Initializes the explosion at a given position and size.

        Inputs:
            position (Vector2): Where the explosion starts.
            size (float): The initial radius of the explosion.

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.width = size

    def draw(self, screen):
        """
        Draws the explosion animation with layered color.

        Inputs:
            screen (pygame.Surface): The game display surface.

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        # Draw the 2 circles
        pygame.draw.circle(screen, (220, 0, 0), self.position, self.width)
        pygame.draw.circle(screen, (255, 153, 51), self.position, self.width - (self.width / 2))

    def scale_down(self):
        """
        Gradually shrinks the explosion radius over time.

        Inputs:
            None

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        if self.width > 0:
            self.width -= dt * 80  # Shrink down

class TimeBubble(pygame.sprite.Sprite):
    """
    A circular field that stops player movement and freezes them when entered. Also, protects player from enemies like a shield.

    Input:
        position (Vector2): The center point of the bubble.

    Made by: Akshit and Aryan
    """
    def __init__(self, position):
        """
        Initializes the time bubble at a position.

        Input:
            position (Vector2): The center point of the bubble.

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        pygame.sprite.Sprite.__init__(self)    # we want to be able to kill the sprite after it has shrank down fully
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.width = 60   # starting size
        self.rect = pygame.Rect(self.position.x - self.width, self.position.y - self.width, self.width*2, self.width*2)  # bounding rect
        self.allow = True  

    def draw(self, screen):
        """
        Draws the bubble on screen.

        Inputs:
            screen (pygame.Surface): Game screen to draw on.

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        # Draw the circles
        pygame.draw.circle(screen, (0, 51, 220), self.position, self.width)
        pygame.draw.circle(screen, (200, 200, 255), self.position, self.width - (self.width / 2))
        
        # Recalculate rect because the bubble is shrinking
        self.rect = pygame.Rect(self.position.x - self.width, self.position.y - self.width, self.width*2, self.width*2)

    def scale_down(self):
        """
        Shrinks the size of the time bubble over time.

        Inputs:
            None

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        if self.width > 0:
            self.width -= dt * 8  # Shrink down

    def stop_player(self, player):
        """
        Stops the player at the center of the bubble and resets their movement.

        Inputs:
            player (Player): The player object to freeze.

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        player.position = self.position
        player.velocity.x = 0    # freeze x movement
        player.velocity.y = 0    # freeze y movement
        player.is_dead = False   # invincibility
        self.allow = False  

class RocketBullet:
    """
    A rocket bullet that travels in a set direction until it explodes after a certain distance.

    Inputs:
        position (Vector2): Start position of the rocket.
        angle (float): Launch angle in radians.
        speed (int, optional): How fast the rocket moves (default is 5).

    Made by: Akshit and Aryan
    """
    def __init__(self, position, angle, speed=5):
        """
        Initializes a rocket bullet that moves based on angle.

        Inputs:
            position (Vector2): Start position of the rocket.
            angle (float): Launch angle in radians.
            speed (int, optional): How fast the rocket moves (default is 5).

        Outputs:
            None
        
        Made by: Akshit and Aryan
        """
        self.position = Vector2()
        self.position.x, self.position.y = position.x, position.y
        self.rect = pygame.Rect(self.position.x, self.position.y, 5, 5)
        self.dx = math.cos(angle) * speed    # the x of the "slope"
        self.dy = math.sin(angle) * speed    # the y of the "slope"
        self.distance_traveled = 0
        self.max_distance = 300    # Distance before it "explodes"

    def move(self):
        """
        Moves the rocket in its trajectory and updates its distance.

        Inputs:
            None

        Outputs:
            None
        
        Made by: Akshit and Aryan
        """
        # Follow the "slope" and move in that direction
        self.position.x += self.dx
        self.position.y += self.dy
        self.rect.topleft = (self.position.x, self.position.y)
        self.distance_traveled += math.hypot(self.dx, self.dy)   # update the distance traveled

    def draw(self, screen):
        """
        Draws the bullet as a red rectangle.

        Inputs:
            screen (pygame.Surface): Game display surface.

        Outputs:
            None
        
        Made by: Akshit and Aryan
        """
        pygame.draw.rect(screen, (225, 0, 0), self.rect)

    def has_exploded(self):
        """
        Checks if the rocket has traveled its maximum distance.

        Inputs:
            None
        
        Outputs:
            bool: True if it should explode, False otherwise.

        Made by: Akshit and Aryan
        """
        return self.distance_traveled >= self.max_distance

class Rocket():
    """
    A rocket that manages its fired projectiles, handles explosions, and tracks ammo.

    Inputs:
        position (Vector2): The starting position of the rocket.

    Made By: Akshit and Aryan
    """
    
    def __init__(self, position):
        """
        Initializes a Rocket object at the given position.

        Inputs:
            position (Vector2): The initial location of the rocket.
        
        Outputs:
            None

        Made By: Akshit and Aryan
        """
        self.position = Vector2(position)
        self.rocket_sprite = pygame.image.load('data/images/Rocket.png').convert_alpha()
        self.rocket_sprite = pygame.transform.scale(self.rocket_sprite, (60, 30))

        # Set default values
        self.angle = 0
        self.rockets = []       
        self.explosions = []   
        self.is_flipped = False
        self.rocket_count = 15  # Initial rockets
        self.num_bullets = 5   

        # Load font for showing rocket ammo count
        pygame.font.init()
        self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 300)

        self.refresh_sprite()

        mixer.init()   # setup sounds

    def render_current_ammo(self, screen):
        """
        Displays the current ammo count at the center of the screen.

        Inputs:
            screen (Surface): The game screen where ammo is displayed.

        Outputs:
            None

        Made By: Akshit and Aryan
        """
        text = self.font.render(str(self.rocket_count), False, (200, 200, 200))
        text_width, text_height = self.font.size(str(self.rocket_count))
        screen.blit(text, (screen_width / 2 - text_width / 2, screen_height / 2 - text_height / 2))    # Center the text

    def shoot(self):
        """
        Shoots a rocket toward the current mouse position if ammo is available.

        Inputs:
            None

        Outputs:
            None

        Made By: Akshit and Aryan
        """
        if self.rocket_count > 0:
            # Play shoot sound
            sound = mixer.Sound("data/audio/Firework.mp3")
            sound.set_volume(0.2)
            sound.play()
            
            # Get mouse position and shoot in that direction
            mouse_x, mouse_y = pygame.mouse.get_pos()
            angle = math.atan2(mouse_y - self.position.y, mouse_x - self.position.x)
            rocket = RocketBullet(self.position, angle, speed=5)
            self.rockets.append(rocket)
            self.rocket_count -= 1   # Decrease ammo count
        else:
            sound = mixer.Sound("data/audio/CantShoot.wav")   # out of ammo sound
            sound.set_volume(0.08)
            sound.play()

    def update(self, screen):
        """
        Updates and draws all current rockets and explosions.

        Inputs:
            screen (Surface): The screen to draw the rockets and bullets on.

        Outputs:
            None

        Made By: Akshit and Aryan
        """
        new_rockets = []
        for rocket in self.rockets:
            if rocket.has_exploded():
                self.explode(rocket.position)   # Replace exploded rocket with new bullets
            else:
                rocket.move()
                rocket.draw(screen)
                new_rockets.append(rocket)
        self.rockets = new_rockets

        # Update explosion bullets
        new_explosions = []
        for bullet in self.explosions:
            bullet.move()
            bullet.draw(screen)
            if not bullet.has_exploded():
                new_explosions.append(bullet)
        self.explosions = new_explosions

    def explode(self, position):
        """
        Creates an explosion at a given position by firing bullets in all directions.

        Inputs:
            position (Vector2): Where the explosion should occur.

        Outputs:
            None

        Made By: Akshit and Aryan
        """
        # Play explosion sound
        explosion_sound = mixer.Sound("data/audio/Explosion.mp3")
        explosion_sound.set_volume(0.01)
        explosion_sound.play()

        # Shoot bullets in circular/pentagon pattern
        for i in range(self.num_bullets):
            angle = i * (2 * math.pi / self.num_bullets)
            bullet = RocketBullet(position, angle, speed=5)
            self.explosions.append(bullet)

    def draw(self, screen):
        """
        Draws the rocket on the screen, applying rotation, and updates its state.

        Inputs:
            screen (Surface): The game screen to draw on.

        Outputs:
            None

        Made By: Akshit and Aryan
        """
        rotated_sprite = pygame.transform.rotate(self.rocket_sprite, -math.degrees(self.angle))   # Rotate the sprite so it faces the mouse
        screen.blit(rotated_sprite, (self.position.x - rotated_sprite.get_width() / 2,
                                     self.position.y - rotated_sprite.get_height() / 2))     # Center the sprite
        self.update(screen)

    def refresh_sprite(self):
        """
        Reloads and re-applies transformations to the rocket sprite.

        Inputs:
            None

        Outputs:
            None

        Made By: Akshit and Aryan
        """
        # Reload the sprite because it is "morphed" when rotated
        self.rocket_sprite = pygame.image.load('data/images/Rocket.png').convert_alpha()
        self.rocket_sprite = pygame.transform.scale(self.rocket_sprite, (60, 30))
        self.rocket_sprite = pygame.transform.rotate(self.rocket_sprite, -math.degrees(self.angle))

    def set_position(self, position):
        """
        Sets the rocket's current position.

        Inputs:
            position (Vector2): The new position to set.

        Outputs:
            None

        Made By: Akshit and Aryan
        """
        self.position = position

    def set_rotation(self, degrees):
        """
        Sets the rotation of the rocket sprite manually.

        Inputs:
            degrees (float): Rotation in degrees.

        Outputs:
            None

        Made By: Akshit and Aryan
        """
        self.refresh_sprite()
        self.rocket_sprite = pygame.transform.rotate(self.rocket_sprite, degrees)

    def blit_position(self):
        """
        Calculates the top-left corner for blitting the rocket sprite.

        Inputs:
            None

        Outputs:
            tuple: (x, y) position to blit the rocket sprite.

        Made By: Akshit and Aryan
        """
        return self.position.x - (self.rocket_sprite.get_width() / 2), \
               self.position.y + (self.rocket_sprite.get_height() / 2)

class Player():
    """
    Player class representing the main character controlled by the user. Handles player movement, rocket control, collision detection, and rendering. Player has health, can shoot rockets, and interacts with game elements.
    
    Inputs:
        None

    Made by: Akshit and Aryan
    """
    
    global dt
    def __init__(self):
        """
        Initialize the player with default position, sprites, and game attributes.
        
        Inputs:
            None
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        # Set up default values
        self.is_dead = False
        self.score = 0
        self.health = 100
        self.position = pygame.Vector2()
        w, h = screen_width, screen_height
        self.position.xy = w / 2, h / 5  # Start in top center of screen
        self.velocity = pygame.Vector2()
        self.rotation = pygame.Vector2()
        self.offset = pygame.Vector2()
        self.rocket = Rocket(self.position)
        self.drag = 100
        self.gravity_scale = 250
        self.allowy = False  # Flag to control vertical wrapping
        
        # Load player sprite - our heroic burger cat!
        self.player_sprite = pygame.image.load('data/images/Burger Cat.png').convert_alpha()
        self.player_sprite = pygame.transform.scale(self.player_sprite, (70, 84))
        
        # Load and configure elytra (wing) sprites
        self.elytra_sprite_left = pygame.image.load('data/images/Elytra.png').convert_alpha()
        self.elytra_sprite_left = pygame.transform.scale(self.elytra_sprite_left, (45, 90))
        self.elytra_sprite_right = pygame.transform.flip(self.elytra_sprite_left, True, False)
        self.elytra_sprite_left = pygame.transform.rotate(self.elytra_sprite_left, -30)
        self.elytra_sprite_right = pygame.transform.rotate(self.elytra_sprite_right, 30)
        
        # Set up collision rectangle
        self.rect = self.player_sprite.get_rect()
        self.rect.topleft = (self.position.x, self.position.y)
        self.rocket.set_position(self.position)
        
        # Arrow indicator for when player goes off-screen vertically
        self.arrow_img = pygame.image.load('data/images/Arrow.png').convert_alpha()
        self.arrow_img = pygame.transform.scale(self.arrow_img, (40, 40))

    def move(self):
        """
        Update player position based on physics, forces and screen boundaries.
        
        Applies gravity, air resistance, and handles screen wrapping.
        
        Inputs:
            None
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        self.gravity()
        self.air_resistance()
        self.wall_detection()
        
        # Apply velocity to position
        self.position.x -= self.velocity.x * dt
        self.position.y -= self.velocity.y * dt
        
        # Update collision rectangle
        self.rect = pygame.Rect(self.position.x, self.position.y, 50, 60)
    
    def handle_rocket(self):
        """
        Update rocket position and rotation based on mouse position.
        
        Positions rocket at player location and rotates to face mouse cursor.
        
        Inputs:
            None
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        self.rocket.set_position(self.position)
        
        # Get mouse position and calculate angle to player
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.position.x, mouse_y - self.position.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.rocket.set_rotation(angle)

        # Limit offset values for smoother aiming
        if(self.offset.x > 0):
            self.offset.x = rel_x if rel_x < 4 else 4
        else:
            self.offset.x = rel_x if rel_x > -4 else -4
        if(self.offset.y > 0):
            self.offset.y = rel_y if rel_y < 4 else 4
        else:
            self.offset.y = rel_y if rel_y > -4 else -4

    def gravity(self):
        """
        Apply gravitational force to the player, pulling them downward.
        
        Inputs:
            None
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        self.velocity.y -= self.gravity_scale * dt 

    def air_resistance(self):
        """
        Apply air resistance to gradually slow the player's movement.
        
        Reduces velocity on both axes to simulate air drag.
        
        Inputs:
            None
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        # Vertical air resistance
        if(self.velocity.y > 0):
            self.velocity.y -= self.drag * dt
            
        # Horizontal air resistance (slightly less than vertical)
        if(self.velocity.x > 0):
            self.velocity.x -= (self.drag - 50) * dt
        else:
            self.velocity.x += (self.drag - 50) * dt

    def wall_detection(self):
        """
        Handle screen boundaries by wrapping player position when crossing edges.
        
        Horizontal wrapping is always enabled; vertical wrapping depends on self.allowy.
        
        Inputs:
            None
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        # Horizontal screen wrapping (always enabled)
        if(self.position.x < 0):
            self.position.x = screen_width
        if(self.position.x > screen_width):
            self.position.x = 0
            
        # Vertical screen wrapping (only if allowy is True)
        if self.allowy == True:
            if(self.position.y < 0):
                self.position.y = screen_height-30
            if(self.position.y > screen_height):
                self.position.y = 0

    def get_score(self):
        """
        Return the player's current score.
        
        Inputs:
            None
        
        Outputs:
            int: The player's score
            
        Made by: Akshit and Aryan
        """
        return self.score

    def check_state(self, last_level):
        """
        Check if player is dead and handle game over sequence.
        
        Updates highscore file if needed and shows menu screen.
        
        Inputs:
            last_level (int): The level number player reached
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        global is_menu
        if(self.is_dead == True):
            # Update highscore if current score is higher
            old_highscore_value = open("data/scores/highscore.csv", "r").readline()
            try:
                if(self.score > int(old_highscore_value)):
                    highscore_value = open("data/scores/highscore.csv", "w")
                    highscore_value.write(str(self.score))
                    highscore_value.close()
            except:
                pass
                
            # Return to menu screen
            is_menu = True
            Menu(screen, last_level)

    def collision_detection(self, level_builder):
        """
        Check collisions with refills and enemies, with instant death on enemy contact.
        
        Used in standard game mode where any enemy contact is fatal.
        
        Inputs:
            level_builder (LevelBuilder): Reference to the current level object
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        # Check collisions with refill items
        for i in range(len(level_builder.refills)):
            other = level_builder.refills[i]
            if(self.get_left() < other.get_right() and self.get_right() > other.get_left() and self.get_top() < other.get_bottom() and self.get_bottom() > other.get_top()):
                # Collect refill and increase score
                self.rocket.rocket_count += 1
                level_builder.populate_refill()
                self.score += 1
        
        self.curr_level = 0

        # Check collisions with enemies - instant death mode
        for i in range(len(level_builder.enemies)):
            other = level_builder.enemies[i]
            for rect in level_builder.enemies[i].rectlist:
                if self.rect.colliderect(rect):
                    self.is_dead = True
                    
        # Check if player fell off bottom of screen (when vertical wrapping is disabled)
        if self.allowy == False:
            if(self.position.y > screen_height-10):
                self.is_dead = True
    
    def health_collision_detection(self, level_builder):
        """
        Check collisions with health-based gameplay, where enemy hits reduce health.
        
        Used in alternate game mode where player has health bar instead of instant death.
        
        Inputs:
            level_builder (LevelBuilder): Reference to the current level object
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        # Check collisions with refill items
        for i in range(len(level_builder.refills)):
            other = level_builder.refills[i]
            if(self.get_left() < other.get_right() and self.get_right() > other.get_left() and self.get_top() < other.get_bottom() and self.get_bottom() > other.get_top()):
                self.rocket.rocket_count += 1
                level_builder.populate_refill()
                self.score += 1

        # Check collisions with enemies - health reduction mode
        for i in range(len(level_builder.enemies)):
            other = level_builder.enemies[i]
            for rect in level_builder.enemies[i].rectlist:
                if self.rect.colliderect(rect):
                    self.health -= 10
                    
            # Check collisions with enemy bombs
            for rect in level_builder.enemies[i].bombs:
                if(self.rect.colliderect(rect)):
                    # Reduce health and create explosion
                    self.health -= 10
                    exp_pos = Vector2()
                    exp_pos.x = rect.x 
                    exp_pos.y = rect.y - 20
                    explosion = Explosion(exp_pos, 100)
                    level_builder.enemies[i].explosions.append(explosion)
                    level_builder.enemies[i].bombs.remove(rect)

                    # Apply knockback force from explosion
                    rel_x, rel_y = exp_pos.x - self.position.x, exp_pos.y - self.position.y
                    vector = Vector2()
                    vector.xy = rel_x, rel_y
                    mag = vector.magnitude()
                    vector.xy /= mag
                    self.velocity.y = 0
                    self.velocity.x = 0
                    self.add_force(vector, 400)
                    break
                    
        # Handle falling off screen in non-wrapping mode
        if self.allowy == False:
            if self.position.y > screen_height:
                # Reset position and reduce health instead of instant death
                w, h = pygame.display.get_surface().get_size()
                self.position.xy = w / 2, h / 5
                self.health -= 10
                
        # Check if health reached zero
        if self.health <= 0:
            self.is_dead = True
    
    # --- Bounding box methods ---
    def get_right(self):
        """
        Get the right edge x-coordinate of player's bounding box.
        
        Inputs:
            None
        
        Outputs:
            float: X-coordinate of right edge
            
        Made by: Akshit and Aryan
        """
        return self.position.x + (self.player_sprite.get_width() / 2)

    def get_left(self):
        """
        Get the left edge x-coordinate of player's bounding box.
        
        Inputs:
            None
        
        Outputs:
            float: X-coordinate of left edge
            
        Made by: Akshit and Aryan
        """
        return self.position.x - (self.player_sprite.get_width() / 2)
    
    def get_top(self):
        """
        Get the top edge y-coordinate of player's bounding box.
        
        Inputs:
            None
        
        Outputs:
            float: Y-coordinate of top edge
            
        Made by: Akshit and Aryan
        """
        return self.position.y - (self.player_sprite.get_height() / 2)
    
    def get_bottom(self):
        """
        Get the bottom edge y-coordinate of player's bounding box.
        
        Inputs:
            None
        
        Outputs:
            float: Y-coordinate of bottom edge
            
        Made by: Akshit and Aryan
        """
        return self.position.y + (self.player_sprite.get_height() / 2)

    def draw(self, screen):
        """
        Draw the player character and its components on the screen.
        
        Renders elytra (wings), player sprite, rocket, and off-screen indicator if needed.
        
        Inputs:
            screen: The pygame surface to draw on
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        # Draw elytra (wings) on both sides of the player
        screen.blit(self.elytra_sprite_left, (self.blit_position()[0] - (5 * self.player_sprite.get_width() / 8), self.blit_position()[1]))
        screen.blit(self.elytra_sprite_right, (self.blit_position()[0] + (self.player_sprite.get_width() / 2), self.blit_position()[1]))
        
        # Draw the main player sprite
        screen.blit(self.player_sprite, self.blit_position())
        
        # Draw the player's rocket
        self.rocket.draw(screen)
        
        # Draw off-screen indicator if player is above the visible area
        if self.position.y < 0:
            arrow_x = self.position.x - (self.arrow_img.get_width() / 2)
            arrow_y = 0
            screen.blit(self.arrow_img, (arrow_x, arrow_y))
            
            # Display height information beneath arrow
            font = pygame.font.SysFont(None, 20)
            height_text = font.render(str(int(abs(self.position.y))) + " px", True, (0, 0, 0))
            screen.blit(height_text, (arrow_x, arrow_y + self.arrow_img.get_height()))
        
    def blit_position(self):
        """
        Calculate the correct position to blit the player sprite.
        
        Adjusts position to center the sprite on the player's position.
        
        Inputs:
            None
        
        Outputs:
            tuple: (x, y) coordinates for sprite rendering
            
        Made by: Akshit and Aryan
        """
        return (self.position.x - (self.player_sprite.get_width() / 2), self.position.y - (self.player_sprite.get_height() / 2))

    def shoot(self):
        """
        Shoot the player's rocket, propelling them in the opposite direction.
        
        Uses rocket count as ammo and applies force in the opposite direction of aim.
        
        Inputs:
            None
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        # Return if no rockets available
        if(self.rocket.rocket_count <= 0):
            return
            
        # Calculate direction vector from player to mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.position.x, mouse_y - self.position.y
        vector = Vector2()
        vector.xy = rel_x, rel_y
        
        # Normalize the vector
        mag = vector.magnitude()
        vector.xy /= mag
        
        # Reset current velocity before applying new force
        self.velocity.y = 0
        self.velocity.x = 0
        
        # Apply propulsion force in the direction of the target
        self.add_force(vector, 500)

    def add_force(self, vector, magnitude):
        """
        Add a directional force to the player's velocity.
        
        Inputs:
            vector (Vector2): Direction vector (should be normalized)
            magnitude (float): Strength of the force to apply
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        self.velocity.x += vector.x * magnitude
        self.velocity.y += vector.y * magnitude

class Refill:
    """
    A refill rocket. Players can collect this to move around.
    
    Inputs:
        position (Vector2): The starting (x, y) coordinates for the refill.
    
    Made by: Akshit and Aryan
    """
    def __init__(self, position):
        """
        Initializes a Refill object at the given position.
        
        Inputs:
            position (Vector2): The starting (x, y) coordinates for the refill.
        
        Outputs:
            None

        Made by: Akshit and Aryan
        """
        # Set the position
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y

        # Load the rocket image
        self.rocket_sprite = pygame.image.load('data/images/Rocket.png').convert_alpha()
        self.rocket_sprite = pygame.transform.scale(self.rocket_sprite, (60, 30))
        self.rocket_sprite = pygame.transform.rotate(self.rocket_sprite, 90)

    def draw(self, screen):
        """
        Draws the refill rocket object on the game screen.
        
        Inputs:
            screen (pygame.Surface): The main game screen.
        
        Outputs:
            None
        
        Made by: Akshit and Aryan
        """
        screen.blit(self.rocket_sprite, self.position)

    def get_right(self):
        """
        Returns the right x-coordinate of the refill.

        Inputs:
            None

        Ouputs:
            None
        
        Made by: Akshit and Aryan
        """
        return self.position.x + 30

    def get_left(self):
        """
        Returns the left x-coordinate of the refill.

        Inputs:
            None

        Ouputs:
            None
        
        Made by: Akshit and Aryan
        """
        return self.position.x 
    
    def get_top(self):
        """
        Returns the top y-coordinate of the refill.

        Inputs:
            None

        Ouputs:
            None
        
        Made by: Akshit and Aryan
        """
        return self.position.y
    
    def get_bottom(self):
        """
        Returns the bottom y-coordinate of the refill.

        Inputs:
            None

        Ouputs:
            None
        
        Made by: Akshit and Aryan
        """
        return self.position.y + 40

class Wall:
    """
    A destructible wall. Walls can take a few hits before respawning elsewhere. Are used by the player for cover.
    
    Inputs:
        position (Vector2): The starting (x, y) coordinates for the wall.
        index (int): Unique ID/index for the wall.
    
    Made by: Akshit and Aryan
    """
    def __init__(self, position, index):
        """
        Initializes the wall at a given position with health and sprite.

        Inputs:
            position (Vector2): The starting (x, y) coordinates for the wall.
            index (int): Unique ID/index for the wall.

        Ouputs:
            None
        
        Made by: Akshit and Aryan
        """
        # Set wall position
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y

        # Set up wall size and sprite
        self.rect = pygame.Rect(self.position, (200, 25))
        self.wall_sprite = pygame.image.load('data/images/Bricks.png').convert_alpha()
        self.wall_sprite = pygame.transform.scale(self.wall_sprite, (200, 25))

        self.rectlist = [self.rect]
        self.health = 2  # wall can take two hits
        self.wallindex = index

    def draw(self, screen):
        """
        Draws the wall on the game screen.

        Inputs:
            screen (pygame.Surface): The main game screen.

        Outputs:
            None
        
        Made by: Akshit and Aryan
        """
        #pygame.draw.rect(screen, (0, 0, 0), self.rect)
        screen.blit(self.wall_sprite, self.position)

    def collision_detection(self, enemies):
        """
        Handles collisions between enemy bombs and the wall.

        Inputs:
            enemies (list): List of enemy objects.

        Outputs:
            enemies (list): Updated list of enemies after removing their bombs.

        Made by: Akshit and Aryan
        """
        try:
            for i in range(0, len(enemies)):
                # Check all bombs from each (wave 4) enemy
                bombs = enemies[i].bombs.copy()
                for rect in bombs:
                    if self.rect.colliderect(rect):  # Did enemy hit the wall
                        enemies[i].bombs.remove(rect)   # remove enmmy
                        self.health -= 1   # decrease wall health

                        # If health is 0, then move wall to random spot
                        if self.health <= 0:
                            self.position.x = random.randint(100, screen_width - 100)
                            self.position.y = random.randint(100, screen_height - 100)
                            self.rect.x = self.position.x
                            self.rect.y = self.position.y
                            break
            return enemies   # update the list (since we probably removed some enemies)
        except:
            return enemies
        
class Enemy1:
    """
    Class for Enemy1, a basic falling enemy unit that spawns with different appearances. This enemy falls from the top of the screen with random gravity scales.
    
    Inputs:
        position (Vector2): The initial position from which the enemy spawns.

    Made by: Akshit and Aryan
    """
    
    global dt
    def __init__(self, position):
        """
        Initialize the Enemy1 instance with a random appearance.
        
        Inputs:
            position (Vector2): The initial position from which the enemy spawns.
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        # Set up default values
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.gravity_scale = random.randint(20, 40)  

        self.xOffset = 0
        self.yOffset = 0
         
        rand = random.randint(0, 2)
        self.enemy_sprite = None

        # Select which enemy design to spawn randomly
        if(rand == 0):
            self.enemy_sprite = pygame.image.load('data/images/Potion.png').convert_alpha()
            self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, (40, 60))
            self.xOffset = 40
            self.yOffset = 60
        elif(rand == 1):
            self.enemy_sprite = pygame.image.load('data/images/Guardian.png').convert_alpha()
            self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, (60, 60))
            self.xOffset = 60
            self.yOffset = 60
        else:
            # Rotate the bone sprite because it is on an angle
            self.enemy_sprite = pygame.image.load('data/images/Bone.png').convert_alpha()
            self.enemy_sprite = pygame.transform.rotate(self.enemy_sprite, 45)
            self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, (90, 90))
            self.xOffset = 40
            self.yOffset = 60

            # Center enemy
            self.position.x -= 90
            self.position.y -= 40
        
        # Make rect
        self.recter = pygame.Rect(self.position, (self.xOffset,self.yOffset))
        self.rectlist = [self.recter]
        self.timenow = 0  

    def draw(self, screen):
        """
        Draw the enemy sprite on the screen and apply gravity.
        
        Inputs:
            screen: The game screen to draw on.
        
        Outputs:
            none
            
        Made by: Akshit and Aryan
        """
        #pygame.draw.rect(screen, (255, 0, 0), self.recter)   # to test hitbox
        screen.blit(self.enemy_sprite, self.position)
        self.gravity()

    def gravity(self):
        """
        Apply gravity to make the enemy fall down the screen.
        
        Inputs:
            None

        Outputs:
            None
        
        Made by: Akshit and Aryan
        """
        self.position.y += self.gravity_scale * dt
        self.gravity_scale += 1  # Accelerate fall speed over time
        self.recter = pygame.Rect(self.position, (self.xOffset,self.yOffset))
        self.rectlist = [self.recter]

class Enemy2: 
    """
    Class for Enemy2, a flying enemy that actively tracks and moves toward the player. This enemy moves through the air, rotating itself to face the player's position.
    
    Inputs:
        position (Vector2): The initial position for this enemy.

    Made by: Akshit and Aryan
    """
    
    global dt
    def __init__(self, position):
        """
        Initialize the flying enemy with a parrot sprite.
        
        Inputs:
            position (Vector2): The initial position for this enemy.
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        # Set default values
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.gravity_scale = 0  # No gravity for flying enemies
        self.enemy_sprite = pygame.image.load('data/images/Parrot.png').convert_alpha()
        self.enemy_sprite = pygame.transform.rotate(self.enemy_sprite, 180)
        self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, (40, 50))
        self.xOffset = 40
        self.yOffset = 50
        self.rect = pygame.Rect(self.position, (40,50))
        self.rectlist = [self.rect]
        self.rotated_surface = self.enemy_sprite
        self.timenow = 0  # Timer for future use

    def draw(self, screen):
        """
        Draw the enemy sprite on the screen.
        
        Inputs:
            screen: The game screen to draw on.
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        #pygame.draw.rect(screen, (255, 0, 0), self.rect)  # Uncomment for hitbox visualization
        screen.blit(self.rotated_surface, self.position)
    
    def move(self, targetx, targety):
        """
        Calculate movement vector and rotate sprite to face target position.
        
        Inputs:
            targetx (float): X-coordinate of target position (typically player)
            targety (float): Y-coordinate of target position (typically player)
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        oldCenter = self.position
        
        # Calculate angle to target for rotation
        angle = math.atan2(targety - self.position.y, targetx - self.position.x)
        angle = angle * 180/ math.pi
        rot_image = pygame.transform.rotate(self.enemy_sprite, 360 - angle)
        self.rotated_surface = rot_image
        self.position = oldCenter
        
        # Calculate movement vector toward target
        angle = math.atan2(targety - self.position.y, targetx - self.position.x)
        self.dx = math.cos(angle) * 2
        self.dy = math.sin(angle) * 2
        
        # Move towards it
        self.position.x += self.dx * 0.4
        self.position.y += self.dy * 0.4
        
        # Update rects
        self.rect = pygame.Rect(self.position, (40,50))
        self.rectlist = [self.rect]
    
    def gravity(self):
        """
        Apply gravity effect if needed (minimal for flying enemies).

        Inputs:
            None

        Outputs:
            None
        
        Made by: Akshit and Aryan
        """
        self.position.y += self.gravity_scale * dt

class Enemy3: 
    """
    A laser-based enemy that moves along a specified axis and emits a dangerous beam. This enemy travels back and forth along either the x or y axis while projecting a continuous laser that serves as a hazard to the player.
    
    Inputs:
        position (Vector2): The starting coordinates of the enemy.
        direction (str): The axis along which the enemy moves ("x-axis" or "y-axis").

    Made by: Akshit and Aryan
    """
    
    global dt
    def __init__(self, position, direction):
        """
        Initialize the laser enemy with position and movement direction.
        
        Inputs:
            position (Vector2): The starting coordinates of the enemy.
            direction (str): The axis along which the enemy moves ("x-axis" or "y-axis").
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        # Set up the basic default values
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.speed = 2
        self.position1 = Vector2()  # Position for the second emitter
        self.laserect_pos = Vector2()
        self.gravity_scale = 0
        self.direction = direction 
        self.enemy_sprite = pygame.image.load('data/images/Pickaxe.png').convert_alpha()
        self.enemy_sprite = pygame.transform.rotate(self.enemy_sprite, 45)
        self.enemy_sprite_size = (80, 80)
        self.xOffset = 80
        self.yOffset = 80
        self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, self.enemy_sprite_size)
        self.enemy_sprite1 = pygame.transform.scale(self.enemy_sprite, self.enemy_sprite_size)

        # Set up different configurations based on movement axis
        if self.direction == "y-axis":
            # Horizontal laser which will move vertically
            self.enemy_sprite = pygame.transform.rotate(self.enemy_sprite, 90)
            self.enemy_sprite1 = pygame.transform.rotate(self.enemy_sprite1, 270)
            self.position1.y = position.y
            self.laserect = pygame.Surface((screen_width, 10))
            self.laserect_pos.x = self.position.x + self.enemy_sprite_size[0]
            self.laserect_pos.y = self.position.y + 1*self.enemy_sprite_size[1]//4
            if self.position.x == 0:
                self.position1.x = position.x + screen_width - 1*self.enemy_sprite_size[0]//4
            self.rect2 = pygame.Rect(self.laserect_pos,(screen_width - 2*self.enemy_sprite_size[0], self.enemy_sprite_size[1]))
        elif self.direction == "x-axis":
            # Vertical laser which will move horizontally
            self.enemy_sprite = pygame.transform.rotate(self.enemy_sprite, 0)
            self.enemy_sprite1 = pygame.transform.rotate(self.enemy_sprite1, 180)
            self.position1.x = position.x
            self.laserect = pygame.Surface((10, screen_height))
            self.laserect_pos.x = self.position.x + 1*self.enemy_sprite_size[0]//4
            self.laserect_pos.y = self.position.y + self.enemy_sprite_size[1]
            if self.position.y == 0:
                self.position1.y = position.y + screen_height - 1*self.enemy_sprite_size[1]//2
            self.rect2 = pygame.Rect(self.laserect_pos, (self.enemy_sprite_size[0], screen_height - 20*self.enemy_sprite_size[1]))

        # Make the rects
        self.rect = pygame.Rect(self.position, self.enemy_sprite_size)
        self.rect1 = pygame.Rect(self.position1, self.enemy_sprite_size)
        self.rectlist = [self.rect,self.rect1,self.rect2]
        self.laserect.fill((0, 153, 153))  # Teal
        self.count = 0
        self.traveled_distance = 0
        self.first_spawn = True
        self.timenow = pygame.time.get_ticks()

    def draw(self, screen):
        """
        Draw the laser emitters and the laser beam on the screen.
        
        Inputs:
            screen: The game screen to draw on.
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        if self.first_spawn:
            # Play sound effect on first appearance
            screen.blit(self.laserect, self.laserect_pos)
            screen.blit(self.enemy_sprite, self.position)
            screen.blit(self.enemy_sprite1, self.position1)
            sound = mixer.Sound("data/audio/laser-charge.mp3")
            sound.set_volume(0.1)
            sound.play()
            self.first_spawn = False
        else:
            # Regular drawing during gameplay
            screen.blit(self.laserect, self.laserect_pos)
            screen.blit(self.enemy_sprite, self.position)
            screen.blit(self.enemy_sprite1, self.position1)
    
    def move(self):
        """
        Move the lasers and update the laser position accordingly.
        
        Inputs:
            None

        Outputs:
            None
        
        Made by: Akshit and Aryan
        """
        if self.direction == "y-axis":
            # Wrap aroudn the screen
            if self.position.y <= 100:
                self.count = 0  # Move downward
            elif self.position.y >= screen_height - 100:
                self.count = 1  # Move upward
                
            # Move based on direction
            if self.count == 0:
                self.position.y += self.speed
                self.position1.y += self.speed
            elif self.count == 1:
                self.position.y -= self.speed
                self.position1.y -= self.speed
                
            # Update laser position 
            self.traveled_distance += self.speed
            self.laserect_pos.x = self.position.x + self.enemy_sprite_size[0]
            self.laserect_pos.y = self.position.y + 1*self.enemy_sprite_size[1]//4
            self.rect2.x = self.laserect_pos.x
            self.rect2.y = self.laserect_pos.y
            
        elif self.direction == "x-axis":
            # Wrap aroudn the screen
            if self.position.x <= 100:
                self.count = 0  # Move right
            elif self.position.x >= screen_width - 100:
                self.count = 1  # Move left
                
            # Move based on direction
            if self.count == 0:
                self.position.x += self.speed
                self.position1.x += self.speed
            elif self.count == 1:
                self.position.x -= self.speed
                self.position1.x -= self.speed
                
            # Update laser position 
            self.traveled_distance += self.speed
            self.laserect_pos.x = self.position.x + 1*self.enemy_sprite_size[0]//4
            self.laserect_pos.y = self.position.y + self.enemy_sprite_size[1]
            self.rect2.x = self.laserect_pos.x
            self.rect2.y = self.laserect_pos.y

        # Update rects
        self.rect.x = self.position.x
        self.rect.y = self.position.y
        self.rect1.x = self.position1.x
        self.rect1.y = self.position1.y
    
    def gravity(self):
        """
        Apply gravity effect (not used for laser enemies).

        Inputs:
            None
        
        Outputs:
            None
        
        Made by: Akshit and Aryan
        """
        self.position.y += 0  # No gravity effect

class Enemy4:
    """
    A bomb-dropping enemy that moves horizontally and periodically drops explosive projectiles.
    
    This enemy travels back and forth along the top of the screen, dropping bombs
    that explode when they reach the bottom of the screen.
    
    Made by: Akshit and Aryan
    """
    
    global dt
    def __init__(self, position):
        """
        Initialize the bomb-dropping enemy with creeper sprite.
        
        Inputs:
            position (Vector2): The initial position for this enemy.
        
        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        # Set the default values for the enemy
        self.position = Vector2()
        self.position.x = position.x
        self.position.y = position.y
        self.gravity_scale = 0  # No gravity for this enemy type
        self.enemy_sprite = pygame.image.load('data/images/Creeper.png').convert_alpha()
        self.enemy_sprite = pygame.transform.scale(self.enemy_sprite, (50, 70))
        self.bomb_img = pygame.transform.scale(pygame.image.load('data/images/Egg.png').convert_alpha(), (50, 50))
        self.rect = pygame.Rect(self.position,(50,70))
        self.speed = random.randrange(2, 5)  
        self.interval = random.randrange(1,7)  # Random bomb dropping interval
        self.rectlist = [self.rect]
        self.xOffset = 50
        self.yOffset = 70
        self.bombs = []  
        self.explosions = []  
        self.count = 0
        self.timenow = pygame.time.get_ticks()

    def draw(self, screen):
        """
        Draw the enemy, its bombs, and any active explosions on the screen.
        
        Inputs:
            screen: The game screen to draw on.

        Outputs:
            None
            
        Made by: Akshit and Aryan
        """
        self.move()
        screen.blit(self.enemy_sprite, self.position)

        # Update  explosions
        explosions_copy = self.explosions.copy()
        for i in range(len(explosions_copy)):
            if(explosions_copy[i].width <= 1):
                # Remove expired explosions
                self.rectlist.remove(self.rectlist[i])
                self.explosions.remove(explosions_copy[i])
                break
            explosions_copy[i].scale_down()
            explosions_copy[i].width -= 10
            explosions_copy[i].draw(screen)

        for bomb in self.bombs:
            screen.blit(self.bomb_img, (bomb.x-15,bomb.y))  # Draw bomb
    
    def move(self):
        """
        Move the enemy horizontally and manage bomb dropping.
        
        Inputs:
            None

        Outputs:
            None
        
        Made by: Akshit and Aryan
        """
        # If the enemy is at the left edge, move right; if at the right edge, move left
        if self.position.x <= 0:
            self.count = 0  # Move right
        elif self.position.x >= screen_width - 30:
            self.count = 1  # Move left
            
        # move
        if self.count == 0:
            self.position.x += self.speed
        elif self.count == 1:
            self.position.x -= self.speed
            
        # update rect
        self.rect.x = self.position.x
        self.rect.y = self.position.y
        self.rectlist = [self.rect]
        
        self.drop_bombs()
    
    def drop_bombs(self):
        """
        Handle the periodic dropping of bombs and their movement. Creates new bombs at intervals and moves existing bombs downward.
        
        Inputs:
            None

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        # Create new bomb at set intervals
        if abs(int((pygame.time.get_ticks() - self.timenow)/1000)) >= self.interval:
            bomb = pygame.Rect(self.rect.centerx, self.rect.bottom, 20, 20)
            self.bombs.append(bomb)
            self.timenow = pygame.time.get_ticks()
            
        # Move all active bombs downward
        for bomb in self.bombs:
            bomb.y += 5
        
        # Check for bombs reaching the bottom
        self.reach_end()
    
    def reach_end(self):
        """
        Check for bombs reaching the bottom of the screen and create explosions. Removes bombs that reach the bottom and creates explosion effects.
        
        Inputs:
            None

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        bombs_copy = self.bombs.copy()
        for bomb in bombs_copy:
            if bomb.y >= screen_height:
                # Create an explosion effect where the bomb landed
                exp_pos = Vector2()
                exp_pos.x = bomb.x 
                exp_pos.y = bomb.y - 20
                explosion = Explosion(exp_pos, 100)  # Create explosion object
                self.explosions.append(explosion)
                self.rectlist.append(pygame.Rect(exp_pos.x, exp_pos.y, 100, 100))
                self.bombs.remove(bomb)  # Remove the exploded bomb

class LevelBuilder:
    def __init__(self):
        """
        Initializes the LevelBuilder class. Sets up empty lists for refills and enemies, as well as counters for enemies killed and extra enemies added.

        Input: None  
        Output: None

        Made by: Akshit and Aryan
        """
        # set up empty list for refills and enemies
        self.refills = []
        self.enemies = []

        # set up counters for enemies killed and extra enemies added (for more difficulty)
        self.killed = 0
        self.more_enemies = 0

    def populate_refill(self):
        """
        Spawns two refill objects at random positions.

        Input : None  
        Output: None

        Made by: Akshit and Aryan
        """
        # play reload sound
        sound = mixer.Sound("data/audio/Reload.wav")
        sound.set_volume(0.1)
        sound.play()

        self.refills.clear()  # clear any existing refills
        for i in range(2):
            # spawn a refill at a random spot
            pos = Vector2()
            pos.x = random.randint(100, 700)
            pos.y = random.randint(100, 500)
            refill = Refill(pos)
            self.refills.append(refill)

    def spawn_enemies1(self):
        """
        Spawns 3 to 5 Enemy1 units at the top of the screen. More enmies will spawn based on time passed.

        Input : None  
        Output: None

        Made by: Akshit and Aryan
        """
        # play spawn sound
        sound = mixer.Sound("data/audio/Spawn.wav")
        sound.set_volume(0.1)
        sound.play()
        
        rand = random.randint(3 + self.more_enemies, 5 + self.more_enemies)   # spawn between 3 to 5 enemies + possible more enemies based on time passed
        for i in range(rand):
            # enemies spawn at random x-positions near the top of the screen
            random_pos = random.randint(100, screen_width-100)
            position = Vector2()
            position.x = random_pos
            position.y = screen_height / 12
            enemy = Enemy1(position)
            self.enemies.append(enemy)

    def spawn_enemies2(self):
        """
        Spawns 3 to 5 Enemy2 units from the edges of the screen.

        Input : None  
        Output: None

        Made by: Akshit and Aryan
        """
        # play spawn sound
        sound = mixer.Sound("data/audio/Spawn.wav")
        sound.set_volume(0.1)
        sound.play()
        
        rand = random.randint(3, 5)  # between 3 and 5 enemies
        for i in range(rand):
            # enemies spawn from a random point on one of the screen edges
            options = [
                (0, random.randint(0, screen_height)),  # left edge
                (random.randint(0, screen_width), 0),   # top edge
                (screen_width, random.randint(0, screen_height)),  # right edge
                (random.randint(0, screen_width), screen_height)   # bottom edge
            ]
            choose = random.randint(0, 3)
            position = Vector2()
            position.x = options[choose][0]
            position.y = options[choose][1]
            enemy = Enemy2(position)
            self.enemies.append(enemy)

    def spawn_enemies3(self):
        """
        Spawns 1 to 4 Enemy3 units that move along specific axes based on their spawn corner.

        Input : None  
        Output: None

        Made by: Akshit and Aryan
        """
        # play spawn sound
        sound = mixer.Sound("data/audio/Spawn.wav")
        sound.set_volume(0.1)
        sound.play()

        rand = random.randint(1, 4)  # between 1 and 4 enemies
        for i in range(rand):
            # enemies spawn from the 4 corners
            options = [(0, 0), (0, 0), (0, screen_height), (screen_width, 0)]
            choose = random.randint(0, 3)
            position = Vector2()
            position.x = options[choose][0]
            position.y = options[choose][1]

            # choose movement axis based on spawn corner
            match choose:
                case 0:
                    enemy = Enemy3(position, "y-axis")
                case 1:
                    enemy = Enemy3(position, "x-axis")
                case 2:
                    enemy = Enemy3(position, "y-axis")
                case 3:
                    enemy = Enemy3(position, "x-axis")
                    
            self.enemies.append(enemy)

    def spawn_enemies4(self):
        """
        Spawns 4 to 5 Enemy4 units from the top of the screen.

        Input : None  
        Output: None

        Made by: Akshit and Aryan
        """
        # play spawn sound
        sound = mixer.Sound("data/audio/Spawn.wav")
        sound.set_volume(0.1)
        sound.play()

        rand = random.randint(4, 5)    # four or five enemies
        for i in range(rand):
            # simple vertical fall enemies from random x-positions
            random_pos = random.randint(0, screen_width)
            position = Vector2()
            position.x = random_pos
            position.y = 0
            enemy = Enemy4(position)
            self.enemies.append(enemy)

    def collision_detection(self, rocket, obj_type, wavenum):
        """
        Detects collisions between rockets and enemies (and bombs in wave 4), and removes hit enemies while counting the eliminated ones.

        :
            rocket: Object - the projectile object
            obj_type: str - "rocket" (in the future, will add more types)
            wavenum: int - the current wave number
        
        Output: None

        Made by: Akshit and Aryan
        """
        enemies_copy = self.enemies.copy()   # copy to avoid modifying the list while iterating

        for i in range(0, len(enemies_copy)):
            # wave 2: remove enemy if hit by rocket
            if wavenum == 2:
                if obj_type == "rocket":
                    if enemies_copy[i].rectlist[0].colliderect(rocket.rect):
                        self.killed += 1   # increment killed enemies
                        self.enemies.remove(enemies_copy[i])
                        break
            # wave 4: trigger explosion if bomb hits rocket
            elif wavenum == 4:
                for rect in self.enemies[i].bombs:
                    if rect.colliderect(rocket.rect):
                        exp_pos = Vector2()
                        exp_pos.x = rect.x 
                        exp_pos.y = rect.y - 20
                        explosion = Explosion(exp_pos, 100)
                        self.enemies[i].explosions.append(explosion)
                        self.enemies[i].bombs.remove(rect)
                        break

    def draw(self, screen):
        """
        Draws all refill objects and enemies to the screen. Also removes enemies that fall off screen.

        :
            screen: Surface - the game screen where objects are drawn
        
        Output: None

        Made by: Akshit and Aryan
        """
        # draw refills (used for reloading or powerups)
        for i in range(len(self.refills)):
            self.refills[i].draw(screen)

        enemies_copy = self.enemies.copy()  # copy to avoid modifying the list while iterating

        # draw enemies and remove those that went off-screen
        for i in range(len(enemies_copy)):
            enemies_copy[i].draw(screen)
            if enemies_copy[i].position.y > 850:
                self.enemies.remove(enemies_copy[i])
            
class Game:
    """
    Class for the game and waves.

    Inputs:
        screen (pygame.Surface): The Pygame screen to render the menu on.
        last_level (int): The last level the player reached.

    Made by: Akshit and Aryan
    """

    def __init__(self, screen, last_level):
        """
        Initializes the Game class with screen and starting level.
        
        Inputs:
            screen (pygame.Surface): The surface where all graphics are rendered.
            last_level (int): The last level player was on or should start from.

        Outputs:
            None (goes to next level and resets all the values)
        
        Made by: Akshit and Aryan
        """
        global wave_num

        # Set the screen, background color, score, timer, and the game objects
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

        wave_num = 1   # First wave
        
        #self.bg_img = pygame.image.load('data/images/end_bg.jpg').convert_alpha()
        #self.bg_img = pygame.transform.scale(self.bg_img, (screen_width, screen_height))

        # load cloud images 
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
            # Randomly set the clouds' positions and type
            cloud_img = random.choice([self.cloud1, self.cloud2, self.cloud3, self.cloud4])
            self.clouds.append([cloud_img, random.randint(0, screen_width), screen_height - random.randint(100, 200), random.uniform(0.1, 0.5)])

        self.go_to_last_level()  # go to the last level

    def go_to_last_level(self):
        """
        Sends the player to the last saved level. This function makes it easy for players to navigate through levels and save progress.

        Inputs:
            None

        Outputs:
            None (just calls the level functions).
        
        Made by: Akshit and Aryan
        """
        ([self.level1, self.level2, self.level3, self.level4])[self.last_level - 1]()

    def level1(self):
        """
        Runs level 1 of the game where the player must survive for 30 seconds. Enemies spawn over time and try to attack.
        
        Inputs:
            None (uses internal state and global variables)

        Outputs:
            None (updates game state, possibly transitions to next level).

        Made by: Akshit and Aryan
        """
        global is_menu
        global wave_num
        self.last_level = 1
        wave_num = 1

        # Reset the level
        self.menu.new_wave(wave_num)
        self.level_builder.populate_refill()
        self.level_builder.enemies = []

        # Valeus for the enemy spawn timers
        next_time = time.time()
        elapsed_time = time.time()
        min_time = 5
        max_time = 10
        enemiy_iteration = 0

        # Start the timers
        timenow = pygame.time.get_ticks()
        timenow1 = pygame.time.get_ticks()

        self.handle_dt()  # reset deltatime

        while ((not is_menu) or (wave_num == 1)):
            self.handle_dt()
            self.clear_screen()
            self.player.rocket.render_current_ammo(screen)

            self.level_builder.draw(screen)  # draw enemies and refill rockets

            # Update and draw player
            self.player.move()
            self.player.handle_rocket()
            self.player.collision_detection(self.level_builder)
            self.player.check_state(self.last_level)
            self.player.draw(self.screen)

            self.score = self.player.get_score()   # update score

            # Goal text
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("Goal: Survive for " + str(30 - abs(int((pygame.time.get_ticks() - timenow)/1000))) + " seconds", False, (0, 0, 0))
            text_width, text_height = self.font.size("Goal: Survive for " + str(30 - abs(int((pygame.time.get_ticks() - timenow)/1000))) + " seconds")
            screen.blit(text, (screen_width/10 - text_width/2, 0))

            # Tip text
            text = self.font.render("Note: Don't fall out of the screen!", False, (0, 0, 0))
            screen.blit(text, (screen_width/70, screen_height - 40))

            pygame.display.flip()   # update screen
            self.handle_events()

            # Spawn enemies if time has passed
            elapsed_time = time.time()
            if(elapsed_time > next_time):
                next_time = elapsed_time + random.randint(min_time, max_time)
                self.level_builder.spawn_enemies1()
                enemiy_iteration += 1
                if(enemiy_iteration > 5 and min_time > 1):
                    min_time -= 1
                    max_time -= 1
                    enemiy_iteration = 0

            # Spawn more enemies as tiem goes on
            if abs(int((pygame.time.get_ticks() - timenow1)/1000)) >= 10:
                self.level_builder.more_enemies += 2
                timenow1 = pygame.time.get_ticks()

            # If player survived for 30s, then go to next level
            if abs(int((pygame.time.get_ticks() - timenow)/1000)) >= 30:   
                self.player.rocket.rocket_count += 5
                self.last_level = 2
                self.go_to_last_level()

    def level2(self):
        """
        Runs level 2 of the game where the player must kill 10 enemies. A time bubble slows things down.
        
        Inputs:
            None (uses internal state and global variables)

        Outputs:
            None (updates game state, possibly transitions to next level)

        Made by: Akshit and Aryan
        """
        global is_menu, wave_num
        self.last_level = 2
        wave_num = 2

        # Player setup and reset
        w, h = pygame.display.get_surface().get_size()
        self.player.position.xy = w / 2, h / 5
        self.menu.new_wave(wave_num)
        self.player.is_dead = False
        self.level_builder.enemies = []
        self.level_builder.populate_refill()
        self.level_builder.killed = 0

        # Timers for enemy spawning
        next_time = time.time()
        elapsed_time = time.time()
        min_time, max_time = 5, 10
        enemy_iteration = 0

        # Time bubble timers and spawn
        eject_cooldown = 0 
        stuck_in_timebubble = False
        tb_pos = Vector2(random.randint(10, screen_width-10), random.randint(10, screen_height-10))
        tb = TimeBubble(tb_pos)
        tb.allow = True
        
        # Start game timer
        timenow = pygame.time.get_ticks() 
        self.handle_dt()  # reset deltatime

        while not is_menu or wave_num == 2:
            self.handle_dt()
            self.clear_screen()
            self.player.rocket.render_current_ammo(screen)
            
            # move enemies only if they're not touching the timebubble (essentially making the timebuble a shield as well)
            enemies_copy = self.level_builder.enemies.copy()
            for i in range(len(enemies_copy) - 1):
                if not enemies_copy[i].rectlist[0].colliderect(tb.rect):
                    self.level_builder.enemies[i].move(self.player.position.x, self.player.position.y)
            
            self.level_builder.draw(screen)  # draw the enemies and refill rockets

            # Player movement and collisions (unless stuck)
            if tb.allow:
                self.player.move()
                self.player.collision_detection(self.level_builder)
            self.player.handle_rocket()    # player can still shoot rockets
            self.player.check_state(self.last_level)

            # Check collisions between rockets and enemies
            for rocket in self.player.rocket.rockets:
                self.level_builder.collision_detection(rocket, "rocket", 2)
            for bullet in self.player.rocket.explosions:
                self.level_builder.collision_detection(bullet, "rocket", 2)

            # respawn time bubble at a random position every 15 sec
            if abs((pygame.time.get_ticks() - timenow) / 1000) >= 12:
                tb_pos = Vector2(random.randint(20, screen_width-20), random.randint(20, screen_height-20))
                tb = TimeBubble(tb_pos)
                timenow = pygame.time.get_ticks()

            # check if time bubble is active
            if tb.width <= 1:
                tb.allow = True
                stuck_in_timebubble = False
                tb.kill()  # kill timebubble if it has shrank down
            else:
                tb.scale_down()
                if tb.rect.colliderect(self.player.rect):   # if timebubble touches the player
                    if pygame.time.get_ticks() > eject_cooldown:    # if player didnt eject already, then put player in timebubble
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

            self.player.draw(self.screen)  # draw player
            self.score = self.player.get_score()  # update score

            # Escape text when player is in timebubble
            if stuck_in_timebubble:
                font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
                escape_text = font.render("Press E to escape!", True, (0, 0, 0))
                text_width, text_height = font.size("Press E to escape!")
                screen.blit(escape_text, (screen_width/70, screen_height - 3*text_height/2))

            # Goal text
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("Goal: Kill " + str(10 - self.level_builder.killed) + " enemies", False, (0, 0, 0))
            text_width, text_height = self.font.size("Goal: Kill " + str(10 - self.level_builder.killed) + " enemies")
            screen.blit(text, (screen_width/70, text_height/2))
            
            pygame.display.flip()   # update screen
            self.handle_events()

            # if E key is pressed, then eject the player
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e] and stuck_in_timebubble and eject_cooldown == 0:
                stuck_in_timebubble = False
                eject_cooldown = pygame.time.get_ticks() + 3000  
                tb.allow = True 
            
            # Spawn enmeies based on time passed
            elapsed_time = time.time()
            if elapsed_time > next_time:
                next_time = elapsed_time + random.randint(min_time, max_time)
                self.level_builder.spawn_enemies2()
                enemy_iteration += 1
                if enemy_iteration > 5 and min_time > 1:
                    min_time -= 1
                    max_time -= 1
                    enemy_iteration = 0
            
            # If player has killed 10 enemies, then go to next level
            if self.level_builder.killed >= 10:
                self.player.rocket.rocket_count += 5
                self.last_level = 3
                self.go_to_last_level()

    def level3(self):
        """
        Runs level 3 of the game where the player must dodge enemies (lasers) for 30 seconds.
        
        Inputs:
            None (uses internal state and global variables)

        Outputs:
            None (updates game state, possibly transitions to next level)

        Made by: Akshit and Aryan
        """
        global is_menu
        global wave_num
        self.last_level = 3
        wave_num = 3
        self.menu.new_wave(wave_num)

        # Clean the screen for a new wave
        self.level_builder.enemies = []
        self.level_builder.populate_refill()
        self.level_builder.killed = 0

        # Set up enemy spawn timers
        next_time = time.time() + 3
        elapsed_time = time.time()
        min_time = 5
        max_time = 10
        enemiy_iteration = 0

        # Center the player
        w, h = pygame.display.get_surface().get_size()
        self.player.position.xy = w / 2, h / 5
        self.player.draw(screen)
        self.player.allowy = True

        # Start the timer
        timenow = pygame.time.get_ticks()
        self.handle_dt()  # Reset delta time

        while ((not is_menu) or (wave_num == 3)):
            self.handle_dt()
            self.clear_screen()

            self.player.rocket.render_current_ammo(screen)

            # Move all enemies and remove ones that went too far
            enemies_copy = self.level_builder.enemies.copy()
            for i in range(0, len(enemies_copy)):
                enemies_copy[i].move()
                if enemies_copy[i].traveled_distance > 500 - (len(enemies_copy) - 1) * 100:
                    self.level_builder.enemies.remove(enemies_copy[i])

            # Update and draw enemies and player
            self.level_builder.draw(screen)
            self.player.move()
            self.player.handle_rocket()
            self.player.collision_detection(self.level_builder)
            self.player.check_state(self.last_level)
            self.player.draw(self.screen)

            self.score = self.player.get_score()   # update score

            # Goal text
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("Goal: Avoid the lasers for " + str(30 - abs(int((pygame.time.get_ticks() - timenow)/1000))) + " seconds", False, (0, 0, 0))
            screen.blit(text, (screen_width/70, 20))

            # Tip text
            text = self.font.render("Tip: You can fall through the bottom now!", False, (0, 0, 0))
            screen.blit(text, (screen_width/70, screen_height - 40))

            pygame.display.flip()   # update screen
            self.handle_events()

            # Spawn enemies if some time has passed
            elapsed_time = time.time()
            if(elapsed_time > next_time):
                next_time = elapsed_time + random.randint(min_time, max_time)
                self.level_builder.spawn_enemies3()
                enemiy_iteration += 1
                if(enemiy_iteration > 5 and min_time > 1):
                    min_time -= 1
                    max_time -= 1
                    enemiy_iteration = 0

            # If player has survived for 30 seconds, then go to next level
            if abs(int((pygame.time.get_ticks() - timenow)/1000)) >= 30:
                self.player.rocket.rocket_count += 5
                self.last_level = 4
                self.go_to_last_level()


    def level4(self):
        """
        Runs level 4 of the game where the player must survive enemies for 60 seconds by avoding the eggs/bombs and using the walls for cover.

        Inputs:
            None

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        global is_menu
        global wave_num
        self.last_level = 4
        wave_num = 4
        self.menu.new_wave(wave_num)

        # Reset state for the new wave
        self.level_builder.populate_refill()
        self.level_builder.enemies = []
        self.player.health = 100   # New feature: player health
        self.player.rocket.rocket_count += 10

        # Make 2 wall objects with random positions
        wallist = []
        wallist.clear()   # just to be safe
        for i in range(0, 2):
            position = Vector2()
            position.xy = random.randint(100, screen_width - 100), random.randint(100, screen_height - 100)
            wallist.append(Wall(position, i))

        # Enemy spawning time values
        next_time = time.time()
        elapsed_time = time.time()
        min_time = 5
        max_time = 10
        enemiy_iteration = 0

        timenow = pygame.time.get_ticks()
        self.handle_dt()  # Reset movement frame delta again

        while ((not is_menu) or (wave_num == 4)):
            self.handle_dt()
            self.clear_screen()
            self.player.rocket.render_current_ammo(screen)

            # update and draw enemies and player
            self.level_builder.draw(screen)
            self.player.move()
            self.player.handle_rocket()
            self.player.health_collision_detection(self.level_builder)
            self.player.check_state(self.last_level)
            self.player.draw(self.screen)

            # Cehck if the enemies have collided with the rockets and bullets
            for rocket in self.player.rocket.rockets:
                self.level_builder.collision_detection(rocket, "rocket", 4)
            for bullet in self.player.rocket.explosions:
                self.level_builder.collision_detection(bullet, "rocket", 4)

            # Draw and detect enemy collisions with walls
            if self.level_builder.enemies:
                for i in range(0, len(wallist)):
                    wallist[i].draw(screen)
                    out = wallist[i].collision_detection(self.level_builder.enemies)
                    if out:
                        self.level_builder.enemies = out

            self.score = self.player.get_score()  # update score

            # Goal text
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("Goal: Survive for " + str(60 - abs(int((pygame.time.get_ticks() - timenow)/1000))) + " seconds", False, (0, 0, 0))
            screen.blit(text, (screen_width/10 - text.get_width()/2, 0))

            # Tip text
            tip = self.font.render("Tip: Hide under a wall! Players can pass through them, but the mobs can't!", False, (0, 0, 0))
            screen.blit(tip, (screen_width - tip.get_width() - 20, screen_height - 30))

            # Display the health bar (red for health, black for background)
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

            # Spawn enemies if enough time has passed
            elapsed_time = time.time()
            if(elapsed_time > next_time):
                next_time = elapsed_time + random.randint(min_time, max_time)
                self.level_builder.spawn_enemies4()
                enemiy_iteration += 1
                if(enemiy_iteration > 5 and min_time > 1):
                    min_time -= 1
                    max_time -= 1
                    enemiy_iteration = 0

            # If player has survived for 60 seconds, move to next level
            if abs(int((pygame.time.get_ticks() - timenow)/1000)) >= 60:
                self.player.rocket.rocket_count += 5
                #self.last_level = 5
                #self.go_to_last_level()
                self.last_level = 1
                is_menu = True
                Menu(screen, 5)
                
    def handle_events(self):
        """
        Handles all incoming Pygame events, including quitting and shooting.

        Inputs:
            None

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:   # if escape key is pressed, exit 
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:   # if mouse is clicked, shoot
                self.player.shoot()
                self.player.rocket.shoot()


    def clear_screen(self):
        """
        Clears the screen and moves clouds.

        Inputs:
            None

        Outputs:
            None

        Made by: Akshit and Aryan
        """
        self.screen.fill(self.background_color)
        #screen.blit(self.bg_img, (0, 0))

        # Move the clouds across the screen
        for cloud in self.clouds:
            surf, x, y, speed = cloud
            x += speed
            if x > screen_width:   # if cloud goes off-screen, move it to the other side
                x = -surf.get_width()
                y = random.randint(screen_height - 180, screen_height - 120)
                speed = random.uniform(0.3, 1.0)
            cloud[1], cloud[2], cloud[3] = x, y, speed
            screen.blit(surf, (x, y))


    def handle_dt(self):
        """
        Updates the global delta time (dt) variable.

        Inputs:
            None

        Outputs:
            None (modifies global dt)

        Made by: Akshit and Aryan
        """
        global dt
        dt = self.clock.tick() / 1000

class Menu():
    """
    Class for the game's main menu and wave intro screens.

    Inputs:
        screen (pygame.Surface): The Pygame screen to render the menu on.
        last_level (int): The last level the player reached.

    Made by: Akshit and Aryan
    """
    
    def __init__(self, screen, last_level):
        """
        Initializes the menu object with screen and level data.

        Inputs:
            screen (pygame.Surface): The game screen to render on.
            last_level (int): The most recently completed level.
        
        Made by: Akshit and Aryan
        """
        self.background_color = 240, 240, 240
        self.screen = screen
        #self.bg_img = pygame.image.load('data/images/end_bg.jpg').convert_alpha()
        #self.bg_img = pygame.transform.scale(self.bg_img, (screen_width, screen_height))
        if last_level == 5:
            self.last_level = 1
            self.game_done()
        else:
            self.last_level = last_level
        self.update()

    def update(self):
        """
        Continuously updates and displays the main menu screen. User can click to start the game.

        Inputs:
            None
        
        Outputs:
            None 

        Made by: Akshit and Aryan
        """
        global is_menu
        pygame.font.init()
    
        # Play a sound when the menu is opened
        sound = mixer.Sound("data/audio/Error.wav")
        sound.set_volume(0.05)
        sound.play()

        while is_menu:
            self.clear_screen()

            # Logo and title
            logo = pygame.image.load('data/images/Burger Cat.png').convert_alpha()
            logo = pygame.transform.scale(logo, (120, 140))
            screen.blit(logo, (screen_width/2 - 100, screen_height/2 - 250))

            # Main title text
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 70)
            text = self.font.render("Burger Cat", False, (100, 100, 100))
            text_width, text_height = self.font.size("Burger Cat")
            screen.blit(text, (screen_width/2 - text_width/2, screen_height/2 - 120))

            # Credits
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("By: Akshit E. & Aryan G.", False, (0, 0, 139))
            text_width, text_height = self.font.size("By: Akshit E. & Aryan G.")
            screen.blit(text, (screen_width/2 - text_width/2, screen_height/2 + 80))

            # Click To Play text with a hover effect
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 50)
            text = self.font.render("Click To Play", False, (200, 200, 200))
            text_width, text_height = self.font.size("Click To Play")
            screen.blit(text, (screen_width/2 - text_width/2, 400 + (math.sin(time.time() * 10) * 5)))

            # Display high score from file
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 30)
            highscore_value = open("data/scores/highscore.csv", "r").readline()
            highscore = self.font.render("Highscore: " + str(highscore_value), False, (180, 180, 180))
            text_width, text_height = self.font.size("Highscore: " + str(highscore_value))
            screen.blit(highscore, (screen_width/2 - text_width/2, 460 + (math.sin(time.time() * 10) * 5)))

            pygame.display.flip()   # update the screen
            self.handle_events()

    def clear_screen(self):
        """
        Fills the screen with the background color. 

        Inputs:
            None
        
        Outputs:
            None 

        Made by: Akshit and Aryan
        """
        self.screen.fill(self.background_color)
        #screen.blit(self.bg_img, (0, 0))
            
    def handle_events(self):
        """
        Handles user input events while the menu is active. Exits or starts the game on key press or mouse click.

        Inputs:
            None
        
        Outputs:
            None 

        Made by: Akshit and Aryan
        """
        global is_menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:   # if escape key is pressed, exit 
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Exit the menu and start the actual game
                is_menu = False
                Game(screen, self.last_level)

    def new_wave(self, wave_num):
        """
        Displays a new wave intro screen with the goal instructions.

        Inputs:
            wave_num (int): The number of the current wave being started.

        Output: 
            None

        Made by: Akshit and Aryan
        """
        global is_wave
        pygame.font.init()
    
        is_wave = True
        goals = ["Survive for 30s", "Kill 10 Enemies.", "Avoid the Lasers", "Survive for 60s", "Kill the Boss"]  # goal text for each wave

        while is_wave:
            self.clear_screen()
            
            # Show which wave you're on
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 70)
            text = self.font.render("Wave " + str(wave_num), False, (100, 100, 100))
            text_width, text_height = self.font.size("Wave " + str(wave_num))
            screen.blit(text, (screen_width/2 - text_width/2, screen_height/2 - 20))

            # Show the challenge/goal for that wave
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 50)
            text = self.font.render("Goal: " + goals[wave_num - 1], False, (200, 200, 200))
            text_width, text_height = self.font.size("Goal: " + goals[wave_num - 1])
            screen.blit(text, (screen_width/2 - text_width/2, 320 + (math.sin(time.time() * 10) * 5)))

            # Check if user clicked to start the wave
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    is_wave = False
                    break

            pygame.display.flip()   # update the screen
    
    def game_done(self):
        """
        Continuously updates and displays the game done screen. User can click to start the game.

        Inputs:
            None
        
        Outputs:
            None 

        Made by: Akshit and Aryan
        """
        global is_menu
        pygame.font.init()
    
        # Play a sound when the menu is opened
        sound = mixer.Sound("data/audio/Celebration.mp3")
        sound.set_volume(0.05)
        sound.play()

        while is_menu:
            self.clear_screen()

            # Logo and title
            logo = pygame.image.load('data/images/Burger Cat.png').convert_alpha()
            logo = pygame.transform.scale(logo, (120, 140))
            screen.blit(logo, (screen_width/2 - 100, screen_height/2 - 250))

            # Main title text
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 70)
            text = self.font.render("Burger Cat", False, (100, 100, 100))
            text_width, text_height = self.font.size("Burger Cat")
            screen.blit(text, (screen_width/2 - text_width/2, screen_height/2 - 120))

            # Credits
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 20)
            text = self.font.render("By: Akshit E. & Aryan G.", False, (0, 0, 139))
            text_width, text_height = self.font.size("By: Akshit E. & Aryan G.")
            screen.blit(text, (screen_width/2 - text_width/2, screen_height/2 + 80))

            # Click To Play text with a hover effect
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 50)
            text = self.font.render("Great Job! Play Again?", False, (200, 200, 200))
            text_width, text_height = self.font.size("Great Job! Play Again?")
            screen.blit(text, (screen_width/2 - text_width/2, 400 + (math.sin(time.time() * 10) * 5)))

            # Display high score from file
            self.font = pygame.font.Font("data/fonts/Montserrat-ExtraBold.ttf", 30)
            highscore_value = open("data/scores/highscore.csv", "r").readline()
            highscore = self.font.render("Highscore: " + str(highscore_value), False, (180, 180, 180))
            text_width, text_height = self.font.size("Highscore: " + str(highscore_value))
            screen.blit(highscore, (screen_width/2 - text_width/2, 460 + (math.sin(time.time() * 10) * 5)))

            pygame.display.flip()   # update the screen
            self.handle_events()

# Play background music 
mixer.init()
mixer.music.load("data/audio/Music.mp3")
mixer.music.set_volume(0.1)
mixer.music.play(-1)

# Game loop start conditions
global instance
instance = None
is_menu = True
last_level = 1   # Start from the first level

# Main control loop
while(True):
    if(is_menu):
        instance = Menu(screen, last_level)   # Go to menu screen
    else:
        instance = Game(screen, last_level)   # Go to game screen
        last_level = instance.last_level