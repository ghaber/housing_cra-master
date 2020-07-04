# -*- coding: utf-8 -*-
import scrapy
import re
import sys
import os
import pandas as pd
from datetime import datetime as dt
from housing_cra.items import Link
from pathlib import Path

sys.path.append(os.getcwd()+'/housing_cra')

# Global declarations
default_url = 'https://www.idealista.com'
saved = []
seen = []
zones = []
entering_parse_subzones = 0

class GetLinks(scrapy.Spider):

    name = 'getLinks'
    allowed_domains = ['idealista.com']

    def __init__(self, start, my_province):
        
        # cojo la lista de los links que vienen como argumento
        self.start_urls = [start]
        # guardo en la variable self el valor de province para poder usarlo globalmente
        self.province = my_province
        
    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse(self, response):

        print("*************Entering parse")
        # -*- When extracting denied links, if it is a subzone link, go to 'parse_subzones'
        # en mi caso solo tengo una start_url y cuando entro no la tengo parseada
        if self.start_urls[0] not in zones:
            yield response.follow(self.start_urls[0], callback=self.parse_subzones)

        else:
            # -*- Get province name -*-
            print("Get province name -> " + self.province)

            try:
                house_num = get_number(response.xpath(
                    "//a[@id='showAllLink']/text()").extract()[0])

                print("Get subzone -> " + str(house_num))

                # -*- Extract link directly if are less than 2000 houses -*-
                if house_num < 2000:

                    # Check if the link is registered already
                    this_link = default_url + \
                        response.xpath(
                            "//a[@id='showAllLink']/@href").extract()[0]
                    if this_link not in saved:
                        link = Link()
                        link['link'] = this_link
                        link['num_link'] = house_num
                        link['province'] = self.province
                        link['obtention_date'] = dt.now().date()
                        yield link
                        saved.extend(this_link)
                    else:
                        print("Link already captured")

                # -*- Get unseen from map -*-
                else:
                    print("*******************")
                    print("Get unseen from map")
                    print("*******************")
                    zone_paths = response.xpath(
                        "//map[@id='map-mapping']/area/@href").extract()
                    for i in range(len(zone_paths)):
                        zone_paths[i] = default_url + zone_paths[i]

                    # discard all the adjacent provinces links that are not part of the zone we are dealing with
                    for path in zones:
                        if path in zone_paths:
                            zone_paths.remove(path)

                    # discard all the zones that are previously saved
                    for path in saved:
                        if path in zone_paths:
                            zone_paths.remove(path)

                    # discard all the zones that are previously seen
                    for path in saved:
                        if path in zone_paths:
                            zone_paths.remove(path)
                    seen.extend(zone_paths)

                    for zone in zone_paths:
                        yield response.follow(zone, callback=self.parse_subzones)

            # -*- Already in the houses list -*-
            except Exception as e:

                # Check if the link is registered already
                this_link = (default_url + response.xpath("//div[@class='fixed-toolbar-controls']/a/@href")
                             .extract()[0])
                if this_link not in saved:
                    link = Link()
                    link['link'] = this_link
                    link['num_link'] = get_number(response.xpath(
                        "//div[@id='h1-container']/h1/text()").extract()[0])
                    link['province'] = self.province
                    link['obtention_date'] = dt.now().date()
                    yield link
                    saved.extend(this_link)
                else:
                    print("Link already captured")

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #

    def parse_subzones(self, response):
        print("*************Entering parse_subzones*************")

        global entering_parse_subzones

        entering_parse_subzones = entering_parse_subzones + 1

        # -*- Get province name -*-

        try:
            house_num = get_number(response.xpath(
                "//a[@id='showAllLink']/text()").extract()[0])

            print("Get subzone " + str(entering_parse_subzones) +
                  " -> " + str(house_num))

            # -*- Extract path directly if are less than 2000 houses -*-
            if house_num < 2000:

                # Check if the link is registered already
                this_link = default_url + \
                    response.xpath("//a[@id='showAllLink']/@href").extract()[0]
                if this_link not in saved:
                    link = Link()
                    link['link'] = this_link
                    link['num_link'] = house_num
                    link['province'] = self.province
                    link['obtention_date'] = dt.now().date()
                    yield link
                    saved.extend(this_link)
                else:
                    print("Link already captured")

            # -*- Get unseen from map -*-
            else:
                subzone_paths = response.xpath(
                    "//map[@id='map-mapping']/area/@href").extract()
                for i in range(len(subzone_paths)):
                    subzone_paths[i] = default_url + subzone_paths[i]

                # discard all the adjacent provinces links that are not part of the zone we are dealing with
                for path in zones:
                    if path in subzone_paths:
                        subzone_paths.remove(path)

                # discard all the zones that are previously saved
                for path in saved:
                    if path in subzone_paths:
                        subzone_paths.remove(path)

                # discard all the zones that are previously seen
                for path in saved:
                    if path in subzone_paths:
                        subzone_paths.remove(path)
                seen.extend(subzone_paths)

                for subzone in subzone_paths:
                    yield response.follow(subzone, callback=self.parse_subzones)

        # -*- Already in the houses list -*-
        # estamos aqui si no hay más links
        except Exception as e:

            # Check if the link is registered already
            # this_link = default_url + response.xpath("//div[@class='fixed-toolbar-controls']/a/@href").extract()[0]
            # victor
            this_link = default_url + \
                response.xpath(
                    "//div[@class='fixed-toolbar']/a/@href").extract()[0]
            print("this link -> " + str(this_link))
            if this_link not in seen:
                link = Link()
                link['link'] = this_link
                # <h1 class="listing-title" id="h1-container">
                # <span class = "h1-simulated" ></span >
                # 55 casas y pisos en Área de A Barcala, A Coruña
                # </h1 >
                link['num_link'] = get_number(response.xpath(
                    "//h1[@id='h1-container']/text()[2]").extract()[0])
                link['province'] = self.province
                link['obtention_date'] = dt.now().date()
                yield link
                seen.extend(this_link)
                print("link added to seen")
            else:
                print("link previously seen")
            print("************ Finished parse_subzones **************")

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #


def get_number(property):
    nums = re.findall(r'\d+', property)
    if len(nums) == 2:
        # '40.000' ->   '40' + '000'  -> '40000'  ->  40000
        return int(nums[0]+nums[1])
    else:
        return int(nums[0])
