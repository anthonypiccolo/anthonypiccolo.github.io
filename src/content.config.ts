import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const posts = defineCollection({
  // The filename (minus extension) is the post's slug.
  loader: glob({ base: './src/content/posts', pattern: '**/*.{md,mdx}' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    // Part of the URL (/analytics/my-post/), matching the old Jekyll permalinks.
    category: z.string(),
    description: z.string().optional(),
    // Path to an image in public/, e.g. /assets/hero.png
    image: z.string().optional(),
    // Social share card only (not shown on the page). Falls back to `image`, then the bio photo.
    ogImage: z.string().optional(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { posts };
