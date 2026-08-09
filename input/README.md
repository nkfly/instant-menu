Place source Japanese menu images in restaurant-specific directories.

Recommended layout:

```text
input/
  honoya/
    menu_jp.png
  another_restaurant/
    menu_jp.jpg
```

When the input image is stored under `input/<restaurant>/`, the CLI will default to writing artifacts under `output/<restaurant>/`.
