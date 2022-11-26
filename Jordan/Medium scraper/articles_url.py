from urllib.parse import urljoin

import scrapy
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
import csv
import json
import bs4 as bs
import requests as Req

csv_columns = []


csvfile = open("trendyol.csv", "w", newline="", encoding="utf-8-sig")
writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
writer.writeheader()
csvfile.flush()

link = open("archive_links.txt", "r")
urls = [v for v in link.read().split("\n") if v]


class medium(scrapy.Spider):
    name = "medium"
    headers = {
        "authority": "medium.com",
        "method": "POST",
        "path": "/_/graphql",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-GB,en;q=0.9",
        "apollographql-client-name": "lite",
        "apollographql-client-version": "main-20221117-175959-59145e878f",
        "content-length": "5940",
        "content-type": "application/json",
        "graphql-operation": "PostViewerEdgeContentQuery",
        "medium-frontend-app": "lite/main-20221117-175959-59145e878f",
        "medium-frontend-path": "/illumination/5-free-premium-services-and-tools-you-need-in-2022-435ed415ee63",
        "medium-frontend-route": "post",
        "origin": "https://medium.com",
        "ot-tracer-sampled": "true",
        "ot-tracer-spanid": "601a22d134db811b",
        "ot-tracer-traceid": "396cb4ae41299fd9",
        "referer": "https://medium.com/illumination/5-free-premium-services-and-tools-you-need-in-2022-435ed415ee63",
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': "empty",
        'sec-fetch-mode': "cors",
        "sec-fetch-site": "same-origin",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "sec-ch-ua": '''"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"''',

    }


    custom_settings = {
        'CONCURRENT_REQUESTS': 100,
        'DOWNLOAD_DELAY': 0,

    }

    def start_requests(self):
        for url in urls:
            yield scrapy.Request(url=url, headers=self.headers, dont_filter=True)


    def parse(self, response, **kwargs):


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})
process.crawl(medium)
process.start()