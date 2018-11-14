#!/usr/bin/python3

import pygame
import os
import pandas as pd

SCREEN_WIDTH = 1610
SCREEN_HEIGHT = 766

PIPE_SIZE = 128

BACKGROUND = pygame.image.load("pics/desert.png")
BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

ANIMATION_FPS = 100 # miliseconds

MAX_LEVEL = 3 # number of available levels


############### classes ##############

class Pipe:
    """
    Corner or straight pipe able to rotate by 90 degrees and fill with water.
    x, y - position to render picture
    left, right, down, up - specify where pipe holes are, exactly two of them must be True
    """
    def __init__(self, x, y, left = False, right = False, down = False, up = False):
        """Initializes pipe and render it to the screen"""
        if sum((left, right, down, up)) != 2:
            print('Cannot initialize pipe, too many or too few holes')
            raise SystemExit(str(geterror()))
        self.x = int(x)
        self.y = int(y)
        self.left = left
        self.right = right
        self.down = down
        self.up = up
        self.filled = False
        self.start = None
        self.end = None
        if down and up:
            self.image = load_image('pics/pipes/pipe_straight.png')
            self.rect = self.image.get_rect(topleft = (self.x, self.y))
        elif left and right:
            self.image = load_image('pics/pipes/pipe_straight.png', 90)
            self.rect = self.image.get_rect(topleft = (self.x, self.y))
        elif left:
            if down:
                self.image = load_image('pics/pipes/pipe_corner.png')
                self.rect = self.image.get_rect(topleft = (self.x, self.y))
            elif up:
                self.image = load_image('pics/pipes/pipe_corner.png', 90)
                self.rect = self.image.get_rect(topleft = (self.x, self.y))
        elif right:
            if down:
                self.image = load_image('pics/pipes/pipe_corner.png', 270)
                self.rect = self.image.get_rect(topleft = (self.x, self.y))
            elif up:
                self.image = load_image('pics/pipes/pipe_corner.png', 180)
                self.rect = self.image.get_rect(topleft = (self.x, self.y))
        screen = pygame.display.get_surface()
        screen.blit(self.image, (x, y))

    def fill_end(self):
        """Determines pipe end if start is known"""
        d = dict(zip(['up', 'right', 'down', 'left'], [self.up, self.right, self.down, self.left]))
        d.pop(self.start)
        self.end = [k for k, v in d.items() if v][0]

    def rotate(self):
        """Rotates pipe by 90 degrees clockwise"""
        old = [self.up, self.right, self.down, self.left]
        new = [0, 0, 0, 0]
        for i in range(4):
            new[i] = old[i - 1]
        self.up, self.right, self.down, self.left = new

        screen = pygame.display.get_surface()
        screen.blit(BACKGROUND, (self.x, self.y), area = self.rect)
        self.image = pygame.transform.rotate(self.image, -90)
        screen.blit(self.image, (self.x, self.y))
        pygame.display.flip()

    def fill_water(self):
        """Animation of filling pipe with water"""
        if self.filled:
            return

        water_file = 'pics/pipes/water_' + self.start + '_' + self.end + '.png'

        # animation
        screen = pygame.display.get_surface()
        water_img = load_image(water_file)
        for i in range(11):
            pygame.time.wait(int(ANIMATION_FPS * 0.6))
            screen.blit(BACKGROUND, (self.x, self.y), area = self.rect)
            screen.blit(water_img, (self.x, self.y),
                        area = pygame.Rect(i * PIPE_SIZE, 0, PIPE_SIZE, PIPE_SIZE))
            screen.blit(self.image, (self.x, self.y))
            pygame.display.flip()

        self.filled = True


