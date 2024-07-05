tar xfv /opt/ft/opencv-4.1.0-armhf.tar.bz2
mv /opt/ft/opencv-4.1.0 /opt
rm /opt/ft/opencv-4.1.0-armhf.tar.bz2
echo 'export LD_LIBRARY_PATH=/opt/opencv-4.1.0/lib:$LD_LIBRARY_PATH' >> /opt/ft/.bashrc
source .bashrc