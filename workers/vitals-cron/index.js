export default {
  async scheduled(_event, env) {
    const response = await fetch(
      `https://api.github.com/repos/${env.REPO}/actions/workflows/${env.WORKFLOW}/dispatches`,
      {
        method: 'POST',
        headers: {
          Accept: 'application/vnd.github+json',
          Authorization: `Bearer ${env.GITHUB_TOKEN}`,
          'User-Agent': 'vitals-cron',
          'X-GitHub-Api-Version': '2022-11-28',
        },
        body: JSON.stringify({ ref: env.REF }),
      },
    );
    if (!response.ok) {
      throw new Error(`dispatch failed: ${response.status} ${await response.text()}`);
    }
  },
};
