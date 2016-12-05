import Tkinter as tk
from PIL import ImageTk, Image

# **************************************************************
# ROUTINE:	FitToScreen
# **************************************************************
def FitToScreen(image_file, w, h):
	cur_width = image_file.size[0]
	cur_height = image_file.size[1]
	width_ratio = float(w)/float(cur_width)
	height_ratio = float(h)/float(cur_height)
	print 'image_file:'
	print '         width=' + str(cur_width)
	print '        height=' + str(cur_height)
	print '   width_ratio=' + str(width_ratio)
	print '  height_ratio=' + str(height_ratio)
	if (width_ratio < height_ratio):
		new_width = cur_width * width_ratio
		new_height = cur_height * width_ratio
	else:
		new_width = cur_width * height_ratio
		new_height = cur_height * height_ratio
	image_file = image_file.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
	return image_file

#This creates the main window of an application
window = tk.Tk()
window.attributes("-fullscreen", True) 
window.focus_set()
window.bind("<Escape>", lambda e: e.widget.quit())
w, h = window.winfo_screenwidth(), window.winfo_screenheight()

#Creates a Tkinter-compatible photo image, which can be used everywhere Tkinter expects an image object.
path = "images/image2.jpeg"
image_file = Image.open(path)
image_file = FitToScreen(image_file, w, h)
photo_image = ImageTk.PhotoImage(image_file)

#The Label widget is a standard Tkinter widget used to display a text or image on the screen.
panel = tk.Label(window, image = photo_image, bg='black')

#The Pack geometry manager packs widgets in rows or columns.
panel.pack(side = "bottom", fill = "both", expand = "yes")

#Start the GUI
window.mainloop()
