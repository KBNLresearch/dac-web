#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

with open('../users/test/art.json') as fh:
    art = json.load(fh)

for i, a in enumerate(art['instances']):
    a['id'] -= 1
    #a['links'] = [a['link']] if a['link'] else []
    #del a['link']

with open('../users/test/art_new.json', 'w', encoding='utf-8') as fh:
    json.dump(art, fh, indent=4, ensure_ascii=False)
