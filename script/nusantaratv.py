import requests
import pymongo
import time, random
import sys
from datetime import date
from datetime import datetime
from dateutil import parser
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from bson.objectid import ObjectId
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from model.db import DBMongo
from modules.helper import ChangeMonth
import pytz
import os
from dotenv import load_dotenv

load_dotenv()
array_error = []


class Nusantaratv:

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
        self.id = ""
        self.log_error = []

    def __enter__(self):
        print("--------------------------------------------------------")
        print("           Online News Scraper: Nusantaratv")
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
        logs["scraper_name"] = "Nusantaratv"
        logs["start"] = datetime.now()
        logs["end"] = None
        logs["duration"] = None
        logs["count"] = None
        logs["status"] = "Running"
        # logs['log'] = self.filename

        log = self.logs.insert_one(logs)
        logs["id"] = log.inserted_id

        return logs

    def check_redirect(self, url):
        response = requests.get(url)
        if response.is_redirect:
            crawler.logs.update_one(
                {"_id": ObjectId(logs["id"])},
                {
                    "$set": {
                        "end": datetime.now(),
                        "count": self.counter,
                        "duration": (datetime.now() - logs["start"]).total_seconds(),
                        "status": "Redirected",
                        "error_message": "Scraper is redirected",
                    }
                },
            )
            print("Scraper is redirected")
            exit()

    def request(self, url):
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        # }
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        page = session.get(url)
        return page

    def get_title(self, page):
        if page.find("h1", class_="my-1"):
            title = page.find("h1", class_="my-1").text
        else:
            title = page.find("h2", class_="title").text.strip()
        return title

    def get_journalist(self, page):
        if page.find("h2", class_="post-title ke-29"):
            journalist = page.find("h2", class_="post-title ke-29").text
            journalist = journalist.partition("-")[0].strip()
        elif page.find("li", class_="d-flex align-items-center"):
            journalist = page.find(
                "li", class_="d-flex align-items-center"
            ).a.text.strip()
        else:
            journalist = ""
        return journalist

    def get_publish_date(self, page):
        if page.find("h2", class_="ke-29"):
            date = page.find("h2", class_="ke-29").text
            date = date.partition("-")[2].strip()
            date = date.replace("Wib", "")
            date = ChangeMonth(date)
            date = parser.parse(date)
        else:
            date = page.find("div", class_="meta-top").time.text.strip()
            date = date.replace("Wib", "")
            date = ChangeMonth(date)
            date = parser.parse(date)

        # if 'Agustus' in date or 'Juli' in date or 'September' in date or 'Oktober' in date or 'November' in date or 'Desember' in date:
        # date = ChangeMonth(date)
        # date = parser.parse(date)
        # else:
        #     date = parser.parse(date)

        return date

    def get_thumbnail(self, page):
        if page.find("meta", attrs={"property": "og:image"}):
            image = page.find("meta", attrs={"property": "og:image"})["content"]
        elif page.find("figure", attrs={"class": "figure"}):
            image = page.find("figure", attrs={"class": "figure"}).img["src"]
        else:
            image = "-"
        return image

    def get_content(self, page):
        if page.find("div", class_="detail_konten_sort"):
            content = page.find("div", class_="detail_konten_sort")
        elif page.find("div", class_="post-body mb-3"):
            content = page.find("div", class_="post-body mb-3")
        elif page.find("div", class_="content"):
            content = page.find("div", class_="content")
        article_content = ""
        for p in content.find_all(["p", "div"], class_=None):
            if "baca juga" in p.text.lower():
                continue
            # if article_content.find(p.text)!=-1:
            #     article1 = article_content.partition(p.text)[0] + "\n\n"
            #     article1 += p.text + "\n\n"
            #     article_content = article1 + article_content.partition(p.text)[2]
            # else:
            article_content += p.text + "\n\n"
        article_content = article_content.strip()
        return article_content

    def parse_page(
        self, session=None, csrf_token=None, nusantaratv_session=None, token=None
    ):
        # Set the XSRF-TOKEN cookie in the session
        session.cookies.set(
            "XSRF-TOKEN=" + csrf_token, "nusantaratv_session=" + nusantaratv_session
        )
        data = {"id": self.id, "_token": token}
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            # Other headers if needed
        }
        try:
            response = session.post(
                "https://nusantaratv.com/loadmore/load_data", headers=headers, data=data
            )
        except requests.exceptions.ConnectionError:
            crawler.logs.update_one(
                {"_id": ObjectId(logs["id"])},
                {
                    "$set": {
                        "end": datetime.now(),
                        "count": self.counter,
                        "duration": (datetime.now() - logs["start"]).total_seconds(),
                        "status": "Unavailable",
                        "error_message": "Site can’t be reached",
                    }
                },
            )
            print("Error : Gagal mengambil berita karena website down")
            exit()
        soup = BeautifulSoup(response.text, "html.parser")
        if soup.find("div", class_="post-content ke-154 mb-2"):
            berita = soup.findAll("div", class_="post-content ke-154 mb-2")
        else:
            crawler.logs.update_one(
                {"_id": ObjectId(logs["id"])},
                {
                    "$set": {
                        "end": datetime.now(),
                        "count": 0,
                        "duration": (datetime.now() - logs["start"]).total_seconds(),
                        "status": "MissingClass",
                        "error_message": "Element not found",
                    }
                },
            )
            print("Error : Gagal menemukan element")
            exit()
        print("Total articles: {}".format(len(berita)))
        if len(berita) > 0:
            for article in berita:
                try:
                    url = article.find("h5", class_="post-title ke-156 mt-2 mr-2").a[
                        "href"
                    ]
                    url_in_db = self.streams.find_one({"origin_url": url})
                    if url_in_db is not None:
                        # print('origin url '+url+' already exists in collection, skip')
                        continue
                    print(url)
                    try:
                        article_detail = requests.get(
                            url,
                            headers={
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                            },
                        )
                    except requests.exceptions.ConnectionError:
                        print(
                            "Error : Gagal mengambil berita karena halaman berita down"
                        )
                        continue
                    if article_detail.status_code != 200:
                        print("Error : " + str(article_detail.status_code))
                        print("URL : " + url)
                        continue
                    page = BeautifulSoup(article_detail.text, "html.parser")
                    # get publish date
                    date = self.get_publish_date(page)
                    # get title
                    title = self.get_title(page)
                    # get journalist
                    journalist = self.get_journalist(page)
                    # get thumbnail
                    thumbnail = self.get_thumbnail(page)
                    # get content
                    content = self.get_content(page)

                    account = urlparse(url).netloc.replace("www.", "")

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
                    meta["portal"] = "Nusantaratv"
                    meta["timestamp"] = datetime.now()
                    meta["thumbnail"] = thumbnail

                    # print(meta)
                    self.insert(meta)

                    # increment counter
                    self.counter += 1
                except Exception as e:
                    # self.logger.error({'url': url, 'message': str(e)})
                    print("ERROR ", url)
                    print(str(e))
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    exc_tb = exc_tb.tb_lineno
                    ## Error di jadikan array
                    error = {
                        "url": url,
                        "error": str(e),
                        "type": str(exc_type),
                        "line": str(exc_tb),
                    }
                    ## error di tampung
                    array_error.append(error)
                    continue
            ## hasil error yang di tampung masukan ke method
            if len(array_error) > 0:
                self.log_error.append(array_error)
            self.page += 1
            item = soup.find("button", attrs={"data-id": True})
            if item:
                self.id += item["data-id"]
            if self.page > random.randint(2, 5):
                return self.counter
            self.parse_page(session, csrf_token, nusantaratv_session, token)
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

    with Nusantaratv() as crawler:
        logs = crawler.insert_log()
        ## Update File name Scraper
        file_name = os.path.basename(__file__)
        crawler.scraper.update_one(
            {"_id": logs["scraper_name"]}, {"$set": {"file_name": file_name}}
        )
        ## End
        try:
            url = "https://nusantaratv.com/"
            session = requests.Session()
            # Make a GET request to the website
            response = session.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                },
            )
            # Get the value of the XSRF-TOKEN cookie
            csrf_token = response.cookies.get("XSRF-TOKEN")
            nusantaratv_session = response.cookies.get("nusantaratv_session")
            page = BeautifulSoup(response.text, "html.parser")
            if page.find("input", attrs={"name": "_token"}):
                token = page.find("input", attrs={"name": "_token"})["value"]
            else:
                print("Gagal ambil token")
                crawler.logs.update_one(
                    {"_id": ObjectId(logs["id"])},
                    {
                        "$set": {
                            "end": datetime.now(),
                            "count": "0",
                            "duration": (
                                datetime.now() - logs["start"]
                            ).total_seconds(),
                            "status": "Completed",
                        }
                    },
                )
                exit()
            total_data = crawler.parse_page(
                session, csrf_token, nusantaratv_session, token
            )

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
