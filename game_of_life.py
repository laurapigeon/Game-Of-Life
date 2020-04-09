import pygame
import random

pygame.init()


class Board:
    def __init__(self, screen_dims):
        self.tile_dims = TILE_DIMS
        self.update_dimensions(screen_dims)

    def update_dimensions(self, screen_dims):
        self.new_columns = screen_dims[0] // self.tile_dims[0]
        self.new_rows = screen_dims[1] // self.tile_dims[1]

    def get_size(self, old=False):
        if old:
            return (self.columns * self.tile_dims[0], self.rows * self.tile_dims[1])
        else:
            return (self.new_columns * self.tile_dims[0], self.new_rows * self.tile_dims[1])

    def flip_tile(self, coords):
        board_size = self.get_size(old=True)
        if coords[0] < board_size[0] and coords[1] < board_size[1]:
            coords[0] //= self.tile_dims[0]
            coords[1] //= self.tile_dims[1]
            self.tiles[coords[1]][coords[0]].change_type(flip=True)

    def populate(self, percentage=0.5, seed=None):
        self.tiles = []
        self.living_cells = 0
        self.generation = 0
        self.columns = self.new_columns
        self.rows = self.new_rows

        dimensions_string = str(self.columns) + "x" + str(self.rows)
        if type(percentage) in (int, float):
            percentage_string = str(percentage * 100) + "% density"
        else:
            percentage_string = percentage
        mode_code = "b" + "".join([str(num) for num in RULES[mode][0]]) + "s" + "".join([str(num) for num in RULES[mode][1]])
        mode_string = "{}-Type Mode: {} ({})".format(RULES[mode][3], RULES[mode][2], mode_code)
        if OUTPUT_TO_FILE is not False:
            open("population.txt", "w").write(dimensions_string + " " + percentage_string + " " + mode_string)

        colour_combo = list(range(5))
        random.shuffle(colour_combo)

        random.seed(seed)
        for y in range(self.rows):
            row = []
            for x in range(self.columns):
                colours = (round(x * 255 / self.columns),
                           round(y * 255 / self.rows),
                           255 - round(x * 255 / self.columns),
                           255 - round(y * 255 / self.rows),
                           255)
                colour = (colours[colour_combo[0]], colours[colour_combo[1]], colours[colour_combo[2]])

                if percentage == "checkerboard":
                    tile_state = (x + y) % 2 == 1
                elif percentage == "lines":
                    tile_state = x % 2 == 1
                elif percentage == "edges":
                    tile_state = x == 0 or x == self.columns - 1 or y == 0 or y == self.rows - 1
                else:
                    tile_state = random.random() < percentage

                self.living_cells += (-1, 1)[tile_state]
                row.append(Tile(self, tile_state, (x, y), colour))

            self.tiles.append(row)

        if OUTPUT_TO_FILE is not False:
            if OUTPUT_TO_FILE == "cells":
                open("population.txt", "a").write("\n" + str(self.living_cells))
            elif OUTPUT_TO_FILE == "percentage":
                size = self.get_size(old=True)
                open("population.txt", "a").write("\n" + str(round(100 * self.living_cells / self.columns / self.rows, 2)))

    def neighbor_check(self):
        for row in self.tiles:
            for tile in row:
                x = tile.column
                y = tile.row
                neighbors = list()
                if x != 0:
                    neighbors.append(self.tiles[y][x - 1])
                if x != self.columns - 1:
                    neighbors.append(self.tiles[y][x + 1])

                if y != 0:
                    neighbors.append(self.tiles[y - 1][x])
                if y != self.rows - 1:
                    neighbors.append(self.tiles[y + 1][x])

                if x != 0 and y != 0:
                    neighbors.append(self.tiles[y - 1][x - 1])
                if x != self.columns - 1 and y != self.rows - 1:
                    neighbors.append(self.tiles[y + 1][x + 1])

                if x != 0 and y != self.rows - 1:
                    neighbors.append(self.tiles[y + 1][x - 1])
                if x != self.columns - 1 and y != 0:
                    neighbors.append(self.tiles[y - 1][x + 1])

                tile.check_neighbors(neighbors)

    def update_tiles(self):
        for row in self.tiles:
            for tile in row:
                tile.change_type()
        if OUTPUT_TO_FILE is not False:
            if OUTPUT_TO_FILE == "value":
                open("population.txt", "a").write("\n" + str(self.living_cells))
            elif OUTPUT_TO_FILE == "percentage":
                open("population.txt", "a").write("\n" + str(round(100 * self.living_cells / self.columns / self.rows, 2)))
        self.generation += 1

    def draw_tiles(self):
        for row in self.tiles:
            for tile in row:
                if tile.state:
                    rect = tile.get_rect()
                    pygame.draw.rect(screen, tile.get_colour(), rect)

    def draw(self):
        size = self.get_size(old=True)
        rect = pygame.Rect(-1, -1, size[0] + 2, size[1] + 2)
        pygame.draw.rect(screen, (255, 255, 255), rect, 1)


