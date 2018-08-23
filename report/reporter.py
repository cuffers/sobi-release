import json
import re
from collections import Counter
from pprint import pprint
import matplotlib.pyplot as plt

class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

class Reporter:

    def __init__(self):
        self.mode = 'converge'

    def report(self, cluster_results, test_corpus, mode):
        print('Reporting...')
        self.mode = mode
        clusters = {}
        full_result_set = []
        for i in range(len(cluster_results)):
            report = test_corpus[i]
            result_set = cluster_results[i]

            if str("cluster_" + str(result_set["cluster"])) in clusters:
                clusters[str("cluster_" + str(result_set["cluster"]))].append(test_corpus[i][1])
            else:
                clusters[str("cluster_" + str(result_set["cluster"]))] = []
                clusters[str("cluster_" + str(result_set["cluster"]))].append(test_corpus[i][1])

            print(report)
            print('D-Score: ' + str(result_set['dist']))
            result_set['report'] = report
            # print(report.format(c=colorful))
            print('\n')
            full_result_set.append(result_set)
        # for cluster in clusters.keys():
        #     pprint(cluster)
        #     pprint(Counter(clusters[cluster]))

        return json.dumps(full_result_set)
