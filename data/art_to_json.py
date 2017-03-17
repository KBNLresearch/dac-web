#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import urllib2
import xml.etree.ElementTree as etree


art_file = open('art_training.txt', 'r')
articles = art_file.read()
articles = articles.strip('\n').split('\n')
art_file.close()

#sample = random.sample(range(249), 25)

data = {}
data['instances'] = []

index = 0
for url in articles:
    print('Processing', url)
    tpta_file = urllib2.urlopen('http://145.100.59.224:8080/tpta/analyse?lang=nl&url=' + url)
    tpta_string = tpta_file.read()
    tpta_file.close()

    root = etree.fromstring(tpta_string)
    if(len(root) > 0 and len(root[0]) > 0):
        entities = []
        for ent in root[0]:
            print('Found entity', ent.text)
            if ent.text not in entities:
                print('Adding entity', ent.text)
                entities.append(ent.text)
                i = {}
                i['url'] = url
                i['ne_string'] = ent.text
                i['ne_type'] = ent.tag
                i['link'] = ''
                data['instances'].append(i)

    index += 1

json_data = json.dumps(data)

json_file = open('art_training.json', 'w')
json_file.write(json_data)
json_file.close
