import pprint


from src.category_manager import CategoryManager
from src.page_manager import PageManager


def main():
    cm = CategoryManager()
    categories = cm.get_category_tree("Códigos jurídicos", 3)
    pprint.pprint(categories)
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
    pm = PageManager()
    pages = pm.get_pages_tree(category_whitelist)
    pprint.pprint(pages)


if __name__ == "__main__":
    main()
