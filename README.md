# Bian Lab website

Static website for the Bian Lab at Westlake University: <https://bianlab.site>

Originally built by Xueqiang Wang from a Themefisher template. The site is plain HTML/CSS/JavaScript and is published by GitHub Pages from the `master` branch.

## Structure

```text
index.html          Home
research.html       Research
team.html           Team overview
publication.html    Publications
news.html           Lab news
gallery.html        Gallery (life / science / art)
contact.html        Contact and map
members/            One detail page per member
images/             Photos and figures
sources/            Publication PDFs
css/style.css       Site styles
js/script.js        Slider, filter, lightbox and preloader setup
js/lazy-bg.js       Defers header and non-first hero backgrounds
plugins/            Vendored front-end libraries
```

## Updating content

Day-to-day content is edited directly in HTML. To keep the layout consistent, use the internal forms and checks in [`_content-kit/`](_content-kit/README.md):

- [`_content-kit/FORMS.md`](_content-kit/FORMS.md) — fill-in forms for new members, photo replacement, news, gallery, publications and text edits.
- [`_content-kit/prepare_image.py`](_content-kit/prepare_image.py) — creates non-destructive web-sized images at the correct aspect ratio.
- [`_content-kit/check_site.py`](_content-kit/check_site.py) — checks local links, metadata and large images before publishing.

`_content-kit/` starts with `_`, so Jekyll does not publish it with the site.

### Content rules

- Keep the existing Bootstrap grid and section styles; do not redesign the page while adding an item.
- Team portraits: 3:4, 1200×1600, face in the upper third.
- News and Life gallery images: 4:3, 1600×1200.
- Science and art figures: preserve the original aspect ratio and all labels; never crop.
- For new content, keep the source image until the web copy is approved. When replacing an existing file, retain a `.bak` unless the user explicitly approves dropping the original.
- Content images use native `loading="lazy"` and `decoding="async"`; navigation logos stay eager. Header backgrounds use `data-bg`; non-first hero slides use `data-bg-deferred`.
- Check the page locally, then run `python _content-kit/check_site.py` before committing.

## Local preview

Because the site uses root-relative files only within each directory and no build step, it can be opened directly. For a closer match to GitHub Pages, serve the folder over HTTP:

```powershell
python -m http.server 8000
```

Then open <http://localhost:8000/>.

## Deployment

GitHub Pages publishes `master` automatically at <https://bianlab.site>. The custom domain is set in `CNAME`.

The repository is configured with a dedicated SSH key through a repo-local `core.sshCommand`; other Git repositories are unaffected.
