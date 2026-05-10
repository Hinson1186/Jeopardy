import pygame
import os

# Colors
BLUE = (6, 12, 233)
YELLOW = (255, 204, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ==========================================
# PUT YOUR EXACT FILE NAMES HERE
# ==========================================
ASSET_FILES = {
    "background": "background.jpg",
    "clue_board": "clue_board.jpg",
    "contestant": "contestant.jpg",
    "LED_blue": "LED_blue.jpg",
    "LED_red": "LED_red.jpg",
    "stage": "stage.jpg",
    "theme_background": "theme_background.jpg",
    
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
    """TV Version 6x5 Board Boxes"""
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
        """Helper to load an image."""
        background_keys = [
            "background", "clue_board", "contestant", "LED_blue", 
            "LED_red", "stage", "theme_background"
        ]

        for key, filename in ASSET_FILES.items():
            path = os.path.join("assets", "images", filename)
            
            is_bg = key in background_keys
            target_size = (1280, 720) if is_bg else (40, 40)

            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                scaled_img = pygame.transform.scale(img, target_size)
                
                if is_bg:
                    self.bgs[key] = scaled_img
                else:
                    self.icons[key] = scaled_img
            else:
                print(f"Warning: Missing image {path}. Using black box fallback.")
                surf = pygame.Surface(target_size)
                surf.fill(BLACK)
                if is_bg:
                    self.bgs[key] = surf
                else:
                    self.icons[key] = surf

    def draw_text(self, text, font, color, x, y, center=True):
        # Shadow
        shadow = font.render(text, True, BLACK)
        s_rect = shadow.get_rect()
        if center: s_rect.center = (x + 2, y + 2)
        else: s_rect.topleft = (x + 2, y + 2)
        self.screen.blit(shadow, s_rect)

        # Main text
        img = font.render(text, True, color)
        rect = img.get_rect()
        if center: rect.center = (x, y)
        else: rect.topleft = (x, y)
        self.screen.blit(img, rect)

    def draw_text_wrapped(self, surface, text, color, rect, font):
        """Wrap text to fit inside the screen window."""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= rect.width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        # Center the block of text
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
        
        col_width = 190
        row_height = 85
        start_x = 40
        start_y = 130

        for col_idx, (cat_name, clues) in enumerate(board.categories.items()):
            for row_idx, clue in enumerate(clues):
                x = start_x + (col_idx * (col_width + 10))
                y = start_y + (row_idx * (row_height + 10))
                box = BoxSprite(x, y, col_width, row_height, clue)
                self.box_group.add(box)

    def draw_board_screen(self, game_manager):
        # TV studio background
        self.screen.blit(self.bgs["stage"], (0, 0))
        
        # Player scores
        self.screen.blit(self.icons["money"], (40, 20))
        score_text = f"P1: ${game_manager.players[0].score}   |   AI 1: ${game_manager.players[1].score}   |   AI 2: ${game_manager.players[2].score}"
        self.draw_text(score_text, self.font_large, WHITE, 90, 20, center=False)

        # Category headers
        start_x = 40
        for col_idx, cat_name in enumerate(game_manager.board.categories.keys()):
            x = start_x + (col_idx * 200)
            header_rect = pygame.Rect(x, 70, 190, 50)
            pygame.draw.rect(self.screen, (0, 0, 100, 200), header_rect)
            pygame.draw.rect(self.screen, YELLOW, header_rect, 2)
            
            cat_font = self.font_small
            if len(cat_name) > 12: cat_font = pygame.font.SysFont('Arial', 14, bold=True)
            self.draw_text(cat_name.upper(), cat_font, WHITE, header_rect.centerx, header_rect.centery)

        self.box_group.draw(self.screen)

    def draw_clue_screen(self, clue):
        # Question background
        self.screen.blit(self.bgs["background"], (0, 0))
        
        self.draw_text(f"CATEGORY: {clue.category.upper()} - ${clue.pt_value}", self.font_large, YELLOW, 640, 50)
        
        clue_rect = pygame.Rect(140, 100, 1000, 250)
        self.draw_text_wrapped(self.screen, clue.question, WHITE, clue_rect, self.font_large)

        for i, option in enumerate(clue.mc_options):
            rect = pygame.Rect(340, 400 + (i * 70), 600, 50)
            surf = pygame.Surface((600, 50), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 180))
            self.screen.blit(surf, rect.topleft)
            pygame.draw.rect(self.screen, WHITE, rect, 2)
            self.draw_text(f"{i+1}. {option}", self.font_small, WHITE, rect.centerx, rect.centery)

    def draw_loading_screen(self):
        self.screen.blit(self.bgs["LED_blue"], (0, 0))
        self.screen.blit(self.icons["time_passing"], (600, 200))
        self.draw_text("Generating TV Jeopardy Board...", self.font_large, YELLOW, 640, 300)
        self.draw_text("Using Azure ChatGPT to fetch 30 questions (This takes ~15s)", self.font_small, WHITE, 640, 350)

    def draw_menu(self):
        self.screen.blit(self.bgs["LED_red"], (0, 0))
        self.draw_text("JEOPARDY!", self.font_title, YELLOW, 640, 200)
        self.draw_text("TV Edition - 6 Categories", self.font_large, WHITE, 640, 300)
        self.draw_text("Click anywhere to start", self.font_large, WHITE, 640, 450)