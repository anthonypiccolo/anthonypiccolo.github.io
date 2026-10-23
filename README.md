# anthonypiccolo.xyz

Personal blog, built with [Astro](https://astro.build) and deployed to GitHub Pages by `.github/workflows/deploy.yml` on every push to `master`.

## Writing

```sh
npm install
npm run dev        # http://localhost:4321
```

Add a Markdown file to `src/content/posts/`. The filename becomes the URL slug:

```md
---
title: "My new post"
date: 2026-10-24
category: Running        # URL becomes /running/my-new-post/
description: Optional summary for search results and social cards.
image: /assets/2026/10/hero.jpg   # optional, file lives in public/
draft: true              # optional, only visible in `npm run dev`
---

Post body…
```

Use `.mdx` instead of `.md` to drop interactive components into a post.

Images go in `public/assets/<year>/<month>/` and are referenced as `/assets/...`.

## Layout

- `src/content/posts/` – posts
- `src/pages/` – routes (`about.md`, `index.astro`, `feed.xml.ts`, `[category]/[slug].astro`)
- `src/layouts/`, `src/components/` – page shells
- `src/styles/global.css` – typography and colours
- `src/consts.ts` – site title, description, social links, GTM ID
