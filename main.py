""" Module to scrape & recalculate IMDB Top250 movie ratings based on number of reviews & Oscars won. """
from concurrent.futures import ProcessPoolExecutor
import csv
import os
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm

TARGET_URL = 'https://www.imdb.com/chart/top/'
OUTPUT_FILE = './Fair_IMDB_Ratings.csv'
TEMP_FILE = './temp.csv'
MAX_WORKERS = 32


def scrape_dataset(top_chart_url: str) -> list[list[str]]:
    """ Function to scrape Top 250 movies dataset from IMDB.com """
    result = requests.get(top_chart_url)
    content = result.text
    soup = BeautifulSoup(content, 'lxml')

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
        'total': len(movie_urls),
        'unit': ' movie',
        'unit_scale': True,
        'leave': True
    }

    # Get number of Oscars - Note:
    #   Using multiprocessing instead of multithreading,
    #   as it is about 2-3x faster in this use case. Maybe because of BS4 parsing overhead?
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        oscars = list(tqdm(executor.map(get_oscars, movie_urls), **kwargs))

    # Prepare temp output & write to CSV
    data = [list(row) for row in zip(titles, ratings, user_numbers, oscars, movie_urls)]
    header = [['Title', 'Ratings', 'Reviews', 'Oscars', 'URL']]
    dataset = header + data

    with open(TEMP_FILE, 'w', encoding='utf-8', newline='') as f:
        write_temp = csv.writer(f)
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


def recalculate_ratings(dataset: list[list[str]]) -> list[list[str]]:
    """ Function to recalculate ratings based on number of ratings & Oscars won. """
    def calculate_oscar_value(wins: int) -> float:
        """ Helper function to modify rating based on the number of Oscars won. """
        if 1 <= wins <= 2:
            return 0.3
        elif 3 <= wins <= 5:
            return 0.5
        elif 5 <= wins <= 10:
            return 1.0
        elif wins > 10:
            return 1.5
        return 0

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
            rating += calculate_oscar_value(oscars[row])
        dataset[row+1][1] = str(round(rating, 1))
    return dataset


if __name__ == '__main__':
    if not os.path.isfile(TEMP_FILE):
        print('Getting data from IMDB...')
        temp_dataset = scrape_dataset(TARGET_URL)
    else:
        print(f'Loading dataset from {TEMP_FILE}')
        with open(TEMP_FILE, 'r', encoding='utf-8', newline='') as f:
            temp_dataset = list(csv.reader(f))

    print('Recalculating Ratings...')
    updated_dataset = recalculate_ratings(temp_dataset)
    updated_dataset.sort(key=lambda row: row[1], reverse=True)

    print(f'Writing results to {OUTPUT_FILE}')
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as output_file:
        write = csv.writer(output_file)
        write.writerows(updated_dataset)
