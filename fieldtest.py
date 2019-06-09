# -*- coding: utf-8 -*-
"""
Created on Sat Jun  1 17:23:54 2019

@author: Burned Yams
"""

import process

while True:
	step = raw_input('Enter "Exit" to exit or enter a number for file name:')
	if step == 'Exit':
		break
	step = int(step, 10)
	brightness = process.pictures(step)
	print(brightness)
print('goobye')