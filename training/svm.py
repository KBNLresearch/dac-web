#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# DAC Entity Linker
#
# Copyright (C) 2017 Koninklijke Bibliotheek, National Library of
# the Netherlands
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import pandas as pd

from sklearn import preprocessing
from sklearn import svm
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.model_selection import StratifiedShuffleSplit

class_weight = {0: 0.2, 1: 0.8}
clf = svm.SVC(kernel='linear', C=1.0, decision_function_shape='ovr',
        class_weight=class_weight, probability=True)

def load_csv():
    '''
    Transform tabular data set into NumPy arrays.
    '''
    df = pd.read_csv('training.csv', sep='\t')

    data = df.ix[:, 6:-1].as_matrix()
    labels = df.ix[:, -1:].as_matrix().reshape(-1)

    lb = preprocessing.LabelBinarizer()
    lb.fit(labels)

    print('Data:', data.shape)
    print('Labels:', labels.shape)

    return data, labels

def validate(data, labels):
    '''
    Ten-fold cross-validation with stratified sampling.
    '''
    accuracy_scores = []
    precision_scores = []
    recall_scores = []
    f1_scores = []

    sss = StratifiedShuffleSplit(n_splits=10)
    for train_index, test_index in sss.split(data, labels):
        x_train, x_test = data[train_index], data[test_index]
        y_train, y_test = labels[train_index], labels[test_index]
        clf.fit(x_train, y_train)
        y_pred = clf.predict(x_test)
        accuracy_scores.append(accuracy_score(y_test, y_pred))
        precision_scores.append(precision_score(y_test, y_pred))
        recall_scores.append(recall_score(y_test, y_pred))
        f1_scores.append(f1_score(y_test, y_pred))

    print('Accuracy', np.mean(accuracy_scores))
    print('Precision', np.mean(precision_scores))
    print('Recall', np.mean(recall_scores))
    print('F1-measure', np.mean(f1_scores))

def train(data, labels):
    '''
    Train and save model.
    '''
    clf.fit(data, labels)
    joblib.dump(clf, 'model.pkl')

    df = pd.read_csv('training.csv', sep='\t')
    df = df.ix[:, 6:-1]
    for i, feature in enumerate(df.columns.values):
        print(feature, clf.coef_[:, i][0])

if __name__ == '__main__':
    data, labels = load_csv()
    #validate(data, labels)
    train(data, labels)
