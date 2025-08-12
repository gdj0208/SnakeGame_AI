
import pygame
from Game import Game
from Agent import Agent
from Helper import plot, show_final_score
import argparse


# Pygame 초기화
pygame.init()

# 화면 설정
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
CELL_SIZE = 20
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
CLOCK = pygame.time.Clock()
pygame.display.set_caption("Snake Game")


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

    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    run = True


    if pre_trained_weight != None:
        agent.load_model(pre_trained_weight)

    loss = 0
    cnt=0
    while run:
        # 1. 현재 상태 가져오기
        old_state = agent.get_state(myGame)

        # 2. 에이전트의 행동 선택
        final_move = agent.get_action(old_state, agent.n_games)

        # 3. 에이전트의 행동 실행 및 결과 얻기
        # play_step 함수 내부에서 화면 그리기, clock.tick(), 이벤트 처리를 모두 수행해야 함.
        reward, done, score = myGame.play_step(action=final_move, n_games=agent.n_games)
        new_state = agent.get_state(myGame)

        # loss += reward
        cnt += 1

        # 4. 짧은 메모리 학습
        agent.train_short_memory(old_state, final_move, reward, new_state, done)
        
        # 5. 경험 저장
        agent.remember(old_state, final_move, reward, new_state, done)

        if done:
            # 6. 긴 메모리(경험 재생) 학습
            myGame.reset_game()
            agent.n_games += 1
            agent.train_long_memory()

            print('Game', agent.n_games, 'Score', score, 'Loss:', loss/cnt)
            loss = 0
            cnt = 0

            # 7. 최고 기록(점수 기준) 업데이트
            if score > agent.record:
                # 최고 점수 기록 시 최종 보상도 함께 저장
                agent.record = score
                # agent.reward = reward        

            if agent.n_games % 200 == 0:
                agent.model.save(agent.n_games)

            # 학습 종료
            if agent.n_games >= 1000 :
                run = False

            plot_scores.append(score)  
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)   
            
    show_final_score(plot_scores, plot_mean_scores)

def eval(pre_trained_weight=None):

    if pre_trained_weight != None:
        agent.load_model(pre_trained_weight)
        print(f"Loaded pre-trained model: {pre_trained_weight}")

    myGame.run(agent)



if __name__ == "__main__":

    # 에이전트 초기화
    agent = Agent()

    # 게임 초기화
    myGame = Game(
        clock=CLOCK,
        screen_width=SCREEN_WIDTH, 
        screen_height=SCREEN_HEIGHT, 
        cell_size=CELL_SIZE, 
        screen=SCREEN
    )

    parser = argparse.ArgumentParser()
    parser.add_argument('-mode', type=str, default='eval', help='Mode to run the game: train, eval or selfplay')
    parser.add_argument('-weight', type=str, default=None, help='Pre-trained model weight file name')
    args = parser.parse_args()

    if args.mode == 'train':
        train(args.weight)
    elif args.mode == 'eval':
        eval(args.weight)
    elif args.mode == 'selfplay':
        myGame.run()        
