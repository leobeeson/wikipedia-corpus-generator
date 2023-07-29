import requests
import re
import json
import os
import logging


from bs4 import BeautifulSoup
from collections import defaultdict
from tqdm import tqdm


from src.utils.telemetry import timeit, time_category_iteration
from src.utils.custom_types import category_label, page_label, page_text, category_pages, taxonomy, category_tree, corpus


logger = logging.getLogger(__name__)


class ContentManager:


    def __init__(self, 
                 pages: category_pages, 
                 taxonomies: taxonomy, 
                 header_id_blacklist: list[str], 
                 li_truncators: list[str], 
                 degree: int,
                 output_path: str = "outputs/",
                 prefix: str = ""
                 ) -> None:
        self.pages: category_pages = pages
        self.taxonomies: taxonomy = taxonomies
        self.header_id_blacklist: list[str] = header_id_blacklist
        self.li_truncators: list[str] = li_truncators
        self.degree: int = degree
        self.output_path: str = output_path
        self.prefix: str = prefix
        self.page_contents: corpus = defaultdict(list)
        self.domain_contents: corpus = defaultdict(list)
        self.update_page_contents_from_disk()
        self.total_pages: int = self.calculate_total_pages_to_process()


    def retrieve_taxonomy_content(self, 
                                  save: bool = True
                                  ) -> None:
        progress_bar = tqdm(total=self.total_pages, desc='Retrieving content', dynamic_ncols=True)
        
        for domain in self.taxonomies:
            domain_taxonomy: category_tree = self.taxonomies[domain]
            for category in domain_taxonomy:
                self.retrieve_pages_content(category, progress_bar)
                for subcategory in domain_taxonomy[category]:
                    self.retrieve_pages_content(subcategory, progress_bar)        
            if save:
                self.save_content(domain)
                self.domain_contents = defaultdict(list)
        
        progress_bar.close()


    @time_category_iteration
    def retrieve_pages_content(self, category: category_label, progress_bar: tqdm) -> None:
        for page in self.pages[category]:
            if page in self.page_contents:
                progress_bar.update()
                continue
            content = self.retrieve_page_content(page)
            self.page_contents[page] = content
            self.domain_contents[page] = content
            progress_bar.update()
        

    
    def retrieve_page_content(self, page_title: page_label) -> page_text:
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
        
        content: page_text = []
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

        return content


    def save_content(self, domain: category_label) -> None:
        domain_name = domain.replace(" ", "_").lower()
        filename = f"{self.output_path}{self.prefix}{domain_name}_content_degree_{self.degree}.json"
        
        if not os.path.exists(filename):
            with open(filename, "w") as out_file:
                json.dump({domain: self.domain_contents}, out_file, indent=4, ensure_ascii=False)
        else:
            logger.info(f"Content for domain {domain_name.upper()} already exists, skipping the saving operation.")


    def update_page_contents_from_disk(self) -> None:
        for domain in self.taxonomies:
            domain_name = domain.replace(" ", "_").lower()
            filename = f"{self.output_path}{self.prefix}{domain_name}_content_degree_{self.degree}.json"
            if os.path.exists(filename):
                with open(filename, 'r') as in_file:
                    domain_content = json.load(in_file)
                    for page, content in domain_content[domain].items():
                        self.page_contents[page] = content


    @timeit
    def calculate_total_pages_to_process(self) -> int:
        total_pages: int = 0
        for domain in self.taxonomies:
            domain_taxonomy: category_tree = self.taxonomies[domain]
            for category in domain_taxonomy:
                total_pages += len(self.pages[category])
                for subcategory in domain_taxonomy[category]:
                    total_pages += len(self.pages[subcategory])
        return total_pages


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

    