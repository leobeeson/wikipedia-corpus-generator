import pprint


from src.category_manager import CategoryManager
from src.page_manager import PageManager
from src.loggers.log_utils import setup_logger


logger = setup_logger("")


def main():
    cm = CategoryManager()
    positive_categories: list[str] = [
        "Códigos jurídicos", 
        "Casos judiciales", 
        "Principios del derecho", 
        "Términos jurídicos", 
        "Derecho de Colombia", 
        "Rama Judicial de Colombia"
    ]
    categories = cm.get_categories(positive_categories, 2)
    pprint.pprint(categories)
    full_match_blacklist: list[str] = [
        "Sharia",
        "Sharia", 
        "Error judicial", 
        "Personas", 
        "Referéndums", 
        "Abogados de Colombia", 
        "Crimen en Colombia", 
        "Juristas de Colombia", 
        "Muerte en Colombia", 
        "Policía de Colombia",
        "Magistrados del Consejo de Estado de Colombia", 
        "Fiscal General de la Nación (Colombia)",
        "Ministerio de Comercio, Industria y Turismo de Colombia",
        "Educación jurídica",
        "Derecho alimentario",
        "Política alimentaria",
        "Películas por género",
        "Revisión judicial"
        ]
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
    total_pages = sum([len(pages[category]) for category in pages])
    pprint.pprint(pages)
    print(f"Total pages: {total_pages}")


if __name__ == "__main__":
    main()
