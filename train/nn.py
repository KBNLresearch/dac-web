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

import json
import pandas as pd
import numpy as np

from keras.constraints import maxnorm
from keras.layers import Dense
from keras.layers import Dropout
from keras.models import load_model
from keras.models import Sequential

from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.model_selection import StratifiedShuffleSplit

class_weight = {0: 0.25, 1: 0.75}
np.random.seed(1337)

def load_csv(training_fn, features_fn):
    '''
    Transform tabular data set into NumPy arrays.
    '''
    df = pd.read_csv(training_fn, sep='\t')

    features = json.load(open(features_fn))['features']
    data = df[features].as_matrix()
    print('Data:', data.shape)

    labels = df[['label']].as_matrix()
    print('Labels:', labels.shape)

    return data, labels

def load_model(data):
    '''
    Load keras model.
    '''
    model = Sequential()
    model.add(Dense(data.shape[1], activation='relu',
        input_dim=data.shape[1], kernel_constraint=maxnorm(3)))
    model.add(Dropout(0.25))
    #model.add(Dense(16, activation='relu', kernel_constraint=maxnorm(3)))
    #model.add(Dropout(0.25))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='RMSprop', loss='binary_crossentropy',
        metrics=['accuracy'])

    return model

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

        model = load_model(data)
        model.fit(x_train, y_train, epochs=100, batch_size=128,
            class_weight=class_weight)
        y_pred = model.predict_classes(x_test, batch_size=128)

        accuracy_scores.append(accuracy_score(y_test, y_pred))
        precision_scores.append(precision_score(y_test, y_pred))
        recall_scores.append(recall_score(y_test, y_pred))
        f1_scores.append(f1_score(y_test, y_pred))

    print('')
    print('Accuracy', np.mean(accuracy_scores))
    print('Precision', np.mean(precision_scores))
    print('Recall', np.mean(recall_scores))
    print('F1-measure', np.mean(f1_scores))

def train(data, labels, model_fn):
    '''
    Train and save model.
    '''
    model = load_model(data)
    model.fit(data, labels, epochs=100, batch_size=128,
            class_weight=class_weight)

    model.save(model_fn)

def predict(data, model_fn):
    '''
    Classify a new example.
    '''
    example = data[:1, :]
    model = load_model(model_fn)
    prob = model.predict(example, batch_size=1)
    print prob

if __name__ == '__main__':
    data, labels = load_csv('training.csv', 'nn.json')
    #validate(data, labels)
    train(data, labels, 'nn.h5')

