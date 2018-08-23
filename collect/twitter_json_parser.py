import os

import json
from pprint import pprint


class TweetJsonParser:
    def __init__(self,path,):
        self.path = path
        self.tweets = []

    def run(self,no_of_accounts=-1):
        directory = os.fsencode(self.path)
        print('# of Accounts: ' + str(len(os.listdir(directory))))

        for file in os.listdir(directory)[:no_of_accounts]:
            filename = os.fsdecode(file)
            if filename.endswith(".json"):
                print('@'+filename[:-5])
                with open(self.path+'/'+filename) as input:
                    tweet_data = json.load(input)
                    for tweet in tweet_data['tweets']:
                        self.tweets.append((tweet['text'],tweet_data['handle']))

                # pprint(self.tweets)
                continue
            else:
                continue

        return self.tweets
