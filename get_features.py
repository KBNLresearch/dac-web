import os
import sys
sys.path.insert(0, "../dac")

import disambiguation
import json


# Input and output files
with open("users/tve/art.json") as data_file:
    data = json.load(data_file)
out = open('features_training.csv', 'w')

# Header row: identifiers
ids = ['id', 'ne', 'type', 'url', 'dpb']
for i in ids:
    out.write(i + '\t')

# Header row: regular features
features = [
        'quotes',
        'found_more',
        'solr_pos',
        'cand_pos',
        'solr_score',
        'inlinks',
        'lang',
        'disambig',
        'main_title_exact_match',
        'main_title_start_match',
        'main_title_end_match',
        'main_title_match',
        'title_exact_match',
        'title_start_match',
        'title_end_match',
        'title_match',
        'last_part_match',
        'mean_levenshtein_ratio',
        'name_conflict',
        'date_match',
        'type_match',
        'role_match',
        'entity_match',
        'spec_match'
        ]

for f in features:
    out.write(f + '\t')

# Header row: label
out.write('label\n')

# Instance rows
instance_count = 0
candidate_count = 0

linker = disambiguation.EntityLinker()

for inst in data['instances']:
    print 'Reviewing instance ' + str(instance_count) + ': ' + inst['ne_string']

    # Check if instance has been labeled
    if inst['link'] != '':
        result = linker.link(inst['url'], inst['ne_string'].encode('utf-8'))
        solr_response = linker.linked[0].solr_response

        # Check if DBpedia canadidates have been retrieved
        if hasattr(solr_response, 'numFound') and solr_response.numFound > 0:

            index = 0
            for r in solr_response:

                line = ''

                # Identifiers
                line += str(candidate_count) + '\t'
                line += inst['ne_string'] + '\t'
                line += inst['ne_type'] + '\t'
                line += inst['url'] + '\t'
                line += r['id'][1:-1] + '\t'

                # Regular features
                for f in features:
                    value = getattr(linker.linked[0].descriptions[index], f)
                    if isinstance(value, float):
                        line += "{0:.5f}".format(value) + '\t'
                    else:
                        line += str(value) + '\t'

                # Label
                if r['id'][1:-1] == inst['link']:
                    line += str(1) + '\n'
                else:
                    line += str(0) + '\n'
                line = line.encode('utf-8')

                out.write(line)

                index += 1
                candidate_count += 1

    instance_count += 1

out.close()

