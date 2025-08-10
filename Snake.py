
import pygame

# Snake 클래스
class Snake:
    def __init__(self, screen_width, screen_height, cell_size):
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.CELL_SIZE = cell_size

        self.body = [(200, 100), (180, 100), (160, 100)] # 초기 몸통
        self.direction = (self.CELL_SIZE, 0) # 오른쪽으로 시작

    def move(self):
        self.grow()
        self.body.pop()

    def grow(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)
    
    def change_direction(self, new_dir):

        if new_dir == [1,0,0] :     # 직진
            return 
        elif new_dir == [0,1,0] :     # 좌회전
            if self.direction[0] == 20 and self.direction[1] == 0:
                self.direction = (0, -20)
            elif self.direction[0] == 0 and self.direction[1] == -20:
                self.direction = (-20, 0)
            elif self.direction[0] == -20 and self.direction[1] == 0:
                self.direction = (0, 20)
            elif self.direction[0] == 0 and self.direction[1] == 20:
                self.direction = (20, 0)
        elif new_dir == [0,0,1]:    # 우회전
            if self.direction[0] == 20 and self.direction[1] == 0:
                self.direction = (0, 20)
            elif self.direction[0] == 0 and self.direction[1] == 20:
                self.direction = (-20, 0)
            elif self.direction[0] == -20 and self.direction[1] == 0:
                self.direction = (0, -20)
            elif self.direction[0] == 0 and self.direction[1] == -20:
                self.direction = (20, 0)

    def change_direction_by_key(self, new_dir):
        # 반대 방향으로 이동하는 것 방지
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.direction = new_dir

    def check_collision(self, head=None):
        if head == None:
            head = self.body[0]
            
        # 벽 충돌
        if (head[0] >= self.SCREEN_WIDTH or head[0] < 0 or
                head[1] >= self.SCREEN_HEIGHT or head[1] < 0):
            return True
        # 몸통 충돌
        if head in self.body[1:]:
            return True
        return False
        
    def draw(self, surface):
        for segment in self.body:
            rect = pygame.Rect(
                segment[0], 
                segment[1], 
                self.CELL_SIZE, 
                self.CELL_SIZE
            )
            pygame.draw.rect(surface, (0, 255, 0), rect)