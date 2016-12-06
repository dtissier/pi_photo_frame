#!/usr/bin/env python

import os
import threading
import random
import getpass
import Tkinter as tk
from PIL import ImageTk, Image

IMAGES_PATH = 'images'
NUM_SECS_PER_PHOTO = 20
window = None
image_label = None
photo_image = None
image_index = 0
photo_paths = []
history_paths = []


# **************************************************************
# ROUTINE:	CreateFileList
# **************************************************************
def CreateFileList(path):
	global photo_paths
	global history

	if os.path.exists(path):
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
def UpdateImage():
	global window
	global image_index
	global photo_paths
	global history_paths

	if len(photo_paths) == 0:
		photos_path = '/media/' + getpass.getuser() + '/PHOTOS'
		CreateFileList(photos_path)

	while True:
		image_path = ''
		num_photos = len(photo_paths)
		if num_photos > 0:
			index = random.randint(0, num_photos-1)
			image_path = photo_paths[index]
			history_paths.append(image_path)
			del photo_paths[index]
		else:
			image_path = 'images/image' + str((image_index%3) + 1) + '.jpeg'
		if UpdateImageLabel(image_path):
			break

	image_index = image_index + 1
	window.after(NUM_SECS_PER_PHOTO * 1000, UpdateImage)

# **************************************************************
# ROUTINE:	Main
# **************************************************************

CreateWindow()

UpdateImage()

window.config(cursor="none")
window.mainloop()
