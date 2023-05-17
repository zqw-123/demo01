
import threading
import argparse
import os
import traceback
from static.python.detect import load_model, run
from static.python.commfuns import set_log

def time_handler():
    # 申明全局日志实例
    global logger
    log_path = os.path.abspath(args.log_path)
    logger = set_log(logger, 'AutoDetect', log_path)
    try:
        _, nums = run(
            model,
            os.path.abspath(args.source),  # file/dir/URL/glob/screen/0(webcam)
            os.path.abspath(args.project),  # save results to project/name
            args.imgsz,  # inference size (height, width)
            args.conf_thres,  # confidence threshold
            args.iou_thres,  # NMS IOU threshold
            args.max_det,  # maximum detections per image
            args.nosave,  # do not save images/videos
            args.classes,  # filter by class: --class 0, or --class 0 2 3
            args.agnostic_nms,  # class-agnostic NMS
            args.augment,  # augmented inference
            args.visualize,  # visualize features
            args.name,  # save results to project/name
            args.exist_ok,  # existing project/name ok, do not increment
            args.line_thickness,  # bounding box thickness (pixels)
            args.hide_labels,  # hide labels
            args.hide_conf,  # hide confidences
            args.vid_stride,  # video frame-rate stride
            args.move_img,
            args.move_path
        )
        if nums > 0:
            logger.info(f"成功处理{nums}张图片")

    except BaseException:
        logger.error(f'\n{traceback.format_exc()}')
    finally:
        timer = threading.Timer(args.inteval, time_handler)
        timer.start()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inteval', type=int, default="5", help="")
    parser.add_argument('--log_path', type=str, default='logs', help='')
    parser.add_argument('--weights', nargs='+', type=str, default=r'./demo_data/model_files/yolov5s_best.pt', help='model path or triton URL')
    parser.add_argument('--source', type=str, default=os.path.join('static', 'photo'), help='file/dir/URL/glob/screen/0(webcam)')
    parser.add_argument('--project', default=os.path.join('static'), help='save results to project/name')
    parser.add_argument('--data', type=str, default=r'./demo_data/blade.yaml', help='(optional) dataset.yaml path')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf_thres', type=float, default=0.1, help='confidence threshold')
    parser.add_argument('--iou_thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max_det', type=int, default=1000, help='maximum detections per image')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--name', default='detect', help='save results to project/name')
    parser.add_argument('--exist_ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--line_thickness', default=10, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide_labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide_conf', default=False, action='store_true', help='hide confidences')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    parser.add_argument('--vid_stride', type=int, default=1, help='video frame-rate stride')
    parser.add_argument('--move_img', action='store_true', help='move the img or not')
    parser.add_argument('--move_path', type=str, default='img_store', help='move img to move_path')
    args = parser.parse_args()
    args.imgsz *= 2 if len(args.imgsz) == 1 else 1  # expand
    return args

if __name__ == "__main__":
    # global args
    args = parse_args()
    # Delete
    args.exist_ok = True
    args.move_img = True

    logger = None
    weights = os.path.abspath(args.weights)
    data = os.path.abspath(args.data)
    model = load_model(weights, data, args.device, args.dnn, args.half)
    time_handler()