import csv


def read_csv(file_path: str) -> list[list[str]]:
    """ Reads a csv file and returns a list of lists. """
    with open(file_path, 'r', encoding='utf-8', newline='') as csv_file:
        return list(csv.reader(csv_file))


def write_csv(file_path: str, dataset: list[list[str]]):
    """ Writes a list of lists to a csv file. """
    with open(file_path, 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(dataset)
