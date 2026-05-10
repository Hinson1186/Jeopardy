import pygame
import sys
import os
import glob
import random
from game_logic import JeopardyGameManager
from ui import UIManager
from powerups import ExtraTime, PointDoubler, Strike

# --- COLORS ---
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

def cleanup_temp_images():
    """Deletes temporary generated images when the game closes."""
    print("Cleaning up temporary image files...")
    temp_files = glob.glob("assets/images/clue_img_*.png")
    for file in temp_files:
        try:
            os.remove(file)
        except Exception:
            pass

def main():
    pygame.init()
    pygame.mixer.init()
    
    screen = pygame.display.set_mode((1280, 720)) 
    pygame.display.set_caption("Jeopardy! TV Edition")
    clock = pygame.time.Clock()

    # --- ASSET LOADING ---
    try:
        pygame.mixer.music.load("assets/sounds/Jeopardy-theme-song.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except: print("Warning: Music file not found")

    try:
        correct_sound = pygame.mixer.Sound("assets/sounds/Correct.wav")
        wrong_sound = pygame.mixer.Sound("assets/sounds/Wrong.wav")
        beeper_sound = pygame.mixer.Sound("assets/sounds/CountDownBeeper.wav")
    except:
        print("Warning: Sound effects missing")
        correct_sound = wrong_sound = beeper_sound = None

    game = JeopardyGameManager(None) # Passing None if you initialize LLM inside Manager
    ui = UIManager(screen)

    # --- POWER-UP & TIMER INITIALIZATION ---
    powerups = [ExtraTime(), PointDoubler(), Strike()]
    clue_start_time = 0
    clue_time_limit = 10000  # Default 10 seconds (10,000 ms)
    beeper_playing = False
    struck_choice_index = -1 # Which answer is hidden by the "Strike" powerup

    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # 1. START MENU LOGIC
                if game.game_state == "START_MENU":
                    game.game_state = "LOADING"
                    ui.draw_loading_screen()
                    pygame.display.flip()
                    game.setup_new_round(num_cats=6, clues_per=5)
                    if game.game_state == "SHOWING_BOARD":
                        ui.build_board_sprites(game.board)

                # 2. BOARD LOGIC
                elif game.game_state == "SHOWING_BOARD":
                    for box in ui.box_group:
                        if box.rect.collidepoint(pos) and not box.clue.is_answered:
                            game.select_clue(box.clue)
                            # RESET TIMER & STRIKE FOR NEW CLUE
                            clue_start_time = pygame.time.get_ticks()
                            clue_time_limit = 10000 
                            beeper_playing = False
                            struck_choice_index = -1

                # 3. CLUE SCREEN LOGIC
                elif game.game_state == "SHOWING_CLUE":
                    # CHECK POWER-UP CLICKS FIRST
                    for p in powerups:
                        if not p.is_used and p.rect.collidepoint(pos):
                            p.is_used = True
                            if isinstance(p, ExtraTime):
                                clue_time_limit += 5000 # Add 5 seconds
                                if beeper_playing and beeper_sound:
                                    beeper_sound.stop()
                                    beeper_playing = False
                            elif isinstance(p, PointDoubler):
                                game.current_clue.pt_value *= 2
                            elif isinstance(p, Strike):
                                # Logic to find a wrong answer that isn't the correct one
                                correct_ans = game.current_clue.correct_answer
                                wrong_indices = [i for i, opt in enumerate(game.current_clue.mc_options) if opt != correct_ans]
                                if wrong_indices:
                                    struck_choice_index = random.choice(wrong_indices)

                    # CHECK ANSWER CLICKS
                    clicked_index = -1
                    if 400 <= pos[1] <= 450: clicked_index = 0
                    elif 470 <= pos[1] <= 520: clicked_index = 1
                    elif 540 <= pos[1] <= 590: clicked_index = 2
                    elif 610 <= pos[1] <= 660: clicked_index = 3

                    # Only process if they didn't click a "Struck" answer
                    if clicked_index != -1 and clicked_index != struck_choice_index:
                        if clicked_index < len(game.current_clue.mc_options):
                            if beeper_sound: beeper_sound.stop()
                            
                            selected_answer = game.current_clue.mc_options[clicked_index]
                            if game.current_clue.check_ans(selected_answer):
                                if correct_sound: correct_sound.play()
                            else:
                                if wrong_sound: wrong_sound.play()

                            game.handle_answer(game.players[0], selected_answer)
                            ui.build_board_sprites(game.board)

        # --- TIMER & BEEPER LOGIC ---
        if game.game_state == "SHOWING_CLUE":
            elapsed = current_time - clue_start_time
            time_left = (clue_time_limit - elapsed) / 1000
            
            # Start beeper at 5 seconds
            if time_left <= 5 and not beeper_playing:
                if beeper_sound: beeper_sound.play(-1)
                beeper_playing = True

            # Handle Time Out
            if time_left <= 0:
                if beeper_sound: beeper_sound.stop()
                if wrong_sound: wrong_sound.play()
                game.handle_answer(game.players[0], "TIMEOUT_AUTO_WRONG")
                ui.build_board_sprites(game.board)

        # --- DRAWING PHASE ---
        if game.game_state == "START_MENU":
            ui.draw_menu()
        elif game.game_state == "SHOWING_BOARD":
            ui.draw_board_screen(game)
        elif game.game_state == "SHOWING_CLUE":
            ui.draw_clue_screen(game.current_clue)
            
            # Draw Timer
            t_color = RED if time_left < 5 else WHITE
            ui.draw_text(f"TIME: {int(max(0, time_left))}", ui.font_clue, t_color, 1150, 80)

            # Draw Power-Ups
            for i, p in enumerate(powerups):
                p.draw(screen, 1200 - (i * 75), 20)

            # Draw Strike effect (Red X)
            if struck_choice_index != -1:
                # Vertical position matches the button logic above
                y_strike = 400 + (struck_choice_index * 70) 
                pygame.draw.line(screen, RED, (400, y_strike), (880, y_strike + 50), 8)
                pygame.draw.line(screen, RED, (880, y_strike), (400, y_strike + 50), 8)

        elif game.game_state == "GAME_OVER":
            ui.screen.blit(ui.bgs["bg_podiums"], (0, 0))
            ui.screen.blit(ui.icons["icon_rank1"], (600, 150))
            ui.draw_text("GAME OVER!", ui.font_title, YELLOW, 640, 300)

        pygame.display.flip()
        clock.tick(60)

    cleanup_temp_images()
    if beeper_sound: beeper_sound.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()