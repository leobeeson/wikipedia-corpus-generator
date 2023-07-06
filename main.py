from src.category_manager import CategoryManager
from src.page_manager import PageManager
from src.loggers.log_utils import setup_logger


logger = setup_logger("")


def main():
    positive_categories: list[str] = [
        "Códigos jurídicos", 
        # "Casos judiciales", 
        # "Principios del derecho", 
        # "Términos jurídicos", 
        # "Derecho de Colombia", 
        # "Rama Judicial de Colombia"
    ]
    degree = 3
    cm = CategoryManager()
    categories = cm.get_categories(positive_categories, degree)
    # cm.save_categories(positive_categories, degree, prefix="raw_", filtered=False)
    
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
    cm.filter_categories(categories, full_match_blacklist, partial_match_blacklist)
    cm.generate_domain_taxonomies(positive_categories, filtered=True)
    cm.save_domain_taxonomies(positive_categories, prefix="filtered_")  


if __name__ == "__main__":
    main()
