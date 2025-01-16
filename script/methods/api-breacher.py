import requests
from bs4 import BeautifulSoup
import time
import pytz
from datetime import datetime


class JabarProv:
    def __init__(self):
        self.StartTime = time.time()
        self.IST = pytz.timezone("Asia/Jakarta")
        self.datetime_ist = datetime.now(self.IST)
        self.base_url = "https://jabarprov.go.id/berita/"
        self.counter = 0
        self.page = 1
        self.log_error = []
        self.kategori = ""

    def __enter__(self):
        print("--------------------------------------------------------")
        print("           Online News Scraper: JabarProv")
        print("--------------------------------------------------------")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Ended at:", datetime.now(self.IST))
        print(
            "----------- Crawler Run %f seconds -----------"
            % (time.time() - self.StartTime)
        )
        if exc_type is not None:
            print(f"An error occurred: {exc_type.__name__}: {exc_val}")
            return False  # propagate the exception
        return True

    def get_page(self):
        try:
            soup = BeautifulSoup(requests.get(self.base_url).text, "html.parser")
            result = soup.find(
                "article",
                class_="min-h-[88px] flex overflow-hidden w-full gap-4 border-4 border-transparent rounded-xl group hover:bg-gray-100 hover:border-gray-100 p-1 transition-colors ease-brand duration-250",
            )
            if not result:
                print("No data found, trying to fetch from API")
                base_url = "https://api.jabarprov.go.id/v1/public/news?page="
                response = requests.get(base_url).json()
                print(f"found {len(response['data'])} data")
                links = [item["link"] for item in response["data"]]
                print(f"links: {links}")
                return links
            else:
                return result.prettify()
        except Exception as e:
            print(f"Error in get_page: {str(e)}")
            raise


if __name__ == "__main__":
    with JabarProv() as crawler:
        print(crawler.get_page())
