import json

with open('../users/jlo/art.json') as data_file:
    art = json.load(data_file)


for i in range(len(art['instances'])):
    if i > 500:
        art['instances'][i]['link'] = ''

out_file = open('../users/jlo/art_new.json', 'w')
json_data = json.dumps(art)
out_file.write(json_data)
out_file.close()
