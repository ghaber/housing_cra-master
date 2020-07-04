# -*- coding: utf-8 -*-
import scrapy
import sys
import os
from housing_cra.items import Zone

# getcwd returns current working directory of a process.
sys.path.append(os.getcwd()+'/housing_cra')

# Global declarations
default_url = 'https://www.idealista.com'
renting = 'https://www.idealista.com/alquiler-viviendas/#municipality-search'
selling_flag = True  # True: Selling ; False: Renting

# our first Spider
class GetZones(scrapy.Spider):
    # Identifies the Spider. It must be unique within a project.
    name = 'getZones'
    allowed_domains = ['idealista.com']
    start_urls = ['https://www.idealista.com']

    # ----------------------------------------------------------- #
    # ----------------------------------------------------------- #
    # Method that will be called to handle the response downloaded for each of the requests made.
    # The response parameter is an instance of TextResponse that holds the page content and has further helpful methods to handle it.
    # The parse() method usually parses the response, extracting the scraped data as dicts and also finding new URLs to follow and creating new requests(Request) from them.

    def parse(self, response):
        global selling_flag
        zone_paths = response.xpath("//div[@class='locations-list clearfix']/ul/li/a/@href").extract()

        for path in zone_paths:
            zone = Zone()
            zone['zone'] = (default_url + path)[:-10] + 'mapa'   # [:-10] -> removes 'municipios' from path
            if selling_flag:
                zone['type'] = 'selling'
            else:
                zone['type'] = 'renting'

            yield zone

        if selling_flag:
            selling_flag = False
            yield response.follow(renting, callback=self.parse)
