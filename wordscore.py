
def score_word(word, rack):
    """
    Calculates the score of a given word based on letter scores.

    The function calculates the score of a word by summing the individual scores
    of its letters. The scores for each letter are defined in the 'scores' dictionary.

    Args:
        word (str): The word for which to calculate the score.

    Returns:
        int: The score of the word.
    """
    scores = {
    "a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2,
    "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3,
    "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1,
    "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4,
    "x": 8, "z": 10
    }

    score = 0 
    rack = list(rack.lower())
    for char in word.lower(): 
        if char in rack: 
            score += scores[char]   
            rack.remove(char)
    return score 