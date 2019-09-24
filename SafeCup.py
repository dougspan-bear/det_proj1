import time
from adafruit_crickit import crickit
from adafruit_seesaw.neopixel import Neopixel

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





def lights(pixels, state):
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

	elif state == 'cup_closed':
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

def servo(state):
	if state =='lock':
	elif state =='unlock'

def main():


if __name__== '__main__':
	main()