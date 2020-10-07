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
        self.valid_positions = list()
        self.path_dict = dict()
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

    def unoccupy_grid(self):
        for row in self.grid:
            for cell in row:
                cell.vacant()

    def show_positions(self):
        row, col = self.selected.get_pos()
        self.jumpMove = False
        self.unoccupy_grid()
        self.__traverse__()
        print("Valid pos: ", list(map(lambda x: x.get_pos(), self.valid_positions)))

        for dest in self.valid_positions:
            path = list()
            current = dest
            while current is not self.selected:
                current = self.path_dict[current]
                path.append(current)

            dest.make_valid()
            print("Path is :", path)
            print("Jump Move is ", self.jumpMove)


    def __traverse__(self, jumpCell = None):
        row, col = self.selected.get_pos()
        name = str(self.selected)

        if not jumpCell:
            # Starting the travel - no jump yet
            # check the basic positions

            options = [(i, j) for i in self.selected.direction for j in (-1, 1)]
            
            for rowDelta, colDelta in options:
                
                nRow = row + rowDelta
                nCol = col + colDelta

                if self.is_valid_dims(nRow, nCol):
                    dest = self.grid[nRow][nCol]
                    destName = str(dest)

                    if destName == "EMPTY":
                        self.valid_positions.append(dest) 
                        self.path_dict[dest] = self.selected

                    elif destName != self.turn:
                        jumpRow = nRow + rowDelta
                        jumpCol = nCol + colDelta

                        if self.is_valid_dims(jumpRow, jumpCol) and str(self.grid[jumpRow][jumpCol]) == "EMPTY":
                            jumpCell = self.grid[jumpRow][jumpCol]

                            jumpCell.occupy()
                            # self.valid_positions.append(jumpCell)
                            # This dict should always be updated before __traverse__ call
                            self.path_dict[jumpCell] = self.selected
                            self.__traverse__(jumpCell)
                            self.jumpMove = True
                            jumpCell.vacant()
        else:
            options = [(2 * i, j) for i in self.selected.direction for j in (-2, 2)]
            row, col = jumpCell.get_pos()
            validForFinalStop = True
            print("In jumpCell", row, col, sep="\t")
            for rowDelta, colDelta in options:
                nRow = row + rowDelta
                nCol = col + colDelta
                print(nRow, nCol, sep="\t\t")

                midRow = row + rowDelta // 2
                midCol = col + colDelta // 2
                print(midRow, midCol, sep="\t\t")

                if self.is_valid_dims(nRow, nCol) and self.is_valid_dims(midRow, midCol):
                    dest = self.grid[nRow][nCol]
                    midCell = self.grid[midRow][midCol]
                    print("It's valid.")

                    if str(dest) == "EMPTY":
                        print("Dest Empty")
                    if str(midCell) != "EMPTY":
                        print("MidCell not Empty")
                    if str(midCell) != self.turn:
                        print("MidCell opposite.")
                    if not dest.is_occupied():
                        print("Not occupied")
        

                    if str(dest) == "EMPTY" and str(midCell) != "EMPTY" and not dest.is_occupied() and str(midCell) != self.turn:
                        print("Inside jumpcell if.")
                        validForFinalStop = False
                        dest.occupy()
                        # This dict should always be updated before __traverse__ call
                        self.path_dict[dest] = jumpCell 
                        self.__traverse__(dest)
                        dest.vacant()

            if validForFinalStop:
                self.valid_positions.append(jumpCell)

                       


    def deselect(self):
        if self.selected is not None:
            self.selected.deselect()
        self.selected = None
        for block in self.valid_positions:
            block.make_invalid()

        self.valid_positions.clear()
        self.path_dict.clear()
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

        elif destName == 'EMPTY':
            if piece in self.valid_positions:
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
                        if not cell.is_king():
                            cell.make_king()
                        else:
                            cell.remove_king()




        pygame.font.quit()
        pygame.quit()


if __name__ == '__main__':
    X = Game()
    X.run()