class Wheel:
    def __init__(self, x, y):
        """Initializes wheel and beginning of pipe and render them to the screen"""
        self.x = int(x)
        self.y = int(y)
        self.rotated = False
        self.image = load_image('pics/wheel.png')
        self.rect = self.image.get_rect(topleft = (self.x, self.y))
        self.image_rotated = load_image('pics/wheel_45.png')
        self.image_start_pipe = load_image('pics/pipes/pipe_start.png')

        screen = pygame.display.get_surface()
        screen.blit(self.image, (self.x, self.y))
        screen.blit(self.image_start_pipe, (self.x, self.y + PIPE_SIZE)) # starting pipe below the wheel

    def spin(self):
        """Spins wheel and fills starting pipe with water"""
        if self.rotated:
            return
        screen = pygame.display.get_surface()
        screen.blit(BACKGROUND, (self.x, self.y), area = self.rect)
        screen.blit(self.image_rotated, (self.x, self.y))
        pygame.display.flip()

        # animation
        water_img = load_image('pics/pipes/water_pipe_start.png')
        for i in range(11):
            pygame.time.wait(ANIMATION_FPS)
            screen.blit(water_img, (self.x, self.y + PIPE_SIZE),
                        area = pygame.Rect(i * PIPE_SIZE, 0, PIPE_SIZE, PIPE_SIZE))
            pygame.display.flip()

        self.rotated = True


class Plant:
    """Plant able to grow"""
    def __init__(self, x, y):
        """Initializes plant and render it to the screen"""
        self.image = load_image('pics/cactus/cactus60.png')
        self.x = int(x)
        self.y = int(y)
        self.grown = False
        screen = pygame.display.get_surface()
        screen.blit(self.image, (self.x, self.y))

    def grow(self):
        if self.grown:
            return
        plant_files = ['cactus80.png', 'cactus110.png', 'cactus130_smile.png']

        # animation
        screen = pygame.display.get_surface()

        for i in range(len(plant_files)):
            screen.blit(BACKGROUND, (self.x, self.y),
                        area = self.image.get_rect(topleft = (self.x, self.y)))
            new_img = load_image('pics/cactus/' + plant_files[i])
            screen.blit(new_img, (self.x, self.y))
            pygame.display.flip()
            pygame.time.wait(ANIMATION_FPS * 2)
        pygame.time.wait(ANIMATION_FPS * 10)

        self.grown = True


class Tap:
    """Tap and water animation"""
    def __init__(self, x, y):
        """Initializes tap and render it to the screen"""
        self.x = int(x)
        self.y = int(y)
        self.used = False
        self.image = load_image('pics/tap/tap.png')
        screen = pygame.display.get_surface()
        screen.blit(self.image, (x, y))

    def water(self):
        if self.used:
            return
        water_files = ['water_1_tap.png', 'water_2_tap.png', 'water_3_tap.png']

        # animation
        screen = pygame.display.get_surface()
        for i in range(len(water_files)):
            new_img = load_image('pics/tap/' + water_files[i])
            screen.blit(new_img, (self.x, self.y))
            pygame.display.flip()
            pygame.time.wait(ANIMATION_FPS * 3)
            screen.blit(BACKGROUND, (self.x, self.y),
                        area = new_img.get_rect(topleft = (self.x, self.y)))

        pygame.time.wait(ANIMATION_FPS)

        screen.blit(self.image, (self.x, self.y))
        pygame.display.flip()

        self.used = True


class Button:
    """Text button to click"""
    def __init__(self, x, y, text):
        self.x = int(x)
        self.y = int(y)
        font = pygame.font.Font(None, 100)
        self.text_surface = font.render(text, True, pygame.Color('Black'))
        self.rect = self.text_surface.get_rect(topleft = (self.x, self.y))
        screen = pygame.display.get_surface()
        screen.blit(self.text_surface, self.rect)


################# functions #################

def load_image(name, angle = 0):
    """
    Loads image from file and optionally rotates it by given angle.
    Returns surface object and bounding rectangle.
    """
    image = pygame.image.load(name)
    if angle:
        image = pygame.transform.rotate(image, -angle) # rotates clockwise
    return image


def start_point(df):
    """
    Calculates coorditates in order to center levels of different size on the screen.
    df - pandas data frame representing level
    Returns x and y coords for start point (wheel).
    """
    max_x, max_y = df.x.max() + 1, df.y.max() + 1
    width_blocks = SCREEN_WIDTH / PIPE_SIZE
    height_blocks = SCREEN_HEIGHT / PIPE_SIZE

    if max_x > width_blocks or max_y > height_blocks:
        print('Too large level')
        raise SystemExit(str(geterror()))

    start_x = int((width_blocks - max_x) / 2 * PIPE_SIZE)
    start_y = int((height_blocks - max_y) / 2 * PIPE_SIZE)

    return start_x, start_y


