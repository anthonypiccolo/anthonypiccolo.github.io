---
title: "Building an NBA betting model using Google Cloud Platform"
date: 2020-10-12
category: Analytics
draft: true
---
With the NBA season coming to a close, the timing could not be worse - I have developed an [NBA betting model web app](https://nbamodel-223111.web.app/). Although I  don't expect this model to 'beat the books', it's an interesting academic exercise. It has been a good reason to dive deeper into some key software engineering practices.

<figure style="width: 800px">
    <img src="/assets/2020/10/nba-model-web-app.png" alt>
</figure>

The model is based largely on Dean Oliver's [Four Factors](https://www.basketball-reference.com/about/factors.html) - the most important statistics that determine who will win a basketball game. Shooting, turnovers, rebounding and free throws. Other advanced team and player statistics will be included in the future to hopefully produce a more accurate model.

The NBA betting model is built using Google Cloud Platform and is completely serverless. NBA team and schedule data is scraped using python scripts taking advantage of packages such as `BeautifulSoup` and are run using GCP's Cloud Functions. The data is then processed to GCS buckets and subsequently BigQuery. The model is then written in SQL using BigQuery - with a scheduled query outputting `json` to another GCS bucket via another Cloud Function invoked by a Pub/Sub Topic on a daily run. From here a static Vue [website](https://github.com/anthonypiccolo/nbamodel) is hosted via Firebase with a compontent serving the `json` via an Axios HTTP request.

<figure style="width: 1000px">
    <img src="/assets/2020/10/nba-betting-model-architecture.png" alt>
</figure>

This architecture does not use any compute resources and is unlikely to incur any billing costs in GCP.

I plan on writing additional posts detailing the code to scrape the NBA data, build the relevant pipelines and serve the ultimate line for daily matchups.

