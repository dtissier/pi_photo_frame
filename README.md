# pi_photo_frame
Simple python photo frame application

First need to get the image library:

    sudo apt-get update
    sudo apt-get install python-imaging
    sudo apt-get install python-imaging-tk

It's always a pain in the ass with Linux to determine which 
file to edit to get stuff to auto launch.  For me it was:

    ~/.config/lxsession/LXDE-pi/autostart

And add the line:

    @lxterminal -e /path/to/the/launcher.sh 


