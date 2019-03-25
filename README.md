# SurveyBot
A survey bot aimed to automate Guest Satisfaction Surveys

This specific file goes directly to Buffalo Wild Wings survey online @ https://bwwlistens.com.
The program can be altered ever so slightly to interact with different surveys online, eg. Cheddars, Red Lobster etc.
Currently, the automation is not complete, I've ran out of 16-digit codes to use, so I am in the process of retreiving more
so that I can complete this.

HOW TO USE:
===========
- First off, you're going to need
  1. Tor Browser Bundle. https://www.torproject.org/
  2. Twilio account with API auth_token and Account_sid. https://www.twilio.com/
  3. Ngrok server to connect your local web server to a live public server. https://ngrok.com/
  
- Once all that is setup and ready to go, just run the SurveyBot Code (after you've changed the automation under
"activate_survey(server_name, digit_code)" method and customized it to your needs). 
- The script will start a local web server
on 127.0.0.1:5000. 
- Once that is up, you'll need to start ngrok on the SAME PORT NUMBER. Place your ngrok file on the same
directory as the Script. open a terminal and type "./ngrok http 5000"
- Afterwards you'll want to copy the https link or http link (I prefer the HTTPS, it makes no real difference for this) and
paste it under your webhook for receiving text messages in your twilio account. ( under consoles and phone numbers, in case
you can't find it.) save changes.
- Finally, Once all that is connected and ready to go, test it out by sending a text message. as such "Keanu.1234567890"
of course, the name will be yours, DON'T FORGET THE PERIOD ( THE CODE SPLITS THE VALUES AND SENDS THEM INTO VARIABLES BASED ON
THE PERIOD), and enter your digit code for the survey you need to automate.
HAVE FUN!


Issues:
=======
- some exit nodes through the Tor Network are blocking certain survey websites. There is nothing that can be done about it,
aside from maybe log those specific exit nodes and avoid them for those specific surveys. I won't be doing that, as there is
no immediate need and one ip that may block one survey might not block the other survey or vice versa. I'll leave that 
customization to the user who needs to automate their own survey.


To Do List  - COMPLETED:
========================
1. Configure exit nodes for Tor Network to come straight from U.S. soil, considering that's where these servers
  are located for the guest satisfaction surveys.
2. Finish programming the survey to completion.
3. create a listener function to activate survey automation via Text message.

Things I've learned:
====================
- Multithreading: There was an issue with the bot moving too fast or too slow at times before, and there would end up
  being an infinite loop that would continuously search for an object. There was no way around this without using a 
  keyboard interrupt to stop the process. I need this to be able to run without getting stuck, since I can't keep an eye
  on this 24/7 when running. I was able to use multithreading to split 2 different process to run a countdown timer and
  a check for element function, that would only continuously check for an element so long as the countdown didn't time out.
  
- Proxy Networking with Tor: One big issue I came across was that the survey website wasn't allowing me to send multiple 
surveys through my local connection. It took some time, but I eventually figured out, there was an IP limitation per survey.
I figured I would have to use proxies and knew Tor, routes traffic through nodes all over the world. After alot of digging
through documentation, I was able to find out how to route Splinter/Selenium's browser settings through a proxy and run that
through to tors network.
