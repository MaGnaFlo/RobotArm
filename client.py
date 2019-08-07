from imutils.video import VideoStream
from imagezmq import imagezmq
import argparse
import socket
import imutils
import time

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--serverip", required=True,
	help = "ip adress of the server to which the client will connect")
args = vars(ap.parse_args())

# initialize the ImageSender object with the socket adress of the server
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(args["serverip"]))

# get hostname, initialize the video stream
# allow the camera sensor to warmup

rpiName = socket.gethostname()
vs = VideoStream(usePiCamera=True, resolution=(640,480)).start()
time.sleep(2.0)

while True:
	# read frame from camera and send it to server
	frame = vs.read()
	frame = imutils.resize(frame, width=200)
	sender.send_image(rpiName, frame)
