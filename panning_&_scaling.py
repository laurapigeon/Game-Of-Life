from pygame.math import Vector2 as Vector
import pygame
import random
pygame.init()


class Board:
    def __init__(self, parent, tile_dims, grid, offset=Vector(0, 0), colour=(100, 100, 100)):
        self.parent = parent  # the surface the board is on

        self.tile_dims = tile_dims
        self.grid = grid
        self.update_dims("dims")  # creates the dims attribute

        self.populate()  # fills the board with tiles
        self.offset = offset
        self.update_rect()  # gives the board and tiles attributes for drawing

        self.colour = colour

    def set_value(self, key_value_pair, fix_key=None, change=False):
        if change:
            new_value = self.__dict__[key_value_pair[0]] + key_value_pair[1]
        else:
            new_value = key_value_pair[1]

        if new_value.x <= 0 or new_value.y <= 0:  # values of 0 or below produce error
            wordset = (("set", "to"), ("change", "by"))[change]
            print("Could not {} {} {} {}.".format(wordset[0], key_value_pair[0], wordset[1], key_value_pair[1]))
        else:
            self.__dict__[key_value_pair[0]] = new_value
            keys = ["grid", "dims", "tile_dims"]  # possible changes to the graphics of the board
            if key_value_pair[0] in keys and fix_key in keys:  # all keys
                keys.remove(key_value_pair[0])  # - changed key
                keys.remove(fix_key)  # - fixed key
                self.update_dims(keys[0])  # = key to be changed to account for new value
            self.update_rect()  # update rects to account for changes
            if key_value_pair[0] == "grid":
                self.populate()  # newly populate grid if the number of rows or columns changes

    def update_dims(self, change_key):
        if change_key == "dims":
            self.dims = self.grid * self.tile_dims.elementwise()
        elif change_key == "grid":
            self.grid = self.dims // self.tile_dims.elementwise()
            self.populate()  # newly populate grid if the number of rows or columns changes
        elif change_key == "tile_dims":
            self.tile_dims = self.dims // self.grid.elementwise()

    def update_rect(self):
        parent_dims = Vector(self.parent.get_rect().size)
        rect_top_left = v_round(parent_dims / 2 + self.offset * self.tile_dims.elementwise() - self.dims / 2)
        rect_dims = v_round(self.dims)
        self.rect_on_parent = pygame.Rect(rect_top_left, rect_dims)  # rect for blitting board surface onto parent
        self.rect_on_self = pygame.Rect((0, 0), rect_dims)  # rect for drawing board
        self.surface = pygame.Surface(rect_dims)  # surface for drawing tiles
        self.update_tile_rects()  # mark tiles on board for rect updates

    def update_tile_rects(self):
        for row in self.tiles:
            for tile in row:
                tile.due_rect_update = True

    def populate(self):
        self.tiles = list()
        for row_num in range(int(self.grid.y)):
            row = list()
            for column_num in range(int(self.grid.x)):
                colour = (random.randint(128, 196), random.randint(128, 196), random.randint(128, 196))
                row.append(Tile(self, random.random() < 0.75, Vector(column_num, row_num), colour))
            self.tiles.append(row)

    def draw(self):
        self.surface.fill(self.colour)  # method one for displaying board
        pygame.draw.rect(self.surface, self.colour, self.rect_on_self)  # method two for displaying board
        for row in self.tiles:
            for tile in row:
                tile.draw()  # draw tiles on board
        self.parent.blit(self.surface, self.rect_on_parent.topleft)  # blit board onto surface


class Tile:
    def __init__(self, board, initial_state, pos, colour=(164, 164, 255)):
        self.board = board
        self.state = initial_state
        self.pos = pos  # position in grid
        self.due_rect_update = True  # due to have rect updated
        self.colour = colour

    def update_rect(self):
        if self.board.tile_dims.x > 5 and self.board.tile_dims.y > 5 and BORDERS:  # for pixel cell border
            rect_top_left = v_round(Vector(1, 1) + self.pos * self.board.tile_dims.elementwise())
            rect_dims = v_round(Vector(-2, -2) + self.board.tile_dims)
        else:
            rect_top_left = v_round(self.pos * self.board.tile_dims.elementwise())
            rect_dims = v_round(self.board.tile_dims)
        screen_rect_top_left = self.board.rect_on_parent.move(rect_top_left).topleft  # tile rect relative to screen
        self.rect_on_screen = pygame.Rect(screen_rect_top_left, rect_dims)  # for detecting if on screen
        self.rect_on_board = pygame.Rect(rect_top_left, rect_dims)  # for drawing cells on board
        self.due_rect_update = False  # done updating rect

    def draw(self):
        if self.state == 1:
            if self.due_rect_update:
                self.update_rect()  # update rects that need it before theyre drawn
            within_x = self.rect_on_screen.right >= 0 and self.rect_on_screen.left <= self.board.parent.get_rect().right
            within_y = self.rect_on_screen.bottom >= 0 and self.rect_on_screen.top <= self.board.parent.get_rect().bottom
            if within_x and within_y:  # tile is only drawn to board if on screen
                pygame.draw.rect(self.board.surface, self.colour, self.rect_on_board)


def v_round(vector):  # takes a Vector instance and returns a rounded tuple
    return (round(vector.x), round(vector.y))


DEFUAULT_SCREEN_DIMS = (500, 500)
screen = pygame.display.set_mode(DEFUAULT_SCREEN_DIMS, pygame.RESIZABLE)

BORDERS = False

board = Board(screen, tile_dims=Vector(10, 10), grid=Vector(105, 105))
board.populate()
# grid (columns/rows), tile_dims (width/height), dims (width/height) (any two of the 3 for a desired effect)
# board.set_value(("key_to_change", value), "key_to_fix", change=True)

left_click_held = False
done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.VIDEORESIZE:  # screen resize by dragging edges of window
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            board.update_rect()

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_EQUALS, pygame.K_MINUS):  # change number of rows and columns
                if event.key == pygame.K_EQUALS:
                    board.set_value(("grid", Vector(10, 10)), "tile_dims", True)
                elif event.key == pygame.K_MINUS:
                    board.set_value(("grid", Vector(-10, -10)), "tile_dims", True)

        elif event.type == pygame.MOUSEBUTTONDOWN:  # begin dragging board
            if event.button == 1:
                left_click_held = True
                pygame.mouse.get_rel()  # clear current relative mouse movement

            elif event.button in (4, 5):  # zoom board (by changing tile dimensions)
                if event.button == 4:
                    board.set_value(("tile_dims", Vector(1, 1)), "grid", True)
                elif event.button == 5:
                    board.set_value(("tile_dims", Vector(-1, -1)), "grid", True)

        elif event.type == pygame.MOUSEBUTTONUP:  # end dragging board
            if event.button == 1:
                left_click_held = False

        elif event.type == pygame.MOUSEMOTION and left_click_held:  # append relative mouse motion to board offset
            board.offset += Vector(pygame.mouse.get_rel()) / board.tile_dims.elementwise()
            board.update_rect()

    screen.fill((0, 0, 0))
    board.draw()
    pygame.display.flip()