def load_level(level_nr):
    """
    Loads pipes positions from csv file for given level, creates objects
    for them and renders to the screen.
    Returns list of clickable objects (pipes, wheel), tap and plant.
    """
    df = pd.read_csv('levels/pipes_level_' + str(level_nr) + '.csv')
    start_x, start_y = start_point(df)
    df_pipes = df.loc[df.type == 'pipe']

    obj_clickable = []

    for row in range(df_pipes.shape[0]):
        down, up, left, right = df_pipes.iloc[row,3:]
        obj_clickable.append(Pipe(
        x = start_x + df_pipes.iloc[row, 1] * PIPE_SIZE,
        y = start_y + df_pipes.iloc[row, 2] * PIPE_SIZE,
        down = down, up = up, left = left, right = right
        ))
    obj_clickable.append(Wheel(
    x = start_x + df.loc[df.type == 'wheel'].x * PIPE_SIZE,
    y = start_y + df.loc[df.type == 'wheel'].y * PIPE_SIZE
    ))

    plant = Plant(
    x = start_x + df.loc[df.type == 'plant'].x * PIPE_SIZE,
    y = start_y + df.loc[df.type == 'plant'].y * PIPE_SIZE
    )
    tap = Tap(
    x = start_x + df.loc[df.type == 'tap'].x * PIPE_SIZE,
    y = start_y + df.loc[df.type == 'tap'].y * PIPE_SIZE
    )

    return obj_clickable, tap, plant


def opposite(direction):
    if direction == 'left':
        return 'right'
    elif direction == 'right':
        return 'left'
    elif direction == 'up':
        return 'down'
    elif direction == 'down':
        return 'up'


def next_pipe(end, pipe1, obj_clickable, tap):
    """
    Ckecks if there is proper pipe after pipe1
    end - string, one of (up, right, down, left)
    """

    # find (x,y) coords required for the next pipe
    if end == 'up':
        x = pipe1.x
        y = pipe1.y - PIPE_SIZE
    elif end == 'right':
        x = pipe1.x + PIPE_SIZE
        y = pipe1.y
    elif end == 'down':
        x = pipe1.x
        y = pipe1.y + PIPE_SIZE
    elif end == 'left':
        x = pipe1.x - PIPE_SIZE
        y = pipe1.y

    if isinstance(pipe1, Wheel):
        y += PIPE_SIZE

    # check if there is proper object on that position
    for obj in obj_clickable:
        if (obj.x == x and obj.y == y):
            if isinstance(obj, Pipe):

                # is hole compatible?
                if (end == 'up' and obj.down) or (end == 'right' and obj.left) or (end == 'down' and obj.up) or (end == 'left' and obj.right):
                    if not obj.filled:
                        obj.start = opposite(end)
                        obj.fill_end()
                        return True, obj

                else: # not compatibile ends
                    return False, None

            else: # wheel
                return False, None

    if tap.x == x and tap.y == y:
        if end == 'right':
            return True, tap

    return False, None


def start_water(wheel, obj_clickable, tap, plant):
    """Checks if level is correct, returns bool"""

    ok, current_pipe = next_pipe('right', wheel, obj_clickable, tap)
    if not ok:
        return False

    while(ok):

        if isinstance(current_pipe, Tap):
            if not current_pipe.used:
                current_pipe.water()
                plant.grow()
                return True

        current_pipe.fill_water()

        ok, current_pipe = next_pipe(current_pipe.end, current_pipe, obj_clickable, tap)

    return False


################### screens #####################

def play_level(nr):
    """Returns boolean - if level was correctly finished or not"""

    # add background and objects
    screen = pygame.display.get_surface()
    screen.blit(BACKGROUND, (0,0))
    obj_clickable, tap, plant = load_level(nr)
    pygame.display.flip() # refresh display

    # test
    # pygame.time.wait(ANIMATION_FPS * 15)
    # return True
    # end test

    # variables
    moves = 0
    can_click = True

    # main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif can_click and event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                for obj in obj_clickable:
                    if obj.rect.collidepoint(mx, my):
                        if isinstance(obj, Pipe):
                            obj.rotate()
                            moves += 1
                            break
                        elif isinstance(obj, Wheel):
                            can_click = False
                            obj.spin()
                            game = start_water(obj, obj_clickable, tap, plant)
                            running = False

    return game


