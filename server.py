import zmq
import time
import sys
import pickle

port = '5556'

# Server is created with a socket type "zmq.REP" and is bound
# to well-known port.
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.bind("tcp://*:%s" % port)

print("Sender connected.")
print("Standby...")

a = 0

# it will block on recv() to get a request *before* it can send a reply
while True:
	try:
		message_save = {'mess': message}
		filename = 'message'
		outfile = open(filename, 'wb')
		pickle.dump(message_save, outfile)
		outfile.close()
		socket.send(b"ok")

		time.sleep(0.5)
		
	except KeyboardInterrupt:
		break
