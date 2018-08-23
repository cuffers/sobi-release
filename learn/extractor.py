import re
from pprint import pprint

import emoji
import nltk
from nltk import pos_tag, ngrams, bigrams
from nltk.corpus import stopwords
from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize
import string
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer

word_tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
sentence_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

class Extractor:

    def __init__(self):
        print('Extracting features...')
        self.text = ''
        self.text_tokens = []
        self.text_words = []
        self.text_sentences = []

    def count_stop_words(self):
        stopword_list = stopwords.words('english')
        c = Counter(self.text_tokens)
        stopword_features = []
        if len(self.text_words) > 0:
            stopword_features = {'count_'+key: c[key]/len(self.text_words) for key in stopword_list}
        else:
            stopword_features = {'count_'+key: 0 for key in stopword_list}
        return stopword_features

    def count_punctuation(self):
        c = Counter(self.text_tokens)
        punct_features = {}
        if len(self.text_words) > 0:
            punct_features = {'count_' + key: c[key]/len(self.text_words) for key in string.punctuation}
        else:
            punct_features = {'count_' + key: 0 for key in c.keys()}
        return punct_features

    def part_of_speech(self):
        pos_tags = ["CC","CD","DT","EX","FW","IN","JJ","JJR","JJS","LS","MD","NN","NNS","NNP","NNPS","PDT","POS","PRP","PRP$","RB","RBR","RBS","RP","SYM","TO","UH","VB","VBD","VBG","VBN","VBP","VBZ","WDT","WP","WP$","WRB"]
        text_pos_tags = pos_tag(self.text_tokens)
        c = Counter(tag[1] for tag in text_pos_tags)
        tags_to_return = {}
        for tag in pos_tags:
            if tag in c.keys() and len(self.text_words) > 0:
                tags_to_return['pos_'+tag] = c[tag]/len(self.text_words)
            else:
                tags_to_return['pos_'+tag] = 0
        return tags_to_return

    # def bigrams(self):
    #     bigrm = list(nltk.bigrams(list("".join(re.split("[^a-zA-Z]+", self.text.lower())))))
    #     bigrm = ["".join(bi) for bi in bigrm]
    #     c = Counter(bigrm)
    #     bigrm_count = {}
    #     if len(self.text_words) > 0:
    #         bigrm_count = {key: c[key]/len(self.text_words) for key in c}
    #     return bigrm_count

    def emoji(self):
        emoji_count = Counter([c for c in self.text if c in emoji.UNICODE_EMOJI])
        emoji_dict = {}
        if(len(emoji_count)):
            emoji_dict = {'emoji_'+key: emoji_count[key] for key in emoji_count.keys()}
        return emoji_dict

    def lexical_features(self):
        lex_feats = {}
        if len(self.text_sentences) > 0:
            words_per_sentence = np.array([len(word_tokenize(s))
                                           for s in self.text_sentences])

            lex_feats['number_of_sentences'] = len(self.text_sentences)
            if len(self.text_words) > 0:
                lex_feats['lexical_diversity'] = len(set(self.text_words))/float(len(self.text_words))
            else:
                lex_feats['lexical_diversity'] = 0
        else:
            lex_feats['number_of_sentences'] = len(self.text_sentences)
            lex_feats['lexical_diversity'] = 0

        return lex_feats

    def other_features(self):
        capital_count = sum(1 for c in self.text if c.isupper())
        if len(self.text_words) > 0:
            capital_count = capital_count/len(self.text_words)
        return {'capital_count': capital_count}

    def extract_all_features(self, text):
        self.text = text
        self.text_tokens = word_tokenize(self.text)
        self.text_words = word_tokenizer.tokenize(self.text)
        self.text_sentences = sentence_tokenizer.tokenize(self.text)
        stopwords_count = self.count_stop_words()
        punctuation_count = self.count_punctuation()
        pos = self.part_of_speech()
        lex_feats = self.lexical_features()
        other_feats = self.other_features()
        # self.bigrams()
        emoji_dict = self.emoji()
        return {**stopwords_count,**punctuation_count,**emoji_dict,**pos,**lex_feats,**other_feats}
