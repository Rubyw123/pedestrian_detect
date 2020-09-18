# Pedestrians Detection Based on Yolo v4

Before started, make sure that you have yolo v4 compiled properly on your machine

### Requirements

* Darknet (See following steps)
* ffmpeg (`sudo apt install -y ffmpeg`)

#### How to install Yolo v4
1. Make sure you have CUDA (>= 10.0), cudDNN (>= 7.0) and OpenCV (>= 2.4) installed properly.
2. Clone the following repository to local: [darknet](https://github.com/AlexeyAB/darknet/edit/master/README.md)
3. Modify the Makefile to make following changes:
  * `GPU=1`
  * `CUDNN=1`
  * `OPENCV=1`
  * `LIBSO=1`
4. Do `make` in the darknet directory.

If no errors popped up, then darknet has been compiled successfully. If you see error messages, please review the
README file in the darknet repository.

#### How to use the pedestrians detection
1. Clone this repository to local.
2. Copy four python files to the darknet directory, remember to replace the orginal darkne.py file.
3. Creat an input folder and an output folder
4. Do `python runAll.py --data_path <your input folder path> --save_path <your output folder path>` in the darknet
  directory.

If `python` is not pointing to a python (>=3.0), you may get `ImportError: No module named 'queue'`. Modify runAll.py
and change `PYTHON = python` to `PYTHON = python3`

