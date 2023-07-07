# WBS

## Filtering Categories

1. Iterate over the root keys of the dictionary `categories`, where each key represents a category.
2. For every key, get its value object, which represent a list of the category's subcategories, i.e. the `subcategories_list` object.
3. For every subcategory:
   1. check if its value (a string) is present in a blacklist of categories, i.e. the `category_blacklist`.
   2. If a subcategory is present in `category_blacklist`:
      1. Remove it from the `subcategories_list`.
      2. Extract (i.e. pop) it's key-value pair from `categories`.
      3. For every subcategory in its `subcategories_list`, recursively extract it and its subcategories from `categories`.

### Unfiltered Dictionary

```json
{
  "category_a": ["category_b", "category_c"],
  "category_b": ["category_d"],
  "category_c": ["category_e"],
  "category_d": [],
  "category_e": []
}
```

### Blacklist

```json
{
  "blacklist": ["category_b", "category_e"]
}
```

### Filtered Dictionary

```json
{
  "category_a": ["category_c"],
  "category_c": [],
}
```

## Notes

### Retrieving All Subcategories without Filtering In place

If you intend to generate the full subcategory tree for a given domain (i.e. `filter_in_place == False`) for a depth greater than 2 (i.e. `degree > 2`), you could run into a `RecursionError: maximum recursion depth exceeded`.

To **potentially** solve this, you will have to increase the maximum depth of recursive calls in Python with [sys.setrecursionlimit(limit)](https://docs.python.org/2/library/sys.html#sys.setrecursionlimit), e.g.:

```python
import sys
sys.setrecursionlimit(3000)
```

Also, as per [here](https://stackoverflow.com/a/7081504) take into account that `limit` in `sys.setrecursionlimit(limit: int)` actually refers to the max stack depth and not really recursion depth.
