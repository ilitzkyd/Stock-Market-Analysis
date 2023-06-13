from wordscore import score_word #Imports score_word function from wordscore.py file

def find_matching_words(rack, data):
    rack = rack.upper() #Converts all letters in the rack input to uppercase 
    matching_words = [] #Stores the words in a list 
    for word in data: 
        word = word.upper() #Converts all letters in the word input to uppercase 
        rack_letters = list(rack) #Converts the stored rack into a list 
        valid_word = True #Determines if the word exists in the twxt file
        for letter in word:
            if letter in rack_letters:
                rack_letters.remove(letter) #Removes letter in rack if it does exist 
            elif '*' in rack_letters or '?' in rack_letters: #Checks for wildcards * or ? 
                rack_letters.remove('*') if '*' in rack_letters else rack_letters.remove('?') 
            else:
                valid_word = False #Invalid word if it is not in the text file 
                break 
        if valid_word: 
            matching_words.append(word) #A valid word does get added to the list of matching words 
        if len(rack) == 2 and all(char in ("*", "?") for char in rack):
            return [] 
    return matching_words


def run_scrabble(word): 
    file_path="C:\\Users\\davidilitzky.REDMOND\\Berkeley\\sowpods.txt"
    try:
        with open(file_path, "r") as infile: #Reads the sowpods text file in local directory 
            raw_input = infile.readlines()
            data = [datum.strip('\n') for datum in raw_input]
    except FileNotFoundError:
        print(f"Error: The sowpods.txt file at '{file_path}' could not be found.")
        print("Please input the correct path")
        return[],0
    if not all(char.isalpha() or char in ("*", "?") for char in word):
        print("Error: The word should contain alphabetical characters or wildcards (*,?)")
        print("Please enter the word again by removing the non-alphabetical letters")
        return[],0

    matching_words = find_matching_words(word, data) #call the matching words function to text file and stores them 
    if not matching_words:
        return [], 0
    
    word_scores = [(word, score_word(word)) for word in matching_words]

    # Sort the list by score in descending order
    word_scores.sort(key=lambda x: x[1], reverse=True)

    grouped_words = []
    for word, score in word_scores:
        count = word_scores.count((word, score))
        if (score, word) not in grouped_words:
            grouped_words.append((score, word))
    print(((grouped_words),len(matching_words))) #Prints the matching words and the count of how many exist

    return grouped_words,len(matching_words)


def main (): 
    word = "?F"
    run_scrabble(word)

if __name__ == "__main__":
    main()
