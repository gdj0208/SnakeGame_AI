
import pygame
from Game import Game


# Pygame 초기화
pygame.init()

# 화면 설정
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
CLOCK = pygame.time.Clock()
pygame.display.set_caption("Snake Game")

myGame = Game(
    clock=CLOCK,
    screen_width=SCREEN_WIDTH, 
    screen_height=SCREEN_HEIGHT, 
    cell_size=CELL_SIZE, 
    screen=SCREEN
)
myGame.run()