#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  room_booker.py
#  
#  rodericd5
#  
#  created 12/24/2017 

import time
import os.path
from datetime import datetime
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
import re
import urllib2
import imaplib
import email

UCSB_ADD = "@umail.ucsb.edu"
FORTNIGHT = 14
IMTP_ADD = "outlook.office365.com"
IMTP_PORT = 993
HARDCODED_DRIVER_LOCATION = '*****'

#enters if file does not already exist and prompts user to enter necessary info to run program
if (os.path.isfile('library_room.txt') == False):
	f = open('library_room.txt', 'w')
	for k in range(5):
	
		timeframe = raw_input("Please enter\n11 to book 11-1\n1 to book 1-3\n 3 to book 3-5\n 5 to book 5-7\n or 7 to book 7-9\n")
		timeframe_check = raw_input("Please enter the number again to confirm: ")
		while (timeframe != timeframe_check):
			print "Error the two numbers do not match. Please try again\n"
			timeframe = raw_input("Please enter\n11 to book 11-1\n1 to book 1-3\n 3 to book 3-5\n 5 to book 5-7\n or 7 to book 7-9\n")
			timeframe_check = raw_input("Please enter the number again to confirm: ")
		
		login_id_noadd = raw_input("Please enter your Net ID (without the .umail extension): ")
		login_id_noadd_check = raw_input("Please enter your Net ID again to confirm: ")
		while (login_id_noadd != login_id_noadd_check):
			print "Error the two Net ID's do not match. Please try again\n"
			login_id_noadd = raw_input("Please enter your Net ID (without the umail extension): ")
			login_id_noadd_check = raw_input("Please enter your Net ID again to confirm: ")
		
		login_pwd = raw_input("Please enter your Net ID password: ")
		login_pwd_check = raw_input("Please enter your password again to confirm: ")
		while (login_pwd != login_pwd_check):
			print "Error the two passwords do not match. Please try again\n"
			login_pwd = raw_input("Please enter your Net ID password: ")
			login_pwd_check = raw_input("Please enter your password again to confirm: ")
	
		#write the answers to the prompts line by line 
		f.write(timeframe + '\n')
		f.write(login_id_noadd + '\n')
		f.write(login_pwd + '\n')
		if (k == 5):
			f.close()
			
#opens file with necessary information		
f = open('library_room.txt', 'r')
	
