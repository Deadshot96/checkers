import pygame
import colors
from settings import *

pygame.init()
pygame.font.init()

CROWN = pygame.transform.scale(pygame.image.load(CROWN_PATH), (RADIUS, RADIUS))


class Block:

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.size = SIZE
        self.padding = PADDING
        self.x = self.col * self.size
        self.y = self.row * self.size
        self.player = None
        self.isKing = False
        self.radius = RADIUS
        self.direction = list()
        self.currentBlock = None
        self.isValid = False
        self.isEmpty = True
        self.selected = False

    def is_king(self):
        return self.isKing

    def make_king(self):
        self.isKing = True
        self.direction = [1, -1]

    def remove_king(self):
        self.isKing = False
        if self.player == colors.RED:
            self.direction = [-1]
        elif self.player == colors.BLUE:
            self.direction = [1]


    def get_pos(self):
        return self.row, self.col

    def get_direction(self):
        return self.direction

    def is_black(self):
        return self.color == colors.BLACK

    def is_empty(self):
        return self.player is None

    def make_valid(self):
        self.isValid = True

    def make_invalid(self):
        self.isValid = False

    def make_player(self, player):
        self.player = player

        if player == colors.BLUE:
            self.direction = [1]
        elif player == colors.RED:
            self.direction = [-1]

        self.isEmpty = False

    def remove_player(self):
        self.player = None
        self.direction = []
        self.isEmpty = True

    def select(self):
        self.selected = True

    def is_selected(self):
        return self.selected

    def deselect(self):
        self.selected = False

    def occupy(self):
        self.isEmpty = False

    def vacant(self):
        self.isEmpty = True

    def is_occupied(self):
        return self.isEmpty

    def __repr__(self):
        if self.player == colors.RED:
            return "RED"
        elif self.player == colors.BLUE:
            return "BLUE"
        else:
            return "EMPTY"

    def draw(self, win):
        rect = (self.x, self.y, self.size, self.size)
        pygame.draw.rect(win, self.color, rect)

        centerX, centerY = self.x + self.size // 2, self.y + self.size // 2

        if self.isValid:
            pygame.draw.circle(win, colors.CORN_FLOWER_BLUE,
                               (centerX, centerY), self.radius // 2)

        if self.player is not None:

            if self.is_selected():
                color = colors.LAWN_GREEN
                surface = pygame.Surface((self.size, self.size))
                surface.set_colorkey(colors.KEY)
                surface.set_alpha(128)
                surface.fill(color)
                rect = surface.get_rect()
                rect.center = centerX, centerY

                win.blit(surface, rect)

            pygame.draw.circle(
                win, self.player, (centerX, centerY), self.radius)
            pygame.draw.circle(win, colors.WHITE,
                               (centerX, centerY), self.radius + 1, 1)

            if self.is_king():
                rect = CROWN.get_rect()
                rect.center = centerX, centerY

                win.blit(CROWN, rect)
