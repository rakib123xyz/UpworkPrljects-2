import scrapy


class Sinsbary1Spider(scrapy.Spider):
    name = 'Sinsbary1'
    allowed_domains = ['www.sainsburys.co.uk']
    start_urls = ['http://www.sainsburys.co.uk/']

    def parse(self, response):
        pass

