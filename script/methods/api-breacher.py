import requests
from bs4 import BeautifulSoup


class JabarProv:
    def __init__(self):
        self.base_url = "https://jabarprov.go.id/berita/"
        # self.data = requests.get(self.base_url).text

    def get_page(self):
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
            # return response["data"]
            # return response
        else:
            return result.prettify()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == "__main__":
    with JabarProv() as crawler:
        print(crawler.get_page())
