'''Unit test for recalculate_ratings function.'''
import csv
import fairmdb.score_calculator as score_calculator

TEMP_FILE = './tests/test_data/cache.csv'
EXPECTED_OUTPUT = './tests/test_data/test.csv'

# Load cache file for testing
with open(TEMP_FILE, 'r', encoding='utf-8', newline='') as temp_file:
    temp_dataset = list(csv.reader(temp_file))

# Load verified dataset for testing
with open(EXPECTED_OUTPUT, 'r', encoding='utf-8', newline='') as test_file:
    test_dataset = list(csv.reader(test_file))


def test_recalculation():
    """ Unit test for recalculation function. """
    test_output = score_calculator.recalculate_ratings(temp_dataset)
    test_output.sort(key=lambda row: row[1], reverse=True)
    assert test_dataset == test_output
