import pygame
import random
import os

os.environ["SDL_VIDEO_WINDOW_POS"] = "0,30"

pygame.init()


class Board:
    def __init__(self, tile_dims, screen_dims):
        self.tile_dims = tile_dims
        self.update_dimensions(screen_dims)

    def update_dimensions(self, screen_dims):
        # new dimensions saved ready for next population
        self.new_columns = screen_dims[0] // self.tile_dims[0]
        self.new_rows = screen_dims[1] // self.tile_dims[1]

    def get_size(self, old=False):
        if old:  # whether to pass the current set of dimensions or the new set (screen rect)
            return (self.columns * self.tile_dims[0], self.rows * self.tile_dims[1])
        else:
            return (self.new_columns * self.tile_dims[0], self.new_rows * self.tile_dims[1])

    def flip_tile(self, coords):
        # for when tile is clicked
        board_size = self.get_size(old=True)
        if coords[0] < board_size[0] and coords[1] < board_size[1]:
            coords[0] //= self.tile_dims[0]
            coords[1] //= self.tile_dims[1]
            self.tiles[coords[1]][coords[0]].change_type(flip=True)

    def populate(self, percentage, seed=None):
        # update values
        self.tiles = []
        self.living_cells = 0
        self.generation = 0
        self.columns = self.new_columns
        self.rows = self.new_rows

        if OUTPUT_TO_FILE is not False:
            # empty and create title line for population.txt
            dimensions_string = str(self.columns) + "x" + str(self.rows)
            if type(percentage) in (int, float):
                percentage_string = str(percentage * 100) + "% density"
            else:
                percentage_string = percentage
            mode_code = "b" + "".join([str(num) for num in RULES[mode][0]]) + "s" + "".join([str(num) for num in RULES[mode][1]])
            mode_string = "{}-Type Mode: {} ({})".format(RULES[mode][3], RULES[mode][2], mode_code)
            seed_string = "seed: {} {}".format(type(seed), seed)
            open("population.txt", "w").write(dimensions_string + " " + percentage_string + " " + mode_string + " " + seed_string)

        random.seed(None)  # for always random colour

        colour_combo = list(range(5))
        random.shuffle(colour_combo)

        random.seed(seed)  # user-entered seed

        for y in range(self.rows):
            row = []
            for x in range(self.columns):
                # possible colour segments dependant on position
                colours = (round(x * 255 / self.columns),
                           round(y * 255 / self.rows),
                           255 - round(x * 255 / self.columns),
                           255 - round(y * 255 / self.rows),
                           255)
                # random 3 of the 5 possibilities
                colour = (colours[colour_combo[0]], colours[colour_combo[1]], colours[colour_combo[2]])

                # determine whether tile is living or dead
                if percentage == "checkerboard":
                    tile_state = (x + y) % 2 == 1
                elif percentage == "lines":
                    tile_state = x % 2 == 1
                elif percentage == "edges":
                    tile_state = x == 0 or x == self.columns - 1 or y == 0 or y == self.rows - 1
                else:
                    tile_state = random.random() < percentage

                self.living_cells += tile_state
                row.append(Tile(self, tile_state, (x, y), colour))

            self.tiles.append(row)

        for row in self.tiles:
            for tile in row:
                tile.update_neighbors()

    def neighbor_check(self):
        for row in self.tiles:
            for tile in row:
                tile.check_neighbors()

    def update_tiles(self):
        # append value to tile before changing tiles
        if OUTPUT_TO_FILE == "value":
            open("population.txt", "a").write("\n" + str(self.living_cells))
        elif OUTPUT_TO_FILE == "percentage":
            open("population.txt", "a").write("\n" + str(round(100 * self.living_cells / self.columns / self.rows, 2)))

        # tiles switched to their new state
        for row in self.tiles:
            for tile in row:
                tile.change_type()
        self.generation += 1

    def draw_tiles(self, surface):
        # draw each board tile on the surface
        for row in self.tiles:
            for tile in row:
                if tile.state:  # if living
                    rect = tile.get_rect()
                    pygame.draw.rect(surface, tile.get_colour(), rect)

    def draw(self, surface):
        # bounding box for board when surface size is different
        size = self.get_size(old=True)
        rect = pygame.Rect(-1, -1, size[0] + 2, size[1] + 2)
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)


