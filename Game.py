
import pygame
import random
from collections import namedtuple
from Food import Food
from Snake import Snake
from Agent import Agent
import math


class Game():
    def __init__(self, clock, screen_width, screen_height, cell_size, screen):   
        self.CLOCK = clock
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.CELL_SIZE = cell_size
        self.SCREEN = screen
        self.point = namedtuple('Point', 'x, y')

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
        self.frame_iteration += 1
        
        # 1. AI 행동에 따라 뱀의 방향 변경
        self.snake.change_direction(action)
        
        # 2. 뱀 이동
        prev_head = self.snake.body[0]
        self.snake.move()
        cur_head = self.snake.body[0]
        game_over = False

        # 3. 보상 체계 설정 (커리큘럼 학습)
        # n_games 값에 따라 보상 가중치를 동적으로 변경합니다.
        # 이 값을 조절하여 학습 속도와 전략을 변경할 수 있습니다.
        if n_games < 2000:
            # Phase 1: 초반 학습 (먹이 찾기 집중)
            # 죽음 페널티가 상대적으로 작아 탐험을 유도합니다.
            REWARD_FOOD = 5000
            REWARD_WALL_DEATH = -50
            REWARD_SELF_DEATH = -150
            REWARD_STEP = -0.5
        elif n_games < 5000:
            # Phase 2: 안정화 단계 (죽음 회피 집중)
            # 죽음 페널티를 크게 높여 안전한 플레이를 유도합니다.
            REWARD_FOOD = 500
            REWARD_WALL_DEATH = -400
            REWARD_SELF_DEATH = -250
            REWARD_STEP = -0.1
        else:
            # Phase 3: 심화 학습 (최적화)
            # 죽음 페널티를 더 높여 효율적인 플레이를 완성합니다.
            REWARD_FOOD = 250
            REWARD_WALL_DEATH = -1000
            REWARD_SELF_DEATH = -1000
            REWARD_STEP = 0

        # 4. 충돌 감지 및 보상 적용
        # 뱀의 몸통과 벽 충돌 체크
        prev_dist = math.hypot(prev_head[0] - self.food.position[0], prev_head[1] - self.food.position[1])
        cur_dist = math.hypot(cur_head[0] - self.food.position[0], cur_head[1] - self.food.position[1])
        REWARD_DIST = 0
        if prev_dist < cur_dist :
            REWARD_DIST += 10
        elif prev_dist > cur_dist :
            REWARD_DIST -= 7

        '''if self.snake.check_wall_collision(self.snake.body[0]) :'''
        if self.snake.check_wall_collision(self.snake.body[0]) or self.frame_iteration > 100 * len(self.snake.body) :
            game_over = True
            return REWARD_WALL_DEATH, game_over, self.score
        
        '''if self.snake.check_snake_collision(self.snake.body[0]) :'''
        if self.snake.check_snake_collision(self.snake.body[0]) or self.frame_iteration > 100 * len(self.snake.body):
            game_over = True
            return REWARD_SELF_DEATH, game_over, self.score


        '''if self.snake.check_collision(self.snake.body[0]) or self.frame_iteration > 100 * len(self.snake.body):
            game_over = True
            reward += REWARD_DEATH
            return reward, game_over, self.score'''


        # 5. 먹이 섭취 및 보상 적용
        if self.snake.body[0] == self.food.position:
            self.score += 1
            self.snake.grow()
            self.food.spawn()
            return REWARD_FOOD, game_over, self.score
        
        # 6. 한 칸 이동 페널티 적용 (먹이를 먹거나 죽지 않았을 때)
        self.draw()
        self.CLOCK.tick(120)
        return REWARD_STEP + REWARD_DIST, game_over, self.score

    def run(self) :
        self.reset_game()

        # Game 클래스의 run 메서드 내부
        running = True
        while running:
            # 1. 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # 키 입력에 따라 뱀 방향 변경
                    if event.key == pygame.K_UP:
                        self.snake.change_direction((0, -self.CELL_SIZE))
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction((0, self.CELL_SIZE))
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction((-self.CELL_SIZE, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction((self.CELL_SIZE, 0))
            

            # 2. 게임 상태 업데이트 (뱀 이동, 충돌 감지)
            self.snake.move()

            # 뱀이 먹이를 먹었는지 확인
            if self.snake.body[0] == self.food.position:
                self.score += 10
                self.snake.grow() # 뱀 몸통 늘리기
                self.food.spawn() # 새 먹이 생성

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