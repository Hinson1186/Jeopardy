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
        
    def populate_from_api(self, api_data: dict):
        """Take raw JSON dictionary from API and build the board."""
        self.categories.clear()
        for category_data in api_data.get('categories', []):
            cat_name = category_data.get('name')
            self.categories[cat_name] = []
            
            for q_data in category_data.get('questions', []):
                clue = Clue(
                    category=cat_name,
                    question=q_data.get('clue'),
                    correct_answer=q_data.get('correct'),
                    wrong_answers=[c for c in q_data.get('choices', []) if c != q_data.get('correct')],
                    pt_value=q_data.get('value')
                )
                self.categories[cat_name].append(clue)
                
        for cat in self.categories:
            self.categories[cat].sort(key=lambda x: x.pt_value)

    def is_complete(self) -> bool:
        for clues in self.categories.values():
            if any(not c.is_answered for c in clues):
                return False
        return True

class JeopardyGameManager:
    def __init__(self):
        self.llm_helper = LLMHelper()
        self.board = Board()
        self.players = [
            Player("Human"),
            AI_Player("Bot 1", difficulty="easy"),
            AI_Player("Bot 2", difficulty="medium")
        ]
        self.current_clue = None
        self.game_state = "START_MENU" 
        self.current_player_index = 0

    def setup_new_round(self, num_cats=3, clues_per=3):
        self.game_state = "LOADING"
        api_data = self.llm_helper.generate_jeopardy_board(num_categories=num_cats, clues_per_category=clues_per)
        if api_data:
            self.board.populate_from_api(api_data)
            self.game_state = "SHOWING_BOARD"
        else:
            self.game_state = "ERROR"

    def select_clue(self, clue: Clue):
        if not clue.is_answered:
            self.current_clue = clue
            self.game_state = "SHOWING_CLUE"
    
    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def handle_answer(self, player, answer: str):
        if self.current_clue is None: return
        if self.current_clue.check_ans(answer):
            player.add_score(self.current_clue.pt_value)
            self.current_clue.is_answered = True
            self.current_clue = None
            self.game_state = "GAME_OVER" if self.board.is_complete() else "SHOWING_BOARD"
        else:
            player.minus_score(self.current_clue.pt_value)
            # We don't mark as answered yet so other players can guess (we'll implement this logic fully later)
            self.next_turn()