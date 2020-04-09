import pygame
import random
pygame.init()


class Tile:
    def __init__(self, state, column, row):
        self.state = self.new_state = state
        self.rect = pygame.Rect(column, row, 1, 1)


columns, rows, board = 640, 360, list()
for y in range(rows):
    row = []
    for x in range(columns):
        row.append(Tile(random.random() < 0.3, x, y))
    board.append(row)
for row in board:
    for tile in row:
        tile.neighbors = list()
        if tile.rect.left != 0:
            tile.neighbors.append(board[tile.rect.top][tile.rect.left - 1])
        if tile.rect.left != columns - 1:
            tile.neighbors.append(board[tile.rect.top][tile.rect.left + 1])
        if tile.rect.top != 0:
            tile.neighbors.append(board[tile.rect.top - 1][tile.rect.left])
        if tile.rect.top != rows - 1:
            tile.neighbors.append(board[tile.rect.top + 1][tile.rect.left])
        if tile.rect.left != 0 and tile.rect.top != 0:
            tile.neighbors.append(board[tile.rect.top - 1][tile.rect.left - 1])
        if tile.rect.left != columns - 1 and tile.rect.top != rows - 1:
            tile.neighbors.append(board[tile.rect.top + 1][tile.rect.left + 1])
        if tile.rect.left != 0 and tile.rect.top != rows - 1:
            tile.neighbors.append(board[tile.rect.top + 1][tile.rect.left - 1])
        if tile.rect.left != columns - 1 and tile.rect.top != 0:
            tile.neighbors.append(board[tile.rect.top - 1][tile.rect.left + 1])
screen = pygame.display.set_mode((columns, rows), pygame.RESIZABLE)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
    screen.fill((0, 0, 0))
    for row in board:
        for tile in row:
            if tile.state:
                pygame.draw.rect(screen, (255, 255, 255), tile.rect)
    pygame.display.flip()
    for row in board:
        for tile in row:
            live_neighbors = 0
            for neighbor in tile.neighbors:
                if neighbor.state:
                    live_neighbors += 1
                    if live_neighbors == 4:
                        break
            if tile.state and live_neighbors not in (2, 3):
                tile.new_state = 0
            elif not tile.state and live_neighbors == 3:
                tile.new_state = 1
    for row in board:
        for tile in row:
            tile.state = tile.new_state