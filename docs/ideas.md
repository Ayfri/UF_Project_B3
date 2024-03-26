# Ideas

Creating a dashboard for storytelling about data analysis with the GDELT Project offers a unique opportunity to explore global events, media coverage, and societal trends. Here are several proposition ideas for your final project, each with associated Google BigQuery queries to help you get started. Remember, each project proposition can be tailored further to meet specific interests or academic requirements.

### Proposition 1: Global Conflict and Peace Events Analysis

Analyze the trends and patterns of global conflicts and peace efforts over time. This dashboard could highlight hotspots around the world where conflicts are intensifying or resolving.

**BigQuery Queries:**

1. **Conflict Events Over Time:**
   ```sql
   SELECT SqlDate, COUNT(*) as TotalEvents
   FROM `gdelt-bq.gdeltv2.events`
   WHERE EventRootCode='19'  -- 19 corresponds to Fight; use GDELT's event codes
   GROUP BY SqlDate
   ORDER BY SqlDate;
   ```

2. **Top 5 Countries with Most Conflict Events in the Last Year:**
   ```sql
   SELECT Actor1CountryCode, COUNT(*) as NumberOfEvents
   FROM `gdelt-bq.gdeltv2.events`
   WHERE EventRootCode='19' AND Year=YEAR(CURRENT_DATE())
   GROUP BY Actor1CountryCode
   ORDER BY NumberOfEvents DESC
   LIMIT 5;
   ```

### Proposition 2: Analysis of Global Response to Climate Change

This dashboard would analyze the coverage and events related to climate change, identifying key actors, countries involved, and the nature of the events (protests, agreements, policy changes).

**BigQuery Queries:**

1. **Climate Change Events by Type:**
   ```sql
   SELECT EventCode, COUNT(*) as EventCount
   FROM `gdelt-bq.gdeltv2.events`
   WHERE Themes LIKE '%CLIMATE_CHANGE%'
   GROUP BY EventCode
   ORDER BY EventCount DESC;
   ```

2. **Countries Leading in Climate Change Discussions:**
   ```sql
   SELECT Actor1CountryCode, COUNT(*) as Mentions
   FROM `gdelt-bq.gdeltv2.gkg`
   WHERE V2Themes LIKE '%CLIMATE_CHANGE%'
   GROUP BY Actor1CountryCode
   ORDER BY Mentions DESC
   LIMIT 10;
   ```

### Proposition 3: Economic Development Stories

Focus on the analysis of economic development stories, tracking how different regions of the world are evolving economically through events related to trade, economic aid, investments, and economic policy changes.

**BigQuery Queries:**

1. **Economic Events Analysis:**
   ```sql
   SELECT EventCode, COUNT(*) as TotalEvents
   FROM `gdelt-bq.gdeltv2.events`
   WHERE EventCode BETWEEN '040' AND '080' -- Economic event codes range
   GROUP BY EventCode
   ORDER BY TotalEvents DESC;
   ```

2. **Trade Agreements and Economic Aid:**
   ```sql
   SELECT Actor1CountryCode, Actor2CountryCode, COUNT(*) as EventsCount
   FROM `gdelt-bq.gdeltv2.events`
   WHERE EventCode='057' OR EventCode='060' -- Formal agreement signed; Economic cooperation
   GROUP BY Actor1CountryCode, Actor2CountryCode
   ORDER BY EventsCount DESC
   LIMIT 10;
   ```

### Proposition 4: Public Health Emergencies and Response

Analyze the global response to public health emergencies, such as the COVID-19 pandemic, tracking government actions, public sentiment, and media coverage over time.

**BigQuery Queries:**

1. **Public Health Events Timeline:**
   ```sql
   SELECT SqlDate, COUNT(*) as NumberOfEvents
   FROM `gdelt-bq.gdeltv2.events`
   WHERE Themes LIKE '%HEALTH_PANDEMIC%' AND Year >= 2019
   GROUP BY SqlDate
   ORDER BY SqlDate;
   ```

2. **Government Response to Health Emergencies:**
   ```sql
   SELECT Actor1CountryCode, AVG(Tone) as AverageTone
   FROM `gdelt-bq.gdeltv2.gkg`
   WHERE V2Themes LIKE '%HEALTH_PANDEMIC%' AND Year >= 2019
   GROUP BY Actor1CountryCode
   ORDER BY AverageTone;
   ```

### Tools and Tips for Building Your Dashboard

- **Visualization Tools:** Consider using tools like Google Data Studio, Tableau, or Power BI for creating your dashboard. These tools often have direct connectors to BigQuery, simplifying the data visualization process.
- **BigQuery Optimization:** To manage costs and improve query performance, consider using partitioned tables and querying only the necessary columns. Also, use the preview feature to check your queries before running them.
- **Dashboard Design:** Plan your dashboard layout carefully. Start with key metrics or KPIs and use charts, maps, and timelines to
