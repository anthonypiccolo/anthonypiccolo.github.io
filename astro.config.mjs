// @ts-check
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import { defineConfig, fontProviders } from 'astro/config';

export default defineConfig({
  site: 'https://anthonypiccolo.xyz',
  trailingSlash: 'always',
  integrations: [mdx(), sitemap()],
  // The old Jekyll site paginated the home page; everything lives on / now.
  redirects: {
    '/page2/': '/',
    // Renamed the day it was published.
    '/tech/building-a-subscription-free-smart-home-pi-5-claude/': '/tech/home-assistant-raspberry-pi-5/',
  },
  markdown: {
    shikiConfig: {
      themes: { light: 'github-light', dark: 'github-dark' },
    },
  },
  fonts: [
    {
      provider: fontProviders.fontsource(),
      name: 'Source Serif 4',
      cssVariable: '--font-serif',
      weights: ['200 900'],
      styles: ['normal', 'italic'],
      subsets: ['latin'],
      fallbacks: ['Georgia', 'serif'],
    },
    {
      provider: fontProviders.fontsource(),
      name: 'IBM Plex Mono',
      cssVariable: '--font-mono',
      weights: ['400', '500'],
      styles: ['normal'],
      subsets: ['latin'],
      fallbacks: ['ui-monospace', 'monospace'],
    },
  ],
});
