import os
import argparse

PYTHON = 'python'

if __name__ == '__main__':
    #args
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type = str, default='',
                        help = 'Path of the videos folder')
    parser.add_argument('--save_path', type = str, default='',
                        help = 'Path of the Output folder')
    args = parser.parse_args()

    #args error checking
    if not os.path.exists(args.data_path):
        raise(ValueError("Invalid input videos folder path {}".format(os.path.abspath(args.data_path))))
    if not os.path.exists(args.save_path):
        raise(ValueError("Invalid output videos folder path {}".format(os.path.abspath(args.save_path))))

    data_path = args.data_path
    save_path = args.save_path
    path_list = []
    save_list = []

    #get each input video's path and put in a list
    filename_list = os.listdir(data_path)
    if len(filename_list):
        i = 0
        for i in range(0,len(filename_list)):
            path = os.path.join(data_path, filename_list[i] )
            path_list.append(path)
            (filename, extension) = os.path.splitext(filename_list[i])
            set_save_path = os.path.join(save_path, filename)
            save_list.append(set_save_path)
            if not os.path.exists(set_save_path):
                os.makedirs(set_save_path)
    else:
        print("No videos found in the folder!")
    
    for i in range(0,len(filename_list)):
        cmd1 = PYTHON +" ./detect.py --input " + path_list[i]
        cmd2 = PYTHON +" ./video_edit.py --inputfolder "+path_list[i]+" --outputfolder "+save_list[i]
        os.system(cmd1)
        os.system(cmd2)