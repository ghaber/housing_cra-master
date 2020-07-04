# -*- coding: utf-8 -*-
from sys import platform
import scrapy
import re
import PIL
import csv
from datetime import datetime as dt
import time
import sys
import os
import json
from housing_cra.items import House
import locale
import numpy as np
import pandas as pd
from pathlib import Path
from urllib.parse import urlparse
from scrapy.utils.project import get_project_settings
from random import randrange


# Si quiero registrar las propiedes nuevas en el campo 'other_prop'
register_undefined = True
# Si quiero extra info para debug de las propiedades
print_properties = False

sys.path.append(os.getcwd() + '/housing_cra')

# Victor: En windows hay que cambiarlo por 'esp'
if platform == "win32":
    # Windows...
    locale.setlocale(locale.LC_ALL, 'esp')
else:
    locale.setlocale(locale.LC_ALL, 'es_ES')

default_url = 'https://www.idealista.com'
# lista en la que guardará cada link a cada inmueble
houses_links = []


class HousesSpider(scrapy.Spider):

    def __init__(self, start, my_province):

        # guardo en la variable self el valor de province para poder usarlo globalmente
        self.province = my_province

        # cojo la lista de los links que vienen como argumento
        self.start_urls = [start]

        self.num_links_processed = 0  # el contador

        # pinto los argumentos
        print("province -> " + str(self.province))
        print("start_urls -> " + str(self.start_urls))
        settings = get_project_settings()
        #print(settings.get('DEFAULT_REQUEST_HEADERS'))
        #print("Your USER_AGENT is: " + settings.get('USER_AGENT'))

    name = 'houses'
    allowed_domains = ['idealista.com', 'www.idealista.com/inmueble/']

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse(self, response):
        # los redefino porque no las coge de globales
        logHouse_filename = './province_houses/logHouse_' + self.province + '.txt'

        # start-url chosen to indicate we pretend extract denied houses
        d_house = 'https://www.idealista.com/login'

        # -*- Check if we pretend to extract denied houses -*-
        if self.start_urls[0] == d_house:
            try:
                denied_links = []
                with open(logHouse_filename, 'a') as log:
                    denied_links.extend(log.readlines())
                    denied_links = [s.strip() for s in denied_links]
                try:
                    os.remove(logHouse_filename)
                except Exception as e:
                    print("ex20 -> " + str(e))

                for link in denied_links:
                    # añado al fichero en el que guardo los links activos en el dia de hoy
                    # la columna es un entero al igual que la que guardo en el csv
                    self.num_links_processed = self.num_links_processed + 1
                    my_house_id = re.findall("\d+", str(link))[0]

                    # sigo los links de cada inmueble
                    # le paso la provincia como argumento
                    yield response.follow(link, callback=self.parse_features, meta={'my_province': self.province, 'num_links_processed': self.num_links_processed})

            except Exception as e:
                print("ex21 -> " + str(e))

        # -*- Extract houses when regular case (not denied houses) -*-
        else:
            info_flats_xpath = response.xpath(
                "//*[@class='item-info-container']")
            # # añado a default_url que es https://www.idealista.com/inmueble/86681016/
            # lo que obtengo en cada paginacion dentro del /@ref que es '/inmueble/86681016/
            # y meto en los  houses_links el link sacado de cada inmueble del tipo
            # https://www.idealista.com/inmueble/86681016/
            houses_links.extend([str(''.join(
                default_url + link.xpath('a/@href').extract().pop())) for link in info_flats_xpath])

            # guardo el enlace a la siguiente pagina dentro de esta zona, que lo saco del link a la palabra siguiente en la web
            next_page_url = response.xpath(
                "//a[@class='icon-arrow-right-after']/@href").extract()

            # si no hay más paginas, por tanto es la ultima la que estoy analizando
            # empiezo a scrapear cada uno de los links que tengo en houses_links
            if not next_page_url:
                for house in houses_links:
                    self.num_links_processed = self.num_links_processed + 1
                    # añado al fichero en el que guardo los links activos en el dia de hoy
                    # la columna es un entero al igual que la que guardo en el csv
                    my_house_id = re.findall("\d+", str(house))[0]
                    #print('Processing link ' + str(self. num_links_processed) + ' id ' + my_house_id)

                    # sigo los links de cada inmueble
                    # le paso la provincia como argumento
                    yield response.follow(house, callback=self.parse_features, meta={'my_province': self.province, 'num_links_processed': self.num_links_processed})

            # lanzo el parse de la siguiente pagina con lo que vuelvo arriba de este bloque y empiezo otra página
            # si hay error meto los denegados en 'logHouse.txt' para reintentar
            else:
                yield response.follow(next_page_url[0], callback=self.parse, errback=self.parse_deny)

    # ----------------------------------------------------------- #
    # If a 403 response is received while browsing the pages   -- #
    # in the link collection, save all the houses stored in    -- #
    # 'houses_links' list after quiting                        -- #
    # ----------------------------------------------------------- #

    def parse_deny(self, response):
        # los redefino porque no las coge de globales
        logHouse_filename = './province_houses/logHouse_' + self.province + '.txt'
        with open(logHouse_filename, 'a') as log:
            for house in houses_links:
                log.write(house+'\n')

    # ------------------------------------------------------------------------- #
    # Esta es la función principal dónde le envio el codigo html en 'response'  #
    # ------------------------------------------------------------------------- #
    def parse_features(self, response):
        # cojo el parametro pasado
        my_province = response.meta['my_province']
        # cojo el parametro pasado
        num_links_processed = response.meta['num_links_processed']
        # Set to zero Extra House Equipments
        # Este objeto está definido en items.py
        house = House(
            storage_room=0,
            built_in_wardrobe=0,
            terrace=0,
            balcony=0,
            garden=0,
            chimney=0,
            air_conditioner=0,
            reduced_mobility=0,
            swimming_pool=0,
            green_zone=0,  # victor adds it
            active=1,  # victor adds it
        )

        # -*- ad description -*-
        # victor puede que haya dos cadenas y habria que unirlas
        try:

            tmp_str = response.xpath(
                "//div[@class='adCommentsLanguage expandable']/text()").extract()
            # print(str(tmp_str))
            # ME DEVUELVE UNA LISTA DE STRING SEPARADAS POR COMAS QUE UNO
            separator = ','
            sent_str = separator.join(tmp_str)
            # print(sent_str)
            # print(str(house['ad_description']))
            # quito comillas, y saltos de lineas
            house['ad_description'] = sent_str.replace(
                '"', '').replace('/n', '').replace('/r', '').strip()
            # reemplazo comas y puntos y comas por puntos para el csv
            house['ad_description'] = house['ad_description'].replace(
                ',', '.').replace(';', '.')
            # print(str(house['ad_description']))
        except Exception as e:
            print("        ex1 -> " + str(e))

        # -*- metadata -*-
        ad_last_update_txt = (response.xpath("//div[@class='ide-box-detail overlay-box mb-jumbo']/p/text()")
                              .extract()[0])
        # victor: aqui tenemos dos opciones
        # Anuncio actualizado el 20 de mayo o cualquier otra fecha
        # más de 5 meses sin actualizar
        # obtengo un objeto datetime tipo 06/06/2020
        house['ad_last_update'] = get_update_date(ad_last_update_txt)

        # obtengo un objeto datetime tipo 06/06/2020
        house['obtention_date'] = dt.now().date()

        # -*- location -*-
        house['loc_full'] = response.xpath(
            "//div[@class='clearfix']/ul/li/text()").extract()
        # Calle de la Mar, 2
        # Formentera
        # Balears (Illes)
        # print(*house['loc_full'], sep = ", ")
        try:
            house['loc_zone'] = house['loc_full'][-1].strip()
            try:
                house['loc_city'] = house['loc_full'][-2].strip()
                try:
                    house['loc_district'] = house['loc_full'][-3].strip()
                    try:
                        house['loc_neigh'] = house['loc_full'][-4].strip()
                        try:
                            house['loc_street'] = house['loc_full'][-5].strip()
                        except Exception as e:
                            pass
                            #print("        ex.loc_street -> " + str(e))
                    except Exception as e:
                        pass
                        #print("        ex.loc_neigh -> " + str(e))
                except Exception as e:
                    pass
                    #print("        ex.loc_district -> " + str(e))
            except Exception as e:
                pass
                #print("        ex.loc_city -> " + str(e))
        except Exception as e:
            pass
            #print("        ex.loc_zone -> " + str(e))

        # -*- some features -*-
        house['price'] = int(response.xpath(
            "//span[@class='txt-bold']/text()").extract()[0].replace(".", ""))
        house['house_type'] = (response.xpath(
            "//span[@class='main-info__title-main']""/text()").extract()[0].split(" en ")[0])
        house['house_id'] = get_number(response.xpath("//ul[@class='lang-selector--lang-options']/li/a/@href")
                                       .extract()[0])

        # -*- house properties from raw text -*-
        # hay varias 'details-property_features'
        properties = response.xpath(
            "//*[@class='details-property_features']/ul/li/text()").extract()
        house = get_all_properties(house, properties)

        # -*- Print Extracted properties (Raw Text) -*-
        # --> True for printing extracted properties (testing)
        if print_properties:
            print("----  PROPERTIES -----")
            i = 0
            for prop in properties:
                i += 1
                print(f"{i}. feature: {prop}")
            print("-----------------------")

        # victor :active # cuando el anuncio no aparezca en la busqueda se pone "0"
        # si he llegado hasta aquí es que está activo
        house['active'] = 1

        # victor. Capturo el numero de imagenes
        # guardo todo el script en la variable script. Cuento el numero de fotos que hay.
        my_script = response.xpath(
            "//script[contains(., 'fullScreenGalleryPics')]/text()").getall()[0]
        # como salen dos veces cada foto
        num_images = int(my_script.count("imageDataService") / 2)
        house['num_images'] = num_images
        #print("num_images-> ", num_images)

        # extraido cada url del codigo del script
        # esta entre el text 'imageDataService:"' y la coma.
        my_urls = re.findall(r'imageDataService:"(.*?)\,', my_script)
        # for i in range(num_images):
        #print("image_url[" + str(i) + "]-> " + my_urls[i])
        # ahora tengo una lista con todas las urls.

        # the spider will return a dict with the image_urls for the Images Pipeline.
        # first num_images elements of this list
        # en la web hay el doble de imagenes pero solo cojo la mitad

        # dd/mm/YY H:M:S
        dt_string = dt.now().strftime("%d/%m/%Y %H:%M:%S")

        # compruebo si el archivo esta ya en el fichero csv o no
        images_list = []
        # Devuelvo 1 si el link estaba en el csv y la lista de imagenes
        # Devuelvo 0 si el link no estaba en el csv
        # Devuelvo -1 si el link estaba más de una vez en el csv
        found_n_times, images_list = check_link(house['house_id'], my_province)

        # printing lists separated by commas
        # print(*images_list, sep = ", ")

        # me devuelve images_list, una lista con todas las imagenes ya descargadas en anteriores ocasiones
        # me quedo con las imagenes nuevas que acabo de obtener
        # my_urls[:num_images] -> aqui tengo las que acabo de obtener
        # images_list -> las anteriores
        # set reduces the lookup time from O(n) to O(1)
        set_1 = set(images_list)
        image_list_new = [
            item for item in my_urls[:num_images] if item not in set_1]

        if found_n_times == 0:
            # si estoy aquí es un inmueble nuevo, no se encontro el house_id en el csv
            print(str(num_links_processed).zfill(4) + ' - This house_id ' +
                  str(house['house_id']) + ' is new, not found in csv')
            house['image_urls'] = my_urls[:num_images]
            house['image_urls_update'] = []
            house['update'] = 0
            # {'timestamp': “12/06/2020 17:18:28”, 'action': 'enabled'}
            delta_dict = {}
            delta_dict['timestamp'] = dt_string
            delta_dict['action'] = 'enabled'
            house['delta'] = delta_dict
            #house['delta'] = '{"timestamp": “' + dt_string + '”, “action”: "enabled"}'

        else:
            # es un update, descargo solo las que no he descargado ya
            num_new_images = len(image_list_new)
            if num_new_images == 0:
                print(str(num_links_processed).zfill(4) + ' - This house_id ' + str(house['house_id']) +
                      ' found ' + str(found_n_times) + ' times in csv. ZERO NEW IMAGES FOUND')
            else:
                print(str(num_links_processed).zfill(4) + ' - his house_id ' + str(house['house_id']) +
                      ' found ' + str(found_n_times) + ' times in csv. ' + str(num_new_images) + ' NEW IMAGES FOUND')
            house['image_urls'] = image_list_new
            # y en esta columna guardo la lista completa que ha llegado
            house['image_urls_update'] = my_urls[:num_images]
            house['update'] = 1
            # {'timestamp': “12/06/2020 17:18:28”, 'action': 'updated'}
            delta_dict = {}
            delta_dict['timestamp'] = dt_string
            delta_dict['action'] = 'updated'
            house['delta'] = delta_dict
            #house['delta'] = '{"timestamp": “' + dt_string + '”, “action”: "updated"}'

        # salgo devolviendo el objeto house
        yield house

