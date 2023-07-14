import requests


from bs4 import BeautifulSoup
from collections import defaultdict


category_label = str
page_label = str
page_text = str


class ContentManager:


    def __init__(self, pages: dict[category_label, list[page_label]]) -> None:
        self.pages: dict[category_label, list[page_label]] = pages
        self.page_contents: dict[category_label, list[dict[page_label, page_text]]] = defaultdict(list)


    def get_text_from_pages(self, save: bool = True) -> dict[category_label, list[dict[page_label, page_text]]]:
        for category in self.pages:
            for page in self.pages[category]:
                self.get_text_from_page(page, category)
        return self.page_contents

    
    def get_text_from_page(self, page_title: page_label, category: category_label) -> dict[category_label, list[dict[page_label, page_text]]]:
        S = requests.Session()
        URL = "https://es.wikipedia.org/w/api.php"

        PARAMS = {
            "action": "parse",
            "page": page_title,
            "format": "json",
            "prop": "text"
        }

        R = S.get(url=URL, params=PARAMS)
        DATA = R.json()

        html_content = DATA["parse"]["text"]["*"]
        soup = BeautifulSoup(html_content, 'html.parser')

        # headers = [header.get_text() for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        list_items = [li.get_text() for li in soup.find_all('li')]

        content = {
            "list_items": list_items,
            "paragraphs": paragraphs
        }

        self.page_contents[category].append({page_title: content})


if __name__ == "__main__":
    pages = {
        'Brocardos': [
            'Brocardo',
            'Aberratio ictus',
            'Acta est fabula'
            ]
        }
    cm = ContentManager(pages)
    page_contents = cm.get_text_from_pages()
