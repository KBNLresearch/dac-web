#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import urllib


SERVICE = 'DAC'

if SERVICE == 'DAC':
    base_url = 'http://www.kbresearch.nl/dac/?'
elif SERVICE == 'DA':
    base_url = 'http://145.100.59.226:8002/?'


# Load test data set
with open('users/test/art.json') as data_file:
    data = json.load(data_file)

# Init results file
fh = open('results.csv', 'w+')
fields = ['Id', 'Entity', 'Link', 'Prediction', 'Correct']
fh.write('\t'.join(fields) + '\n')

# Get and evaluate results
instances = 0
links = 0
correct = 0
correct_links = 0

for i in data['instances']:

    # Check if instance has been properly labeled
    if not i['link'] == '':

        print 'Evaluating: ' + i['link']

        # Get result for current instance
        url = base_url + 'ne=' + i['ne_string'].encode('utf-8')
        if SERVICE == 'DAC':
            url += '&url=' + i['url'].encode('utf-8')
            url += '&debug=1'
        print url
        result = urllib.urlopen(url).read()
        result = json.loads(result)
        if SERVICE == 'DAC':
            result = result['linkedNEs'][0]

        # Save result data
        fh.write(str(instances) + '\t')
        fh.write(i['ne_string'].encode('utf-8') + '\t')
        fh.write(i['link'].encode('utf-8') + '\t')
        if 'link' in result:
            fh.write(result['link'].encode('utf-8') + '\t')
        else:
            fh.write('none' + '\t')

        # Evaluate result
        if i['link'] != 'none' and 'link' in result and result['link'] == i['link']:
            fh.write('1\t')
            correct_links += 1
            correct += 1
        elif i['link'] == 'none' and not 'link' in result:
            fh.write('1\t')
            correct += 1
        else:
            fh.write('0\t')
        fh.write('\n')

        if i['link'] != 'none':
            links += 1
        instances += 1

fh.close()

print '--'
print 'Instances: ' + str(instances)
print 'Correct: ' + str(correct)
print 'Accuracy: ' + str(correct / float(instances))
print '--'
print 'Links: ' + str(links)
print 'Correct links: ' + str(correct_links)
print 'Link recall: ' + str(correct_links / float(links))
print '--'


