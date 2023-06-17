import requests
import logging


from src.utils.telemetry import timeit


logger = logging.getLogger(__name__)


class CategoryManager:


    def __init__(self) -> None:
        self.categories: dict[str, list[str]] = {}

    
    @timeit
    def get_categories(self, domains: list[str], degree: int) -> dict[str, list[str]]:
        for domain in domains:
            self.get_category_tree(domain, degree)
        return self.categories

    
    def get_category_tree(self, domain: str, degree: int, current_degree: int = 0) -> None:
        if current_degree > degree:
            return

        subcategories = self.get_subcategories(domain)
        self.categories[domain] = subcategories
        current_degree += 1

        for subcategory in subcategories:
            self.get_category_tree(subcategory, degree, current_degree)


    def get_subcategories(self, category: str) -> list[str]:
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

        subcategories = []
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
            categories: dict[str, list[str]], 
            full_match_blacklist: list[str], 
            partial_blacklist_items: list[str]
            ) -> dict[str, list[str]]:
        categories_copy: dict[str, list[str]] = categories.copy()  # We'll iterate over a copy of categories

        for category, subcategories in categories_copy.items():
            for subcategory in list(subcategories):  # Iterate over a copy of subcategories
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
        return categories


    @staticmethod
    def _remove_subcategories(categories: dict[str, list[str]], category: str) -> None:
        if category in categories:
            for subcategory in categories[category]:
                CategoryManager._remove_subcategories(categories, subcategory)
            del categories[category]
            logger.info(f"Remove category {category.upper()}")


if __name__ == "__main__":
    import pprint
    cm = CategoryManager()
    categories = cm.get_category_tree("Códigos jurídicos", 3)
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
    category_whitelist= cm.filter_categories(categories, full_match_blacklist, partial_match_blacklist)
    pprint.pprint(category_whitelist)
