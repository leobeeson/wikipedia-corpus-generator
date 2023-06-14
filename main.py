from src.category_manager import CategoryManager
from src.page_manager import PageManager


def main():
    cm = CategoryManager()
    categories = cm.get_category_tree("Términos jurídicos", 2)
    pm = PageManager()
    pages = pm.get_pages_tree(categories)


if __name__ == "__main__":
    main()