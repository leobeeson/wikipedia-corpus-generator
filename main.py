from src.category_manager import CategoryManager
from src.page_manager import PageManager
from src.loggers.log_utils import setup_logger
from src.utils.custom_types import category_label, category_tree, taxonomy


logger = setup_logger("")


def main():
    positive_domains: list[category_label] = [
        "Códigos jurídicos", 
        "Casos judiciales", 
        "Principios del derecho", 
        "Términos jurídicos", 
        "Derecho de Colombia", 
        "Rama Judicial de Colombia"
    ]
    negative_domains: list[category_label] = []
    domains = positive_domains + negative_domains
    full_match_blacklist: list[category_label] = [
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
        "Revisión judicial",
        "Ciudadanía honoraria"
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
    degree = 2
    cm = CategoryManager(domains, full_match_blacklist, partial_match_blacklist, degree)
    cm.retrieve_taxonomies(prefix="filtered_gamma_")
    taxonomies: taxonomy = cm.get_taxonomies()


if __name__ == "__main__":
    main()
