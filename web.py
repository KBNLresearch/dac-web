#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# Add DAC directory to the Python path
abs_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, abs_path + '/../dac')

import bottle

# Add absolute path to the Bottle template path
bottle.TEMPLATE_PATH.insert(0, abs_path)
bottle.TEMPLATE_PATH.insert(0, abs_path + '/templates')

# Import DAC scripts
import dac
import solr
import utilities

import hashlib
import json
import re
import time
import urllib

import xml.etree.ElementTree as etree

from bottle import abort
from bottle import default_app
from bottle import get
from bottle import post
from bottle import template
from bottle import redirect
from bottle import request
from bottle import route
from bottle import run
from bottle import static_file

@get('/<name>')
def show_candidates(name):
    '''
    Present an entity and its candidate links for selection.
    '''
    # Load json data from file
    with open(abs_path + '/users/' + name + '/art.json') as fh:
        data = json.load(fh)
    no_instances = len(data['instances'])
    last_instance = no_instances - 1

    # Get instance id
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

    # Get instance data
    url = data['instances'][index]['url']
    ne_string = data['instances'][index]['ne_string']
    ne_type = data['instances'][index]['ne_type']
    link = data['instances'][index]['link']

    # Get ocr, publication date
    context = dac.Context(url, dac.TPTA_URL)
    publ_date = context.publ_date
    ocr = context.ocr
    ocr = re.sub('(?P<pf>(^|\W|:punct:))' + re.escape(ne_string) +
        '(?P<sf>(\W|$|:punct:))', '\g<pf>' +
        '<span style="background-color:yellow;">' +
        ne_string + '</span>' + '\g<sf>', ocr)

    # Get Solr response
    norm = utilities.normalize(ne_string)
    last_part = utilities.get_last_name(norm)
    solr_connection = solr.SolrConnection(dac.SOLR_URL)
    cand_list = dac.CandidateList(solr_connection, dac.SOLR_ROWS,
        norm, last_part)
    solr_response = cand_list.solr_response

    return template('index', last_instance=last_instance, index=index, url=url,
            ne=ne_string, ne_type=ne_type, link=link, publ_date=publ_date,
            ocr=ocr, norm=norm, solr_response=solr_response)

@post('/<name>')
def save_link(name):
    '''
    Save selected link for an entity to file.
    '''
    index = int(request.forms.get('index'))
    link = request.forms.get('link')
    if link == 'other':
        link = request.forms.get('other_link')
    action = request.forms.get('action')

    orig_file = abs_path + '/users/' + name + '/art.json'
    temp_file = abs_path + '/users/' + name + '/temp.json'

    # Load json data from file
    with open(orig_file) as fh:
        data = json.load(fh)

    # Set new link value
    data['instances'][index]['link'] = link

    # Save json data to temp file
    with open(temp_file, 'w') as fh:
        fh.write(json.dumps(data))

    # Check temp file existence and size
    if os.path.exists(temp_file) and (abs(os.path.getsize(orig_file) -
            os.path.getsize(temp_file)) < 200):
        os.chmod(temp_file, 0777)
        os.remove(orig_file)
        os.rename(temp_file, orig_file)

        # Redirect to next page
        if action == 'last':
            redirect('../' + name)
        elif action == 'first':
            redirect('../' + name + '?index=0')
        else:
            next_index = (index + 1) if action == 'next' else (index - 1)
            redirect('../' + name + '?index=' + str(next_index))
    else:
        abort(500, 'Error saving data.')

@get('/<name>/edit')
def update_training_set(name):
    '''
    Add or delete an article.
    '''
    action = request.query.action
    url = request.query.url
    if not action or action not in ['add', 'delete'] or not url:
        abort(500, "Invoke with ?action=[add, delete]&url=[resolver_id]")

    orig_file = abs_path + '/users/' + name + '/art.json'
    temp_file = abs_path + '/users/' + name + '/temp.json'

    # Load original json data from file
    with open(orig_file) as fh:
        data = json.load(fh)

    # Perform requested update
    if action == 'add':
        # Check if article isn't included already
        # If so display error
        for i in data['instances']:
            if i['url'] == url:
                abort(500, 'Url ' + url + ' is already part of this data set.')

        # Keep test and training data seperate
        alt_name = 'tve' if name == 'test' else 'test'
        alt_file = abs_path + '/users/' + alt_name + '/art.json'
        with open(alt_file) as fh:
            alt_data = json.load(fh)
            for i in alt_data['instances']:
                if i['url'] == url:
                    abort(500, 'Url ' + url +
                        ' is already part of another data set.')

        # If not, retrieve entities and add them to the training data
        tpta_file = urllib.urlopen(dac.TPTA_URL + url)
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
            abort(500, 'No entities found for url ' + url + '.')

    if action == 'delete':
        # Check if article can be found
        to_remove = []
        for i in data['instances']:
            if i['url'] == url:
                to_remove.append(i)

        # If not display error
        if not to_remove:
            abort(500, 'Url ' + url + ' was not found in the data set.')
        else:
            for i in to_remove:
                data['instances'].remove(i)

    # Save json data to temp file
    with open(temp_file, 'w') as fh:
        fh.write(json.dumps(data))

    # Check temp file existence and size
    if os.path.exists(temp_file) and (abs(os.path.getsize(orig_file) -
            os.path.getsize(temp_file)) < 15000):
        os.chmod(temp_file, 0777)
        os.remove(orig_file)
        os.rename(temp_file, orig_file)
    else:
        abort(500, 'Error saving data.')

    return 'Success'

@route('/static/<filename:path>')
def static(filename):
    '''
    Load static css, js files.
    '''
    return static_file(filename, root=abs_path + '/static')

if __name__ == '__main__':
    run(host='localhost', port=5001)
else:
    application = default_app()

