# -*- coding: utf-8 -*-
from picamera import PiCamera
from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import argparse
import RPi.GPIO as GPIO
import imutils
import time
import dlib
import cv2

GPIO.setmode(GPIO.BCM)

# 피에조 번호로 바꿔주세요
led_pin1=14
led_pin2=15

GPIO.setup(led_pin1,GPIO.OUT)
GPIO.setup(led_pin2,GPIO.OUT)


def euclidean_dist(ptA, ptB):
	# 두 점 사이의 거리 리턴
	return np.linalg.norm(ptA - ptB)
	
# ear 알고리즘 사용
def eye_aspect_ratio(eye):
	A = euclidean_dist(eye[1], eye[5])
	B = euclidean_dist(eye[2], eye[4])
	C = euclidean_dist(eye[0], eye[3])
	ear = (A + B) / (2.0 * C)
	
	return ear
	
try:
	# 파라미터로 입력값 받음(haar cascade xml file,dlib facial landmark predictor file)
	ap = argparse.ArgumentParser()
	ap.add_argument("-c", "--cascade", required=True,help = "path to where the face cascade resides")
	ap.add_argument("-p", "--shape-predictor", required=True,help="path to facial landmark predictor")
	# ap.add_argument("-a", "--alarm", type=int, default=0,help="boolean used to indicate if TrafficHat should be used")
	args = vars(ap.parse_args())
	
	# threshold 지정
	EYE_AR_THRESH = 0.3
	EYE_AR_CONSEC_FRAMES = 16
	
	COUNTER = 0
	ALARM_ON = False
	
	# 눈 detection에 쓰일 파일들 로드
	detector = cv2.CascadeClassifier(args["cascade"])
	predictor = dlib.shape_predictor(args["shape_predictor"])

	# facial landmark 사용해서 왼쪽, 오른쪽 눈 찾기
	(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
	(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
	
	# 비디오 실행
	print("비디오 실행중...")
	vs = cv2.VideoCapture(0)
	if vs.isOpened()==False:
		exit()
	time.sleep(1.0)
	# ---------------------------------------------------------------------
	# loop over frames from the video stream
	while True:
		# grab the frame from the threaded video file stream, resize
		# it, and convert it to grayscale
		# channels)
		ret,frame = vs.read()
		frame = imutils.resize(frame, width=450)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# detect faces in the grayscale frame
		rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)
		
		# loop over the face detections
		for (x, y, w, h) in rects:
			# construct a dlib rectangle object from the Haar cascade
			# bounding box
			rect = dlib.rectangle(int(x), int(y), int(x + w),int(y + h))
			# determine the facial landmarks for the face region, then
			# convert the facial landmark (x, y)-coordinates to a NumPy
			# array
			shape = predictor(gray, rect)
			shape = face_utils.shape_to_np(shape)
			
			# extract the left and right eye coordinates, then use the
			# coordinates to compute the eye aspect ratio for both eyes
			leftEye = shape[lStart:lEnd]
			rightEye = shape[rStart:rEnd]
			leftEAR = eye_aspect_ratio(leftEye)
			rightEAR = eye_aspect_ratio(rightEye)
			# average the eye aspect ratio together for both eyes
			ear = (leftEAR + rightEAR) / 2.0
			
			# compute the convex hull for the left and right eye, then
			# visualize each of the eyes
			leftEyeHull = cv2.convexHull(leftEye)
			rightEyeHull = cv2.convexHull(rightEye)
			cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
			cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
			# ---------------------------------------------------------------------
			# check to see if the eye aspect ratio is below the blink
			# threshold, and if so, increment the blink frame counter
			if ear < EYE_AR_THRESH:
				COUNTER += 1
				# if the eyes were closed for a sufficient number of
				# frames, then sound the alarm
				if COUNTER >= EYE_AR_CONSEC_FRAMES:
					# if the alarm is not on, turn it on
					if not ALARM_ON:
						ALARM_ON = True
						# check to see if the TrafficHat buzzer should
						# be sounded
						#if args["alarm"] > 0: # 알람 파라미터 안주었습니다~이 부분 피에조로 구현해주세요
							#th.buzzer.blink(0.1, 0.1, 10,background=True)
							
					# draw an alarm on the frame
					cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
			# otherwise, the eye aspect ratio is not below the blink
			# threshold, so reset the counter and alarm
			else:
				COUNTER = 0
				ALARM_ON = False
			
			# draw the computed eye aspect ratio on the frame to help
			# with debugging and setting the correct eye aspect ratio
			# thresholds and frame counters
			cv2.putText(frame, "EAR: {:.3f}".format(ear), (300, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	
		# show the frame
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
 
		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break
	# do a bit of cleanup
	cv2.destroyAllWindows()
	vs.stop()
finally:
	print("Cleaning up")
	GPIO.cleanup()
	
