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

import codecs
import json
import re
import urllib

import xml.etree.ElementTree as etree

from bottle import abort
from bottle import default_app
from bottle import get
from bottle import post
from bottle import template
from bottle import redirect
from bottle import request
from bottle import response
from bottle import route
from bottle import run
from bottle import static_file

@get('/<name>')
def show_candidates(name):
    '''
    Present an entity and its candidate links for selection.
    '''
    # Load json data from file
    with codecs.open(abs_path + '/users/' + name + '/art.json', 'r', 'utf-8') as fh:
        data = json.load(fh)

    # Get instance index or id
    no_instances = len(data['instances'])
    last_instance = no_instances - 1

    if request.query.id:
        index = None
        for i in data['instances']:
            if i['id'] == int(request.query.id):
                index = data['instances'].index(i)
                break
        if not index:
            abort(500, 'Identifier not found in dataset.')
    elif request.query.index:
        index = int(request.query.index)
    else:
        # First instance that hasn't been linked yet
        index = 0
        for i in data['instances']:
            if not i['links']:
                index = data['instances'].index(i)
                break
    if index >= no_instances:
        index = 0
    if index <= -1:
        index = last_instance

    # Get instance data
    instance_id = data['instances'][index]['id']
    url = data['instances'][index]['url']
    ne = data['instances'][index]['ne_string']
    ne_type = data['instances'][index]['ne_type']
    links = data['instances'][index]['links']

    # Get context
    context = dac.Context(url, dac.TPTA_URL)
    ocr = re.sub(
        '(?P<pf>(^|\W|:punct:))' + re.escape(ne) + '(?P<sf>(\W|$|:punct:))',
        '\g<pf>' + '<span style="background-color:yellow;">' + ne + '</span>' +
        '\g<sf>', context.ocr)

    # Get candidates
    solr_connection = solr.SolrConnection(dac.SOLR_URL)
    cluster = dac.Cluster([dac.Entity(ne, ne_type, context)])
    if cluster.entities[0].valid:
        cand_list = dac.CandidateList(solr_connection, dac.SOLR_ROWS, cluster)
        candidates = cand_list.candidates
    else:
        candidates = []

    return template('index', last_instance=last_instance, index=index, url=url,
            ne=ne, ne_type=ne_type, links=links, publ_date=context.publ_date,
            ocr=ocr, candidates=candidates, instance_id=instance_id)

@post('/<name>')
def save_links(name):
    '''
    Save selected links for an entity to file.
    '''
    index = int(request.forms.get('index'))
    links = request.forms.getall('links')
    if 'other' in links:
        links = [l for l in links if l != 'other']
        links.append(request.forms.get('other_link'))
    action = request.forms.get('action')

    orig_file = abs_path + '/users/' + name + '/art.json'
    temp_file = abs_path + '/users/' + name + '/temp.json'

    # Load json data from file
    with open(orig_file) as fh:
        data = json.load(fh)

    # Set new link value
    data['instances'][index]['links'] = [l.decode('utf-8') for l in links]

    # Save json data to temp file
    with codecs.open(temp_file, 'w', 'utf-8') as fh:
        json.dump(data, fh, indent=4, sort_keys=True, ensure_ascii=False)

    # Check temp file existence and size
    if os.path.exists(temp_file) and (abs(os.path.getsize(orig_file) -
            os.path.getsize(temp_file)) < 15000):

        os.chmod(temp_file, 0777)
        os.remove(orig_file)
        os.rename(temp_file, orig_file)

        # Redirect to next page
        redirect_url = '../' + name

        if action == 'first':
            redirect_url += '?index=0'

        elif action == 'next_art':
            next_index = 0
            current_url = data['instances'][index]['url']
            for i in data['instances'][index:]:
                if i['url'] != current_url:
                    next_index = data['instances'].index(i)
                    break
            redirect_url += '?index=' + str(next_index)

        elif action == 'prev_art':
            next_index = -1
            current_url = data['instances'][index]['url']
            prev_url = None
            for i in reversed(data['instances'][:index]):
                if i['url'] != current_url:
                    prev_url = i['url']
                    prev_index = data['instances'].index(i)
                    next_index = 0
                    for j in reversed(data['instances'][:prev_index]):
                        if j['url'] != prev_url:
                            next_index = data['instances'].index(j) + 1
                            break
                    break
            if next_index == -1:
                prev_url = data['instances'][-1]['url']
                for i in data['instances'][::-1]:
                    if i['url'] != prev_url:
                        next_index = data['instances'].index(i) + 1
                        break

            redirect_url += '?index=' + str(next_index)

        elif action == 'next':
            redirect_url += '?index=' + str(index + 1)

        elif action == 'prev':
            redirect_url += '?index=' + str(index + -1)

        redirect(redirect_url)

    else:
        abort(500, 'Error saving data.')

