import pygame
import random

class PowerUp:
    def __init__(self, name, surface):
        self.name = name
        self.image = pygame.transform.scale(surface, (60, 60))
        self.is_used = False
        self.rect = pygame.Rect(0, 0, 60, 60)

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        if not self.is_used:
            screen.blit(self.image, self.rect)
            pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        else:
            temp_surface = self.image.copy()
            temp_surface.set_alpha(100)
            screen.blit(temp_surface, self.rect)

class ExtraTime(PowerUp):
    def __init__(self, surface):
        super().__init__("Extra Time", surface)

class PointDoubler(PowerUp):
    def __init__(self, surface):
        super().__init__("Point Doubler", surface)

class Strike(PowerUp):
    def __init__(self, surface):
        super().__init__("Strike", surface)