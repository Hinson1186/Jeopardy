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
            temp_surface.set_alpha(100) # Fade out when used
            screen.blit(temp_surface, self.rect)

    def apply(self, **kwargs):
        """This will be overridden by subclasses."""
        if self.is_used: return False
        self.is_used = True
        return True

class ExtraTime(PowerUp):
    def apply(self, timer_data):
        if super().apply():
            # timer_data is a dictionary we pass from main.py
            timer_data['limit'] += 5000 
            print("Power-up: 5 seconds added!")
            return True
        return False

class PointDoubler(PowerUp):
    def apply(self, game_manager):
        if super().apply():
            game_manager.current_clue.pt_value *= 2
            print("Power-up: Points Doubled!")
            return True
        return False

class Strike(PowerUp):
    def apply(self, clue_obj):
        if super().apply():
            # Returns the index of a wrong answer to hide
            correct = clue_obj.correct_answer
            wrongs = [i for i, opt in enumerate(clue_obj.mc_options) if opt != correct]
            return random.choice(wrongs) if wrongs else -1
        return -1