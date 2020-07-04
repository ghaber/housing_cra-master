# -*- coding: utf-8 -*-
# https://docs.scrapy.org/en/latest/topics/settings.html

# The name of the bot implemented by this Scrapy project (also known as the project name). This name will be used for the logging too.
BOT_NAME = 'housing_cra'
# A list of modules where Scrapy will look for spiders.
SPIDER_MODULES = ['housing_cra.spiders']
# Module where to create new spiders using the genspider command.
NEWSPIDER_MODULE = 'housing_cra.spiders'
# The user agent string to use for matching in the robots.txt file. If None, the User-Agent header you are sending with the request or
# the USER_AGENT setting (in that order) will be used for determining the user agent to use in the robots.txt file.
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0'

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

AUTOTHROTTLE_ENABLED = False  # CRAWLERA
DOWNLOAD_TIMEOUT = 600  # CRAWLERA

# -*- Concurent requests & Delay
# If enabled, Scrapy will respect robots.txt policies.
ROBOTSTXT_OBEY = False
# The maximum number of concurrent (i.e. simultaneous) requests that will be performed by the Scrapy downloader.
CONCURRENT_REQUESTS = 1  # 1
# The amount of time (in secs) that the downloader should wait before downloading consecutive pages from the same website.
# This can be used to throttle the crawling speed to avoid hitting servers too hard.
# recommended: use download delays (2 or higher).
#DOWNLOAD_DELAY = 2
# The maximum number of concurrent (i.e. simultaneous) requests that will be performed to any single domain.
CONCURRENT_REQUESTS_PER_DOMAIN = 1  # 1
# The maximum number of concurrent (i.e. simultaneous) requests that will be performed to any single IP.
# If non-zero, the CONCURRENT_REQUESTS_PER_DOMAIN setting is ignored, and this one is used instead.
# In other words, concurrency limits will be applied per IP, not per domain.
# This setting also affects DOWNLOAD_DELAY and AutoThrottle extension: if CONCURRENT_REQUESTS_PER_IP is non-zero,
# download delay is enforced per IP, not per domain.
CONCURRENT_REQUESTS_PER_IP = 1

# Victor: Whether to enable the cookies middleware. If disabled, no cookies will be sent to web servers.
COOKIES_ENABLED = False
COOKIES_DEBUG = True

# -*-  -*- -*- -*- -*- -*- -*-

# A dict containing the downloader middlewares enabled in your project, and their orders
# https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#topics-downloader-middleware-setting

DOWNLOADER_MIDDLEWARES = {
    # creo los headers del valor de DEFAULT_REQUEST_HEADERS
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 550,
    # habilito este middleware para sacar por log los headers de cada request
    'housing_cra.middlewares.SpaHousingCrawlerDownloaderMiddleware':560,
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    # A middleware to retry failed requests that are potentially caused by temporary problems such as a connection timeout or HTTP 500 error.
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    # 'housing_cra.middlewares.SleepRetryMiddleware': 100,

    #  ---------> USER-AGENTS
    # Se ha añadido un middleware llamado Random-Useragent que hace que Scrapy utilice un User-Agent
    # distinto por cada petición que emite. Now all the requests from your crawler will have a random user-agent picked from the text file USER_AGENT_LIST
    # 'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
    # 'random_useragent.RandomUserAgentMiddleware': 400,

    # 'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,

    #  ---------> PROXIES
    # 'scrapy_proxies.RandomProxy': 100,
    # 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    # Además, se ha añadido otro middleware llamado Rotating Proxies, para hacer que las peticiones
    # se realicen desde distinta dirección IP cada vez
    # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,

    # ------  Victor: añadimos CRAWLERA
    'scrapy_crawlera.CrawleraMiddleware': 610,

    # añadimos un middleware para inspeccionar la request que enviamos y sus headers
}

# ------  Scrapy random user-agent
USER_AGENT_LIST = "./housing_cra/useragents.txt"

# ------  Scrapy fake user-agent
RANDOM_UA_PER_PROXY = True

# ------  Retry many times since proxies often fail. Setting from middleware RetryMiddleware
# Maximum number of times to retry, in addition to the first download.
RETRY_TIMES = 0

# Which HTTP response codes to retry.
RETRY_HTTP_CODES = [500, 503, 504, 400, 403, 404, 408]

# ------  Scrapy rotating proxies
# https://free-proxy-list.net/
ROTATING_PROXY_LIST_PATH = "./housing_cra/proxies.txt"

# ------  Scrapy proxies
PROXY_LIST = "./housing_cra/proxies.txt"
PROXY_MODE = 0

# ------  añadimos la descarga de imagenes
#ITEM_PIPELINES = {'scrapy.pipelines.images.ImagesPipeline': 1}
# Storage in local disk in folder images
IMAGES_STORE = 'images'  # relativo al path donde estamos
# Para que no descargue las mismas fotos dos veces
# The Image Pipeline avoids downloading files that were downloaded recently.
IMAGES_EXPIRES = 36500  # 100 years; never expires by default.
# Storage in Amson S3 bucket
# IMAGES_STORE = 's3://bucket/images'
# AWS_ACCESS_KEY_ID = 'your-access-key'
# AWS_SECRET_ACCESS_KEY = 'your-secret-access-key'
# By default, the ACL is set to private.
# IMAGES_STORE_S3_ACL = 'public-read'
# Use this option if you want to disable SSL connection for communication with S3 or S3-like storage. By default SSL will be used.
# AWS_USE_SSL = False  # or True (None by default)
# Verify SSL connection between Scrapy and S3 or S3-like storage. By default SSL verification will occur.
# AWS_VERIFY = False  # or True (None by default)

# ------  Victor: añadimos CRAWLERA
CRAWLERA_ENABLED = False
CRAWLERA_APIKEY = ''
CRAWLERA_PRESERVE_DELAY = True

# If you want to process broken responses set the setting DOWNLOAD_FAIL_ON_DATALOSS = False
DOWNLOAD_FAIL_ON_DATALOSS = False

# Log Settings
# LOG_FILE = "./log/log.txt"
# LOG_ENABLED = True
# LOG_LEVEL = 'DEBUG'
# LOG_STDOUT = False  # Route stdout to log

# The amount of time (in secs) that the downloader should wait before downloading consecutive pages from the same website.
DOWNLOAD_DELAY = 10
# This setting is also affected by the RANDOMIZE_DOWNLOAD_DELAY setting(which is enabled by default). By default, Scrapy doesn’t wait a fixed amount of time between requests,
# but uses a random interval between 0.5 * DOWNLOAD_DELAY and 1.5 * DOWNLOAD_DELAY.
