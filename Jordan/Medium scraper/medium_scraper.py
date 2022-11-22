from urllib.parse import urljoin

import scrapy
from scrapy.crawler import CrawlerProcess
import time
import csv
import json
import traceback
import concurrent
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
import requests as Requests

csv_columns = ["Post_url","Title","Post_Details","Author_Name",]
index = 0

csvfile = open("medium.csv", "w", newline="",encoding="utf-8-sig")
writer = csv.DictWriter(csvfile, fieldnames=csv_columns, dialect='excel')
writer.writeheader()
csvfile.flush()
default_Item = dict()
link = open("link_list.txt", "r")
urls = [v for v in link.read().split("\n") if v]
start_time = time.time()



name = "medium"


custom_settings = {
    'CONCURRENT_REQUESTS': 100,
    'DOWNLOAD_DELAY': 0,

}

def start_requests( index,url):



    id = url[url.rindex("-") + 1:]

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

    payload = [
        {
            "operationName":"PostViewerEdgeContentQuery","variables":{
            "postId":id
        },
            "query": "query PostViewerEdgeContentQuery(\n  $postId: ID!\n  \n) {\n  post(id: $postId) {\n    ... on Post {\n        creator{\n      name\n      }\n      id\n      title\n      viewerEdge {\n        \n        fullContent {\n          bodyModel {\n               paragraphs {\n                    text\n                    type\n                    }\n                }\n            }\n        } \n    }\n  }\n}\n\n\n  \n\n"
        }
    ]

    # response = Requests.post(url="https://medium.com/_/graphql" ,json=payload, headers=headers, proxies={ 'https' : 'socks5://auzykcgz-rotate:no7dr8c5j7mn@p.webshare.io:80' })
    # self.parse(response,id,url)
    response = Requests.post(url="https://medium.com/_/graphql", json=payload, headers=headers)

    return {"response":response,
            "id": id,
            "url": url,
            "index":index,
            "runtime":start_time

            }

def parse(response,id,url):
    item = dict()
    item["Post_url"] = url
    item["Title"] = ""
    item["Post_Details"]=""
    item["Author_Name"] = ""

    if response.status_code == 200:

        result = json.loads(response.text)
        item["Title"] = result[0]["data"]["post"]["title"]
        item["Author_Name"] = result[0]["data"]["post"]["creator"]["name"]

        details = ""

        paragraphs = result[0]["data"]["post"]["viewerEdge"]["fullContent"]["bodyModel"]["paragraphs"]
        for i, para in enumerate(paragraphs):
            _type = para['type']
            text = para["text"]
            wraper = "ul"

            #print(f"{text}")

            if text !="":
                if (para["type"] != "ULI" and para["type"] != "OLI"):
                    if _type == "MIXTAPE_EMBED":
                        text = ""
                    elif _type == "IMG":
                        text = f"<figcaption>{text}</figcaption>\n"
                    elif _type == "BQ" or _type == "PQ":
                        text = f"<blockquote>{text}</blockquote>\n"
                    else:
                        text = f"<{_type}>{text}</{_type}>\n"

                elif (_type == "ULI" or _type == "OLI"):
                    if _type =="ULI":
                        wraper = "ul"
                    if _type =="OLI":
                        wraper = "ol"

                    text = f"<li>{text}</li>\n"
                    if (paragraphs[i - 1]["type"] == "ULI" or paragraphs[i - 1]["type"] == "OLI") != True:
                        text = f"<{wraper}>\n {text}"

                    try:
                        if paragraphs[i + 1]["type"] != "ULI" and paragraphs[i + 1]["type"] != "OLI":
                            text = f"{text}</{wraper}>\n"
                    except Exception:
                        text = f"{text}</{wraper}>\n"

            details =f"{details}{text}"

        item["Post_Details"] = str(details)

    if len(item["Post_Details"]) > 32758:
        item["Post_Details"] = "out of range"

    writer.writerow(item)
    csvfile.flush()


with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_url = {executor.submit(start_requests, i,url)
    for i,url in enumerate(urls)}


    for future in concurrent.futures.as_completed(fs=future_to_url):
        try:

            data = future.result()

            runtime = int((time.time() - start_time) / 60)
            index += 1

            id = data["id"]
            url = data["url"]
            parse(data["response"],data["id"],data["url"])
            print(f"Runtime {runtime} minutes Scraping {index} article id {id} \n")
        except Exception as e:
            print('Looks like something went wrong:',e)
            traceback.print_exc()
            default_Item["Post_url"] = url
            writer.writerow(default_Item)
            csvfile.flush()
            with open("missing_urls.txt",mode="a") as f:
                f.writelines(url + "\n")
                f.close()
    csvfile.close()







