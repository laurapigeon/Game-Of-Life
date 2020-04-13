import pygame, random, os
os.environ['SDL_VIDEO_WINDOW_POS'] = "0,0"
columns, rows, board, screen = 1280, 720, list(), pygame.display.set_mode((1280, 720), pygame.NOFRAME)
for tile_num in range(rows * columns):
    state = random.random() < 0.3
    board.append({"state": state, "new_state": state, "rect": pygame.Rect(tile_num % columns, tile_num // columns, 1, 1)})
for tile in board:
    bottom_x, top_x, bottom_y, top_y = (tile["rect"].left - 1, columns - 1)[tile["rect"].left == 0], (tile["rect"].left + 1, 0)[tile["rect"].left == columns - 1], (tile["rect"].top - 1, rows - 1)[tile["rect"].top == 0], (tile["rect"].top + 1, 0)[tile["rect"].top == rows - 1]
    tile["neighbors"] = (board[tile["rect"].top * columns + bottom_x], board[tile["rect"].top * columns + top_x], board[bottom_y * columns + tile["rect"].left], board[top_y * columns + tile["rect"].left], board[bottom_y * columns + bottom_x], board[top_y * columns + top_x], board[top_y * columns + bottom_x], board[bottom_y * columns + top_x])
while True:
    if pygame.event.get() and pygame.key.get_pressed()[pygame.K_ESCAPE] or pygame.key.get_pressed()[pygame.K_q]:
        quit()
    screen.fill((0, 0, 0))
    for tile in board:
        if tile["state"] == 1:
            pygame.draw.rect(screen, ((0, 0, 0), (255, 255, 255))[tile["state"] == 1], tile["rect"])
        live_neighbors = 0
        for neighbor in tile["neighbors"]:
            live_neighbors += neighbor["state"]
            if live_neighbors == 4:
                break
        if tile["state"] and live_neighbors not in (2, 3):
            tile["new_state"] = 0
        elif not tile["state"] and live_neighbors == 3:
            tile["new_state"] = 1
    pygame.display.update()
    for tile in board:
        tile["state"] = tile["new_state"]