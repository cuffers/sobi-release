import os
import pickle
import random
import subprocess
import sys

import requests
import twitter

from tqdm import tqdm
import learn.clusterer as clusterer
import collect.twitter_json_parser as twitter_json_parser
import learn.extractor as extractor
import report.reporter as reporter
from flask import Flask, render_template, request
from flask_cors import CORS
# app = Flask(__name__,
#             static_folder = "./dist/static",
#             template_folder = "./dist")

# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
import argparse

class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class SOBI():
    def __init__(self, number_of_authors):
        print(bcolors.HEADER + 'Welcome to SOBI' + bcolors.ENDC)
        self.corpus = []
        self.number_of_authors = number_of_authors
        self.corpus = []
        self.cu = clusterer.Clusterer()
        self.train_labeled_features = []
        self.state = 'initialised'


    def extract_features(self, path):
        self.corpus = twitter_json_parser.TweetJsonParser(path).run(self.number_of_authors)
        # path = 'blogs'
        # directory = os.fsencode(path)
        # print('# of Accounts: ' + str(len(os.listdir(directory))))
        #
        # for file in os.listdir(directory)[-3000:]:
        #     filename = os.fsdecode(file)
        #     if filename.endswith(".xml"):
        #         try:
        #             blog = untangle.parse(path+'/'+filename)
        #             for post in blog.Blog.post:
        #                 self.corpus.append(post.cdata.strip())
        #         except:
        #             continue
        #         continue
        #     else:
        #         continue
        print(str(len(self.corpus)) + ' texts')
        ex = extractor.Extractor()

        
        for text in tqdm(self.corpus):
            self.train_labeled_features.append(ex.extract_all_features(text[0]))

        self.state = 'extracted'
        return str(len(self.corpus))

    def train_model(self):
        self.cu.train(self.train_labeled_features, self.number_of_authors)
        self.state = 'trained'

    def analyse_text(self,text,mode):
        test_labeled_features = []
        ex = extractor.Extractor()

        test_labeled_features.append(ex.extract_all_features(text))

        cluster_results = self.cu.analyse(test_labeled_features, mode)

        rep = reporter.Reporter()
        report = rep.report(cluster_results, [text], mode)
        return report

app = Flask(__name__)
parser = argparse.ArgumentParser(description='Analyse stylistic distinctiveness.')
parser.add_argument('corpus_path', type=str, help='path to corpus')
parser.add_argument('number_of_authors',type=int, help='rough number of authors in corpus')

args = parser.parse_args()

sobi_instance = SOBI(args.number_of_authors)
sobi_instance.extract_features(args.corpus_path)
sobi_instance.train_model()

url = 'http://localhost:5000'

if sys.platform=='win32':
    os.startfile(url)
elif sys.platform=='darwin':
    subprocess.Popen(['open', url])
else:
    try:
        subprocess.Popen(['xdg-open', url])
    except OSError:
        print('Please open a browser on: '+url)

@app.route('/')
def index():
    return render_template("index.html",status='initialised')

@app.route('/api/extract', methods=['GET'])
def extract():
    if sobi_instance.state is 'initialised':
        number_of_texts = sobi_instance.extract_features()
        return number_of_texts
    if sobi_instance.state is 'extracted':
        return 'already extracted'
    if sobi_instance.state is 'trained':
        return 'already extracted'

@app.route('/api/train', methods=['GET'])
def train():
    if sobi_instance.state is 'initialised':
        sobi_instance.extract_features()
    if sobi_instance.state is 'extracted':
        sobi_instance.train_model()
    if sobi_instance.state is 'trained':
        return 'already trained'

@app.route('/api/report', methods=['POST'])
def generate_report():
    if request.method == 'POST':
        if sobi_instance.state is 'initialised':
            sobi_instance.extract_features()
        if sobi_instance.state is 'extracted':
            sobi_instance.train_model()
        if sobi_instance.state is 'trained':
            data = request.form
            report = sobi_instance.analyse_text(data['text'],data['mode'])
            return report

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://localhost:8080/{}'.format(path)).text
    return render_template("index.html")

app.run()

