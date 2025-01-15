import sys
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept-Encoding": "identity",
}
token = os.getenv("TOKEN")
print(token)


class NusantaraTV:

    def __init__(self):
        self.StartTime = time.time()
        self.IST = pytz.timezone("Asia/Jakarta")
        self.datetime_ist = datetime.now(self.IST)
        self.counter = 0
        self.session = requests.Session()
        self.base_url = "https://nusantaratv.com"
        self.headers = headers.copy()
        self.headers.update(
            {
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://nusantaratv.com",
                "Referer": "https://nusantaratv.com/",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
            }
        )
        self.session.cookies.set(
            "XSRF-TOKEN",
            "eyJpdiI6ImZGSjRTSEYyQ3h0WEg3NzRpeGRHbWc9PSIsInZhbHVlIjoiYmUyS09TTmNaU0xIUFVPS0pNRjRaWHV0OUFTQlNzTmJCWjZBQVBhTllHRERwNG1ZL25PRlVSVDVSSG1zTTRpM3dYU1lTYjlFM2pRUWE2c0ZJTDNPeXVWZHhQZmxONkExK1I2Z0h0Zk5TRzIzNzlNV1hUaENkL3NidzNENDg2dzIiLCJtYWMiOiI1MWQ3MjY0MDU5YTZhZWI5Y2Y1MmQwZjA2ZWQ4YzQ2NWU0MWJlMzI1ZWYyYmZiMzE1MGJkY2U3MWQ1MTFmZTEzIiwidGFnIjoiIn0=",
        )
        self.session.cookies.set(
            "nusantaratv_session",
            "eyJpdiI6IlREdUVPaXd5cnZkRXQxUm9RdXdKTEE9PSIsInZhbHVlIjoiUUF2UXZuZmU2QXVuMEMrdHVnSW90eGFMcWIwVGhjZmlmVVdXcFpRNlE3amFhWXo1SUJiSGIwT3hOcVlDeTRNYVBPWkZHWjZuRnZjUUZMYS9HYlMyQS81ZFM2ZzRsanBETmpQcWg0dmZVaTlOVFRreCtqZWpJSGJURVE3VmFsbmEiLCJtYWMiOiIyYTJjZTY3NTU4MzE0YmZjNDk3YmE2NGM5ZDk4OTgzY2Y4YzczYTU3Y2UxZjRkMGEwNjA2ZjBiODQwYjgwMjA5IiwidGFnIjoiIn0=",
        )
        self.session.cookies.set("cProps", "4b5a5e03-0b56-44e3-ad55-cd5681f423e6")
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.db = self.client["nusantaratv"]
        self.scraper = self.db["scraper"]
        self.logs = self.db["logs"]

    def __enter__(self):
        print("--------------------------------------------------------")
        print("           Online News Scraper: NusantaraTV")
        print("--------------------------------------------------------")
        print("Started Time:", self.datetime_ist)
        return self

    def insert_log(self):
        log = {
            "scraper_name": "NusantaraTV",
            "start": datetime.now(),
            "status": "Running",
        }
        log_id = self.logs.insert_one(log).inserted_id
        return {"id": str(log_id), "scraper_name": log_id}

    def get_page(self, url):
        csrf_token = "4TCbOcNfg6s18QSdvfduK2cY74sK4W2RFUtrOnkz"
        payload = {"id": "", "_token": csrf_token}
        try:
            response = self.session.post(
                url,
                data=payload,
                headers=self.headers,
                cookies=self.session.cookies,
            )
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error: Failed, status code {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def parse_page(self, content):
        soup = BeautifulSoup(content, "html.parser")
        articles = soup.find_all("h5", {"class": "post-title"})

        if articles:
            print("\nFound articles:")
            for article in articles:
                if article.a:
                    # print(f"Title: {article.a.text.strip()}")
                    print(f"URL: {article.a['href']}")
        else:
            print("No articles found")
        return soup

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print(
            "----------- Crawler Run %f seconds -----------"
            % (time.time() - self.StartTime)
        )


if __name__ == "__main__":
    with NusantaraTV() as crawler:
        logs = crawler.insert_log()
        file_name = os.path.basename(__file__)
        crawler.scraper.update_one(
            {"_id": logs["scraper_name"]}, {"$set": {"file_name": file_name}}
        )
        try:
            url = "https://www.nusantaratv.com/loadmore/load_data"
            page_content = crawler.get_page(url)
            if page_content:
                soup = crawler.parse_page(page_content)
                # Add your data extraction and processing logic here
                crawler.logs.update_one(
                    {"_id": ObjectId(logs["id"])},
                    {
                        "$set": {
                            "end": datetime.now(),
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
                        "status": "Error",
                        "error_message": f"{str(e)} Line : {str(exc_tb.tb_lineno)} {str(exc_type)}",
                    }
                },
            )
