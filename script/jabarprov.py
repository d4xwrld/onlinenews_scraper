import requests
import time
import sys
import cloudscraper
from random import randint
from time import sleep
from datetime import date
from datetime import datetime, timedelta
from dateutil import parser
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from bson.objectid import ObjectId
from model.db import DBMongo
import pytz
import os
import json
import re
from modules.helper import ChangeMonth
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv

load_dotenv()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
}

today = datetime.today()
d = datetime.today().day
m = today.strftime("%m")
y = datetime.today().year
array_error = []


class JabarProv:

    def __init__(self):
        self.StartTime = time.time()
        self.IST = pytz.timezone("Asia/Jakarta")
        self.datetime_ist = datetime.now(self.IST)

        # log_format = "%(levelname)s %(asctime)s - %(message)s"
        # logging.basicConfig(filename=self.filename, filemode='w', format=log_format, level=logging.ERROR)
        # self.logger = logging.getLogger()

        self.ConnectionDB = DBMongo(
            HOST=os.getenv("DB_HOST"),
            USERNAME=os.getenv("DB_USER"),
            PASSWORD=os.getenv("DB_PASS"),
            AUTH_SOURCE=os.getenv("DB_NAME"),
        )
        self.db = None
        self.streams = None
        self.logs = None
        self.counter = 0
        self.page = 1
        self.log_error = []
        self.kategori = ""

    def __enter__(self):
        print("--------------------------------------------------------")
        print("           Online News Scraper: JabarProv")
        print("--------------------------------------------------------")
        print("Started Time:", self.datetime_ist)
        self.db = self.ConnectionDB.GetDatabase(os.getenv("DB_NAME"))
        self.streams = self.db["streams"]
        self.logs = self.db["logs"]
        self.scraper = self.db["scraper"]
        return self

    def insert(self, dict):
        stream = self.streams.insert_one(dict)
        # if stream.inserted_id:
        #     print("Data inserted sucessfully")
        # else:
        #     print("Data Not Inserted")

    def insert_log(self):
        logs = {}
        logs["scraper_name"] = "JabarProv"
        logs["start"] = datetime.now()
        logs["end"] = None
        logs["duration"] = None
        logs["count"] = None
        logs["status"] = "Running"
        # logs['log'] = self.filename

        log = self.logs.insert_one(logs)
        logs["id"] = log.inserted_id

        return logs

    def get_content(self, page):
        content = page.find("div", class_="article__body")
        article_content = ""
        for p in content.find_all(["p", "div"], class_=None):
            if "baca juga :" in p.text.lower():
                continue
            if "baca juga:" in p.text.lower():
                continue
            article_content += p.text + "\n\n"
        article_content = article_content.strip()
        return article_content

    def parse_page(self, url, params=None, headers=None):
        print(url)
        try:
            scraper = cloudscraper.create_scraper(delay=10, browser="chrome")
            page = scraper.get(url, params=params, headers=headers)
        except requests.exceptions.ConnectionError:
            crawler.logs.update_one(
                {"_id": ObjectId(logs["id"])},
                {
                    "$set": {
                        "end": datetime.now(),
                        "count": 0,
                        "duration": (datetime.now() - logs["start"]).total_seconds(),
                        "status": "Unavailable",
                        "error_message": "Site can’t be reached",
                    }
                },
            )
            print("Error : Gagal mengambil berita karena website down")
            exit()
        # check if scraper redirected
        # self.check_redirect(url)
        soup = json.loads(page.text, strict=False)
        berita = soup["data"]
        print("Total articles: {}".format(len(berita)))
        if len(berita) > 0:
            for article in berita:
                try:
                    # get article detail link
                    url = article["slug"]
                    if "jabarprov.go.id" not in url:
                        url = "https://jabarprov.go.id/berita/" + url
                    # check origin url in collection, if exists, skip
                    url_in_db = self.streams.find_one({"origin_url": url})
                    if url_in_db is not None:
                        # print('origin url '+url+' already exists in collection, skip')
                        continue
                    sleep(randint(5, 9))
                    print("url", url)
                    # handler halaman berita down
                    try:
                        # article_detail = self.request(url)
                        scraper = cloudscraper.create_scraper(
                            delay=10, browser="chrome"
                        )
                        article_detail = scraper.get(
                            url, params=params, headers=headers
                        )
                    except requests.exceptions.ConnectionError:
                        print(
                            "Error : Gagal mengambil berita karena halaman berita down"
                        )
                        continue
                    page = BeautifulSoup(article_detail.text, "html.parser")

                    # get publish date
                    date = article["published_at"]
                    date = parser.parse(date)
                    # get title
                    title = article["title"]
                    # get journalist
                    journalist = article["author"]
                    # get thumbnail
                    thumbnail = article["image"]
                    # get content
                    content = self.get_content(page)

                    account = urlparse(url).netloc

                    # build meta dict for insert to db
                    meta = {}
                    meta["id_account"] = account
                    meta["date"] = date
                    meta["title"] = title
                    meta["content"] = (
                        content  # str(content.encode('utf-8').decode('unicode_escape'))
                    )
                    meta["account"] = account
                    meta["journalist"] = journalist
                    meta["url"] = url
                    meta["origin_url"] = url
                    meta["source"] = "news"
                    meta["portal"] = "JabarProv"
                    meta["timestamp"] = datetime.now()
                    meta["thumbnail"] = thumbnail

                    # print(meta)
                    self.insert(meta)

                    # increment counter
                    self.counter += 1
                except Exception as e:
                    print(url)
                    print(str(e))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    error = {
                        "url": url,
                        "error": str(e),
                        "type": str(exc_type),
                        "line": str(exc_tb.tb_lineno),
                    }
                    ## error di tampung
                    array_error.append(error)
                    continue
            ## hasil error yang di tampung masukan ke method
            if len(array_error) > 0:
                self.log_error.append(array_error)
            self.page += 1
            if self.page > 3:
                return self.counter
            next = (
                "https://api.jabarprov.go.id/v1/public/news?page="
                + str(self.page)
                + "&sort_by=published_at&sort_order=DESC&per_page=10&cat="
                + crawler.kategori
            )
            self.parse_page(next)
        return self.counter

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print("Close Database Connection...")
        print("Ended at: {}".format(datetime.now(self.IST)))
        self.ConnectionDB.DisconnectDatabase()
        print(
            "----------- Crawler Run %f seconds -----------"
            % (time.time() - self.StartTime)
        )