for k in range(5):
		
	#reads first line which determines times to book (need to get rid of '\n' character)
	timeframe = f.readline()
	timeframe = int(timeframe.rstrip('\n'))

	#reads second line which is the Net ID (need to get rid of '\n' character)
	login_id_noadd = f.readline()
	login_id_noadd = login_id_noadd.rstrip('\n')

	#reads third line which is the users login password (need to get rid of '\n' character)
	login_pwd = f.readline()
	login_pwd = login_pwd.rstrip('\n')


	#set the login id for the logging into email
	email_login_id = login_id_noadd + UCSB_ADD

	#initialize our driver called web and use chrome to open up library booking link
	web = webdriver.Chrome(HARDCODED_DRIVER_LOCATION)
	web.get("http://libcal.library.ucsb.edu/rooms.php?i=12405")

	#Note: The wait times were implemented merely to ensure that everything loaded before
	#searching through the html file for data
	web.implicitly_wait(0.5)

	#get the current date from an xpath it is already in a better form to
	#create a datetime object
	current_date = web.find_element_by_xpath('//*[@id="s-lc-rm-tg-h"]')
	current_date = current_date.get_attribute('innerHTML')
	print "Today's day is currently: " + current_date + "\n"

	#split the date and create a modified date in a format that will be used 
	#to create a datetime object in the form Month day Year
	mod_date = current_date.split(",",1)[1]
	mod_date = mod_date.strip()
	mod_date = mod_date.replace(',','')

	#create the datetime object by passing mod_date into the string parse
	#time function with the form Month day Year
	mod_datetime = datetime.strptime(mod_date,'%B %d %Y')

	#initialize the day of reference. This is important, because every number
	#on the reservation grid is determined based on the numbers found on this
	#day in the html file
	day_reference = datetime(2018,01,17)

	#the difference in days between the current day and the day of reference
	#datetime objects will allow us to determine how many days it has been
	#and thus how much to multiply each value by
	numday_difference = mod_datetime - day_reference
	numday_difference_str = str(numday_difference)
	numday_difference_str = numday_difference_str.split(' ',1)[0]

	#convert how many days it has been since the day of reference to an int
	#for calculations later
	numday_difference_int = int(numday_difference_str)

	#dt is initialized to 14 days in advance (the soonest we can reserve a 
	#room) and then it is added to the current day
	dt = timedelta(days=FORTNIGHT)
	mod_datetime = mod_datetime + dt


	#these values are the initial values assigned to the grids in the html
	#on Dec 30 2017 which is the day of reference. From here it is simply
	#a matter of adding a multiple that was determined to be 816
	if timeframe == 11:
		numdiff = 600893789
	elif timeframe == 1:
		numdiff = 600893793
	elif timeframe == 3:
		numdiff = 600893797
	elif timeframe == 5:
		numdiff = 600893801
	elif timeframe == 7:
		numdiff = 600893805
	else:
		raise ValueError('a proper timeframe was not read from the file')
	
	#perform basic arithmetic and cast as strings to later use when searching
	#xpath to decide what grid boxes to click 
	difference_factor = numdiff + (numday_difference_int+FORTNIGHT)*816
	difference_factor1 = str(difference_factor)
	difference_factor2 = str(difference_factor+1)
	difference_factor3 = str(difference_factor+2)
	difference_factor4 = str(difference_factor+3)

	#go back to creating a datetime object of the day we are supposed to be 
	#booking (14 days in advance)
	mod_date = datetime.strftime(mod_datetime, '%b %d %Y')
	print "Attempting to book a room on " + mod_date + "..\n"

	#gather the month
	month = mod_date.split(" ",3)[0]

	#gather the day (removing any leading 0's because that does not follow
	#the format that will later be used when searching xpath
	day = mod_date.split(" ",3)[1]
	day = day.lstrip('0')

	#gather the year
	year = mod_date.split(" ",3)[2]

	#basic if statements checking so as not to reserve when unnecessary and
	#because often days are unavailable for booking when school is not in 
	#session 
	if (month == 'Jan' and day < '16' and year == '2018'):
		raise ValueError(month + ' ' + day + ' ' + year + ' is not an academic day')
	elif (month == 'Feb' and day == '19' and year == '2018'):
		raise ValueError(month + ' ' + day + ' ' + year + ' is not an academic day')
	elif (month == 'Mar' and day > '22' and year == '2018'):
		raise ValueError(month + ' ' + day + ' ' + year + ' is not an academic day')
	elif (month == 'May' and day == '28' and year == '2018'):
		raise ValueError(month + ' ' + day + ' ' + year + ' is not an academic day')
	elif (month == 'Jun' and day > '14' and year == '2018'):
		raise ValueError(month + ' ' + day + ' ' + year + ' is not an academic day')
	elif (month == 'Jul' or month == 'Aug'):
		raise ValueError(month + ' ' + day + ' ' + year + ' is not an academic day')
	elif (month == 'Sep' and day < '24' and year == '2018'):
		raise ValueError(month + ' ' + day + ' ' + year + ' is not an academic day')
	elif (month == 'Nov' and (day == '12' or day == '22' or day == '23') and year == '2018'):
		raise ValueError(month + ' ' + day + ' ' + year + ' is not an academic day')

	#prepare a wait to ensure everything is clicked
	wait = WebDriverWait(web, 10)

	#click the month and then the day of the month that we will be booking
	reserve_month = web.find_element_by_xpath("//*[text()[contains(., '"+ month +"')]]")
	reserve_month.click()
	time.sleep(0.5)
	reserve_date = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@class='ui-state-default'][text()[contains(.,'"+ day +"')]]")))
	reserve_date.click()
	time.sleep(2)

	#perform all of the bookings using our difference factors
	#by clicking on the timegrids at predetermined locations
	book1 = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='"+ difference_factor1 +"']")))
	book1.click()
	time.sleep(0.3)
	book2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='"+ difference_factor2 +"']")))
	book2.click()
	time.sleep(0.3)
	book3 = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='"+ difference_factor3 +"']")))
	book3.click()
	time.sleep(0.3)
	book4 = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id='"+ difference_factor4 +"']")))
	book4.click()


	#click continue
	cont = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="rm_tc_cont"]')))
	cont.click()

	#click submit
	submit = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="s-lc-rm-sub"]')))
	submit.click()
	time.sleep(0.7)

	#enter login credentials and click login
	username = wait.until(EC.presence_of_element_located((By.ID, "username")))
	password = web.find_element_by_id("password")
	username.send_keys(login_id_noadd)
	password.send_keys(login_pwd)
	log = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="fm1"]/section[3]/input[4]')))
	log.click()

	#enter group name and submit the booking
	group_name = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="nick"]')))
	group_name.send_keys('CS nerds')
	sub_booking = wait.until(EC.element_to_be_clickable((By.XPATH,'//*[@id="s-lc-rm-sub"]')))
	time.sleep(0.7)
	sub_booking.click()

