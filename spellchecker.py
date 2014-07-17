# Nick Sweeting 2014
# python spellchecker for disqus

from itertools import product, imap

word_file = open('/usr/share/dict/words', 'r')
word_list = { x.strip() for x in word_file.readlines() }

vowels = set("aeiouy")

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

def suggestions(word, short_circuit=True):
    """get best spelling suggestion for word
    return on first match if short_circuit is true, otherwise collect all possible suggestions
    """

    # Case (upper/lower) errors:
    #  "inSIDE" => "inside"

    if word != word.lower():
        if word.lower() in word_list:
            return set([word.lower()])
        word = word.lower()

    # Repeated letters:
    #  "jjoobbb" => "job"
    reductions = flatten(get_reductions(word))
    print "Reductions: ", len(reductions)
    valid_reductions = word_list & reductions
    if valid_reductions and short_circuit:
        return valid_reductions

    # Incorrect vowels:
    #  "weke" => "wake"
    vowelswaps = flatten(get_vowelswaps(word))
    print "Vowelswaps: ",len(vowelswaps)
    valid_vowelswaps = word_list & vowelswaps
    if valid_vowelswaps and short_circuit:
        return valid_vowelswaps

    # combinations
    # "CUNsperrICY" => "conspiracy"
    both = set()
    for reduction in reductions:
        both = both | flatten(get_vowelswaps(reduction))
    print "Both: ", len(both)
    valid_both = word_list & both
    if valid_both and short_circuit:
        return valid_both

    if short_circuit:
        return set(["NO SUGGESTION"])

    return (valid_vowelswaps | valid_reductions | valid_both) or set(["NO SUGGESTION"])

def best_suggestion(suggestions, inputted_word):
    """choose the best suggestion in a list based on lowest hamming distance from original word"""

    scores = {}

    # give each suggestion a score based on hamming distance
    for suggestion in suggestions:
        score = sum(imap(str.__ne__, suggestion, inputted_word[:len(suggestion)]))
        if score in scores:
            scores[score] += [suggestion]
        else:
            scores[score] = [suggestion]

    # pick the list of suggestions with the lowest hamming distance
    # return the one that comes first in the alphabet (solves weke-> wake vs wyke)
    print "Scores:", scores
    return min(scores[min(scores.keys())])

if __name__ == "__main__":
    try:
        while True:
            word = str(raw_input(">"))
            possibilities = suggestions(word, short_circuit=False)
            print(best_suggestion(possibilities, word))
    except EOFError:
        exit(0)
