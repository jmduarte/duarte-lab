# Duarte Lab @ UCSD

Source for the [Duarte Lab](https://jduarte.physics.ucsd.edu/) website, built with [Jekyll](https://jekyllrb.com/) and served via GitHub Pages from the `gh-pages` branch.

## Structure

- `_config.yml` — site configuration
- `_layouts/default.html` — shared page shell (head, nav, footer)
- `_includes/` — shared head/nav/footer partials
- `index.html`, `research.html`, `people.html`, `teaching.html`, `resources.html`, `404.html` — page content, each with Jekyll front matter (`layout`, `active_nav`, `title`)
- `images/`, `css/`, `js/`, `vendor/`, `favicon_io/` — static assets (Bootstrap 4 + jQuery, vendored under `vendor/`)

To update the nav, footer, or `<head>`, edit the corresponding file under `_includes/` once instead of every page.

## Local preview

```
bundle install
bundle exec jekyll serve
```

Then open http://localhost:4000.

## Credits

Based on the [Modern Business](https://startbootstrap.com/template-overviews/modern-business/) Bootstrap template by Start Bootstrap, MIT licensed.
