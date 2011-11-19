#!/bin/bash
set -o errexit
set -o nounset

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
readonly OPENCV="http://${MIRROR}.dl.sourceforge.net/project/opencvlibrary/opencv-unix/2.3.1/OpenCV-2.3.1a.tar.bz2"

sudo apt-get --assume-yes install \
    cmake \
    freeglut3-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavfilter-dev \
    libavformat-dev \
    libavutil-dev \
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
cd ..

# OpenCV
wget -O - "${OPENCV}" | tar --directory=/tmp -xj
cd /tmp/OpenCV-*
cmake -D WITH_TBB=ON \
      -D WITH_V4L=ON \
      -D BUILD_NEW_PYTHON_SUPPORT=ON \
      -D INSTALL_C_EXAMPLES=ON \
      -D INSTALL_PYTHON_EXAMPLES=ON \
      -D BUILD_EXAMPLES=ON \
      .
make
sudo make install

