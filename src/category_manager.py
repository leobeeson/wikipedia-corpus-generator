import requests
import logging
import json


from src.utils.telemetry import timeit


logger = logging.getLogger(__name__)


category_label = str
category_tree = dict[category_label, list[category_label]]
taxonomy = dict[category_label, category_tree]


class CategoryManager:


    def __init__(self) -> None:
        self.degree: int = 0
        self.categories: category_tree = {}
        self.categories_filtered: category_tree = {}
        self.domain_taxonomies: taxonomy = {}

    
    @timeit
    def get_categories(self, domains: list[category_label], degree: int) -> category_tree:
        self.degree = degree
        for domain in domains:
            self.get_category_tree(domain, degree)
        return self.categories

    
    def get_category_tree(self, domain: category_label, degree: int, current_degree: int = 0) -> None:
        if current_degree > degree:
            return

        subcategories: list[category_label] = self.get_subcategories(domain)
        self.categories[domain] = subcategories
        current_degree += 1

        for subcategory in subcategories:
            self.get_category_tree(subcategory, degree, current_degree)


    def get_subcategories(self, category: category_label) -> list[category_label]:
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


    def filter_categories(
            self, 
            categories: category_tree, 
            full_match_blacklist: list[category_label], 
            partial_blacklist_items: list[str]
            ) -> None:
        categories_copy: category_tree = categories.copy()

        for category, subcategories in categories_copy.items():
            for subcategory in list(subcategories):
                if subcategory in full_match_blacklist:
                    try:
                        categories[category].remove(subcategory)
                        logger.info(f"Remove subcategory {subcategory.upper()} - from category {category.upper()}")
                    except KeyError:
                        logger.info(f"Remove subcategory {subcategory.upper()} - from category {category.upper()} ### Category {category.upper()} had been previously removed.")
                    self._remove_subcategories(categories, subcategory)
                elif any(blacklist_item in subcategory for blacklist_item in partial_blacklist_items):
                    try:
                        categories[category].remove(subcategory)
                        logger.info(f"Remove subcategory {subcategory.upper()} - from category {category.upper()}")
                    except KeyError:
                        logger.info(f"Remove subcategory {subcategory.upper()} - from category {category.upper()} ### Category {category.upper()} had been previously removed.")
                    self._remove_subcategories(categories, subcategory)
        self.categories_filtered = categories


    def generate_domain_taxonomies(self, domains: list[category_label], filtered: bool = True) -> None:
        for domain in domains:
            if filtered:
                domain_taxonomy = self._get_subcategories_dfs(self.categories_filtered, domain)
            else:
                domain_taxonomy = self._get_subcategories_dfs(self.categories, domain)
            self.domain_taxonomies[domain] = domain_taxonomy


    def save_domain_taxonomies(self, domains: list[category_label], prefix: str = "") -> None:
        for domain in domains:
            if domain in self.domain_taxonomies:
                domain_taxonomy: taxonomy = self.domain_taxonomies[domain]
                category_name = domain.replace(" ", "_").lower()
                filename = f"outputs/{prefix}{category_name}_categories_degree_{self.degree}.json"
                with open(filename, "w") as f:
                    json.dump({domain: domain_taxonomy}, f, indent=4, ensure_ascii=False)


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
    cm = CategoryManager()
    categories = cm.get_categories(["Códigos jurídicos"], 3)
    output_cats = cm._get_subcategories_dfs(cm.categories, "Códigos jurídicos")
    output_cats == cm.categories
    output_cats = cm._get_subcategories_dfs(cm.categories, "Códigos por país")
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
    cm.filter_categories(cm.categories, full_match_blacklist, partial_match_blacklist)
    pprint.pprint(cm.categories_filtered)
    output_cats = cm._get_subcategories_dfs(cm.categories_filtered, "Códigos jurídicos")
    output_cats == cm.categories_filtered
