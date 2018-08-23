import random
from collections import Counter

import pandas as pd
from pprint import pprint

import matplotlib.pyplot as plt
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
from pyclustering.cluster.xmeans import xmeans
from sklearn.cluster import KMeans, MiniBatchKMeans
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm
from sklearn.decomposition import PCA


class Clusterer:
    def __init__(self):
        self.most_significant = []
        self.centers = []
        self.predictions = []
        self.feats = []
        self.dv = DictVectorizer(sort=False,sparse=False)
        self.scaler = StandardScaler()
        self.kmeans = None
        self.number_of_authors = None

    def train(self, train_data, number_of_authors=None):
        print('Clustering...')
        self.number_of_authors = number_of_authors
        cluster_train = self.dv.fit_transform(train_data)
        self.feats = self.dv.feature_names_

        cluster_train = self.scaler.fit_transform(cluster_train)

        if self.number_of_authors is None:
            print('Using x-means to cluster as number of authors is unknown...')
            initial_centers = kmeans_plusplus_initializer(cluster_train, 2).initialize()
            xmeans_instance = xmeans(cluster_train, initial_centers, kmax=20, ccore=False)
            xmeans_instance.process()
            self.centers = xmeans_instance.get_centers()
            print('# of clusters: ' + str(len(self.centers)))
        else:
            # TODO: if number of authors is above a certain number, use minibatchkmeans
            print('Using k-means with n_clusters='+str(self.number_of_authors)+'...')
            self.kmeans = KMeans(n_clusters=self.number_of_authors,precompute_distances=True).fit(cluster_train)
            self.centers = self.kmeans.cluster_centers_

        pca = PCA(n_components=2)
        principalComponents = pca.fit_transform(cluster_train)
        principalDf = pd.DataFrame(data=principalComponents
                                   , columns=['principal component 1', 'principal component 2'])

        # finalDf = pd.concat([principalDf, df[['target']]], axis=1)
        finalDf = principalDf
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(1, 1, 1)
        ax.set_xlabel('Principal Component 1', fontsize=15)
        ax.set_ylabel('Principal Component 2', fontsize=15)
        ax.set_title('2 component PCA', fontsize=20)
        ax.scatter(finalDf['principal component 1'],
                   finalDf['principal component 2'],
                   s=120)
        ax.grid()
        plt.show()

    def analyse(self,test_data,mode):
        # Vectorise
        cluster_test = self.dv.transform(test_data)
        # Scale
        cluster_test = self.scaler.transform(cluster_test)

        cluster_results = []

        if self.number_of_authors is None:
            for i in range(len(cluster_test)):
                closest_center = None
                closest_distance = None
                for j in range(len(self.centers)):
                    distance = cosine_similarity([cluster_test[i],self.centers[j]])[0][0]
                    if closest_distance is None:
                        closest_distance = distance
                        closest_center = j
                    elif distance < closest_distance:
                        closest_distance = distance
                        closest_center = j
                self.predictions.append(closest_center)
        else:
            self.predictions = self.kmeans.predict(cluster_test)

        feature_significance_level = 2
        mode_code = 1
        if mode == 'diverge':
            mode_code = 2
            feature_significance_level = 0.2

        for i in range(len(self.predictions)):
            prediction = self.predictions[i]

            result_set = {}
            result_set["significant_features"] = []
            result_set["cluster"] = int(prediction)
            result_set['dist'] = cosine_distances([cluster_test[i], self.centers[prediction]])[0][1] * 100

            for j in range(len(self.centers[prediction])):
                feature_name = self.feats[j]
                if feature_name is 'capital_count':
                    print(feature_name)
                unscaled_test_value = 0
                try:
                    unscaled_test_value = test_data[i][feature_name]
                except:
                    pass
                centroid_value = self.centers[prediction][j]
                if centroid_value is not 0 and unscaled_test_value > 0:
                    test_value = cluster_test[i][j]
                    feature_difference = abs(test_value - centroid_value)
                    if mode_code == 2:
                        if feature_significance_level > feature_difference and unscaled_test_value > 0:
                            result_set["significant_features"].append(
                                (feature_name, feature_difference, test_value, centroid_value))
                    else:
                        if feature_difference > feature_significance_level and unscaled_test_value > 0:
                            result_set["significant_features"].append(
                                (feature_name, feature_difference, test_value, centroid_value))

            cluster_results.append(result_set)

        return cluster_results
