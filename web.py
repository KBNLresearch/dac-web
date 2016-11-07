#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, '/var/www/dac')

from bottle import redirect, abort, route, get, post, run, template, request, default_app

import xml.etree.ElementTree as etree

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
    if os.path.exists(temp_file) and (abs(os.path.getsize(orig_file) -
            os.path.getsize(temp_file)) < 200):
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

    # Get training example data
    url = data['instances'][index]['url']
    ne_string = data['instances'][index]['ne_string']
    ne_type = data['instances'][index]['ne_type']
    link = data['instances'][index]['link']

    # Get current dac prediction
    linker = disambiguation.EntityLinker()
    result = linker.link(url, ne_string.encode('utf-8'))[0]

    # Get article publication date
    publ_date = linker.context.document.publ_date

    # Get ocr
    ocr = linker.context.document.ocr
    if not ocr:
        abort(500, "Error retrieving ocr.")

    # Mark the named entity string in the ocr text
    ocr = re.sub('(?P<pf>(^|\W|:punct:))' + re.escape(ne_string) +
            '(?P<sf>(\W|$|:punct:))', '\g<pf>' +
            '<span style="background-color:yellow;">' +
            ne_string + '</span>' + '\g<sf>', ocr)

    return template('index', last_instance=last_instance, index=index,
            url=url, publ_date=publ_date, ne=ne_string, ne_type=ne_type,
            ocr=ocr, link=link, dac_result=result, linker=linker)


@get('/<name>/edit')
def get_update(name):
    os.chdir(os.path.dirname(__file__))

    action = request.query.action
    url = request.query.url
    if not action or action not in ['add', 'delete'] or not url:
        abort(500, "Invoke with ?action=[add, delete]&url=[resolver_id]")

    orig_file = '/var/www/training/users/' + name + '/art.json'
    temp_file = '/var/www/training/users/' + name + '/temp.json'

    # Load original json data from file
    fh = open(orig_file, 'r')
    data = json.load(fh)
    fh.close()

    # Perform requested update
    if action == 'add':
        # Check if article isn't included already
        # If so display error
        for i in data['instances']:
            if i['url'] == url:
                abort(500, "Url " + url + " is already part of this data set.")

        # Keep test and training data seperate
        alt_name = 'tve' if name == 'test' else 'test'
        alt_file = '/var/www/training/users/' + alt_name + '/art.json'
        with open(alt_file) as fh:
            alt_data = json.load(fh)
            for i in alt_data['instances']:
                if i['url'] == url:
                    abort(500, "Url " + url + " is already part of another data set.")

        # If not, retrieve entities and add them to the training data
        #tpta_file = urllib.urlopen('http://145.100.59.224:8080/tpta/analyse?lang=nl&url=' + url)
        tpta_file = urllib.urlopen('http://192.87.165.3:8080/tpta2/analyse?lang=nl&url=' + url)
        tpta_string = tpta_file.read()
        tpta_file.close()

        root = etree.fromstring(tpta_string)
        if(len(root) > 0 and len(root[0]) > 0):
            entities = []
            for ent in root[0]:
                if ent.text not in entities:
                    entities.append(ent.text)
                    i = {}
                    i['url'] = url
                    i['ne_string'] = ent.text
                    i['ne_type'] = ent.tag
                    i['link'] = ''
                    data['instances'].append(i)
        else:
            abort(500, "No entities found for url " + url + ".")

    if action == 'delete':
        # Check if article can be found
        to_remove = []
        for i in data['instances']:
            if i['url'] == url:
                to_remove.append(i)

        # If not display error
        if not to_remove:
            abort(500, "Url " + url + " was not found in the training data.")
        else:
            for i in to_remove:
                data['instances'].remove(i)

    # Save json data to temp file
    fh = open(temp_file, 'w')
    fh.write(json.dumps(data))
    fh.close()

    # Check temp file existence and size
    if os.path.exists(temp_file) and (abs(os.path.getsize(orig_file) -
            os.path.getsize(temp_file)) < 15000):
        os.chmod(temp_file, 0777)
        os.remove(orig_file)
        os.rename(temp_file, orig_file)
    else:
        abort(500, "Error saving data.")

    return "Success"


#run(host='localhost', port=5001)
application = default_app()

