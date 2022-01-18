#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import json
import os
import base64
import requests
import numpy as np
import matplotlib.pyplot as plt
import cv2
import urllib3
from PIL import Image
from bs4 import BeautifulSoup
import pickle
import wget
import imageio

db_index = 'https://pokemondb.net/pokedex/national'
pokedex_index = 'https://pokemondb.net/pokedex/'
pokemon_data = {}

# Helper Function blatently stolen (with love) from
# https://stackoverflow.com/questions/50331463/convert-rgba-to-rgb-in-python
def rgba2rgb( rgba, background=(255,255,255) ):
    row, col, ch = rgba.shape

    if ch == 3:
        return rgba

    assert ch == 4, 'RGBA image has 4 channels.'

    rgb = np.zeros( (row, col, 3), dtype='float32' )
    r, g, b, a = rgba[:,:,0], rgba[:,:,1], rgba[:,:,2], rgba[:,:,3]

    a = np.asarray( a, dtype='float32' ) / 255.0

    R, G, B = background

    rgb[:,:,0] = r * a + (1.0 - a) * R
    rgb[:,:,1] = g * a + (1.0 - a) * G
    rgb[:,:,2] = b * a + (1.0 - a) * B

    return np.asarray( rgb, dtype='uint8' )

class PokemonScrapper():
    def scrape_pokemon_data(gen='all', deep=False):
        """scrape Pokemon data from pokemondb.net
        gen='all' by default. Set Gen = GENNUM for specific generation only
        deep='False' by default. Set deep = TRUE to get additional data about each pokemon"""
        html_doc = requests.get(db_index).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        target_gen = gen
        current_gen = 1

        for gen in soup.main.find_all("div", class_="infocard-list"):
            for pokemon in gen.find_all("div", class_="infocard"):
                if target_gen != 'all' and current_gen != target_gen:
                    current_gen +=1
                    continue
                pokemon_span = pokemon.find_all('span')
                src_link = pokemon_span[0].a.span.get('data-src')
                name = pokemon_span[2].a.get_text()
                number = pokemon_span[2].find_all('small')[0].get_text()
                types = pokemon_span[2].find_all('small')[1].find_all('a')
                types = [t.get_text() for t in types]
                # Format Pokemon name
                name = "-".join(name.split(" "))
                name = name.lower()
                name = name.replace("\'", '')
                name = name.replace(".", '')

                # Add Data about this Pokemon
                pokemon_data[name] = {
                    "name": name,
                    "img_link" : src_link,
                    "number" : int(number[1::]),
                    "types" : types,
                    "generation": current_gen
                }
                if deep:
                    # TODO: Get Link To Individual Entry and get Large Photo
                    pass
                current_gen +=1
            
    def save_object():
        # TODO: Allow the user to set directory she wants to save to
        json_string = json.dumps(pokemon_data)
        with open('output/output.json', 'w') as outfile:
            outfile.write(json_string)

    def save_images():
        pass

    def get_pokemon_images(save_to_object=True, download_to_disk=False):
        #TODO: Thread this? Or find a way to batch!
        #TODO: Set Custom Download Location
        http = urllib3.PoolManager()
        for entry in pokemon_data.keys():
            link = pokemon_data[entry]['img_link']

            # Bypass 403 by pretending to be a browser
            resp = http.request(
                "GET",
                link,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
                }
            )
            img_array = np.array(bytearray(resp.data), dtype=numpy.uint8)
            img = cv2.imdecode(img_array, -1)
            if download_to_disk:
                cv2.imwrite("test_images/{}.png".format(entry), rgba2rgb(img))
            if save_to_object:
                pokemon_data[entry]['np_array'] = rgba2rgb(img).tolist()

    def get_pokemon_info():
        if pokemon_data == {}:
            raise Exception("No Pokemon Info Scrapped. Run scrape_pokemon_data() first")
        return pokemon_data

