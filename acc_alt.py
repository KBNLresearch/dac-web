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

#linker = disambiguation.EntityLinker()
inst_count = 0

for i in data['instances']:

    # Check if instance has been properly labeled
    if not i['link'] == '':
        print i['link']

        # Get the DAC Solr result and current predection
        #result = linker.link(i['url'], i['ne_string'].encode('utf-8'))[0]
        result = urllib.urlopen('http://145.100.59.226:8002/?ne=' + i['ne_string'].encode('utf-8')).read()
        print result, type(result)
        result = json.loads(result)
        print result, type(result)

        #solr_response = linker.linked[0].solr_response

        # Check if any Solr results
        if True:

            pred.write(str(inst_count) + '\t')
            pred.write(i['ne_string'].encode('utf-8') + '\t')
            pred.write(i['link'].encode('utf-8') + '\t')
            if 'link' in result:
                pred.write(result['link'].encode('utf-8') + '\t')
            else:
                pred.write('none' + '\t')

            if i['link'] != 'none' and 'link' in result and result['link'] == i['link']:
                pred.write('1\t')
            elif i['link'] == 'none' and not 'link' in result:
                pred.write('1\t')
            else:
                pred.write('0\t')
            pred.write('\n')

            inst_count += 1

pred.close()

