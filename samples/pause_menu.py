from ursina import *


app = Ursina()

# Make a simple game so we have something to test with
from ursina.prefabs.first_person_controller import FirstPersonController
player = FirstPersonController(gravity=0, model='cube', color=color.azure)
camera.z = -10
ground = Entity(model='plane', texture='grass', scale=10)

# Create an Entity for handling pausing an unpausing.
# Make sure to set ignore_paused to True so the pause handler itself can still receive input while the game is paused.
pause_handler = Entity(ignore_paused=True)
pause_text = Text('PAUSED', origin=(0,0), scale=2, enabled=False) # Make a Text saying "PAUSED" just to make it clear when it's paused.

def pause_handler_input(key):
    if key == 'escape':
        application.paused = not application.paused # Pause/unpause the game.
        pause_text.enabled = application.paused     # Also toggle "PAUSED" graphic.

pause_handler.input = pause_handler_input   # Assign the input function to the pause handler.


app.run()
