# NLP_0-project
Group project for MFIN7036. Our goal is to predict firm profitability with text-based competition measures[^1].
We are a "democratic" and collaborative group of five, and I mentioned our names based on our initial work division below :smile:.

Here is the outline of our project:
## Data collection. 
@LeiyuanHuo, jyang130, FanFanShark, xdc1999, gaojiamin1116
- [ ] Based on file __[data-WRDS-list.csv]()__, write a web-scraping algorithm to download all 10-Ks (html format) these companies filed to the SEC within 2010 to 2022 at [Historical EDGAR documents](https://www.sec.gov/cgi-bin/srch-edgar), and rename them __data-10K-COMPNAME-Year.html__.
- [ ] Parse _html_ files to extract __Business__ and __MD&A__ sections.

## Text Processing: feature extraction[^2]
- [ ] Part of Speech Tagging (POS) _(mainly this method)_ to get product name, descriptions. Store these for each company.
- [ ] Named Entity Recognition (NER) _(also mainly this method)_ to get mentioned competitor names. Store these for each company.
- [ ] Product texts: BoW and tf-idf for each company's product(s), and hopefully we have a term-product matrix then.
- [ ] Competitor texts: definitely BoW, as we care about the frequency of being mentioned.
- [ ] :bangbang: We also need to combine __sector__ and __firm size/market power__ into competitor texts and re-count. 

## Text Processing: feature transformation and representation[^2]
- [ ] Term-product matrix: calculate cosine similarity scores for products pairwise; use score threshold to cluster products into similar groups.
- [ ] Term-product matrix: directly apply clustering method (e.g., KMeans clustering) to product vectors, and cluster them.

## Econometric Analysis and Hypothesis Testing[^2]
- [ ] Multivariate regression: DV is profitability (e.g., sales, revenue, Tobin's q), IV is competition measures (one from similar product count, one from mentions as competitors), also include relevant control variables.
- [ ] Cross-section portfolios: our competition measures are cross-sectional (one for each year), so we can create long-short portfolios for both measures, and examine stock return effects.

[^1]: Two papers inspired this project. Citations: Eisdorfer, A., Froot, K., Ozik, G., & Sadka, R. (2021). Competition Links and Stock Returns. The Review of Financial Studies, The Review of financial studies, 2021-12-20. && Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries and Endogenous Product Differentiation. The Journal of Political Economy, 124(5), 1423-1465.
[^2]: Text processing processes are based on MFIN7036 Lecture_Notes and a review paper. Citation: Marty, T., Vanstone, B., & Hahn, T. (2020). News media analytics in finance: A survey. Accounting and Finance (Parkville), 60(2), 1385-1434.
