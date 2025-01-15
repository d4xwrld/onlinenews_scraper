import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

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

    def __enter__(self):
        print("--------------------------------------------------------")
        print("           Online News Scraper: NusantaraTV")
        print("--------------------------------------------------------")
        print("Started Time:", self.datetime_ist)
        return self

    def get_page(self, url):
        try:
            # csrf_token = os.getenv("CSRF_TOKEN")
            headers_with_csrf = headers.copy()
            headers_with_csrf["X-CSRF-Token"] = token
            response = requests.post(url, headers=headers_with_csrf)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Error: Failed, status code {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def parse_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        target_class = "website-top-news slick-initialized slick-slider slick-dotted"
        if soup.find(class_=target_class):
            print("Class found!")
            print(soup.prettify())
        else:
            print(f"Class '{target_class}' not found")
        return soup

    # def __exit__(self, exc_type, exc_value, exc_traceback):
    def __exit__(self, exc_type, exc_value, exc_traceback):
        # Unused parameters
        pass
        print(
            "----------- Crawler Run %f seconds -----------"
            % (time.time() - self.StartTime)
        )


if __name__ == "__main__":
    with NusantaraTV() as crawler:
        url = "https://www.nusantaratv.com/"
        page_content = crawler.get_page(url)
        if page_content:
            soup = crawler.parse_page(page_content)
            # Add your data extraction and processing logic here
