import Arm_Lib
import cv2 as cv
import threading
from time import sleep
from dofbot_config import *
import ipywidgets as widgets
from IPython.display import display
from garbage_identify import garbage_identify
from server import  Server
import sys
# 创建获取目标实例
target = garbage_identify()
# 创建相机标定实例
calibration = Arm_Calibration()
# 创建机械臂驱动实例
arm = Arm_Lib.Arm_Device()
# 初始化一些参数
num=0
# 初始化标定方框边点
dp = []
# 初始化抓取信息
msg = {}
# 初始化1,2舵机角度值
xy = [120, 135]
# 初始化二值图阈值
threshold = 140
# 初始化模式
model = "General"
# XYT参数路径
# XYT_path="/home/jetson/dofbot_ws/src/dofbot_garbage_yolov5/XYT_config.txt"
# try: xy, thresh = read_XYT(XYT_path)
# except Exception: print("Read XYT_config Error !!!")

import Arm_Lib
arm = Arm_Lib.Arm_Device()
myserver=Server()
t1=threading.Thread(target=myserver.SingleReceiveText)
t1.start()
joints_0 = [xy[0], xy[1], 0, 0, 90, 30]
arm.Arm_serial_servo_write6_array(joints_0, 1000)
while True:
    if myserver.centerx and myserver.centery:
        x,y=myserver.centerx,myserver.centery
        if x<320:
            tmpx=x+(480-y)*0.416
        elif x==320:
            tmpx=x
        else:
            tmpx=x+(y-480)*0.416
        msg=target.get_pos_new1(x,tmpx,y)
        if y!=480 and x>320:
            x=640-(tmpx+(640-x)*(0.625/2))
        elif x==320 or y==480:
            x=640-tmpx
        else:
            x=640-(tmpx-(x)*0.312)
        skip_x=5.33
        x_angle=x/skip_x+60
        # x_angle=240-x_angle
        print(x_angle)

        if x_angle>180:
            x_angle=180
        if x_angle<120:
            joints_x = x_angle*0.857
        elif x_angle<90:
            print("no")
            sys.exit(0)
        else:
            joints_x = x_angle
        # msg['Green'] = (-0.20, 0.254)
        target.garbage_grap_new(joints_x,40,msg,xy)
        myserver.centerx=None
        myserver.centery=None

