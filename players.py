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
    
    def get_reaction_time(self) -> float:
        """Fake AI reaction time."""
        reaction_speeds = {"easy": (5.0, 8.0), "medium": (3.0, 5.0), "hard": (1.0, 3.0)}
        low, high = reaction_speeds.get(self.difficulty, (3.0, 5.0))
        return random.uniform(low, high)

    def decides_to_answer_correctly(self) -> bool:
        """AI gets the answer right based on probability."""
        chances = {"easy": 0.5, "medium": 0.75, "hard": 0.9}
        probability = chances.get(self.difficulty, 0.75)
        return random.random() < probability
        
    def determine_wager(self, max_wager: int) -> int:
        """AI logic for Daily Doubles and Final Jeopardy"""
        aggression = {"easy": 0.2, "medium": 0.5, "hard": 0.8}
        pct = aggression.get(self.difficulty, 0.5)
        
        # Add some randomness to their bet
        bet = int(max_wager * random.uniform(pct * 0.5, pct * 1.2))
        bet = max(5, min(bet, max_wager))
        return round(bet / 5) * 5