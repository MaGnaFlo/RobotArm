import pigpio
import time
import RPi.GPIO as GPIO
import numpy as np
import zmq
import json

port = '5556'

camera = {"focal_length": 5141,
          "width": 640,
          "height": 480}

# Server is created with a socket type "zmq.REP" and is bound
# to well-known port.
context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("tcp://*:%s" % port)

def angle_to_duty(angle):
    duty = float(angle)/180.*(2500-600) + 600
    return duty

def rotate(p, pin, a, mode='constant_time', speed=10):

    duty_final = []
    duty_init = []
    drange = []
    lrange = []
    delta_d = []
    for i in range(len(pin)):
      di = p[i].get_servo_pulsewidth(pin[i])
      df = angle_to_duty(float(a[i]))
      duty_init.append(di)
      duty_final.append(df)
      delta_d.append(np.abs(df-di))

    max_delta_d = max(delta_d)
    print(max_delta_d, np.argmax(delta_d))

    for i in range(len(pin)):
      if mode in ['constant_speed']:
        r = np.linspace(duty_init[i], duty_final[i], int(max_delta_d/speed))
        drange.append(r)
        lrange.append(len(r))
      elif mode in ['constant_time']:
        r = np.linspace(duty_init[i], duty_final[i], int(2500/speed)) # 2500 arbitrary
        drange.append(r)
        lrange.append(len(r))

    duty_final = np.array(duty_final)
    duty_init = np.array(duty_init)

    max_lrange = max(lrange)
    argmax_lrange = np.argmax(lrange)

    for n in range(max_lrange):
      for i in range(len(p)):
        d = drange[i][n]
        p[i].set_servo_pulsewidth(pin[i], d)
        time.sleep(0.01)

# Initialize the servo motors
a1 = 90
a2 = 45
a3 = 90

servoPIN_1 = 17
p1 = pigpio.pi()
p1.set_mode(servoPIN_1, pigpio.OUTPUT) # Initialization
p1.set_servo_pulsewidth(servoPIN_1, angle_to_duty(a1))
p1.set_PWM_frequency(17,50)

servoPIN_2 = 18
p2 = pigpio.pi()
p2.set_mode(servoPIN_2, pigpio.OUTPUT) # Initialization
p2.set_servo_pulsewidth(servoPIN_2, angle_to_duty(a2))
p2.set_PWM_frequency(17,50)

servoPIN_3 = 27
p3 = pigpio.pi()
p3.set_mode(servoPIN_3, pigpio.OUTPUT) # Initialization
p3.set_servo_pulsewidth(servoPIN_3, angle_to_duty(a3))
p3.set_PWM_frequency(17,50)

p = [p1, p2, p3]
pin = [servoPIN_1, servoPIN_2, servoPIN_3]

# loop
try:
  while True:

    json_coords = socket.recv_json()
    coords = json.loads(json_coords)
    x = coords["x"]
    y = coords["y"]
    print("received coords:", x, y)

    dx = camera["width"]/2. - x
    dy = camera["height"]/2. - y
    da1 = np.arctan2(dx, camera["focal_length"]) * 180. / np.pi
    da2 = np.arctan2(dy, camera["focal_length"]) * 180. / np.pi

    print(da1, da2)

    # update
    a1 = a1 - da1
    a2 = a2 + da2

    a = [a1, a2, a3]
    print(a)

    # rotate accordingly
    rotate(p, pin, a, mode='constant_speed', speed=10)

except KeyboardInterrupt:
  p1.stop()
  p2.stop()

