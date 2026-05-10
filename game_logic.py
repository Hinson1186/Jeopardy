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
        self.is_daily_double = False
        
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
        all_clues = []

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
                all_clues.append(clue)
                
        for cat in self.categories:
            self.categories[cat].sort(key=lambda x: x.pt_value)
        
        if all_clues:
            daily_double = random.choice(all_clues)
            daily_double.is_daily_double = True

    def is_complete(self) -> bool:
        for clues in self.categories.values():
            if any(not c.is_answered for c in clues):
                return False
        return True

class JeopardyGameManager:
    def __init__(self):
        self.llm_helper = LLMHelper()
        self.board = Board()
        self.players = []
        self.current_clue = None
        self.game_state = "START_MENU" 
        self.current_wager = 5
        self.max_wager = 1000
        
        self.has_active_game = False
        self.ai_turn_index = 1

    def set_difficulty_and_start(self, difficulty: str):
        self.players = [
            Player("Human"),
            AI_Player("Bot 1", difficulty=difficulty),
            AI_Player("Bot 2", difficulty=difficulty)
        ]
        self.has_active_game = True

    def setup_new_round(self, num_cats=3, clues_per=3):
        self.game_state = "LOADING"
        api_data = self.llm_helper.generate_jeopardy_board(num_categories=num_cats, clues_per_category=clues_per)
        if api_data:
            self.board.populate_from_api(api_data)
            self.game_state = "SHOWING_BOARD"
        else:
            self.game_state = "ERROR"

    def select_clue(self, clue: Clue, player: Player):
        if not clue.is_answered:
            self.current_clue = clue
            self.ai_turn_index = 1
            
            if clue.is_daily_double:
                self.game_state = "WAGERING"
                self.max_wager = max(1000, player.score)
                self.current_wager = 5
            else:
                self.game_state = "SHOWING_CLUE"
    
    def handle_human_answer(self, answer: str) -> bool:
        """Returns True if human is correct, False if wrong."""
        pts = self.current_wager if self.current_clue.is_daily_double else self.current_clue.pt_value
        player = self.players[0]

        if self.current_clue.check_ans(answer):
            player.add_score(pts)
            self.current_clue.is_answered = True
            self.current_clue = None
            self.game_state = "GAME_OVER" if self.board.is_complete() else "SHOWING_BOARD"
            return True
        else:
            player.minus_score(pts)
            # If it's a Daily Double:
            if self.current_clue.is_daily_double:
                self.current_clue.is_answered = True
                self.current_clue = None
                self.game_state = "GAME_OVER" if self.board.is_complete() else "SHOWING_BOARD"
            else:
                self.game_state = "AI_TURN"
            return False

    def handle_ai_steal(self):
        """Processes AI attempt to steal a missed question."""
        ai_player = self.players[self.ai_turn_index]
        pts = self.current_clue.pt_value

        if ai_player.is_correct():
            ai_player.add_score(pts)
            self.current_clue.is_answered = True
            self.current_clue = None
            self.game_state = "GAME_OVER" if self.board.is_complete() else "SHOWING_BOARD"
            return True
        else:
            ai_player.minus_score(pts)
            self.ai_turn_index += 1
            # If both AI wrong, back to the board
            if self.ai_turn_index >= len(self.players):
                self.current_clue.is_answered = True
                self.current_clue = None
                self.game_state = "GAME_OVER" if self.board.is_complete() else "SHOWING_BOARD"
            return False