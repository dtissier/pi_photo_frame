import os
import threading
import Tkinter as tk
from PIL import ImageTk, Image

IMAGES_PATH = 'images'
window = None
image_label = None
photo_image = None
image_index = 0

# **************************************************************
# ROUTINE:	CreateFileList
# **************************************************************
def CreateFileList():
	print 'IMAGES:'
	for root, dirs, files in os.walk(IMAGES_PATH):
		path = root.split('/')
		for filename in files:
			print ' ' + os.path.join(root,filename)

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

	w, h = window.winfo_screenwidth(), window.winfo_screenheight()
	image_file = Image.open(image_path)
	image_file = FitToScreen(image_file, w, h)
	photo_image = ImageTk.PhotoImage(image_file)

	image_label.configure(image = photo_image)
	image_label.image = photo_image
	image_label.pack(side = "bottom", fill = "both", expand = "yes")

# **************************************************************
# ROUTINE:	UpdateImage
# **************************************************************
def UpdateImage():
	global window
	global image_index

	image_path = 'images/image' + str((image_index%3) + 1) + '.jpeg'
	UpdateImageLabel(image_path)
	image_index = image_index + 1
	window.after(3000, UpdateImage)

# **************************************************************
# ROUTINE:	Main
# **************************************************************

CreateFileList()
CreateWindow()

UpdateImage()

window.config(cursor="none")
window.mainloop()
