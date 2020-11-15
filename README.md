# SafeDriving

💡 Algorithm   
Detect eyes->Count time(when eyes closed)->if the count up to 3->alarm🔥   

🙈 What we use   
RasberryPi, opencv, webcam

### 🌼 How to install openCV in your RasberryPi
🔥 Make sure there's no opencv file exists in your RasberryPi   
1. Check your RasberryPi OS version
```
$ cat /etc/*release*
```   
<img src="https://user-images.githubusercontent.com/57944153/99189068-b16fa000-27a2-11eb-991c-84d9f023c02f.PNG" width="600" height="200"/>

2. Update any existing packages
```
$ sudo apt-get update
```

3. Install some developer tools
```
$ sudo apt-get install build-essential cmake pkg-config
$ sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
$ sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
$ sudo apt-get install libxvidcore-dev libx264-dev
$ sudo apt-get install libgtk2.0-dev
$ sudo apt-get install libatlas-base-dev gfortran
$ sudo apt-get install python2.7-dev python3-dev
```

4. Download the openCV source code
```
$ cd ~
$ wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.1.0.zip
$ unzip opencv.zip
$ wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.1.0.zip
$ unzip opencv_contrib.zip
```
⚡ I don't know why, but in my RasberryPi, I can get opencv-3.0.0 file when I do unzip opencv.zip   
&nbsp;&nbsp;&nbsp;&nbsp; Make sure the opencv_contrib and opencv file's version are the **same**   
&nbsp;&nbsp;&nbsp;&nbsp; So I just download the opencv file in window, and I import it by USB.   

4. Install pip
```
$ wget https://bootstrap.pypa.io/get-pip.py
$ sudo python get-pip.py
```

5. Install numpy
```
$ pip install numpy
```

6. Setup build using CMake
```
$ cd ~/opencv-3.1.0/
$ mkdir build
$ cd build
$ cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.1.0/modules \
    -D BUILD_EXAMPLES=ON ..
```

7. Build
```
$ make -j4
```
⚡ It could take more than 2 hours, so just take a rest.

8. Install openCV
```
$ sudo make install
$ sudo ldconfig
```

9. Finish
<img src="https://user-images.githubusercontent.com/57944153/99189710-d3b6ed00-27a5-11eb-88b4-37a8b0c0276d.PNG" width="600" height="200"/>
