import time
import threading
from random import choice

from stem import Signal
from stem.control import Controller

from splinter import Browser
from selenium import webdriver


''' this function is created so that we can jump around the tor networks to bypass ip limiting
from the survey... we want to be able to automate as many surveys as possible..
let's break the limits!!!!
'''
def jump_to_new_tor_node():
	with Controller.from_port(port = 9151) as controller:
		controller.authenticate()
		controller.signal(Signal.NEWNYM) # changes tor node.


'''
Countdown timer to find elements within a certain time. This is a fail safe against something
not working properly, causing the browser gets stuck on one page, while the code tries to continue.
This fail safe prevents the code from being stuck in an infinite loop.
'''
def timer(seconds):
	global browser
	global did_quit
	global is_timed_out
	global did_find_element

	incremValue = seconds
	while incremValue != 0:
		# if element is found, break the timer loop.
		if did_find_element:
			is_timed_out = True
			break

		time.sleep(1) # sleep for one second
		incremValue -= 1

	# if element is not found and countdown timed out, send error
	if did_find_element == False:
		is_timed_out = True
		browser.quit()
		did_quit = True
		print('Browser timed out. Please try again.')
		'''
		SEND TWILIO <TIMED OUT> NOTIFICATION TO USER
		'''


'''
These check_for functions are made to dependent on the timer using multithreading.
I needed a way to run a timer and to make sure the desired element exists on the page we are on
'''
def check_for_id_element(id_tag, is_multiple_opts=False):
	global browser
	global is_timed_out
	global did_find_element

	while True:
		if is_timed_out: # break loop if timed out
			break
		try:
			if browser.find_by_id(id_tag):
				did_find_element = True
				break # break loop if element is found
			elif not browser.find_by_id(id_tag):
				did_find_element = False
		except: pass

def check_for_css_element(css_tag, is_multiple_opts=False):
	global browser
	global is_timed_out
	global did_find_element

	while True:
		if is_timed_out: # break loop if timed out
			break
		try:
			if browser.find_by_css(css_tag):
				did_find_element = True
				break # break loop if element is found
			elif not browser.find_by_css(css_tag):
				did_find_element = False
		except: pass


'''
This is a test function that, if written correctly,
should follow the K.I.S.S (keep it simple stupid) method.
The REAL magic happens here.

======= example ========
interact_with_id('promptInput_191744', text_input=True, textInput_opts=list_of_text_queries)
interact_with_id('option_423220_198378') # should ignore text_input and textInput_opts as those are default blank
========================

if id_tag question has to be of a specific index send them in a list as such:
	=======================================================================
	- interact_with_id(['id_tag213:[1]', 'id_tag890:[3]'], multi_tags=True)
	=======================================================================
	the function will check for a split by the colons, if there, it will associate the
	index with the proper id_tag and interact with it properly
'''
def interact_with_id(id_tag, multi_tags=False, text_input=False, textInput_choice=None):
	if not did_quit:
		t1 = threading.Thread(target=timer, args=(20,))
		if multi_tags:
			# use first id_tag if a list is given through the multi_tags argument
			t2 = threading.Thread(target=check_for_id_element, args=(id_tag[0],))
		elif not multi_tags:
			# if not just go about your day.
			t2 = threading.Thread(target=check_for_id_element, args=(id_tag,))
		t1.start() ; t2.start()
		t1.join() ; t2.join()

	if multi_tags: # if we have multiple tags to interact with go here
		if did_find_element:
			if not text_input:
				for id in id_tag:
					browser.find_by_id(id).click()
				browser.find_by_id('nextPageLink').click() # head to the next page
				is_timed_out = False # reset check query
				did_find_element = False # reset check query

	if did_find_element:
		if text_input == True:
			browser.find_by_id(id_tag).fill(textInput_choice)
			browser.find_by_id('nextPageLink').click() # head to next page
			is_timed_out = False # reset check query
			did_find_element = False # reset check query

		elif text_input == False:
			browser.find_by_id(id_tag).click()
			browser.find_by_id('nextPageLink').click() # head to next page
			is_timed_out = False # reset check query
			did_find_element = False # reset check query


