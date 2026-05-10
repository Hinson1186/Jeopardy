import pygame
import os

BLUE = (6, 12, 233)
YELLOW = (255, 204, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)

ASSET_FILES = {
    "background": "background.jpg",
    "clue_board": "clue_board.jpg",
    "contestant": "contestant.jpg",
    "LED_blue": "LED_blue.jpg",
    "LED_red": "LED_red.jpg",
    "stage": "stage.jpg",
    "theme_background": "theme_background.jpg",
    "loading": "loading.png", 
    
    "money": "money.png",
    "rank": "rank.png",
    "time_passing": "time_passing.png",
    "tournament": "tournament.png",
    "coin": "coin.png",
    "diamonds": "diamonds.png",
    "heart": "heart.png",
    "level_up": "level_up.png",
}

class BoxSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, clue):
        super().__init__()
        self.clue = clue
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.font = pygame.font.SysFont('Arial', 32, bold=True)
        self.update_appearance()

    def update_appearance(self):
        self.image.fill((6, 12, 233, 230))
        pygame.draw.rect(self.image, YELLOW, self.image.get_rect(), 3)
        if not self.clue.is_answered:
            text = self.font.render(f"${self.clue.pt_value}", True, YELLOW)
            text_rect = text.get_rect(center=(self.rect.width//2, self.rect.height//2))
            shadow = self.font.render(f"${self.clue.pt_value}", True, BLACK)
            self.image.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
            self.image.blit(text, text_rect)

class UIManager:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont('Arial', 80, bold=True)
        self.font_large = pygame.font.SysFont('Arial', 36, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 20, bold=True)
        self.box_group = pygame.sprite.Group()
        self.bgs = {}
        self.icons = {}
        self.load_all_assets()

    def load_all_assets(self):
        background_keys = ["background", "clue_board", "contestant", "LED_blue", "LED_red", "stage", "theme_background", "loading"]
        for key, filename in ASSET_FILES.items():
            path = os.path.join("assets", "images", filename)
            is_bg = key in background_keys
            target_size = (1280, 720) if is_bg else (40, 40)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                if is_bg: self.bgs[key] = pygame.transform.scale(img, target_size)
                else: self.icons[key] = pygame.transform.scale(img, target_size)
            else:
                surf = pygame.Surface(target_size)
                surf.fill(BLACK)
                if is_bg: self.bgs[key] = surf
                else: self.icons[key] = surf

    def draw_text(self, text, font, color, x, y, center=True):
        shadow = font.render(text, True, BLACK)
        s_rect = shadow.get_rect()
        if center: s_rect.center = (x + 2, y + 2)
        else: s_rect.topleft = (x + 2, y + 2)
        self.screen.blit(shadow, s_rect)
        img = font.render(text, True, color)
        rect = img.get_rect()
        if center: rect.center = (x, y)
        else: rect.topleft = (x, y)
        self.screen.blit(img, rect)

    def draw_text_wrapped(self, surface, text, color, rect, font):
        words = text.split(' ')
        lines, current_line = [], []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= rect.width: current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        total_height = len(lines) * font.get_linesize()
        y_offset = rect.y + (rect.height - total_height) // 2
        for line in lines:
            rendered = font.render(line, True, color)
            shadow = font.render(line, True, BLACK)
            line_rect = rendered.get_rect(centerx=rect.centerx, y=y_offset)
            surface.blit(shadow, (line_rect.x + 2, line_rect.y + 2))
            surface.blit(rendered, line_rect)
            y_offset += font.get_linesize()

    def build_board_sprites(self, board):
        self.box_group.empty()
        col_width, row_height = 190, 85
        start_x, start_y = 40, 130
        for col_idx, (i, clues) in enumerate(board.categories.items()):
            for row_idx, clue in enumerate(clues):
                x = start_x + (col_idx * (col_width + 10))
                y = start_y + (row_idx * (row_height + 10))
                self.box_group.add(BoxSprite(x, y, col_width, row_height, clue))

    def draw_menu(self):
        self.screen.blit(self.bgs["LED_red"], (0, 0))
        self.draw_text("JEOPARDY!", self.font_title, YELLOW, 640, 200)
        pygame.draw.rect(self.screen, BLUE, (440, 400, 400, 60), border_radius=10)
        pygame.draw.rect(self.screen, WHITE, (440, 400, 400, 60), 3, border_radius=10)
        self.draw_text("ENTER LOBBY", self.font_large, WHITE, 640, 430)

    def draw_lobby(self, game_manager):
        self.screen.blit(self.bgs["LED_blue"], (0, 0))
        self.draw_text("WAITING ROOM", self.font_title, YELLOW, 640, 100)
        y_start = 200
        for i, p in enumerate(game_manager.players):
            self.draw_text(f"Player {i+1}: {p.name}", self.font_large, WHITE, 640, y_start + (i * 40))
        if len(game_manager.players) < 3:
            diffs = [("Add EASY Bot", 400, (0, 200, 0)), ("Add MED Bot", 480, (200, 150, 0)), ("Add HARD Bot", 560, (200, 0, 0))]
            for text, y, color in diffs:
                pygame.draw.rect(self.screen, color, (300, y, 300, 50), border_radius=10)
                pygame.draw.rect(self.screen, WHITE, (300, y, 300, 50), 3, border_radius=10)
                self.draw_text(text, self.font_small, WHITE, 450, y + 25)
        pygame.draw.rect(self.screen, BLUE, (700, 450, 300, 80), border_radius=10)
        pygame.draw.rect(self.screen, WHITE, (700, 450, 300, 80), 3, border_radius=10)
        self.draw_text("START GAME", self.font_large, YELLOW, 850, 490)

    def draw_board_screen(self, game_manager):
        self.screen.blit(self.bgs["stage"], (0, 0))
        self.screen.blit(self.icons["money"], (40, 20))
        score_text = "   |   ".join([f"{p.name}: ${p.score}" for p in game_manager.players])
        self.draw_text(score_text, self.font_large, WHITE, 90, 20, center=False)
        pygame.draw.rect(self.screen, RED, (1100, 20, 150, 40), border_radius=8)
        self.draw_text("LEAVE", self.font_small, WHITE, 1175, 40)
        for col_idx, cat_name in enumerate(game_manager.board.categories.keys()):
            x = 40 + (col_idx * 200)
            pygame.draw.rect(self.screen, (0, 0, 100, 200), (x, 70, 190, 50))
            pygame.draw.rect(self.screen, YELLOW, (x, 70, 190, 50), 2)
            cat_font = self.font_small if len(cat_name) <= 12 else pygame.font.SysFont('Arial', 14, bold=True)
            self.draw_text(cat_name.upper(), cat_font, WHITE, x + 95, 95)
        self.box_group.draw(self.screen)

    def draw_wagering_screen(self, game_manager, is_final=False):
        self.screen.blit(self.bgs["theme_background"], (0, 0))
        title = "FINAL JEOPARDY!" if is_final else "DAILY DOUBLE!"
        self.draw_text(title, self.font_title, YELLOW, 640, 150)
        self.draw_text(f"Max Wager: ${game_manager.max_wager}", self.font_large, WHITE, 640, 250)
        self.draw_text(f"Your Wager: ${game_manager.current_wager}", self.font_title, WHITE, 640, 350)
        pygame.draw.rect(self.screen, WHITE, (340, 450, 600, 20), border_radius=10)
        min_w = 0 if is_final else 5
        percent = (game_manager.current_wager - min_w) / max(1, (game_manager.max_wager - min_w))
        handle_x = 340 + int(percent * 600)
        pygame.draw.circle(self.screen, YELLOW, (handle_x, 460), 20)
        pygame.draw.circle(self.screen, BLACK, (handle_x, 460), 20, 3)
        pygame.draw.rect(self.screen, BLUE, (540, 550, 200, 60), border_radius=15)
        pygame.draw.rect(self.screen, YELLOW, (540, 550, 200, 60), 3, border_radius=15)
        self.draw_text("WAGER!", self.font_large, YELLOW, 640, 580)

    def draw_clue_screen(self, clue):
        self.screen.blit(self.bgs["background"], (0, 0))
        self.draw_text(f"CATEGORY: {clue.category.upper()} - ${clue.pt_value}", self.font_large, YELLOW, 640, 50)
        if clue.image_path and os.path.exists(clue.image_path):
            img = pygame.image.load(clue.image_path).convert_alpha()
            img = pygame.transform.scale(img, (300, 300))
            self.screen.blit(img, (80, 100))
            clue_rect = pygame.Rect(400, 100, 750, 250)
        else: clue_rect = pygame.Rect(140, 100, 1000, 250)
        self.draw_text_wrapped(self.screen, clue.question, WHITE, clue_rect, self.font_large)
        for i, option in enumerate(clue.mc_options):
            rect = pygame.Rect(340, 400 + (i * 70), 600, 50)
            surf = pygame.Surface((600, 50), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 180))
            self.screen.blit(surf, rect.topleft)
            pygame.draw.rect(self.screen, WHITE, rect, 2)
            self.draw_text(f"{i+1}. {option}", self.font_small, WHITE, rect.centerx, rect.centery)

    def draw_loading_screen(self, round_num):
        self.screen.blit(self.bgs["loading"], (0, 0))
        rd_text = "Round 1" if round_num == 1 else ("Double Jeopardy" if round_num == 2 else "Final Jeopardy")
        self.draw_text(f"Generating {rd_text} Board...", self.font_large, YELLOW, 640, 600)
        self.draw_text("Please wait ~15s (AI Image Generation takes time)", self.font_small, WHITE, 640, 650)
        pygame.display.flip() 