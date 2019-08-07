import pigpio
import time
import RPi.GPIO as GPIO
import numpy as np

def angle_to_duty(angle):
    duty = float(angle)/180.*(2500-600) + 600
    return duty

def rotate(p, pin, a, mode='constant_time', speed=5):

    duty_final = angle_to_duty(float(a))
    duty_init = p.get_servo_pulsewidth(pin)

    if mode in ['constant_speed']:
      drange = np.linspace(duty_init, duty_final, np.abs(duty_final-duty_init)/speed)
    elif mode in ['constant_time']:
      drange = np.linspace(duty_init, duty_final, 2500/speed)

    print(drange)
    for d in drange:
      print(d)
      p.set_servo_pulsewidth(pin, d)
      time.sleep(0.01)

servoPIN_1 = 17
p1 = pigpio.pi()
p1.set_mode(servoPIN_1, pigpio.OUTPUT) # Initialization
p1.set_servo_pulsewidth(servoPIN_1, 600)
p1.set_PWM_frequency(17,50)

try:
  while True:
    a = input("Angle (0-180): ")
    while float(a)>180 or float(a)<0:
      a = input("Angle (0-180): ")
    rotate(p1, servoPIN_1, a, mode='constant_time', speed=20)

except KeyboardInterrupt:
  p1.stop()

