import json
from pprint import pprint
import numpy as np
import requests
import twitter
import operator
import argparse
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Helper tool for SOBI.')
parser.add_argument('corpus_account_list', type=str, help='path to corpus account list')
parser.add_argument('test_account_list', type=str, help='path to test account list')


args = parser.parse_args()

twitterConsumerKey = # insert key
twitterConsumerSecret = # insert key
twitterAccessToken = # insert key
twitterAccessTokenSecret = # insert key

api = twitter.Api(consumer_key=twitterConsumerKey,
                    consumer_secret=twitterConsumerSecret,
                    access_token_key=twitterAccessToken,
                    access_token_secret=twitterAccessTokenSecret)


test_account_list = []
corpus_account_list = []

with open(args.test_account_list) as input:
    account_handles = input.readlines()
    test_account_list = [acc.strip()[1:] for acc in account_handles]

with open(args.corpus_account_list) as input:
    account_handles = input.readlines()
    for acc in account_handles:
        if acc.strip()[1:] not in test_account_list:
            print(acc+' will be scraped.')
            corpus_account_list.append(acc.strip()[1:])
        else:
            print(acc+' present in test account list.')



corpus_tweets = {}
print(str(len(corpus_account_list)) + ' accounts being scraped for corpus...')

for acc in tqdm(corpus_account_list):
    try:
        corpus_tweets[acc] = api.GetUserTimeline(screen_name=acc,
                                        count=1000,
                                        exclude_replies=True,
                                        include_rts=False)
    except:
        print('Error getting tweets from: @' + acc )
        continue

for account in corpus_tweets:
  import json
  data = {"handle": account, "tweets":[{"text": tweet.text, "id": tweet.id, "time": tweet.created_at} for tweet in corpus_tweets[account]]}
  pprint(data)
  with open('mp_demo/'+account+'.json', 'w+') as outfile:
    json.dump(data, outfile)