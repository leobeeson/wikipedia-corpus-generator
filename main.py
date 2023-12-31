from src.utils.custom_types import category_label, taxonomy, category_pages
from src.category_manager import CategoryManager
from src.page_manager import PageManager
from src.content_manager import ContentManager
from src.loggers.log_utils import setup_logger


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
    negative_domains: list[category_label] = [
        "Deportes en Colombia por deporte",
        "Turismo en Colombia",
        "Arte de Colombia",
        "Música de Colombia",
        "Lenguas de Colombia",
        "Religión en Colombia",
        "Ciencia y tecnología de Colombia",
        "Geografía de Colombia",
        "Biodiversidad de Colombia",
        "Geología de Colombia",
        "Medio ambiente de Colombia",
        "Etnias de Colombia",
        "Etnografía de Colombia",
        "Atracciones turísticas de Colombia",
        "Cine de Colombia",
        "Humor de Colombia",
        "Medios de comunicación de Colombia",
        "Educación en Colombia",
        "Economía de Colombia",
        "Educación por materia",
        "Biología",
        "Bioingeniería",
        "Genómica",
        "Ingeniería biomédica",
        "Ciencias de la salud",
        "Géneros y formas musicales",
        "Cartografía",
        "Geografía física",
        "Conceptos físicos",
        "Magnitudes físicas",
        "Teorías físicas",
        "Alimentos",
        "Bebidas",
        "Comidas",
        "Nutrición",
        "Vehículos por tipo",
        "Atracciones turísticas",
        "Bellas artes",
        "Técnicas cinematográficas",
        "Teoría cinematográfica",
        "Terminología cinematográfica",
        "Filosofía del lenguaje",
        "Familias de lenguas",
        "Terminología religiosa"
    ]
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
    header_id_blacklist: list[str] = [
        "Notas", 
        "Referencias",
        "Citas_y_referencias",
        "Bibliografía",
        "Enlaces_externos",
        "Véase_también"
    ]
    li_truncators: list[str] = [
        "Proyectos Wikimedia", 
        "Identificadores", 
        "Diccionarios y enciclopedias"
    ]
    degree = 2

    # Positive Corpus
    # category_manager_pos = CategoryManager(positive_domains, full_match_blacklist, partial_match_blacklist, degree)
    # category_manager_pos.retrieve_taxonomies(prefix="a_positive_")
    # taxonomies_pos: taxonomy = category_manager_pos.get_taxonomies()
    
    # page_manager_pos = PageManager(taxonomies_pos, degree)
    # page_manager_pos.retrieve_taxonomy_pages(prefix="a_positive_")
    # pages_pos: category_pages = page_manager_pos.get_pages()
    
    # content_manager_pos = ContentManager(
    #     pages_pos, 
    #     taxonomies_pos, 
    #     header_id_blacklist, 
    #     li_truncators, 
    #     degree, 
    #     prefix="a_positive_"
    #     )
    # content_manager_pos.retrieve_taxonomy_content()
    
    # Negative Corpus
    category_manager_neg = CategoryManager(negative_domains, full_match_blacklist, partial_match_blacklist, degree)
    category_manager_neg.retrieve_taxonomies(prefix="b_negative_")
    taxonomies_neg: taxonomy = category_manager_neg.get_taxonomies()
    
    page_manager_neg = PageManager(taxonomies_neg, degree)
    page_manager_neg.retrieve_taxonomy_pages(prefix="b_negative_")
    pages_neg: category_pages = page_manager_neg.get_pages()
    
    content_manager_neg = ContentManager(
        pages_neg, 
        taxonomies_neg, 
        header_id_blacklist, 
        li_truncators, 
        degree, 
        prefix="b_negative_"
        )
    content_manager_neg.retrieve_taxonomy_content()

if __name__ == "__main__":
    main()