class Tile:
    def __init__(self, board, state, pos, colour):
        self.board = board
        self.state = state  # 0 as dead, 1 as live
        self.colour = colour
        self.column = pos[0]
        self.row = pos[1]

    def change_type(self, flip=False):
        if flip:  # for clicking on individual cells
            self.state = 1 - self.state
            self.board.living_cells += (-1, 1)[self.state]
        else:  # for editing all cells at once
            self.state = self.new_state

    def check_neighbors(self, neighbors):
        alive_neighbors = 0
        for neighbor in neighbors:
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
    def get_surface(string, frame=None, print_string=True):
        if DISPLAY_TEXT:
            return {"surface": FONT.render(string, True, (255, 255, 255)),
                    "size": FONT.size(string),
                    "birthframe": frame}
        else:
            if print_string:
                print(string)
            return None

    @staticmethod
    def display_surface(surface, board, location, frame=None):
        if surface is not None:
            rect = pygame.Rect(0, 0, *surface["size"])
            if location == "bottomright":
                rect.bottomright = board.get_size()
            elif location == "bottomleft":
                rect.bottomleft = (0, board.get_size()[1])
            elif location == "topright":
                rect.topright = (board.get_size()[0], 0)
            elif location == "topleft":
                rect.topleft = (0, 0)

            screen.blit(surface["surface"], rect)

            if surface["birthframe"] is not None and frame is not None:
                if frame - surface["birthframe"] >= 60:
                    return None
                else:
                    return surface
        else:
            return None


#region definitions
TILE_DIMS = (10, 10)
SCREEN_DIMS = (1080, 720)
FIXED_DIMS = False
COLOUR = True
DISPLAY_TEXT = True
OUTPUT_TO_FILE = "value"  # None, "value" or "percentage"
SEED = 44
MAX_FRAMERATE = 30
DEFAULT_SLOW_AMOUNT = 1
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
        [[3, 6, 7, 8], [3, 4, 6, 7, 8],             "Day & Night",        "Life"],
]
DEFAULT_MODE = 7
FONT = pygame.font.SysFont("Calibri", round(board.get_size()[1] / 20))

board = Board(SCREEN_DIMS)
board.populate(0, seed=SEED)
slow_amount = DEFAULT_SLOW_AMOUNT
mode = DEFAULT_MODE
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
            if FIXED_DIMS:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            else:
                board.update_dimensions((event.w, event.h))
                FONT = pygame.font.SysFont("Calibri", round(board.get_size()[1] / 20))
                screen = pygame.display.set_mode(board.get_size(), pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pause = not pause
                text_surface = ScreenPrint.get_surface(("Unpaused", "Paused")[pause], frame)

            if event.key == pygame.K_RETURN and pause:
                board.neighbor_check()
                board.update_tiles()
                text_surface = ScreenPrint.get_surface("Frame advanced", frame)

            if event.key in (pygame.K_PERIOD, pygame.K_COMMA):
                if event.unicode == "." and slow_amount > 1.5:
                    slow_amount -= 1
                elif event.unicode == "," and slow_amount < MAX_FRAMERATE - 0.5:
                    slow_amount += 1
                text_surface = ScreenPrint.get_surface("{} frames per second".format(round(MAX_FRAMERATE / slow_amount, 1)), frame)

            if event.key in (pygame.K_EQUALS, pygame.K_MINUS):
                if event.unicode == "=":
                    mode += 1
                else:
                    mode -= 1
                mode %= len(RULES)
                mode_code = "b" + "".join([str(num) for num in RULES[mode][0]]) + "s" + "".join([str(num) for num in RULES[mode][1]])
                mode_string = "{}-Type Mode: {} ({})".format(RULES[mode][3], RULES[mode][2], mode_code)
                if OUTPUT_TO_FILE is not False:
                    open("population.txt", "a").write("\nMode changed to " + mode_string)
                text_surface = ScreenPrint.get_surface(mode_string, frame)

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
            if event.button == 1:
                coords = list(pygame.mouse.get_pos())
                board.flip_tile(coords)
    #endregion

    if frame % slow_amount == 0:
        screen.fill((0, 0, 0))
        board.draw_tiles()
        board.draw()

        if DISPLAY_TEXT:
            text_surface = ScreenPrint.display_surface(text_surface, board, "bottomright", frame=frame)

        ScreenPrint.display_surface(ScreenPrint.get_surface(str(board.generation), print_string=False), board, "bottomleft")

        pygame.display.flip()

        if not pause:
            board.neighbor_check()
            board.update_tiles()

    frame += 1

    if MAX_FRAMERATE is not None:
        clock.tick(MAX_FRAMERATE)
