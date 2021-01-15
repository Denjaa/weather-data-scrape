
# list of packages that are being required to be run the code
import requests
from lxml import html
import warnings
import sqlite3
import os
import time
import datetime

# ignoring some of the warnings related to SSL
warnings.filterwarnings('ignore')

# city that user wants to get data for
user_location = 'Navan'

"""
The idea of this class is to connect to the website
that stores all the data regarding the weather and
save it to a special to csv file
"""
class Weather:

	def __init__(self, user_location):
		self.URL = r'https://www.timeanddate.com/weather/ireland/{}/historic'.format(user_location)
		self.connection = sqlite3.connect("weather.db")
		self.cursor = self.connection.cursor()
		self.sql_command = """CREATE TABLE IF NOT EXISTS weather (
									date DATE NOT NULL,
									time VARCHAR(10),
									temperature VARCHAR(10),
									comment VARCHAR(50),
									wind INTEGER,
									humidity INTEGER,
									baromiter VARCHAR(25),
									visibility VARCHAR(25)
									);
							"""
		self.cursor.execute(self.sql_command)
		self.connection.commit()
		self.validation = list(self.cursor.execute('SELECT date, time FROM weather'))

	def get_data(self):
		self.response = requests.get(self.URL, verify = False)
		self.content = html.fromstring(self.response.content)
		self.total_rows_amount = len(self.content.xpath('//*[@id="wt-his"]/tbody/tr'))
		self.current_date = ''
		for i in range(1, self.total_rows_amount + 1):
			self.row_data = self.content.xpath('//*[@id="wt-his"]/tbody/tr[{}]//text()'.format(i))
			if len(self.row_data) == 9:
					self.current_date = self.row_data[1]
					self.time, self.temperature, self.comment = self.row_data[0], self.row_data[2], self.row_data[3]
					self.wind, self.humidity, self.baromiter, self.visibility = self.row_data[4], self.row_data[6], self.row_data[7], self.row_data[8]
					self.sql_extract = """	INSERT INTO weather (date, time, temperature, comment, wind, humidity, baromiter, visibility)
											VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}') """.format(	self.current_date, self.time,
																												self.temperature, self.comment,
																												self.wind, self.humidity,
																												self.baromiter, self.visibility)
					self.cursor.execute(self.sql_extract)
			elif len(self.row_data) == 8:
				self.time, self.temperature, self.comment = self.row_data[0], self.row_data[1], self.row_data[2]
				self.wind, self.humidity, self.baromiter, self.visibility = self.row_data[3], self.row_data[5], self.row_data[6], self.row_data[7]
				self.sql_extract = """	INSERT INTO weather (date, time, temperature, comment, wind, humidity, baromiter, visibility)
										VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}') """.format(	self.current_date, self.time,
																											self.temperature, self.comment,
																											self.wind, self.humidity,
																											self.baromiter, self.visibility)
				self.cursor.execute(self.sql_extract)

			if str(self.current_date) not in str(self.validation):
				print ('*** NEW DATA AVAILABLE AND SCRAPED...')
				self.connection.commit()

def timer(timer):
	while timer:
		minutes, seconds = divmod(timer, 60)
		timeformat = 'Time left until code wakes up : {:02d}:{:02d}'.format(minutes, seconds)
		print (timeformat, end = '\n')
		time.sleep(1)
		timer = timer - 1

computerTime = (datetime.datetime.now()).strftime("%H:%M")
while computerTime =< '25:00':
	print ('*** CHECKING FOR NEW DATA AVAILABILITY...')
	Weather(user_location = user_location).get_data()
	timer(600)
	computerTime = (datetime.datetime.now()).strftime("%H:%M")
	print ('\n')
