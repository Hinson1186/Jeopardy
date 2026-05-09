import random
import time

class Actor:
    def __init__(self, name: str):
        self.name = name
        self.score = 0

    def add_score(self, pt: int):
        self.score += pt

    def minus_score(self, pt: int):
        self.score -= pt


class Player(Actor):
    def __init__(self, name: str, score: int = 0):
        super().__init__(name)
        self.score = score
        self.is_human = True


class AI_Player(Actor):
    def __init__(self, name: str, score: int = 0, difficulty: str = "medium"):
        super().__init__(name)
        self.score = score
        self.difficulty = difficulty
        self.is_human = False
    
    def delay_time(self) -> int:
        """Fake AI thinking time."""
        if self.difficulty == "easy":
            return random.uniform(2.5, 4.0)
        elif self.difficulty == "medium":
            return random.uniform(1.5, 3.0)
        else: 
            return random.uniform(0.5, 1.5)

    def is_correct(self) -> bool:
        """AI get the answer right based on probability."""
        correct_chance = {"easy": 0.5, "medium": 0.75, "hard": 0.9}
        probability = correct_chance.get(self.difficulty, 0.75)
        return random.random() < probability