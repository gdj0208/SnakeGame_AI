import torch
import random
from collections import deque
from Model import Snake_AI, Trainer, Snake_Advanced_AI
import os
import numpy as np

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.0001
EPSILON_BASE = 120 # 80

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9 # 할인율
        self.memory = deque(maxlen=MAX_MEMORY)
        # self.model = Snake_AI(11, 256, 3) # 입력 11차원, 은닉층 256, 출력 3차원
        self.model = Snake_Advanced_AI(11, 256, 3)
        self.trainer = Trainer(self.model, lr=LR, gamma=self.gamma)
        self.record = 0
        self.reward = 0

    def get_state(self, game):
        def check_collision_dir_and_porint(dir, point) :
            return dir and game.is_collision(point)
        
        head = game.snake.body[0]

        # 뱀 머리 상하좌우
        point_l = (head[0] - 20, head[1])
        point_r = (head[0] + 20, head[1])
        point_u = (head[0], head[1] - 20)
        point_d = (head[0], head[1] + 20)

        # 뱀의 이동 방향 정보
        dir_l = game.snake.direction == (-20, 0)
        dir_r = game.snake.direction == (20, 0)
        dir_u = game.snake.direction == (0, -20)
        dir_d = game.snake.direction == (0, 20)

        # 뱀 전방 충돌 확인
        danger_front = check_collision_dir_and_porint(dir_r, point_r) or check_collision_dir_and_porint(dir_l, point_l) or check_collision_dir_and_porint(dir_u, point_u) or check_collision_dir_and_porint(dir_d, point_d)

        # 뱀 좌측 충돌 확인
        danger_left = check_collision_dir_and_porint(dir_r, point_u) or check_collision_dir_and_porint(dir_l, point_d) or check_collision_dir_and_porint(dir_u, point_l) or check_collision_dir_and_porint(dir_d, point_r)

        # 뱀 우측 충돌 확인
        danger_right = check_collision_dir_and_porint(dir_r, point_d) or check_collision_dir_and_porint(dir_l, point_u) or check_collision_dir_and_porint(dir_u, point_r) or check_collision_dir_and_porint(dir_d, point_l)

        # 뱀 머리와 먹이와의 거리 (x,y)
        dx = game.food.position[0] - head[0]
        dy = game.food.position[1] - head[1]

        # 뱀의 머리, 먹이 위치, 충돌 위험 등 11가지 상태 정보
        state = [
            # 1. 위험 예측 : 배의 다음 움직임에 벽, 뱀 몸통 여부
            danger_front,   # [0] 뱀이 현재 방향으로 한 칸 이동 시 충돌 위험 여부
            danger_left,    # [1] 뱀이 현재 방향에서 오른쪽으로 회전 시 충돌 위험 여부
            danger_right,   # [2] 뱀이 현재 방향에서 왼쪽으로 회전 시 충돌 위험 여부

            # 2. 현재 방향 : 뱀이 이동하는 방향
            dir_r,          # [3] 뱀이 오른쪽으로 이동 중인지 여부
            dir_l,          # [4] 뱀이 왼쪽으로 이동 중인지 여부
            dir_u,          # [5] 뱀이 위로 이동 중인지 여부
            dir_d,          # [6] 뱀이 아래로 이동 중인지 여부

            # 3. 먹이 위치 : 뱀 머리 기준으로 먹이의 위치
            dx < 0,         # [7] 먹이가 뱀 머리 왼쪽에 있는지 여부
            dx > 0,         # [8] 먹이가 뱀 머리 오른쪽에 있는지 여부
            dy < 0,         # [9] 먹이가 뱀 머리 위에 있는지 여부
            dy > 0          # [10] 먹이가 뱀 머리 아래에 있는지 여부
        ]
        # return state
        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state, n_games=EPSILON_BASE):
        # 엡실론-그리디 전략을 위한 엡실론값 설정
        self.epsilon = EPSILON_BASE - n_games
        
        # 직진, 좌회전, 우회전
        final_move = [0, 0, 0]

        # 엡실론-그리디 조건부 실행
        new_emp = random.randint(0, 200)
        #print(new_emp)
        if new_emp < self.epsilon:
            # 무작위 탐험
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            # 활용 : 신경망 예측을 바탕으로 최적 활동 설정
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move
    
    def load_model(self, file_name):
        model_folder_path = './weights'
        file_path = os.path.join(model_folder_path, file_name)
        
        if os.path.exists(file_path):
            print(f"Loading pre-trained model from {file_path}")
            self.model.load_state_dict(torch.load(file_path))
        else:
            print(f"No model found at {file_path}. Starting training from scratch.")