# ----------------------------------------------------------- #
# ---- *   FUNCTIONS TO EXTRACT FEATURES FROM PROPERTIES  * --#
# ----------------------------------------------------------- #


def get_all_properties(house, properties):
    for prop in properties:
        prop = prop.lower().strip()

        # *-* lift *-*
        if match_property(prop, ['ascensor']):
            house['lift'] = check_property(
                prop, ['con'])   # 0: no lift ; 1: with lift

        # *-* bath number *-*
        elif match_property(prop, ['baño']):
            try:
                house['bath_num'] = get_number(prop)
            except Exception as e:
                print("        ex.bath_num -> " + str(e))
                house['bath_num'] = prop

        # *-* construction date *-*
        elif match_property(prop, ['construido en']):
            try:
                house['construct_date'] = get_number(prop)
            except Exception as e:
                print("        ex.construct_date -> " + str(e))
                house['construct_date'] = prop

        # *-* storage room *-*
        elif match_property(prop, ['trastero']):
            # 0: no storage room ; 1: with storage room
            house['storage_room'] = 1

        # *-* orientation of the house *-*
        elif match_property(prop, ['orientación']):
            house['orientation'] = prop.split(' ', maxsplit=1)[1].strip()

        # *-* energetic certification of the house *-*
        elif match_property(prop, ['certific']):
            house['energetic_certif'] = prop.split(':')[1].strip()

        # *-* flat floor *-*
        elif match_property(prop, ['bajo', 'planta', 'interior', 'exterior']):
            house['floor'] = prop

        # *-* room number *-*
        elif match_property(prop, ['habitaci']):
            try:
                house['room_num'] = get_number(prop)
            except:
                house['room_num'] = prop
        # miramos antes parcela porque sino detectara los m2 y se metera en esta
        # *-* ground_size *-*
        elif match_property(prop, ['parcela']):
            try:
                house['ground_size'] = get_number(prop)
            except:
                house['ground_size'] = prop
        # *-* m2 of the house *-*
        elif match_property(prop, ['m²']):
            # print(str(prop))
            try:
                house['m2_real'] = get_number(prop.split(',')[0])
                try:
                    house['m2_useful'] = get_number(prop.split(',')[1])
                except Exception as e:
                    #print("        ex.m2_useful -> " + str(e))
                    pass
            except Exception as e:
                #print("        ex.m2_real -> " + str(e))
                house['m2_real'] = prop

        # *-* condition of the house *-*
        elif match_property(prop, ['segunda mano', 'promoción de obra nueva']):
            house['condition'] = prop

        # *-* built in wardrobe *-*
        elif match_property(prop, ['armarios empotrados']):
            house['built_in_wardrobe'] = 1

        # *-* terrace *-*f
        elif match_property(prop, ['terraza']):
            house['terrace'] = 1

        # *-* balcony *-*
        elif match_property(prop, ['balcón']):
            house['balcony'] = 1

        # *-* garden *-*
        elif match_property(prop, ['jardín']):
            house['garden'] = 1

        # *-* garage *-*
        elif match_property(prop, ['garaje']):
            house['garage'] = prop

        # *-* heating *-*
        elif match_property(prop, ['calefacción']):
            house['heating'] = prop

        # *-* chimney *-*
        elif match_property(prop, ['chimenea']):
            house['chimney'] = 1

        # *-* air_conditioner *-*
        elif match_property(prop, ['aire acondicionado']):
            house['air_conditioner'] = 1

        # *-* reduced_mobility *-*
        elif match_property(prop, ['movilidad reducida']):
            house['reduced_mobility'] = 1

        # *-* swimming_pool *-*
        elif match_property(prop, ['piscina']):
            house['swimming_pool'] = 1

        # *-* victor: zonas verdes *-*
        elif match_property(prop, ['zonas verdes']):
            house['green_zone'] = 1

        # *-* kitchen & unfurnished *-*
        elif match_property(prop, ['cocina']):
            house['kitchen'] = 1
            if match_property(prop, ['sin amueblar']):
                house['unfurnished'] = 1

        elif match_property(prop, ['sin amueblar']):
            house['unfurnished'] = 1
            if match_property(prop, ['cocina']):
                house['kitchen'] = 1

        # *-* house type redundancy *-*
        elif match_property(prop, ['chalet', 'finca', 'casa', 'caserón', 'palacio']):
            pass

        else:
            # -*- Register undefined properties not included yet -*-
            # ---> True for register undefined properties (testing)
            if register_undefined:
                with open('undefined_props.csv', 'a') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow([prop])
                csvFile.close()
                # victor, añado al campo 'other_prop' las propiedades que aparezcan nuevas
                print("New property detected, added to other_prop field")
                house['other_prop'] = house['other_prop'] + [prop]
    return house

    # ----------------------------------------------------------- #


