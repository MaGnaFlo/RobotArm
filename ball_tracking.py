from collections import deque
from imutils.video import VideoStream
import numpy as np 
import argparse
import cv2
import imutils
import time

from imutils import build_montages
from datetime import datetime
from imagezmq import imagezmq
import pickle
import zmq
import json

port = "5556"
server_ip = '192.168.0.17'
context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.connect("tcp://{}:{}".format(server_ip, port))

def save_coordinates(center):
	coords = {"x": center[0], "y": center[1]}
	with open("coords.pickle", "wb") as f:
		pickle.dump(coords, f)

print("Ball tracking...")

# initialize ImageHub object
imageHub = imagezmq.ImageHub()

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points

# Tennis ball
greenLower = (26 ,37, 7)
greenUpper = (81, 232, 171)

## Green pen
# greenLower = (32 ,172, 9)
# greenUpper = (114, 255, 223)

bufferlen = 128

pts = deque(maxlen=bufferlen)

# warm up
time.sleep(2.0)

xc,yc=None, None

while True:
	(rpiName, frame) = imageHub.recv_image()
	imageHub.send_reply(b'OK')

	# preprocess
	frame = imutils.resize(frame, width=640)
	frame = frame[::-1,:]
	blurred = cv2.GaussianBlur(frame, (11,11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color of the object
	# erode and dilate to get rid of artifacts
	mask = cv2.inRange(hsv, greenLower, greenUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None

	overlay = frame.copy()
	output = frame.copy()

	if len(cnts) > 0:
		# find the largest contour in the mask
		# use it to compute minimum enclosing circle and centroid
		c = max(cnts, key=cv2.contourArea)
		((x,y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		if xc == None:
			xc = center[0]
			yc = center[0]
		print("Current coordinates:", center)
		# save_coordinates(center)
		# if np.abs(center[0]-xc) > 50 and np.abs(center[1]-yc) > 50:
			# continue
		xc = center[0]
		yc = center[0]
		coords = {"x": center[0], "y": center[1]}
		json_coords = json.dumps(coords)
		socket.send_json(json_coords)

		# only proceed if the radius meets a minimum size
		if radius > 10:
			cv2.circle(overlay, (int(x), int(y)), int(radius),
				(0, 255, 255), 1)
			cv2.circle(overlay, center, 2, (0,0,255), -1)

	pts.appendleft(center)
	# loop over the set of tracked points
	for i in range(1, len(pts)):
		if pts[i-1] is None or pts[i] is None:
			continue

		thickness = max(1,int(bufferlen / float(i+1) / 4.))
		alpha = 1./(i+1)

		cv2.line(overlay, pts[i-1], pts[i], (0,0,255), thickness)
		cv2.addWeighted(overlay, alpha, output, 1 - alpha,
		0, output)

	cv2.imshow("frame", output)
	cv2.imshow("masked", mask)
	key = cv2.waitKey(1) & 0xFF
	if key == ord('q'):
		break
 
# close all windows
cv2.destroyAllWindows()



