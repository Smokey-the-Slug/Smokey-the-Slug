# -*- coding: utf-8 -*-
"""
Created on Wed May  8 13:56:49 2019

@author: Burned Yams
"""
import os

while True:
    command = input('Enter the terminal command to execute or type "Exit" \
                    to exit the script: ')
    if command == 'Exit':
        break
    print(command)
    
    os.system('%s' % command)