def match_property(property, patterns):
    for pat in patterns:
        match_prop = re.search(pat, property)
        if match_prop is not None:
            return True
    return False


def check_property(property, patterns):
    for pat in patterns:
        check = re.search(pat, property)
        if check:
            return 1
    return 0


def get_number(property):
    nums = re.findall(r'\d+', property)
    if len(nums) == 2:
        # '40.000' ->   '40' + '000'  -> '40000'  ->  40000
        return int(nums[0]+nums[1])
    else:
        return int(nums[0])

# victor: aqui tenemos dos opciones
# Anuncio actualizado el 20 de mayo o cualquier otra fecha
# más de 5 meses sin actualizar


def get_update_date(property):
    if property == 'más de 5 meses sin actualizar':
        # lo convierto a dt.now().date() -> 01/01/2000 para qwue sepamos es más de 5 meses
        x = dt(2000, 1, 1).date()
    else:
        temp = property.replace('Anuncio actualizado el ', '').strip()
        temp = temp.replace('de ', '').strip()
        # aqui me queda 20 mayo
        temp_date = temp.split()
        # aqui me queda ['20', 'mayo']
        day = int(temp_date[0])
        month = temp_date[1]
        if month == "enero":
            month_num = 1
        elif month == "febrero":
            month_num = 2
        elif month == "marzo":
            month_num = 3
        elif month == "abril":
            month_num = 4
        elif month == "mayo":
            month_num = 5
        elif month == "junio":
            month_num = 6
        elif month == "julio":
            month_num = 7
        elif month == "agosto":
            month_num = 8
        elif month == "septiembre":
            month_num = 9
        elif month == "octubre":
            month_num = 10
        elif month == "noviembre":
            month_num = 11
        elif month == "diciembre":
            month_num = 12
        # obtengo el año
        current_year = int(dt.now().date().year)
        current_month = int(dt.now().date().month)
        current_day = int(dt.now().date().day)
        # veo si es de este año o del anterior
        if current_month > month_num:
            year = current_year
        elif current_month < month_num:
            year = current_year - 1
        else:
            # si el mes coincide compruebo el mes
            if current_day > day:
                year = current_year
            elif current_day < day:
                year = current_year - 1
            else:
                # aqui coincide mes y dia
                year = current_year
        # lo convierto a dt.now().date() -> 06/06/2020
        x = dt(year, month_num, day).date()
    return x


