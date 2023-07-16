import requests
import json
import logging


from src.utils.telemetry import time_category_iteration
from src.utils.custom_types import category_pages, category_label, taxonomy, category_tree, page_label


logger = logging.getLogger(__name__)


class PageManager:


    def __init__(self, taxonomies: taxonomy, degree: int) -> None:
        self.taxonomies: taxonomy = taxonomies
        self.degree: int = degree
        self.pages: category_pages = {}


    def retrieve_taxonomy_pages(self,
                                save: bool = True,
                                output_path: str = "outputs/",
                                prefix: str = ""
                                ) -> None:
            for domain in self.taxonomies:
                self.retrieve_domain_pages(domain)
            if save:
                self.save_pages(output_path, prefix)


    @time_category_iteration
    def retrieve_domain_pages(self, domain: category_label) -> category_pages:        
            if domain in self.pages:
                pass
            else:
                self.pages[domain] = self.retrieve_category_pages(domain)
            domain_taxonomy: category_tree = self.taxonomies[domain]
            for category in domain_taxonomy:
                if category in self.pages:
                    pass
                else:
                    self.pages[category] = self.retrieve_category_pages(category)
                    subcategories: list[category_label] = domain_taxonomy[category]
                    for subcategory in subcategories:
                        if subcategory in self.pages:
                            pass
                        else:
                            self.pages[subcategory] = self.retrieve_category_pages(subcategory)


    def retrieve_category_pages(self, category: str) -> list[page_label]:
        S = requests.Session()
        URL = "https://es.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": "Categoría:" + category,
            "cmtype": "page",
            "cmlimit": 500
        }

        pages: list[page_label] = []
        while True:
            try:
                R = S.get(url=URL, params=PARAMS)
                R.raise_for_status()
                DATA = R.json()

                if 'query' in DATA:
                    pages += [page['title'] for page in DATA['query']['categorymembers']]

                if 'continue' in DATA:
                    PARAMS['cmcontinue'] = DATA['continue']['cmcontinue']
                else:
                    break

            except requests.exceptions.HTTPError as http_err:
                logger.warning(f'HTTP error occurred: {http_err}')
                break
            except requests.exceptions.ConnectionError as conn_err:
                logger.warning(f'Error connecting: {conn_err}')
                break
            except requests.exceptions.Timeout as timeout_err:
                logger.warning(f'Timeout error: {timeout_err}')
                break
            except requests.exceptions.RequestException as err:
                logger.warning(f'An unexpected error occurred: {err}')
                break

        return pages


    def save_pages(self, output_path: str, prefix: str) -> None:
        for domain in self.taxonomies:
            domain_pages: category_pages = {}
            domain_taxonomy: category_tree = self.taxonomies[domain]
            for category in domain_taxonomy:
                subcategories: list[category_label] = domain_taxonomy[category]
                for subcategory in subcategories:
                    domain_pages[subcategory] = self.pages[subcategory]
            domain_name = domain.replace(" ", "_").lower()
            filename = f"{output_path}{prefix}{domain_name}_pages_degree_{self.degree}.json"
            with open(filename, "w") as out_file:
                json.dump({domain: domain_pages}, out_file, indent=4, ensure_ascii=False)


    def get_pages(self) -> category_pages:
        return self.pages


if __name__ == "__main__":
    import pprint
    from category_manager import CategoryManager
    positive_domains = ["Códigos jurídicos"]
    cm = CategoryManager()
    categories = cm.retrieve_categories(positive_domains, 3)
    full_match_blacklist: list[str] = ["Sharia"]
    partial_match_blacklist: list[str] = [
        "por país",
        "LGBT", 
        "brujería",
        "Anexos",
        "por continente",
        "por fecha",
        "por siglo",
        "por década",
        "por año",
        "por período",
        "por país",
        "por territorio",
        "por departamento",
        "por localidad",
        "por región",
        "Ministros",
        "Presidentes",
        "Gerentes",
        "Directores",
        "Actores",
        "Actrices",
        "Directoras"
    ]
    cm.filter_subcategories(cm.categories, full_match_blacklist, partial_match_blacklist)
    pprint.pprint(cm.categories_filtered)
    pm = PageManager()
    pages = pm.retrieve_domain_pages(categories)
    pprint.pprint(pages)