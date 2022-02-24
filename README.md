# "Fair" IMDB Ranking  [![Pylint](https://github.com/kasztp/FairMDB/actions/workflows/pylint.yml/badge.svg)](https://github.com/kasztp/FairMDB/actions/workflows/pylint.yml)

Web Scraping practice project with BeautifulSoup, Requests, CSV.
It scrapes the Top 250 Movies from IMDB, then recalculates their ranking based on number of reviews & Oscars won.

Usage: Just run main.py :)

Optional arguments:
  -h, --help            Show this help message and exit.
  -o OUTPUT, --output OUTPUT
                        Output file name. Default: ./Fair_IMDB_Ratings_top20.csv
  -c CACHE, --cache CACHE
                        Cache file name. Default: ./cache.csv
                        (If you have a previously scraped csv, or want to do recalculation for movies other than the Top250 list.)
  -w MAX_WORKERS, --max-workers MAX_WORKERS
                        Maximum number of workers to use for parallel scraping.
                        (Default is 4, 8-32 works best for performance, above 32 you'll get temporarily blocked by IMDB.)
  -m MOVIES, --movies MOVIES
                        Number of movies to scrape. (Default is 20, maximum is 250.)

Todo:
1. Add some UI / Data Visualization.
3. Investigate more why multiprocessing is more performant in this case than the more obvious multithreading.

Done:
2. Make it more general (e.g. user definable list of movies, or use bigger dataset, etc.)