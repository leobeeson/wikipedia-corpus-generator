import requests
import logging
import json


from src.utils.custom_types import category_label, category_tree, taxonomy
from src.utils.telemetry import time_category_iteration


logger = logging.getLogger(__name__)


class CategoryManager:


    def __init__(
            self, 
            domains: list[category_label],
            full_match_blacklist: list[category_label], 
            partial_blacklist_items: list[str],
            degree: int = 1
            ) -> None:
        self.domains: list[category_label] = domains
        self.full_match_blacklist: list[category_label] = full_match_blacklist
        self.partial_blacklist_items: list[str] = partial_blacklist_items
        self.degree: int = degree
        self.categories: category_tree = {}
        self.taxonomies: taxonomy = {}


    def retrieve_taxonomies(
            self,
            filter_in_place: bool = True,
            save: bool = True,
            output_path: str = "outputs/",
            prefix: str = ""
            ) -> None:
        self.retrieve_categories(filter_in_place)
        if not filter_in_place:
            self.filter_subcategories()
        self.generate_taxonomies()
        if save:
            self.save_taxonomies(output_path, prefix)

    
    def retrieve_categories(self, filter_in_place: bool) -> None:
        for domain in self.domains:
            if filter_in_place:
                self.filtered_recursive_category_search(domain, self.degree)
                self.filter_subcategories()
            else:
                self.recursive_category_search(domain, self.degree)

    
    @time_category_iteration
    def recursive_category_search(self, domain: category_label, degree: int, current_degree: int = 0) -> None:
        if current_degree > degree:
            return

        subcategories: list[category_label] = self.retrieve_subcategories(domain)
        self.categories[domain] = subcategories
        current_degree += 1

        for subcategory in subcategories:
            self.recursive_category_search(subcategory, degree, current_degree)

    
    @time_category_iteration
    def filtered_recursive_category_search(self, domain: category_label, degree: int, current_degree: int = 0) -> None:
        if current_degree >= degree:
            return

        subcategories: list[category_label] = self.retrieve_subcategories(domain)
        self.categories[domain] = subcategories
        current_degree += 1

        for subcategory in subcategories:
            if subcategory not in self.full_match_blacklist:
                if not any(blacklist_item in subcategory for blacklist_item in self.partial_blacklist_items):
                    self.filtered_recursive_category_search(subcategory, degree, current_degree)


    def retrieve_subcategories(self, category: category_label) -> list[category_label]:
        S = requests.Session()
        URL = "https://es.wikipedia.org/w/api.php"
        PARAMS = {
            "action": "query",
            "format": "json",
            "list": "categorymembers",
            "cmtitle": "Categoría:" + category,
            "cmtype": "subcat",
            "cmlimit": 500
        }

        subcategories: list[category_label] = []
        while True:
            try:
                R = S.get(url=URL, params=PARAMS)
                R.raise_for_status()
                DATA = R.json()

                if 'query' in DATA:
                    subcategories += [subcategory['title'].replace('Categoría:', '') for subcategory in DATA['query']['categorymembers']]

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

        return subcategories


    def filter_subcategories(self) -> None:
        categories_copy: category_tree = self.categories.copy()

        for category, subcategories in categories_copy.items():
            for subcategory in list(subcategories):
                if subcategory in self.full_match_blacklist:
                    try:
                        self.categories[category].remove(subcategory)
                        logger.info(f"Remove subcategory {subcategory.upper()} - from category {category.upper()}")
                    except KeyError:
                        logger.info(f"Remove subcategory {subcategory.upper()} - from category {category.upper()} ### Category {category.upper()} had been previously removed.")
                    self._remove_subcategories(self.categories, subcategory)
                elif any(blacklist_item in subcategory for blacklist_item in self.partial_blacklist_items):
                    try:
                        self.categories[category].remove(subcategory)
                        logger.info(f"Remove subcategory {subcategory.upper()} - from category {category.upper()}")
                    except KeyError:
                        logger.info(f"Remove subcategory {subcategory.upper()} - from category {category.upper()} ### Category {category.upper()} had been previously removed.")
                    self._remove_subcategories(self.categories, subcategory)


    def generate_taxonomies(self) -> None:
        for domain in self.domains:
            domain_taxonomy = self._get_subcategories_dfs(self.categories, domain)
            self.taxonomies[domain] = domain_taxonomy


    def save_taxonomies(self, output_path: str, prefix: str) -> None:
        for domain in self.domains:
            if domain in self.taxonomies:
                domain_taxonomy: taxonomy = self.taxonomies[domain]
                domain_name = domain.replace(" ", "_").lower()
                filename = f"{output_path}{prefix}{domain_name}_categories_degree_{self.degree}.json"
                with open(filename, "w") as out_file:
                    json.dump({domain: domain_taxonomy}, out_file, indent=4, ensure_ascii=False)


    def get_taxonomies(self) -> taxonomy:
        return self.taxonomies


    @staticmethod
    def _remove_subcategories(categories: dict[category_label, list[category_label]], category: category_label) -> None:
        if category in categories:
            for subcategory in categories[category]:
                CategoryManager._remove_subcategories(categories, subcategory)
            del categories[category]
            logger.info(f"Remove category {category.upper()}")


    @staticmethod
    def _get_subcategories_dfs(category_tree: dict[category_label, list[category_label]], domain: category_label) -> dict[category_label, list[category_label]]:
        subcategory_tree: dict[category_label, list[category_label]] = {}
        if domain in category_tree:
            subcategory_tree[domain] = category_tree[domain]
            for subcategory in category_tree[domain]:
                subcategory_tree.update(CategoryManager._get_subcategories_dfs(category_tree, subcategory))
        return subcategory_tree


if __name__ == "__main__":
    import pprint
    domains: list[category_label] = ["Códigos jurídicos"]
    full_match_blacklist: list[category_label] = ["Sharia"]
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
    degree: int = 3
    
    cm_in_place = CategoryManager(domains, full_match_blacklist, partial_match_blacklist, degree)
    cm_in_place.retrieve_categories(filter_in_place=True)
    pprint.pprint(cm_in_place.categories)
    
    cm = CategoryManager(domains, full_match_blacklist, partial_match_blacklist, degree)
    cm.retrieve_categories(filter_in_place=False)
    pprint.pprint(cm.categories)

    output_cats = cm._get_subcategories_dfs(cm.categories, "Códigos jurídicos")
    output_cats == cm.categories
    output_cats = cm._get_subcategories_dfs(cm.categories, "Códigos por país")
    pprint.pprint(output_cats)
    
    cm.filter_subcategories()
    pprint.pprint(cm.categories)
    cm_in_place.categories == cm.categories

    output_cats = cm._get_subcategories_dfs(cm.categories, "Códigos jurídicos")
    output_cats == cm.categories

    cm_pipeline = CategoryManager(domains, full_match_blacklist, partial_match_blacklist, degree)
    cm_pipeline.retrieve_taxonomies(output_path="temp/", prefix="test_")