from abc import ABC, abstractmethod
import random
import pygame

# --- 1. Actor Hierarchy (Slide 39) ---
class Actor:
    def __init__(self, name: str):
        self.name = name
        self.score = 0

    def update_score(self, pt: int):
        """Adds or subtracts points based on the value passed."""
        self.score += pt

class Player(Actor):
    def __init__(self, name: str, is_human: bool = True):
        super().__init__(name)
        self.is_human = is_human

class AI_Player(Player):
    def __init__(self, name: str):
        # AI Players are just Players where is_human = False
        super().__init__(name, is_human=False)
        self.difficulty = 0.7  # Probability of getting a correct answer (Slide 47)

# --- 2. Clue Data Class (Slide 37) ---
class Clue:
    def __init__(self, category: str, question: str, correct_answer: str, wrong_answers: list, pt_value: int):
        self.category = category
        self.question = question
        self.correct_answer = correct_answer
        self.pt_value = pt_value
        self.is_answered = False
        
        # Combine and shuffle options so the correct one isn't always first
        self.mc_options = [correct_answer] + wrong_answers
        random.shuffle(self.mc_options)
    
    def check_ans(self, selected_ans: str) -> bool:
        return selected_ans == self.correct_answer

# --- 3. Board Manager (Slide 37/43) ---
class Board:
    def __init__(self):
        # A dictionary is best: { "CategoryName": [List of 5 Clue objects] }
        self.categories = {} 

    def organize_clues(self, fetched_clues: list):
        """Sorts a flat list of Clue objects into the categories dictionary."""
        for clue in fetched_clues:
            if clue.category not in self.categories:
                self.categories[clue.category] = []
            self.categories[clue.category].append(clue)
        
        # Optional: Sort clues in each category by point value
        for cat in self.categories:
            self.categories[cat].sort(key=lambda x: x.pt_value)

# --- 4. Abstract Game Class (Slide 40) ---
class Game(ABC):
    def __init__(self):
        self.players = []
        self.is_running = True

    @abstractmethod
    def start_round(self):
        """All games must be able to start a round."""
        pass

# --- 5. Main Game Implementation ---
class MainGame(Game):
    def __init__(self):
        super().__init__()
        self.board = Board()
        self.current_round = "Jeopardy" # Round tracking (Slide 46)
        
        # Initialize Players
        self.players.append(Player("User"))
        self.players.append(AI_Player("AI Bot 1"))
        self.players.append(AI_Player("AI Bot 2"))

    def start_round(self):
        print(f"Starting {self.current_round} Round!")
        # Logic to fetch from Azure would go here

# --- 6. Azure Integration Stub (Slide 52) ---
class AzureConnector:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_jeopardy_data(self, category: str):
        # This will contain your OpenAI/Azure API call logic
        pass