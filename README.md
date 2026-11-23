# sriram's site

Personal research site and handwritten-essay blog, built with [Eleventy](https://www.11ty.dev/) and published to GitHub Pages.

```
npm install        # once
npm start          # live preview at http://localhost:8080, reloads on save
npm run check      # build + verify every internal link
git push           # GitHub Actions builds, checks and deploys
```

## Where things live

| To change…                         | Edit                                   |
|------------------------------------|----------------------------------------|
| Name, email, social links, menu    | `src/_data/site.yaml`                  |
| News on the home page              | `src/_data/news.yaml`                  |
| Research & engineering projects    | `src/_data/projects.yaml`              |
| Manuscripts list                   | `src/_data/manuscripts.yaml`           |
| Experience, education, reading, tools | `src/_data/about.yaml`              |
| Photography                        | `src/_data/photos.yaml` + `src/assets/photos/gallery/` |
| Essays and notes                   | `src/writing/*.md` (one file each)     |
| Intro text on Home / About         | `src/index.njk`, `src/about.njk`       |
| Look and feel                      | `src/assets/style.css`                 |
| Header, footer, shared components  | `src/_includes/`                       |

Content is data; templates only decide how it looks. Every page shares one header, footer and stylesheet.

## Common tasks

**Add a handwritten essay**
1. `python3 tools/stitch_essay.py "~/Downloads/Essay.pdf" my-slug` (add `300` as a third argument if Notes shows a title/date header on page 1). This writes the image tiles to `src/assets/essays/my-slug/` and creates `src/writing/my-slug.md` with the front matter filled in.
2. Open the new `.md` file, set the title, summary and date, and type the transcript below the `---`.
3. Optionally add a line to `src/_data/news.yaml`.

**Add a typed note**: create `src/writing/my-note.md`:
```yaml
---
title: My note
date: 2026-12-01
kindLabel: Note
handwritten: false
summary: One line for the writing list.
---
Text in Markdown…
```

**Add a project**: append an entry to `src/_data/projects.yaml` (the format is described at the top of the file). Give it a `home:` block to feature it on the home page.

**Add a photo**: put the image in `src/assets/photos/gallery/` and add it to `items:` in `src/_data/photos.yaml`.

**Update the CV**: replace `src/assets/cv.pdf`. Redact the phone number first; it is a public page.

## Layout

```
src/
  _data/        content (YAML)
  _includes/    layouts and shared components (Nunjucks)
  assets/       css, images, pdfs (copied as-is)
  writing/      essays and notes (Markdown)
  *.njk         the top-level pages
tools/          essay stitcher, link checker
eleventy.config.js
```
