import os
from flask import Blueprint
from flask import render_template
from flask import make_response, request
import numpy as np
from static.python.MLModel import RFModel
import static.python.detect as detect
from collections import defaultdict
from PIL import Image
import io


bp = Blueprint("route_blue", __name__)

labels = {
    0: '正常',
    1: '积冰，程度：轻微',
    2: '积冰，程度：严重',
    3: '积冰，程度：非常严重',
    4: '三条裂痕，程度：[轻微，轻微，轻微]',
    5: '三条裂痕，程度：[严重，严重，轻微]',
    6: '三条裂痕，程度：[严重，严重，严重]',
    7: '三条裂痕，程度：[非常严重，严重，严重]',
    8: '三条裂痕，程度：[非常严重，非常严重，严重]',
    9: '三条裂痕，程度：[非常严重，非常严重，非常严重]'
}

root_path = 'demo_data'
data_path = os.path.join(root_path, 'datas')
model_path = os.path.join(root_path, 'model_files')

# 加载模型
clf_low = RFModel('RF_-15')
clf_low.load(os.path.join(model_path, 'RF_-15.pickle'))
clf_high = RFModel('RF_+35')
clf_high.load(os.path.join(model_path, 'RF_+35.pickle'))

# 加载数据
X_low = np.load(os.path.join(data_path, 'X_valid_-15.npy'))
Y_low = np.load(os.path.join(data_path, 'Y_valid_-15.npy'))
X_high = np.load(os.path.join(data_path, 'X_valid_+35.npy'))
Y_high = np.load(os.path.join(data_path, 'Y_valid_+35.npy'))

count_low, count_high = 0, 0
right_low, right_high = 0, 0

m_low, _ = X_low.shape
m_high, _ = X_high.shape

file_chahe = defaultdict(dict)

save_img_path = r'./static/photo'
move_img_path = r'./img_store'

@bp.route("/")
def index():
    """Show all the posts, most recent first."""
    for _ in range(150):
        run_model()
    return render_template("views/index.html")

basedir = os.path.abspath(os.path.dirname(__file__))
 
@bp.route('/up_photo', methods=['post'])
def up_photo():
    img = request.files.get('photo')
    path = f"{basedir}/static/photo/"
    file_path = path+img.filename
    img.save(file_path)
    return file_path

@bp.route('/upload_file', methods=['post'])
def upload_file():
    data = request.get_data()
    file_name = request.args.get('filename')
    chunk_index = request.args.get('chunk')
    chunk_count = int(request.args.get('chunks'))
    file_chahe[file_name][chunk_index] = data
    if len(file_chahe[file_name]) == chunk_count:
        file_data = b''
        for i in range(chunk_count):
            file_data += file_chahe[file_name][str(i)]
        save_binary_image(file_data, os.path.join(save_img_path, file_name))
        del file_chahe[file_name]
        return 'GETALL'
    else:
        return 'GET'

@bp.route('/check_file/<file_name>')
def check_file(file_name):
    if os.path.exists(os.path.join(move_img_path, file_name)) \
        or os.path.exists(os.path.join(save_img_path, file_name)):
        return "EXIST"
    return ','.join(file_chahe[file_name].keys()) if file_name in file_chahe else ''


@bp.route("/yolo/<img_name>")
def yolo(img_name):
    weights=r'./demo_data/model_files/yolov5s_best.pt'
    data=r'./demo_data/blade.yaml'
    model = detect.load_model(weights, data, '')
    img_path, _ = detect.run(
        model,
        os.path.join(r'demo_data/datas/images', img_name),  # file/dir/URL/glob/screen/0(webcam)
        os.path.join('static'),  # save results to project/name
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        nosave=False,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        name='detect',  # save results to project/name
        exist_ok=True,  # existing project/name ok, do not increment
        line_thickness=10,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        vid_stride=1,  # video frame-rate stride
    )
    # with open(img_path, 'rb') as im:
    #     image_data = im.read()
    #     response = make_response(image_data)
    #     response.headers['Content-Type'] = 'image/png'
    return {'save_dir': img_path}

@bp.route("/rf")
def RF():
    pred, true, temp = run_model()
    return {'temp': temp, 'true': labels[true],'pred': labels[pred],
            '-15': 100 if count_low == 0 else np.around(right_low/count_low*100, 2), 
            '+35': 100 if count_high == 0 else np.around(right_high/count_high*100, 2)}

def run_model():
    if np.random.random() < 0.5:
        temp = '-15'
        tmp = np.random.randint(m_low)
        pred = clf_low.best_estimator.predict(X_low[tmp:tmp+1, ...])[0]
        true = Y_low[tmp, 0]
        global count_low
        global right_low
        count_low += 1
        right_low += (pred == true)
    else:
        temp = '+35'
        tmp = np.random.randint(m_high)
        pred = clf_high.best_estimator.predict(X_high[tmp:tmp+1, ...])[0]
        true = Y_high[tmp, 0]
        global count_high
        global right_high
        count_high += 1
        right_high += (pred == true)
    return pred, true, temp

def save_binary_image(binary_data, file_path):
    # 将二进制数据读取为Image对象
    image = Image.open(io.BytesIO(binary_data))

    # 保存图片
    with open(file_path, 'wb') as file:
        image.save(file, 'JPEG')

