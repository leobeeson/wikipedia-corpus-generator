import requests
import re


from bs4 import BeautifulSoup
from collections import defaultdict


from src.utils.telemetry import timeit
from src.utils.custom_types import category_label, page_label, page_text, category_pages, corpus


class ContentManager:


    def __init__(self, pages: category_pages, header_id_blacklist: list[str], li_truncators: list[str]) -> None:
        self.pages: category_pages = pages
        self.header_id_blacklist: list[str] = header_id_blacklist
        self.li_truncators: list[str] = li_truncators
        self.page_contents: corpus = defaultdict(list)


    @timeit
    def retrieve_pages_content(self, save: bool = True) -> None:
        for category in self.pages:
            for page in self.pages[category]:
                self.retrieve_page_content(page, category)
        

    
    def retrieve_page_content(self, page_title: page_label, category: category_label) -> page_text:
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
        
        content: list[str] = []

        for tag in soup.find('div', {'class': 'mw-parser-output'}).children:
            tag_text = tag.get_text().strip()

            if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if any(child.get('id') in self.header_id_blacklist for child in tag.find_all('span')):
                    continue
                tag_text = re.sub(r'\[.*?\]$', '', tag_text)
                content.append(f"{tag.name}: {tag_text}")           

            if tag.name in ['ul', 'ol']:
                for li in tag.find_all('li'):
                    li_text = li.get_text().strip()
                    if li_text in self.li_truncators:
                        break
                    content.append(f"{li.name}: {li_text}")                
                continue

            if tag.name == 'p':
                content.append(f"{tag.name}: {tag_text}")

        self.page_contents[category].append({page_title: content})


    def truncate_li(self, list_items: list[str]) -> list[str]:
        truncators: list[str] = [
            "Proyectos Wikimedia", 
            "Identificadores", 
            "Diccionarios y enciclopedias"
            ]
        for i, li in enumerate(list_items):
            if li in truncators:
                return list_items[:i]
        return list_items


    def get_corpus(self) -> corpus:
        return self.page_contents


if __name__ == "__main__":
    pages: category_pages = {
        "Brocardos": [
            "Brocardo",
            "Aberratio ictus",
            "Acta est fabula"
            ],
        "Códigos jurídicos": [
            "Buke Shohatto",
            "Cinco castigos",
            "Codificación (derecho)"
            ],
        "Códigos civiles": [
            "Código civil",
            "Código Civil de Alemania",
            "Código Civil de la República Argentina"
            ]
        }
    header_id_blacklist: list[str] = [
        "Notas", 
        "Referencias",
        "Citas_y_referencias",
        "Bibliografía",
        "Enlaces_externos",
        "Véase_también"
    ]
    li_truncators: list[str] = [
        "Proyectos Wikimedia", 
        "Identificadores", 
        "Diccionarios y enciclopedias"
    ]
    cm = ContentManager(pages, header_id_blacklist, li_truncators)
    cm.retrieve_pages_content()
    cm.page_contents