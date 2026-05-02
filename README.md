Welcome to AIST 1110 project!!!
ABC
15/4/2026
Currently completed Player class. 
2/5/2026
jeopardy_project/
|
|-- main.py                 # Main entry point, starts the game.
|-- game_models.py          # Core data classes (Clue, Player, AIPlayer).
|-- game_controller.py      # The main game logic and state machine.
|-- services.py             # Handles communication with Azure AI.
|-- ui_components.py        # Reusable Pygame UI elements (Buttons, Sprites).
|-- scenes.py               # Manages different game screens (Menu, Game Board, etc.).
|-- requirements.txt        # List of required packages (e.g., pygame, requests).
|-- .env                    # Stores your Azure API key securely.
|
|-- assets/                 # Folder for all game resources.
|   |-- images/
|   |   |-- board_background.png
|   |   |-- player_profile.png
|   |-- sounds/
|   |   |-- background_music.mp3
|   |   |-- correct_answer.wav
|   |-- fonts/
|       |-- jeopardy_font.ttf