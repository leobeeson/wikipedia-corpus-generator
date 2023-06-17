import requests
import logging


logger = logging.getLogger(__name__)


from src.utils.telemetry import timeit


class PageManager:


    def __init__(self) -> None:
        self.pages: dict[str, list[str]] = {}


    @timeit
    def get_pages_tree(self, categories: dict[str, list[str]]) -> dict[str, list[str]]:
        for category in categories:
            self.pages[category] = self.get_category_pages(category)
        return self.pages


    def get_category_pages(self, category: str) -> list[str]:
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

        pages = []
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


if __name__ == "__main__":
    from category_manager import CategoryManager
    cm = CategoryManager()
    categories = cm.get_category_tree("Términos jurídicos", 2)
    pm = PageManager()
    pages = pm.get_pages_tree(categories)
    print(pages)