if __name__ == "__main__":

    with JabarProv() as crawler:
        logs = crawler.insert_log()
        ## Update File name Scraper
        file_name = os.path.basename(__file__)
        crawler.scraper.update_one(
            {"_id": logs["scraper_name"]}, {"$set": {"file_name": file_name}}
        )
        ## End
        kategori = [
            "ekonomi",
            "kesehatan",
            "pendidikan",
            "pemerintahan",
            "infrastruktur",
            "sosial",
            "teknologi",
        ]
        try:
            for i in kategori:
                crawler.kategori = i
                crawler.page = 1
                base_url = (
                    "https://api.jabarprov.go.id/v1/public/news?page=1&sort_by=published_at&sort_order=DESC&per_page=10&cat="
                    + crawler.kategori
                )
                total_data = crawler.parse_page(base_url)
                print("Sucessfully processing {} article(s)".format(crawler.counter))

            ## cek method log error ada tidak
            if len(crawler.log_error) > 0:
                crawler.logs.update_one(
                    {"_id": ObjectId(logs["id"])},
                    {
                        "$set": {
                            "end": datetime.now(),
                            "count": total_data,
                            "duration": (
                                datetime.now() - logs["start"]
                            ).total_seconds(),
                            "status": "Error",
                            "error_message": crawler.log_error[0],
                        }
                    },
                )
            else:
                crawler.logs.update_one(
                    {"_id": ObjectId(logs["id"])},
                    {
                        "$set": {
                            "end": datetime.now(),
                            "count": total_data,
                            "duration": (
                                datetime.now() - logs["start"]
                            ).total_seconds(),
                            "status": "Completed",
                        }
                    },
                )
        except Exception as e:
            print(str(e))
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            crawler.logs.update_one(
                {"_id": ObjectId(logs["id"])},
                {
                    "$set": {
                        "end": datetime.now(),
                        "count": 0,
                        "duration": (datetime.now() - logs["start"]).total_seconds(),
                        "status": "Error",
                        "error_message": str(e)
                        + "\n\n"
                        + str(exc_type)
                        + " "
                        + str(fname)
                        + " Line : "
                        + str(exc_tb.tb_lineno),
                    }
                },
            )
