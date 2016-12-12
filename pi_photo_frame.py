#!/usr/bin/env python

import os, threading, random, getpass
from time import sleep
from threading import Thread
import SimpleHTTPServer, SocketServer, platform, sys, socket, urlparse
import Tkinter as tk
from Tkinter import StringVar
from PIL import ImageTk, Image
from PIL.ExifTags import TAGS

IMAGES_PATH = 'images'
NUM_SECS_PER_PHOTO = 45
PAUSE_NUM_SECS = (60 * 5)
PAUSE_COUNT_START = PAUSE_NUM_SECS/NUM_SECS_PER_PHOTO
IMAGE_WEB_PATH = 'image_history/'
window = None
image_label = None
image_label_text = None
photo_image = None
image_index = 0
photo_paths = []
history_paths = []
history_index = 0
running = True
web_thread = None
httpd = None
port_number = 8000
html_template = ''
pause_count = 0
date_time_digitized = ''

#####################################################################
# ROUTINE: SetRunning
#####################################################################
def SetRunning(value):
	global running
	global pause_count
	running = value
	if running == False:
		pause_count = PAUSE_COUNT_START
	UpdateImage(False)

#####################################################################
# ROUTINE: LoadHTMLTemplate
#####################################################################
def LoadHTMLTemplate():
	global html_template

	f = open('template.html', 'r')
	with f as template_file:
		html_template = template_file.read()
		html_template = html_template.replace('images/image1.jpeg', 'images_image1.jpeg')
		html_template = html_template.replace('images/image2.jpeg', 'images_image2.jpeg')
		html_template = html_template.replace('images/image3.jpeg', 'images_image3.jpeg')

#####################################################################
# ROUTINE: CreateHTML
#####################################################################
def CreateHTML(index, range, back_path, forward_path, main_path):
	global html_template
	global running
	# print 'BEFORE: ' + str(html_template)
	footer_info = str(index + 1) + ' of ' + str(range)
	html_str = html_template.replace('FOOTER_INFO', str(footer_info))
	if running == True:
		html_str = html_str.replace('/?action=run', '/?action=pause')
		html_str = html_str.replace('PAUSE_RUN_TEXT', 'PAUSE')
	else:
		html_str = html_str.replace('PAUSE_RUN_TEXT', 'RUN')
	html_str = html_str.replace('images_image1.jpeg', str(back_path))
	html_str = html_str.replace('images_image2.jpeg', str(forward_path))
	html_str = html_str.replace('images_image3.jpeg', str(main_path))
	# print 'AFTER: ' + str(html_str)
	return html_str

#####################################################################
# CLASS: MyWebHandler
#####################################################################
class MyWebHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

	#####################################################################
	# ROUTINE: do_GET
	#####################################################################
	def do_GET(self):
		global history_paths
		global running
		global history_index
		global pause_count

		# Parse query data & params to find out what was passed
		parsed_params = urlparse.urlparse(self.path)
		query_parsed = urlparse.parse_qs(parsed_params.query)
		# print 'parsed_params: ' + str(parsed_params)
		if parsed_params.query == 'action=pause':
			# print 'ACTION: pause'
			history_index = len(history_paths) - 1
			SetRunning(False)
		elif parsed_params.query == 'action=run':
			# print 'ACTION: run'
			history_index = len(history_paths) - 1
			SetRunning(True)
		elif parsed_params.query == 'action=backward':
			# print 'ACTION: backward'
			if history_index > 0:
				history_index = history_index - 1
			SetRunning(False)
		elif parsed_params.query == 'action=forward':
			# print 'ACTION: forward'
			if history_index < len(history_paths) - 1:
				history_index = history_index + 1
			SetRunning(False)

		# request is either for a file to be served up or our test
		if parsed_params.path == "/":
			self.ProcessMyRequest(query_parsed)
		else:
			# print 'path: ' + parsed_params.path
			# Default to serve up a local file 
			SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self);

	#####################################################################
	# ROUTINE: ProcessMyRequest
	#####################################################################
	def ProcessMyRequest(self, query):
		global history_paths
		global history_index
		global running

		num_images = len(history_paths)
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

		back_bath = ''
		forward_bath = ''
		main_path = ''
		if history_index >= 0 and history_index < num_images:
			main_path = str(history_paths[history_index])
			if history_index > 0:
				back_bath = str(history_paths[history_index-1])
			if history_index < (num_images-1):
				forward_bath = str(history_paths[history_index+1])
		# print str(history_paths)
		# print str(history_index) + ' ' + str(num_images) + ' "' + back_bath + '" "' + main_path + '" "' + forward_bath + '" ' +  str(running)
		new_html = CreateHTML(history_index, str(num_images), back_bath, forward_bath, main_path)
		self.wfile.write(new_html)

