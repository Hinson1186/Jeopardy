# Testing code
name = ["a", "b", "c"]
print(f"{name} is here")
print(Hi)

# I added Player class only, still thinking what to do, here is referencing from ppt p.39
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
