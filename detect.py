from ctypes import *
import random
import os
import cv2
import time
import darknet
import argparse
import numpy
from threading import Thread, enumerate
from queue import Queue
from datetime import datetime, timedelta



def parser():
    parser = argparse.ArgumentParser(description="YOLO Object Detection")
    parser.add_argument("--input", type=str, default= "",
                        help="video source. If empty, uses webcam 0 stream")
    parser.add_argument("--out_filename", type=str, default="",
                        help="inference video name. Not saved if empty")
    parser.add_argument("--weights", default="yolov4.weights",
                        help="yolo weights path")
    parser.add_argument("--dont_show", action='store_true',
                        help="windown inference display. For headless systems")
    parser.add_argument("--ext_output", action='store_true',
                        help="display bbox coordinates of detected objects")
    parser.add_argument("--config_file", default="./cfg/yolov4.cfg",
                        help="path to config file")
    parser.add_argument("--data_file", default="./cfg/coco.data",
                        help="path to data file")
    parser.add_argument("--thresh", type=float, default=.90,
                        help="remove detections with confidence below this value")
    parser.add_argument("--clip_time",type=int,default="120")
    return parser.parse_args()


def str2int(video_path):
    """
    argparse returns and string althout webcam uses int (0, 1 ...)
    Cast to int if needed
    """
    try:
        return int(video_path)
    except ValueError:
        return video_path


def check_arguments_errors(args):
    assert 0 < args.thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
    if not os.path.exists(args.config_file):
        raise(ValueError("Invalid config path {}".format(os.path.abspath(args.config_file))))
    if not os.path.exists(args.weights):
        raise(ValueError("Invalid weight path {}".format(os.path.abspath(args.weights))))
    if not os.path.exists(args.data_file):
        raise(ValueError("Invalid data file path {}".format(os.path.abspath(args.data_file))))
    if str2int(args.input) == str and not os.path.exists(args.input):
        raise(ValueError("Invalid video path {}".format(os.path.abspath(args.input))))


def set_saved_video(input_video, output_video, size):
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    fps = int(input_video.get(cv2.CAP_PROP_FPS))
    video = cv2.VideoWriter(output_video, fourcc, fps, size)
    return video

def findtime(milliseconds):
    seconds = milliseconds//1000
    minutes = 0
    hours = 0
    if seconds >= 60:
        minutes = seconds//60
        seconds = seconds % 60

    if minutes >= 60:
        hours = minutes//60
        minutes = minutes % 60
    sec = "%02d"%seconds
    minu = "%02d"%minutes
    h = "%02d"%hours

    timestamp = "{}:{}:{}".format(h,minu,sec)
    return timestamp

def timeconverter(time_list):
    lis = []
    if len(time_list):
        for i in time_list:
            t = findtime(i)
            lis.append(t)
    return lis

def get_clips_time(time_list, clip_t):
    lis = []
    if len(time_list):
        time_list = timeconverter(time_list)
        time_list = list(set(time_list))
        time_list.sort()

        lis.append(time_list[0])
        i = 0
        j = 0
        while i < len(time_list):
            for j in range((i+1),len(time_list)):
                former_time = datetime.strptime(time_list[i], '%H:%M:%S')
                latter_time = datetime.strptime(time_list[j], '%H:%M:%S')
                delta = (latter_time-former_time).seconds
                if delta >= clip_t:
                    lis.append(time_list[j])
                    i = j
                    break
            if j == len(time_list)-1:
                break
    
    numpy.savetxt("./timestamp.txt",lis,fmt='%s')



