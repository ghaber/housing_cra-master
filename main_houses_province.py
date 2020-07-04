# Extracting houses data choosing in the poped window the province where you want to extract houses data.

import subprocess
import pandas as pd
import time
import sys
import os
import json
from pathlib import Path
import csv
from datetime import datetime as dt
import numpy as np
import pandas as pd

file_type = '.json'


def merge_json_files():
    debug = True
    print("\n************************************************************************************")
    print("***   AÑADO LAS FILAS QUE SON UPDATE A LA COLUMNA DELTAS DEL INMUEBLE ORIGINAL*******")
    print("*************************************************************************************\n")

    # 'houses_ibiza.json'
    original_csv = './province_houses/houses_' + province_name + file_type
    print("output_filename -> " + str(original_csv))

    # creo un dataframe de pandas con el contenido del csv
    try:
        df = pd.read_csv(original_csv)
    except pd.io.common.EmptyDataError:
        print("Json Empty")

    # creo una lista con los nombres de las columnas
    column_names = list(df.columns)


def print_stats():
    # Reviso los argumentos de entrada enviados al programa
    print("\nEjecutado script -> " + sys.argv[0] + " with " +
          str(len(sys.argv)-1) + " arguments " + str(sys.argv[1:]))
    print('province_name -> ' + province_name)

    print('Start Time -> ' + start_time)
    print('Finish Time -> ' + dt.now().strftime("%d/%m/%Y %H:%M:%S"))
    # 2020-06-12 19:39:10 [scrapy.extensions.logstats] INFO: Crawled 1479 pages (at 9 pages/min), scraped 81 items (at 1 items/min)


# Once we have all the zones/subzones/neighborhoods links in links.csv, the next step is extracting houses data.
# But, as in the web page there are stored over one million and half houses, trying to extract
# all of them in one shot would be dramatic. So instead, you choose just the provinces you want to extract,
# and the crawler starts first getting the links of each house in this province, and then,
# parsing and extracting all the relevant data from each house page.

# Probably you will get blocked during more than once(much more!) during extraction. Don't worry.
# The crawler is developed for stopping and reloading after a while whenever gets blocked.
# Additionaly, it saves all the denied houses-links and subzones-links in logHouse.txt and
# logLink.txtfiles respectively. Then, once it finishes extracting all the houses, the crawler retries
# getting this previously blocked houses data.

# -*- Load links dataframe -*-
# victor, en el caso ibiza sólo están las zonas de ibiza con menos de 1800 links
# link,num_link,obtention_date,province
# http: // idealista.com/venta-viviendas/formentera-balears-illes /, 107, 2020-06-04, balears illes
# http: // idealista.com/venta-viviendas/eivissa-balears-illes /, 938, 2020-06-04, balears illes
# http: // idealista.com/venta-viviendas/santa-eulalia-del-rio-balears-illes /, 955, 2020-06-04, balears illes
# http: // idealista.com/venta-viviendas/sant-josep-de-sa-talaia-balears-illes /, 906, 2020-06-04, balears illes
# http: // idealista.com/venta-viviendas/balears-illes/ibiza/area-de-sant-joan /, 135, 2020-06-04, balears illes
# http: // idealista.com/venta-viviendas/balears-illes/ibiza/area-de-sant-antoni /, 285, 2020-06-04, balears illes


# Reviso los argumentos de entrada enviados al programa
print("\nEjecutando script -> " + sys.argv[0] + " with " +
      str(len(sys.argv)-1) + " arguments " + str(sys.argv[1:]))
print()
start_time = dt.now().strftime("%d/%m/%Y %H:%M:%S")
print('Start Time -> ' + start_time)
# veo si hay algumentos:
if (len(sys.argv) != 2):
    print("EXIT: YOU MUST INCLUDE ONLY ONE ARGUMENT, THE PROVINCE/ISLAND NAME")
    print("EX: python main_houses_province.py ibiza")
    sys.exit()

province_name = sys.argv[1].replace("\n", "").replace("\r", "")
print('province_name -> ' + province_name)

links_file_name = './additional_csv/links_' + province_name + '.csv'

exclude = [i for i, line in enumerate(
    open(links_file_name)) if line.startswith('link')]
if len(exclude) == 1:
    all_zones = pd.read_csv(links_file_name)
