from wordscore import score_word #Imports score_word function from wordscore.py file

def find_matching_words(rack, data):
    rack = rack.upper()
    matching_words = []
    for word in data:
        word = word.upper()
        rack_letters = list(rack)
        valid_word = True
        for letter in word:
            if letter in rack_letters:
                rack_letters.remove(letter)
            elif '*' in rack_letters or '?' in rack_letters:
                rack_letters.remove('*') if '*' in rack_letters else rack_letters.remove('?')
            else:
                valid_word = False
                break
        if valid_word:
            matching_words.append(word)
    if len(rack) == 2 and all(char in ("*", "?") for char in rack):
        return []
    return matching_words

def run_scrabble(word=None):
    if word is None:
        return "Error: No input has been provided. Please enter a rack", ""

    rack = word.upper()

    if not all(char.isalpha() or char in ("*", "?") or char.isdigit() for char in word):
        return "Error: The word should contain alphabetical characters or wildcards (*, ?). Please enter the word again by removing the non-alphabetical letters", ""

    if not all(char.isalpha() or char in ("*", "?") or char.isdigit() for char in rack):
        return "Error: The letter rack should contain alphabetical characters or wildcards (*, ?). Please enter the rack again by removing the non-alphabetical letters", ""

    if len(word) == 1:
        return "Error: The rack should be more than a letter. Please input more than 1 letter", ""

    if rack.count('*') + rack.count('?') > 2:
        return "Error: Rack cannot have more than 2 wildcards. Please only have 2 wildcards", ""

    if len(rack) > 7:
        return "Error: Rack cannot have more than 7 letters. Please only have 7 letters", ""

    with open("C:\\Users\davidilitzky.REDMOND\\Berkeley\\sowpods.txt", "r") as infile:
        raw_input = infile.readlines()
        data = [datum.strip('\n') for datum in raw_input]

    matching_words = find_matching_words(word, data)
    if not matching_words:
        return "", 0

    word_scores = [(word, score_word(word)) for word in matching_words]
    word_scores.sort(key=lambda x: x[1], reverse=True)

    grouped_words = []
    for word, score in word_scores:
        count = word_scores.count((word, score))
        if (score, word) not in grouped_words:
            grouped_words.append((score, word))

    return grouped_words, len(matching_words)

def main():
    word = "*?"
    result = run_scrabble(word)
    print(result)

if __name__ == "__main__":
    main()