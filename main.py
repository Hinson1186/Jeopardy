import pygame
import sys
import os
import glob
from game_logic import JeopardyGameManager
from ui import UIManager

YELLOW = (255, 255, 0)

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
    # Prevent buzzing sound when loading mp3s
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    
    screen = pygame.display.set_mode((1280, 720)) 
    pygame.display.set_caption("Jeopardy! TV Edition")
    clock = pygame.time.Clock()

    # --- SOUND LOADING ---
    try:
        pygame.mixer.music.load("assets/sounds/Jeopardy-theme-song.mp3")
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

    ai_timer_start = 0
    ai_think_time = 0

    clue_start_time = 0
    clue_time_limit = 10000  # Total 10 seconds to answer (in milliseconds)
    beeper_playing = False
    time_left = 10

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
                    # NEW GAME
                    if 440 <= pos[0] <= 840 and 300 <= pos[1] <= 360:
                        game.game_state = "DIFFICULTY_MENU"
                    # RESUME
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
                        if game.game_state == "SHOWING_BOARD":
                            ui.build_board_sprites(game.board)

                # --- MAIN BOARD ---
                elif game.game_state == "SHOWING_BOARD":
                    # MENU
                    if 1100 <= pos[0] <= 1250 and 20 <= pos[1] <= 60:
                        game.game_state = "START_MENU"
                    else:
                        for box in ui.box_group:
                            if box.rect.collidepoint(pos) and not box.clue.is_answered:
                                game.select_clue(box.clue, game.players[0])
                                
                                # Start timer if it's not a Daily Double
                                if game.game_state == "SHOWING_CLUE":
                                    clue_start_time = pygame.time.get_ticks()
                                    beeper_playing = False

                # --- WAGERING ---
                elif game.game_state == "WAGERING":
                    # Wager!
                    if 540 <= pos[0] <= 740 and 550 <= pos[1] <= 610:
                        game.game_state = "SHOWING_CLUE"
                        clue_start_time = pygame.time.get_ticks()
                        beeper_playing = False

                # --- ANSWERING CLUE ---
                elif game.game_state == "SHOWING_CLUE":
                    clicked_index = -1
                    if 400 <= pos[1] <= 450: clicked_index = 0
                    elif 470 <= pos[1] <= 520: clicked_index = 1
                    elif 540 <= pos[1] <= 590: clicked_index = 2
                    elif 610 <= pos[1] <= 660: clicked_index = 3

                    if clicked_index != -1 and clicked_index < len(game.current_clue.mc_options):
                        if beeper_sound: beeper_sound.stop()
                        
                        selected_answer = game.current_clue.mc_options[clicked_index]
                        is_correct = game.handle_human_answer(selected_answer)
                        
                        if is_correct:
                            if correct_sound: correct_sound.play()
                        else:
                            if wrong_sound: wrong_sound.play()
                            
                            if game.game_state == "AI_TURN":
                                ai_player = game.players[game.ai_turn_index]
                                ai_think_time = ai_player.delay_time() * 1000
                                ai_timer_start = pygame.time.get_ticks()

                        ui.build_board_sprites(game.board)

                # --- GAME OVER ---
                elif game.game_state == "GAME_OVER":
                    game.has_active_game = False
                    game.game_state = "START_MENU"

        # Wager Slider
        if game.game_state == "WAGERING":
            if pygame.mouse.get_pressed()[0]:
                # If mouse is near the slider
                if 340 <= pos[0] <= 940 and 400 <= pos[1] <= 500:
                    # Calculate percentage based on mouse position
                    percent = (pos[0] - 340) / 600.0
                    percent = max(0.0, min(1.0, percent))
                    
                    wager_range = game.max_wager - 5
                    new_wager = 5 + int(percent * wager_range)
                    
                    # Round to nearest $5
                    game.current_wager = round(new_wager / 5) * 5
        
        elif game.game_state == "SHOWING_CLUE":
            elapsed = current_time - clue_start_time
            time_left = (clue_time_limit - elapsed) / 1000.0 # float seconds
            
            # Play beeper if 5 seconds or less
            if time_left <= 5 and not beeper_playing:
                if beeper_sound:
                    beeper_sound.play(-1)
                beeper_playing = True

            # TIME OUT
            if time_left <= 0:
                if beeper_sound: beeper_sound.stop()
                if wrong_sound: wrong_sound.play()
                
                # Treat timeout as a wrong answer
                is_correct = game.handle_human_answer("TIME_OUT_WRONG_ANSWER")
                if not is_correct and game.game_state == "AI_TURN":
                    ai_player = game.players[game.ai_turn_index]
                    ai_think_time = int(ai_player.get_delay_time() * 1000)
                    ai_timer_start = pygame.time.get_ticks()
                    
                ui.build_board_sprites(game.board)

        # AI Timer
        elif game.game_state == "AI_TURN":
            current_time = pygame.time.get_ticks()
            if current_time - ai_timer_start >= ai_think_time:
                ai_got_it = game.handle_ai_steal()
                
                if ai_got_it:
                    if correct_sound: correct_sound.play()
                    ui.build_board_sprites(game.board)
                else:
                    if wrong_sound: wrong_sound.play()
                    # If still in AI_TURN, the next AI is up
                    if game.game_state == "AI_TURN":
                        ai_player = game.players[game.ai_turn_index]
                        ai_think_time = int(ai_player.delay_time() * 1000)
                        ai_timer_start = pygame.time.get_ticks()
                    else:
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
            time_text = f"Time: {int(max(0, time_left))}"
            time_color = (255, 0, 0) if time_left < 5 else (255, 255, 255)
            ui.draw_text(time_text, ui.font_large, time_color, 1150, 50)
        elif game.game_state == "AI_TURN":
            current_bot_name = game.players[game.ai_turn_index].name
            ui.draw_ai_turn_screen(current_bot_name)
        elif game.game_state == "GAME_OVER":
            ui.screen.blit(ui.bgs["stage"], (0, 0))
            ui.screen.blit(ui.icons["rank"], (600, 150))
            ui.draw_text("GAME OVER!", ui.font_title, YELLOW, 640, 300)
            
            # Find winner
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