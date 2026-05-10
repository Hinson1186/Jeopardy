import pygame
import random

class PowerUp:
    def __init__(self, name, icon_path):
        self.name = name
        try:
            self.image = pygame.image.load(icon_path)
            self.image = pygame.transform.scale(self.image, (60, 60))
        except:
            self.image = pygame.Surface((60, 60))
            self.image.fill((200, 200, 200))
        
        self.is_used = False
        self.rect = pygame.Rect(0, 0, 60, 60)

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        if not self.is_used:
            screen.blit(self.image, self.rect)
            # Draw a border
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        else:
            # Draw faded if used
            temp_surface = self.image.copy()
            temp_surface.set_alpha(100)
            screen.blit(temp_surface, self.rect)

class ExtraTime(PowerUp):
    def __init__(self):
        super().__init__("Extra Time", "assets/images/time-passing.png")

class PointDoubler(PowerUp):
    def __init__(self):
        super().__init__("Point Doubler", "assets/images/coin.png")
class Strike(PowerUp):
    def __init__(self):
        super().__init__("Strike", "assets/images/level-up.png") 