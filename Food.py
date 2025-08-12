
import pygame
import random

# Food 클래스
class Food:
    def __init__(self, screen_width, screen_height, cell_size):
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.CELL_SIZE = cell_size

        self.position = (0, 0)
        self.spawn()

    def spawn(self):
        # 화면 격자 내에 랜덤 위치 생성
        x = random.randrange(0, self.SCREEN_WIDTH // self.CELL_SIZE) * self.CELL_SIZE
        y = random.randrange(0, self.SCREEN_HEIGHT // self.CELL_SIZE) * self.CELL_SIZE
        self.position = (x, y)
            
    def draw(self, surface):
        rect = pygame.Rect(self.position[0], self.position[1], self.CELL_SIZE, self.CELL_SIZE)
        pygame.draw.rect(surface, (255, 0, 0), rect)

