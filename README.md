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

On top of this I had to do some permision changes:

    sudo chmod +x launcher.sh
    sudo chmod +x pi_photo_frame.py

But I really don't know what actually was needed to get it to work.

To make it so the device doesn't sleep edit:

    sudo nano /etc/lightdm/lightdm.conf

and add the line:

    xserver-command=X -s 0 dpms


