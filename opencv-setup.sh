#!/bin/bash
set -o errexit
set -o nounset

readonly REPO="$(readlink -f -- "$(dirname -- "${0}")/..")"
readonly LIB="${REPO}/rock-bot/lib"

readonly USERNAME="`id -un`"

MIRROR='switch'

while (( "$#" )); do
    shift
    case "${1}" in
        -m) shift; MIRROR="${1}" ;;
    esac
done

readonly MIRROR

readonly ARTOOLKIT='http://javacv.googlecode.com/files/ARToolKitPlus_2.1.1t.zip'
readonly FREENECT='https://github.com/OpenKinect/libfreenect/zipball/v0.1.1'
readonly JAVACV='http://javacv.googlecode.com/files/javacv-src-20111001.zip'
readonly JAVACPP='http://javacpp.googlecode.com/files/javacpp-src-20111001.zip'
readonly OPENCV="http://${MIRROR}.dl.sourceforge.net/project/opencvlibrary/opencv-unix/2.3.1/OpenCV-2.3.1a.tar.bz2"

sudo apt-get --assume-yes install \
    ant \
    cmake \
    default-jdk \
    freeglut3-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavfilter-dev \
    libavformat-dev \
    libavutil-dev \
    libcommons-cli-java \
    libdc1394-22-dev \
    libgstreamermm-0.10-dev \
    libgtk2.0-dev \
    libopenexr-dev \
    libpostproc-dev \
    libqt4-dev \
    libswscale-dev \
    libusb-1.0.0-dev \
    libv4l-dev \
    libvdpau-dev \
    libxi-dev \
    libxmu-dev \
    python-numpy \
    python-sphinx \
    qt4-qmake \
    texlive \
    x11proto-video-dev

# ARTToolKit
cd /tmp
wget "${ARTOOLKIT}"
unzip ARToolKitPlus_*
cd ARToolKitPlus_*
export ARTKP="$(readlink -f .)"
qmake
make
sudo make install
cd ..

# libfreenect
cd /tmp
wget -O libfreenect.zip "${FREENECT}"
unzip libfreenect.zip
cd OpenKinect-libfreenect-*
cmake .
make
sudo make install
sudo ldconfig /usr/local/lib64/
sudo adduser "${USERNAME}" video
sudo cat << EOF >> /etc/udev/rules.d/51-kinect.rules
# ATTR{product}=="Xbox NUI Motor"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02b0", MODE="0666"
# ATTR{product}=="Xbox NUI Audio"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ad", MODE="0666"
# ATTR{product}=="Xbox NUI Camera"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ae", MODE="0666"
EOF
cd ..

# OpenCV
cd /tmp
wget -O - "${OPENCV}" | tar -xj
cd OpenCV-*
cmake .
make
sudo make install


# JavaCV
cd /tmp
wget "${JAVACPP}"
unzip javacpp-*
wget "${JAVACV}"
unzip javacv-*
cd javacv
ant

# Build lib
cd /tmp/javacv
mv dist "${LIB}/javacv"
mv src "${LIB}/javacv"
cd "${LIB}/javacv/javadoc"
zip -r ../javadoc.zip *
cd ..
rm -fr javadoc
cd /tmp/javacpp
mv dist "${LIB}/javacpp"
mv src "${LIB}/javacpp"

