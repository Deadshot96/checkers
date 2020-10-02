import pygame
import random
import math
import colors
import os
import itertools
from Block import *
from settings import *

pygame.init()
pygame.font.init()


class Game:

    FPS = 60
    COOLDOWN = 20
    COLORS = [colors.RED, colors.BLACK]
    PLAYERS = [colors.BLUE, colors.RED]
    TURNS = ['RED', 'BLUE']

    def __init__(self):
        self.width = WIDTH
        self.height = HEIGHT
        self.rows = NROW
        self.cols = NCOL
        self.gameWidth = GAMEWIDTH
        self.gameHeight = GAMEHEIGHT
        self.size = SIZE
        self.xoff = (self.width - self.gameWidth) // 2
        self.yoff = int((self.height - self.gameHeight) * 0.8)
        self.cooldown_index = 0
        self.grid = None
        self.clock = None
        self.titleFont = None
        self.jumpMove = False

    def game_init(self):

        self.win = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Checkers Developer")

        self.gameWin = self.win.subsurface(
            (self.xoff, self.yoff, self.gameWidth, self.gameHeight))
        self.win.fill(colors.MID_BLACK)
        self.gameWin.fill(colors.BLACK)

        pygame.display.update()

        self.clock = pygame.time.Clock()
        self.titleFont = pygame.font.SysFont("comicsansms", 40)

        titleText = self.titleFont.render("Checkers Developer", 1, colors.GOLD)
        wid, hgt = titleText.get_size()
        self.win.blit(titleText, ((self.width - wid) //
                                  2, (self.yoff - hgt) // 2))

        self.grid_init()

    def grid_init(self):
        self.grid = list()
        count = -1
        for row in range(self.rows):
            count += 1
            self.grid.append(list())
            for col in range(self.cols):
                color = self.COLORS[count % 2]
                self.grid[row].append(Block(row, col, color))
                count += 1

    def new_game(self):

        self.blueKing = 0
        self.redKing = 0
        self.numBlue = 12
        self.numRed = 12
        self.CYCLE = itertools.cycle(self.TURNS)
        self.turn = next(self.CYCLE)
        self.selected = None
        self.valid_positions = dict()
        self.num_valid_moves = 0
        self.jumpMove = False

        # Reset Index
        for rowIndex, row in enumerate(self.grid):
            for colIndex, spot in enumerate(row):
                if spot.is_black():
                    if rowIndex < 3:
                        spot.make_player(self.PLAYERS[0])
                    elif rowIndex > 4:
                        spot.make_player(self.PLAYERS[1])
                    else:
                        spot.remove_player()

    def get_pos(self, pos):
        x, y = pos
        x -= self.xoff
        y -= self.yoff

        return y // self.size, x // self.size

    def cooldown(self):
        if self.cooldown_index > self.COOLDOWN:
            self.cooldown_index = 0
        elif self.cooldown_index > 0:
            self.cooldown_index += 1

    def draw_grid(self, win):
        for row in self.grid:
            for spot in row:
                spot.draw(win)

    def is_cool(self):
        self.cooldown_index == 0

    def show_positions(self):
        row, col = self.selected.get_pos()
        self._traverse(self.selected)
        print(self.valid_positions)

        for key, values in self.valid_positions.items():
            if self.jumpMove:
                if values is not None:
                    key.make_valid()
            else:
                key.make_valid()


    def _traverse(self, piece,jumpCell=None, isSkipped=False):
        row, col = piece.get_pos()
        name = str(piece)

        print("In Traverse")
        if not isSkipped:
            for rowDelta in piece.direction:
                for colDelta in [-1, 1]:
                    nRow = row + rowDelta
                    nCol = col + colDelta

                    if self.is_valid_dims(nRow, nCol):
                        dest = self.grid[nRow][nCol]
                        destName = str(dest)

                        if destName == "EMPTY":
                            self.valid_positions[dest] = None

                        elif destName != self.turn:
                            jumpRow = nRow + rowDelta
                            jumpCol = nCol + colDelta

                            if self.is_valid_dims(jumpRow, jumpCol) and str(self.grid[jumpRow][jumpCol]) == 'EMPTY':
                                jumpCell = self.grid[jumpRow][jumpCol]

                                jumpCell.occupy()
                                self.valid_positions[jumpCell] = [self.grid[nRow][nCol]]
                                self.jumpMove = True
                                self._traverse(piece, jumpCell, True)
                                jumpCell.vacant()
        else:
            options = [(2 * i, j) for i in piece.direction for j in [2, -2]]
            row, col = jumpCell.get_pos()
            jumps = self.valid_positions[jumpCell]

            for rowDelta, colDelta in options:
                nRow = row + rowDelta
                nCol = col + colDelta
                
                pieceRow = row + rowDelta // 2
                pieceCol = col + colDelta // 2

                if self.is_valid_dims(nRow, nCol) and self.is_valid_dims(pieceRow, pieceCol):
                    dest = self.grid[nRow][nCol]
                    jump = self.grid[pieceRow][pieceCol]

                    if str(dest) == 'EMPTY' and dest.is_empty() and str(jump) != 'EMPTY' and str(jump) != self.turn:
                        dest.occupy()
                        jumps.append(jump)
                        self.valid_positions[dest] = jumps
                        self.valid_positions.pop(jumpCell)
                        self._traverse(piece, dest, True)
                        dest.vacant()
                        


    def deselect(self):
        self.selected.deselect()
        self.selected = None
        for block in self.valid_positions.keys():
            block.make_invalid()

        self.valid_positions.clear()
        self.jumpMove = False

    def select(self, piece):
        if self.selected is not None:
            self.deselect()

        self.selected = piece
        self.selected.select()
        self.show_positions()

    def game_move(self, row, col):
        piece = self.grid[row][col]
        destName = str(piece)

        if destName == self.turn and self.selected is None:
            self.select(piece)

        elif destName == self.turn:
            self.select(piece)

        elif destName.lower() == 'empty':
            if piece in self.valid_positions.keys():
                self.move_piece(piece)
            else:
                self.deselect()

        else:
            self.deselect()

    def move_piece(self, dest):
        pass

    def draw(self, win):
        self.draw_grid(win)
        pygame.display.update()

    def is_valid_dims(self, row, col):
        return row in range(NROW) and col in range(NCOL)

    def run(self):
        self.game_init()
        self.new_game()

        run = True
        while run:
            self.clock.tick(self.FPS)
            self.draw(self.gameWin)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pressed = pygame.mouse.get_pressed()

                    if pressed[0]:
                        pos = pygame.mouse.get_pos()
                        row, col = self.get_pos(pos)

                        if self.is_valid_dims(row, col):
                            self.game_move(row, col)

                        print(self.grid[row][col])

                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    pos = pygame.mouse.get_pos()

                    row, col = self.get_pos(pos)
                    if self.is_valid_dims(row, col):
                        cell = self.grid[row][col]

                    if keys[pygame.K_SPACE]:
                        cell.remove_player()

                    if keys[pygame.K_r]:
                        cell.make_player(self.PLAYERS[1])

                    if keys[pygame.K_b]:
                        cell.make_player(self.PLAYERS[0])

                    if keys[pygame.K_k]:
                        cell.make_king()




        pygame.font.quit()
        pygame.quit()


if __name__ == '__main__':
    X = Game()
    X.run()
