import random

class Actor:
    def __init__(self, name: str, score: int = 0):
        self.name = name
        self.score = score

    def add_score(self, pt: int):
        self.score += pt

    def minus_score(self, pt: int):
        self.score -= pt

class Player(Actor):
    def __init__(self, name: str, score: int = 0):
        super().__init__(name, score)
        self.is_human = True

class AI_Player(Actor):
    def __init__(self, name: str, score: int = 0, difficulty: str = "medium"):
        super().__init__(name, score)
        self.difficulty = difficulty
        self.is_human = False
    
    def get_delay_time(self) -> float:
        delays = {"easy": (2.5, 4.0), "medium": (1.5, 3.0), "hard": (0.5, 1.5)}
        low, high = delays.get(self.difficulty, (1.5, 3.0))
        return random.uniform(low, high)

    def decides_to_answer_correctly(self) -> bool:
        chances = {"easy": 0.5, "medium": 0.75, "hard": 0.9}
        probability = chances.get(self.difficulty, 0.75)
        return random.random() < probability