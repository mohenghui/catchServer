import Arm_Lib
arm = Arm_Lib.Arm_Device()
import sys
#50<=120<=180
#70,60
x=300
x=640-x
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
# print(joints_x)
joints_0 = [joints_x, 90, 0, 0, 265, 30]
arm.Arm_serial_servo_write6_array(joints_0, 500)