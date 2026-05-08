import random
from players import Player, AI_Player

class Clue:
    def __init__(self, category: str, question: str, correct_answer: str, wrong_answers: list, pt_value: int):
        self.category = category
        self.question = question
        self.correct_answer = correct_answer
        self.pt_value = pt_value
        self.is_answered = False

        self.mc_options = [correct_answer] + wrong_answers
        random.shuffle(self.mc_options)
    
    def check_ans(self, ans: str) -> bool:
        return ans == self.correct_answer


class Board:
    def __init__(self):
        self.categories = {}

    def load_clues(self, fetched_clues: list):
        """Sort Clue objects into dictionary."""
        for clue in fetched_clues:
            if clue.category not in self.categories:
                self.categories[clue.category] = []
            self.categories[clue.category].append(clue)
        
        for cat in self.categories:
            self.categories[cat].sort(key=lambda x: x.pt_value)


class JeopardyGameManager:
    """Game logic."""
    def __init__(self):
        self.board = Board()
        self.players = [
            Player("Human"),
            AI_Player("Bot 1", difficulty="easy"),
            AI_Player("Bot 2", difficulty="medium")
        ]
        self.state = "BOARD"
        self.current_clue = None
        self.current_round = "Jeopardy"

    def setup_fake_board(self):
        """Temporary function to test the game before the API is ready."""
        fake_clues = []
        categories = ["Python", "General", "AI"]
        for cat in categories:
            for i in range(1, 4):
                val = i * 200
                clue = Clue(cat, f"What is {cat} for {val}?", "Correct", ["Wrong 1", "Wrong 2"], val)
                fake_clues.append(clue)
        self.board.load_clues(fake_clues)