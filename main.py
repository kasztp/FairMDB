""" Module to scrape & recalculate IMDB Top250 movie ratings
    based on number of reviews & Oscars won. """

import argparse
import os

from fairmdb.file_utils import read_csv, write_csv
from fairmdb.scraper import scrape_dataset
from fairmdb.score_calculator import recalculate_ratings


def parse_args():
    parser = argparse.ArgumentParser(description='Scrape IMDB Top 250 movies & recalculate ratings.')
    parser.add_argument('-o', '--output', type=str, default='./Fair_IMDB_Ratings_top20.csv',
                        help='Output file name.')
    parser.add_argument('-i', '--input', type=str,
                        help='Own imput file name.')
    parser.add_argument('-t', '--temp', type=str,
                        help='Temp file name for saving scraped raw data.')
    parser.add_argument('-w', '--max-workers', type=int, default=4,
                        help='Maximum number of workers to use.')
    parser.add_argument('-m', '--movies', type=int, default=20,
                        help='Number of movies to scrape.')
    parser.add_argument('-r', '--recalculate', action='store_true',
                        help='Recalculate ratings.')
    parser.add_argument('-s', '--scrape', action='store_true',
                        help='Scrape movies from IMDB.')
    config = parser.parse_args()
    config.__setattr__('target_url', 'https://www.imdb.com/chart/top/')
    return config


def scrape(config):
    print('Getting data from IMDB...')
    return scrape_dataset(config)


def recalculate(dataset):
    print('Recalculating ratings...')
    updated_dataset = recalculate_ratings(dataset)
    return sorted(updated_dataset, key=lambda row: row[1], reverse=True)


if __name__ == '__main__':
    config = parse_args()

    if config.scrape and not config.input:
        dataset = scrape(config)
        if config.temp is not None:
            print(f'Saving scraped data to {config.temp} ...')
            write_csv(config.temp, dataset)
    elif config.input is not None:
        dataset = read_csv(config.input)
    else:
        print('No scraping argument or input file specified. Exiting...')
        exit()
    
    if config.recalculate:
        updated_dataset = recalculate(dataset)
        print(f'Writing results to {config.output} ...')
        write_csv(config.output, updated_dataset)
