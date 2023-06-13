scores = {
    "a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2,
    "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3,
    "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1,
    "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4,
    "x": 8, "z": 10
}

def score_word(word, wildcard_count=0, memo={}):
    """
    Calculates the score of a given word based on letter scores.

    The function calculates the score of a word by summing the individual scores
    of its letters. The scores for each letter are defined in the 'scores' dictionary.

    Args:
        word (str): The word for which to calculate the score.
        wildcard_count (int): The number of wildcard characters encountered.
        memo (dict): A dictionary to store previously computed scores.

    Returns:
        int: The score of the word.
    """
    if wildcard_count == 2:
        return 0

    if word in memo:
        return memo[word]

    total_score = 0
    max_score = 0

    for i, letter in enumerate(word):
        if letter == '*' or letter == '?':
            if wildcard_count == 0:
                score_with_wildcard = score_word(word[:i] + word[i + 1:], wildcard_count + 1, memo)
                max_score = max(max_score, score_with_wildcard)
        else:
            total_score += scores.get(letter.lower(), 0)

    if wildcard_count == 1:
        for letter in scores.keys():
            word_with_wildcard = word.replace('*', letter).replace('?', letter)
            score_with_wildcard = score_word(word_with_wildcard, wildcard_count + 1, memo)
            max_score = max(max_score, score_with_wildcard)

    total_score = max(total_score, max_score)
    memo[word] = total_score

    return total_score