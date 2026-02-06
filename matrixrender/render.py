import pygame
import numpy as np
import typing as ttypes
from PIL import Image

class WindowExitRequested(BaseException): ...

class App:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock, zoom: int = 1, target_fps: int = 60):
        self.screen = screen
        self.clock = clock
        self.zoom = zoom
        self.target_fps = target_fps
        self.__width =  int(self.screen.get_width() / zoom)
        self.__height = int(self.screen.get_height() / zoom)
        self.__delta_time: float = 1.0 / target_fps

    def tick(self):
        self.__delta_time = float(self.clock.tick(self.target_fps)) / 1000

    @property
    def width(self): return self.__width

    @property
    def height(self): return self.__height

    @property
    def dt(self) -> float:
        return min(self.__delta_time, 0.25)  # Clamp at 4 FPS
    
    def clear_events(self):
        for event in pygame.event.get():
            yield event

class State:
    def __init__(self, width: int, height: int):
        self.x_max = width
        self.y_max = height

        # State.area usage:
        # State.area[x, y]
        #
        # or (not recommended as it is slower): State.area[x][y]
        self.area = np.zeros((self.x_max, self.y_max), dtype=int)

    def set_area(self, area: np.ndarray) -> None:
        if area.shape != self.area.shape:
            raise ValueError("Area shape mismatch")
        
        self.area = area

    def set_cell(self, x: int, y: int, value: int) -> None:
        self.area[x, y] = value

def init_screen(width=800, height=600, title="Pygame Window", zoom: int = 1, target_fps: int = 60) -> App:
    pygame.init()
    
    screen = pygame.display.set_mode((width * zoom, height * zoom))
    pygame.display.set_caption(title)
    
    clock = pygame.time.Clock()
    
    return App(screen, clock, zoom, target_fps)

def _draw_cell(
    screen: pygame.Surface,
    x: int,
    y: int,
    visual: pygame.Color | pygame.Surface,
    cell_size: int,
) -> None:
    dest = (x * cell_size, y * cell_size)

    if isinstance(visual, pygame.Surface):
        screen.blit(visual, dest)
    else:
        rect = pygame.Rect(dest[0], dest[1], cell_size, cell_size)
        pygame.draw.rect(screen, visual, rect)


def pil_to_surface(img: Image.Image) -> pygame.Surface:
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")

    data = img.tobytes()
    size = img.size
    mode = img.mode

    return pygame.image.fromstring(data, size, mode)


WHITE: pygame.Color = pygame.Color(255, 255, 255, 255)
BLACK: pygame.Color = pygame.Color( 0,   0,   0,  255)
_states: dict[int, pygame.Color | pygame.Surface] = {0: WHITE}

def register_state(
    value: int,
    visual: pygame.Color | Image.Image,
    *,
    app: App | None = None
) -> None:
    if isinstance(visual, Image.Image):
        surface = pil_to_surface(visual)

        if app is None:
            raise ValueError("Registering an Image as a state requires passing the app= keyword argument (type App)")

        if app.zoom is not None:
            surface = pygame.transform.scale(
                surface,
                (app.zoom, app.zoom),
            )

        _states[value] = surface

    elif isinstance(visual, pygame.Color):
        _states[value] = visual

    else:
        raise TypeError("State visual must be pygame.Color or PIL.Image.Image")

def update_screen(app: App, state: State) -> tuple[bool, ttypes.Optional[Exception]]:
    # If types don't correspond, raise Error as the caller is possibly in an invalid state
    #
    # If drawing fails, simply return the Error so the caller can understand what went wrong
    # and handle the error / do cleanup

    if (not isinstance(app, App)):
        raise TypeError("app is not an instance of type App().")
    elif (not isinstance(state, State)):
        raise TypeError("state is not an instance of type State().")
    
    app.screen.fill(BLACK)
    
    for i in range(0, state.x_max):
        for j in range(0, state.y_max):
            _draw_cell(app.screen, i, j, _states.get(state.area[i, j], BLACK), app.zoom)

    if pygame.event.peek(pygame.QUIT):
        raise WindowExitRequested("User closed the PyGame window.")

    try:
        pygame.display.flip()
        app.tick()
        return (True, None)
    except Exception as e:
        return (False, e)
