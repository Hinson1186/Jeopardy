import pygame
import sys
import os
import glob
import random
from game_logic import JeopardyGameManager
from ui import UIManager
from powerups import ExtraTime, PointDoubler, Strike

# --- CONSTANTS ---
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

def cleanup_temp_images():
    """Deletes temporary generated images when the game closes."""
    print("Cleaning up temporary image files...")
    temp_files = glob.glob("assets/images/clue_img_*.png")
    for file in temp_files:
        try: os.remove(file)
        except: pass

def main():
    # Optimization for sounds
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    
    screen = pygame.display.set_mode((1280, 720)) 
    pygame.display.set_caption("Jeopardy! TV Edition")
    clock = pygame.time.Clock()

    # --- LOAD SOUNDS ---
    try:
        pygame.mixer.music.load("assets/sounds/Jeopardy-theme-song.mp3")
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
    except: pass

    try:
        correct_sound = pygame.mixer.Sound("assets/sounds/Correct.wav")
        wrong_sound = pygame.mixer.Sound("assets/sounds/Wrong.wav")
        beeper_sound = pygame.mixer.Sound("assets/sounds/CountDownBeeper.wav")
    except:
        correct_sound = wrong_sound = beeper_sound = None

    # --- INITIALIZE GAME OBJECTS ---
    game = JeopardyGameManager()
    ui = UIManager(screen)

    # Initialize Power-ups using images loaded through UI
    # Replace filenames below with your actual filenames
    powerups = [
        ExtraTime(pygame.image.load("assets/images/time-passing.png")),
        PointDoubler(pygame.image.load("assets/images/coin.png")),
        Strike(pygame.image.load("assets/images/level-up.png"))
    ]

    # Timer and State Variables
    ai_timer_start = 0
    ai_think_time = 0
    clue_start_time = 0
    clue_time_limit = 10000 
    beeper_playing = False
    time_left = 10
    struck_choice_index = -1 # Which answer is hidden by Strike powerup

    running = True
    while running:
        pos = pygame.mouse.get_pos()
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # --- START MENU ---
                if game.game_state == "START_MENU":
                    if 440 <= pos[0] <= 840 and 300 <= pos[1] <= 360:
                        game.game_state = "DIFFICULTY_MENU"
                    elif game.has_active_game and 440 <= pos[0] <= 840 and 400 <= pos[1] <= 460:
                        game.game_state = "SHOWING_BOARD"

                # --- DIFFICULTY MENU ---
                elif game.game_state == "DIFFICULTY_MENU":
                    diff = None
                    if 440 <= pos[0] <= 840:
                        if 300 <= pos[1] <= 360: diff = "easy"
                        elif 400 <= pos[1] <= 460: diff = "medium"
                        elif 500 <= pos[1] <= 560: diff = "hard"
                    if diff:
                        game.set_difficulty_and_start(diff)
                        game.game_state = "LOADING"
                        ui.draw_loading_screen()
                        pygame.display.flip()
                        game.setup_new_round(num_cats=6, clues_per=5)
                        if game.game_state == "SHOWING_BOARD": ui.build_board_sprites(game.board)

                # --- MAIN BOARD ---
                elif game.game_state == "SHOWING_BOARD":
                    if 1100 <= pos[0] <= 1250 and 20 <= pos[1] <= 60:
                        game.game_state = "START_MENU"
                    else:
                        for box in ui.box_group:
                            if box.rect.collidepoint(pos) and not box.clue.is_answered:
                                game.select_clue(box.clue, game.players[0])
                                # Reset Clue Variables
                                if game.game_state == "SHOWING_CLUE":
                                    clue_start_time = current_time
                                    clue_time_limit = 10000 
                                    beeper_playing = False
                                    struck_choice_index = -1

                # --- WAGERING ---
                elif game.game_state == "WAGERING":
                    if 540 <= pos[0] <= 740 and 550 <= pos[1] <= 610:
                        game.game_state = "SHOWING_CLUE"
                        clue_start_time = current_time
                        clue_time_limit = 10000
                        beeper_playing = False
                        struck_choice_index = -1

                # --- ANSWERING CLUE ---
                elif game.game_state == "SHOWING_CLUE":
                    # CHECK POWER-UP CLICKS FIRST
                    for p in powerups:
                        if not p.is_used and p.rect.collidepoint(pos):
                            if isinstance(p, ExtraTime):
                                p.apply() # Marks used
                                clue_time_limit += 5000 
                                if beeper_playing and beeper_sound:
                                    beeper_sound.stop()
                                    beeper_playing = False
                            elif isinstance(p, PointDoubler):
                                p.apply()
                                game.current_clue.pt_value *= 2
                            elif isinstance(p, Strike):
                                # Logic to get wrong index
                                struck_choice_index = p.apply(game.current_clue)

                    # CHECK ANSWER CLICKS
                    clicked_index = -1
                    if 400 <= pos[1] <= 450: clicked_index = 0
                    elif 470 <= pos[1] <= 520: clicked_index = 1
                    elif 540 <= pos[1] <= 590: clicked_index = 2
                    elif 610 <= pos[1] <= 660: clicked_index = 3

                    # Skip processing if answer was "Struck" by power-up
                    if clicked_index != -1 and clicked_index != struck_choice_index:
                        if clicked_index < len(game.current_clue.mc_options):
                            if beeper_sound: beeper_sound.stop()
                            selected_answer = game.current_clue.mc_options[clicked_index]
                            is_correct = game.handle_human_answer(selected_answer)
                            
                            if is_correct:
                                if correct_sound: correct_sound.play()
                            else:
                                if wrong_sound: wrong_sound.play()
                                # Start AI Timer if human missed
                                if game.game_state == "AI_TURN":
                                    ai_player = game.get_current_ai_player()
                                    ai_think_time = ai_player.get_delay_time() * 1000
                                    ai_timer_start = current_time
                            ui.build_board_sprites(game.board)

                # --- GAME OVER ---
                elif game.game_state == "GAME_OVER":
                    game.has_active_game = False
                    game.game_state = "START_MENU"

        # --- CONTINUOUS LOGIC (TIMERS) ---
        if game.game_state == "SHOWING_CLUE":
            elapsed = current_time - clue_start_time
            time_left = (clue_time_limit - elapsed) / 1000.0
            
            if time_left <= 5 and not beeper_playing:
                if beeper_sound: beeper_sound.play(-1)
                beeper_playing = True

            if time_left <= 0:
                if beeper_sound: beeper_sound.stop()
                if wrong_sound: wrong_sound.play()
                is_correct = game.handle_human_answer("TIMEOUT")
                if not is_correct and game.game_state == "AI_TURN":
                    ai_player = game.get_current_ai_player()
                    ai_think_time = ai_player.get_delay_time() * 1000
                    ai_timer_start = current_time
                ui.build_board_sprites(game.board)

        elif game.game_state == "AI_TURN":
            if current_time - ai_timer_start >= ai_think_time:
                ai_got_it = game.handle_ai_steal()
                if ai_got_it:
                    if correct_sound: correct_sound.play()
                else:
                    if wrong_sound: wrong_sound.play()
                    if game.game_state == "AI_TURN":
                        ai_player = game.get_current_ai_player()
                        ai_think_time = ai_player.get_delay_time() * 1000
                        ai_timer_start = current_time
                ui.build_board_sprites(game.board)

        # --- DRAWING ---
        if game.game_state == "START_MENU":
            ui.draw_menu(game.has_active_game)
        elif game.game_state == "DIFFICULTY_MENU":
            ui.draw_difficulty_menu()
        elif game.game_state == "SHOWING_BOARD":
            ui.draw_board_screen(game)
        elif game.game_state == "WAGERING":
            ui.draw_wagering_screen(game)
        elif game.game_state == "SHOWING_CLUE":
            ui.draw_clue_screen(game.current_clue)
            # Timer Display
            t_color = RED if time_left < 5 else WHITE
            ui.draw_text(f"Time: {int(max(0, time_left))}", ui.font_large, t_color, 1150, 80)
            # Power-up Display (Top Right)
            for i, p in enumerate(powerups):
                p.draw(screen, 1200 - (i * 75), 20)
            # Strike Visual (Red X)
            if struck_choice_index != -1:
                y_strike = 400 + (struck_choice_index * 70)
                pygame.draw.line(screen, RED, (400, y_strike), (880, y_strike+50), 10)
                pygame.draw.line(screen, RED, (880, y_strike), (400, y_strike+50), 10)

        elif game.game_state == "AI_TURN":
            ui.draw_ai_turn_screen(game.get_current_ai_player().name)
        elif game.game_state == "GAME_OVER":
            ui.screen.blit(ui.bgs["stage"], (0, 0))
            winner = max(game.players, key=lambda p: p.score)
            ui.draw_text(f"WINNER: {winner.name} (${winner.score})", ui.font_title, YELLOW, 640, 300)
            ui.draw_text("Click to restart", ui.font_small, WHITE, 640, 500)

        pygame.display.flip()
        clock.tick(60)

    cleanup_temp_images()
    if beeper_sound: beeper_sound.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()