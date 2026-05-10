import pygame
import sys
import os
import glob
from game_logic import JeopardyGameManager
from ui import UIManager

# --- COLORS ---
YELLOW = (255, 255, 0)

def cleanup_temp_images():
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

    # --- SOUND LOADING ---
    try:
        pygame.mixer.music.load("assets/sounds/Jeopardy-theme-song.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except: print("Warning: Music file not found")

    try:
        correct_sound = pygame.mixer.Sound("assets/sounds/Correct.wav")
        wrong_sound = pygame.mixer.Sound("assets/sounds/Wrong.wav")
        # 1. NEW: Load the Beeper Sound
        beeper_sound = pygame.mixer.Sound("assets/sounds/CountDownBeeper.wav")
    except:
        correct_sound = wrong_sound = beeper_sound = None

    game = JeopardyGameManager()
    ui = UIManager(screen)

    # 2. NEW: Variables to track time
    clue_start_time = 0
    clue_time_limit = 10000  # Total 10 seconds to answer (in milliseconds)
    beeper_playing = False

    running = True
    while running:
        current_time = pygame.time.get_ticks() # Get current time in ms

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.game_state == "START_MENU":
                    game.game_state = "LOADING"
                    ui.draw_loading_screen()
                    pygame.display.flip()
                    game.setup_new_round(num_cats=6, clues_per=5)
                    if game.game_state == "SHOWING_BOARD":
                        ui.build_board_sprites(game.board)

                elif game.game_state == "SHOWING_BOARD":
                    pos = pygame.mouse.get_pos()
                    for box in ui.box_group:
                        if box.rect.collidepoint(pos) and not box.clue.is_answered:
                            game.select_clue(box.clue)
                            # 3. NEW: Record when the clue was opened
                            clue_start_time = pygame.time.get_ticks()
                            beeper_playing = False 

                elif game.game_state == "SHOWING_CLUE":
                    pos = pygame.mouse.get_pos()
                    clicked_index = -1
                    if 400 <= pos[1] <= 450: clicked_index = 0
                    elif 470 <= pos[1] <= 520: clicked_index = 1
                    elif 540 <= pos[1] <= 590: clicked_index = 2
                    elif 610 <= pos[1] <= 660: clicked_index = 3

                    if clicked_index != -1 and clicked_index < len(game.current_clue.mc_options):
                        # 4. NEW: Stop beeper if an answer is clicked
                        if beeper_sound: beeper_sound.stop()
                        
                        selected_answer = game.current_clue.mc_options[clicked_index]
                        if game.current_clue.check_ans(selected_answer):
                            if correct_sound: correct_sound.play()
                        else:
                            if wrong_sound: wrong_sound.play()

                        game.handle_answer(game.players[0], selected_answer)
                        ui.build_board_sprites(game.board)

        # 5. NEW: COUNTDOWN LOGIC
        if game.game_state == "SHOWING_CLUE":
            elapsed = current_time - clue_start_time
            time_left = (clue_time_limit - elapsed) / 1000 # convert to seconds
            
            # Play beeper if less than 5 seconds left
            if time_left <= 5 and not beeper_playing:
                if beeper_sound:
                    beeper_sound.play(-1) # -1 means loop until stopped
                beeper_playing = True

            # Auto-fail if time runs out
            if time_left <= 0:
                if beeper_sound: beeper_sound.stop()
                if wrong_sound: wrong_sound.play()
                game.handle_answer(game.players[0], "TIME_OUT_WRONG_ANSWER")
                ui.build_board_sprites(game.board)

        # --- Drawing ---
        if game.game_state == "START_MENU":
            ui.draw_menu()
        elif game.game_state == "SHOWING_BOARD":
            ui.draw_board_screen(game)
        elif game.game_state == "SHOWING_CLUE":
            ui.draw_clue_screen(game.current_clue)
            # 6. OPTIONAL: Draw the time left on screen
            time_text = f"Time: {int(max(0, time_left))}"
            ui.draw_text(time_text, ui.font_clue, (255,0,0) if time_left < 5 else (255,255,255), 1150, 50)
            
        elif game.game_state == "GAME_OVER":
            ui.screen.blit(ui.bgs["bg_podiums"], (0, 0))
            ui.screen.blit(ui.icons["icon_rank1"], (600, 150))
            ui.draw_text("GAME OVER!", ui.font_title, YELLOW, 640, 300)

        pygame.display.flip()
        clock.tick(60)

    cleanup_temp_images()
    if beeper_sound: beeper_sound.stop() # Final safety stop
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()