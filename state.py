# -*- coding: utf-8 -*-
"""
Created on Sun May 19 13:46:53 2019

@author: Burned Yams
"""
import os, numpy as np, RPi.GPIO as GPIO, time
#import process
#import the scripts for processing images
#import process

#Next Sector
def next_step(step, rotate):
    if step == 6 and rotate == 1:
        rotate = -1
        return step, rotate
    if step == 1 and rotate == -1:
        rotate = 1
        return step, rotate
    step = step + rotate
    return step, rotate
        

    
#Initialize
    
#Inputs
diag_pin = 21
diag = 0
step_pin = 20
ready = 0

#Outputs
cap_pin = 16
captured = 0

#Internal variables
step = 1
rotate = 1
anomaly = np.zeros(7)
fp_anomaly = np.zeros(7)
anomaly_string = ['' for x in range(7)]
brightness = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(cap_pin, GPIO.OUT)
GPIO.setup(diag_pin, GPIO.IN)
GPIO.setup(step_pin, GPIO.IN)
    
while True:
    #Check inputs
    diag = GPIO.input(diag_pin)
    ready = GPIO.input(step_pin)
    
    if not ready and captured:
        step, rotate = next_step(step, rotate)
        captured = 0
        
    if ((step == 1 and rotate == 1) or (step == 6 and rotate == -1)) and not ready and not captured:
        if fp_anomaly.any():
            for i in range(7):
                if fp_anomaly[i]:
                    anomaly_string[i] = str(fp_anomaly[i])
            anomaly_string[0] = ''
            for i in range(1,7):
                anomaly_string[0] += anomaly_string[i] 
            file = open('send_message.txt', 'w')
            file.write('A\n%s' % anomaly_string[0])
            file.close()
            os.system('LoRa_Detection_Node TX') #transmit
        
    
    if not ready and not captured:
        #os.system('LoRa_Detection_Node RX 5') #recieve
        time.sleep(1)
        
    if ready and not captured:
        #brightness = process.pictures(step)
        if anomaly[step]:
            #fp_anomaly[step] = process.false_positive(step, brightness)
            time.sleep(3)
        #anomaly[step] = process.regular(step, brightness)
        captured = 1
    
    GPIO.output(cap_pin, captured)