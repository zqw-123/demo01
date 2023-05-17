from cassandra.cluster import Cluster
import time
from Config import *

def connect_cassandra():
    count = 0
    while(count<5): #尝试连接5次，失败则退出
        try:
            cluster = Cluster(cassandra_host, cassandra_port, protocol_version=protocol_version)
            session = cluster.connect()
            print('Conncet cassandra successful!')
            return True
        except:
            time.sleep(1)
            count+=1
    if count==5:
        print('Connet cassandra time out! Please check again')
        return False