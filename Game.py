
import pygame
import random
from collections import namedtuple
from Food import Food
from Snake import Snake
from Agent import Agent
import math

REWARD_FOOD = 10
REWARD_DEATH = -10
REWARD_STEP = 0

class Game():
    def __init__(self, clock, screen_width, screen_height, cell_size, screen, agent=None):   
        self.CLOCK = clock
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.CELL_SIZE = cell_size
        self.SCREEN = screen
        self.point = namedtuple('Point', 'x, y')
        self.agent = agent

    def reset_game(self):
        # 1. 게임 상태 초기화
        self.score = 0
        self.frame_iteration = 0

        # 2. 게임 객체 재설정
        # Snake 객체를 새로 생성
        self.snake = Snake(
            screen_width=self.SCREEN_WIDTH,
            screen_height=self.SCREEN_HEIGHT,
            cell_size=self.CELL_SIZE
        ) 
        
        # Food 객체를 새로 생성 (또는 기존 객체의 spawn() 메서드 호출)
        self.food = Food(
            screen_width=self.SCREEN_WIDTH,
            screen_height=self.SCREEN_HEIGHT,
            cell_size=self.CELL_SIZE
        )

    def game_over(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                # 사용자의 키 입력 처리
                elif event.type == pygame.KEYDOWN:

                    # 'R' 키를 누르면 게임 재시작
                    if event.key == pygame.K_r: 
                        self.reset_game()
                        return # game_over 루프를 빠져나감
                    
                    # 'Q' 키를 누르면 게임 종료
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        quit()

            # 화면에 게임 오버 메시지 표시
            self.SCREEN.fill((0, 0, 0)) # 화면을 검은색으로 채우기
            

            # 게임오버 출력
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("GAME OVER", True, (255, 255, 255))
            text_rect = game_over_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 - 50))
            self.SCREEN.blit(game_over_text, text_rect)

            font_score = pygame.font.Font(None, 48)
            score_text = font_score.render(f"Score: {self.score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 20))
            self.SCREEN.blit(score_text, score_rect)

            font_hint = pygame.font.Font(None, 36)
            hint_text = font_hint.render("Press 'R' to Restart or 'Q' to Quit", True, (200, 200, 200))
            hint_rect = hint_text.get_rect(center=(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 100))
            self.SCREEN.blit(hint_text, hint_rect)

            pygame.display.flip()

    def play_step(self, action, n_games):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        self.frame_iteration += 1
        
        # 1. AI 행동에 따라 뱀의 방향 변경
        self.snake.change_direction(action)
        
        # 2. 뱀 이동
        prev_head = self.snake.body[0]
        self.snake.move()
        cur_head = self.snake.body[0]
        game_over = False

        # 3. 충돌 감지
        if self.snake.check_collision(self.snake.body[0]) or self.frame_iteration > 100 * len(self.snake.body) :
            game_over = True
            return REWARD_DEATH, game_over, self.score

        # 5. 먹이 섭취 및 보상 적용
        if self.snake.body[0] == self.food.position:
            self.score += 1
            self.snake.grow()

            # 먹이가 뱀의 몸통에 겹치지 않도록 확인
            while True:
                self.food.spawn()
                if self.food.position not in self.snake.body:
                    break
            return REWARD_FOOD, game_over, self.score
        
        self.draw()
        self.CLOCK.tick(120)
        return REWARD_STEP, game_over, self.score

    def run(self, agent=None) :
        self.reset_game()

        # Game 클래스의 run 메서드 내부
        running = True
        while running:
            # AI 에이전트가 게임을 플레이하는 경우
            if agent is not None:
                action = agent.get_action(agent.get_state(self))
                self.snake.change_direction(action)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.game_over()
            # 직접 게임하는 경우
            else :
                # 1. 이벤트 처리
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.game_over()
                        # 키 입력에 따라 뱀 방향 변경
                        elif event.key == pygame.K_UP:
                            self.snake.change_direction_by_key((0, -self.CELL_SIZE))
                        elif event.key == pygame.K_DOWN:
                            self.snake.change_direction_by_key((0, self.CELL_SIZE))
                        elif event.key == pygame.K_LEFT:
                            self.snake.change_direction_by_key((-self.CELL_SIZE, 0))
                        elif event.key == pygame.K_RIGHT:
                            self.snake.change_direction_by_key((self.CELL_SIZE, 0))
            

            # 2. 게임 상태 업데이트 (뱀 이동, 충돌 감지)
            self.snake.move()

            # 뱀이 먹이를 먹었는지 확인
            if self.snake.body[0] == self.food.position:
                self.score += 10
                self.snake.grow() # 뱀 몸통 늘리기

                while True:
                    self.food.spawn()
                    if self.food.position not in self.snake.body:
                        break
                    # print("bug solved!")

            # 충돌 감지 후 게임 오버
            if self.snake.check_collision():
                self.game_over()
                # running = False

            # 3. 화면 그리기
            self.draw()
            
            # 4. 프레임 제어
            self.CLOCK.tick(10) # 1초에 10프레임으로 제한

    def draw(self) :
        self.SCREEN.fill((0, 0, 0))     # 화면을 검은색으로 지우기
        self.snake.draw(self.SCREEN)
        self.food.draw(self.SCREEN)
        pygame.display.flip()           # 화면 업데이트

    def is_collision(self, point):
        # 충돌 감지 로직
        return self.snake.check_collision(point)
        # head = self.snake.body[0]