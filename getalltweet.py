#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
import io, json
import sys, getopt

#Twitter API credentials
consumer_key = "BDA8fVv22qx365hWa1CZhnx6O"
consumer_secret = "Aqma2b8zlDPEuZLVLvjmm7P2mC7gBT218BEYZyErpSqz60d5HE"
access_key = "2423518370-NzhoBOqf25PJO84UZuOUxFahvrGUf5S8A0JtZML"
access_secret = "e3rrLarSLoEmGnk9TEn2OHRAtC2BMY0lcoa96qmOmYLpq"


def get_all_tweets(argv):
	twitterUserName = ""
	data = ""
	count=0
	
	try:
		opts, args = getopt.getopt(argv,"hu:d:c:",["user=","data=","count="])
	except getopt.GetoptError:
		print ('getAllTweet.py -u <twitterUserName> -c <numberOfTweet>')
		print ('getAllTweet.py -d <data> -c <numberOfTweet>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print ('getAllTweet.py -u <twitterUserName> -c <numberOfTweet>')
			print ('getAllTweet.py -d <data> -c <numberOfTweet>')
			sys.exit()
		elif opt in ("-u", "--twitterUserName"):
			print ("Argument twitterUserName :"+arg)
			twitterUserName = arg
		elif opt in ("-d", "--data"):
			print ("Argument data :"+arg)
			data = arg
		elif opt in ("-c", "--count"):
			print ("Argument count :"+arg)
			count = arg
	
	
	#authorize twitter, initialize tweepy
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)
	
	#initialize a list to hold all the tweepy Tweets
	alltweets = []	
	
	if twitterUserName != "":
		#make initial request for most recent tweets (200 is the maximum allowed count)
		new_tweets = api.user_timeline(twitterUserName = twitterUserName,count=count)
		
	if data != "":
		print ("on est ici")
		new_tweets = api.search(q=data, count=count)
		print ("### tweets récupérés:")
		#print (*new_tweets)
		print ("### fin")
		
	#save most recent tweets
	alltweets.extend(new_tweets)

	#save tweets as json files
	save_tweets_as_json(new_tweets)
	
	#save the id of the oldest tweet less one
	oldest = alltweets[-1].id - 1
	
	#keep grabbing tweets until there are no tweets left to grab
	while len(new_tweets) > 0:
		print ("getting tweets before %s" % (oldest))
		
		#all subsiquent requests use the max_id param to prevent duplicates
		if twitterUserName != "":
			new_tweets = api.user_timeline(twitterUserName = twitterUserName,count=200,max_id=oldest,tweet_mode="extended")
			
		if data != "":
			new_tweets = api.search(q=data, count=100,max_id=oldest,tweet_mode="extended")
		
		#save most recent tweets
		alltweets.extend(new_tweets)

		#save tweets as json files
		save_tweets_as_json(new_tweets)
		
		#update the id of the oldest tweet less one
		oldest = alltweets[-1].id - 1
		
		print ("...%s tweets downloaded so far" % (len(alltweets)))

	#transform the tweepy tweets into a 2D array that will populate the csv	
	#outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]

	pass

def save_tweets_as_json(tweetslist):
	for eachtweet in tweetslist:
		with io.open('C:/dev/croustibatch/croustibatch/source_test/'+eachtweet.id_str+'.json', 'w', encoding='utf-8') as jfile:
			jfile.write(json.dumps(eachtweet._json, ensure_ascii=False))

if __name__ == '__main__':
	get_all_tweets(sys.argv[1:])