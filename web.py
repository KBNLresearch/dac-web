#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, '/var/www/dac')

from bottle import redirect, abort, route, get, post, run, template, request, default_app
import disambiguation
import hashlib
import json
import re
import time
import urllib


@post('/<name>')
def save(name):
    os.chdir(os.path.dirname(__file__))

    index = int(request.forms.get('index'))
    link = request.forms.get('link')
    if link == 'other':
        link = request.forms.get('other_link')
    action = request.forms.get('action')

    orig_file = '/var/www/training/users/' + name + '/art.json'
    temp_file = '/var/www/training/users/' + name + '/temp.json'

    # Load json data from file
    fh = open(orig_file, 'r')
    data = json.load(fh)
    fh.close()

    # Set new link value
    data['instances'][index]['link'] = link

    # Save json data to temp file
    fh = open(temp_file, 'w')
    fh.write(json.dumps(data))
    fh.close()

    # Check temp file existence and size
    if os.path.exists(temp_file) and (os.path.getsize(orig_file) - os.path.getsize(temp_file) < 200):
        os.chmod(temp_file, 0777)
        os.remove(orig_file)
        os.rename(temp_file, orig_file)

        # Redirect to next page
        if action == 'last':
            redirect('/training/' + name)
        elif action == 'first':
            redirect('/training/' + name + '?index=0')
        else:
            next_index = (index + 1) if action == 'next' else (index - 1)
            redirect('/training/' + name + '?index=' + str(next_index))
    else:
        abort(500, "Error saving data.")


@get('/<name>')
def training(name):
    os.chdir(os.path.dirname(__file__))

    # Load json data from file
    fh = open('/var/www/training/users/' + name + '/art.json', 'r')
    data = json.load(fh)
    fh.close()

    no_instances = len(data['instances'])
    last_instance = no_instances - 1

    # Get article url by index
    if request.query.index:
        index = int(request.query.index)
    else:
        # Find first instance that hasn't been linked yet
        index = no_instances
        for i in data['instances']:
            if i['link'] == '':
                index = data['instances'].index(i)
                break
    if index >= no_instances:
        index = 0
    if index <= -1:
        index = last_instance

    url = data['instances'][index]['url']
    ne_string = data['instances'][index]['ne_string']
    ne_type = data['instances'][index]['ne_type']
    link = data['instances'][index]['link']

    linker = disambiguation.EntityLinker()
    result = linker.link(url, ne_string.encode('utf-8'))

    # Article date
    publ_date = linker.document.publ_date

    # Get ocr
    ocr = linker.document.ocr
    if not ocr:
        abort(500, "Error retrieving ocr.")
    #ocr = ocr.decode('utf-8')

    # Mark the named entity string in the ocr text
    ocr = re.sub('(?P<pf>(^|\W|:punct:))' + re.escape(ne_string) +
            '(?P<sf>(\W|$|:punct:))', '\g<pf>' +
            '<span style="background-color:yellow;">' +
            ne_string + '</span>' + '\g<sf>', ocr)

    # Get Solr results
    solr_results = linker.to_link.solr_response

    # Get current dac prediction
    dac_link = linker.to_link.link if linker.to_link.link else 'none'

    # Current da prediction
    da_url = 'http://145.100.59.226/da/link?ne="' + ne_string.encode('utf-8') + '"'
    da_str = urllib.urlopen(da_url).read()
    da_data = json.loads(da_str)
    da_link = da_data['link'] if 'link' in da_data else 'none'

    return template('index', last_instance=last_instance, index=index,
            url=url, publ_date=publ_date, ocr=ocr, ne=ne_string,
            ne_type=ne_type, solr_results=solr_results, link=link,
            da_link=da_link, dac_link=dac_link)

#run(host='localhost', port=5001)
application = default_app()

