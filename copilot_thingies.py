# 1) In your Player class, load and scale an arrow image (e.g. in __init__):
self.arrow_img = pygame.image.load('data/images/arrow.png').convert_alpha()
self.arrow_img = pygame.transform.scale(self.arrow_img, (40, 40))

# 2) In your Player draw method or wherever you handle drawing:
def draw(self, screen):
    self.rocket.draw(screen)
    screen.blit(self.elytra_sprite, (
        self.blit_position()[0] - (self.player_sprite.get_width() / 4),
        self.blit_position()[1]
    ))
    screen.blit(self.player_sprite, self.blit_position())

    # 3) If the player is above the screen, show an arrow at the top center:
    if self.position.y < 0:
        arrow_x = self.position.x - (self.arrow_img.get_width() / 2)
        arrow_y = 0
        screen.blit(self.arrow_img, (arrow_x, arrow_y))