else:
    all_zones = pd.read_csv(links_file_name, skiprows=exclude[1:])

# Normalize province names column:
all_zones['province'] = province_name

# -*- Extract houses from selected provinces
province = province_name

# renombro el fichero json actual a ./province_houses/houses_old_ibiza.jon
old_name = './province_houses/houses_' + province + '.json'
new_name = './province_houses/houses_old_' + province + '.json'
try:
    os.rename(old_name, new_name)
    print('Json file renamed to -> ' + new_name)
except Exception as e:
    print(old_name + ' file not renamed as not exists')
    pass

# 'num_link' solo se muestra en el texto, si hay más o menos se hace scrapping de las que haya en ese momento
num_link = sum(all_zones[all_zones['province'] == province]['num_link'])

print("\n***********************")
print(f"Crawler is ready to extract {num_link} houses from {province}")
print("***********************")
time.sleep(3)

# analizo cada subzona guardada en links_ibiza.json que no tienen mas de 1800 links cada una
for zone in all_zones.itertuples():
    print("\n***********************")
    print(f"Extracting {zone.num_link} houses from a zone of {province}")
    print("***********************\n\n")
    time.sleep(3)

    # lanzo el spider 'houses' que guardara el resultado en /province_houses/houses_"province_name".json
    command = f'scrapy crawl houses -a start={zone.link} -a my_province={province} -o ./province_houses/houses_{province}{file_type}'
    subprocess.run(command, shell=True)
    print(
        "\n********   ZONE HOUSE EXTRACTION FINISHED!   Waiting 2 seconds before reload\n")
    time.sleep(2)

# -*- Get denied links of selected province -*-
deny_link_flag = True
while deny_link_flag:
    denied_links = []
    try:
        # los links denegados estan en 'logLink.txt'
        with open('logLink.txt') as log:
            denied_links.extend(log.readlines())
            denied_links = [s.strip() for s in denied_links]
        try:
            # borro el fichero
            os.remove('logLink.txt')
        except Exception as e:
            print(e)
            # no sigo por haber error
            print("ERROR deleting denied houses links file logLink.txt")
            deny_link_flag = False
        print("\n***********************")
        print(f"Extracting denied houses links from {province}")
        print("***********************\n\n")
        print("********   Waiting 3 minutes before starting")
        time.sleep(180)

        for link in denied_links:
            # lanzo el spider 'houses' que guardara el resultado en /province_houses/houses_"province_name".json
            command_denied_link = f'scrapy crawl houses -a start={link} -a my_province={province} -o ./province_houses/houses_{province}{file_type}'
            subprocess.run(command_denied_link, shell=True)

        # -*- Check if still are denied houses -*-
        # si de nuevo hay un fichero 'logLink.txt' es que han aparecido nuevos porque lo borre anteriormente
        if os.path.isfile('logLink.txt'):
            print(
                "********   STILL ARE DENIED LINKS! Waiting 2 extra minutes before reload")
            time.sleep(120)
        else:
            deny_link_flag = False
    except Exception as e:
        print('No hay links denegados,"logLink.txt" no encontrado')
        deny_link_flag = False

# -*- Get denied houses of selected province -*-
# los houses cuyo scrpaiing fue denegado estan en 'logHouse.txt'
if os.path.isfile('logHouse.txt'):
    deny_house_flag = True
else:
    deny_house_flag = False

while deny_house_flag:
    print("\n***********************")
    print(f"Extracting denied houses links from {province}")
    print("***********************\n\n")
    print("********   Waiting 3 minutes before starting")
    time.sleep(180)
    # start-url-code to extract denied links
    denied_link = 'https://www.idealista.com/login'
    # lanzo el spider 'houses' que guardara el resultado en /province_houses/houses_"province_name".json
    command_denied_house = f'scrapy crawl houses -a start={denied_link} -a my_province={province} -o ./province_houses/houses_{province}{file_type}'
    subprocess.run(command_denied_house, shell=True)

    # -*- Check if still are denied houses -*-
    if os.path.isfile('./logHouse.txt'):
        print("********   STILL ARE DENIED HOUSES! Waiting 2 extra minutes before reload")
        time.sleep(120)
    else:
        deny_house_flag = False

#  imprimo las estadisticas
print_stats()

