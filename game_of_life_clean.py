from pygame.math import Vector2 as Vector
import pygame
import random
pygame.init()


class Board:
    def __init__(self, parent, tile_dims, grid, borders=Vector(0, 0), offset=Vector(0, 0), colour=(100, 100, 100), border_colour=(200, 200, 200)):
        self.parent = parent  # the surface the board is on

        self.tile_dims = tile_dims
        self.grid = grid
        self.update_dims("dims")  # creates the dims attribute

        self.borders = borders
        self.offset = offset
        self.due_rect_update = True  # gives the board and tiles attributes for drawing
        self.due_draw = True

        self.colour = colour
        self.border_colour = border_colour

        self.populate(0)  # fills the board with tiles

    def set_value(self, key_value_pair, fix_key=None, change=False):
        if change:
            new_value = self.__dict__[key_value_pair[0]] + key_value_pair[1]
        else:
            new_value = key_value_pair[1]

        keys = ["grid", "dims", "tile_dims"]  # possible changes to the graphics of the board
        outbound_dims = key_value_pair[0] in keys and (new_value.x <= 0 or new_value.y <= 0)  # values of 0 or below produce error
        outbound_borders = key_value_pair[0] == "borders" and (new_value.x < 0 or new_value.y < 0)  # values below 0 not wanted
        if outbound_dims or outbound_borders:
            wordset = (("set", "to"), ("change", "by"))[change]
            print("Could not {} {} {} {}.".format(wordset[0], key_value_pair[0], wordset[1], key_value_pair[1]))
        else:
            self.__dict__[key_value_pair[0]] = new_value
            if key_value_pair[0] in keys and fix_key in keys:  # all keys
                keys.remove(key_value_pair[0])  # - changed key
                keys.remove(fix_key)  # - fixed key
                self.update_dims(keys[0])  # = key to be changed to account for new value
            if key_value_pair[0] == "grid":
                self.populate(0)  # newly populate grid if the number of rows or columns changes
            self.due_rect_update = True  # update rects to account for changes
            self.due_draw = True

    def update_dims(self, change_key):
        if change_key == "dims":
            self.dims = self.grid * self.tile_dims.elementwise()
        elif change_key == "grid":
            self.grid = self.dims // self.tile_dims.elementwise()
            self.populate(0)  # newly populate grid if the number of rows or columns changes
        elif change_key == "tile_dims":
            self.tile_dims = self.dims // self.grid.elementwise()

    def update_rect(self):
        parent_dims = Vector(self.parent.get_rect().size)
        board_top_left = v_round(self.borders / 2 * self.tile_dims.elementwise())
        rect_top_left = v_round((parent_dims - self.dims) / 2 + (self.offset - self.borders / 2) * self.tile_dims.elementwise())
        board_dims = v_round(self.dims)
        rect_dims = v_round(self.dims + self.borders * self.tile_dims.elementwise())

        self.rect_on_parent = pygame.Rect(rect_top_left, rect_dims)  # rect for blitting board surface onto parent
        self.rect_on_self = pygame.Rect(board_top_left, board_dims)  # rect for drawing board
        self.surface = pygame.Surface(rect_dims)  # surface for drawing tiles

        self.update_tile_rects()  # mark tiles on board for rect updates

        self.due_rect_update = False  # done updating rect

    def update_tile_rects(self):
        for row in self.tiles:
            for tile in row:
                tile.due_rect_update = True

    def update_tile_states(self):
        for row in self.tiles:
            for tile in row:
                tile.update_state()

    def set_tile_neighbors(self):
        for row in self.tiles:
            for tile in row:
                tile.set_neighbors()

    def check_tile_neighbors(self):
        for row in self.tiles:
            for tile in row:
                tile.check_neighbors()

    def update_ants(self):
        for ant in self.ants:
            ant.update()

    def populate(self, percentage, ant_rules=[], seed=None):

        random.seed(seed)

        self.ants = list()
        for i in range(len(ant_rules)):
            facing = (Vector(1, 0), Vector(0, -1), Vector(-1, 0), Vector(0, 1))[random.randint(0, 3)]
            self.ants.append(Ant(self, facing, Vector(random.randint(0, self.grid.x - 1), random.randint(0, self.grid.y - 1)), random.randint(0, 5), ant_rules[i]))

        self.tiles = list()
        for row_num in range(int(self.grid.y)):
            row = list()
            for column_num in range(int(self.grid.x)):
                state = random.random() < percentage
                row.append(Tile(self, state, Vector(column_num, row_num)))
            self.tiles.append(row)

        if seed is not None:
            random.seed(None)

        self.set_tile_neighbors()

        self.due_draw = True

    def draw(self):
        if self.due_rect_update:
            self.update_rect()  # update rect if needed before drawn
        self.surface.fill(self.border_colour)  # borders outside rect_on_self area
        pygame.draw.rect(self.surface, self.colour, self.rect_on_self)  # area covered by tiles

        self.draw_tiles()

        self.draw_ants()

        self.due_draw = False

    def blit(self):
        self.parent.blit(self.surface, self.rect_on_parent.topleft)  # blit board onto surface

    def draw_tiles(self):
        for row in self.tiles:
            for tile in row:
                tile.draw()  # draw tiles on board

    def draw_ants(self):
        for ant in self.ants:
            ant.draw()


