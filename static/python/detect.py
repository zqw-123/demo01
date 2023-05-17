import os
import sys
import shutil
from pathlib import Path
yolov5_path = str(Path(__file__).resolve().parent)
if yolov5_path not in sys.path:
    sys.path.append(yolov5_path)  # add ROOT to PATH
import torch

from models.common import DetectMultiBackend
from utils.dataloaders import LoadImages
from utils.general import (check_img_size, cv2, increment_path, non_max_suppression, scale_boxes)
from utils.plots import Annotator, colors
from utils.torch_utils import select_device

def load_model(weights, data_path, device, dnn=False, half=False):
    # Load model
    device = select_device(device)
    return DetectMultiBackend(weights, device=device, dnn=dnn, data=data_path, fp16=half)

def run(
        model,
        source,  # file/dir/URL/glob/screen/0(webcam)
        project,  # save results to project/name
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        nosave=False,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        name='exp',  # save results to project/name
        exist_ok=False,  # existing project/name ok, do not increment
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        vid_stride=1,  # video frame-rate stride
        move_img=False, # move detected img file or not
        move_path='' 
    ):
    save_img = not nosave
    # Directories
    save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run
    save_dir.mkdir(parents=True, exist_ok=True)  # make dir

    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size
    dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
    if dataset.nf == 0:
        return "", 0
    save_path = ''
    img_num = 0
    for path, im, im0s, vid_cap, s in dataset:
        im = torch.from_numpy(im).to(model.device)
        im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim

        visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
        pred = model(im, augment=augment, visualize=visualize)

        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

        # Process predictions
        for i, det in enumerate(pred):  # per image
            p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)

            p = Path(p)  # to Path
            save_path = str(save_dir / p.name)  # im.jpg
            s += '%gx%g ' % im.shape[2:]  # print string
            annotator = Annotator(im0, line_width=line_thickness, example=str(names))
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()


                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if save_img:  # Add bbox to image
                        c = int(cls)  # integer class
                        label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                        if label.startswith('Erosion'):
                            continue
                        annotator.box_label(xyxy, label, color=colors(c, True))

            # Save results (image with detections)
            if save_img:
                cv2.imwrite(save_path, im0)

            if move_img:
                try:
                    _, fname=os.path.split(path)             # 分离文件名和路径
                    if not os.path.exists(move_path):
                        os.makedirs(move_path)                       # 创建路径
                    shutil.move(path, os.path.join(move_path, fname))          # 移动文件
                    img_num += 1
                except:
                    print('error')
    return save_path, img_num