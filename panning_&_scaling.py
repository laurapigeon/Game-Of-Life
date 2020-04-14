from pygame.math import Vector2 as Vector
import pygame
import random
pygame.init()

DEFUAULT_SCREEN_DIMS = (500, 500)
screen = pygame.display.set_mode(DEFUAULT_SCREEN_DIMS, pygame.RESIZABLE)


def v_round(vector):
    return (round(vector.x), round(vector.y))


class Board:
    def __init__(self, parent, tile_dims, grid, offset=Vector(0, 0), colour=(100, 100, 100)):
        self.parent = parent
        self.tiles = list()
        self.tile_dims = tile_dims
        self.grid = grid
        self.update_dims("dims")
        self.offset = offset
        self.update_rect()
        self.colour = colour

    def set_value(self, key_value_pair, fix_key=None, change=False):
        if change:
            new_value = self.__dict__[key_value_pair[0]] + key_value_pair[1]
        else:
            new_value = key_value_pair[1]

        if new_value.x <= 0 or new_value.y <= 0:
            print("Could not {} {} {} {}.".format(("set", "change")[change], key_value_pair[0], ("to", "by")[change], key_value_pair[1]))
        else:
            self.__dict__[key_value_pair[0]] = new_value
            keys = ["grid", "dims", "tile_dims"]
            if key_value_pair[0] in keys and fix_key in keys:
                keys.remove(key_value_pair[0])
                keys.remove(fix_key)
                self.update_dims(keys[0])
            self.update_rect()
            if key_value_pair[0] == "tile_dims":
                self.update_tile_rects()
            elif key_value_pair[0] == "grid":
                self.populate()

    def update_tile_rects(self):
        for row in self.tiles:
            for tile in row:
                tile.update_rect()

    def update_dims(self, change_key):
        if change_key == "grid":
            self.grid = self.dims // self.tile_dims.elementwise()
        elif change_key == "dims":
            self.dims = self.grid * self.tile_dims.elementwise()
        elif change_key == "tile_dims":
            self.tile_dims = self.dims // self.grid.elementwise()
        if change_key == "tile_dims":
            self.update_tile_rects()
        if change_key == "grid":
            self.populate()

    def update_rect(self):
        parent_rect = self.parent.get_rect()
        parent_dims = Vector(parent_rect.size)
        rect_top_left = v_round(parent_dims / 2 + self.offset * self.tile_dims.elementwise() - self.dims / 2)
        rect_dims = v_round(self.dims)
        self.rect_on_parent = pygame.Rect(rect_top_left, rect_dims)
        self.rect_on_self = pygame.Rect((0, 0), rect_dims)
        self.surface = pygame.Surface(rect_dims)

    def populate(self):
        self.tiles = list()
        for row_num in range(int(self.grid.y)):
            row = list()
            for column_num in range(int(self.grid.x)):
                row.append(Tile(self, 1, Vector(column_num, row_num), (random.randint(128, 192), random.randint(128, 192), random.randint(128, 192))))
            self.tiles.append(row)

    def draw(self):
        self.surface.fill(self.colour)
        pygame.draw.rect(self.surface, self.colour, self.rect_on_self)
        for row in self.tiles:
            for tile in row:
                tile.draw()
        self.parent.blit(self.surface, self.rect_on_parent.topleft)


class Tile:
    def __init__(self, board, initial_state, pos, colour):
        self.board = board
        self.state = initial_state
        self.pos = pos
        self.update_rect()
        self.colour = colour

    def update_rect(self):
        parent_rect = self.board.parent.get_rect()
        parent_dims = Vector(parent_rect.size)
        rect_top_left = v_round(self.pos * self.board.tile_dims.elementwise())
        rect_dims = v_round(self.board.tile_dims)
        screen_rect_top_left = self.board.rect_on_parent.move(rect_top_left).topleft
        self.rect_on_screen = pygame.Rect(screen_rect_top_left, rect_dims)
        self.rect_on_board = pygame.Rect(rect_top_left, rect_dims)

    def draw(self):
        if self.state == 1:
            #print(self.rect_on_screen, self.board.parent.get_rect())
            within_x = self.rect_on_screen.right >= 0 and self.rect_on_screen.left <= self.board.parent.get_rect().right
            within_y = self.rect_on_screen.bottom >= 0 and self.rect_on_screen.top <= self.board.parent.get_rect().bottom
            if within_x and within_y:
                pygame.draw.rect(self.board.surface, self.colour, self.rect_on_board)


board = Board(screen, tile_dims=Vector(10, 10), grid=Vector(15, 15))
board.populate()
# grid (columns/rows), tile_dims (width/height), dims (width/height) (any two of the 3 for a desired effect)
# board.set_value(("key_to_change", value), "key_to_fix", True)

left_click_held = False
done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            board.update_rect()
            board.update_tile_rects()

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_EQUALS, pygame.K_MINUS):
                if event.key == pygame.K_EQUALS:
                    board.set_value(("grid", Vector(10, 10)), "tile_dims", True)
                elif event.key == pygame.K_MINUS:
                    board.set_value(("grid", Vector(-10, -10)), "tile_dims", True)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                left_click_held = True
                pygame.mouse.get_rel()

            elif event.button in (4, 5):
                if event.button == 4:
                    board.set_value(("tile_dims", Vector(1, 1)), "grid", True)
                elif event.button == 5:
                    board.set_value(("tile_dims", Vector(-1, -1)), "grid", True)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                left_click_held = False

        elif event.type == pygame.MOUSEMOTION and left_click_held:
            delta_mouse = pygame.mouse.get_rel()
            board.offset += Vector(delta_mouse) / board.tile_dims.elementwise()
            board.update_rect()
            board.update_tile_rects()

    screen.fill((0, 0, 0))
    board.draw()
    pygame.display.flip()