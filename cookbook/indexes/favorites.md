# Favorites

```dataview
TABLE WITHOUT ID link(file.link, title) AS Recipe, category AS Category, rating AS Rating
FROM "recipes"
WHERE status = "favorite"
SORT rating DESC, title ASC
```
