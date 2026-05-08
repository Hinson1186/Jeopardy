# Unwelcome to AIST 1110 project :(

## Notice:
```diff
- This project is not completed yet.
- Please do not expect any functional features.
- Put .venv in .gitignore after the project is completed.
- Put API key before submitting the project.
```

## Project Log:
* 15/4/2026
Currently completed Player class. 
* 2/5/2026
added different sections.
```text
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
```
* 5/5/2026
kind of completed the game_models, please revisit the thinking time and the chance of answering correctly. (Read slide p.47 fyr)

* 7/5/2026
Upload parts of assets.
Draft api.py.

* 8/5/2026
Add game_logic.py and player.py.
```diff
- Test api.py after plug in the API key. For functionality and performance of AI under prompt.
- tmp.py can be removed, but still double check or wait until all functions in tmp.py are completed in other files.
```