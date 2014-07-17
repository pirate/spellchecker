# Nick Sweeting 2014
# python spellchecker

from itertools import product, imap
import re

VERBOSE = True
vowels = set("aeiouy")

def log(*args):
    if VERBOSE:
        print ''.join([ str(x) for x in args])

def words(text):
    """filter body of text for words"""
    return re.findall('[a-z]+', text.lower()) 

def numberofdupes(string, idx):
    """return the number of times in a row the letter at index idx is duplicated"""
    # "abccdefgh", 2  returns 1
    initial_idx = idx # 2
    last = string[idx] # c
    while idx+1 < len(string) and string[idx+1] == last:
        idx += 1 # 3
    return idx-initial_idx # 3-2 = 1

def get_reductions(word):
    """return flat option list of all possible variations of the word by removing duplicate letters"""
    word = list(word)
    for idx, l in enumerate(word):
        n = numberofdupes(word, idx)
        # if letter appears more than once in a row
        if n:
            # generate a flat list of options ('hhh' becomes ['h','hh','hhh'])
            flat_dupes = [ l*(r+1) for r in xrange(n+1) ][:3] # only take up to 3, there are no 4 letter repetitions in english
            # remove duplicate letters in original word
            for _ in range(n):
                word.pop(idx+1)
            # replace original letter with flat list
            word[idx] = flat_dupes
    # ['h','i', 'i', 'i'] becomes ['h', ['i', 'ii', 'iii']]
    return word

def get_vowelswaps(word):
    """return flat option list of all possible variations of the word by swapping vowels"""
    word = list(word)
    for idx, l in enumerate(word):
        if type(l) == list:
            # dont mess with the reductions
            pass
        elif l in vowels:
            # if l is a vowel, replace with all possible vowels
            word[idx] = list(vowels)
        
    # ['h','i'] becomes ['h', ['a', 'e', 'i', 'o', 'u', 'y']]
    return word

def flatten(options):
    """convert compact nested options list into full list"""
    # ['h',['i','ii','iii']] becomes 'hi','hii','hiii'
    a = set()
    for p in product(*options):
        a.add(''.join(p))
    return a

def suggestions(word, real_words, short_circuit=True):
    """get best spelling suggestion for word
    return on first match if short_circuit is true, otherwise collect all possible suggestions
    """

    # Case (upper/lower) errors:
    #  "inSIDE" => "inside"
    if word != word.lower():
        if word.lower() in real_words:
            return set([word.lower()])
        word = word.lower()

    # Repeated letters:
    #  "jjoobbb" => "job"
    reductions = flatten(get_reductions(word))
    log("Reductions: ", len(reductions))
    valid_reductions = real_words & reductions
    if valid_reductions and short_circuit:
        return valid_reductions

    # Incorrect vowels:
    #  "weke" => "wake"
    vowelswaps = flatten(get_vowelswaps(word))
    log("Vowelswaps: ", len(vowelswaps))
    valid_vowelswaps = real_words & vowelswaps
    if valid_vowelswaps and short_circuit:
        return valid_vowelswaps

    # combinations
    # "CUNsperrICY" => "conspiracy"
    both = set()
    for reduction in reductions:
        both = both | flatten(get_vowelswaps(reduction))
    log("Both: ", len(both))
    valid_both = real_words & both
    if valid_both and short_circuit:
        return valid_both

    log("Total Variations Tried: ", len(both)+len(vowelswaps)+len(reductions))

    if short_circuit:
        return set(["NO SUGGESTION"])

    return (valid_vowelswaps | valid_reductions | valid_both) or set(["NO SUGGESTION"])

def best_suggestion(inputted_word, suggestions):
    """choose the best suggestion in a list based on lowest hamming distance from original word"""

    scores = {}
    # give each suggestion a score based on hamming distance
    for suggestion in suggestions:
        score = sum(imap(str.__ne__, suggestion, inputted_word[:len(suggestion)]))
        if score in scores:
            scores[score] += [suggestion]
        else:
            scores[score] = [suggestion]

    log("Scores: ", scores)

    # pick the list of suggestions with the lowest hamming distance
    # return the one that comes first in the alphabet (solves weke-> wake vs wyke)
    return min(scores[min(scores.keys())])

if __name__ == "__main__":
    word_file = open('/usr/share/dict/words', 'r')
    real_words = set(words(word_file.read()))

    log("Total Word Set: ", len(real_words))

    try:
        while True:
            word = str(raw_input(">"))

            possibilities = suggestions(word, real_words, short_circuit=not VERBOSE)

            print(best_suggestion(word, possibilities))

    except (EOFError, KeyboardInterrupt):
        exit(0)
