import time
from adafruit_crickit import crickit
from adafruit_seesaw.neopixel import NeoPixel

#Set global variables

#initialize LEDs and color states
num_pixels = 9
pixels = NeoPixel(crickit.seesaw, 20, num_pixels)

RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
OFF = (0, 0, 0)





def lights(state):
	# controls light behavior. Does not handle interrupts
	# lights begin and end with each LED in the off state

	pixels.fill(OFF)
	pixels.show()

	if state == 'ID_scanning':
		#blue lights move across the LED strip
		for i in range(num_pixels):
			pixels.fill(OFF)
			pixels[i] = BLUE
			pixels.show()
			time.sleep(.2)

	elif state == 'ID_registered':
		#green light turns on for 1 second
		pixels.fill(GREEN)
		pixels.show()
		time.sleep(1)

	elif state == 'cup_locked':
		#green light flashes quickly twice
		for i in range(2):
			pixels.fill(GREEN)
			pixels.show()
			time.sleep(.25)
			pixels.fill(OFF)
			pixels.show()
			time.sleep(.25)

	elif state == 'ID_wrong':
		#red light flashes quickly twice
		for i in range(2):
			pixels.fill(RED)
			pixels.show()
			time.sleep(.25)
			pixels.fill(OFF)
			pixels.show()
			time.sleep(.25)

	elif state == 'ID_correct':
		#green light flashes slowly once
		pixels.fill(GREEN)
		pixels.show()
		time.sleep(1.0)
	else:
		print("lights state undefined")

	pixels.fill(OFF)
	pixels.show()
	return True

def servo(state):
	#controls servo angle to lock/unlock the safecup
	if state =='lock':
		crickit.servo_1.angle = 0
	elif state =='unlock':
		crickit.servo_1.angle = 180
	return True

def readImg(image):
	# returns the drivers license number if DL is detected
	# returns cropped image of the largest face in the image if face detected and no DL number found
	# returns empty array if no face or no drivers license found

	# code stub here only to test program flow

	if image == 1:
		return 'ID', readID(image)
	if image == 2:
		return 'ID', '123457'
	if image == 3:
		return 'Face', [[0 for i in range(10)] for j in range(10)]
	else:
		return '',[]

def readID (image):
	# Only handles california driver's licenses
	# Return empty string if no ID found
	# Return drivers license number as a string if ID found

	return '123456'

def textFace(image):
	print('texting face to phone')

def main():
	#runs a forever while loop when the function starts. 
	# System state initializes with no ID registered
	# System states and transitions are:

	# scanning ID 		initial state. DL is an empty string.
	#					Can only return to this state by
	#					restarting program
	#
	# ID_registered 	DL is a non-empty string
	# locked			DL is a non-empty string and button is pressed
	# 

	#initialize program loop
	ID = ''
	while True:
		faceOrID=''
		content =''


		
		if not ID:
			readImginput = int(input('press 1 to load ID'))
			print ('ID not loaded')
			lights('ID_scanning')
			faceOrID, content = readImg(readImginput)
			if faceOrID == 'ID':
				ID = content
				print('ID loaded', ID)
		elif ID:
			readImginput = int(input('1 to load correct ID, 2 to load incorrect ID, 3 to be a creep, 4 for no face/ID'))
			print(readImginput)
			if crickit.touch_1.value:
				print('lock button pressed')
				servo('lock')
				lights('cup_locked')
			if crickit.touch_2.value:
				print('call for help button pressed')
			else:
				faceOrID, content = readImg(readImginput)
				if not faceOrID:
					print('no face or ID found')
				if faceOrID =='Face':
					print('stranger danger')
					textFace(content)
				if faceOrID =='ID':
					if content == ID:
						print('ID correct')
						lights('ID_correct')
						servo('unlock')
					else:
						print('ID wrong')
						lights('ID_wrong')

		else:
			print ('something went wrong in ID loop')



if __name__== '__main__':
	main()