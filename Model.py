import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os

class Snake_AI(nn.Module) :
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    
    def save(self, file_name, lr=0):
        model_folder_path = './weights'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        
        file_name = os.path.join(model_folder_path,"lr_" +str(float(lr)) +"_ver_"+str(file_name))
        torch.save(self.state_dict(), file_name+".pth")

class Snake_Advanced_AI(nn.Module):
    def __init__(self, input_size, hidden_size, output_size, dropout_p=0.3):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.ㅣn1 = nn.LayerNorm(hidden_size)
        self.dropout1 = nn.Dropout(dropout_p)
        
        self.linear2 = nn.Linear(hidden_size, hidden_size)
        self.ln2 = nn.LayerNorm(hidden_size)
        self.dropout2 = nn.Dropout(dropout_p)

        self.linear3 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # 입력이 1차원([11])이면 2차원([1,11])으로 변환
        if x.dim() == 1:
            x = x.unsqueeze(0)
        x = F.relu(self.ㅣn1(self.linear1(x)))
        x = self.dropout1(x)
        x = F.relu(self.ln2(self.linear2(x)))
        x = self.dropout2(x)
        x = self.linear3(x)
        return x

    def save(self, file_name, lr=0):
        model_folder_path = './weights'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        
        file_name = os.path.join(model_folder_path,"lr_" +str(lr) +"_ver_"+str(file_name))
        torch.save(self.state_dict(), file_name+".pth")

class Trainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)

        # 1: 예측된 Q 값
        pred = self.model(state)

        # 2: Q_new = reward + gamma * max(next_predicted_Q_value)
        target = pred.clone()
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))
            target[idx][torch.argmax(action[idx]).item()] = Q_new

        # 역전파
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        #print("Loss:", loss.item())
        loss.backward()
        self.optimizer.step()
        
        return loss.item()
        
