import requests
from bs4 import BeautifulSoup


class NusantaraTVScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://nusantaratv.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://nusantaratv.com",
            "Referer": "https://nusantaratv.com/",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

        # Set required cookies from curl request
        self.session.cookies.set(
            "XSRF-TOKEN",
            "eyJpdiI6ImZGSjRTSEYyQ3h0WEg3NzRpeGRHbWc9PSIsInZhbHVlIjoiYmUyS09TTmNaU0xIUFVPS0pNRjRaWHV0OUFTQlNzTmJCWjZBQVBhTllHRERwNG1ZL25PRlVSVDVSSG1zTTRpM3dYU1lTYjlFM2pRUWE2c0ZJTDNPeXVWZHhQZmxONkExK1I2Z0h0Zk5TRzIzNzlNV1hUaENkL3NidzNENDg2dzIiLCJtYWMiOiI1MWQ3MjY0MDU5YTZhZWI5Y2Y1MmQwZjA2ZWQ4YzQ2NWU0MWJlMzI1ZWYyYmZiMzE1MGJkY2U3MWQ1MTFmZTEzIiwidGFnIjoiIn0=",
        )
        self.session.cookies.set(
            "nusantaratv_session",
            "eyJpdiI6IlREdUVPaXd5cnZkRXQxUm9RdXdKTEE9PSIsInZhbHVlIjoiUUF2UXZuZmU2QXVuMEMrdHVnSW90eGFMcWIwVGhjZmlmVVdXcFpRNlE3amFhWXo1SUJiSGIwT3hOcVlDeTRNYVBPWkZHWjZuRnZjUUZMYS9HYlMyQS81ZFM2ZzRsanBETmpQcWg0dmZVaTlOVFRreCtqZWpJSGJURVE3VmFsbmEiLCJtYWMiOiIyYTJjZTY3NTU4MzE0YmZjNDk3YmE2NGM5ZDk4OTgzY2Y4YzczYTU3Y2UxZjRkMGEwNjA2ZjBiODQwYjgwMjA5IiwidGFnIjoiIn0=",
        )
        self.session.cookies.set("cProps", "4b5a5e03-0b56-44e3-ad55-cd5681f423e6")

    def scrape_content(self):
        csrf_token = "4TCbOcNfg6s18QSdvfduK2cY74sK4W2RFUtrOnkz"
        load_more_url = f"{self.base_url}/loadmore/load_data"

        payload = {"id": "", "_token": csrf_token}

        try:
            response = self.session.post(
                load_more_url,
                data=payload,
                headers=self.headers,
                cookies=self.session.cookies,
            )

            if response.status_code == 200:
                self.parse_content(response.text)
            else:
                print(f"Error: {response.status_code}")
                print(response.text)

        except requests.RequestException as e:
            print(f"Request error: {e}")

    def parse_content(self, content):
        soup = BeautifulSoup(content, "html.parser")
        articles = soup.find_all("h5", {"class": "post-title"})

        if articles:
            print("\nFound articles:")
            for article in articles:
                if article.a:
                    print(f"Title: {article.a.text.strip()}")
                    print(f"URL: {article.a['href']}\n")
        else:
            print("No articles found")


def main():
    scraper = NusantaraTVScraper()
    scraper.scrape_content()


if __name__ == "__main__":
    main()