class Tile:
    def __init__(self, board, state, pos, colour):
        self.board = board
        self.state = state  # 0 as dead, 1 as live
        self.colour = colour
        self.column = pos[0]
        self.row = pos[1]

    def update_neighbors(self):
        x = self.column
        y = self.row
        # creates neighbors based on position of tile
        if WRAPPING:
            bottom_x = (x - 1, self.board.columns - 1)[x == 0]
            top_x    = (x + 1, 0)[x == self.board.columns - 1]
            bottom_y = (y - 1, self.board.rows - 1)[y == 0]
            top_y    = (y + 1, 0)[y == self.board.rows - 1]

            self.neighbors = [self.board.tiles[y][bottom_x],
                              self.board.tiles[y][top_x],
                              self.board.tiles[bottom_y][x],
                              self.board.tiles[top_y][x],
                              self.board.tiles[bottom_y][bottom_x],
                              self.board.tiles[top_y][top_x],
                              self.board.tiles[top_y][bottom_x],
                              self.board.tiles[bottom_y][top_x]]

        else:
            self.neighbors = list()
            if x != 0:
                self.neighbors.append(self.board.tiles[y][x - 1])
            if x != self.board.columns - 1:
                self.neighbors.append(self.board.tiles[y][x + 1])

            if y != 0:
                self.neighbors.append(self.board.tiles[y - 1][x])
            if y != self.board.rows - 1:
                self.neighbors.append(self.board.tiles[y + 1][x])

            if x != 0 and y != 0:
                self.neighbors.append(self.board.tiles[y - 1][x - 1])
            if x != self.board.columns - 1 and y != self.board.rows - 1:
                self.neighbors.append(self.board.tiles[y + 1][x + 1])

            if x != 0 and y != self.board.rows - 1:
                self.neighbors.append(self.board.tiles[y + 1][x - 1])
            if x != self.board.columns - 1 and y != 0:
                self.neighbors.append(self.board.tiles[y - 1][x + 1])

    def change_type(self, flip=False):
        if flip:  # for clicking on individual cells
            self.state = 1 - self.state
            self.board.living_cells += (-1, 1)[self.state]
        else:  # for editing all cells at once
            self.state = self.new_state

    def check_neighbors(self):
        # change state based on ruleset and living neighbors
        alive_neighbors = 0
        for neighbor in self.neighbors:
            if neighbor.state == 1:
                alive_neighbors += 1

        if self.state == 0:
            if alive_neighbors in RULES[mode][0]:
                self.new_state = 1
                self.board.living_cells += 1
            else:
                self.new_state = 0
        else:
            if alive_neighbors in RULES[mode][1]:
                self.new_state = 1
            else:
                self.new_state = 0
                self.board.living_cells -= 1

    def get_rect(self):
        coords = (self.column * self.board.tile_dims[0], self.row * self.board.tile_dims[1])
        dimensions = (self.board.tile_dims[0], self.board.tile_dims[1])
        return pygame.Rect(*coords, *dimensions)

    def get_colour(self):
        if COLOUR:
            return self.colour
        else:
            return (255, 255, 255)


class ScreenPrint:
    @staticmethod
    def get_surface(string, location="bottomright", frame=None, print_string=True):
        # returns a dict of the text surface and rect and birth frame
        if DISPLAY_TEXT:
            rect = pygame.Rect(0, 0, *FONT.size(string))
            if location == "bottomright":
                rect.bottomright = board.get_size()
            elif location == "bottomleft":
                rect.bottomleft = (0, board.get_size()[1])
            elif location == "topright":
                rect.topright = (board.get_size()[0], 0)
            elif location == "topleft":
                rect.topleft = (0, 0)
            return {"surface": FONT.render(string, True, (255, 255, 255)),
                    "rect": rect,
                    "birthframe": frame}
        else:
            if print_string:
                print(string)
            return None

    @staticmethod
    def display_surface(surface, board, frame=None):
        # takes in and ages the curent priority surface
        if surface is not None:
            screen.blit(surface["surface"], surface["rect"])

            if surface["birthframe"] is not None and frame is not None:
                if frame - surface["birthframe"] >= 60:
                    return None
                else:
                    return surface
        else:
            return None


#region definitions
TILE_DIMS = (10, 10)  # the dimensions of each tile
SCREEN_DIMS = (1280, 720)  # the dimensions of the screen
board = Board(TILE_DIMS, SCREEN_DIMS)
FIXED_DIMS = False  # whether resising the window resizes the board (board resizes to screen when repopulated)

DISPLAY_TEXT = True  # whether to display text on screen
OUTPUT_TO_FILE = "value"  # None, "value" or "percentage" appended to population.txt when the program is run

MAX_FRAMERATE = 60  # maximum framerate the program runs at
DEFAULT_SLOW_AMOUNT = 2  # fraction of the max framerate the program runs at
slow_amount = DEFAULT_SLOW_AMOUNT

