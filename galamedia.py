import requests
import time
import sys
import cloudscraper
from modules.proxy import Proxy, proxy_get
from random import randint
from datetime import datetime
from dateutil import parser
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from bson.objectid import ObjectId
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from model.db import DBMongo
import pytz
from modules.helper import ChangeMonth
import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Encoding": "identity",
}

today = datetime.today()
d = today.strftime("%d")
m = today.strftime("%m")
y = today.year


class Galamedia:

    def __init__(self):
        self.StartTime = time.time()
        self.IST = pytz.timezone("Asia/Jakarta")
        self.datetime_ist = datetime.now(self.IST)
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
        self.logs_proxy = None
        self.proxy = None

    def __enter__(self):
        print("--------------------------------------------------------")
        print("           Online News Scraper: Galamedia")
        print("--------------------------------------------------------")
        print("Started Time:", self.datetime_ist)
        self.db = self.ConnectionDB.GetDatabase(os.getenv("DB_NAME"))
        self.streams = self.db["streams"]
        self.logs = self.db["logs"]
        self.scraper = self.db["scraper"]
        self.proxy = self.db["proxy"]
        self.logs_proxy = self.db["logs_proxy"]
        return self

    def insert(self, data):
        self.streams.insert_one(data)

    def insert_log(self):
        logs = {
            "scraper_name": "Galamedia",
            "start": datetime.now(),
            "end": None,
            "duration": None,
            "count": None,
            "status": "Running",
        }
        log = self.logs.insert_one(logs)
        logs["id"] = log.inserted_id
        return logs

    def get_title(self, page):
        meta_title = page.find("meta", attrs={"property": "og:title"})
        if meta_title:
            return meta_title["content"]
        title_tag = page.find("h1", class_="read__title")
        return title_tag.text.strip() if title_tag else "No Title"

    def get_journalist(self, page):
        journalist_tag = page.find("div", class_="read__info__author")
        return journalist_tag.text.strip() if journalist_tag else "No Journalist"

    def get_publish_date(self, page):
        date_tag = page.find("div", class_="read__info__date")
        if date_tag:
            date_str = (
                date_tag.text.partition(",")[2]
                .partition("W")[0]
                .replace("|", "")
                .strip()
            )
            date_str = ChangeMonth(date_str)
            return parser.parse(date_str)
        return datetime.now()

    def get_thumbnail(self, page):
        meta_image = page.find("meta", attrs={"property": "og:image"})
        if meta_image:
            return meta_image["content"]
        image_tag = page.find("img", class_="photo__img")
        return (
            image_tag["src"]
            if image_tag and image_tag.has_attr("src")
            else "No Thumbnail"
        )

    def get_content(self, page):
        content_div = page.find("article", class_="read__content clearfix")
        if not content_div:
            return ""

        paragraphs = content_div.find_all("p")
        content = ""
        for p in paragraphs:
            text = p.text.strip()
            if "Baca Juga:" in text or "Baca juga:" in text or "BACA JUGA" in text:
                a_tag = p.find("a")
                if a_tag:
                    temp = a_tag.text
                else:
                    temp = ""
                content += (
                    text.replace("Baca Juga:", "")
                    .replace("Baca juga:", "")
                    .replace("BACA JUGA", "")
                    .replace(temp, "")
                )
            else:
                content += text + "\n\n"
        return content.strip()

    def check_redirect(self, url):
        response = requests.get(url, headers=headers)
        if response.is_redirect:
            self.logs.update_one(
                {"_id": ObjectId(logs["id"])},
                {
                    "$set": {
                        "end": datetime.now(),
                        "count": 0,
                        "duration": (datetime.now() - logs["start"]).total_seconds(),
                        "status": "Redirected",
                        "error_message": "Scraper is redirected",
                    }
                },
            )
            print("Scraper is redirected")
            exit()

    def request(self, url, params=None, **kwargs):
        scraper = cloudscraper.create_scraper(delay=10, browser="chrome")
        allow_redirects = kwargs.get("allow_redirects", True)
        max_retries = 3
        retries = 0
        page = None
        while retries < max_retries:
            try:
                ## Pakai Proxy
                get_proxy = proxy_get()
                if get_proxy is not None:
                    print(f"Proxy  : {get_proxy.partition('@')[2]}")
                    proxies = {
                        "https": "socks5://" + get_proxy,
                        "http": "socks5://" + get_proxy,
                    }
                    page = requests.get(
                        url,
                        proxies=proxies,
                        params=params,
                        headers=headers,
                        allow_redirects=allow_redirects,
                    )
                    if page.status_code != 200:
                        print("Gagal Pakai Proxy", str(page.status_code))
                        print("Retrying...")
                        retries += 1
                        logs_ = {
                            "url": url,
                            "proxy": get_proxy.partition("@")[2].partition(":")[0],
                            "port": get_proxy.partition("@")[2].partition(":")[2],
                            "message": "Gagal pakai Proxy Status Code:"
                            + str(page.status_code),
                            "status": "Failed",
                        }
                        self.logs_proxy.insert_one(logs_)
                        continue
                    logs_ = {
                        "url": url,
                        "proxy": get_proxy.partition("@")[2].partition(":")[0],
                        "port": get_proxy.partition("@")[2].partition(":")[2],
                        "status": "Success",
                    }
                    self.logs_proxy.insert_one(logs_)
                    break
                ## Tidak pakai Proxy
                else:
                    print("Proxy Tidak Ada")
                    page = scraper.get(
                        url,
                        params=params,
                        headers=headers,
                        allow_redirects=allow_redirects,
                    )
            except (
                requests.exceptions.ConnectionError,
                requests.exceptions.TooManyRedirects,
                BaseException,
            ) as e:
                logs_ = {
                    "url": url,
                    "proxy": get_proxy.partition("@")[2].partition(":")[0],
                    "port": get_proxy.partition("@")[2].partition(":")[2],
                    "message": "Gagal pakai Proxy: " + str(e),
                    "status": "Failed",
                }
                self.logs_proxy.insert_one(logs_)
                print(e)
                retries += 1
                print("Retrying...")
                continue
        return page

    def parse_page(self, url):
        print(url)
        try:
            scraper = cloudscraper.create_scraper(delay=10, browser="chrome")
            page = scraper.get(url, headers=headers)
        except requests.exceptions.ConnectionError:
            self.logs.update_one(
                {"_id": ObjectId(logs["id"])},
                {
                    "$set": {
                        "end": datetime.now(),
                        "count": 0,
                        "duration": (datetime.now() - logs["start"]).total_seconds(),
                        "status": "Unavailable",
                        "error_message": "Site can't be reached",
                    }
                },
            )
            print("Error: Failed to fetch news because website is down")
            exit()
        soup = BeautifulSoup(page.text, "html.parser")

        latest_wrap = soup.find("div", class_="latest__wrap mail")
        if not latest_wrap:
            self.logs.update_one(
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
            print("Error: Failed to find element")
            exit()

        articles = latest_wrap.find_all("div", class_="latest__item")
        print(f"Total articles: {len(articles)}")
        if articles:
            for article in articles:
                try:
                    article_url = article.find("h2", class_="latest__title").a["href"]
                    print(article_url)
                    if self.streams.find_one({"origin_url": article_url}):
                        continue

                    scraper = cloudscraper.create_scraper(delay=10, browser="chrome")
                    article_detail = scraper.get(article_url, headers=headers)

                    if not article_detail or article_detail.status_code != 200:
                        print(
                            f"Error: {article_detail.status_code if article_detail else 'No response'}"
                        )
                        print(f"URL: {article_url}")
                        continue

                    page = BeautifulSoup(article_detail.text, "html.parser")

                    date = self.get_publish_date(page)
                    title = self.get_title(page)
                    journalist = self.get_journalist(page)
                    thumbnail = self.get_thumbnail(page)

                    paging_wrap = page.find("div", class_="paging__wrap clearfix")
                    if paging_wrap:
                        total_pages = paging_wrap.find_all("div", class_="paging__item")
                        content = self.get_content(page)
                        for i in range(1, len(total_pages)):
                            url_page = f"{article_url}?page={i}"
                            article_detail_page = self.request(url_page)
                            if article_detail_page:
                                page_content = BeautifulSoup(
                                    article_detail_page.text, "html.parser"
                                )
                                content += "\n\n" + self.get_content(page_content)
                        content = content.strip()
                    else:
                        content = self.get_content(page)

                    if not content:
                        print(f"No content found for URL: {article_url}")
                        continue

                    account = urlparse(article_url).netloc.replace("www.", "")

                    meta = {
                        "id_account": account,
                        "date": date,
                        "title": title,
                        "content": content,
                        "account": account,
                        "journalist": journalist,
                        "url": article_url,
                        "origin_url": article_url,
                        "source": "news",
                        "portal": "Galamedia",
                        "timestamp": datetime.now(),
                        "thumbnail": thumbnail,
                    }

                    self.insert(meta)
                    self.counter += 1
                except Exception as e:
                    print(f"Error processing article: {article_url}")
                    exc_type, _, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    continue
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
    with Galamedia() as crawler:
        logs = crawler.insert_log()
        ## Update File name Scraper
        file_name = os.path.basename(__file__)
        crawler.scraper.update_one(
            {"_id": logs["scraper_name"]}, {"$set": {"file_name": file_name}}
        )
        ## End
        try:
            base_url = "https://galamedia.pikiran-rakyat.com/indeks-berita"
            total_data = crawler.parse_page(base_url)
            crawler.logs.update_one(
                {"_id": ObjectId(logs["id"])},
                {
                    "$set": {
                        "end": datetime.now(),
                        "count": total_data,
                        "duration": (datetime.now() - logs["start"]).total_seconds(),
                        "status": "Completed",
                    }
                },
            )
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            crawler.logs.update_one(
                {"_id": ObjectId(logs["id"])},
                {
                    "$set": {
                        "end": datetime.now(),
                        "count": 0,
                        "duration": (datetime.now() - logs["start"]).total_seconds(),
                        "status": "Error",
                        "error_message": f"{str(e)} Line : {str(exc_tb.tb_lineno)} {str(exc_type)}",
                    }
                },
            )
