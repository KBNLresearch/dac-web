#!/usr/bin/env python                                                                                |
# -*- coding: utf-8 -*-

import os, sys
print os.path.dirname(os.path.realpath(__file__))

os.chdir(os.path.dirname(os.path.realpath(__file__)))

import json


with open('users/jlo/art.json') as j_file:
    j_data = json.load(j_file)

with open('users/tve/art.json') as t_file:
        t_data = json.load(t_file)

for i in range(len(j_data['instances'])):

    # Find corresponding jlo and tve link:
    t_link = t_data['instances'][i]['link']
    j_link = j_data['instances'][i]['link']

    # Check if instance has been identically labeled
    if t_link != '' and j_link != '' and t_link != j_link:
        print(i)
        print('theo: ' + (t_link).encode('utf-8'))
        print('juliette: ' + (j_link).encode('utf-8') + '\n')
