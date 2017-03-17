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

import json
import os
import sys

sys.path.insert(0, "../dac")

import dac

import unicodecsv as csv

from pprint import pprint

features = [
    'pref_label_exact_match', 'pref_label_end_match', 'pref_label_match',
    'alt_label_exact_match', 'alt_label_end_match', 'alt_label_match',
    'last_part_match', 'levenshtein_ratio', 'name_conflict', 'date_match',
    'solr_iteration', 'solr_position', 'solr_score', 'inlinks', 'lang',
    'ambig', 'quotes', 'type_match', 'role_match', 'spec_match',
    'keyword_match', 'subject_match', 'entity_match'
]
metadata = ['inst_id', 'cand_id', 'url', 'ne', 'type', 'link']
label = ['label']

def generate():
    '''
    Generate a training data set based on the manually labeled examples from
    the training web interface.
    '''
    with open("users/tve/art.json") as fh:
        data = json.load(fh)

    with open('training.csv', 'w') as fh:
        csv_writer = csv.writer(fh, delimiter='\t', encoding='utf-8')
        csv_writer.writerow(metadata + features + label)

        linker = dac.EntityLinker(debug=True, candidates=True, training=True)

        instance_count = 0
        candidate_count = 0

        for inst in data['instances']:
            print('Reviewing instance ' + str(instance_count) + ':')
            print(inst['ne_string'].encode('utf-8'))

            # Check if instance has been labeled
            if inst['link'] != '':
                result = linker.link(inst['url'],
                    inst['ne_string'].encode('utf-8'))[0]

                # Check if DBpedia canadidates have been retrieved
                if 'candidates' in result:

                    for cand in result['candidates']:

                        row = []

                        # Metadata
                        row.append(str(instance_count))
                        row.append(str(candidate_count))
                        row.append(inst['url'])
                        row.append(inst['ne_string'].encode('utf-8'))
                        row.append(inst['ne_type'])
                        row.append(cand['id'].encode('utf-8'))

                        # Features
                        for f in features:
                            value = cand['features'][f]
                            row.append("{0:.3f}".format(float(value)))

                        # Label
                        if cand['id'] == inst['link']:
                            row.append(str(1))
                        else:
                            row.append(str(0))

                        # Exclude name and date conflicts
                        if cand['features']['name_conflict'] == 1:
                            continue
                        elif cand['features']['date_match'] == -1:
                            continue
                        else:
                            candidate_count += 1
                            csv_writer.writerow(row)

            instance_count += 1

if __name__ == '__main__':
    generate()

