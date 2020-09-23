#coding:utf-8
import sys
import os
import re
import shutil
import subprocess
import argparse
from datetime import datetime, timedelta

TIME_FROMAT = '%H:%M:%S'

def args():
    args = argparse.ArgumentParser(description="Args for video clips editor")
    args.add_argument("--inputfolder", type=str, default="")
    args.add_argument("--outputfolder", type=str, default="")
    args.add_argument("--duration",type=str,default="00:02:00")
    args.add_argument("--start_time_txt", type=str,default="./timestamp.txt")
    return args.parse_args()

def check_arguments_errors(args):
    if not os.path.exists(args.inputfolder):
       raise(ValueError("Invalid input path {}".format(os.path.abspath(args.inputfolder)))) 
    if not os.path.exists(args.outputfolder):
        raise(ValueError("Invalid output path {}".format(os.path.abspath(args.outputfolder))))
    if not os.path.exists(args.start_time_txt):
        raise(ValueError("Invalid start_time_txt path {}".format(os.path.abspath(args.start_time_txt))))

def do_cut(file_input, file_output, s1_time, duration):
    cmd = 'ffmpeg -fflags +genpts -accurate_seek -i '+ file_input+ ' -ss '+s1_time+' -t '+str(duration)+' -codec copy '+file_output
    print ("cmd=", cmd)
    subprocess.call(cmd, shell=True)

def do_edit(file_input, file_output,duration,lines):
    if os.path.exists(file_output):
        shutil.rmtree(file_output)
    os.mkdir(file_output)
    (filepath, tempfilename) = os.path.split(file_input)
    (filename, extension) = os.path.splitext(tempfilename)
    for i in range(0, len(lines)):
        output = file_output + '/' + filename + "_" + (timelist(lines[i])) + extension
        do_cut(file_input, output, lines[i],duration)

def readfile(filepath):
    l = []
    file = open(filepath,"r")
    lines = file.readlines()
    for i in lines:
        l.append(i.strip('\n'))
    file.close()
    return l

def timelist(time):
    new_time = time.replace(":","")
    return new_time

if __name__ == "__main__":
    lines =[]
    args = args()
    check_arguments_errors(args)
    file_input = args.inputfolder
    file_output = args.outputfolder
    duration = args.duration
    timefile = args.start_time_txt

    lines = readfile(timefile)
    if len(lines):
        do_edit(file_input, file_output,duration,lines)
    else:
        print ("No pedestrains detected!")