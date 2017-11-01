#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import urllib


SERVICE = 'DAC'

if SERVICE == 'DAC':
    base_url = 'http://www.kbresearch.nl/dac/?'
elif SERVICE == 'DA':
    #base_url = 'http://145.100.59.226:8002/?'
    base_url = 'http://kbresearch.nl/da/link?'

# Load test data set
with open('users/test/art.json') as data_file:
    data = json.load(data_file)

# Init results file
fh = open('results.csv', 'w+')
fields = ['Id', 'Entity', 'Link', 'Prediction', 'Correct']
fh.write('\t'.join(fields) + '\n')

# Get and evaluate results
nr_instances = 0 # Total number of test examples
nr_correct_instances = 0 # Number of correctly predicted examples
nr_links = 0 # Number of examples where correct answer is a link
nr_correct_links = 0 # Number of link examples that were predicted correctly
nr_false_links = 0 # Number of link or non-link examples where incorrect link was predicted

for i in data['instances']:

    # Check if instance has been properly labeled
    if not i['link'] == '':

        print 'Evaluating: ' + str(nr_instances) + ' - ' + i['link']

        # Get result for current instance
        qs = {}
        qs['ne'] = i['ne_string'].encode('utf-8')
        if SERVICE == 'DAC':
            qs['url'] = i['url'].encode('utf-8')
            qs['debug'] = '1'
            #qs['model'] = 'nn'
        url = base_url + urllib.urlencode(qs)

        print url
        result = urllib.urlopen(url).read()
        result = json.loads(result)
        if SERVICE == 'DAC':
            result = result['linkedNEs'][0]

        # Save result data
        fh.write(str(nr_instances) + '\t')
        fh.write(i['ne_string'].encode('utf-8') + '\t')
        fh.write(i['link'].encode('utf-8') + '\t')
        if 'link' in result:
            fh.write(result['link'].encode('utf-8') + '\t')
        else:
            fh.write('none' + '\t')

        # Evaluate result
        if i['link'] != 'none':
            nr_links += 1
            if 'link' in result:
                if result['link'] == i['link']:
                    nr_correct_instances += 1
                    nr_correct_links += 1
                    fh.write('1\t')
                else:
                    nr_false_links += 1
                    fh.write('0\t')
            else:
                fh.write('0\t')
        elif i['link'] == 'none':
            if 'link' in result:
                nr_false_links += 1
                fh.write('0\t')
            else:
                nr_correct_instances += 1
                fh.write('1\t')

        fh.write('\n')

        nr_instances += 1

fh.close()

accuracy = nr_correct_instances / float(nr_instances)
link_recall = nr_correct_links / float(nr_links)
link_precision = nr_correct_links / float(nr_correct_links + nr_false_links)
link_f_measure = 2 * ((link_precision * link_recall) / float(link_precision +
        link_recall))

print '---'
print 'Number of instances: ' + str(nr_instances)
print 'Number of correct predictions: ' + str(nr_correct_instances)
print 'Prediction accuracy: ' + str(accuracy)
print '---'
print 'Number of link instances: ' + str(nr_links)
print 'Number of correct link predictions: ' + str(nr_correct_links)
print 'Link recall: ' + str(link_recall)
print '---'
print 'Number of correct link predictions: ' + str(nr_correct_links)
print 'Number of link predictions: ' + str(nr_correct_links + nr_false_links)
print 'Link precision: ' + str(link_precision)
print '---'
print 'Link F1-measure: ' + str(link_f_measure)
print '---'

