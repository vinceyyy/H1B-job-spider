# H1B-job-spider

A scraper for LinkedIn/indeed job postings related to H1B/OPT/CPT.

Do you feel exhausted when looking for jobs that support OPT/H1B with OPT/H1B as search keywords, but all the search results are actually saying "we are not consider... H1B/OPT/CPT"?

Yeah it sucks. If there is a filter for it, 99% job posters will ignore it just like most of the filters on LinkedIn; if there is no filter for it, it will screw up the text searching.

Big tech companies don't take the responsibilities for this, we are on our own.

## Process

1. Scraping job descriptions with visa-related keywords in it.
2. Grouping them by the setense containing visa-related keywords, extract patterns.
3. Identifying meaning of the setense.
