#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import urllib

sys.path.insert(0, "../dac")
import disambiguation

linker = disambiguation.EntityLinker()

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

        print 'Evaluating: ' + str(instances) + ' - ' + i['link']

        # Get result for current instance
        result = linker.link(i['url'], i['ne_string'].encode('utf-8'))[0]
        #print result

        # Save result data
        fh.write(str(instances) + '\t')
        fh.write(i['ne_string'].encode('utf-8') + '\t')
        fh.write(i['link'].encode('utf-8') + '\t')
        if result['link']:
            fh.write(result['link'].encode('utf-8') + '\t')
        else:
            fh.write('none' + '\t')

        # Evaluate result
        if i['link'] != 'none' and result['link'] and result['link'] == i['link']:
            fh.write('1\t')
            correct_links += 1
            correct += 1
        elif i['link'] == 'none' and not result['link']:
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


