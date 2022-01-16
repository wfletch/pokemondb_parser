#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import json
import os
import base64
import requests
import numpy
import matplotlib.pyplot as plt
import cv2
from PIL import Image
from bs4 import BeautifulSoup
import pickle
import wget

db_index = 'https://pokemondb.net/pokedex/national'
pokedex_index = 'https://pokemondb.net/pokedex/'
html_doc = requests.get(db_index).text
soup = BeautifulSoup(html_doc, 'html.parser')
pokemon_data = {}

def get_all_pokemon_data(gen='all'):
    #TODO: Pick Specific Generations
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
            break
        break
            # TODO: Get Link To Individual Entry and get Large Photo
        
def write_object_to_disk():
    json_string = json.dumps(pokemon_data)
    with open('output/output.json', 'w') as outfile:
        outfile.write(json_string)

def write_to_disk():
    #TODO: Thread this? Or find a way to batch!
    #TODO: Set Custom Download Location
    download_to_disk = False
    if download_to_disk:
        for entry in pokemon_data.keys():
            link = pokemon_data[entry]['img_link']
            os.system('curl {} > images/{}.png'.format(link, entry))
    else:
        for entry in pokemon_data.keys():
            link = pokemon_data[entry]['img_link']
            print(link)
            data = wget.download(link)
            np_image = cv2.imread(data)
            pokemon_data[name]['img_b64'] = base64.b64encode(pickle.dumps(data, protocol=0))

