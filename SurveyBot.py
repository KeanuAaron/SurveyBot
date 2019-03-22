import time
import threading
from random import choice

from stem import Signal
from stem.control import Controller

from splinter import Browser
from selenium import webdriver

from twilio.rest import Client

ACCOUNT_SID = ''
AUTH_TOKEN = ''
client = Client(ACCOUNT_SID, AUTH_TOKEN)

CLIENT_NUMBER = 'users_number'
TWILIO_PHONE_NUMBER = 'twilio_number'
SURVEY_URL = 'https://bwwlistens.com'
CLICK_NEXT_BUTTON = 'nextPageLink'


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
		#print('Browser timed out. Please try again.')
		# send twilio timed out notification
		message = client.messages.create(
			from_=TWILIO_PHONE_NUMBER,
			body="TheSurveyBot has timed out, couldn't find element. Please try agin.",
			to=CLIENT_NUMBER
		)


'''
These check_for functions are made to dependent on the timer using multithreading.
I needed a way to run a timer and to make sure the desired element exists on the page we are on
'''
def check_for_id_element(id_tag):
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

def check_for_css_element(css_tag):
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
The REAL magic happens here.

======= example ========
interact_with_id('promptInput_191744', text_input=True, textInput_choice=list_of_text_queries)
interact_with_id('option_423220_198378', next_page=True) # should ignore text_input and textInput_opts as those are default blank
========================

if id_tag question has to be of a specific index send them in a list as such:
	=======================================================================
	- interact_with_id('id_tag213', is_index_present=True, id_index=4)

	currently index can't be used with multi_tags due to an issue where if
	A = ['noindex_id', 'index_id_of_3', 'index_id_of_13']
	B = [4, 3]

	originally, if I tried to loop through and connect them it would work, however
	in the case where one of the id's doesn't require an index (e.g. A[0]) it would throw
	an error in the automation or choose the wrong one. Looking into this.
	=======================================================================
'''
def interact_with_id(id_tag, is_index_present=False, id_index=None, multi_tags=False, text_input=False, textInput_choice=None, next_page=True):
	global did_find_element
	global is_timed_out
	global browser

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

	if is_index_present:
		if did_find_element:
			if not text_input:
				browser.find_by_id(id_tag)[id_index].click()
				#browser.find_by_id(CLICK_NEXT_BUTTON).clic() # head to the next page
				is_timed_out = False # reset check query
				did_find_element = False # reset check query

	if multi_tags: # if we have multiple tags to interact with go here
		if did_find_element:
			if not text_input:
				for id_name in id_tag:
					browser.find_by_id(id_name).click()
				#browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to the next page
				is_timed_out = False # reset check query
				did_find_element = False # reset check query

	if did_find_element and not is_index_present:
		if text_input == True:
			browser.find_by_id(id_tag).fill(textInput_choice)
			#browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to next page
			is_timed_out = False # reset check query
			did_find_element = False # reset check query

		elif text_input == False:
			browser.find_by_id(id_tag).click()
			#browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to next page
			is_timed_out = False # reset check query
			did_find_element = False # reset check query
	if next_page:
		browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to next page


def interact_with_css(css_tag, is_index_present=False, css_index=None, multi_tags=False, text_input=False, textInput_choice=None, next_page=True):
	global did_find_element
	global is_timed_out
	global browser
	
	if not did_quit:
		t1 = threading.Thread(target=timer, args=(20,))
		if multi_tags:
			# use first id_tag if a list is given through the multi_tags argument
			t2 = threading.Thread(target=check_for_css_element, args=(css_tag[0],))
		elif not multi_tags:
			# if not just go about your day.
			t2 = threading.Thread(target=check_for_css_element, args=(css_tag,))
		t1.start() ; t2.start()
		t1.join() ; t2.join()

	if is_index_present:
		if did_find_element:
			if not text_input:
				browser.find_by_css(css_tag)[css_index].click()
				#browser.find_by_id(CLICK_NEXT_BUTTON).clic() # head to the next page
				is_timed_out = False # reset check query
				did_find_element = False # reset check query

	if multi_tags: # if we have multiple tags to interact with go here
		if did_find_element:
			if not text_input:
				for css_name in css_tag:
					browser.find_by_css(css_name).click()
				#browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to the next page
				is_timed_out = False # reset check query
				did_find_element = False # reset check query

	if did_find_element and not is_index_present:
		if text_input == True:
			browser.find_by_css(css_tag).fill(textInput_choice)
			#browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to next page
			is_timed_out = False # reset check query
			did_find_element = False # reset check query

		elif text_input == False:
			browser.find_by_css(css_tag).click()
			#browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to next page
			is_timed_out = False # reset check query
			did_find_element = False # reset check query
	if next_page:
		browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to next page


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
	interact_with_id('promptInput_191744', text_input=True, textInput_choice=digit_code, next_page=True)
	if did_find_element: # element found, fill the details
		if browser.is_element_not_present_by_text('Sorry that is not a valid answer, please try again') == False: # isn't catching error.
			message = client.messages.create(
				from_=TWILIO_PHONE_NUMBER,
				body="Sorry, the digit code you have entered has already been used, or typed incorrectly. Please try agin.",
				to=CLIENT_NUMBER
			)
			print('Sorry that is not a valid code, please try again')

	# did you visit x location (second question) ===================================
	interact_with_id('option_423220_198378', next_page=True)
	# how would you rate your experience at Buffalo Wild Wings? (third question) ===================================
	interact_with_css('.option.option_408610_189757.first', next_page=True)
	# reason for visiting Buffalo Wild Wings? (fourth question) ===================================
	interact_with_css('.show-check', is_index_present=True, css_index=choice([0,1,2,3,4,5,6,7,8]), next_page=False)
	interact_with_id(choice(["option_683213_312382", "option_683214_312382"]), next_page=True) # selecting bar area.
	# how did you place your order (fifth question) ===================================
	interact_with_id('option_408626_189778', next_page=True)
	# what food/beverage did you order (sixth question) ===================================
	interact_with_css('.show-check', is_index_present=True, css_index=choice([0,9,10,11]), next_page=False)
	interact_with_css('.show-check', is_index_present=True, css_index=choice([14,15,18,20]), next_page=True)
	# speed of service and overall quality (seventh question) ===================================
	interact_with_css(['.option.option_508973_239500.first',
				'.option.option_508991_239503.first','.option.option_508996_239504.first'], multi_tags=True, next_page=True)


'''
This function sets up the initial options and customizes the settings
for properly connecting to the Tor network
'''
def start_browser():
	global browser
	global digit_code
	global server_name

	emulate_device = choice([True, False]) # to emulate, or not. That is the question

	PROXY = "127.0.0.1:9150" # connect to localhost using the Tor port.
	if emulate_device:
	    # emulate a mobile phone to trick headers
	    # not 100% sure if this even tricks headers, but why not..
		mobile_options = ['iPhone 6', 'iPhone 7', 'iPhone 8', 'iPhone X'] # NEED TO LOOK FOR MORE AVAILABLE DEVICES TO EMULATE ================================
		mobile_emulation = {"deviceName": choice(mobile_options)}

		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--proxy-server=socks5://%s' % PROXY)
		chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

	chrome_options = webdriver.ChromeOptions()
	chrome_options.add_argument('--proxy-server=socks5://%s' % PROXY)

	executable_path = {'executable_path':'/path/to/chromedriver'}
	# set headless to False when in development, and True when live
	browser = Browser('chrome', **executable_path, headless=False, options=chrome_options)
	browser.visit(SURVEY_URL)

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
