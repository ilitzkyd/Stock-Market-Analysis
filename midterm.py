
def count_retweets_by_username(tweet_list):
    """ (list of tweets) -> dict of {username: int}
    Returns a dictionary in which each key is a username that was 
    retweeted in tweet_list and each value is the total number of times this 
    username was retweeted.
    """
    # write code here and update return statement with your dictionary
    frequency_username = {}
    sum_shares = [phrase.split()[phrase.split().index('RT') + 1][1:] for phrase in tweet_list if 'RT' in phrase]
    frequency_username = {account: sum_shares.count(account) for account in sum_shares}
    return frequency_username
    return {}


import numpy as np
def display(deposits, top, bottom, left, right):
    """display a subgrid of the land, with rows starting at top and up to 
    but not including bottom, and columns starting at left and up to but
    not including right."""
    square = np.full((bottom - top, right - left), '-')
    for i,j, _ in deposits: 
        if top <= i < bottom and left <= j < right:
            square[i - top,j - left] = 'X'
    return '\n'.join(map(' '.join, square))




def tons_inside(deposits, top, bottom, left, right):
    """Returns the total number of tons of deposits for which the row is at least top,
    but strictly less than bottom, and the column is at least left, but strictly
    less than right."""
    return sum(tons for i, j, tons in deposits if top <= i < bottom and left <= j < right)


def birthday_count(dates_list):
    """Total number of birthday pairs in a list by counting each pair only once"""
    count = 0 
    for people in range(len(dates_list)):
        person_a = dates_list[people]
        for j in range(people + 1, len(dates_list)):
            person_b = dates_list[j]

            # Check both month and day
            if person_a[0] == person_b[0] and person_a[1] == person_b[1]:
                count += 1
    return count
