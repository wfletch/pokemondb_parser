#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
import requests
from bs4 import BeautifulSoup



db_index = 'https://pokemondb.net/pokedex/national'
html_doc = requests.get(db_index).text
soup = BeautifulSoup(html_doc, 'html.parser')
pokemon_data = {}

for gen in soup.main.find_all("div", class_="infocard-list"):
    for pokemon in gen.find_all("div", class_="infocard"):
        pokemon_span = pokemon.find_all('span')
        src_link = pokemon_span[0].a.span.get('data-src')
        name = pokemon_span[2].a.get_text()
        number = pokemon_span[2].find_all('small')[0].get_text()
        types = pokemon_span[2].find_all('small')[1].find_all('a')
        types = [t.get_text() for t in types]
        name = "-".join(name.split(" "))
        name = name.lower()
        name = name.replace("\'", '')
        name = name.replace(".", '')
        pokemon_data[name] = {
            "name": name,
            "img_link" : src_link,
            "number" : int(number[1::]),
            "types" : types
        }


json_string = json.dumps(pokemon_data)
with open('raw_data/output.json', 'w') as outfile:
    outfile.write(json_string)
#TODO: Thread this? Or find a way to batch!
for entry in pokemon_data.keys():
    link = pokemon_data[entry]['img_link']
    os.system('curl {} > images/{}.png'.format(link, entry))