class Tile:
    def __init__(self, board, initial_state, pos, colour=(255, 255, 255)):
        self.board = board
        self.state = initial_state
        self.pos = pos  # position in grid
        self.due_rect_update = True  # due to have rect updated
        self.due_draw = False
        self.live_colour = colour
        self.dead_colour = [255 - colour[0], 255 - colour[1], 255 - colour[2]]

    def update_rect(self):
        if self.board.tile_dims.x > 16 and self.board.tile_dims.y > 16 and TILE_BORDERS:  # for pixel cell border
            rect_top_left = v_round(Vector(1, 1) + (self.pos + self.board.borders / 2) * self.board.tile_dims.elementwise())
            rect_dims = v_round(Vector(-2, -2) + self.board.tile_dims)
        else:
            rect_top_left = v_round((self.pos + self.board.borders / 2) * self.board.tile_dims.elementwise())
            rect_dims = v_round(self.board.tile_dims)

        screen_rect_top_left = self.board.rect_on_parent.move(rect_top_left).topleft  # tile rect relative to screen

        self.rect_on_screen = pygame.Rect(screen_rect_top_left, rect_dims)  # for detecting if on screen
        self.rect_on_board = pygame.Rect(rect_top_left, rect_dims)  # for drawing cells on board

        self.due_rect_update = False  # done updating rect

    def update_state(self):
        self.state = self.new_state
        if self.due_draw:
            self.draw()

    def set_neighbors(self):
        bot_x = round((self.pos.x - 1) % self.board.grid.x)
        mid_x = round((self.pos.x))
        top_x = round((self.pos.x + 1) % self.board.grid.x)
        bot_y = round((self.pos.y - 1) % self.board.grid.y)
        mid_y = round((self.pos.y))
        top_y = round((self.pos.y + 1) % self.board.grid.y)

        self.neighbors = [
            self.board.tiles[bot_y][bot_x],
            self.board.tiles[mid_y][bot_x],
            self.board.tiles[top_y][bot_x],
            self.board.tiles[bot_y][mid_x],
            self.board.tiles[top_y][mid_x],
            self.board.tiles[bot_y][top_x],
            self.board.tiles[mid_y][top_x],
            self.board.tiles[top_y][top_x]
        ]

    def check_neighbors(self):
        live_neighbors = 0
        for neighbor in self.neighbors:
            live_neighbors += neighbor.state

        if self.state == 0:
            if live_neighbors in RULES[mode][0]:
                self.new_state = 1
                self.due_draw = True
            else:
                self.new_state = 0
        else:
            if live_neighbors in RULES[mode][1]:
                self.new_state = 1
            else:
                self.new_state = 0
                self.due_draw = True

    def draw(self):
        if self.due_rect_update:
            self.update_rect()  # update rects that need it before theyre drawn

        within_x = self.rect_on_screen.right >= 0 and self.rect_on_screen.left <= self.board.parent.get_rect().right
        within_y = self.rect_on_screen.bottom >= 0 and self.rect_on_screen.top <= self.board.parent.get_rect().bottom
        if within_x and within_y:  # tile is only drawn to board if on screen
            colour = (self.dead_colour, self.live_colour)[self.state]
            pygame.draw.rect(self.board.surface, colour, self.rect_on_board)

            self.due_draw = False


