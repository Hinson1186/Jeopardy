import pygame
import sys

# --- Configuration & Colors ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
BLUE = (6, 12, 233)
YELLOW = (255, 204, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# --- Object Oriented Classes ---

class Question:
    def __init__(self, category, clue, options, answer, points):
        self.category = category
        self.clue = clue
        self.options = options
        self.answer = answer
        self.points = points
        self.answered = False

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0

class JeopardyGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.font_large = pygame.font.SysFont('Arial', 50, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 24)
        self.player = Player("Human")
        self.state = "BOARD"  # States: BOARD, QUESTION, RESULT
        self.current_q = None
        
        # Build a 3x3 Board
        self.categories = ["Python", "General", "AI"]
        self.board = []
        for col in range(3):
            column_questions = []
            for row in range(3):
                points = (row + 1) * 200
                q = Question(self.categories[col], 
                             f"Clue for {self.categories[col]} ${points}",
                             ["Option A", "Option B", "Option C"], 
                             "Option A", points)
                column_questions.append(q)
            self.board.append(column_questions)

    def draw_text(self, text, font, color, x, y, center=True):
        img = font.render(text, True, color)
        rect = img.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        self.screen.blit(img, rect)

    def draw_board(self):
        self.screen.fill(BLUE)
        self.draw_text(f"Score: ${self.player.score}", self.font_small, YELLOW, 50, 20, False)
        
        for col in range(3):
            # Draw Categories
            self.draw_text(self.categories[col], self.font_small, WHITE, 166 + (col * 333), 80)
            for row in range(3):
                q = self.board[col][row]
                rect = pygame.Rect(col * 333 + 10, row * 150 + 120, 313, 130)
                
                if not q.answered:
                    pygame.draw.rect(self.screen, BLUE, rect)
                    pygame.draw.rect(self.screen, YELLOW, rect, 3)
                    self.draw_text(f"${q.points}", self.font_large, YELLOW, rect.centerx, rect.centery)
                else:
                    pygame.draw.rect(self.screen, GRAY, rect)

    def draw_question(self):
        self.screen.fill(BLUE)
        self.draw_text(self.current_q.clue, self.font_small, WHITE, SCREEN_WIDTH//2, 200)
        
        for i, option in enumerate(self.current_q.options):
            rect = pygame.Rect(250, 350 + (i * 80), 500, 60)
            pygame.draw.rect(self.screen, WHITE, rect, 2)
            self.draw_text(f"{i+1}. {option}", self.font_small, WHITE, rect.centerx, rect.centery)

    def handle_click(self, pos):
        if self.state == "BOARD":
            col = pos[0] // 333
            row = (pos[1] - 120) // 150
            if 0 <= col < 3 and 0 <= row < 3:
                q = self.board[col][row]
                if not q.answered:
                    self.current_q = q
                    self.state = "QUESTION"

        elif self.state == "QUESTION":
            # Very simple: Top button is always right for this prototype
            if 350 <= pos[1] <= 410: # Top option
                self.player.score += self.current_q.points
            else:
                self.player.score -= self.current_q.points
            
            self.current_q.answered = True
            self.state = "BOARD"

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(pygame.mouse.get_pos())

            if self.state == "BOARD":
                self.draw_board()
            elif self.state == "QUESTION":
                self.draw_question()

            pygame.display.flip()

if __name__ == "__main__":
    game = JeopardyGame()
    game.run() 