# ----------------------------------------------------------- #
# ---- *   CHEQUEO SI SE EL LINK ESTABA YA O NO           * --#
# ----------------------------------------------------------- #
# Devuelvo 1 si el link estaba en el csv
# Devuelvo 0 si el link no estaba en el csv
# Devuelvo -1 si el link estaba más de una vez en el csv
def check_link(my_house_id, my_province):
    debug = False
    # house contiene el house_id del inmueble a descargar
    # house_link = 'https://www.idealista.com/inmueble/89768744/'
    # my_house_id es un string '89768744'

    if debug:
        print("Entering function check_link with house_id -> " + str(my_house_id))

    # en la variable output_filename tengo la ruta del fichero './province_houses/houses_old_ibiza.json'
    output_filename = './province_houses/houses_old_' + my_province + '.json'
    if debug:
        print("333 output_filename -> " + str(output_filename))

    images_list = []

    # read the entire file into a python array
    if not os.path.exists(output_filename):
        if debug:
            print("Old json do not exists")
        return 0, images_list
    with open(output_filename, 'r', encoding="utf-8") as json_file:
        data = json.load(json_file)
        found_n_times = 0
        for line in data:
            if str(line['house_id']) == str(my_house_id):
                found_n_times = found_n_times + 1
                images_list = line['image_urls']
                break

    if found_n_times == 0:
        if debug:
            print("New house link not in json to be processed -> " + str(my_house_id))
        return 0, images_list
    elif found_n_times > 1:
        print('ERROR: check_link FOUND MORE THAN ONE TIME IN JSON -> ' +
              str(my_house_id) + ' - times found -> ' + str(found_n_times))
        return -1, images_list
    # si aparece una vez es correcto
    else:
        if debug:
            print("This house link already in json file -> " +
                  str(my_house_id) + ' - times found -> ' + str(found_n_times))
        if debug:
            print('Es una lista? -> ' + str(isinstance(images_list, list)))
            print(*images_list, sep=", ")
            print('number of images -> ' + str(len(images_list)))
            print(images_list)

        # retorno dos valores
        # found_n_times que será 0 si es un inmueble nuevo, 1 si ya estaba, y 2 o mayor si estaba mas veces porque ya hubo mas updates
        # images_list: lista con todas las imagenes ya descargadas en anteriores ocasiones
        return found_n_times, images_list
