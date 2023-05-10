import socket
import os
import random
import multiprocess
from static.python.commfuns import set_log
import argparse
import imghdr
import traceback
import requests

imgType_list = {'jpg','bmp','png','jpeg','rgb','tif'}

# 分片上传文件
def upload_file(file_path, chunk_size=1024*1024):
    assert imghdr.what(file_path) in imgType_list, '请选择正确的图片格式'
    
    file_name = os.path.split(file_path)[-1]
    if args.proto_type == 'TCP':
        res = send_data_by_tcp(file_name.encode(), args.tcp_server_ip, args.tcp_server_port)
    else:
        res = check_file_by_http(file_name)
  
    if res == 'EXIST':
        logger.info('文件已上传')
        return

    sended_id = res.split(',')

    file_size = os.path.getsize(file_path)

    # 计算分片数量
    chunk_count = (file_size // chunk_size) + (1 if file_size % chunk_size != 0 else 0)
    with open(file_path, 'rb') as file:
        # 分别上传文件分片
        for i in range(chunk_count):
            if str(i) in sended_id:
                # logger.info(f'分片{i}已上传')
                continue
            # 计算分片大小和偏移量
            offset = i * chunk_size
            chunk_num = min(chunk_size, file_size - offset)

            # 读取分片数据
            file.seek(offset)
            chunk_data = file.read(chunk_num)

            # 调用API上传分片
            params = {
                'filename': file_name,  # 文件名
                'chunk': i,  # 分片索引
                'chunks': chunk_count,  # 分片数量
            }
            if args.proto_type == 'TCP':
                params['chunk_data'] = chunk_data
                tmp_process = multiprocess.Process(target=async_send_data_by_tcp, 
                    args=(str(params).encode(), 'send', print_info, 
                    *(i, file_name, log_path, args.tcp_server_ip, args.tcp_server_port)))
            else:
                tmp_process = multiprocess.Process(target=async_send_data_by_http, 
                    args=(chunk_data, params, print_info, 
                    *(i, file_name, log_path, post_url)))
            tmp_process.start()
            

def print_info(res, *args):
    i, file_name, logger = args
    if 'ERROR' in res:
        logger.info(f'分片{i}上传失败:{res}')
    elif res == 'GET':
        logger.info(f'分片{i}上传成功')
    else:
        logger.info(f'分片{i}上传成功')
        logger.info(f'图片{file_name}上传成功')

# ============================TCP=======================
def send_data_by_tcp(data, host, port, op_type='check'):
    assert type(data) == bytes, '输入数据类型需要为bytes'
    # 创建客户端 socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 连接服务器
    client_socket.connect((host, port))

    # 组装数据
    head = b'\x95\x67'
    tail = b'\x76\x59'
    type_code = b'\x00' if op_type == 'check' else b'\x01' # 00:check, 01:send
    # 发送数据
    client_socket.sendall(head + type_code + data + tail)

    # 接受数据
    res = client_socket.recv(1024)

    # 关闭连接
    client_socket.close()
    return res.decode()

def async_send_data_by_tcp(data, op_type='check', callback=None, *args):
    i, file_name, log_path, host, port = args
    logger = set_log(None, 'upload_file', log_path)
    try:
        res = send_data_by_tcp(data, host, port, op_type)

        if callback is None:
            return res
        else:
            callback(res, *(i, file_name, logger))
    except BaseException:
        logger.error(traceback.format_exc())

# =============================HTTP==============================
def check_file_by_http(file_name):
    res = requests.get(f'{check_url}/{file_name}')
    return res.text

def async_send_data_by_http(chunk_data, params, callback=None, *args):
    i, file_name, log_path, post_url = args
    logger = set_log(None, 'upload_file', log_path)
    try:
        headers = {'Content-Type': 'application/octet-stream'}
        response = requests.post(post_url, params=params, data=chunk_data, headers=headers)

        if response.status_code == 200:
            res = response.text
        else:
            res = 'ERROR CODE: {response.status_code}'

        if callback is None:
            return res
        else:
            callback(res, *(i, file_name, logger))
    except BaseException:
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path', type=str, default=r'demo_data\datas\images\0006.jpg', help="文件路径")
    parser.add_argument('--log_path', type=str, default='logs', help="日志保存文件夹路径")
    parser.add_argument('--proto_type', type=str, default='HTTP', help="协议类型：HTTP、TCP(default)")
    parser.add_argument('--tcp_server_ip', type=str, help="TCPSERVER IP，当proto_type=TCP时填写")
    parser.add_argument('--tcp_server_port', type=int, help="TCPSERVER PORT，当proto_type=TCP时填写")
    parser.add_argument('--http_url', type=str, help="HTTP URL，当proto_type=HTTP时填写")
    args = parser.parse_args()

    assert os.path.exists(args.file_path), '请填写正确的文件路径'
    assert args.proto_type in ['TCP', 'HTTP'], '请填写正确的协议：[TPC, HTTP]'
    if args.proto_type == 'TCP':
        assert args.tcp_server_ip is not None and args.tcp_server_port is not None, '请填写TCP SERVER的IP和PORT'
    elif args.proto_type == 'HTTP':
        assert args.http_url is not None, '请填写HTTP SERVER的URL'
        check_url = f'{args.http_url}/check_file'
        post_url = f'{args.http_url}/upload_file'

    log_path = os.path.abspath(args.log_path)
    logger = set_log(None, 'upload_file', log_path)
    logger.info(f'基于协议【{args.proto_type}】传输文件')
    try:
        upload_file(args.file_path)
    except BaseException:
        logger.error(traceback.format_exc())