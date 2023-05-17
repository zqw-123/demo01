from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
import os
import sys
import json
import numpy as np
from scipy.stats import gamma
from pathlib import Path
fun_path = str(Path(__file__).resolve().parent)
if fun_path not in sys.path:
    sys.path.append(fun_path)  # add ROOT to PATH

from BasicModel import BasicMLModel

class RFModel(BasicMLModel):
    best_estimator = None
    def __init__(self, name):
        super().__init__()
        self.model_name = name
        self.model = RandomForestClassifier()
    def __call__(self, X):
        return self.best_estimator.predict_proba(X)

class SVCModel(BasicMLModel):
    best_estimator = None
    def __init__(self, name):
        super().__init__()
        self.model_name = name
        self.model = SVC(probability=True)
    def __call__(self, X):
        return self.best_estimator.predict_proba(X)


class OutliersModel(object):

    def __init__(self, name, input_shape):
        super().__init__()
        self.model_name = name
        self.centent = None
        self.weights = np.ones((input_shape[1], 1))
        self.threshold_gamma = 0.99
        self.threshold = 0

    def __call__(self, X):  # sourcery skip: raise-specific-error
        if self.centent is None or self.threshold <= 0:
            raise BaseException("模型未训练")
        dist = np.sqrt((X - self.centent)**2 @ self.weights)
        res = np.zeros((dist.shape[0], 2))
        res[np.where(dist[:,0] > self.threshold), 1] = 1
        res[np.where(dist[:,0] <= self.threshold), 0] = 1
        return res
        

    def fit(self, X):
        self.centent = np.mean(X, 0)
        dist = np.sqrt((X - self.centent)**2 @ self.weights)
        shape_hat, loc_hat, scale_hat = gamma.fit(dist)
        self.threshold = gamma.ppf(q=self.threshold_gamma, a=shape_hat, loc=loc_hat, scale=scale_hat)


    def score(self, X, Y):
        pred_Y = np.argmax(self(X), axis=1)
        return np.sum(pred_Y==Y) / Y.shape[0]

    def save(self, root_path, mysql_fun, id_motor=0):
        '''
        保存模型原型参数
            这里只保存模型原型是因为，对于电机专属的模型，只做更新操作
        params:
            root_path: 文件储存路径，不包含文件名
            mysql_fun: mysql相关函数
        '''
        os.makedirs(root_path, exist_ok=True)
        file_path = os.path.join(root_path, f'{self.model_name}.json')
        model_params = {
            "model_name": self.model_name,
            "centent": self.centent.tolist(),
            "threshold": self.threshold,
            "weights": self.weights.tolist(),
            "threshold_gamma": self.threshold_w

        }
        with open(file_path, 'w') as f:
            json.dump(model_params, f)

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
        with open(file_path, 'r') as f:
            model_params = json.load(f)
        self.model_name = model_params["model_name"]
        self.centent = np.array(model_params["centent"])
        self.threshold = model_params["threshold"]
        self.weights = np.array(model_params["weights"])
        self.threshold_w = model_params["threshold_gamma"]