@get('/<name>/edit')
def update_training_set(name):
    '''
    Add or delete an article.
    '''
    action = request.query.action
    url = request.query.url
    ne = request.query.ne

    if not action or action not in ['add', 'delete'] or not url:
        abort(500, "Invoke with ?action=[add, delete]&url=[resolver_id]")

    orig_file = abs_path + '/users/' + name + '/art.json'
    temp_file = abs_path + '/users/' + name + '/temp.json'

    # Load json data from file
    with codecs.open(orig_file, 'r', 'utf-8') as fh:
        data = json.load(fh)

    # Add article or NE
    if action == 'add':
        # Check if article and / or NE isn't included already in current set
        for i in data['instances']:
            if i['url'] == url:
                if not ne or i['ne_string'] == ne:
                    abort(500, 'Url and / or entity already part of data set.')

        # Check if article isn't included in another set
        alt_name = 'tve' if name == 'test' else 'test'
        alt_file = abs_path + '/users/' + alt_name + '/art.json'
        with codecs.open(alt_file, 'r', 'utf-8') as fh:
            alt_data = json.load(fh)
            for i in alt_data['instances']:
                if i['url'] == url:
                    abort(500, 'Url ' + url +
                        ' is already part of another data set.')

        next_id = data['instances'][-1]['id'] + 1

        if ne:
            # Add single NE
            i = {}
            i['url'] = url
            i['ne_string'] = ne
            i['ne_type'] = None
            i['links'] = []
            i['id'] = next_id
            data['instances'].append(i)
        else:
            # Add article
            tpta_file = urllib.urlopen(dac.TPTA_URL + url)
            tpta_string = tpta_file.read()
            tpta_file.close()

            root = etree.fromstring(tpta_string)
            if(len(root) > 0 and len(root[0]) > 0):
                entities = []
                next_id = data['instances'][-1]['id'] + 1
                for ent in root[0]:
                    if ent.text not in entities:
                        entities.append(ent.text)
                        i = {}
                        i['url'] = url
                        i['ne_string'] = ent.text
                        i['ne_type'] = ent.tag
                        i['links'] = []
                        i['id'] = next_id
                        next_id += 1
                        data['instances'].append(i)
            else:
                abort(500, 'No entities found for url ' + url + '.')

    # Delete article or NE
    if action == 'delete':
        # Check if article can be found
        to_remove = []
        for i in data['instances']:
            if i['url'] == url:
                if not ne or i['ne_string'] == ne:
                    to_remove.append(i)
        if not to_remove:
            abort(500, 'Url and / or entity not found in data set.')
        else:
            for i in to_remove:
                data['instances'].remove(i)

    # Save json data to temp file
    with codecs.open(temp_file, 'w', 'utf-8') as fh:
        json.dump(data, fh, indent=4, sort_keys=True, ensure_ascii=False)

    # Check temp file existence and size
    if os.path.exists(temp_file) and (abs(os.path.getsize(orig_file) -
            os.path.getsize(temp_file)) < 50000):
        os.chmod(temp_file, 0777)
        os.remove(orig_file)
        os.rename(temp_file, orig_file)
    else:
        abort(500, 'Error saving data.')

    return 'Success'

@get('/predict')
def predict():
    '''
    Get the current DAC prediction.
    '''
    linker = dac.EntityLinker(debug=True, candidates=True, model='svm')
    result = linker.link(request.query.url,
        request.query.ne.encode('utf-8'))[0]
    response.set_header('Content-Type', 'application/json')
    return result

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
