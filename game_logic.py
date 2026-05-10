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
        self.image_path = None
        
        self.mc_options = [correct_answer] + wrong_answers
        random.shuffle(self.mc_options)
    
    def check_ans(self, ans: str) -> bool:
        return ans == self.correct_answer

class Board:
    def __init__(self):
        self.categories: dict[str, list[Clue]] = {}
        
    def populate_from_api(self, api_data: dict, llm_helper: LLMHelper, num_daily_doubles: int = 1):
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
                
                # 10% chance to generate an image for this clue
                if random.random() < 0.10:
                    img_prompt = f"A clear, simple visual representation of {clue.correct_answer} without any text."
                    clue.image_path = llm_helper.generate_image_for_clue(img_prompt)

                self.categories[cat_name].append(clue)
                all_clues.append(clue)
                
        for cat in self.categories:
            self.categories[cat].sort(key=lambda x: x.pt_value)

        if all_clues:
            picks = min(num_daily_doubles, len(all_clues))
            dd_clues = random.sample(all_clues, picks)
            for dd in dd_clues:
                dd.is_daily_double = True

    def is_complete(self) -> bool:
        for clues in self.categories.values():
            if any(not c.is_answered for c in clues):
                return False
        return True

class JeopardyGameManager:
    def __init__(self):
        self.llm_helper = LLMHelper()
        self.board = Board()
        
        self.players = [Player("Human")]
        self.ai_counter = 1
        
        self.current_clue = None
        self.game_state = "START_MENU" 
        self.round_num = 1
        
        self.current_wager = 5
        self.max_wager = 1000
        
        self.active_player_index = 0

    def add_ai_player(self, difficulty: str):
        """Adds an AI player to the lobby."""
        if len(self.players) < 3:
            self.players.append(AI_Player(f"Bot {self.ai_counter}", difficulty=difficulty))
            self.ai_counter += 1

    def remove_ai_player(self):
        if len(self.players) > 1:
            self.players.pop()
            self.ai_counter -= 1

    def advance_round(self):
        self.round_num += 1
        
        # Double Jeopardy
        if self.round_num == 2:
            self.game_state = "LOADING"
            api_data = self.llm_helper.generate_jeopardy_board(num_categories=6, clues_per_category=5, round_num=2)
            if api_data:
                self.board.populate_from_api(api_data, self.llm_helper, num_daily_doubles=2)
                self.game_state = "SHOWING_BOARD"
            else:
                self.game_state = "ERROR"
                
        # Final Jeopardy
        elif self.round_num == 3:
            self.players = [p for p in self.players if p.score > 0]
            
            if len(self.players) == 0:
                self.game_state = "GAME_OVER"
                return
                
            self.game_state = "LOADING"
            api_data = self.llm_helper.generate_jeopardy_board(num_categories=1, clues_per_category=1, round_num=3)
            if api_data:
                self.board.populate_from_api(api_data, self.llm_helper, num_daily_doubles=0)
                
                cat_name = list(self.board.categories.keys())[0]
                self.current_clue = self.board.categories[cat_name][0]
                
                for p in self.players:
                    if not p.is_human:
                        p.final_wager = p.determine_wager(p.score)
                        
                self.active_player_index = 0
                if self.players[0].is_human:
                    self.max_wager = self.players[0].score
                    self.current_wager = 0
                    self.game_state = "FINAL_WAGERING"
                else:
                    self.game_state = "SHOWING_CLUE"
            else:
                self.game_state = "ERROR"

    def select_clue(self, clue: Clue, player_index: int):
        if not clue.is_answered:
            self.current_clue = clue
            self.active_player_index = player_index
            
            if clue.is_daily_double:
                self.game_state = "WAGERING"
                board_max = 1000 if self.round_num == 1 else 2000
                self.max_wager = max(board_max, self.players[player_index].score)
                self.current_wager = 5
            else:
                self.game_state = "SHOWING_CLUE"

    def handle_answer(self, player_index: int, answer: str) -> bool:
        if self.current_clue is None: return False
        
        player = self.players[player_index]
        
        if self.round_num == 3:
            pts = self.current_wager if player.is_human else getattr(player, 'final_wager', 0)
        elif self.current_clue.is_daily_double:
            pts = self.current_wager if player.is_human else player.determine_wager(self.max_wager)
        else:
            pts = self.current_clue.pt_value

        if self.current_clue.check_ans(answer):
            player.add_score(pts)
            
            if self.round_num == 3:
                self.game_state = "GAME_OVER"
            else:
                self.current_clue.is_answered = True
                self.current_clue = None
                self.check_board_complete()
            return True
        else:
            player.minus_score(pts)
            
            if self.round_num == 3:
                self.game_state = "GAME_OVER"
            elif self.current_clue.is_daily_double:
                self.current_clue.is_answered = True
                self.current_clue = None
                self.check_board_complete()
            return False

    def check_board_complete(self):
        if self.board.is_complete():
            self.advance_round()
        else:
            self.game_state = "SHOWING_BOARD"