"""
Authors: Masafumi Endo
Date: 04/10/2021
Content: improved version of picarx.py
"""

### begin 2.5.3
try:
    from ezblock import *
    from ezblock import __reset_mcu__
    __reset_mcu__()
    time.sleep(0.01)
except ImportError:
    print("This computer does not appear to be a PiCar-X system(/opt/ezblock is not present). Shadowing hardware calls with substitute functions")
    from sim_ezblock import *
### end 2.5.3

### begin 2.6
import logging
# from logdecorator import log_on_start , log_on_end , log_on_error

logging_format = "%(asctime)s:%(message)s"
logging.basicConfig(format=logging_format, level = logging.INFO, datefmt ="% H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)
### end 2.6

### begin 2.7.1
import atexit
### end 2.7.1

import time

PERIOD = 4095
PRESCALER = 10
TIMEOUT = 0.02

dir_servo_pin = Servo(PWM('P2'))
camera_servo_pin1 = Servo(PWM('P0'))
camera_servo_pin2 = Servo(PWM('P1'))
left_rear_pwm_pin = PWM("P13")
right_rear_pwm_pin = PWM("P12")
left_rear_dir_pin = Pin("D4")
right_rear_dir_pin = Pin("D5")

S0 = ADC('A0')
S1 = ADC('A1')
S2 = ADC('A2')

Servo_dir_flag = 1
dir_cal_value = 0
cam_cal_value_1 = 0
cam_cal_value_2 = 0
motor_direction_pins = [left_rear_dir_pin, right_rear_dir_pin]
motor_speed_pins = [left_rear_pwm_pin, right_rear_pwm_pin]
cali_dir_value = [1, -1]
cali_speed_value = [0, 0]
#初始化PWM引脚
for pin in motor_speed_pins:
    pin.period(PERIOD)
    pin.prescaler(PRESCALER)

def set_motor_speed(motor, speed):
    global cali_speed_value,cali_dir_value
    motor -= 1
    if speed >= 0:
        direction = 1 * cali_dir_value[motor]
    elif speed < 0:
        direction = -1 * cali_dir_value[motor]
    speed = abs(speed)
    ### begin 2.7.2
    # if speed != 0:
    #     speed = int(speed /2 ) + 50
    # speed = speed - cali_speed_value[motor]
    ### end 2.7.2
    if direction < 0:
        motor_direction_pins[motor].high()
        motor_speed_pins[motor].pulse_width_percent(speed)
    else:
        motor_direction_pins[motor].low()
        motor_speed_pins[motor].pulse_width_percent(speed)

def motor_speed_calibration(value):
    global cali_speed_value,cali_dir_value
    cali_speed_value = value
    if value < 0:
        cali_speed_value[0] = 0
        cali_speed_value[1] = abs(cali_speed_value)
    else:
        cali_speed_value[0] = abs(cali_speed_value)
        cali_speed_value[1] = 0

def motor_direction_calibration(motor, value):
    # 0: positive direction
    # 1:negative direction
    global cali_dir_value
    motor -= 1
    if value == 1:
        cali_dir_value[motor] = -1*cali_dir_value[motor]


def dir_servo_angle_calibration(value):
    global dir_cal_value
    dir_cal_value = value
    set_dir_servo_angle(dir_cal_value)
    # dir_servo_pin.angle(dir_cal_value)

def set_dir_servo_angle(value):
    global dir_cal_value
    dir_servo_pin.angle(value+dir_cal_value)

def camera_servo1_angle_calibration(value):
    global cam_cal_value_1
    cam_cal_value_1 = value
    set_camera_servo1_angle(cam_cal_value_1)
    # camera_servo_pin1.angle(cam_cal_value)

def camera_servo2_angle_calibration(value):
    global cam_cal_value_2
    cam_cal_value_2 = value
    set_camera_servo2_angle(cam_cal_value_2)
    # camera_servo_pin2.angle(cam_cal_value)

def set_camera_servo1_angle(value):
    global cam_cal_value_1
    camera_servo_pin1.angle(-1 *(value+cam_cal_value_1))

def set_camera_servo2_angle(value):
    global cam_cal_value_2
    camera_servo_pin2.angle(-1 * (value+cam_cal_value_2))

def get_adc_value():
    adc_value_list = []
    adc_value_list.append(S0.read())
    adc_value_list.append(S1.read())
    adc_value_list.append(S2.read())
    return adc_value_list

def set_power(speed):
    set_motor_speed(1, speed)
    set_motor_speed(2, speed)

def backward(speed):
    set_motor_speed(1, speed)
    set_motor_speed(2, speed)

### begin 2.7.3
def forward(speed, steer_angle):
    """
    method to move forward w/ given steering angle
    """
    # set vertical and horizontal length of differences (measured value)
    length_vert = 9.5 # (cm)
    length_horz = 12 # (cm)

    l_speed_ratio = 1
    r_speed_ratio = 1

    if steer_angle != 0:
        theta = steer_angle * math.pi / 180.
        r = length_vert / math.cos(abs(theta))
        speed_ratio = r / (r + length_horz)
        if theta > 0:
            # update right speed ratio
            r_speed_ratio = speed_ratio
        elif theta < 0:
            # update left speed ratio
            l_speed_ratio = speed_ratio

    # adjust servo angle
    set_dir_servo_angle(steer_angle)
    # command speed w/ speed ratios
    print('left speed ratio: {}, right speed ratio: {}'.format(l_speed_ratio, r_speed_ratio))
    set_motor_speed(1, -1 * l_speed_ratio * speed)
    set_motor_speed(2, -1 * r_speed_ratio * speed)
### end 2.7.3

def stop():
    set_motor_speed(1, 0)
    set_motor_speed(2, 0)


def Get_distance():
    timeout=0.01
    trig = Pin('D8')
    echo = Pin('D9')

    trig.low()
    time.sleep(0.01)
    trig.high()
    time.sleep(0.000015)
    trig.low()
    pulse_end = 0
    pulse_start = 0
    timeout_start = time.time()
    while echo.value()==0:
        pulse_start = time.time()
        if pulse_start - timeout_start > timeout:
            return -1
    while echo.value()==1:
        pulse_end = time.time()
        if pulse_end - timeout_start > timeout:
            return -2
    during = pulse_end - pulse_start
    cm = round(during * 340 / 2 * 100, 2)
    #print(cm)
    return cm

### begin 2.8.1
def basic_maneuvering(speed, steer_angle, time2drive):
    forward(0, 0)
    time.sleep(0.01)
    forward(speed, steer_angle)
    time.sleep(time2drive)
    stop()

def parallel_parking(direction, speed=60, steer_angle=30):

    # set direction
    if direction == 'left':
        steer_dir = -1
    elif direction == 'right':
        steer_dir = 1
    speed = -1 * speed

    time2drive = 1
    basic_maneuvering(speed, 0, time2drive)
    basic_maneuvering(speed, steer_dir * steer_angle, time2drive)
    basic_maneuvering(speed, -1 * steer_dir * steer_angle, time2drive)
    basic_maneuvering(speed, 0, time2drive)

def three_point_turning(direction, speed=60, steer_angle=30):
    # set direction
    if direction == 'left':
        steer_dir = -1
    elif direction == 'right':
        steer_dir = 1

    time2drive = 1
    basic_maneuvering(speed, steer_dir * steer_angle, time2drive)
    basic_maneuvering(speed, -1 * steer_dir * steer_angle, time2drive)
    basic_maneuvering(speed, steer_dir * steer_angle, time2drive)

### end 2.8.1

### begin 2.8.2
def interface2drive():
    while True:
        print('This is a interface to drive your PiCar w/ various types of maneuvering. Below is list of commands...')
        print(' a -- go forward \n'
              ' b -- go backward \n'
              ' c -- go left \n'
              ' d -- go right \n'
              ' e -- parallel parking w/ left turn \n'
              ' f -- parallel parking w/ right turn \n'
              ' g -- k-turning w/ left turn \n'
              ' h -- k-turning w/ right turn')
        print('If you input other keys, this process will be stopped. Enjoy your drive!')
        command = input('input your desired maneuvering: ')

        if command == 'a' or command == 'b' or command == 'c' or command == 'd':
            time2drive = input('input your desired time to drive: ')
            time2drive = float(time2drive)
            speed = 60
            steer_angle = 0
            direction = 1
            if command == 'a':
                print('go forward')
            elif command == 'b':
                print('go backward')
                direction = -1
            elif command == 'c':
                steer_angle = -30
                print('go left')
            elif command == 'd':
                steer_angle = 30
                print('go right')
            basic_maneuvering(speed * direction, steer_angle, time2drive)
        elif command == 'e':
            print('parallel parking w/ left turn')
            parallel_parking('left')
        elif command == 'f':
            print('parallel parking w/ right turn')
            parallel_parking('right')
        elif command == 'g':
            print('k-turning w/ left turn')
            three_point_turning('left')
        elif command == 'h':
            print('k-turning w/ right turn')
            three_point_turning('right')
        else:
            print('end driving')
            break
### end 2.8.2
