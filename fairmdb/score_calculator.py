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