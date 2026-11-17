import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 600, 600
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

LIGHT_PINK = (255, 182, 193)
LIGHT_GREY = (211, 211, 211)
HIGHLIGHT_COLOR = (0, 255, 0)
MOVE_HINT_COLOR = (0, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("UroojChessGame")

PIECES = {
    "wp": pygame.image.load("assets/white_pawn.png"),
    "bp": pygame.image.load("assets/black_pawn.png"),
    "wr": pygame.image.load("assets/white_rook.png"),
    "br": pygame.image.load("assets/black_rook.png"),
    "wn": pygame.image.load("assets/white_knight.png"),
    "bn": pygame.image.load("assets/black_knight.png"),
    "wb": pygame.image.load("assets/white_bishop.png"),
    "bb": pygame.image.load("assets/black_bishop.png"),
    "wq": pygame.image.load("assets/white_queen.png"),
    "bq": pygame.image.load("assets/black_queen.png"),
    "wk": pygame.image.load("assets/white_king.png"),
    "bk": pygame.image.load("assets/black_king.png"),
}

for key in PIECES:
    PIECES[key] = pygame.transform.smoothscale(PIECES[key], (SQUARE_SIZE, SQUARE_SIZE))

def create_initial_board():
    return [
        ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
        ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"],
    ]

board = create_initial_board()
selected_piece = None
valid_hints = []
current_turn = "w"

def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = LIGHT_PINK if (row + col) % 2 == 0 else LIGHT_GREY
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    if selected_piece:
        col, row = selected_piece
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
        for hint_col, hint_row in valid_hints:
            pygame.draw.rect(screen, MOVE_HINT_COLOR, (hint_col * SQUARE_SIZE, hint_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

def draw_pieces(board):
    for row in range(len(board)):
        for col in range(len(board[row])):
            piece = board[row][col]
            if piece != "":
                screen.blit(PIECES[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

def is_valid_move(piece, start_pos, end_pos):
    sx, sy = start_pos
    ex, ey = end_pos
    dx, dy = ex - sx, ey - sy

    if board[ey][ex] != "" and board[ey][ex][0] == piece[0]:
        return False
    if sx == ex and sy == ey:
        return False

    ptype = piece[1]
    color = piece[0]
    direction = -1 if color == "w" else 1

    if ptype == "p":
        if dx == 0 and dy == direction and board[ey][ex] == "":
            return True
        if abs(dx) == 1 and dy == direction and board[ey][ex] != "" and board[ey][ex][0] != color:
            return True
        return False

    if ptype == "r":
        if dx == 0 or dy == 0:
            step_x = 0 if dx == 0 else dx // abs(dx)
            step_y = 0 if dy == 0 else dy // abs(dy)
            x, y = sx + step_x, sy + step_y
            while (x, y) != (ex, ey):
                if board[y][x] != "":
                    return False
                x += step_x
                y += step_y
            return True

    if ptype == "b":
        if abs(dx) == abs(dy):
            step_x = dx // abs(dx)
            step_y = dy // abs(dy)
            x, y = sx + step_x, sy + step_y
            while (x, y) != (ex, ey):
                if board[y][x] != "":
                    return False
                x += step_x
                y += step_y
            return True

    if ptype == "q":
        return is_valid_move(color + "r", start_pos, end_pos) or is_valid_move(color + "b", start_pos, end_pos)

    if ptype == "n":
        return (abs(dx), abs(dy)) in [(1, 2), (2, 1)]

    if ptype == "k":
        return max(abs(dx), abs(dy)) == 1

    return False

def get_valid_moves(color):
    moves = []
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece != "" and piece[0] == color:
                for r in range(ROWS):
                    for c in range(COLS):
                        if is_valid_move(piece, (col, row), (c, r)):
                            moves.append(((col, row), (c, r)))
    return moves

def get_valid_destinations(piece_pos):
    sx, sy = piece_pos
    piece = board[sy][sx]
    destinations = []
    for r in range(ROWS):
        for c in range(COLS):
            if is_valid_move(piece, piece_pos, (c, r)):
                destinations.append((c, r))
    return destinations

def show_game_over(winner):
    font = pygame.font.SysFont(None, 35)
    message = f"{winner} wins! Press R to restart or Q to quit."
    text = font.render(message, True, (255, 0, 0))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    waiting = False
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

def reset_game():
    global board, selected_piece, current_turn, valid_hints
    board[:] = create_initial_board()
    selected_piece = None
    valid_hints = []
    current_turn = "w"

def ai_move():
    global current_turn
    valid_moves = get_valid_moves("b")
    if valid_moves:
        move = random.choice(valid_moves)
        (sx, sy), (ex, ey) = move
        piece = board[sy][sx]
        if board[ey][ex] == "wk":
            board[sy][sx] = ""
            board[ey][ex] = piece
            draw_board()
            draw_pieces(board)
            pygame.display.flip()
            pygame.time.wait(500)
            show_game_over("Black")
            return
        board[sy][sx] = ""
        board[ey][ex] = piece
        current_turn = "w"

def handle_click(pos):
    global selected_piece, current_turn, valid_hints
    col = pos[0] // SQUARE_SIZE
    row = pos[1] // SQUARE_SIZE

    if selected_piece:
        sx, sy = selected_piece
        piece = board[sy][sx]
        if is_valid_move(piece, selected_piece, (col, row)):
            if board[row][col] == "bk":
                board[sy][sx] = ""
                board[row][col] = piece
                draw_board()
                draw_pieces(board)
                pygame.display.flip()
                pygame.time.wait(500)
                show_game_over("White")
                return
            board[sy][sx] = ""
            board[row][col] = piece
            selected_piece = None
            valid_hints = []
            current_turn = "b"
        else:
            selected_piece = None
            valid_hints = []
    else:
        if board[row][col] != "" and board[row][col][0] == current_turn:
            selected_piece = (col, row)
            valid_hints = get_valid_destinations((col, row))

def main():
    global selected_piece, current_turn
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and current_turn == "w":
                if event.button == 1:
                    handle_click(pygame.mouse.get_pos())

        if current_turn == "b":
            ai_move()

        screen.fill((0, 0, 0))
        draw_board()
        draw_pieces(board)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
