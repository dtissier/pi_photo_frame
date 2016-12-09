#!/usr/bin/env python

import os, threading, random, getpass
from time import sleep
from threading import Thread
import SimpleHTTPServer, SocketServer, platform, sys, socket, urlparse
import Tkinter as tk
from PIL import ImageTk, Image

IMAGES_PATH = 'images'
NUM_SECS_PER_PHOTO = 45
IMAGE_WEB_PATH = 'image_history/'
window = None
image_label = None
photo_image = None
image_index = 0
photo_paths = []
history_paths = []
history_index = None
show_history = False
web_thread = None
httpd = None
port_number = 8000

#####################################################################
# CLASS: MyWebHandler
#####################################################################
class MyWebHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

	#####################################################################
	# ROUTINE: do_GET
	#####################################################################
	def do_GET(self):
		global history_paths
		global show_history
		global history_index

		# Parse query data & params to find out what was passed
		parsed_params = urlparse.urlparse(self.path)
		query_parsed = urlparse.parse_qs(parsed_params.query)
		print 'parsed_params: ' + str(parsed_params)
		if parsed_params.query == 'action=pause':
			show_history = True
			history_index = len(history_paths) - 1
			UpdateImage(False)
		elif parsed_params.query == 'action=run':
			show_history = False
			history_index = None
			UpdateImage(False)
		elif parsed_params.query == 'action=backward':
			if history_index != None and history_index > 0:
				history_index = history_index - 1
			show_history = True
			UpdateImage(False)
		elif parsed_params.query == 'action=forward':
			if history_index != None and history_paths != None and history_index < len(history_paths) - 1:
				history_index = history_index + 1
			show_history = True
			UpdateImage(False)

		# request is either for a file to be served up or our test
		if parsed_params.path == "/":
			self.ProcessMyRequest(query_parsed)
		else:
			print 'path: ' + parsed_params.path
			# Default to serve up a local file 
			SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self);

	#####################################################################
	# ROUTINE: ProcessMyRequest
	#####################################################################
	def ProcessMyRequest(self, query):
		global history_paths
		global history_index
		global show_history

		num_images = len(history_paths)
		if history_index == None:
			history_index = num_images - 1
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

		image_url = str(history_paths[history_index])
		self.wfile.write('<html><head><title>RESPBERRY PI PHOTO FRAME</title></head>')
		self.wfile.write('<body>')
		self.wfile.write('' + str(history_index+1) + ' of ' + str(num_images) + '<br>')
		self.wfile.write('<a href="/"><button>Refresh</button></a>')
		if show_history == True:
			self.wfile.write('<a href="/?action=run"><button>Run</button></a>')
		else:
			self.wfile.write('<a href="/?action=pause"><button>Pause</button></a>')
		self.wfile.write('<a href="/?action=backward"><button>Backward</button></a>')
		self.wfile.write('<a href="/?action=forward"><button>Forward</button></a><br>')
		self.wfile.write('<img src="' + image_url + '">')
		self.wfile.write('</body></html>')

#####################################################################
# ROUTINE: WebThread
#####################################################################
def WebThread(arg):
	global httpd
	handler = MyWebHandler
	httpd = SocketServer.TCPServer( ("", port_number), handler )
	print
	print "Photo Frame Server"
	print "       Port:", port_number
	print
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
	print
	print "Server Closed"

#####################################################################
# ROUTINE: StartWebServer
#####################################################################
def StartWebServer():
	global web_thread
	web_thread = Thread(target=WebThread, args = (10, ))
	web_thread.start()
	return web_thread

# **************************************************************
# ROUTINE:	CreateFileList
# **************************************************************
def CreateFileList(path):
	global photo_paths
	global history

	if os.path.exists(path):
		os.chdir('/')
		# print 'IMAGES:'
		for root, dirs, files in os.walk(path):
			path = root.split('/')
			for filename in files:
				if filename.endswith('.jpg'):
					if filename.startswith('.') == False:
						full_path = os.path.join(root,filename)
						photo_paths.append(full_path)
						history_paths = []
						# print ' ' + full_path
		print 'COUNT: ' + str(len(photo_paths))

# **************************************************************
# ROUTINE:	QuitEvent
# **************************************************************
def QuitEvent(e):
	global web_thread
	global httpd
	if httpd != None:
		httpd.shutdown()
	if web_thread != None:
		web_thread.join()
	e.widget.quit()

# **************************************************************
# ROUTINE:	CreateWindow
# **************************************************************
def CreateWindow():
	global window
	global image_label

	#This creates the main window of an application
	window = tk.Tk()
	window.attributes("-fullscreen", True) 
	window.focus_set()
	window.bind("<Escape>", QuitEvent)

	image_label = tk.Label(window, image = None, bg='black')
	image_label.pack(side = "bottom", fill = "both", expand = "yes")


# **************************************************************
# ROUTINE:	FitToScreen
# **************************************************************
def FitToScreen(image_file, w, h):
	cur_width = image_file.size[0]
	cur_height = image_file.size[1]
	width_ratio = float(w)/float(cur_width)
	height_ratio = float(h)/float(cur_height)
	# print 'image_file:'
	# print '         width=' + str(cur_width)
	# print '        height=' + str(cur_height)
	# print '   width_ratio=' + str(width_ratio)
	# print '  height_ratio=' + str(height_ratio)
	if (width_ratio < height_ratio):
		new_width = cur_width * width_ratio
		new_height = cur_height * width_ratio
	else:
		new_width = cur_width * height_ratio
		new_height = cur_height * height_ratio
	image_file = image_file.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
	return image_file

# **************************************************************
# ROUTINE:	UpdateImageLabel
# **************************************************************
def UpdateImageLabel(image_path):
	global window
	global image_label
	global photo_image

	try:
		w, h = window.winfo_screenwidth(), window.winfo_screenheight()
		image_file = Image.open(image_path)
		image_file = FitToScreen(image_file, w, h)
		photo_image = ImageTk.PhotoImage(image_file)

		image_label.configure(image = photo_image)
		image_label.image = photo_image
		image_label.pack(side = "bottom", fill = "both", expand = "yes")
		return True

	except:
		return False

	return False

# **************************************************************
# ROUTINE:	UpdateImage
# **************************************************************
def UpdateImage(restart=True):
	global window
	global image_index
	global photo_paths
	global history_paths
	global show_history

	if len(photo_paths) == 0:
		photos_path = '/media/' + getpass.getuser() + '/PHOTOS'
		CreateFileList(photos_path)

	while True:
		image_path = ''
		num_photos = len(photo_paths)
		if show_history and history_index != None and history_index < len(history_paths):
			image_path = history_paths[history_index]
		elif num_photos > 0:
			index = random.randint(0, num_photos-1)
			image_path = photo_paths[index]
			history_paths.append(image_path)
			del photo_paths[index]
		else:
			image_path = 'images/image' + str((image_index%3) + 1) + '.jpeg'
			history_paths.append(image_path)

		if UpdateImageLabel(image_path):
			break

	if show_history == False and history_paths != None:
		while len(history_paths) > 20:
			del history_paths[0]

	if restart == True:
		image_index = image_index + 1
		window.after(NUM_SECS_PER_PHOTO * 1000, UpdateImage)

# **************************************************************
# ROUTINE:	Main
# **************************************************************

CreateWindow()
UpdateImage()
web_thread = StartWebServer()

window.config(cursor="none")
window.mainloop()

