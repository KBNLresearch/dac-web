#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# DAC Entity Linker
#
# Copyright (C) 2017-2018 Koninklijke Bibliotheek, National Library of
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
from keras.layers import concatenate
from keras.layers import Dense
from keras.layers import dot
from keras.layers import Dropout
from keras.layers import Input
from keras.models import load_model
from keras.models import Model

from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.model_selection import StratifiedShuffleSplit

np.random.seed(1337)
class_weight = {0: 0.25, 1: 0.75}

def load_csv(training_fn, features_fn):
    '''
    Transform tabular data set into NumPy arrays.
    '''
    df = pd.read_csv(training_fn, sep='\t')

    features = json.load(open(features_fn))['features']
    entity_features = [f for f in features if f.startswith('entity')]
    candidate_features = [f for f in features if f.startswith('candidate')]
    match_features = [f for f in features if f.startswith('match')]

    data = [df[entity_features].as_matrix(), df[candidate_features].as_matrix(),
        df[match_features].as_matrix()]
    for d in data:
        print('Data:', d.shape)

    labels = df[['label']].as_matrix()
    print('Labels:', labels.shape)

    return data, labels

def create_model(data):
    '''
    Load keras model.
    '''
    # Entity branch
    entity_inputs = Input(shape=(data[0].shape[1],))
    entity_x = Dense(data[0].shape[1], activation='relu',
            kernel_constraint=maxnorm(3))(entity_inputs)
    entity_x = Dropout(0.25)(entity_x)
    #entity_x = Dense(50, activation='relu',
    #        kernel_constraint=maxnorm(3))(entity_x)
    #entity_x = Dropout(0.25)(entity_x)

    # Candidate branch
    candidate_inputs = Input(shape=(data[1].shape[1],))
    candidate_x = Dense(data[1].shape[1], activation='relu',
            kernel_constraint=maxnorm(3))(candidate_inputs)
    candidate_x = Dropout(0.25)(candidate_x)
    #candidate_x = Dense(50, activation='relu',
    #        kernel_constraint=maxnorm(3))(candidate_x)
    #candidate_x = Dropout(0.25)(candidate_x)

    # Cosine proximity
    # cos_x = dot([entity_x, candidate_x], axes=1, normalize=False)
    # cos_x = concatenate([entity_x, candidate_x])
    # cos_output = Dense(1, activation='sigmoid')(cos_x)

    # Match branch
    match_inputs = Input(shape=(data[2].shape[1],))
    match_x = Dense(data[1].shape[1], activation='relu',
            kernel_constraint=maxnorm(3))(match_inputs)
    match_x = Dropout(0.25)(match_x)

    # Merge
    x = concatenate([entity_x, candidate_x, match_x])
    x = Dense(32, activation='relu', kernel_constraint=maxnorm(3))(x)
    x = Dropout(0.25)(x)
    x = Dense(16, activation='relu', kernel_constraint=maxnorm(3))(x)
    x = Dropout(0.25)(x)
    x = Dense(8, activation='relu', kernel_constraint=maxnorm(3))(x)
    x = Dropout(0.25)(x)

    predictions = Dense(1, activation='sigmoid')(x)

    model = Model(inputs=[entity_inputs, candidate_inputs, match_inputs],
        outputs=predictions)
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

    for train_index, test_index in sss.split(data[0], labels):
        x_train_0, x_test_0 = data[0][train_index], data[0][test_index]
        x_train_1, x_test_1 = data[1][train_index], data[1][test_index]
        x_train_2, x_test_2 = data[2][train_index], data[2][test_index]

        y_train, y_test = labels[train_index], labels[test_index]

        model = create_model(data)
        model.fit([x_train_0, x_train_1, x_train_2], y_train,
            epochs=100, batch_size=128, class_weight=class_weight)
        #y_pred = model.predict_classes(x_test, batch_size=128)

        y_pred = model.predict([x_test_0, x_test_1, x_test_2], batch_size=128)
        y_pred = [1 if y[0] > 0.5 else 0 for y in y_pred]

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
    model = create_model(data)
    model.fit(data, labels, epochs=100, batch_size=128,
            class_weight=class_weight)

    model.save(model_fn)

def predict(data, model_fn):
    '''
    Classify a new example.
    '''
    example = []
    for d in data:
        example.append(d[:1, :])
    model = load_model(model_fn)
    prob = model.predict(example, batch_size=1)
    print prob

if __name__ == '__main__':
    data, labels = load_csv('training.csv', 'bnn.json')
    #validate(data, labels)
    train(data, labels, 'bnn.h5')
    #predict(data, 'bnn.h5')

