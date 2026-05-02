from abc import ABC, abstractmethod
import pygame

#Read README.md before editing

class Game(ABC):
    def __init__(self):
        self.players = []

    @abstractmethod
    def start(self):
        pass


class Board:
    def __init__(self):
        self.categories = []

    def get_from_azure(self):
        fetched_clues = []
        for clues in fetched_clues:
            self.categories(clues.category).append(clues)
        pass

class Azure:
    def __init__(self):
        pass

class MainGame(Game):
    def __init__(self):
        super().__init__()
        self.board = Board()

