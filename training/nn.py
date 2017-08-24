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

import pandas as pd
import numpy as np

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

def load_csv():
    '''
    Transform tabular data set into NumPy arrays.
    '''
    df = pd.read_csv('training.csv', sep='\t')

    data = df.ix[:, 5:-1].as_matrix()
    labels = df.ix[:, -1:].as_matrix()

    print('Data:', data.shape)
    print('Labels:', labels.shape)

    return data, labels

def load_model(data):
    '''
    Load keras model.
    '''
    model = Sequential()
    model.add(Dense(64, activation='relu', input_dim=data.shape[1]))
    model.add(Dropout(0.5))
    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(16, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    model.compile(optimizer='RMSprop', loss='binary_crossentropy',
        metrics=['accuracy'])

    return model

def validate(data, labels, model):
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

        model.fit(x_train, y_train, epochs=10, batch_size=128,
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

def train(data, labels, model):
    '''
    Train and save model.
    '''
    model.fit(data, labels, epochs=50, batch_size=128,
            class_weight=class_weight)

    model.save('model.h5')

def predict(data):
    example = data[:1, :]
    model = load_model('model.h5')
    prob = model.predict(example, batch_size=1)
    print prob

if __name__ == '__main__':
    data, labels = load_csv()
    model = load_model(data)
    #validate(data, labels, model)
    train(data, labels, model)

