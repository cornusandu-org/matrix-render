from matrixrender import render

App = render.init_screen(30, 30, zoom = 20)

State = render.State(App.screen.get_width(), App.screen.get_height())

State.area[0, 0] = 1

render.register_state(1, render.pygame.Color(255, 0, 0, 255))  # Full Red

while True:
    success, exc = render.update_screen(App, State)

    if (not success):
        raise exc
    
    for event in App.clear_events(): ...
