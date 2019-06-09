# -*- coding: utf-8 -*-
"""
Created on Sun May  5 15:11:17 2019

@author: Burned Yams
"""

import picamera, time, os, smbus, RPi.GPIO as GPIO, numpy as np, cv2, math
import algorithm

def pictures(step):
    # Initialization
    pin = 26
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    camera = picamera.PiCamera()
    time.sleep(3)
    
    red = 65535
    blue = 65535
    green = 65535
    bus = smbus.SMBus(1)
    address = 0x44
    brightness = 0


    # RGB brightness sensor
    for x in range(2):
        bus.write_byte_data(address,1,0b00001101)
    for x in range(9,15):
        data = bus.read_byte_data(address,x)
        data = bus.read_byte_data(address,x)
        time.sleep(0.5)
        print('Reg%d : %d' % (x, data))
        if x == 9:
        	green = data
        if x == 10:
        	green = data*256 + green
        if x == 11:
        	red = data
        if x == 12:
        	red = data*256 + red
        if x == 13:
        	blue = data
        if x == 14:
        	blue = data*256 + blue
    
    file = open('step%d.txt' % step, 'w')
    file.write('green = %d\n' % green)
    file.write('red = %d\n' % red)
    file.write('blue = %d\n' % blue)
    file.close()
    
    if blue and green and red < 150:
        brightness = 0
    else:
        brightness = 1
    
    # Take a picture with picamera
    
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(1)
    camera.capture('RGB_high%d.jpg' % step)
    

    GPIO.output(pin, GPIO.LOW)
    time.sleep(1)
    camera.capture('RGB_low%d.jpg' % step)
    
    
    
    # Take a picture with lepton
    os.system('./LeptonModule/software/raspberrypi_capture/raspberrypi_capture')
    os.rename('IMG_0000.pgm', 'lepton%d.pgm' % step)
    
    # Clean up
    GPIO.cleanup()
    camera.close()
    
    return brightness
    
def regular(step, brightness):
    
    if not brightness:
        rgb_anomaly = algorithm.rgb_threshold(step)
    else:
        rgb_anomaly = algorithm.ColorProcess(step)
        
    lep_anomaly = algorithm.lep_threshold(step)
    
    anomaly = lep_anomaly[0] and rgb_anomaly[0]
    return anomaly

def false_positive(step, brightness):
    #Strategy: look at the center of all objects that are the right size for a fire
    #If the objects' centers are close enough together confirm the false positive
    rgb_anomaly = 0
    rgb_anomaly0 = 0
    rgb_anomaly1 = 0
    lep_anomaly = 0
    lep_anomaly0 = 0
    lep_anomaly1 = 0
    anti_step = step*(-1)
    #Read in both images
    if brightness:
        rgb_anomaly0 = algorithm.ColorProcess(step)
        rgb_anomaly1 = algorithm.ColorProcess(anti_step)
    else:
        rgb_anomaly0 = algorithm.threshold(step)
        rgb_anomaly1 = algorithm.threshold(anti_step)
        
    output0 = cv2.connectedComponentsWithStats(rgb_anomaly0[1], 8, cv2.CV_32S)
    # Extract states
    stats0 = output0[2]
    # Extract center of all objects
    centroids0 = output0[3]
    
    output1 = cv2.connectedComponentsWithStats(rgb_anomaly1[1], 8, cv2.CV_32S)
    # Extract states
    stats1 = output1[2]
    # Extract center of all objects
    centroids1 = output1[3]
    
    # Compare all centers of objects of the right size
    # Object 0 is the background
    for i,j in enumerate(stats0[:,4]):
        if i > 0 and 100 < j < 500:
            for k,n in enumerate(stats1[:,4]):
                if k > 0 and 100 < n < 500:
                    dist = math.hypot[centroids0[i,0] - centroids1[k,0], centroids0[i,1] - centroids1[k,1]]
                    if dist < 250:
                        rgb_anomaly = 1
                        
    lep_anomaly0 = algorithm.lep_threshold(step)
    lep_anomaly1 = algorithm.lep_threshold(anti_step)
    # Perform the operation
    lep_output0 = cv2.connectedComponentsWithStats(lep_anomaly0[1], 8, cv2.CV_32S)
    # Extract states
    lep_stats0 = lep_output0[2]
    # Extract center of all objects
    lep_centroids0 = lep_output0[3]
    # Perform the operation
    lep_output1 = cv2.connectedComponentsWithStats(lep_anomaly1[1], 8, cv2.CV_32S)
    # Extract states
    lep_stats1 = lep_output1[2]
    # Extract center of all objects
    lep_centroids1 = lep_output1[3]
    
    # Compare all centers of objects of the right size
    # Object 0 is the background
    for i,j in enumerate(lep_stats0[:,4]):
        if i > 0 and 100 < j < 500:
            for k,n in enumerate(lep_stats1[:,4]):
                if k > 0 and 100 < n < 500:
                    dist = math.hypot[lep_centroids0[i,0] - lep_centroids1[k,0], lep_centroids0[i,1] - lep_centroids1[k,1]]
                    if dist < 250:
                        lep_anomaly = 1
    
    
    anomaly = lep_anomaly and rgb_anomaly
    return anomaly