def video_capture(frame_queue, darknet_image_queue,time_queue,pedestrain_frame):
    while cap.isOpened():
        if not pedestrain_frame.empty():
            pedestrain_time = pedestrain_frame.get(False)
            cap.set(cv2.CAP_PROP_POS_MSEC, pedestrain_time)
    
        ret, frame = cap.read()
        if not ret:
            break
        timestamp =cap.get(cv2.CAP_PROP_POS_MSEC)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (width, height),
                                   interpolation=cv2.INTER_LINEAR)
        if frame_queue.empty():
            frame_queue.put(frame_resized, block = False)
        darknet.copy_image_from_bytes(darknet_image, frame_resized.tobytes())
        if darknet_image_queue.empty():
            darknet_image_queue.put(darknet_image, block = False)
        if time_queue.empty():
            time_queue.put(timestamp)

        
    
    cap.release()





def inference(darknet_image_queue, detections_queue, fps_queue, time_queue, time_list,pedestrain_frame):
    while cap.isOpened():
        detect = []
        if (not darknet_image_queue.empty()) and (not time_queue.empty()):
            darknet_image = darknet_image_queue.get(False)
            timestamp = time_queue.get(False)

            prev_time = time.time()
            if (darknet_image is not None) and (timestamp is not None):
                detections = darknet.detect_image(network, class_names, darknet_image, timestamp, thresh=args.thresh)

            """
            for label, confidence, bbox, timestamp in detect_people:
                pedestrain_frame.put(timestamp+clip_t*1000)
                time_list.append(timestamp)
                detect.append((label,confidence,bbox))
            detect_people_queue.put(detect, timeout =4)
            """
            if len(detections):
                for label, confidence, bbox, times in detections:
                    if pedestrain_frame.empty():
                        pedestrain_frame.put(times +clip_t*1000, block = False)
                    time_list.append(times)
                    detect.append((label,confidence,bbox))
            if detections_queue.empty():
                detections_queue.put(detect, block = False)



            fps = int(1/(time.time() - prev_time))
            if fps_queue.empty():
                fps_queue.put(fps,block = False)
            print("FPS: {}".format(fps))
            darknet.print_detections(detections, args.ext_output)
    cap.release()


def drawing(frame_queue, detections_queue, fps_queue):
    random.seed(3)  # deterministic bbox colors
    video = set_saved_video(cap, args.out_filename, (width, height))
    while cap.isOpened():
        if (not frame_queue.empty()) and (not detections_queue.empty()) and (not fps_queue.empty()):
            frame_resized = frame_queue.get(False)
            detections = detections_queue.get(False)
            fps = fps_queue.get(False)
            if frame_resized is not None:
                image = darknet.draw_boxes(detections, frame_resized, class_colors)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                if args.out_filename is not None:
                    video.write(image)
                if not args.dont_show:
                    cv2.imshow('Inference', image)
                if cv2.waitKey(fps) == 27:
                    break
    cap.release()
    video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    frame_queue = Queue()
    darknet_image_queue = Queue(maxsize=1)
    detections_queue = Queue(maxsize=1)
    time_queue = Queue(maxsize=1)   
    fps_queue = Queue(maxsize=1)
    pedestrain_frame = Queue(maxsize=1)
    time_list = []
    threads = []

    args = parser()
    check_arguments_errors(args)
    network, class_names, class_colors = darknet.load_network(
            args.config_file,
            args.data_file,
            args.weights,
            batch_size=1
        )
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    darknet_image = darknet.make_image(width, height, 3)
    input_path = str2int(args.input)
    cap = cv2.VideoCapture(input_path)
    clip_t = args.clip_time  

    threads.append(Thread(target=video_capture, args=(frame_queue, darknet_image_queue,time_queue, pedestrain_frame)))
    threads.append(Thread(target=inference, args=(darknet_image_queue, detections_queue, fps_queue, time_queue, time_list, pedestrain_frame)))
    threads.append(Thread(target=drawing, args=(frame_queue, detections_queue, fps_queue)))
    
    while True:
        for i in threads:
            try:
                i.start()
            except Exception as e:
                print(e)
                break
        for i in threads:
            i.join()
            print(i.name+" has finished!")
        break
    get_clips_time(time_list,clip_t)