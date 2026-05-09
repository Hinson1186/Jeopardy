import random
from players import Player, AI_Player
from api import LLMHelper
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
        self.categories: dict[str, list[Clue]] = {}
        
    def load_clues(self, fetched_clues: list):
        """Sort Clue objects into dictionary."""
        self.categories.clear()
        for clue in fetched_clues:
            if clue.category not in self.categories:
                self.categories[clue.category] = []
            self.categories[clue.category].append(clue)
        
        for cat in self.categories:
            self.categories[cat].sort(key=lambda x: x.pt_value)

    def populate_from_api(self, api_data: dict):
        """ Takes the raw JSON dictionary from the API and builds the board. """
        self.categories.clear() # to clear old data
        
        for category_data in api_data.get('categories', []):
            category_name = category_data.get('name')
            self.categories[category_name] = []
            
            for q_data in api_data.get('questions', []):
                correct_answer = q_data.get('correct')
                all_choices = q_data.get('choices', [])
                wrong_answers = [choice for choice in all_choices if choice != correct_answer]
                clue = Clue(
                    category=category_name,
                    question=q_data.get('clue'),
                    correct_answer=correct_answer,
                    wrong_answers=wrong_answers,
                    pt_value=q_data.get('value')
                )
                self.categories[category_name].append(clue)

class JeopardyGameManager:
    """Game logic."""
    def __init__(self):
        self.llm_helper = LLMHelper(key_filename="api_key.txt")
        self.board = Board()
        self.players = [
            Player("Human"),
            AI_Player("Bot 1", difficulty="easy"),
            AI_Player("Bot 2", difficulty="medium")
        ]
        self.current_clue = None
        self.current_round = "Jeopardy"
        self.game_state = "START_MENU" # need more states for better coding , such as "START_MENU", "SHOWING_BOARD", "SHOWING_CLUE"
        self.current_player_index = 0

    def setup_new_round(self):
        self.game_state = "LOADING"
        api_data = self.llm_helper.generate_jeopardy_board(num_categories=3, clues_per_category=3)
        if api_data:
            self.board.populate_from_api(api_data)
            self.game_state = "SHOWING_BOARD"
        else:
            self.game_state = "ERROR"

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
        self.game_state = "SHOWING_BOARD"
    
    def select_clue(self, clue: Clue):
        """Clue selection logic."""
        if not clue.is_answered:
            self.current_clue = clue
            self.game_state = "SHOWING_CLUE"
    
    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def handle_answer(self, player: Player, answer: str):
        """Processes answer, updates score, and marks clue as played."""
        if self.current_clue is None:
            return
        if self.current_clue.check_ans(answer):
            player.add_score(self.current_clue.pt_value)
        else:
            player.minus_score(self.current_clue.pt_value)
        
        self.current_clue.is_answered = True
        self.current_clue = None
        self.game_state = "SHOWING_BOARD"
        self.next_turn()