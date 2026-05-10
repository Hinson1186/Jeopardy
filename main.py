import pygame
import sys
import os
import glob
from game_logic import JeopardyGameManager
from ui import UIManager
from powerups import ExtraTime, PointDoubler, Strike

YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

def cleanup_temp_images():
    """Delete temporary generated images when the game closes."""
    print("Cleaning up temporary image files...")
    temp_files = glob.glob("assets/images/clue_img_*.png")
    for file in temp_files:
        try: os.remove(file)
        except Exception: pass

def main():
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    
    screen = pygame.display.set_mode((1280, 720)) 
    pygame.display.set_caption("Jeopardy! TV Edition")
    clock = pygame.time.Clock()

    # --- SOUND LOADING ---
    try:
        pygame.mixer.music.load("assets/sounds/Jeopardy-theme-song.wav")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except:
        pass

    try:
        correct_sound = pygame.mixer.Sound("assets/sounds/Correct.wav")
        wrong_sound = pygame.mixer.Sound("assets/sounds/Wrong.wav")
        beeper_sound = pygame.mixer.Sound("assets/sounds/CountDownBeeper.wav")
    except:
        correct_sound = wrong_sound = beeper_sound = None

    game = JeopardyGameManager()
    ui = UIManager(screen)

    powerups = [
        ExtraTime(ui.icons["time_passing"]), 
        PointDoubler(ui.icons["coin"]), 
        Strike(ui.icons["heart"])
    ]

    # Timers
    ai_timer_start = 0
    ai_think_time = 0
    clue_start_time = 0
    clue_time_limit = 10000 
    beeper_playing = False
    struck_choice_index = -1 
    time_left = 10
    
    # Answer tracker
    active_ai_list = []
    current_ai_turn = 0

    running = True
    while running:
        pos = pygame.mouse.get_pos()
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # --- DEV TOOL: PRESS F1 TO SKIP ROUND ---
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1 and game.game_state == "SHOWING_BOARD":
                    game.advance_round()
                    if game.game_state == "LOADING":
                        ui.draw_loading_screen(game.round_num)
                        pygame.display.flip()
                        if game.game_state == "SHOWING_BOARD":
                            ui.build_board_sprites(game.board)
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.game_state == "START_MENU":
                    if 440 <= pos[0] <= 840 and 400 <= pos[1] <= 460:
                        # Reset game completely
                        game = JeopardyGameManager()
                        for p in powerups: p.is_used = False
                        game.game_state = "LOBBY"

                elif game.game_state == "LOBBY":
                    # Add AI Buttons
                    if 300 <= pos[0] <= 600:
                        if 400 <= pos[1] <= 450: game.add_ai_player("easy")
                        elif 480 <= pos[1] <= 530: game.add_ai_player("medium")
                        elif 560 <= pos[1] <= 610: game.add_ai_player("hard")
                    
                    # Start Game Button
                    if 700 <= pos[0] <= 1000 and 450 <= pos[1] <= 530:
                        game.game_state = "LOADING"
                        ui.draw_loading_screen(game.round_num)
                        pygame.display.flip()
                        game.setup_new_round(num_cats=6, clues_per=5)
                        if game.game_state == "SHOWING_BOARD":
                            ui.build_board_sprites(game.board)

                elif game.game_state == "SHOWING_BOARD":
                    # LEAVE BUTTON
                    if 1100 <= pos[0] <= 1250 and 20 <= pos[1] <= 60:
                        game.game_state = "START_MENU"
                    else:
                        for box in ui.box_group:
                            if box.rect.collidepoint(pos) and not box.clue.is_answered:
                                game.select_clue(box.clue, 0)
                                if game.game_state == "SHOWING_CLUE":
                                    clue_start_time = pygame.time.get_ticks()
                                    clue_time_limit = 10000
                                    beeper_playing = False
                                    struck_choice_index = -1
                                    
                                    active_ai_list = [p for p in game.players if not p.is_human]
                                    active_ai_list.sort(key=lambda x: x.get_reaction_time())
                                    current_ai_turn = 0
                                    
                                    if active_ai_list:
                                        ai_think_time = int(active_ai_list[0].get_reaction_time() * 1000)
                                        ai_timer_start = pygame.time.get_ticks()

                elif game.game_state in ["WAGERING", "FINAL_WAGERING"]:
                    if 540 <= pos[0] <= 740 and 550 <= pos[1] <= 610:
                        game.game_state = "SHOWING_CLUE"
                        clue_start_time = pygame.time.get_ticks()
                        beeper_playing = False
                        active_ai_list = []

                elif game.game_state == "SHOWING_CLUE":
                    # POWERUPS
                    for p in powerups:
                        if not p.is_used and p.rect.collidepoint(pos):
                            p.is_used = True
                            if p.name == "Extra Time":
                                clue_time_limit += 5000
                                if beeper_sound: beeper_sound.stop()
                                beeper_playing = False
                            elif p.name == "Point Doubler":
                                game.current_clue.pt_value *= 2
                            elif p.name == "Strike":
                                correct_ans = game.current_clue.correct_answer
                                wrong_indices = [i for i, opt in enumerate(game.current_clue.mc_options) if opt != correct_ans]
                                if wrong_indices:
                                    struck_choice_index = random.choice(wrong_indices)

                    # ANSWERING
                    clicked_index = -1
                    if 400 <= pos[1] <= 450: clicked_index = 0
                    elif 470 <= pos[1] <= 520: clicked_index = 1
                    elif 540 <= pos[1] <= 590: clicked_index = 2
                    elif 610 <= pos[1] <= 660: clicked_index = 3

                    if clicked_index != -1 and clicked_index != struck_choice_index and clicked_index < len(game.current_clue.mc_options):
                        if beeper_sound: beeper_sound.stop()
                        
                        selected_answer = game.current_clue.mc_options[clicked_index]
                        is_correct = game.handle_answer(0, selected_answer) # 0 is Human
                        
                        if is_correct:
                            if correct_sound: correct_sound.play()
                        else:
                            if wrong_sound: wrong_sound.play()
                            
                        if game.game_state == "LOADING":
                            ui.draw_loading_screen(game.round_num)
                            pygame.display.flip()
                        
                        ui.build_board_sprites(game.board)

        # --- SLIDER DRAGGING ---
        if game.game_state in ["WAGERING", "FINAL_WAGERING"]:
            if pygame.mouse.get_pressed()[0]:
                if 340 <= pos[0] <= 940 and 400 <= pos[1] <= 500:
                    percent = max(0.0, min(1.0, (pos[0] - 340) / 600.0))
                    min_w = 0 if game.game_state == "FINAL_WAGERING" else 5
                    new_wager = min_w + int(percent * (game.max_wager - min_w))
                    game.current_wager = round(new_wager / 5) * 5
        
        # --- HUMAN COUNTDOWN ---
        elif game.game_state == "SHOWING_CLUE" and game.active_player_index == 0:
            elapsed = current_time - clue_start_time
            time_left = (clue_time_limit - elapsed) / 1000.0
            
            if time_left <= 5 and not beeper_playing:
                if beeper_sound: beeper_sound.play(-1)
                beeper_playing = True

            if time_left <= 0:
                if beeper_sound: beeper_sound.stop()
                if wrong_sound: wrong_sound.play()
                
                game.handle_answer(0, "TIME_OUT")
                ui.build_board_sprites(game.board)

        # --- AI STEALING & BUZZING LOGIC ---
        elif game.game_state == "SHOWING_CLUE" and active_ai_list and current_ai_turn < len(active_ai_list):
            if current_time - ai_timer_start >= ai_think_time:
                ai_player = active_ai_list[current_ai_turn]
                
                true_idx = game.players.index(ai_player)
                
                if ai_player.decides_to_answer_correctly():
                    if correct_sound: correct_sound.play()
                    if beeper_sound: beeper_sound.stop()
                    game.handle_answer(true_idx, game.current_clue.correct_answer)
                else:
                    if wrong_sound: wrong_sound.play()
                    game.handle_answer(true_idx, "WRONG_GUESS")
                    
                    current_ai_turn += 1
                    if current_ai_turn < len(active_ai_list):
                        ai_think_time = int(active_ai_list[current_ai_turn].get_reaction_time() * 1000)
                        ai_timer_start = pygame.time.get_ticks()
                        
                ui.build_board_sprites(game.board)

        # --- DRAWING ---
        if game.game_state == "START_MENU":
            ui.draw_menu()
        elif game.game_state == "LOBBY":
            ui.draw_lobby(game)
        elif game.game_state == "SHOWING_BOARD":
            ui.draw_board_screen(game)
        elif game.game_state in ["WAGERING", "FINAL_WAGERING"]:
            ui.draw_wagering_screen(game, is_final=(game.round_num == 3))
        elif game.game_state == "SHOWING_CLUE":
            ui.draw_clue_screen(game.current_clue)
            time_text = f"Time: {int(max(0, time_left))}"
            time_color = RED if time_left < 5 else WHITE
            ui.draw_text(time_text, ui.font_large, time_color, 1150, 50)
            
            # Powerups & Strike
            for i, p in enumerate(powerups): p.draw(screen, 1200 - (i * 75), 20)
            if struck_choice_index != -1:
                y_strike = 400 + (struck_choice_index * 70) 
                pygame.draw.line(screen, RED, (340, y_strike), (940, y_strike + 50), 8)
                pygame.draw.line(screen, RED, (940, y_strike), (340, y_strike + 50), 8)

        elif game.game_state == "GAME_OVER":
            ui.screen.blit(ui.bgs["stage"], (0, 0))
            ui.screen.blit(ui.icons["rank"], (600, 150))
            ui.draw_text("GAME OVER!", ui.font_title, YELLOW, 640, 300)
            
            if game.players:
                winner = max(game.players, key=lambda p: p.score)
                ui.draw_text(f"WINNER: {winner.name} with ${winner.score}", ui.font_large, WHITE, 640, 400)
            ui.draw_text("Click to return to menu", ui.font_small, WHITE, 640, 500)

        pygame.display.flip()
        clock.tick(60)

    cleanup_temp_images()
    if beeper_sound: beeper_sound.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()