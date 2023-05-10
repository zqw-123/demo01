import time
import logging
import sys
import os

def set_log(logger, logger_name, root_path='./logs'):
    '''
    日志参数配置
    '''
    if logger is None:
        # create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        # create file handler
        now_time = time.strftime('%Y%m%d')
        log_path = f"{root_path}/log_{logger_name}_{now_time}.log"
        if not os.path.exists(root_path):
            os.makedirs(root_path)
        fh_handler = logging.FileHandler(log_path, encoding='utf-8')
        fh_handler.setLevel(logging.DEBUG)

        # create sys handler
        sys_handler = logging.StreamHandler(sys.stderr)
        sys_handler.setLevel(logging.DEBUG)

        # create formatter
        fmt = "%(asctime)-15s | %(levelname)s | %(filename)s:%(funcName)s:%(lineno)d:%(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(fmt, datefmt)

        # add handler and formatter to logger
        fh_handler.setFormatter(formatter)
        logger.addHandler(fh_handler)
        sys_handler.setFormatter(formatter)
        logger.addHandler(sys_handler)
    else:
        now_time = time.strftime('%Y%m%d')
        log_path = f"{root_path}/log_{logger_name}_{now_time}.log"
        fh_handler = logging.FileHandler(log_path, encoding='utf-8')
    return logger 