def start_screen():
    """Returns boolean - start game or quit"""

    # add background and buttons
    screen = pygame.display.get_surface()
    screen.fill((254, 196, 79))

    font = pygame.font.Font(None, 200)
    hello = font.render('PLUMBER GAME', True, pygame.Color('Black'))
    screen.blit(hello, hello.get_rect(center = (SCREEN_WIDTH/2, 150)))

    start_button = Button(SCREEN_WIDTH/5, SCREEN_HEIGHT/3*2, "PLAY")
    quit_button = Button(SCREEN_WIDTH/5 * 3, SCREEN_HEIGHT/3*2, "QUIT")

    pygame.display.flip()

    # main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if start_button.rect.collidepoint(mx, my):
                    return True
                elif quit_button.rect.collidepoint(mx, my):
                    return False


def winning_screen():
    """Returns boolean - move to next level or quit"""

    # add background and buttons
    screen = pygame.display.get_surface()
    screen.fill((40, 150, 40))

    font = pygame.font.Font(None, 200)
    you_win = font.render('CONGRATULATIONS!', True, pygame.Color('Black'))
    screen.blit(you_win, you_win.get_rect(center = (SCREEN_WIDTH/2, 150)))

    next_level = Button(SCREEN_WIDTH/5, SCREEN_HEIGHT/3*2, "NEXT LEVEL")
    quit = Button(SCREEN_WIDTH/5 * 3, SCREEN_HEIGHT/3*2, "QUIT")

    pygame.display.flip()

    # main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if next_level.rect.collidepoint(mx, my):
                    return True
                elif quit.rect.collidepoint(mx, my):
                    return False


def losing_screen():
    """Returns boolean - try again this level or not"""
    screen = pygame.display.get_surface()
    screen.fill((150, 40, 40))

    font = pygame.font.Font(None, 200)
    you_lost = font.render('YOU LOST :(', True, pygame.Color('Black'))
    screen.blit(you_lost, you_lost.get_rect(center = (SCREEN_WIDTH/2, 150)))

    try_again = Button(SCREEN_WIDTH/5, SCREEN_HEIGHT/3*2, "TRY AGAIN")
    quit = Button(SCREEN_WIDTH/5 * 3, SCREEN_HEIGHT/3*2, "QUIT")

    pygame.display.flip()

    # main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if try_again.rect.collidepoint(mx, my):
                    return True
                elif quit.rect.collidepoint(mx, my):
                    return False


def trophy_screen():
    """Returns nothing, ends after click anywhere"""

    # add background and trophy
    screen = pygame.display.get_surface()
    screen.fill((255, 247, 188))

    font1 = pygame.font.Font(None, 180)
    hello1 = font1.render('CONGRATULATIONS', True, pygame.Color('Black'))
    screen.blit(hello1, hello1.get_rect(center = (SCREEN_WIDTH/2, 110)))

    font2 = pygame.font.Font(None, 80)
    hello2 = font2.render('You finished all levels.', True, pygame.Color('Black'))
    screen.blit(hello2, hello2.get_rect(center = (SCREEN_WIDTH/2, 210)))

    trophy = load_image('pics/trophy.png')
    rect = trophy.get_rect(center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 130))
    screen = pygame.display.get_surface()
    screen.blit(trophy, rect)

    pygame.display.flip()

    # main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return


def main():

    # initialize window
    pygame.init()
    clock = pygame.time.Clock()
    logo = pygame.image.load('pics/logo.png')
    pygame.display.set_icon(logo)
    pygame.display.set_caption('Plumber')
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # start screen
    start_game = start_screen()
    if not start_game:
        pygame.quit()
        quit()

    # levels and winning/losing screens
    i = 1
    while(1 <= MAX_LEVEL):

        game = play_level(i)

        if game:
            if i == MAX_LEVEL:
                break
            next = winning_screen()
            if next:
                i += 1
                continue
            else:
                pygame.quit()
                quit()

        else:
            next = losing_screen()
            if not next:
                pygame.quit()
                quit()

    # trophy screen
    trophy_screen()

    pygame.quit()
    quit()


if __name__ == '__main__':
    main()
