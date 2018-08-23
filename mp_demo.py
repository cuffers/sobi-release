import json
from pprint import pprint
import numpy as np
import requests
import twitter
import operator
import argparse
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Helper tool for SOBI.')
parser.add_argument('account_list', type=str, help='path to account list')

args = parser.parse_args()

test = []

twitterConsumerKey = # insert key
twitterConsumerSecret = # insert key
twitterAccessToken = # insert key
twitterAccessTokenSecret = # insert key

api = twitter.Api(consumer_key=twitterConsumerKey,
                    consumer_secret=twitterConsumerSecret,
                    access_token_key=twitterAccessToken,
                    access_token_secret=twitterAccessTokenSecret)

account_names = []

with open(args.account_list) as input:
    account_handles = input.readlines()
    account_names = [acc.strip()[1:] for acc in account_handles]

tweets = {}
reports = {}
results = {}
print(str(len(account_names)) + ' accounts being scraped...')

for acc in tqdm(account_names):
    reports[acc] = []
    results[acc] = []
    try:

        tweets[acc] = api.GetUserTimeline(screen_name=acc,
                                        count=1000,
                                        exclude_replies=True,
                                        include_rts=False)
    except:
        print('Error getting tweets from: @' + acc )
        continue

for account in tweets:
    for tweet in tweets[account]:
        test.append((tweet.text, account))

print(str(len(test)) + ' tweets being analysed...')

for text in tqdm(test):
    form_data = {
        'text': text[0],
        'mode': 'converge'
    }
    r = requests.post('http://localhost:5000/api/report',data=form_data)
    try:
        reports[text[1]].append((text[0],r.json()[0]['dist']))
    except:
        print('Error parsing JSON')
        continue
# pprint(reports)

for res in reports:
    results[res] = {
        'mean': np.mean([result[1] for result in reports[res]]),
        'std':  np.std([result[1] for result in reports[res]])
    }

# pprint(results)

def get_mean(x):
    return x[1]['mean']

def get_std(x):
    return x[1]['std']

def get_score(x):
    return x[1]

sorted_results_mean = sorted(results.items(), key=get_mean)
sorted_results_std = sorted(results.items(), key=get_std)
print('Most distinctive: @' + sorted_results_mean[-1][0] + ' with mean score of ' + str(get_mean(sorted_results_mean[-1])))
most_distinct_tweets = sorted(reports[sorted_results_mean[-1][0]], key=get_score)[-3:]
for tweet in most_distinct_tweets:
    print(tweet[0])

print('Most varying: @' + sorted_results_std[-1][0] + ' with deviation of ' + str(get_std(sorted_results_std[-1])))

print('\\noindent Top 5 Most Distinctive')
print('\\begin{itemize}')
for i in sorted_results_mean[-1:-6:-1]:
    print('\\item @' + i[0] + ' with mean score of ' + str(get_mean(i)))
print('\\end{itemize}')
print('\\noindent Top 5 Least Distinctive')
print('\\begin{itemize}')
for i in sorted_results_mean[:5]:
    print('\\item @' + i[0] + ' with mean score of ' + str(get_mean(i)))
print('\\end{itemize}')
print('\\noindent Top 5 Most Varying')
print('\\begin{itemize}')
for i in sorted_results_std[-1:-6:-1]:
    print('\\item @' + i[0] + ' with standard deviation of ' + str(get_std(i)))
print('\\end{itemize}')
print('\\noindent Top 5 Least Varying')
print('\\begin{itemize}')
for i in sorted_results_std[:5]:
    print('\\item @' + i[0] + ' with standard deviation of ' + str(get_std(i)))
print('\\end{itemize}')