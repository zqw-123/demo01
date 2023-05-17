import pyd3tn
from pyd3tn.tcpcl import TCPCLConnection
from pyd3tn.bundle6 import serialize_bundle6
from pyd3tn.bundle7 import serialize_bundle7
from PIL import Image
import io
import traceback
import os
import time

def save_binary_image(binary_data, file_path):
    # 将二进制数据读取为Image对象
    image = Image.open(io.BytesIO(binary_data))

    # 保存图片
    with open(file_path, 'wb') as file:
        image.save(file, 'JPEG')

with TCPCLConnection('dtn://node1.dtn/testing', '192.168.0.105', 4556) as conn:
    # conn.send_bundle(serialize_bundle6('dtn://node1.dtn/me', 'dtn://node2.dtn/testing', 
    #                 bytes(b'fafa3')))
    img = b''
    file_type = ''
    n = 0
    while True:
        try:
            flag, buf = conn.recv_bundle()
            n += 1
            if flag == 2:
                # JPEG (jpg)，文件头：FFD8FF
                # PNG (png)，文件头：89504E47
                # GIF (gif)，文件头：47494638
                # TIFF (tif)，文件头：49492A00
                print('start')
                img = b''
                img_index = buf.find(b'\xFF\xD8\xFF')
                img += buf[img_index:]
            elif flag == 1:
                print(f'get {n} parts')
                img += buf
                save_binary_image(img, os.path.join('save_img', f'{int(time.time())}.jpg'))
                print('finished')
            else:
                img += buf
        except BaseException:
            print(traceback.format_exc())
        


