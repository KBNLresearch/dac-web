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
import sys
import unicodecsv as csv

sys.path.insert(0, "../../dac")

import dac

with open('../users/test/art.json') as fh:
    data = json.load(fh)

linker = dac.EntityLinker(debug=True)

with open('results.csv', 'w') as fh:

    keys = ['id', 'entity', 'links', 'prediction', 'correct']

    csv_writer = csv.writer(fh, delimiter='\t', encoding='utf-8')
    csv_writer.writerow(keys)

    nr_instances = 0 # Total number of test examples
    nr_correct_instances = 0 # Number of correctly predicted examples
    max_nr_links = 0 # Max number of examples where correct (or 'best') answer is a link
    min_nr_links = 0 # Min number of examples where correct (or 'best') answer is a link
    nr_correct_links = 0 # Number of link examples that were predicted correctly
    nr_false_links = 0 # Number of examples where incorrect link was predicted

    for i in data['instances']:

        # Check if instance has been properly labeled
        if i['links'] != []:

            print('Evaluating instance ' + str(nr_instances) + ': ' +
                i['ne_string'].encode('utf-8'))

            # Get result for current instance
            result = linker.link(i['url'], i['ne_string'].encode('utf-8'))[0]

            row = []
            row.append(str(nr_instances))
            row.append(i['ne_string'].encode('utf-8'))
            row.append(', '.join(i['links']).encode('utf-8'))
            row.append(result['link'].encode('utf-8') if 'link' in result
                else result['reason'])

            # Evaluate result
            if 'link' in result: # Link was predicted
                if result['link'] in i['links']: # Link is correct
                    nr_correct_instances += 1
                    nr_correct_links += 1
                    row.append('1')
                else: # Link is false
                    nr_false_links += 1
                    row.append('0')
            else: # No link was predicted
                if 'none' in i['links']: # No link is correct
                    nr_correct_instances += 1
                    row.append('1')
                else: # No link is false
                    row.append('0')

            csv_writer.writerow(row)

            nr_instances += 1
            if len([l for l in i['links'] if l != 'none']) >= 1:
                max_nr_links += 1
            if 'none' not in i['links']:
                min_nr_links += 1

accuracy = nr_correct_instances / float(nr_instances)
max_link_recall = nr_correct_links / float(min_nr_links)
min_link_recall = nr_correct_links / float(max_nr_links)
mean_link_recall = (max_link_recall + min_link_recall) / 2
link_precision = nr_correct_links / float(nr_correct_links + nr_false_links)
link_f_measure = 2 * ((link_precision * mean_link_recall) / float(link_precision +
    mean_link_recall))

print '---'
print 'Number of instances: ' + str(nr_instances)
print 'Number of correct predictions: ' + str(nr_correct_instances)
print 'Prediction accuracy: ' + str(accuracy)
print '---'
print 'Number of correct link predictions: ' + str(nr_correct_links)
print '(Min) number of link instances: ' + str(min_nr_links)
print '(Max) number of link instances: ' + str(max_nr_links)
print '(Min) link recall: ' + str(min_link_recall)
print '(Max) link recall: ' + str(max_link_recall)
print '(Mean) link recall: ' + str(mean_link_recall)
print '---'
print 'Number of correct link predictions: ' + str(nr_correct_links)
print 'Number of link predictions: ' + str(nr_correct_links + nr_false_links)
print 'Link precision: ' + str(link_precision)
print '---'
print '(Mean) link F1-measure: ' + str(link_f_measure)
print '---'
