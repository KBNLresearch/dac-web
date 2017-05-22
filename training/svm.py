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
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.externals import joblib

class_weight = {0: 0.25, 1: 0.75}
clf = svm.SVC(kernel='linear', C=1.0, decision_function_shape='ovr',
        class_weight=class_weight, probability=True)

def load_csv():
    '''
    Transform tabular data set into NumPy arrays.
    '''
    df = pd.read_csv('training.csv', sep='\t')

    X = df.ix[:, 6:-1].as_matrix()
    y = df.ix[:, -1:].as_matrix().reshape(-1)

    lb = preprocessing.LabelBinarizer()
    lb.fit(y)

    print('Features:', X.shape)
    print('Labels:', y.shape)

    return X, y

def validate(X, y):
    '''
    Ten-fold cross-validation with stratified sampling.
    '''
    accuracy_scores = []
    precision_scores = []
    recall_scores = []
    f1_scores = []

    sss = StratifiedShuffleSplit(n_splits=10)
    for train_index, test_index in sss.split(X, y):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        accuracy_scores.append(accuracy_score(y_test, y_pred))
        precision_scores.append(precision_score(y_test, y_pred))
        recall_scores.append(recall_score(y_test, y_pred))
        f1_scores.append(f1_score(y_test, y_pred))

    print('Accuracy', np.mean(accuracy_scores))
    print('Precision', np.mean(precision_scores))
    print('Recall', np.mean(recall_scores))
    print('F1-measure', np.mean(f1_scores))

def train(X, y):
    '''
    Train and save model.
    '''
    clf.fit(X, y)
    joblib.dump(clf, 'model.pkl')

if __name__ == '__main__':
    X, y = load_csv()
    validate(X, y)
    #train(X, y)
