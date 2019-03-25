import time
import datetime
import threading
from random import choice

from stem import Signal
from stem.util import term
from stem.control import Controller

import splinter
from splinter import Browser
from selenium import webdriver

from flask import Flask, request
from twilio.rest import Client

ACCOUNT_SID = 'TWILIO_ACCOUNT_SID'
AUTH_TOKEN = 'TWILIO_AUTH_TOKEN'
client = Client(ACCOUNT_SID, AUTH_TOKEN)

CLIENT_NUMBER = '+11234567890' # users number
TWILIO_PHONE_NUMBER = '+11234567890' # number from twilio account a.k.a. the bot.
SURVEY_URL = 'https://redlobstersurvey.com'
CLICK_NEXT_BUTTON = 'NextButton'

app = Flask(__name__)


''' this function is created so that we can jump around the tor networks to bypass ip limiting
from the survey... we want to be able to automate as many surveys as possible..
let's break the limits!!!!
'''
def jump_to_new_tor_node():
	with Controller.from_port(port = 9151) as controller:
		controller.authenticate()
		controller.set_options({
		  'ExitNodes': '{US}' # 'ExitNodes': '{US}, {CA}, {RU}' # more exit nodes to use.
		})
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

def check_for_text_element(text_tag):
	global browser
	global is_timed_out
	global did_find_element

	while True:
		if is_timed_out: # break loop if timed out
			break
		try:
			if browser.find_by_text(text_tag):
				did_find_element = True
				break # break loop if element is found
			elif not browser.find_by_text(text_tag):
				did_find_element = False
		except: pass


