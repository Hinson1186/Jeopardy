import abc as abc
import pygame as pg

#Read README.md before editing
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


class AI_Player(Player):
    def __init__(self, name: str, score: int = 0):
        super().__init__(name, score)
        self.score = score

class Game(abc.ABC):
    def __init__(self):
        self.players = []

    @abc.abstractmethod
    def start(self):
        pass

class Clue:
    def __init__(self, category: str, question: str, correct_answer: str, wrong_answers: list, pt_value: int):
        self.category = category
        self.question = question
        self.correct_answer = correct_answer
        self.pt_value = pt_value

        self.mc_options = [correct_answer] + wrong_answers
    
    def check_ans(self, ans: str) -> bool:
        return ans == self.correct_answer
