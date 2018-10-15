import gym
import random
import os
import json
import numpy as np
import pandas as pd
from collections      import deque
from keras.models     import Sequential
from keras.layers     import Dense, CuDNNLSTM, BatchNormalization, Dropout
from keras.optimizers import Adam
from decimal import Decimal


class Agent():
    def __init__(self, state_size, action_size):
        self.weight_backup      = "pk10_weight.h5"
        self.state_size         = state_size
        self.action_size        = action_size
        self.memory             = deque(maxlen=10000)
        self.learning_rate      = 0.001
        self.gamma              = 0.95
        self.exploration_rate   = 1.0
        self.exploration_min    = 0.01
        self.exploration_decay  = 0.995
        self.brain              = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))

        if os.path.isfile(self.weight_backup):
            model.load_weights(self.weight_backup)
            self.exploration_rate = self.exploration_min
        return model

    def save_model(self):
            self.brain.save_weights(self.weight_backup)

    def load_model(self):
            self.brain.load_weights(self.weight_backup)

    def act(self, state):
        if np.random.rand() <= self.exploration_rate:
            return random.randrange(self.action_size)
        act_values = self.brain.predict(state)
        return np.argmax(act_values[0])

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, sample_batch_size):
        if len(self.memory) < sample_batch_size:
            return
        sample_batch = random.sample(self.memory, sample_batch_size)
        for state, action, reward, next_state, done in sample_batch:
            target = reward
            if not done:
              target = reward + self.gamma * np.amax(self.brain.predict(next_state)[0])
            target_f = self.brain.predict(state)
            target_f[0][action] = target
            self.brain.fit(state, target_f, epochs=1, verbose=0)
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay

class PK10_ENV:
    def __init__(self):
        self.total_money = 10000
        self.df = pd.read_csv('fix_pk10.csv')
        self.df_size = self.df.shape[0]
        self.last_state = True
        self.vote_money = 1
        self.max_money = 1
        self.all_max_money = []

    def reset(self):
        self.total_money = 10000
        self.df = pd.read_csv('fix_pk10.csv')
        self.df_size = self.df.shape[0]
        self.last_state = True
        self.vote_money = 1
        self.max_money = 1000

        return [self.last_state, 5]

    def render(self):
        print('my money : {:.1f} max money : {:.1f}'.format(self.total_money, self.max_money))
        #print('max money : {:.1f}'.format(self.max_money))
        self.all_max_money.append(self.max_money)

    def print_size(self):
        print(self.df.shape[0])
    
    def step(self, vote_decision):
        self.total_money -= 5 * self.vote_money
        ran_index = random.randint(1, self.df_size)
        open_result = np.array(self.df[ran_index - 1 : ran_index])
        #print(f'{ran_index} 開獎號碼：{open_result[0][1]} 開獎結果：{open_result[0][-1]} 我下注：{vote_decision} 下注比率：{self.vote_money}')

        if vote_decision != np.array(open_result[0][-1]):
            #print('沒中!')
            reward = -5 * self.vote_money
            self.last_state = False
            self.vote_money = 2 * self.vote_money
        else:
            self.total_money += 1.98 * 5 * self.vote_money
            #print('中獎！')
            reward = 1.98 * 5 * self.vote_money
            self.last_state = True
            self.vote_money = 1
        
        if self.total_money >= self.max_money:
            self.max_money = self.total_money

        if self.total_money <= 0 or self.total_money >= 500000:
            done = True
        else:
            done = False

        return [self.last_state, open_result[0][1]], reward, done


class PK10:
    def __init__(self):
        self.sample_batch_size = 32
        self.episodes          = 10000
        self.env               = PK10_ENV()

        self.state_size        = 2
        self.action_size       = 3
        self.agent             = Agent(self.state_size, self.action_size)

    def run(self):
        try:
            for index_episode in range(self.episodes):
                state = self.env.reset()
                state = np.array([state])
                done = False
                index = 0
                while not done:
                    action = self.agent.act(state)
                    if action == 2:
                        decision = state[0][1] % 2
                    else:
                        decision = action

                    next_state, reward, done= self.env.step(decision)
                    #self.env.render()
                    next_state = np.array([next_state])
                    self.agent.remember(state, action, reward, next_state, done)
                    state = next_state
                    index += 1
                print("Episode {}# Score: {}".format(index_episode, index + 1))
                self.env.render()
                self.agent.replay(self.sample_batch_size)

        finally:
            self.agent.save_model()
            with open('all_max_money.json', 'w') as f:
                json.dump(self.env.all_max_money, f)
                print('wrote!')


if __name__ == "__main__":
    '''
    cartpole = CartPole()
    cartpole.printtt()
    cartpole.run()
    '''
    pk10 = PK10()
    pk10.run()

'''
class CartPole: 
    def __init__(self):
        self.sample_batch_size = 32
        self.episodes          = 10000
        self.env               = gym.make('CartPole-v1')

        self.state_size        = self.env.observation_space.shape[0]
        self.action_size       = self.env.action_space.n
        self.agent             = Agent(self.state_size, self.action_size)

    def printtt(self):
        print(self.state_size, self.action_size)

    def run(self):
        try:
            for index_episode in range(self.episodes):
                state = self.env.reset()
                state = np.reshape(state, [1, self.state_size])

                done = False
                index = 0
                while not done:
                    #self.env.render()

                    action = self.agent.act(state)

                    next_state, reward, done, _ = self.env.step(action)
                    next_state = np.reshape(next_state, [1, self.state_size])
                    self.agent.remember(state, action, reward, next_state, done)
                    state = next_state
                    index += 1
                print("Episode {}# Score: {}".format(index_episode, index + 1))
                self.agent.replay(self.sample_batch_size)
        finally:
            self.agent.save_model()
'''