export const SITE_TITLE = 'Anthony Piccolo';
export const SITE_DESCRIPTION =
  'Anthony Piccolo is a digital analyst from Melbourne, blogging about web analytics, data science, data visualisation, digital marketing and more.';

// Google Tag Manager container carried over from the Jekyll site.
export const GTM_ID = 'GTM-5V89W7';

export const SOCIAL_LINKS = [
  { label: 'Strava', href: 'https://www.strava.com/athletes/anthonypiccolo' },
  { label: 'GitHub', href: 'https://github.com/anthonypiccolo' },
  { label: 'LinkedIn', href: 'https://www.linkedin.com/in/anthonyjpiccolo' },
  { label: 'Twitter', href: 'https://twitter.com/anthonypiccolo' },
];

// Written every ~15 min by .github/workflows/vitals.yml to the `vitals` branch.
const DATA_BASE =
  import.meta.env.PUBLIC_DATA_BASE ?? 'https://raw.githubusercontent.com/anthonypiccolo/anthonypiccolo.github.io/vitals/';
export const VITALS_URL = `${DATA_BASE}vitals.json`;
export const RUNNING_URL = `${DATA_BASE}running.json`;
