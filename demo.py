import Arm_Lib
import cv2 as cv
import threading
from time import sleep
from dofbot_config import *
import ipywidgets as widgets
from IPython.display import display
from garbage_identify import garbage_identify
from server import  Server
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
        msg=target.get_pos_new(myserver.centerx,myserver.centery)

        # msg['Green'] = (-0.20, 0.254)
        target.garbage_grap(msg,xy)
        myserver.centerx=None
        myserver.centery=None

