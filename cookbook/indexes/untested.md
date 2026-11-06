# Not Yet Tried

```dataview
TABLE WITHOUT ID link(file.link, title) AS Recipe, source AS Source, created AS Created
FROM "recipes"
WHERE status = "untested"
SORT created DESC
```
