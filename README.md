# Duarte Lab @ UCSD

Source for the [Duarte Lab](https://jduarte.physics.ucsd.edu/) website, built with [Jekyll](https://jekyllrb.com/) and served via GitHub Pages from the `gh-pages` branch.

## Structure

- `_config.yml` — site configuration
- `_layouts/default.html` — shared page shell (head, nav, footer)
- `_includes/` — shared head/nav/footer partials
- `_data/papers.yml` — the research entries (see below)
- `scripts/fetch_papers.py` — fills in paper metadata from INSPIRE-HEP
- `index.html`, `research.html`, `people.html`, `teaching.html`, `resources.html`, `404.html` — page content, each with Jekyll front matter (`layout`, `active_nav`, `title`)
- `images/`, `css/`, `js/`, `vendor/`, `favicon_io/` — static assets (Bootstrap 4 + jQuery, vendored under `vendor/`)

To update the nav, footer, or `<head>`, edit the corresponding file under `_includes/` once instead of every page.

## Adding a paper to the research page

`research.html` renders whatever is in `_data/papers.yml`, newest first. To add a
paper, put a new entry at the top of that file:

```yaml
- arxiv: '2601.12345'          # or: doi: 10.1103/PhysRevD.000.000000
  image: my_figure.png         # from images/ — pick this yourself, see below
  links:
    - label: Paper
      url: https://arxiv.org/abs/2601.12345
      text: arXiv:2601.12345
    - label: Code
      url: https://github.com/...
      text: https://github.com/...
```

then run:

```
python3 scripts/fetch_papers.py
```

It fills in `title:` and `abstract:` from INSPIRE-HEP and converts any `$...$`
math to the `\( ... \)` delimiters this site's MathJax is configured for.

Notes:

- **Existing `title:`/`abstract:` values are never overwritten.** Several
  abstracts here are deliberately trimmed versions of the official one, and a
  re-run must not silently revert those edits. Write the field in by hand and
  the script leaves it alone. `--diff` reports where our text differs from
  INSPIRE on purpose.
- **The image is chosen by hand, on purpose.** INSPIRE does expose paper
  figures, but which figure belongs on a landing page is an editorial call —
  existing entries use anything from figure 1 to figure 3 of the source paper,
  and many use a CMS public-results figure or a custom diagram that isn't in
  the paper at all.
- Entries without an `arxiv:` or `doi:` (e.g. CMS PAS / CDS records) need
  `title:` and `abstract:` filled in manually; the script will say so.
- `python3 scripts/fetch_papers.py --check` exits non-zero if any entry is
  missing metadata.
- The first 10 entries show by default; the rest sit behind the "Show older
  research" toggle. Change `collapse_after` in `research.html` to adjust.

## Local preview

```
bundle install
bundle exec jekyll serve
```

Then open http://localhost:4000.

## Credits

Based on the [Modern Business](https://startbootstrap.com/template-overviews/modern-business/) Bootstrap template by Start Bootstrap, MIT licensed.
