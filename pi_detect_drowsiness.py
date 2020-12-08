# -*- coding: utf-8 -*-
from imutils import face_utils
import numpy as np
import argparse
import RPi.GPIO as GPIO
import imutils
import time
import dlib
import cv2

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# 피에조 번호 할당
gpio_pin=13
scale = [261]
GPIO.setup(gpio_pin,GPIO.OUT)
#gpio_pin의 주파수 100인 pwm 인스턴스 생성
p = GPIO.PWM(gpio_pin, 100)
GPIO.output(gpio_pin,True)

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
	args = vars(ap.parse_args())
	
	# 임곗값 지정
	EYE_AR_THRESH = 0.3
	EYE_AR_CONSEC_FRAMES = 16
	
	COUNTER = 0
	
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
	
	# 비디오 실행중 프레임 반복
	while True:
                
		# 프레임을 가져오고 크기 조정
		# 그레이스케일(회색조)로 변환(효율성)
		ret,frame = vs.read()
		frame = imutils.resize(frame, width=450)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		
		# 그레이 스케일 이미지에서 얼굴 감지
		rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)
		
		# 얼굴 감지 반복
		for (x, y, w, h) in rects:
                        
			# haar cascade에서 dlib 직사각형 객체 생성
			rect = dlib.rectangle(int(x), int(y), int(x + w),int(y + h))
			
			# 얼굴 영역 얼굴 landmarks 결정
			# 얼굴 landmark (x,y)좌표를 Numpy 배열로 변환
			shape = predictor(gray, rect)
			shape = face_utils.shape_to_np(shape)
			
			# 배열이 주어지면 눈 좌표 추출
			# 양쪽 눈 종횡비(ear값) 계산하는 좌표
			leftEye = shape[lStart:lEnd]
			rightEye = shape[rStart:rEnd]
			leftEAR = eye_aspect_ratio(leftEye)
			rightEAR = eye_aspect_ratio(rightEye)
			
			# 양쪽 눈 종횡비(ear값) 평균 구하기 (더 정확한 추정치)
			ear = (leftEAR + rightEAR) / 2.0

			# 양쪽 눈 볼록껍질 계산
			# drawContours 함수 이용해 실시간으로 눈 주변에 선 그리기
			leftEyeHull = cv2.convexHull(leftEye)
			rightEyeHull = cv2.convexHull(rightEye)
			cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
			cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

			# 눈 종횡비가 깜박임보다 작으면
			# 임곗값(0.3)보다 작으면 카운터를 증가시킨다
			if ear < EYE_AR_THRESH:
				COUNTER += 1
				
				# 카운터가 임곗값(16)보다 크면 
				# 알람을 울린다
				if COUNTER >= EYE_AR_CONSEC_FRAMES:
					# duty cycle을 100%로 시작
					# duty cycle을  90%로 변경
					p.start(100)
					p.ChangeDutyCycle(90)
					p.ChangeFrequency(scale[0])
					time.sleep(1)
					
					# 프레임에 "ALAM ON!" 알림
					cv2.putText(frame, "ALARM ON!", (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
				else:
					p.stop()

			# 눈 가로 세로 비율이 깜박임보다 크면
			# 카운터와 알람을 reset한다
			else:
				p.stop()
				COUNTER = 0
			
			# 눈 가로 세로 비율을 보여준다
			# 디버깅과 적절한 눈 가로 세로 비율 설정(300,30)
			# 임곗값, 프레임, 카운터
			cv2.putText(frame, "EAR: {:.3f}".format(ear), (300, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
	
		# 프레임을 보여준다
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
 
		# 'q'를 누르면 loop를 멈춘다
		if key == ord("q"):
			break
	# 윈도우 종료
	cv2.destroyAllWindows()
finally:
	print("Cleaning up")
	GPIO.cleanup()
	
