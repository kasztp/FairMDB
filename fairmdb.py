""" Module to scrape & recalculate IMDB Top250 movie ratings
    based on number of reviews & Oscars won. """
import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import os
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Scrape IMDB Top 250 movies & recalculate ratings.')
parser.add_argument('-o', '--output', type=str, default='./Fair_IMDB_Ratings_top20.csv',
                    help='Output file name.')
parser.add_argument('-c', '--cache', type=str, default='./cache.csv',
                    help='Cache file name.')
parser.add_argument('-w', '--max-workers', type=int, default=4,
                    help='Maximum number of workers to use.')
parser.add_argument('-m', '--movies', type=int, default=20,
                    help='Number of movies to scrape.')
args = parser.parse_args()


TARGET_URL = 'https://www.imdb.com/chart/top/'
OUTPUT_FILE = args.output
TEMP_FILE = args.cache
MAX_WORKERS = args.max_workers
MOVIES_TO_SCRAPE = args.movies


def scrape_dataset(top_chart_url: str) -> list[list[str]]:
    """ Function to scrape Top 250 movies dataset from IMDB.com """
    request_result = requests.get(top_chart_url)
    soup = BeautifulSoup(request_result.text, 'lxml')

    # Parse movie titles
    elements = soup(class_='titleColumn')
    titles = [element.get_text(strip=True, separator='|').split('|')[1]
              for element in elements]

    # Parse ratings
    elements = soup(class_='ratingColumn imdbRating')
    ratings = [element.get_text(strip=True, separator='|')
               for element in elements]

    # Parse number of ratings
    user_numbers = [str(element.strong).split('"')[1].split(' ')[3].replace(',', '')
                    for element in elements]

    # Parse movie urls
    elements = soup.select("tbody a")
    movie_urls = ['https://www.imdb.com' + element['href']
                  for index, element in enumerate(elements) if index % 2 != 0]

    # Set up tqdm progress bar
    kwargs = {
        'total': MOVIES_TO_SCRAPE,
        'unit': ' movie',
        'unit_scale': True,
        'leave': True
    }

    # Get number of Oscars - Note:
    #   Using multiprocessing instead of multithreading,
    #   as it is about 2-3x faster in this use case. Maybe because of BS4 parsing overhead?
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        oscars = list(tqdm(executor.map(get_oscars, movie_urls[0:MOVIES_TO_SCRAPE]), **kwargs))

    # Prepare temp output & write to CSV
    dataset = [list(row) for row in zip(
        titles[0:MOVIES_TO_SCRAPE],
        ratings[0:MOVIES_TO_SCRAPE],
        user_numbers[0:MOVIES_TO_SCRAPE],
        oscars[0:MOVIES_TO_SCRAPE],
        movie_urls[0:MOVIES_TO_SCRAPE])]
    dataset.insert(0, ['Title', 'Original Rating', 'Reviews', 'Oscars', 'URL'])

    with open(TEMP_FILE, 'w', encoding='utf-8', newline='') as temp:
        write_temp = csv.writer(temp)
        write_temp.writerows(dataset)

    return dataset


def get_oscars(movie_url: str) -> int:
    """ Function to get number of Oscars won based on an imdb movie url. """
    result = requests.get(movie_url)
    content = result.text
    soup = BeautifulSoup(content, 'lxml')
    element = soup.find_all(class_='ipc-metadata-list-item__label')

    try:
        extracted_text = element[6].get_text(strip=True).split()
        if extracted_text[0] == 'Won' and 'Oscar' in extracted_text[-1]:
            return int(extracted_text[1])
    except IndexError:
        print(element)
    return 0


def oscar_calculator(wins: int) -> float:
    """ Helper function to modify rating based on the number of Oscars won. """
    if 1 <= wins <= 2:
        return 0.3
    if 3 <= wins <= 5:
        return 0.5
    if 6 <= wins <= 10:
        return 1.0
    if wins > 10:
        return 1.5
    return 0


def recalculate_ratings(dataset: list[list[str]]) -> list[list[str]]:
    """ Function to recalculate ratings based on number of ratings & Oscars won. """
 
    dataset[0].insert(1, 'Recalculated Rating')
    ratings = [float(row[1]) for row in dataset[1:]]
    reviews = [int(row[2]) for row in dataset[1:]]
    oscars = [int(row[3]) for row in dataset[1:]]
    print(f'Ratings rows: {len(ratings)}, '
          f'Reviews rows: {len(reviews)}, '
          f'Oscars rows: {len(oscars)}.')
    max_reviews = max(reviews)

    for row, movie in enumerate(dataset[1:]):
        rating = ratings[row]
        if movie[2] != max_reviews:
            rating -= (max_reviews - reviews[row])//100000*0.1
        if movie[3] != 0:
            rating += oscar_calculator(oscars[row])
        dataset[row+1].insert(1, str(round(rating, 1)))
    return dataset


if __name__ == '__main__':
    if not os.path.isfile(TEMP_FILE):
        print('Getting data from IMDB...')
        temp_dataset = scrape_dataset(TARGET_URL)
    else:
        print(f'Loading dataset from {TEMP_FILE}')
        with open(TEMP_FILE, 'r', encoding='utf-8', newline='') as temp_file:
            temp_dataset = list(csv.reader(temp_file))

    print('Recalculating Ratings...')
    updated_dataset = recalculate_ratings(temp_dataset)
    updated_dataset.sort(key=lambda row: row[1], reverse=True)

    print(f'Writing results to {OUTPUT_FILE}')
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as output_file:
        write = csv.writer(output_file)
        write.writerows(updated_dataset)
