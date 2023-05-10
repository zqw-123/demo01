import socket
from collections import defaultdict
import os
from PIL import Image
import io
import argparse
from static.python.commfuns import set_log
import traceback

mem_dict = defaultdict(bytes)
file_chahe = defaultdict(dict)
HEAD = b'\x95\x67'
TAIL = b'\x76\x59'

move_img_path = r'img_store'

def save_binary_image(binary_data, file_path):
    # 将二进制数据读取为Image对象
    image = Image.open(io.BytesIO(binary_data))
    # 确定图片类型
    img_type = ''
    if binary_data[:3] == b'\xff\xd8\xff':
        img_type = 'JPEG'
    elif binary_data[:4] == b'\x89\x80\x4e\x47':
        img_type = 'PNG'
    else:
        return False
    # 保存图片
    with open(file_path, 'wb') as file:
        image.save(file, 'JPEG')
    return True

def trans_data(key, client_socket):
    data = mem_dict[key]
    if data[:2] != HEAD or data[-2:] != TAIL:
        del mem_dict[key]
        client_socket.sendall('ERROR: 接受到的数据不全'.encode())
        return
    if data[2] == 0:
        file_name = data[3:-2].decode()
        if os.path.exists(os.path.join(move_img_path, file_name)) \
            or os.path.exists(os.path.join(save_img_path, file_name)):
            msg = 'EXIST'
        else:
            msg = ','.join(file_chahe[file_name].keys()) if file_name in file_chahe else ''
    else:
        dic_msg = eval(data[3:-2])
        file_name = dic_msg['filename']
        chunk_index = str(dic_msg['chunk'])
        chunk_count = dic_msg['chunks']
        file_chahe[file_name][chunk_index] = dic_msg['chunk_data']
        if len(file_chahe[file_name]) == chunk_count:
            file_data = b''
            for i in range(chunk_count):
                file_data += file_chahe[file_name][str(i)]
            if not save_binary_image(file_data, os.path.join(save_img_path, file_name)):
                msg = 'ERROR: 获取到错误格式文件'
                logger.info('获取到错误格式文件')
            else:
                msg = 'GETALL'
                logger.info('接收图片成功')
            del file_chahe[file_name]
        else:
            msg = 'GET'
    client_socket.sendall(msg.encode())


if __name__ == '__main__':
     
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_img_path', type=str, default=r'./static/photo', help="")
    parser.add_argument('--log_path', type=str, default='logs', help="")
    parser.add_argument('--server_url', type=str, default='127.0.0.1', help="")
    parser.add_argument('--server_port', type=int, default='3333', help="")
    args = parser.parse_args()

    save_img_path = args.save_img_path
    logger = set_log(None, 'tcp_server_for_get_file', args.log_path)
    
    # 创建tcp服务端socket
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定端口
    tcp_server_socket.bind(("", args.server_port))
    # 设置监听，把服务端socket由主动套接字改成被动套接字，只能接收客户端的连接请求
    tcp_server_socket.listen(128)

    if not  os.path.exists(save_img_path):
        os.makedirs(save_img_path)

    while True:
        try:
            # 接收客户端信息
            client_socket, client_ip = tcp_server_socket.accept()
            logger.info(f"客户端：{client_ip}连接")
            with client_socket:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    mem_dict[client_ip] += data

                    if data[-2:] == TAIL:
                        trans_data(client_ip, client_socket)
                        break
                        
            logger.info(f"客户端：{client_ip}断开")
        except BaseException:
            logger.error(traceback.format_exc())


