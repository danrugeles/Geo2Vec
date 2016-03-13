#!/usr/bin/python

"""
Script to crawl tweets from twitter and store only those with geographical locations.

Brief details about crawling
1) I do a geo-search, get a list of tweets (via a paginated cursor, means it gets about 1000+ tweets)
2) This can be considered a list of seeds for user crawling 
3) This intial first geo-crawl is persisted to save API calls
4) For each tweet in the initial batch, we crawl the user, and get their timeline. 
(Intuition is that people with geocodes in one tweet will have in many or most)
5) Store a list of crawled user in duplicates

Notes:
1) It gets about 100+ tweets per user. Have not gone deeper. 
2) It gets recent tweets 
3) It might be hard to paginate and get older tweets
4) The idea is to sample more users, rather than get just one user's movements.
5) Favor a wider sampling over users rather than going in depth and getting one user's full history

Oh, I also added the tweet-id so that we do not have to worry about getting too many duplicated tweets.
We can just clean it later. 

"""

import tweepy
from config import * 
import pprint
import logging
import cPickle
import csv

# Initializing all the basic stuff 
logging.basicConfig(level=logging.INFO)
pp = pprint.PrettyPrinter(indent=4)
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)
api = tweepy.API(auth)

# Config for files
FILE_PREFIX = "dataset/"	# where all files go
temp_results_f = FILE_PREFIX + 'temp_results.pkl'
temp_users_f = FILE_PREFIX + 'temp_users.pkl'
temp_data_f = FILE_PREFIX + 'temp_data.pkl'
csv_data = FILE_PREFIX +'data.csv'
csv_users = FILE_PREFIX + 'users.csv'

# Geographical crawl centroid
# Just start from NTU geo code first. May extend to anything else
NTU_GEO_CODE = {'lat':'1.348288','lng':'103.682748'}
RADIUS = '2km'
Coordinates = NTU_GEO_CODE
geocode = Coordinates['lat'] + ',' + Coordinates['lng'] + "," + RADIUS

# If we want to load the initial batch from pickled file or not
LOAD_TEMP = True

# Load the existing lists of users that we have crawled
# This is to save on API calls. 
try:
	with open(temp_users_f,'rb') as f:
		users = cPickle.load(f)
		logging.info("Loaded temp users file")
		logging.info(users)
except:
	logging.info("Can't load user database")
	users = []


try:
	if(LOAD_TEMP==False):
		raise Exception("Not supposed to be loading temp file")
	with open(temp_results_f,'rb') as f:
		results = cPickle.load(f)
		logging.info(len(results))
		logging.info("Loaded temp results file")
except:
	logging.info("Cannot load temp results file")
	results = []
	for tweet in tweepy.Cursor(api.search,
	               count=100,
	               geocode=geocode,
	               result_type="recent",
	               include_entities=True,
	               lang="en").items():
		results.append(tweet)

	with open(temp_results_f,'w') as f:
		cPickle.dump(results,f)

data = []

# Whether we want to ignore duplicate users or not 
# Duplicate users may cause a lot wasted API calls, we do not want that 
IGNORE_DUPLICATES = True

# We could use the users to check, but storedIds seem more efficient actually
# I could pickle this too. 
storedIds = []
originalIdLength = len(storedIds)
NoGeoError = 0 	# Number of tweets we came across but had no geolocations

# Stored Ids seem redundant for now. but might be faster for checking
for u in users:
	storedIds.append(u[0])

# results = results[]

for result in results:
	"Iterate initial results"
	# logging.info(result.user.id)
	# logging.info(result.user.screen_name)
	# logging.info(result.text)
	# logging.info(result.created_at)
	# logging.info(result.place)
	# userswriter.writerow([result.user.id,result.user.screen_name])

	# Warning -> I'm still working out this ignore mechanism 
	if(IGNORE_DUPLICATES):
		if(result.user.id in storedIds):
			logging.info("Ignoring duplicated user")
			continue
	if(result.user.id not in storedIds):
		users.append([result.user.id,result.user.screen_name])
		# For duplicate checking
		storedIds.append(result.user.id)
	else:
		logging.info("Ignoring duplicated user")
		continue

	logging.info("Checking user %s out more...",result.user.screen_name)
	try:
		user_results = []
		for tweet in tweepy.Cursor(api.user_timeline,id=result.user.id,count=1000).items():
			user_results.append(tweet)
		# user_results = api.user_timeline(result.user.id,count=1000)
		for r in user_results:
			# logging.info('=================================')
			# logging.info(r.text)
			# logging.info(r.created_at)
			# geo format for data file
			try:
				geo_format = r.coordinates
				coordinates = geo_format['coordinates']
				cleaned_text = r.text.encode('utf-8').rstrip('\n')
				data.append([result.id,result.user.id,str(r.created_at),coordinates[0],coordinates[1],r.user.screen_name,cleaned_text])
			except:
				NoGeoError+=1
	except:
		logging.info("Rate limit reached")
		break

with open(temp_data_f,'w') as f:
	cPickle.dump(data,f)

with open(temp_users_f,'w') as f:
	cPickle.dump(users,f)

# with open('temp_data.pkl','rb') as f:
# 	data = cPickle.load(f)
# 	logging.info("Loaded temp results file")
# with open('temp_users.pkl','rb') as f:
# 	users = cPickle.load(f)
# 	logging.info("Loaded temp results file")


logging.info("Writing data to csv...")
with open(csv_data,'a+') as f:
	datawriter = csv.writer(f, delimiter=',')
	datawriter.writerows(data)	

logging.info("Writing user to csv...")
with open(csv_users,'w') as f2:
	userswriter = csv.writer(f2, delimiter=',')
	userswriter.writerows(users)

logging.info("Number of new users->%d",len(storedIds)-originalIdLength)
logging.info("Number of data points->%d",len(data))
logging.info("Number of No Geo Errors->%d",NoGeoError)
logging.info("Done")
	

	#print result.text
	#print result.location if hasattr(result, 'location') else "Undefined location"