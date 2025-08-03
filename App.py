
import pygame
from Game import Game
from Agent import Agent


# Pygame 초기화
pygame.init()

# 화면 설정
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
CLOCK = pygame.time.Clock()
pygame.display.set_caption("Snake Game")

'''
myGame = Game(
        clock=CLOCK,
        screen_width=SCREEN_WIDTH, 
        screen_height=SCREEN_HEIGHT, 
        cell_size=CELL_SIZE, 
        screen=SCREEN
    )
    myGame.run()
'''

def train(pre_trained_weight = None):
    agent = Agent()
    myGame = Game(
        clock=CLOCK,
        screen_width=SCREEN_WIDTH, 
        screen_height=SCREEN_HEIGHT, 
        cell_size=CELL_SIZE, 
        screen=SCREEN
    )
    myGame.reset_game()

    if pre_trained_weight != None:
        agent.load_model(pre_trained_weight)

    total_reward = 0
    while True:
        # 1. 현재 상태 가져오기
        old_state = agent.get_state(myGame)

        # 2. 에이전트의 행동 선택
        final_move = agent.get_action(old_state, agent.n_games)

        # 3. 에이전트의 행동 실행 및 결과 얻기
        # play_step 함수 내부에서 화면 그리기, clock.tick(), 이벤트 처리를 모두 수행해야 함.
        reward, done, score = myGame.play_step(action=final_move, n_games=agent.n_games)
        total_reward += reward

        new_state = agent.get_state(myGame)

        # 4. 짧은 메모리 학습
        # max(0, reward) 로직을 사용하지 않아야 함
        agent.train_short_memory(old_state, final_move, reward, new_state, done)
        

        # 5. 경험 저장
        agent.remember(old_state, final_move, reward, new_state, done)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            myGame.draw()
            myGame.CLOCK.tick(120)

        if done:
            print('Game', agent.n_games, 'Score', score, 'Total Reward:', total_reward)

            # 6. 긴 메모리(경험 재생) 학습
            myGame.reset_game()
            agent.n_games += 1
            agent.train_long_memory()
            total_reward = 0

            # 7. 최고 기록(점수 기준) 업데이트
            if score > agent.record:
                agent.record = score
                agent.reward = reward # 최고 점수 기록 시 최종 보상도 함께 저장

                # cnt 변수는 필요 없음. n_games로 대체 가능
                if agent.n_games % 500 == 0:
                    agent.model.save(agent.n_games)

            

train()