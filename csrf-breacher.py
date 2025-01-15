import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()


class NusantaraTVScraper:

    def __init__(self):
        self.service = Service(os.getenv("GECKODRIVER_PATH"))
        self.options = webdriver.FirefoxOptions()
        self.options.add_argument("--headless")
        self.driver = webdriver.Firefox(service=self.service, options=self.options)
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
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//input[@type='hidden']")
                )
            )
            return self.driver.page_source
        except TimeoutException:
            print("Timeout while waiting for page to load")
            return None

    def fill_hidden_inputs(self, soup):
        hidden = soup.find_all("input", {"type": "hidden"})
        payload_token = os.getenv("TOKEN")
        payload = {"_token": payload_token}

        for input_element in hidden:
            if input_element.get("name") in payload:
                self.driver.execute_script(
                    "arguments[0].value = arguments[1];",
                    input_element.get("value"),
                    payload[input_element.get("name")],
                )

    def parse_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        self.fill_hidden_inputs(soup)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_all_elements_located((By.ID, "post_data"))
            )
        except TimeoutException:
            print("Timeout while waiting for elements with id 'post_data'")
            return None

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        wrap = soup.find("div", {"id": "post_data"})
        title_elements = wrap.find_all("h5", {"class": "post-title"})
        for element in title_elements:
            if element.a:
                print(element.a["href"])
            else:
                print("No titles found")
        return soup

    def __exit__(self, *args):
        self.driver.quit()
        print(
            "----------- Crawler Run %f seconds -----------"
            % (time.time() - self.StartTime)
        )


if __name__ == "__main__":
    with NusantaraTVScraper() as scraper:
        url = "https://nusantaratv.com/"
        page_content = scraper.get_page(url)
        if page_content:
            scraper.parse_page(page_content)
