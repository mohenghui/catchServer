# !/usr/bin/env python
# coding: utf-8
import random
import Arm_Lib
import cv2 as cv
import numpy as np
import tkinter as tk

class Arm_Calibration:
    def __init__(self):
        # 初始化图像
        self.image = None
        self.threshold_num = 130
        # 机械臂识别位置调节
        self.xy=[90,135]
        # 创建机械臂驱动实例
        self.arm = Arm_Lib.Arm_Device()

    def calibration_map(self, image,xy=None, threshold_num=130):
        '''
        放置方块区域检测函数
        :param image:输入图像
        :return:轮廓区域边点,处理后的图像
        '''
        if xy!=None: self.xy=xy
        # 机械臂初始位置角度
        joints_init = [self.xy[0], self.xy[1], 0, 0, 90, 30]
        # 将机械臂移动到标定方框的状态
        self.arm.Arm_serial_servo_write6_array(joints_init, 1500)
        self.image = image
        self.threshold_num = threshold_num
        # 创建边点容器
        dp = []
        h, w = self.image.shape[:2]
        # 获取轮廓点集(坐标)
        contours = self.Morphological_processing()
        # 遍历点集
        for i, c in enumerate(contours):
            # 计算轮廓区域。
            area = cv.contourArea(c)
            # 设置轮廓区域范围
            if h * w / 2 < area < h * w:
                # 计算多边形的矩
                mm = cv.moments(c)
                if mm['m00'] == 0:
                    continue
                cx = mm['m10'] / mm['m00']
                cy = mm['m01'] / mm['m00']
                # 绘制轮廓区域
                cv.drawContours(self.image, contours, i, (255, 255, 0), 2)
                # 获取轮廓区域边点
                dp = np.squeeze(cv.approxPolyDP(c, 100, True))
                # 绘制中心
                cv.circle(self.image, (np.int(cx), np.int(cy)), 5, (0, 0, 255), -1)
        return dp, self.image

    def Morphological_processing(self):
        '''
        形态学及去噪处理,并获取轮廓点集
        '''
        # 将图像转为灰度图
        gray = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        # 使用高斯滤镜模糊图像。
        gray = cv.GaussianBlur(gray, (5, 5), 1)
        # 图像二值化操作
        ref, threshold = cv.threshold(gray, self.threshold_num, 255, cv.THRESH_BINARY)
        # 获取不同形状的结构元素
        kernel = np.ones((3, 3), np.uint8)
        # 形态学开操作
        blur = cv.morphologyEx(threshold, cv.MORPH_OPEN, kernel, iterations=4)
        # 提取模式
        mode = cv.RETR_EXTERNAL
        # 提取方法
        method = cv.CHAIN_APPROX_NONE
        # 获取轮廓点集(坐标) python2和python3在此处略有不同
        # 层级关系 参数一：输入的二值图，参数二：提取模式，参数三：提取方法。
        contours, hierarchy = cv.findContours(blur, mode, method)
        return contours

    def Perspective_transform(self, dp, image):
        '''
        透视变换
        :param dp: 方框边点(左上,左下,右下,右上)
        :param image: 原始图像
        :return: 透视变换后图像
        '''
        if len(dp)!=4: return image
        upper_left = []
        lower_left = []
        lower_right = []
        upper_right = []
        for i in range(len(dp)):
            if dp[i][0]<320 and dp[i][1]<240:
                upper_left=dp[i]
            if dp[i][0]<320 and dp[i][1]>240:
                lower_left=dp[i]
            if dp[i][0]>320 and dp[i][1]>240:
                lower_right=dp[i]
            if dp[i][0]>320 and dp[i][1]<240:
                upper_right=dp[i]
        # 原图中的四个顶点,与变换矩阵
        pts1 = np.float32([upper_left, lower_left, lower_right, upper_right])
        # 原图中的四个顶点,与变换矩阵
        pts2 = np.float32([[0, 0], [0, 480], [640, 480], [640, 0]])
        # 根据四对对应点计算透视变换。
        M = cv.getPerspectiveTransform(pts1, pts2)
        # 将透视变换应用于图像。
        Transform_img = cv.warpPerspective(image, M, (640, 480))
        return Transform_img