def interact_with_css(css_tag, multi_tags=False, text_input=False, textInput_choice=None):
	if not did_quit:
		t1 = threading.Thread(target=timer, args=(20,))
		if multi_tags:
			# use first css_tag if a list is given through the multi_tags argument
			t2 = threading.Thread(target=check_for_css_element, args=(css_tag[0],))
		elif not multi_tags:
			# if not just go about your day.
			t2 = threading.Thread(target=check_for_css_element, args=(css_tag,))
		t1.start() ; t2.start()
		t1.join() ; t2.join()

	if multi_tags: # if we have multiple tags to interact with go here
		if did_find_element:
			if not text_input:
				for class_id in css_tag:
					browser.find_by_css(class_id).click()
				browser.find_by_id('nextPageLink').click() # head to the next page
				is_timed_out = False # reset check query
				did_find_element = False # reset check query

	if did_find_element:
		if text_input == True:
			browser.find_by_css(css_tag).fill(textInput_choice)
			browser.find_by_id('nextPageLink').click() # head to next page
			is_timed_out = False # reset check query
			did_find_element = False # reset check query

		elif text_input == False:
			browser.find_by_css(css_tag).click()
			browser.find_by_id('nextPageLink').click() # head to next page
			is_timed_out = False # reset check query
			did_find_element = False # reset check query


'''
This function just runs all the id tags and css tags through the
interact with method nothing too special
'''
def activate_survey(server_name, digit_code):
	global browser
	global did_quit
	global is_timed_out # check status on timer
	global did_find_element # check status on element location

	did_quit = False
	is_timed_out = False
	did_find_element = False

	# first page of the survey, the 16-digit code =================================
	interact_with_id('promptInput_191744', text_input=True, textInput_choice=digit_code)
	if did_find_element: # element found, fill the details
		if not browser.is_element_not_present_by_text('Sorry that is not a valid answer, please try again'):
			''' INSERT TWILIO ERROR RESPONSE HERE '''
			print('Sorry that is not a valid code, please try again')

	# did you visit x location (second question) ===================================
	interact_with_id('option_423220_198378')
	# how would you rate your experience at Buffalo Wild Wings? (third question) ===================================
	interact_with_css('.option.option_408610_189757.first')
	# reason for visiting Buffalo Wild Wings? (fourth question) ===================================
	interact_with_css('.show-check')
	'''
	still need to program the index functionality inside of interact_with_

	if did_find_element: # element found, fill the details
		# two questions on this exact page
		browser.find_by_css(".show-check")[choice([0,1,2,3,4,5,6,7,8])].click()
		browser.find_by_id(choice(["option_683213_312382", "option_683214_312382"])).click() # selecting bar area. Josh is a bartender
	'''
	# how did you place your order (fifth question) ===================================
	interact_with_id('option_408626_189778')
	# what food/beverage did you order (sixth question) ===================================
	interact_with_css(['.show-check:[%d]' % (choice([0,9,10,11])), '.show-check:[%d]' % (choice([14,15,18,20]))], multi_tags=True)
	# speed of service and overall quality (seventh question) ===================================
	interact_with_css(['.option.option_508973_239500.first',
				'.option.option_508991_239503.first','.option.option_508996_239504.first'], multi_tags=True)


'''
This function sets up the initial options and customizes the settings
for properly connecting to the Tor network
'''
def start_browser():
	global browser
	global digit_code
	global server_name

	emulate_device = [True, False] # to emulate, or not. That is the question

	PROXY = "127.0.0.1:9150" # connect to localhost using the Tor port.
	if emulate_device:
	    # emulate a mobile phone to trick headers
	    # not 100% sure if this even tricks headers, but why not..
		mobile_options = ['iPhone 6', 'iPhone X'] # NEED TO LOOK FOR MORE AVAILABLE DEVICES TO EMULATE ================================
		mobile_emulation = {"deviceName": choice(mobile_options)}

		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--proxy-server=socks5://%s' % PROXY)
		chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--proxy-server=socks5://%s' % PROXY)

	executable_path = {'executable_path':'/path/to/chromedriver'}
	# set headless to False when in development, and True when live
	browser = Browser('chrome', **executable_path, headless=False, options=chrome_options)

	url = 'https://bwwlistens.com'
	browser.visit(url)

	activate_survey(server_name, digit_code)


# this will constantly wait for the variables submitted by text using twilio's api
# for now i have just given temporary values
def main():
	global digit_code
	global server_name
	digit_code = '1421030000861149'
	server_name = 'name'
	jump_to_new_tor_node()
	start_browser()

if __name__ == '__main__':
	main()
