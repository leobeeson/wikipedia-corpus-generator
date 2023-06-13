import requests


class CategoryManager:


    def __init__(self) -> None:
        pass

    
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
                print(f'HTTP error occurred: {http_err}')
                break
            except requests.exceptions.ConnectionError as conn_err:
                print(f'Error connecting: {conn_err}')
                break
            except requests.exceptions.Timeout as timeout_err:
                print(f'Timeout error: {timeout_err}')
                break
            except requests.exceptions.RequestException as err:
                print(f'An unexpected error occurred: {err}')
                break

        return subcategories


if __name__ == "__main__":
    cm = CategoryManager()
    subcategories = cm.get_subcategories("Códigos jurídicos")