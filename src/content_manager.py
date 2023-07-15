import requests
import re
import logging


from bs4 import BeautifulSoup
from collections import defaultdict


from src.utils.telemetry import timeit
from src.utils.custom_types import category_label, page_label, page_text, category_pages, corpus


logger = logging.getLogger(__name__)


class ContentManager:


    def __init__(self, pages: category_pages, header_id_blacklist: list[str], li_truncators: list[str]) -> None:
        self.pages: category_pages = pages
        self.header_id_blacklist: list[str] = header_id_blacklist
        self.li_truncators: list[str] = li_truncators
        self.page_contents: corpus = defaultdict(list)


    def retrieve_taxonomy_content(self, 
                                  save: bool = True,
                                  output_path: str = "outputs/",
                                  prefix: str = ""
                                  ) -> None:
        for category in self.pages:
            for page in self.pages[category]:
                self.retrieve_page_content(page, category)
        if save:
            self.save_taxonomy_content()


    @timeit
    def retrieve_pages_content(self) -> None:
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
        blacklisted_section: bool = False
        for tag in soup.find('div', {'class': 'mw-parser-output'}).children:
            
            if blacklisted_section:
                if tag.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    continue
                else:
                    blacklisted_section = False

            tag_text = tag.get_text().strip()

            if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if any(child.get('id') in self.header_id_blacklist for child in tag.find_all('span')):
                    blacklisted_section = True
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

            if tag.name == 'dl':
                for dt in tag.find_all('dt'):
                    dt_text = dt.get_text().strip()
                    content.append(f"{dt.name}: {dt_text}")
                continue

        self.page_contents[category].append({page_title: content})


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

    # "li: Portal:Derecho. Contenido relacionado con Derecho."
    # "li: Codificación",
    # "li: Código de comercio",
    # "li: Fuentes extralegales",
    # "li: Categoría:Códigos civiles", "li: Guzmán Brito, A. (2000). La codificación civil en Iberoamérica. Siglos XIX y XX. Santiago: Editorial Jurídica de Chile. ISBN\xa0956-10-1310-X."
