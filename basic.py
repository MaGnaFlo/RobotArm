import RPi.GPIO as GPIO
import time
import numpy as np

def angle_to_duty(angle):
    duty = float(angle)/180.*(11.6-2.5) + 2.5
    return duty

def rotate(p, a, frame=0.1, ask=False):
    if ask:
        a = input("Angle (0-180): ")
        while float(a)>180 or float(a)<0:
            a = input("Angle (0-180): ")

    duty = angle_to_duty(float(a))
    p.ChangeDutyCycle(duty)
    print(duty)
    time.sleep(0.1)

def rotate_with_speed(p, init_a, a=0, speed=0.1, ask=False):
    if ask:
        a = input("Angle (0-180): ")
        while float(a)>180 or float(a)<0:
            a = input("Angle (0-180): ")

    duty_final = angle_to_duty(float(a))
    duty_init = angle_to_duty(float(init_a))

    for d in np.linspace(duty_init, duty_final, 1./speed):
      print(d)
      p.ChangeDutyCycle(d)
      time.sleep(0.03)
    return a

def rotate_with_speed2(p, init_a, a=0, speed=0.1, ask=False):
    if ask:
        a = input("Angle (0-180): ")
        while float(a)>180 or float(a)<0:
            a = input("Angle (0-180): ")

    duty_final = angle_to_duty(float(a))
    duty_init = angle_to_duty(float(init_a))

    for d in np.linspace(duty_init, duty_final, np.abs(duty_final-duty_init)/speed):
      print(d)
      p.ChangeDutyCycle(d)
      time.sleep(0.01)
    return a

servoPIN_1 = 17
# servoPIN_2 = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN_1, GPIO.OUT)
# GPIO.setup(servoPIN_2, GPIO.OUT)

p1 = GPIO.PWM(servoPIN_1, 50) # GPIO 17 for PWM with 50Hz
# p2 = GPIO.PWM(servoPIN_2, 50) # GPIO 18 for PWM with 50Hz
p1.start(2.5) # Initialization
# p2.start(2.5) # Initialization

a = 0
dir = 0

# ask = input("Prompt angle? (y/n)")=='y'
init_a = 0
try:
  while True:
    # rotate(p1, a, frame=0.1, ask=ask)
    init_a = rotate_with_speed2(p1, init_a, speed=0.05, ask=True)

except KeyboardInterrupt:
  # rotate(p1, 0, frame=0.1, ask=False)
  rotate_with_speed2(p1, init_a, a=0, speed=0.1, ask=False)

  p1.stop()
  # p2.stop()
  GPIO.cleanup()
