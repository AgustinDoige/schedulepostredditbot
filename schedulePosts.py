#!/usr/bin/python
import praw             # Reddit wrapper: https://praw.readthedocs.io
import datetime         # Module to keep track of dates
import pytz             # Module for different timezones
from time import sleep  # This imports a single function that tells the program to wait (sleep) for a while
import json             # Module for saving a dictionary following a known standard

def parsedString(string):
	"""This is a function that takes a string and creates a aware datetime."""
	parsed_date = datetime.datetime.strptime(string,'%Y - %m - %d - %I:%M %p')
	return parsed_date.replace(tzinfo=dummydate.tzinfo)

def makePost(sub,titl,selftxt):
	"""This function makes a post with title:titl and selftext:selftxt on the subreddit:sub
		It also stickies that submission and unstickies the previous sub that IT stickied. It does nothing to 
		submissions that it did not post"""
	subreddit = reddit.subreddit(sub)
	try:
		# This tries to unstick the previous submission that the bot made sticky
		with open("old"+sub+"Sticky.txt","r") as g:
			oldSticky = g.read()
		oldsubmission = reddit.submission(id=oldSticky)
		oldsubmission.mod.sticky(state=False)
	except FileNotFoundError:
		pass

	newsubmission = subreddit.submit(titl,selftext=selftxt) #This makes the post
	newsubmission.mod.sticky(state=True) # This makes it sticky

	with open("old"+sub+"Sticky.txt","w") as g:
		# This saves the post's ID so it can unsticky it in the future
		g.write(newsubmission.id) 

reddit = praw.Reddit('bot1')
timeZone = 'US/Eastern' # Google "pytz timezones" for other options
dummydate = datetime.datetime.now(tz=pytz.timezone(timeZone)) # This is needed for the .replace(tzinfo=dummydate.tzinfo) method
sleepTime = 3600   #Time (in seconds) the program will wait to loop again

while True:
	try:
		with open("schedule.txt","r") as f:
			#This loads the json dictionary
			dateDictionary = json.load(f) # If the console says there's an error here then the format of the file was probably messed up
	except FileNotFoundError:
		print("Error. File 'schedule.txt' not found.")
		raise FileNotFoundError

	currentTime = datetime.datetime.now(tz=pytz.timezone(timeZone)) # Gets current time on chosen timezone
	foundadate = False
	for scheduledSubm in dateDictionary['Dates']: # Starts a loop that goes through every date
		if scheduledSubm['announced'] == False:   #Checks if a date was already posted. If it was, it goes to the next
			schDate = parsedString(scheduledSubm['date'])
			#Gets a delta which is how far away from now is the scheduled date. Positive means future. Negative means past.
			delta = schDate - currentTime  
			totalSec = delta.total_seconds()
			if (totalSec < 0):
				foundadate = True
				# If an unannounced date has already passed, it means that it must have just passed moments ago. 
				# So it means it's now time to make the post
				if scheduledSubm['for_evansville'] == True:
					makePost('evvthunderbolts',scheduledSubm['title'],scheduledSubm['selftext']) 
					m1 = "\nMade a post in evvthunderbolts at <{}>\n".format(currentTime)
					m2 = "With title: <{}>\n".format(scheduledSubm['title'])
					m3 = "Selftext: <{}>\n\n".format(scheduledSubm['selftext'])
				else:
					makePost('IndyFuel',scheduledSubm['title'],scheduledSubm['selftext']) 
					m1 = "\nMade a post in IndyFuel at <{}>\n".format(currentTime)
					m2 = "With title: <{}>\n".format(scheduledSubm['title'])
					m3 = "Selftext: <{}>\n\n".format(scheduledSubm['selftext'])
		
				print(m1+m2+m3) # This is just a message for the console to see if the post was made
				scheduledSubm['announced'] = True
	if (foundadate == False):
		# If no date has passed in this check, it just tells that it checked it at what time.
		print("Checked for scheduled announcements at ",currentTime)

	# Finally, this just saves the dictionary in case a date was posted, so it doesn't post it more than once
	with open("schedule.txt","w") as h:
		json.dump(dateDictionary,h,indent=2)

	sleep(sleepTime) # This commands tells the program to wait for a while to do the loop again.