class Ant:
    colours = ((164, 255, 164), (255, 255, 164), (255, 164, 164), (255, 164, 255), (164, 164, 255), (164, 255, 255))

    def __init__(self, board, facing, pos, colour, rules):
        self.board = board
        self.facing = facing
        self.pos = pos
        self.colour = self.colours[colour]
        self.rules = rules

    def update(self):
        tile = self.board.tiles[int(self.pos.y)][int(self.pos.x)]
        self.facing.rotate_ip(self.rules[tile.state])
        tile.state = 1 - tile.state
        tile.draw()
        self.move()
        self.draw()

    def move(self):
        self.pos += self.facing
        self.pos %= self.board.grid.elementwise()

    def get_rect(self):
        rect_top_left = v_round((self.pos + self.board.borders / 2) * self.board.tile_dims.elementwise())
        rect_dims = v_round(self.board.tile_dims)
        return pygame.Rect(rect_top_left, rect_dims)  # for drawing cells on board

    def draw(self):
        pygame.draw.rect(self.board.surface, (255, 0, 0), self.get_rect())


def v_round(vector):  # takes a Vector instance and returns a rounded tuple
    return (round(vector.x), round(vector.y))


DEFUAULT_SCREEN_DIMS = (1920, 1030)
screen = pygame.display.set_mode(DEFUAULT_SCREEN_DIMS, pygame.RESIZABLE)
clock = pygame.time.Clock()

TILE_BORDERS = False
SEED = None

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
DEFAULT_MODE = 14  # default rule of the program
mode = DEFAULT_MODE

board = Board(screen, tile_dims=Vector(5, 5), grid=Vector(382, 206), borders=Vector(2, 2))
board.populate(0)

# grid (columns/rows), tile_dims (width/height), dims (width/height) (any two of the 3 for a desired effect)
# board.set_value(("key_to_change", value), "key_to_fix", change=True)

left_click_held = False
done = False

while not done:
    events = pygame.event.get()
    keys_pressed = pygame.key.get_pressed()
    for event in events:
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.VIDEORESIZE:  # screen resize by dragging edges of window
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            board.due_rect_update = True  # board.set_value() not needed as board.parent is dynamic
            board.due_draw = True

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_EQUALS, pygame.K_MINUS):  # change number of rows and columns
                if keys_pressed[pygame.K_LSHIFT]:
                    magnitude = 100
                else:
                    magnitude = 10
                if event.key == pygame.K_EQUALS:
                    board.set_value(("grid", Vector(magnitude, magnitude)), "tile_dims", change=True)
                elif event.key == pygame.K_MINUS:
                    board.set_value(("grid", Vector(-magnitude, -magnitude)), "tile_dims", change=True)

            if event.key in (pygame.K_PERIOD, pygame.K_COMMA):  # change border widths
                if event.key == pygame.K_PERIOD:
                    mode += 1
                elif event.key == pygame.K_COMMA:
                    mode -= 1
                mode %= len(RULES)

            if event.unicode in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                ants = list()
                for i in range(100):
                    ants.append((0, 90))
                    ants.append((90, 0))
                board.populate(int(event.unicode) / 10, ants, seed=SEED)

        elif event.type == pygame.MOUSEBUTTONDOWN:  # begin dragging board
            if event.button == 1:
                left_click_held = True
                pygame.mouse.get_rel()  # clear current relative mouse movement

            elif event.button in (4, 5):  # zoom board (by changing tile dimensions)
                if event.button == 4:
                    board.set_value(("tile_dims", Vector(1, 1)), "grid", change=True)
                elif event.button == 5:
                    board.set_value(("tile_dims", Vector(-1, -1)), "grid", change=True)

        elif event.type == pygame.MOUSEBUTTONUP:  # end dragging board
            if event.button == 1:
                left_click_held = False

        elif event.type == pygame.MOUSEMOTION and left_click_held:  # append relative mouse motion to board offset
            board.set_value(("offset", Vector(pygame.mouse.get_rel()) / board.tile_dims.elementwise()), change=True)

    if board.due_draw:
        screen.fill((0, 0, 0))
        board.draw()

    board.blit()

    pygame.display.flip()

    board.check_tile_neighbors()
    board.update_tile_states()
    board.update_ants()

    clock.tick(60)
