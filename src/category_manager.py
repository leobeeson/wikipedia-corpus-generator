import requests
import copy


from src.utils.telemetry import timeit


class CategoryManager:


    def __init__(self) -> None:
        self.categories: dict[str, list[str]] = {}

    @timeit
    def get_category_tree(self, domain: str, degree: int, current_degree: int = 0) -> dict[str, list[str]]:
        if current_degree > degree:
            return

        subcategories = self.get_subcategories(domain)
        self.categories[domain] = subcategories
        current_degree += 1

        for subcategory in subcategories:
            self.get_category_tree(subcategory, degree, current_degree)

        return self.categories


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


    def filter_categories(self, full_match_blacklist: dict[str, list[str]], partial_match_blacklist: dict[str, list[str]]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
        category_whitelist = copy.deepcopy(self.categories)  # Create a deep copy of self.categories
        category_blacklist = {}

        # Check for global blacklists
        global_full_match_blacklist = full_match_blacklist.get("_GLOBAL", [])
        global_partial_match_blacklist = partial_match_blacklist.get("_GLOBAL", [])

        for category, subcategories in list(category_whitelist.items()):  # Use list to get a static copy of keys and values
            # Combine category-specific and global blacklists
            full_blacklist_items = full_match_blacklist.get(category, []) + global_full_match_blacklist
            partial_blacklist_items = partial_match_blacklist.get(category, []) + global_partial_match_blacklist

            # Full match: if category matches the blacklist, it's excluded
            if category in full_blacklist_items:
                self._filter_full_match_categories(category, category_whitelist, category_blacklist, full_blacklist_items)

            # Partial match: if category contains a substring in the blacklist, it's excluded
            elif any(blacklist_item in category for blacklist_item in partial_blacklist_items):
                self._filter_partial_match_categories(category, subcategories, partial_blacklist_items, category_whitelist, category_blacklist)
            
        return category_whitelist, category_blacklist


    def _filter_full_match_categories(self, category, category_whitelist, category_blacklist, full_blacklist_items):
        if category in category_whitelist:
            category_blacklist[category] = category_whitelist.pop(category)
            self._remove_subcategories(category_whitelist, category_blacklist, category_blacklist[category])
            for subcategory in category_blacklist[category]:
                if subcategory in full_blacklist_items:
                    self._remove_subcategories(category_whitelist, category_blacklist, [subcategory])


    def _filter_partial_match_categories(self, category, subcategories, partial_blacklist_items, category_whitelist, category_blacklist):
        category_blacklist[category] = []  # Initialize empty list for blacklist
        for subcategory in list(subcategories):  # Use list to get a static copy of subcategories
            # Partial match: if any item in partial_match_blacklist is a substring of subcategory
            if any(blackitem in subcategory for blackitem in partial_blacklist_items):
                category_whitelist[category].remove(subcategory)
                category_blacklist[category].append(subcategory)
                if subcategory in category_whitelist:
                    # Move subcategory and its subcategories to blacklist
                    category_blacklist[subcategory] = category_whitelist.pop(subcategory)
                    self._remove_subcategories(category_whitelist, category_blacklist, category_blacklist[subcategory])


    @staticmethod
    def _remove_subcategories(category_whitelist, category_blacklist, subcategories):
        for subcategory in subcategories:
            if subcategory in category_whitelist:
                category_blacklist[subcategory] = category_whitelist.pop(subcategory)
                # Recursive call with subcategories of current subcategory
                CategoryManager._remove_subcategories(category_whitelist, category_blacklist, category_blacklist[subcategory])



if __name__ == "__main__":
    cm = CategoryManager()
    categories = cm.get_category_tree("Códigos jurídicos", 3)
    full_match_blacklist: dict[str, list[str]] = {"_GLOBAL": [
        "Sharia"
    ]}
    partial_match_blacklist: dict[str, list[str]] = {"_GLOBAL": [
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
    ]}
    category_whitelist, category_blacklist = cm.filter_categories(full_match_blacklist, partial_match_blacklist)