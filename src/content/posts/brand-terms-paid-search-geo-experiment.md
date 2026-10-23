---
title: "Should you bid on brand terms in Paid Search? A randomised geo-experiment"
date: 2019-03-15
category: Analytics
image: /assets/paid-search-brand-bid.png
---
Paid Search advertising has major advantages, not only over traditional forms of media (print, tv and radio) but even other digital channels. Search has access to a huge amount of metrics for measurement. The intent driven nature of search means there is a high degree of relevance. In a pay-per-click model, an advertiser will only pay a publisher (Google or Bing) when a user clicks on an ad.  

Paid Search is a mature advertising channel, [making up 44% of digital advertising spend in Australia in FY18](https://www.iabaustralia.com.au/news-and-updates/iab-press-releases/item/22-iab-press-releases/2624-marketers-continue-to-reinvest-strongly-in-digital-advertising). However, the question of incrementality on brand remains. That is, if an advertiser is bidding on their brand term where there is no competition, what is incremental? Without the presence of an ad when a user queries the brand term, would all sales simply flow through to organic search?

One of the key arguments for bidding on brand is brand protection, ensuring competitors aren't appearing before the first organic result. Another key advantage is incrementality, where there is the opportunity to drive more traffic by having both an organic and paid result on the SERP by increasing the overall CTR. The ability to control messaging in ad copy is also considered advantageous to many advertisers. Finally, bidding on brand is incredibly cheap from a cost-per-click perspective -- it's cheap traffic!

![Paid Search ads with competitors bidding on brand terms](/assets/2019/03/sportsbet-serp.jpg)

The main argument made against bidding on brand is cannibalisation. A user searching for a brand term is showing a high degree of intent and is already aware of a brand &mdash; making it likely they would convert via an organic result without the presence of paid advertising.

![Paid Search ad with no competitors bidding on brand term](/assets/2019/03/bupa-serp.jpg)

It's important to understand the degree to which branded ads cannibalise organic search and the overall rate of incrementality. Those who work in SEO or Paid Search usually have pre-conceived notions where these biases are generally fuelled by protection of their own area of specialisation. Organic results are going bad? Blame that on Paid Search cannibalising the activity you look after. Any talk of cannibalisation / incrementality on branded Paid Search activity? Make a reductionist argument that budget is wasted on other areas of advertising where ROI can't be measured.  

There have been multiple peer-reviewed studies over the years on Paid Search incrementality. A [2011 Google study](https://ai.google/research/pubs/pub37161) measured incremental ad clicks from paid search ads and concluded over 89% of ad clicks are incremental. There was a [2012 study](https://ai.google/research/pubs/pub37731) which looked at the relationship between paid search ads and a top ranking organic result. This study found that when an advertiser has the top organic result, the rate of incrementality of ad clicks is 50%. A [2013 Google study](https://ai.google/research/pubs/pub41334) looked at incrementality from a device perspective and found that 88% ad clicks wouldn't have occurred without the presence of a paid ad. A [study released in 2014](http://faculty.haas.berkeley.edu/stadelis/tadelis.pdf) found that for a well known brand such as eBay, showing ads for brand terms would not be useful as incremental clicks to dot translate to incremental sales.  

It's important to set any biases aside and make informed decisions which are validated by data. One of the best ways to do this is through experimentation. Perhaps results aren't definitive one way or another, but at least then it will help understand the rate of incrementality where an advertiser can be satisfied by spending a set amount of budget on brand.  

There are numerous methods for testing ad effectiveness with a randomised geo-experiments considered the grail for inferring causal assessments. Geo experiments meet a large range of measurement needs &mdash; non-overlapping geographic regions which are randomly assigned to a control and treatment (test). Such experiments can then be used to analyse the impact of advertising on any metric that can be collected at the geo level. There have been numerous peer-reviewed studies on geo-experiments which address methodology from design to analysing results and all other considerations. Here are four below;

  * [Measuring Ad Effectiveness Using Geo Experiments](https://ai.google/research/pubs/pub45950)

  * [Inferring causal impact using Bayesian structural time-series models](https://ai.google/research/pubs/pub41854)

  * [Estimating Ad Effectiveness using Geo Experiments in a Time-Based Regression Framework](https://ai.google/research/pubs/pub38355)

  * [Periodic Measurement of Advertising Effectiveness Using Multiple-Test-Period Geo Experiments](https://ai.google/research/pubs/pub38356)

Kay Brodersen at Google also has a great [video published on YouTube](https://www.youtube.com/watch?v=GTgZfCltMm8) where he demonstrates the open-source [CausalImpact](https://google.github.io/CausalImpact/) R package.

In the below example I'm using another R library, once again open sourced by Google, called [GeoexperimentsResearch](ttps://github.com/google/GeoexperimentsResearch). It is based on the study of using geo experiments in a time-based regression (TBR) framework.  

First, I used `googleanalyticsR` for data collection purposes. Make sure you set up your dimension filters and filter clauses. I needed to make sure Paid Search data was google / cpc, but also only from Brand campaigns. In collecting organic search data I also ensured I had a dimension filter on country to ensure data was exclusively from Australia as our business does not advertise internationally.

```r
df1 <- dim_filter("source","EXACT","google", not = FALSE)
df2 <- dim_filter("medium", "EXACT", "cpc", not = FALSE)
df3 <- dim_filter("campaign", "PARTIAL", "brand", not = FALSE)
df4 <- dim_filter("country", "EXACT", "Australia", not = FALSE)
df5 <- dim_filter("source","EXACT","google", not = FALSE)
df6 <- dim_filter("medium", "EXACT", "organic", not = FALSE)
fc1 <- filter_clause_ga4(list(df1,df2,df3,df4), operator = "AND")
fc2 <- filter_clause_ga4(list(df5,df6,df4), operator = "AND")
```
Now it is time to get the data!

```r
sem_data <- google_analytics(my_id,
                                 date_range = c("2018-10-01", "2019-0228"),
                                 metrics = c("transactionRevenue"),
                                 dimensions = c("date", "city"),
                                 dim_filters = fc1,
                                 anti_sample = TRUE)

 organic_data <- google_analytics(my_id,
                              date_range = c("2018-10-01", "2019-02-28"),
                              metrics = c("transactionRevenue"),
                              dimensions = c("date", "city"),
                              dim_filters = fc2,
                              anti_sample = TRUE)
```

From the above, you can see my response metric is `transactionRevenue` &mdash; I want to test the incrementality of sales on Branded Paid Search campaigns in the test geos, which are cities in Australia.

The `GeoexperimentsResearch` package requires the geo field to be named geos so we need to change this column name as per below;

```r
colnames(sem_data)[2]<-"geo"
colnames(organic_data)[2]<-"geo"
```

Next, we need to convert the the data frame into a GeoTimeseries object.

```r
obj.gts <- GeoTimeseries(organic_data, metrics=c("transactionRevenue"))
```

It is important to set up experiment periods &mdash; pretest, start of the test and the end of the experiment.

```r
obj.per <- ExperimentPeriods(c("2018-10-01", "2018-12-01", "2019-02-28"))
```

It's time to assign geos to test and control groups. Geos are stratified by their sizes in terms of the volume of the response variable to ensure a more balance set of groups.

```r
obj.geo.strata <- ExtractGeoStrata(obj.gts, volume="transactionRevenue", n.groups=2)
obj.geo.assignment <- Randomize(obj.geo.strata)
 ```

Next you need to combine all experiment info into one object (geo time series, periods, geo assignment);

```r
obj <- GeoExperimentData(obj.gts,
                          periods=obj.per,
                          geo.assignment=obj.geo.assignment)
```

Now it's time to run a TBR analysis;

```r
obj.tbr <- DoTBRAnalysis(obj, response='transactionRevenue',
                          model='tbr1',
                          pretest.period=0,
                          intervention.period=1,
                          cooldown.period=NULL,
                          control.group=1,
                          treatment.group=2)
```

The below is the output plot.

![Time-Based Regression (TBR) causal effect analysis example - results of Paid Search incrementality](/assets/2019/03/tbr-analysis-768x572.jpg)

From here, you could effectively run this analysis on both your paid and organic data set and measure the level of incrementality / cannibalisation. This will give an objective understanding of the percentage of investment should go to Brand campaigns. Of course, none of this is necessary if there are competitors constantly bidding against your brand terms!
