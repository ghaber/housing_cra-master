# Extracting all the zones/subzones links

from pathlib import Path
import subprocess
import pandas as pd
import time
import os
import sys

# In idealista.com there is data from over 50 Spain provinces. On the other hand,
# there are 2 main choices for each one: Renting or Selling. Every combination has
# it’s own path, so the first thing the crawler does is to extract all this links and
# save them into a csv file called zones.csv. This task is carried out by the GetZones spider.

# Reviso los argumentos de entrada enviados al programa
print("Ejecutando script -> " + sys.argv[0] + " with " + str(len(sys.argv)-1) + " arguments " + str(sys.argv[1:]))
print()
# veo si hay algumentos:
if (len(sys.argv)!=2):
    print("EXIT: YOU MUST INCLUDE ONLY ONE ARGUMENT, THE PROVINCE/ISLAND NAME")
    print("ex:   python main_links_province.py ibiza")
    sys.exit()

province_name = sys.argv[1].replace("\n", "").replace("\r", "")
print('province_name -> ' + province_name)

# -*- Load zone dataframe -*-

#borro y creo el fichero \additional_csv\zones_ibiza.csv en el que tengo las zonas a escrapear en el que ya he tenido en cuenta que sólo se pueden obtener 1.800 links, por lo que aquí lo he subdividido. Queda un fichero de las zonas a escrapear de ibiza:

#    link, num_link, obtention_date, province
#    https: // idealista.com/venta-viviendas/formentera-balears-illes /, 107, 2020-06-04, balears illes
#    https: // idealista.com/venta-viviendas/eivissa-balears-illes /, 938, 2020-06-04, balears illes
#    https: // idealista.com/venta-viviendas/santa-eulalia-del-rio-balears-illes /, 955, 2020-06-04, balears illes
#    https: // idealista.com/venta-viviendas/sant-josep-de-sa-talaia-balears-illes /, 906, 2020-06-04, balears illes
#    https: // idealista.com/venta-viviendas/balears-illes/ibiza/area-de-sant-joan /, 135, 2020-06-04, balears illes
#    https: // idealista.com/venta-viviendas/balears-illes/ibiza/area-de-sant-antoni /, 285, 2020-06-04, balears illes


# saco el el link de inico de mi provincia de \additional_csv\provinces.csv
# province_name, url
# A Coruña, https: // www.idealista.com/venta-viviendas/a-coruna-provincia/mapa/
# Ibiza, https: // www.idealista.com/venta-viviendas/balears-illes/ibiza/mapa
all_provinces = pd.read_csv('./additional_csv/provinces.csv', delimiter=',')
# read row line by line
province_link = ''
for row in all_provinces.values:
    # read column by index
    if row[0].lower() == province_name:
        province_link = row[1].lower().replace("\n", "").replace("\r", "")
        print('province_link -> ' + province_link)
        break
if province_link == '':
    print("EXIT: PROVINCE NAME NOT FOUND IN FILE ./additional_csv/provinces.csv")
    sys.exit()

# Besides, is not possible to extract over 1.800 houses from each province main-page.
# Since there are provinces which have around 50.000 or 70.000 houses, this approach is not enough.
# So, instead of extracting houses from the main province link, the crawler sniffs all the subzones
# of each province and saves the links just if they have up to 1.800 houses.
# If there is a subzone wich has more than 1.800 houses, the crawler dives into this subzone
# and extracts links of each neighborhood. This task is made by the spider GetLinks, and all
# the extracted links are saved into links_ibiza.csv file.

# -*- Get all the links -*

# borro el fichero ./additional_csv/links_ibiza.csv si existe
try:
    os.remove('./additional_csv/links_' + province_name + '.csv')
    print('Deleted output_links_file -> ./additional_csv/links_' + province_name + '.csv')
except Exception as e:
    print('output_links_file not deleted as not exists -> ./additional_csv/links_' + province_name + '.csv')
    pass

print("\n***********************")
print(f"Extracting selling houses links from {province_link}")
print("***********************\n")
time.sleep(3)

# ejecuto el spider getLinks y guardo el resultado el el fichero links.csv
command_links = f'scrapy crawl getLinks -a start={province_link} -a my_province={province_name} -o ./additional_csv/links_{province_name}.csv'
#command_links = ["scrapy", "crawl", "getLinks", output_str, "-a","start={0}".format(province_link), "-a", "my_province={0}".format(province_name)]
subprocess.run(command_links, shell=True)

print("********   PROVINCE LINK EXTRACTION FINISHED!")

# -*- Get all the denied links -*-
denied_flag = True
while denied_flag:
    denied_links = []
    try:
        with open('logLink.txt') as log:
            denied_links = log.readlines()
            denied_links = [s.strip() for s in denied_links]
        try:
            os.remove('logLink.txt')
        except:
            denied_flag = False

        print("\n***********************")
        print(f"Extracting denied {len(denied_links)} houses links")
        print("***********************\n\n")
        time.sleep(3)

        for link in denied_links:
            command_denied = f'scrapy crawl getLinks -a start={link} -o ./additional_csv/links.csv'
            subprocess.run(command_denied, shell=True)

        # -*- Check if still are denied links -*-
        if os.path.isfile('./logLink.txt'):
            print(
                "********   STILL ARE DENIED LINKS! Waiting 3 minutes before restarting extraction")
            time.sleep(180)
        else:
            denied_flag = False
    except:
        denied_flag = False
