from wordscore import score_word  # Imports score_word function from wordscore.py file

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
            elif '*' in rack_letters:
                 rack_letters.remove('*') 
            elif '?' in rack_letters:
                 rack_letters.remove('?')
            else:
                valid_word = False
                break
        if valid_word:
            matching_words.append(word)
    #if len(rack) == 2 and all(char in ("*", "?") for char in rack):
    #    return []
    return matching_words

def run_scrabble(word):
    """
    Runs the Scrabble game for a given word or letter rack.
    The function checks the validity of the input word or rack, performs error checks,
    and returns error messages if necessary. If the input is valid, it proceeds to find
    matching words and calculates their scores.
    Returns:
            - A list of grouped words and their scores, sorted in descending order.
            - The count of matching words.
    """
    rack = word.upper()
    if len(rack) < 2:
        return "Error: Rack needs to have more 2 letters. Please have more than 2 letters"
    
    elif len(rack) > 7:
        return "Error: Rack cannot have more than 7 letters. Please only have 7 letters"
    
    elif rack.count('*')> 1 or  rack.count('?') > 1:
        return "Error: Rack cannot have more than 2 wildcards. Please only have 2 wildcards"
    
    elif any(char.isdigit() for char in rack):
    #if not all(char.isalpha() or char in ("*", "?") or char.isdigit() for char in rack)
        return "The word should contain alphabetical characters or wildcards (*, ?). Please enter the word again by removing the non-alphabetical letters"
    elif not all(char.isalpha() or char in ("*", "?") for char in rack):
        return ("Please enter a valid wildcard")
    else: 
#"C:\Users\davidilitzky.REDMOND\Berkeley\sowpods.txt"
        with open("sowpods.txt", "r") as infile:
            raw_input = infile.readlines()
            data = [datum.strip('\n') for datum in raw_input]

        matching_words = find_matching_words(word, data)
        if not matching_words:
            return [], 0

        word_scores = [(word, score_word(word,rack)) for word in matching_words]
        word_scores.sort(key=lambda x: x[1], reverse=True)

        if len(word_scores) == 1 and word_scores[0][1] == 0:
            return [], len(matching_words)

        grouped_words = [(score, word) for word, score in word_scores]  # Swap the position of word and score
        return grouped_words, len(matching_words)

def main():
    rack = "?a"
    result = run_scrabble(rack)
    #grouped_words = [f"({score}, '{word}')" for score, word in result]  # Swap the position of score and word
    #output = "[\n" + ",\n".join(grouped_words) + "\n]"
    print(result)
if __name__ == "__main__":
    main()