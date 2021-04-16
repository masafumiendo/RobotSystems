# RobotSystems

## Motor commands

### sim_ezblock.py
It is used for simulate ezblock library in my computer. Following classes are simulated:

* _Basic_class
* Pin
* I2C
* ADC
* PWM
* Servo

This follows instructions from 2.5.4 to 2.5.5.

### picarx_improved.py
This implements improved version of picarx.py. The method named **forward** is modified to enable steering. 
The methods named **basic_maneuvering**, **parallel_parking**, and **three_point_turning** are used for maneuvering the car.
The method named **interface2drive** implements simple user-interface.

### picarx_organized.py
The class version of picarx_improved.py.

### main
The folder named **main** contains all the necessary files to drive the car. I basically run the code inside this folder.

## Sensors and Control

### sensing.py
The class for sensing using ground-scanning photo-sensors attached to the ADC pins.

### interpretation.py
TBC

### controller.py
TBC