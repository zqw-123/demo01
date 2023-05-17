import redis
from Mysql_fun import connect_mysql
from Cassandra_fun import connect_cassandra
from Init_fun import init
from Monitor_fun import response
import time
import os
from Config import *

def start_redis():
    os.system('redis-server --daemonize yes')
def pub_sub():
    pass
def sub_redis():
    r = redis.Redis(host=redis_host,port=redis_port,password='',decode_responses=True)
    r.set("msg","client1 connect to redis_server sucessfully!")
    print(r.get("msg"))
        
    ps = r.pubsub()    
    
    ps.subscribe(channel_name)  
    for item in ps.listen(): 
        if item['type'] == 'message':
            response()
            return True
    
    
        
def main():
    tag = connect_mysql()
    if not tag:
        raise Exception
    tag = connect_cassandra()
    if not tag:
        raise Exception
    start_redis()
    time.sleep(1)
    tag = init()
    if not tag:
        raise Exception
    tag = sub_redis()
    if not tag:
        raise Exception


if __name__ == '__main__' :
    main()
   