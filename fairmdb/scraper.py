from concurrent.futures import ProcessPoolExecutor

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


def scrape_dataset(config: dict) -> list[list[str]]:
    """ Function to scrape Top 250 movies dataset from IMDB.com """
    request_result = requests.get(config.target_url)
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
        'total': config.movies,
        'unit': ' movie',
        'unit_scale': True,
        'leave': True
    }

    # Get number of Oscars - Note:
    #   Using multiprocessing instead of multithreading,
    #   as it is about 2-3x faster in this use case. Maybe because of BS4 parsing overhead?
    with ProcessPoolExecutor(max_workers=config.max_workers) as executor:
        oscars = list(tqdm(executor.map(get_oscars, movie_urls[:config.movies]), **kwargs))

    # Prepare temp output & write to CSV
    dataset = list(zip(
        titles[:config.movies],
        ratings[:config.movies],
        user_numbers[:config.movies],
        oscars[:config.movies],
        movie_urls[:config.movies]))
    dataset.insert(0, ['Title', 'Original Rating', 'Reviews', 'Oscars', 'URL'])

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
