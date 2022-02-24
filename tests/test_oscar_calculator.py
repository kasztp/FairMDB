import fairmdb


def test_calculate_oscar_value():
    '''Unit test for calculate_oscar_value function.
    0 oscars → 0 point
    1 to 2 oscars → 0.3 point
    3 to 5 oscars → 0.5 point
    6 to 10 oscars → 1 point
    10+ oscars → 1.5 points

    For example: if a movie is awarded 4 Oscar titles and the original IMDB rating is 7.5,
    the adjusted value will increase to 8 points.'''
    assert fairmdb.oscar_calculator(0) == 0
    assert fairmdb.oscar_calculator(-1) == 0
    assert fairmdb.oscar_calculator(1) == 0.3
    assert fairmdb.oscar_calculator(2) == 0.3
    assert fairmdb.oscar_calculator(3) == 0.5
    assert fairmdb.oscar_calculator(4) == 0.5
    assert fairmdb.oscar_calculator(5) == 0.5
    assert fairmdb.oscar_calculator(6) == 1.0
    assert fairmdb.oscar_calculator(7) == 1.0
    assert fairmdb.oscar_calculator(8) == 1.0
    assert fairmdb.oscar_calculator(9) == 1.0
    assert fairmdb.oscar_calculator(10) == 1.0
    assert fairmdb.oscar_calculator(11) == 1.5
    assert fairmdb.oscar_calculator(23) == 1.5