#####################################################################
# ROUTINE: WebThread
#####################################################################
def WebThread(arg):
	global httpd
	handler = MyWebHandler
	httpd = SocketServer.TCPServer(("", port_number), handler)
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
		# print 'COUNT: ' + str(len(photo_paths))

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
	global image_label_text

	#This creates the main window of an application
	window = tk.Tk()
	window.attributes("-fullscreen", True) 
	window.focus_set()
	window.bind("<Escape>", QuitEvent)

	image_label = tk.Label(window, image = None, bg='black')
	image_label.pack(side = "bottom", fill = "both", expand = "yes")

	image_label_text = tk.Label(image_label, text='HELLO THERE', fg="red", bg="black")
	image_label_text.place(x=0, y=0)


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
	global date_time_digitized

	try:
		w, h = window.winfo_screenwidth(), window.winfo_screenheight()
		image_file = Image.open(image_path)

		try:
			photo_info = image_file._getexif()
			if photo_info != None:
				for tag, value in photo_info.items():
					decoded = TAGS.get(tag, tag)
					if decoded == 'DateTimeDigitized':
						date_time_digitized = str(value)
						split_data_time = date_time_digitized.split(' ')
						if len(split_data_time) == 2:
							year_month_day = split_data_time[0].split(':')
							if len(year_month_day) == 3:
								date_time_digitized = year_month_day[1] + '/' + year_month_day[2] + '/' + year_month_day[0]
						break
		except:
			print 'Exception did occur'
			pass

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
	global history_index
	global running
	global image_label_text
	global pause_count
	global date_time_digitized

	if len(photo_paths) == 0:
		photos_path = '/media/' + getpass.getuser() + '/PHOTOS'
		# photos_path = '/Volumes/PHOTOS'
		CreateFileList(photos_path)

	if restart:
		if pause_count > 0:
			pause_count = pause_count - 1
			if pause_count <= 0:
				running = True

	while True:
		image_path = ''
		num_photos = len(photo_paths)
		if running == False:
			image_label_text.configure(text='PAUSED')
			image_label_text.place(x=0, y=0)
			if history_index >= 0 and history_index < len(history_paths):
				image_path = history_paths[history_index]
			else:
				history_index = len(history_paths) - 1
				image_path = history_paths[history_index]
		elif num_photos > 0:
			index = random.randint(0, num_photos-1)
			image_path = photo_paths[index]
			if running:
				del photo_paths[index]
		else:
			image_path = 'images/image' + str((image_index%3) + 1) + '.jpeg'

		if running:
			# image_label_text.place(x=-1000, y=-1000)
			history_paths.append(image_path)
			history_index = len(history_paths) - 1

		if UpdateImageLabel(image_path):
			if running:
				image_label_text.configure(text=date_time_digitized)
			else:
				image_label_text.configure(text=date_time_digitized + ' - PAUSED')
			break

	if running == True and history_paths != None:
		while len(history_paths) > 20:
			del history_paths[0]

	if restart == True:
		image_index = image_index + 1
		window.after(NUM_SECS_PER_PHOTO * 1000, UpdateImage)

# **************************************************************
# ROUTINE:	Main
# **************************************************************

LoadHTMLTemplate()
CreateWindow()
UpdateImage()
web_thread = StartWebServer()

window.config(cursor="none")
window.mainloop()