#wait for the booking to send an email and then execute the following code
#after 5 minutes 
f.close()
print "Waiting 2 minutes to ensure that confirmation email is sent and then accessing it..." 
time.sleep(120)


#opens file with necessary information		
f = open('library_room.txt', 'r')

for k in range(5):
	#reads first line which determines times to book (need to get rid of '\n' character)
	timeframe = f.readline()
	timeframe = int(timeframe.rstrip('\n'))

	#reads second line which is the Net ID (need to get rid of '\n' character)
	login_id_noadd = f.readline()
	login_id_noadd = login_id_noadd.rstrip('\n')

	#reads third line which is the users login password (need to get rid of '\n' character)
	login_pwd = f.readline()
	login_pwd = login_pwd.rstrip('\n')


	#set the login id for the logging into email
	email_login_id = login_id_noadd + UCSB_ADD
	try:
		#open up a mail session with our IMTP_ADD and login then look at inbox
		mail = imaplib.IMAP4_SSL(IMTP_ADD)
		mail.login(email_login_id, login_pwd)
		mail.select('inbox')
	
		#search through all of the mail 
		type, data = mail.search(None, 'ALL')
		mail_ids = data[0]
	
		#make a list of the mail ids and assign the first (oldest) and latest
		#emails
		id_list = mail_ids.split()   
		first_email_id = int(id_list[0])
		latest_email_id = int(id_list[-1])

		#iterate through the most recent couple of emails to see if it came
		for i in range(latest_email_id,latest_email_id-2,-1):
			typ, data = mail.fetch(i,'(RFC822)')
		
			#iterate through the successful mail fetches
			for response_part in data:
				#if there is an instance find out what the subject and message
				#are. The confirmation email will be a multipart message 
				if isinstance(response_part, tuple):
					msg = email.message_from_string(response_part[1])
					email_subject = msg['subject']
					email_from = msg['from']
				
					#all confirmation emails follow this structure so if it
					#is a confirmation email gather the link and clean it up
					#so that it can be opened up and accessed.
					if email_subject == 'Please confirm your booking!' and email_from == 'LibCal <alerts@mail.libcal.com>':
						confirm_link = re.search("http://(.+?)\"", str(msg.get_payload(1)))
						unclean_link = str(confirm_link.groups(0))
						unclean_link = unclean_link.replace("'",'')
						unclean_link = unclean_link.replace("(",'')
						unclean_link = unclean_link.replace(",",'')
						unclean_link = unclean_link.replace(")",'')
						unclean_link = unclean_link.replace("amp;",'')
						clean_link = "http://" + unclean_link + "&m=confirm"
						print "accessing...\n%s\n" %(clean_link)
						urllib2.urlopen(str(clean_link))
						print "\n\nshould have worked\n\n"
							
	except Exception as e:
		print str(e)
		
f.close()
			
