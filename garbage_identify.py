#!/usr/bin/env python3
# coding: utf-8
import time
import torch
import rospy
import Arm_Lib
import cv2 as cv
import numpy as np
from time import sleep
from numpy import random
from garbage_grap import garbage_grap_move
from dofbot_info.srv import kinemarics, kinemaricsRequest, kinemaricsResponse




class garbage_identify:
    def __init__(self):
        # 初始化图像
        self.frame = None
        # 创建机械臂实例
        self.arm = Arm_Lib.Arm_Device()
        # 机械臂识别位置调节
        self.xy = [90, 130]
        self.garbage_index=0
        # 创建垃圾识别抓取实例
        self.grap_move = garbage_grap_move()
        # 创建节点句柄
        self.n = rospy.init_node('dofbot_garbage', anonymous=True)
        # 创建用于调用的ROS服务的句柄。
        self.client = rospy.ServiceProxy("dofbot_kinemarics", kinemarics)
        self.lowerGreen = np.array([60,120,10])
        self.upperGreen = np.array([90,145,240])

    def garbage_grap(self, msg, xy=None):
        '''
        执行抓取函数
        :param msg: {name:pos,...}
        '''
        if xy != None: self.xy = xy
        print("init")
        if len(msg)!=0:
            self.arm.Arm_Buzzer_On(1)
            sleep(0.5)
        print("init out")
        for index, name in enumerate(msg):
            try:
                # 此处ROS反解通讯,获取各关节旋转角度
                joints = self.server_joint(msg[name])
                # 调取移动函数
                print("move")
                self.grap_move.arm_run(str(name), joints)
            except Exception:
                print("sqaure_pos empty")
        # 初始位置
        joints_0 = [self.xy[0], self.xy[1], 0, 0, 90, 30]
        # 移动至初始位置
        # self.arm.Arm_serial_servo_write6_array(joints_0, 1000)
        # sleep(0.25)
    def garbage_grap_new(self, newx,newhead,msg, xy=None):
        '''
        执行抓取函数
        :param msg: {name:pos,...}
        '''
        if xy != None: self.xy = xy
        print("init")
        if len(msg)!=0:
            self.arm.Arm_Buzzer_On(1)
            sleep(0.5)
        print("init out")
        for index, name in enumerate(msg):
            try:
                # 此处ROS反解通讯,获取各关节旋转角度
                joints = self.server_joint(msg[name])
                joints[0]=newx
                joints[3]-=newhead
#                 print(joints)
                # 调取移动函数
                print("move")
                self.grap_move.arm_run(str(name), joints)
            except Exception:
                print("sqaure_pos empty")
        # 初始位置
        # joints_0 = [self.xy[0], self.xy[1], 0, 0, 90, 30]
        # 移动至初始位置
        # self.arm.Arm_serial_servo_write6_array(joints_0, 1000)
        # sleep(0.25)
    def garbage_run(self, image):
        '''
        执行垃圾识别函数
        :param image: 原始图像
        :return: 识别后的图像,识别信息(name, msg)
        '''
        # 规范输入图像大小
        self.frame = cv.resize(image, (640, 480))
        # txt0 = 'Model-Loading...'
        msg={}
        # if self.garbage_index<3:
        #     cv.putText(self.frame, txt0, (190, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        #     self.garbage_index+=1
        #     return self.frame,msg 
        # if self.garbage_index>=3:
            # 创建消息容器
        try: msg = self.get_pos() # 获取识别消息
        except Exception: print("get_pos NoneType")
        print(msg)
        return self.frame, msg

    def get_pos(self):
        '''
        获取识别信息
        :return: 名称,位置
        '''
        # 复制原始图像,避免处理过程中干扰
        frame = self.frame.copy()
        msg = {}
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        mask = cv.inRange(hsv, self.lowerGreen, self.upperGreen)
        mask = cv.dilate(mask, None, iterations=2)
        # mask = cv2.erode(mask, None, iterations=2)
        mask = cv.dilate(mask, None, iterations=2)
        res = cv.bitwise_and(frame, frame, mask=mask)
        contours, hierarchy = cv.findContours(mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        for c in contours:
            (x, y), radius = cv.minEnclosingCircle(c)
            if radius > 100:
                cv.circle(frame, (int(x), int(y)), int(radius), (153,153,0),2)
                cv.circle(frame, (int(x), int(y)), 2, (127,0,255),2)
            point_x,point_y=int(x),int(y)

        # 反转或排列数组的轴；返回修改后的数组。
        (a, b) = (round(((point_x - 320) / 4000), 5), round(((480 - point_y) / 3000) * 0.8+0.19, 5))
        msg['Green'] = (a, b)
        return msg
    def get_pos_new(self,point_x,point_y):
        msg = {}
        # if point_x<320:
        #     a = round(((point_x - 320) / 450), 5)
        # elif point_x==320:
        #     a = round(((point_x - 320) -0.13), 5)
        # else:
        #     a=round(((point_x - 320) / 5000), 5)
        # #900
        # if :
        # if b>240:
        # if point_y==240:
        #     b = round(((480 - point_y) / 8000) * 0.88+0.06, 5)
        # else:
        #0.1-0.2
        # a=0.1
        # b = round(((480 - point_y) / 4000) * 0.88+0.08, 5)
        (a, b) = (round(((point_x - 320) / 1500), 5), round(((480 - point_y) / 4000) * 0.8+0.08, 5))
        # print(a,b)
        msg['Green'] = (a, b)
        return msg
    def get_pos_new1(self,og_x,point_x,point_y):
        msg = {}
        # if point_x<320:
        #     a = round(((point_x - 320) / 450), 5)
        # elif point_x==320:
        #     a = round(((point_x - 320) -0.13), 5)
        # else:
        #     a=round(((point_x - 320) / 5000), 5)
        # #900
        # if :
        # if b>240:
        # if point_y==240:
        #     b = round(((480 - point_y) / 8000) * 0.88+0.06, 5)
        # else:
        #0.1-0.2
        # print(point_x)
        # a=0.1+point_x*0.0005
        if point_x>og_x:
            a=-0.1-((point_x-og_x)*0.0005)
        elif point_x==og_x and point_x==320:
            # a=-0.1-((480-point_y)*0.000208)
            a=-0.0-((480-point_y)*0.000416)
        else:
            a=-0.1-((og_x-point_x)*0.0005)
        b = round(((480 - point_y) / 4000) * 0.88+0.08, 5)
        print(a,b)
        msg['Green'] = (a, b)
        return msg
    def server_joint(self, posxy):
        '''
        发布位置请求,获取关节旋转角度
        :param posxy: 位置点x,y坐标
        :return: 每个关节旋转角度
        '''
        # 等待server端启动
        self.client.wait_for_service()
        # 创建消息包
        request = kinemaricsRequest()
        request.tar_x = posxy[0]
        request.tar_y = posxy[1]
        request.kin_name = "ik"
        try:
            response = self.client.call(request)
            if isinstance(response, kinemaricsResponse):
                # 获取反解的响应结果
                joints = [0, 0, 0, 0, 0]
                joints[0] = response.joint1
                joints[1] = response.joint2
                joints[2] = response.joint3
                joints[3] = response.joint4
                joints[4] = response.joint5
                print(joints)
                # 角度调整
                if joints[2] < 0:
                    joints[1] += joints[2] / 2
                    joints[3] += joints[2] * 3 / 4
                    joints[2] = 0
                # print joints
                return joints
        except Exception:
            rospy.loginfo("arg error")
