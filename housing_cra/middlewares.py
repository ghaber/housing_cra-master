# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from time import sleep
from scrapy import signals
import sys
import os
import re

sys.path.append(os.getcwd()+'/housing_cra')


class SpaHousingCrawlerSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for i, request in enumerate(start_requests):
            #spider.logger.info('My request headers: %s', request.headers)
            yield request


    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s',spider.name)


class SpaHousingCrawlerDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        spider.logger.info('URL of this request: %s', request.url)
        spider.logger.info('Callback of this request: %s', str(request.callback))
        spider.logger.info('Method of this request: %s', request.method)
        for k, v in request.meta.items():
            spider.logger.info('My Meta %s: %s', k, v)
        spider.logger.info('Body of this request: %s', request.body)
        for k, v in request.headers.items():
            spider.logger.info('My header %s: %s', str(k, 'utf-8'), str(v[0], 'utf-8'))
        spider.logger.info('Encoding of this request: %s', request.encoding)
        spider.logger.info('Priority of this request: %s', str(request.priority))
        spider.logger.info('dont_filter of this request: %s', str(request.dont_filter))

        #spider.logger.info('My request headers: %s', request.headers)
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        spider.logger.info('Response: %s', response.text)
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened : %s',spider.name)


class SleepRetryMiddleware(RetryMiddleware):
    def __init__(self, settings):
        RetryMiddleware.__init__(self, settings)

    def process_response(self, request, response, spider):
        if response.status in [403]:
            link = str(request)[5:-1]+'\n'

            # -*- Register log of denied houses -*-
            check_house = re.search('inmueble', link)
            if check_house:
                with open('logHouse.txt', 'a') as log:
                    log.write(link)

            # -*- Register log of denied links -*-
            else:
                with open('logLink.txt', 'a') as log:
                    log.write(link)

            # -*- Wait for a while before restarting crawling -*-
            reason = response_status_message(response.status)

            time_wait = 45
            print("********   REQUEST BLOCKED!  :(   Waiting " +
                  str(time_wait) + " seconds before reload")
            sleep(time_wait)

            return self._retry(request, reason, spider) or response

        return super(SleepRetryMiddleware, self).process_response(request, response, spider)
