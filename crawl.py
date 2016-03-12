import tweepy
from config import * 
import pprint
import logging
import cPickle
import csv

logging.basicConfig(level=logging.INFO)

LOAD_TEMP = True

NTU_GEO_CODE = {'lat':'1.348288','lng':'103.682748'}

RADIUS = '2km'

Coordinates = NTU_GEO_CODE

pp = pprint.PrettyPrinter(indent=4)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token_key, access_token_secret)
 
api = tweepy.API(auth)

geocode = Coordinates['lat'] + ',' + Coordinates['lng'] + "," + RADIUS

try:
	with open('temp_users.pkl','rb') as f:
		users = cPickle.load(f)
		logging.info("Loaded temp users file")
		logging.info(users)
except:
	logging.info("Can't load user database")
	users = []



if(LOAD_TEMP):
	try:
		with open('temp_results.pkl','rb') as f:
			results = cPickle.load(f)
			logging.info(len(results))
			logging.info("Loaded temp results file")
	except:
		logging.info("Cannot load temp results file")
else:
	results = []
	for tweet in tweepy.Cursor(api.search,
                   count=100,
                   geocode=geocode,
                   result_type="recent",
                   include_entities=True,
                   lang="en").items():
		results.append(tweet)

	with open('temp_results.pkl','w') as f:
		cPickle.dump(results,f)
	# pass

data = []

IGNORE_DUPLICATES = True

storedIds = []
originalIdLength = len(storedIds)
NoGeoError = 0 

# Stored Ids seem redundant for now
for u in users:
	storedIds.append(u[0])

# results = results[]

for result in results:
	# logging.info(result.user.id)
	# logging.info(result.user.screen_name)
	# logging.info(result.text)
	# logging.info(result.created_at)
	# logging.info(result.place)
	# userswriter.writerow([result.user.id,result.user.screen_name])
	# For writing later 

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
				data.append([result.user.id,str(r.created_at),coordinates[0],coordinates[1],r.user.screen_name,cleaned_text])
			except:
				NoGeoError+=1
	except:
		logging.info("Rate limit eached")
		break

with open('temp_data.pkl','w') as f:
	cPickle.dump(data,f)

with open('temp_users.pkl','w') as f:
	cPickle.dump(users,f)

# with open('temp_data.pkl','rb') as f:
# 	data = cPickle.load(f)
# 	logging.info("Loaded temp results file")
# with open('temp_users.pkl','rb') as f:
# 	users = cPickle.load(f)
# 	logging.info("Loaded temp results file")


logging.info("Writing data to csv...")
with open('data.csv','a') as f:
	datawriter = csv.writer(f, delimiter=',')
	datawriter.writerows(data)	

logging.info("Writing user to csv...")
with open('users.csv','w') as f2:
	userswriter = csv.writer(f2, delimiter=',')
	userswriter.writerows(users)

logging.info("Number of new users->%d",len(storedIds)-originalIdLength)
logging.info("Number of data points->%d",len(data))
# logging.info("Number of No Geo Errors->%d",NoGeoError)
logging.info("Done")
	

	#print result.text
	#print result.location if hasattr(result, 'location') else "Undefined location"