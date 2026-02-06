from matrixrender import render
from PIL import Image

img = Image.open("assets/image.png")

App = render.init_screen(20, 20, zoom = 30)

State = render.State(App.width, App.height)

# State.area[x, y]
State.area[0, 0] = 1
State.area[0, 1] = 2
State.area[0, 2] = 3

render.register_state(1, render.pygame.Color(255, 0, 0, 255))  # Full Red
render.register_state(2, img, app = App)

while True:
    for event in App.clear_events(): ...  # Clear events. You can process/check them if you
                                          # need key-based events (ex. KEY_LEFT)

    # Update/refresh the screen
    # Already calls clock.tick(), so no need to do it ourselves
    success, exc = render.update_screen(App, State)

    # Throw an error if we failed to update the screen
    if (not success):
        raise exc
