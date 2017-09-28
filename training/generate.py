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
import sys

sys.path.insert(0, '../../dac')

import dac

import unicodecsv as csv

features = [
    'pref_label_exact_match', 'pref_label_end_match', 'pref_label_match',
    'alt_label_exact_match', 'alt_label_end_match', 'alt_label_match',
    'last_part_match', 'non_matching_labels', 'name_conflict', 'pref_lsr',
    'mean_lsr', 'date_match', 'query_id_0', 'query_id_1', 'query_id_2',
    'query_id_3', 'substitution', 'solr_position', 'solr_score', 'inlinks',
    'inlinks_rel', 'outlinks', 'outlinks_rel', 'inlinks_newspapers',
    'inlinks_newspapers_rel', 'lang', 'ambig', 'quotes', 'type_match',
    'role_match', 'spec_match', 'keyword_match', 'subject_match',
    'entity_match', 'entity_similarity', 'entity_similarity_top',
    'entity_similarity_mean', 'max_vec_sim', 'mean_vec_sim', 'vec_match'
]

metadata = ['entity_id', 'cand_id', 'url', 'ne', 'cand_uri']
label = ['label']

def generate():
    '''
    Generate a training data set based on the manually labeled examples from
    the training web interface.
    '''
    with open('../users/tve/art.json') as fh:
        data = json.load(fh)

    with open('training.csv', 'w') as fh:
        csv_writer = csv.writer(fh, delimiter='\t', encoding='utf-8')
        csv_writer.writerow(metadata + features + label)

        linker = dac.EntityLinker(debug=True, candidates=True, train=True)

        instance_count = 0
        candidate_count = 0

        url = None
        url_result = None

        for inst in data['instances']:
            print('Reviewing instance ' + str(instance_count) + ': ' +
                inst['ne_string'].encode('utf-8'))

            # Check if instance has been labeled
            if inst['links']:
                if inst['url'] != url:
                    print('Getting result for url: ' + inst['url'])
                    url = inst['url']
                    #print(linker.link(inst['url']))

                    url_result = linker.link(inst['url'])['linkedNEs']

                result = [r for r in url_result
                    if r['text'] == inst['ne_string']]
                if len(result) != 1:
                    print('No result for: ' + inst['ne_string'])
                    continue
                else:
                    result = result[0]

                # Check if DBpedia canadidates have been retrieved
                if 'candidates' in result:

                    for cand in result['candidates']:

                        row = []

                        # Metadata
                        row.append(str(inst['id']))
                        row.append(str(candidate_count))
                        row.append(inst['url'].encode('utf-8'))
                        row.append(inst['ne_string'].encode('utf-8'))
                        row.append(cand['id'].encode('utf-8'))

                        # Features
                        for f in features:
                            value = cand['features'][f]
                            row.append("{0:.3f}".format(float(value)))

                        # Label
                        if cand['id'] in inst['links']:
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

