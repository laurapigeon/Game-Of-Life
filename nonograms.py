from pygame.math import Vector2 as Vector
import pygame
import random
pygame.init()


class Board:
    def __init__(self, parent, tile_dims, grid, borders=Vector(0, 0), offset=Vector(0, 0), colour=(100, 100, 100), border_colour=(100, 0, 0)):
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

    def get_collide_tile(self):
        for row in self.tiles:
            for tile in row:
                if tile.rect_on_screen.collidepoint(pygame.mouse.get_pos()):
                    return tile
        return None

    def update_tile_rects(self):
        for row in self.tiles:
            for tile in row:
                tile.due_rect_update = True

    def populate(self, percentage, seed=None):

        random.seed(seed)

        self.tiles = list()
        for row_num in range(int(self.grid.y)):
            row = list()
            for column_num in range(int(self.grid.x)):
                true_state = (1, 2)[random.random() < percentage]
                row.append(Tile(self, true_state, Vector(column_num, row_num)))
            self.tiles.append(row)

        if seed is not None:
            random.seed(None)

        self.set_numbers()

        self.due_draw = True

    def draw(self):
        if self.due_rect_update:
            self.update_rect()  # update rect if needed before drawn
        self.surface.fill(self.border_colour)  # borders outside rect_on_self area
        pygame.draw.rect(self.surface, self.colour, self.rect_on_self)  # area covered by tiles

        self.draw_tiles()

        for i, column_num in enumerate(self.column_nums):
            text = " ".join(str(num) for num in column_num)
            location = self.tiles[i][0].rect_on_screen.topleft
            location = (location[0] - self.tile_dims[0] * self.borders[0] / 2, location[1])

            rect = pygame.Rect(0, 0, *FONT.size(text))
            rect.topright = location
            surface = FONT.render(text, True, (255, 255, 255))

            screen.blit(surface, rect)

        for j, row_num in enumerate(self.row_nums):
            location = self.tiles[0][j].rect_on_screen.topleft
            location = (location[0], location[1] - self.tile_dims[1] * self.borders[1] / 2)

            rects = list()
            surfaces = list()
            for i, num in enumerate(row_num[::-1]):
                rect = pygame.Rect(0, 0, *FONT.size(str(num)))
                rect.bottomleft = (location[0], location[1] - i * (FONT_SIZE))
                rects.append(rect)
                surfaces.append(FONT.render(str(num), True, (255, 255, 255)))

            for rect, surface in zip(rects, surfaces):
                screen.blit(surface, rect)

        self.due_draw = False

    def set_numbers(self):
        self.column_nums = list()
        for x in range(int(self.grid[0])):
            self.column_nums.append(self.get_num_array(self.tiles[x]))
        self.row_nums = list()
        for y in range(int(self.grid[1])):
            row_of_tiles = list()
            for x in range(int(self.grid[0])):
                row_of_tiles.append(self.tiles[x][y])
            self.row_nums.append(self.get_num_array(row_of_tiles))

    @staticmethod
    def get_num_array(tile_array):
        state = False
        num_array = list()
        num = 0
        for tile in tile_array:
            if tile.true_state == 2:
                state = True
                num += 1
            if state and tile.true_state == 1:
                state = False
                num_array.append(num)
                num = 0
        if num != 0:
            num_array.append(num)
        return num_array

    def blit(self):
        self.parent.blit(self.surface, self.rect_on_parent.topleft)  # blit board onto surface

    def draw_tiles(self):
        for row in self.tiles:
            for tile in row:
                tile.draw()  # draw tiles on board


class Tile:
    def __init__(self, board, true_state, pos):
        self.board = board
        self.true_state = true_state
        self.state = 0
        self.pos = pos  # position in grid
        self.due_rect_update = True  # due to have rect updated
        self.due_draw = False

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

    def draw(self):
        if self.due_rect_update:
            self.update_rect()  # update rects that need it before theyre drawn

        within_x = self.rect_on_screen.right >= 0 and self.rect_on_screen.left <= self.board.parent.get_rect().right
        within_y = self.rect_on_screen.bottom >= 0 and self.rect_on_screen.top <= self.board.parent.get_rect().bottom
        if within_x and within_y:  # tile is only drawn to board if on screen
            colour = ((0, 0, 0), (127, 127, 127), (255, 255, 255))[self.true_state]
            pygame.draw.rect(self.board.surface, colour, self.rect_on_board)

            self.due_draw = False


