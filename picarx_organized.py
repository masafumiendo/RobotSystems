"""
Authors: Masafumi Endo
Date: 04/10/2021
Content: class of picarx_improved.py (2.9)
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

class PicarX:
    # initialization
    def __init__(self, servo=Servo, pwm=PWM, pin=Pin, adc=ADC):

        self.Servo = servo
        self.PWM = pwm
        self.Pin = pin
        self.ADC = adc

        self.PERIOD = 4095
        self.PRESCALER = 10
        self.TIMEOUT = 0.02

        self.dir_servo_pin = self.Servo(self.PWM('P2'))
        self.camera_servo_pin1 = self.Servo(self.PWM('P0'))
        self.camera_servo_pin2 = self.Servo(self.PWM('P1'))
        self.left_rear_pwm_pin = self.PWM("P13")
        self.right_rear_pwm_pin = self.PWM("P12")
        self.left_rear_dir_pin = self.Pin("D4")
        self.right_rear_dir_pin = self.Pin("D5")

        self.S0 = self.ADC('A0')
        self.S1 = self.ADC('A1')
        self.S2 = self.ADC('A2')

        self.Servo_dir_flag = 1
        self.dir_cal_value = 0
        self.cam_cal_value_1 = 0
        self.cam_cal_value_2 = 0
        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]
        self.cali_dir_value = [1, -1]
        self.cali_speed_value = [0, 0]

        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)

        atexit.register(self.cleanup)

    ### begin 2.9.3
    def cleanup(self):
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)
    ### end 2.9.3

    def set_motor_speed(self, motor, speed):

        motor -= 1
        if speed >= 0:
            direction = 1 * self.cali_dir_value[motor]
        elif speed < 0:
            direction = -1 * self.cali_dir_value[motor]
        speed = abs(speed)
        ### begin 2.7.2
        # if speed != 0:
        #     speed = int(speed /2 ) + 50
        # speed = speed - cali_speed_value[motor]
        ### end 2.7.2
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    def motor_speed_calibration(self, value):

        self.cali_speed_value = value
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(self.cali_speed_value)
        else:
            self.cali_speed_value[0] = abs(self.cali_speed_value)
            self.cali_speed_value[1] = 0

    def motor_direction_calibration(self, motor, value):
        # 0: positive direction
        # 1:negative direction

        motor -= 1
        if value == 1:
            self.cali_dir_value[motor] = -1*self.cali_dir_value[motor]

    def dir_servo_angle_calibration(self, value):

        self.dir_cal_value = value
        self.set_dir_servo_angle(self.dir_cal_value)
        # dir_servo_pin.angle(dir_cal_value)

    def set_dir_servo_angle(self, value):

        self.dir_servo_pin.angle(value+self.dir_cal_value)

    def camera_servo1_angle_calibration(self, value):

        self.cam_cal_value_1 = value
        self.set_camera_servo1_angle(self.cam_cal_value_1)
        # camera_servo_pin1.angle(cam_cal_value)

    def camera_servo2_angle_calibration(self, value):

        self.cam_cal_value_2 = value
        self.set_camera_servo2_angle(self.cam_cal_value_2)
        # camera_servo_pin2.angle(cam_cal_value)

    def set_camera_servo1_angle(self, value):

        self.camera_servo_pin1.angle(-1 *(value+self.cam_cal_value_1))

    def set_camera_servo2_angle(self, value):

        self.camera_servo_pin2.angle(-1 * (value+self.cam_cal_value_2))

    def get_adc_value(self):
        adc_value_list = []
        adc_value_list.append(self.S0.read())
        adc_value_list.append(self.S1.read())
        adc_value_list.append(self.S2.read())
        return adc_value_list

    def set_power(self, speed):
        self.set_motor_speed(1, speed)
        self.set_motor_speed(2, speed)

    def backward(self, speed):
        self.set_motor_speed(1, speed)
        self.set_motor_speed(2, speed)

    ### begin 2.7.3
    def forward(self, speed, steer_angle):
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
        self.set_dir_servo_angle(steer_angle)
        # command speed w/ speed ratios
        self.set_motor_speed(1, -1 * l_speed_ratio * speed)
        self.set_motor_speed(2, -1 * r_speed_ratio * speed)
    ### end 2.7.3

    def stop(self):
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)


    def Get_distance(self):
        timeout=0.01
        trig = self.Pin('D8')
        echo = self.Pin('D9')

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
    def basic_maneuvering(self, speed, steer_angle, time2drive):
        self.set_dir_servo_angle(0)
        self.forward(speed, steer_angle)
        time.sleep(time2drive)
        self.stop()

    def parallel_parking(self, direction, speed=60, steer_angle=30):

        # set direction
        if direction == 'left':
            steer_dir = -1
        elif direction == 'right':
            steer_dir = 1
        speed = -1 * speed

        time2drive = 1
        self.basic_maneuvering(speed, 0, time2drive)
        self.basic_maneuvering(speed, steer_dir * steer_angle, time2drive)
        self.basic_maneuvering(speed, -1 * steer_dir * steer_angle, time2drive)
        self.basic_maneuvering(speed, 0, time2drive)

    def three_point_turning(self, direction, speed=60, steer_angle=30):
        # set direction
        if direction == 'left':
            steer_dir = -1
        elif direction == 'right':
            steer_dir = 1

        time2drive = 1
        self.basic_maneuvering(speed, steer_dir * steer_angle, time2drive)
        self.basic_maneuvering(speed, -1 * steer_dir * steer_angle, time2drive)
        self.basic_maneuvering(speed, steer_dir * steer_angle, time2drive)

    ### end 2.8.1

    ### begin 2.8.2
    def interface2drive(self):
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
                self.basic_maneuvering(speed * direction, steer_angle, time2drive)
            elif command == 'e':
                print('parallel parking w/ left turn')
                self.parallel_parking('left')
            elif command == 'f':
                print('parallel parking w/ right turn')
                self.parallel_parking('right')
            elif command == 'g':
                print('k-turning w/ left turn')
                self.three_point_turning('left')
            elif command == 'h':
                print('k-turning w/ right turn')
                self.three_point_turning('right')
            else:
                print('end driving')
                break
    ### end 2.8.2