import torch
from torch import nn
from tqdm import tqdm
import os
from sklearn.model_selection import GridSearchCV
import os
import pickle #pickle模块


class BasicTorchModel(nn.Module):
    '''
    神经网络基础类
    '''
    def __init__(self):
        super().__init__()

    def score(self, dataloader, params_set=None, device='cpu'):
        '''
        验证精度函数
        params:
            dataloader: 数据集
            device: 默认为cpu,可修改为gpu
        '''
        res = [0, 0]
        size = len(dataloader.dataset)
        num_batches = len(dataloader)
        self.to(device)
        self.eval()
        test_loss, correct = 0, 0
        if self.metric_fn is not None:
            self.metric_fn.reset()
        with torch.no_grad():
            for X, y in dataloader:
                X, y = X.to(device), y.to(device)
                #控制自定义损失函数(损失函数需要输出损失和预测值)
                if params_set is not None:
                    params = {}
                    if 'model' in params_set: params['model'] = self
                    if 'x' in params_set: params['x'] = X
                    if 'y' in params_set: params['y'] = y
                    # 特定的loss_fn，必须同时传回loss和pred
                    loss, pred = self.loss_fn(params)
                    test_loss += loss.item()
                    
                else:
                    pred = self(X)
                    test_loss += self.loss_fn(pred, y) #损失之和
                if self.metric_fn is not None:
                    correct = self.metric_fn(pred, y)  #返回预测正确的个数

        test_loss /= num_batches
        res[0] = test_loss
        if self.metric_fn is not None: 
            correct /= size
            res[1] = correct
        
        return res

    def fit(self, train_iter, valid_iter, epochs=20, params_set=None, device='cpu', leave=True):
        '''
        输入:
        训练集、测试集
        params_set:控制损失函数是否为特殊自定义损失函数
        '''
        size = len(train_iter.dataset)
        num_batches = len(train_iter)
        self.to(device)
        for i in range(epochs):
            self.train()
            current = 0
            #输入metric，将acc初始化为0
            if self.metric_fn is not None:
                self.metric_fn.reset()
            with tqdm(total=num_batches, leave=leave) as t:
                t.set_description(f'Epoch {i + 1} / {epochs}')
                for X, y in train_iter:
                    self.optimizer.zero_grad()
                    X, y = X.to(device), y.to(device)

                    #控制是否为自定义损失函数
                    if params_set is not None:
                        params = {}
                        if 'model' in params_set:
                            params['model'] = self
                        if 'x' in params_set:
                            params['x'] = X
                        if 'y' in params_set:
                            params['y'] = y
                        loss, pred = self.loss_fn(params)
                    else:
                        pred = self(X)
                        loss = self.loss_fn(pred, y)

                    # Backpropagation
                    loss.backward()
                    self.optimizer.step()

                    #计算精度，输入metric的时候，acc更新为self.metric_fn，当没有输入metric的时候，不能返回acc
                    loss, current = loss.item(), current + len(X)
                    params = {"loss": round(loss, 4)}
                    if self.metric_fn is not None:
                        acc = self.metric_fn(pred, y)
                        params["acc"] = round(acc / current, 4)
                    t.set_postfix(params)
                    t.update(1)

                #计算测试集的损失和精度，不是分类问题时，不输出精度
                valid_res = self.score(valid_iter, params_set=params_set, device=device)
                params["val_loss"] = round(float(valid_res[0]), 4)
                if self.metric_fn is not None:
                    params["val_acc"] = round(float(valid_res[1]), 4)
                t.set_postfix(params)

    def test(self, test_iter, params_set=None, device='cpu'):
        if self.metric_fn is not None:
            test_loss, correct = self.score(test_iter,params_set = params_set,device = device)
        print(f"Test Error: \n Accuracy: {(100*correct):>0.1f}%, Avg loss: {test_loss:>8f} \n")

    def save(self, root_path, mysql_fun, id_motor=0):
        '''
        保存模型原型参数
            这里只保存模型原型是因为，对于电机专属的模型，只做更新操作
        params:
            root_path: 文件储存路径，不包含文件名
            mysql_fun: mysql相关函数
        '''
        os.makedirs(root_path, exist_ok=True)
        file_path = os.path.join(root_path, f'{self.model_name}.pt')
        torch.save(self.state_dict(), file_path)

        # 存到mysql中
        if id_motor == 0:
            # 代表是原型模型
            mysql_fun.insert_proto_model_and_file(self.model_name, file_path)
        else:
            # 代表是模型更新
            mysql_fun.update_model_and_file(id_motor, self.model_name, file_path)
        return file_path


    def load(self, file_path):
        '''
        加载模型参数
        params:
            file_path: 文件储存路径，包含文件名
        '''
        if not os.path.isfile(file_path):
            raise (f'模型文件：[{file_path}] 不存在')
        m_state_dict = torch.load(file_path)
        self.load_state_dict(m_state_dict)

class BasicModel(object):

    def save(self, root_path, mysql_fun=None, id_motor=0):
        '''
        保存模型原型参数
        params:
            root_path: 文件储存路径，不包含文件名
            mysql_fun: mysql相关函数
            id_motor: 
        '''
        os.makedirs(root_path, exist_ok=True)
        file_path = os.path.join(root_path, f'{self.model_name}.pickle')
        with open(file_path, 'wb') as f:
            pickle.dump(self.best_estimator, f)

        # 存到mysql中
        if mysql_fun:
            if id_motor == 0:
                # 代表是原型模型
                mysql_fun.insert_proto_model_and_file(self.model_name, file_path)
            else:
                # 代表是模型更新
                mysql_fun.update_model_and_file(id_motor, self.model_name, file_path)
        return file_path


    def load(self, file_path):
        '''
        加载模型参数
        params:
            file_path: 文件储存路径，包含文件名
        '''
        if not os.path.isfile(file_path):
            raise (f'模型文件：[{file_path}] 不存在')
        with open(file_path, 'rb') as f:
            self.best_estimator = pickle.load(f)

class BasicMLModel(BasicModel):

    def fit(self, X, Y, parameters, **kwargs):
        clf = GridSearchCV(self.model, parameters, **kwargs)
        clf.fit(X, Y)
        self.best_estimator = clf.best_estimator_
        print(f'The best score: {clf.best_score_} in params: {clf.best_params_}')
    
    def score(self, X, Y):
        return self.best_estimator.score(X, Y)