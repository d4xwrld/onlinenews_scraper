import requests
from bs4 import BeautifulSoup


class NusantaraTVScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://nusantaratv.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
        }

        # Set required cookies from curl request
        # self.session.cookies.get()
        # self.session.cookies.set("cProps", "4b5a5e03-0b56-44e3-ad55-cd5681f423e6")

    def scrape_content(self):
        response = self.session.get(self.base_url, headers=self.headers)
        page = BeautifulSoup(response.text, "html.parser")
        csrf_token = page.find("input", attrs={"name": "_token"})
        session_cookie = self.session.cookies.get("nusantaratv_session")

        if not csrf_token or not session_cookie:
            print("Failed to get CSRF token or session cookie")
            return

        csrf_token = csrf_token["value"]

        load_more_url = f"{self.base_url}/loadmore/load_data"
        self.headers.update(
            {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            }
        )

        self.session.cookies.set("XSRF-TOKEN", csrf_token)
        self.session.cookies.set("nusantaratv_session", session_cookie)

        payload = {"id": "", "_token": csrf_token}

        try:
            response = self.session.post(
                load_more_url,
                data=payload,
                headers=self.headers,
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