'''
The REAL magic happens here.

======= example ========
interact_with_id('promptInput_191744', text_input=True, textInput_choice=list_of_text_queries)
interact_with_id('option_423220_198378', next_page=True) # should ignore text_input and textInput_choice as those are default blank
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

	if is_index_present and did_find_element and not text_input:
		browser.find_by_id(id_tag)[id_index].click()
		is_timed_out = False # reset check query
		did_find_element = False # reset check query

	if not is_index_present and did_find_element and text_input:
		browser.find_by_id(id_tag).click()
		browser.find_by_id(id_tag).type(textInput_choice)
		is_timed_out = False # reset check query
		did_find_element = False # reset check query

	if multi_tags and did_find_element and not text_inputs: # if we have multiple tags to interact with go here
		for id_name in id_tag:
			browser.find_by_id(id_name).click()
		is_timed_out = False # reset check query
		did_find_element = False # reset check query

	if did_find_element and not is_index_present and not text_input:
		browser.find_by_id(id_tag).click()
		is_timed_out = False # reset check query
		did_find_element = False # reset check query

	if next_page:
		browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to next page
		time.sleep(1)


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

	if is_index_present and did_find_element and not text_input:
		browser.find_by_css(css_tag)[css_index].click()
		#browser.find_by_id(CLICK_NEXT_BUTTON).clic() # head to the next page
		is_timed_out = False # reset check query
		did_find_element = False # reset check query

	if not is_index_present and did_find_element and text_input:
		browser.find_by_css(css_tag).click()
		browser.find_by_css(css_tag).type(textInput_choice)
		is_timed_out = False # reset check query
		did_find_element = False # reset check query

	if multi_tags and did_find_element and not text_inputs: # if we have multiple tags to interact with go here
		for css_name in css_tag:
			browser.find_by_css(css_name).click()
		is_timed_out = False # reset check query
		did_find_element = False # reset check query

	if did_find_element and not is_index_present and not text_input:
		browser.find_by_css(css_tag).click()
		#browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to next page
		is_timed_out = False # reset check query
		did_find_element = False # reset check query

	if next_page:
		browser.find_by_css(CLICK_NEXT_BUTTON).click() # head to next page
		time.sleep(1)

def interact_with_text(text_tag, next_page=True):
	global did_find_element
	global is_timed_out
	global browser

	if not did_quit:
		t1 = threading.Thread(target=timer, args=(20,))
		if multi_tags:
			# use first id_tag if a list is given through the multi_tags argument
			t2 = threading.Thread(target=check_for_text_element, args=(text_tag[0],))
		elif not multi_tags:
			# if not just go about your day.
			t2 = threading.Thread(target=check_for_text_element, args=(text_tag,))
		t1.start() ; t2.start()
		t1.join() ; t2.join()

	if did_find_element:
		browser.find_by_text(text_tag).click()
		is_timed_out = False # reset check query
		did_find_element = False # reset check query

	if next_page:
		browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to next page
		time.sleep(1)

def interact_with_select(id_tag, is_index_present=False, id_index=None, next_page=True):
	global did_find_element
	global is_timed_out
	global browser

	if not did_quit:
		t1 = threading.Thread(target=timer, args=(20,))
		t2 = threading.Thread(target=check_for_id_element, args=(id_tag,))
		t1.start() ; t2.start()
		t1.join() ; t2.join()

	if is_index_present and did_find_element:
		browser.select(id_tag, id_index)
		is_timed_out = False # reset check query
		did_find_element = False # reset check query

	if next_page:
		browser.find_by_id(CLICK_NEXT_BUTTON).click() # head to next page
		time.sleep(1)


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
	current_time = datetime.datetime.now().time() # depending on time this will choose the proper response.
	current_time = str(current_time)

	exp_comment_list = [
		"{server} was extremely knowledgable and very kind! Great experience".format(server=server_name),
		"Everything was great and beyond my expectations, I had the lobster in paradise, recommended by {server} for my husband and I anniversary. Food was amazing.".format(server=server_name),
		"So many choices! {server} was extremely helpful in helping us come to a decision based on our needs. I'm extremely critical lol.".format(server=server_name),
		"{server} was very fast and professional. {server} was not only helping out with us, but I saw {server} numerous times helping other tables and servers. Truly helped our experience to have a server like {server}!".format(server=server_name),
		"Everything was great. Thanks {server}!".format(server=server_name),
		"I like to go to restaurants and test the knowledge of the servers, and WOW {server} really knew their stuff!".format(server=server_name),
		"I came to have a nice meal with my family and that is exactly what I got and more. 10/10. Oh, {server} you're awesome!".format(server=server_name)
	]
	likely_to_return = [
		"Of course I'll return, red lobster is my favorite restaurant!", "Yes, I'll gladly be back with friends and family",
		"Very likely, great service, great food, great experience overall.", "duh! of course i'll be back!!!!!",
		"you'll all definitely see me again. for sure!", "FAVORITE restaurant, I'll be back!"
	]

	# digit code section is split off by 3 'id''s. so we have to split up the digit_code
	digit_first = digit_code[:4]
	digit_second = digit_code[4:9]
	digit_third = digit_code[9:]
	message = client.messages.create(
		from_=TWILIO_PHONE_NUMBER,
		body="Starting survey. Please hold for response.",
		to=CLIENT_NUMBER
	)
	
	'''
	THE REST OF THE CODE FROM HERE TO THE END OF THE ACTIVATE_SURVEY METHOD IS JUST TO 
	SHOW AS AN EXAMPLE OF HOW THIS CODE AND METHODS ACTUALLY WORK, AND HOW YOU CAN 
	UTILIZE THE METHODS ABOVE TO MAKE IT WORK FOR YOUR SURVEY OR ANY OTHER SURVEY.
	'''
	try: # try loop to watch out for Errors
		interact_with_id('CN1', text_input=True, textInput_choice=digit_first, next_page=False)
		interact_with_id('CN2', text_input=True, textInput_choice=digit_second, next_page=False)
		interact_with_id('CN3', text_input=True, textInput_choice=digit_third, next_page=True)
		print(term.format('Code Valid. Entering survey questionaire.', term.Color.GREEN))

		# Lunch Dinner or Other Randomization (first question) =========================================
		'''
		want this to depend on the current time of activation
		'''
		if int(current_time[:2]) <= 15:
			meal_of_day = 'Lunch'
		elif int(current_time[:2]) > 15 and int(current_time[:2]) <= 24:
			meal_of_day = 'Dinner'
		# second question ==============================================================================
		#interact_with_text(choice(['Lunch','Dinner','Other']), next_page=True)
		interact_with_text(meal_of_day, next_page=True)
		print(term.format("[ + ] 1/28.", term.Color.BLUE))
		# third question ===============================================================================
		interact_with_text('Dine In', next_page=True)
		print(term.format('[ + ] 2/28.', term.Color.BLUE))

		# this is what time you were there. once again I want to depend upon time of activation
		# before 3, between 3 & 6, or after 6. (fourth question) =======================================
		#time_of_visit = choice(['Before 3:00 pm ','Between 3:00 pm and 6:00 pm ','After 6:00 pm'])
		if int(current_time[:2]) <= 15:
			time_of_visit = ('Before 3:00 pm ')
		elif int(current_time[:2]) > 15 and int(current_time[:2]) <= 18:
			time_of_visit = ('Between 3:00 pm and 6:00 pm ')
		elif int(current_time[:2]) > 18 and int(current_time[:2]) <= 24:
			time_of_visit = ('After 6:00 pm')

		interact_with_text(time_of_visit, next_page=True)
		print(term.format("[ + ] 3/28.", term.Color.BLUE))

		# where were you seated (fifth question) =======================================================
		interact_with_text('Dining room', next_page=True)
		print(term.format('[ + ] 4/28.', term.Color.BLUE))
		# overall how would you rate experience ? (sixth question) =====================================
		interact_with_css(choice(['.Opt5.inputtyperbloption','.Opt5.inputtyperbloption']), next_page=True)
		print(term.format('[ + ] 5/28.', term.Color.BLUE))

		time.sleep(2) # (seventh question) these have no other unique classes or tags ==================
		interact_with_css('.radioBranded', is_index_present=True, css_index=choice([0,1]), next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=choice([5,6]), next_page=True)
		print(term.format('[ + ] 6/28.', term.Color.BLUE))

		# how long did you wait to be seated (eighth question) =========================================
		interact_with_text(choice(['Did not wait']), next_page=True)
		print(term.format('[ + ] 7/28.', term.Color.BLUE))
		#interact_with_text('About the quoted time', next_page=True)

		time.sleep(2)
		interact_with_css('.radioBranded', is_index_present=True, css_index=0, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=6, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=11, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=16, next_page=True)
		print(term.format('[ + ] 8/28.', term.Color.BLUE))
		time.sleep(2)
		interact_with_css('.radioBranded', is_index_present=True, css_index=0, next_page=True)
		print(term.format('[ + ] 9/28.', term.Color.BLUE))
		time.sleep(2)
		interact_with_css('.radioBranded', is_index_present=True, css_index=0, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=5, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=10, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=15, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=20, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=25, next_page=True)
		print(term.format('[ + ] 10/28.', term.Color.BLUE))
		time.sleep(2)
		interact_with_css('.radioBranded', is_index_present=True, css_index=0, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=5, next_page=True)
		print(term.format('[ + ] 11/28.', term.Color.BLUE))
		time.sleep(2)
		interact_with_css('.radioBranded', is_index_present=True, css_index=1, next_page=True)
		print(term.format('[ + ] 12/28.', term.Color.BLUE))
		time.sleep(2)
		interact_with_css('.radioBranded', is_index_present=True, css_index=0, next_page=True)
		print(term.format('[ + ] 13/28.', term.Color.BLUE))
		time.sleep(2)
		interact_with_css('.radioBranded', is_index_present=True, css_index=0, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=5, next_page=True)
		print(term.format('[ + ] 14/28.', term.Color.BLUE))

		# how was your experience
		exp_comment = choice(exp_comment_list)
		interact_with_id('S80000', text_input=True, textInput_choice=exp_comment, next_page=True)
		print(term.format('[ + ] Interacted with TextArea. 15/28.', term.Color.BLUE))
		# this is how likely are you to return. 1200 characters max (including spaces).
		return_comment = choice(likely_to_return)
		interact_with_id('S00020', text_input=True, textInput_choice=choice(likely_to_return), next_page=True)
		print(term.format('[ + ] 16/28.', term.Color.BLUE))

		interact_with_css('.radioBranded', is_index_present=True, css_index=choice([1,2,3,4]), next_page=True)
		print(term.format('[ + ] 17/28.', term.Color.BLUE))

		print('STARTING CHECK BOX PAGE')
		interact_with_css('.checkboxBranded', is_index_present=True, css_index=choice([1,2,3,4,5,6,7,8,9,10,11]), next_page=True)
		print('JUST LEFT CHECKBOX PAGE')
		print(term.format('[ + ] 18/28.', term.Color.BLUE))

		#interact_with_css('.radioBranded', is_index_present=True, css_index=choice([0]), next_page=True)
		#print(term.format('[ + ] 19/28.', term.Color.BLUE))
		print('SHOULD BE THE THREE QUESTIONS NOW')
		interact_with_css('.radioBranded', is_index_present=True, css_index=0, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=2, next_page=False)
		interact_with_css('.radioBranded', is_index_present=True, css_index=4, next_page=True)
		print(term.format('[ + ] 19/28.', term.Color.BLUE))

		interact_with_css('.radioBranded', is_index_present=True, css_index=choice([0,1,2,3]), next_page=True)
		print(term.format('[ + ] 20/28.', term.Color.BLUE))

		interact_with_css('.radioBranded', is_index_present=True, css_index=choice([0,1,2,3]), next_page=True)
		print(term.format('[ + ] 21/28.', term.Color.BLUE))

		interact_with_css('.radioBranded', is_index_present=True, css_index=choice([0,1,2,3]), next_page=True)
		print(term.format('[ + ] 22/28.', term.Color.BLUE))

		interact_with_text('I am aware, and have downloaded  the App', next_page=True)
		print(term.format('[ + ] Interated with Red Lobster Rewards Segment. 23/28.', term.Color.BLUE))

		interact_with_text('Excellent', next_page=True)
		print(term.format('[ + ] 24/28.', term.Color.BLUE))
		#interact_with_css('.radioBranded', is_index_present=True, css_index=choice([0,1,2,3]), next_page=True)

		# select boxes for personal information.. gross...
		interact_with_select('R54000', is_index_present=True, id_index=choice(['1','2','8']), next_page=False)
		interact_with_select('R55000', is_index_present=True, id_index=choice(['1','2','3','4','5','6','7','8']), next_page=False)
		interact_with_select('R56000', is_index_present=True, id_index=choice(['1','2','3','4','5','6','7','8']), next_page=True)
		print(term.format('[ + ] 25/28.', term.Color.BLUE))

		# ethnicity... gross more data siphoning....
		interact_with_css('.checkboxBranded', is_index_present=True, css_index=3, next_page=True)
		print(term.format('[ + ] 26/28.', term.Color.BLUE))

		# do you want to join the sweepstakes?
		# no because we would have to generate fake emails and info anyways and theres no point just pointless code....
		interact_with_css('.radioBranded', is_index_present=True, css_index=1, next_page=True)
		print(term.format('[ + ] 27/28.', term.Color.BLUE))

		# congrats the survey is completed now... we can move on..
		t1 = threading.Thread(target=timer, args=(20,))
		t2 = threading.Thread(target=check_for_text_element, args=('THANKS FOR YOUR FEEDBACK',))
		t1.start() ; t2.start()
		t1.join() ; t2.join()
		if did_find_element == True:
			print(term.format('[ + ] Survey Completed and final "Thank You" has been found! 28/28.', term.Color.GREEN))
			message = client.messages.create(
				from_=TWILIO_PHONE_NUMBER,
				body="Thank you for using TheSurveyBot! Your survey has been automated and complete. See you soon! ",
				to=CLIENT_NUMBER
			)
		browser.quit()
		jump_to_new_tor_node()
		return 'success'
	except Exception as e:
		browser.quit()
		print(term.format(str(e), term.Color.RED))
		message = client.messages.create(
			from_=TWILIO_PHONE_NUMBER,
			body="Caught an unexpected Error. Bot must me moving too fast. Try again, or optimize code.",
			to=CLIENT_NUMBER
		)
		return 'failure'


'''
This function sets up the initial options and customizes the settings
for properly connecting to the Tor network
'''
def start_browser():
	global browser
	global digit_code
	global server_name

	emulate_device = choice([False, False]) # to emulate, or not. That is the question

	PROXY = "127.0.0.1:9150" # connect to localhost using the Tor port.
	'''
	====================================================================================
	WHEN EMULATING A DEVICE THE PROGRAM ISN'T CLICKING THE NEXT BUTTON. LOOKING INTO IT.
	====================================================================================

	if emulate_device:
	    # emulate a mobile phone to trick headers
	    # not 100% sure if this even tricks headers, but why not..
		mobile_options = ["iPhone 6", "iPhone 7", "iPhone 8", "iPhone X"] # NEED TO LOOK FOR MORE AVAILABLE DEVICES TO EMULATE ================================
		mobile_emulation = {"deviceName": choice(mobile_options)}

		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument("--proxy-server=socks5://%s" % PROXY)
		chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
	'''

	if not emulate_device: # no mobile emulation
		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument("--proxy-server=socks5://%s" % PROXY)

	executable_path = {'executable_path':'/Users/Keanu/Desktop/SurveyBot/RedLobster/chromedriver'}
	# set headless to False when in development, and True when live
	browser = Browser('chrome', **executable_path, headless=False, options=chrome_options)
	browser.visit(SURVEY_URL)

	activate_survey(server_name, digit_code)


# this will constantly wait for the variables submitted by text using twilio's api
# for now i have just given temporary values
@app.route('/sms', methods=['POST'])
def main():
	global digit_code
	global server_name
	server_name, digit_code = request.form['Body'].split('.')
	#server_name = 'Keanu'
	#digit_code = '3032723638279'
	jump_to_new_tor_node()
	start_browser()

if __name__ == '__main__':
	app.run()
