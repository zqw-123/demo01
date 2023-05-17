import pymysql
from Config import *
import time

def connect_mysql():
    count = 0
    while(count<5):#尝试连接5次，失败则退出
        try:
            conn = pymysql.connect(host=mysql_host, port=mysql_port,
                                user=mysql_user, password=mysql_pwd,
                                charset='utf8mb4')
            if conn:
                print('Connect mysql successful!')
                return True
        except BaseException:
            time.sleep(1)
            count+=1
    if count==5:
        print('Connet mysql time out! Please check again')
        return False