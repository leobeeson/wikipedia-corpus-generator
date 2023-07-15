

# Categories:
category_label = str
category_tree = dict[category_label, list[category_label]]
taxonomy = dict[category_label, category_tree]

# Pages:
page_label = str
category_pages = dict[category_label, list[page_label]]
page_text = str
corpus = dict[page_label, page_text]