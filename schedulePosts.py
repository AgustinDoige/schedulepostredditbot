#!/usr/bin/python
import praw             # Reddit wrapper: https://praw.readthedocs.io
import datetime         # Module to keep track of dates
import pytz             # Module for different timezones
from time import sleep  # This imports a single function that 
import json

def parsedString(string):
	parsed_date = datetime.datetime.strptime(string,'%Y - %m - %d - %I:%M %p')
	return parsed_date.replace(tzinfo=dummydate.tzinfo)

def makePost(sub,titl,selftxt):
	subreddit = reddit.subreddit(sub)
	try:
		with open("old"+sub+"Sticky.txt","r") as g:
			oldSticky = g.read()
		oldsubmission = reddit.submission(id=oldSticky)
		oldsubmission.mod.sticky(state=False)
	except FileNotFoundError:
		pass

	newsubmission = subreddit.submit(titl,selftext=selftxt)
	newsubmission.mod.sticky(state=True)

	with open("old"+sub+"Sticky.txt","w") as g:
		g.write(newsubmission.id)

reddit = praw.Reddit('bot1')
timeZone = 'US/Eastern' # Google "pytz timezones" for other options
dummydate = datetime.datetime.now(tz=pytz.timezone(timeZone)) # This is needed for the .replace(tzinfo=dummydate.tzinfo) method
sleepTime = 3600   #Time (in seconds) the program will wait to loop again

while True:

	try:
		with open("schedule.txt","r") as f:
			dateDictionary = json.load(f)
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
				# First it makes the post on evvthunderbolts
				makePost('botlamptestsub',scheduledSubm['title'],scheduledSubm['selftext']) 
				m1 = "\nMade a post in evvthunderbolts and IndyFuel at <{}>\n".format(currentTime)
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