class update_hsv:
    def __init__(self):
        '''
        初始化一些参数
        '''
        self.image = None
        self.binary = None

    def Image_Processing(self, hsv_range):
        '''
        形态学变换去出细小的干扰因素
        :param img: 输入初始图像
        :return: 检测的轮廓点集(坐标)
        '''
        (lowerb, upperb) = hsv_range
        # 复制原始图像,避免处理过程中干扰
        color_mask = self.image.copy()
        # 将图像转换为HSV。
        hsv_img = cv.cvtColor(self.image, cv.COLOR_BGR2HSV)
        # 筛选出位于两个数组之间的元素。
        color = cv.inRange(hsv_img, lowerb, upperb)
        # 设置非掩码检测部分全为黑色
        color_mask[color == 0] = [0, 0, 0]
        # 将图像转为灰度图
        gray_img = cv.cvtColor(color_mask, cv.COLOR_RGB2GRAY)
        # 获取不同形状的结构元素
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5, 5))
        # 形态学闭操作
        dst_img = cv.morphologyEx(gray_img, cv.MORPH_CLOSE, kernel)
        # 图像二值化操作
        ret, binary = cv.threshold(dst_img, 10, 255, cv.THRESH_BINARY)
        # 获取轮廓点集(坐标) python2和python3在此处略有不同
        # _, contours, heriachy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE) #python2
        contours, heriachy = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)  # python3
        return contours, binary

    def draw_contours(self, hsv_name, contours):
        '''
        绘制轮廓
        '''
        for i, cnt in enumerate(contours):
            # 计算多边形的矩
            mm = cv.moments(cnt)
            if mm['m00'] == 0:
                continue
            cx = mm['m10'] / mm['m00']
            cy = mm['m01'] / mm['m00']
            # 计算轮廓的⾯积
            area = cv.contourArea(cnt)
            # ⾯积⼤于800
            if area > 800:
                # 获取多边形的中心
                (x, y) = (np.int(cx), np.int(cy))
                # 绘制中⼼
                cv.circle(self.image, (x, y), 5, (0, 0, 255), -1)
                # 计算最小矩形区域
                rect = cv.minAreaRect(cnt)
                # 获取盒⼦顶点
                box = cv.boxPoints(rect)
                # 转成long类型
                box = np.int0(box)
                # 绘制最小矩形
                cv.drawContours(self.image, [box], 0, (255, 0, 0), 2)
                cv.putText(self.image, hsv_name, (int(x - 15), int(y - 15)),
                           cv.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

    def get_contours(self, img, color_name, hsv_msg, color_hsv):
        binary = None
        # 规范输入图像大小
        self.image = cv.resize(img, (640, 480), )
        for key, value in color_hsv.items():
            # 检测轮廓点集
            if color_name == key:
                color_contours, binary = self.Image_Processing(hsv_msg)
            else:
                color_contours, _ = self.Image_Processing(color_hsv[key])
            # 绘制检测图像,并控制跟随
            self.draw_contours(key, color_contours)
        return self.image, binary


def write_HSV(wf_path, dict):
    with open(wf_path, "w") as wf:
        for key, value in dict.items():
            wf_str = '"' + key + '": [' + str(value[0][0]) + ', ' + str(
                value[0][1]) + ', ' + str(value[0][2]) + ', ' + str(
                value[1][0]) + ', ' + str(value[1][1]) + ', ' + str(
                value[1][2]) + '], ' + '\n'
            wf.write(wf_str)
        wf.flush()


def read_HSV(rf_path, dict):
    rf = open(rf_path, "r+")
    for line in rf.readlines():
        list = []
        name = None
        aa = line.find('"')
        bb = line.rfind('"')
        cc = line.find('[')
        dd = line.rfind(']')
        if aa >= 0 and bb >= 0: name = line[aa + 1:bb]
        if cc >= 0 and dd >= 0:
            rf_str = line[cc + 1:dd].split(',')
            for index, i in enumerate(rf_str): list.append(int(i))
            if name != None: dict[name] = ((list[0], list[1], list[2]), (list[3], list[4], list[5]))
    rf.flush()


def write_XYT(wf_path, xy, thresh):
    with open(wf_path, "w") as wf:
        str1 = 'x' + '=' + str(xy[0])
        str2 = 'y' + '=' + str(xy[1])
        str3 = 'thresh' + '=' + str(thresh)
        wf_str = str1 + '\n' + str2 + '\n' + str3
        wf.write(wf_str)
        wf.flush()


def read_XYT(rf_path):
    dict = {}
    rf = open(rf_path, "r+")
    for line in rf.readlines():
        index = line.find('=')
        dict[line[:index]] = line[index + 1:]
    xy = [int(dict['x']), int(dict['y'])]
    thresh = int(dict['thresh'])
    rf.flush()
    return xy, thresh


def write_PIDT(wf_path, PID, time_config):
    with open(wf_path, "w") as wf:
        str1 = 'P' + '=' + str(PID[0])
        str2 = 'I' + '=' + str(PID[1])
        str3 = 'D' + '=' + str(PID[2])
        str4 = 'T1' + '=' + str(time_config[1])
        str5 = 'T2' + '=' + str(time_config[1])
        str6 = 'T3' + '=' + str(time_config[2])
        wf_str = str1 + '\n' + str2 + '\n' + str3 + '\n' + str4 + '\n' + str5 + '\n' + str6
        wf.write(wf_str)
        wf.flush()


def read_PIDT(rf_path):
    dict = {}
    rf = open(rf_path, "r+")
    for line in rf.readlines():
        index = line.find('=')
        dict[line[:index]] = line[index + 1:]
    PID = [int(dict['P']), int(dict['I']), int(dict['D'])]
    time_config = [int(dict['T1']), int(dict['T2']), int(dict['T3'])]
    rf.flush()
    return PID, time_config