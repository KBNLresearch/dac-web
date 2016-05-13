#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, '../dac')

import disambiguation
import json
import urllib


pred_fields = ['Id', 'Entity', 'Link', 'Prediction', 'Correct']
pred = open('predictions.csv', 'w')
pred.write('\t'.join(pred_fields) + '\n')

with open('users/test/art.json') as data_file:
    data = json.load(data_file)

instance_count = 0
candidate_count = 0
correct_pred = 0
pos_label = 0

linker = disambiguation.EntityLinker()

for i in data['instances']:

    print 'Reviewing instance ' + str(instance_count) + ': ' + i['ne_string']

    # Check if instance has been properly labeled
    if not i['link'] == '':

        # Get the DAC Solr result and current predection
        result = linker.link(i['url'], i['ne_string'].encode('utf-8'))[0]
        solr_response = linker.linked[0].solr_response

        # Check if any Solr results
        if hasattr(solr_response, 'numFound') and solr_response.numFound > 0:

            pred.write(str(instance_count) + '\t')
            pred.write(i['ne_string'].encode('utf-8') + '\t')
            pred.write(i['link'].encode('utf-8') + '\t')
            if result['link']:
                pred.write(result['link'].encode('utf-8') + '\t')
            else:
                pred.write('none' + '\t')

            if i['link'] != 'none' and 'link' in result and result['link'] == i['link']:
                pred.write('1\t')
            elif i['link'] == 'none' and not result['link']:
                pred.write('1\t')
            else:
                pred.write('0\t')
            pred.write('\n')

            index = 0

            for r in solr_response:
                print 'solr_link', r['id'][1:-1]

                # Label 1
                if r['id'][1:-1] == i['link']:
                    pos_label += 1
                    if 'link' in result and result['link'] == r['id'][1:-1]:
                        correct_pred += 1
                    else:
                        print 'Wrong prediction! This is a link.'

                # Label 0
                else:
                    if 'link' in result:
                        if result['link'] != r['id'][1:-1]:
                            correct_pred += 1
                        else:
                            print 'Wrong prediction! This is NOT a link.'
                    else:
                        correct_pred += 1

                candidate_count += 1

            index += 1

    instance_count += 1

accuracy = float(correct_pred) / float(candidate_count)

print('number of candidates', candidate_count)
print('number of positive labels', pos_label)
print('number of correct predictions', correct_pred)
print('accuracy', accuracy)

pred.close()