WRAPPING = True  # maps the screen onto a torus (left-right and top-bottom wrapping)
RULES = [
        [[1, 3, 5, 7], [1, 3, 5, 7],                "Replicator",         "Replication"],
        [[1, 3, 5, 7], [0, 2, 4, 6, 8],             "Fredkin",            "Replication"],
        [[2],          [],                          "Seeds",              "Seeder"],
        [[2],          [0],                         "Live Free or Die",   "Seeder"],
        [[3],          [0, 1, 2, 3, 4, 5, 6, 7, 8], "Life Without Death", "Picture"],
        [[3],          [1, 2, 3, 4],                "Mazectric",          "Picture"],
        [[3],          [1, 2, 3, 4, 5],             "Maze",               "Picture"],
        [[3],          [2, 3],                      "Conway's Life",      "Life"],
        [[3, 6],       [2, 3],                      "HighLife",           "Life"],
        [[3, 6, 8],    [2, 4, 5],                   "Move",               "Life"],
        [[3, 7],       [2, 3],                      "DryLife",            "Life"],
        [[3, 8],       [2, 3],                      "Pedestrian Life",    "Life"],
        [[3],          [1, 2],                      "Flock",              "Life"],
        [[3, 6],       [1, 2, 5],                   "2x2",                "Life"],
        [[3, 6, 7, 8], [3, 4, 6, 7, 8],             "Day & Night",        "Life"]
]  # possible sets of rules coded in
DEFAULT_MODE = 7  # default rule of the program
mode = DEFAULT_MODE

COLOUR = True  # random tile colour distribution
SEED = "nyaaa"  # seed to generate the random starting population
board.populate(0, seed=SEED)

FONT = pygame.font.SysFont("Calibri", round(board.get_size()[1] / 20))  # font for screen text
text_surface = None

pygame.display.set_caption("The Game of Life")
screen = pygame.display.set_mode(board.get_size(), pygame.RESIZABLE)
clock = pygame.time.Clock()
#endregion

done = False
pause = False
frame = 0

while not done:
    #region check_keys
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.VIDEORESIZE:
            if FIXED_DIMS:  # allows screen to any size regardless of board
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            else:  # locks screen size to nearest whole tile size and updates board
                board.update_dimensions((event.w, event.h))
                FONT = pygame.font.SysFont("Calibri", round(board.get_size()[1] / 20))
                screen = pygame.display.set_mode(board.get_size(), pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN:
            # pause
            if event.key == pygame.K_SPACE:
                pause = not pause
                text_surface = ScreenPrint.get_surface(("Unpaused", "Paused")[pause], "bottomright", frame)

            # frame advance
            if event.key == pygame.K_RETURN and pause:
                board.neighbor_check()
                board.update_tiles()
                text_surface = ScreenPrint.get_surface("Frame advanced", "bottomright", frame)

            # change fraction of max framerate
            if event.key in (pygame.K_EQUALS, pygame.K_MINUS):
                if event.unicode == "=" and slow_amount > 1.5:
                    slow_amount -= 1
                elif event.unicode == "-" and slow_amount < MAX_FRAMERATE - 0.5:
                    slow_amount += 1
                text_surface = ScreenPrint.get_surface("{} frames per second".format(round(MAX_FRAMERATE / slow_amount, 1)), "bottomright", frame)

            # change mode
            if event.key in (pygame.K_PERIOD, pygame.K_COMMA):
                if event.unicode == ".":
                    mode += 1
                else:
                    mode -= 1
                mode %= len(RULES)
                mode_code = "b" + "".join([str(num) for num in RULES[mode][0]]) + "s" + "".join([str(num) for num in RULES[mode][1]])
                mode_string = "{}-Type Mode: {} ({})".format(RULES[mode][3], RULES[mode][2], mode_code)
                if OUTPUT_TO_FILE is not False:
                    open("population.txt", "a").write("\nMode changed to " + mode_string)
                text_surface = ScreenPrint.get_surface(mode_string, "bottomright", frame)

            # populate board
            key = event.unicode
            if key == "c":
                board.populate("checkerboard")
            if key == "l":
                board.populate("lines")
            if key == "e":
                board.populate("edges")
            if key in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                board.populate(int(key) / 10, seed=SEED)

        if event.type == pygame.MOUSEBUTTONDOWN:
            # flip cell on click
            if event.button == 1:
                coords = list(pygame.mouse.get_pos())
                board.flip_tile(coords)
    #endregion

    # reduce calculations to every n frames
    if frame % slow_amount != 0 or slow_amount == 1:
        screen.fill((0, 0, 0))
        board.draw(screen)
        board.draw_tiles(screen)

        if DISPLAY_TEXT:
            text_surface = ScreenPrint.display_surface(text_surface, board, frame)

        ScreenPrint.display_surface(ScreenPrint.get_surface(str(board.generation), "bottomleft", print_string=False), board)

        pygame.display.flip()
    if (frame % slow_amount != 0 or slow_amount == 1) and not pause:
        board.neighbor_check()
        board.update_tiles()
        # cap framerate to avoid lagging
        if MAX_FRAMERATE is not None:
            clock.tick(MAX_FRAMERATE / slow_amount)

    frame += 1