def v_round(vector):  # takes a Vector instance and returns a rounded tuple
    return (round(vector.x), round(vector.y))


DEFUAULT_SCREEN_DIMS = (1366, 768)
screen = pygame.display.set_mode(DEFUAULT_SCREEN_DIMS, pygame.RESIZABLE)
clock = pygame.time.Clock()

TILE_BORDERS = True
SEED = None

board = Board(screen, tile_dims=Vector(40, 40), grid=Vector(15, 15), borders=Vector(1, 1))
board.populate(0)
# grid (columns/rows), tile_dims (width/height), dims (width/height) (any two of the 3 for a desired effect)
# board.set_value(("key_to_change", value), "key_to_fix", change=True)

FONT_SIZE = int(board.tile_dims[0] / 2)
FONT = pygame.font.SysFont("Calibri", FONT_SIZE)  # font for screen text
text_surface = None

due_tile = False
mouse_create = None
tiles = list()
middle_click_held = False
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
                    magnitude = 5
                else:
                    magnitude = 1
                if event.key == pygame.K_EQUALS:
                    board.set_value(("grid", Vector(magnitude, magnitude)), "tile_dims", change=True)
                elif event.key == pygame.K_MINUS:
                    board.set_value(("grid", Vector(-magnitude, -magnitude)), "tile_dims", change=True)

            if event.unicode in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                board.populate(int(event.unicode) / 10, seed=SEED)

        elif event.type == pygame.MOUSEBUTTONDOWN:  # begin dragging board
            if event.button in (1, 3):
                mouse_state = (None, 2, None, 1)[event.button]
                due_tile = True
            elif event.button == 2:
                middle_click_held = True
                pygame.mouse.get_rel()  # clear current relative mouse movement
            elif event.button in (4, 5):  # zoom board (by changing tile dimensions)
                if event.button == 4:
                    board.set_value(("tile_dims", Vector(2, 2)), "grid", change=True)
                elif event.button == 5:
                    board.set_value(("tile_dims", Vector(-2, -2)), "grid", change=True)
                FONT_SIZE = int(board.tile_dims[0] / 2)
                FONT = pygame.font.SysFont("Calibri", FONT_SIZE)  # font for screen text

        elif event.type == pygame.MOUSEBUTTONUP:  # end dragging board
            if event.button in (1, 3):
                mouse_create = None
                due_tile = False
                select_direction = None
            if event.button == 2:
                middle_click_held = False

        elif event.type == pygame.MOUSEMOTION:
            if middle_click_held:  # append relative mouse motion to board offset
                board.set_value(("offset", Vector(pygame.mouse.get_rel()) / board.tile_dims.elementwise()), change=True)

        if due_tile:
            if board.rect_on_parent.collidepoint(pygame.mouse.get_pos()):
                tile = board.get_collide_tile()
                if tile is not None:
                    due_tile = False
                    tiles = list()
                    if tile.state == mouse_state:
                        mouse_create = False
                    else:
                        mouse_create = True
                    select_origin = tile.pos
                    select_direction = None

        if mouse_create is not None:  # change tile states based on current click state
            if board.rect_on_parent.collidepoint(pygame.mouse.get_pos()):
                tile = board.get_collide_tile()
                if tile is not None:
                    if tile.pos != select_origin and select_direction is None:
                        if tile.pos[0] == select_origin[0]:
                            select_direction = 0
                        elif tile.pos[1] == select_origin[1]:
                            select_direction = 1
                    if (tile.pos == select_origin) or (select_direction is not None and tile not in tiles and tile.pos[select_direction] == select_origin[select_direction]):
                        if tile.state == 0 and mouse_create:
                            tile.state = mouse_state
                            tile.due_draw = True
                            board.due_draw = True
                        elif tile.state == mouse_state and not mouse_create:
                            tile.state = 0
                            tile.due_draw = True
                            board.due_draw = True
                        tiles.append(tile)

    if board.due_draw:
        screen.fill((0, 0, 0))
        board.draw()

    board.blit()

    pygame.display.flip()

    clock.tick(60)
