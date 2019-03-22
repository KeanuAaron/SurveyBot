# SurveyBot
A survey bot aimed to automate Guest Satisfaction Surveys

This specific file goes directly to Buffalo Wild Wings survey online @ https://bwwlistens.com.
The program can be altered ever so slightly to interact with different surveys online, eg. Cheddars, Red Lobster etc.
Currently, the automation is not complete, I've ran out of 16-digit codes to use, so I am in the process of retreiving more
so that I can complete this.

Issues:
=======
- some exit nodes through the Tor Network are blocking https://bwwlistens.com for some reason, not sure if
  it's blocking multiple different survey websites, or whats going on. I haven't had the chance to look into it yet,
  but my guess is that those are overseas servers with content blocking active. I could be wrong


To Do List
==========
1. Configure exit nodes for Tor Network to come straight from U.S. soil, considering that's where these servers
  are located for the guest satisfaction surveys.
2. Finish programming the survey to completion.
3. create a listener function to activate survey automation via Text message.

Things I've learned so far
==========================
- Multithreading: There was an issue with the bot moving too fast or too slow at times before, and there would end up
  being an infinite loop that would continuously search for an object. There was no way around this without using a 
  keyboard interrupt to stop the process. I need this to be able to run without getting stuck, since I can't keep an eye
  on this 24/7 when running. I was able to use multithreading to split 2 different process to run a countdown timer and
  a check for element function, that would only continuously check for an element so long as the countdown didn't time out.
