import json

with open('../users/jlo/art.json') as data_file:
    art_old = json.load(data_file)

with open('art_training.json') as data_file_2:
    art_new = json.load(data_file_2)

for i_new in art_new['instances']:
    for i_old in art_old['instances']:
        if i_old['url'] == i_new['url'] and i_old['ne_string'] == i_new['ne_string'] and i_old['ne_type'] == i_new['ne_type']:
            i_new['link'] = i_old['link']

out_file = open('../users/jlo/art_new.json', 'w')
json_data = json.dumps(art_new)
out_file.write(json_data)
out_file.close()
