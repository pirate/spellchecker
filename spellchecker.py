# Nick Sweeting 2014
# python spellchecker

import re, collections
from itertools import product, imap

VERBOSE = True
vowels = set("aeiouy")
alphabet = set('abcdefghijklmnopqrstuvwxyz')

def log(*args):
    if VERBOSE:
        print ''.join([ str(x) for x in args])

def words(text):
    """filter body of text for words"""
    return re.findall('[a-z]+', text.lower()) 

def train(text, model=None):
    """generate word model (dictionary of word:frequency)"""
    if model is None:
        model = collections.defaultdict(lambda: 0)
    for word in text:
        model[word] += 1
    return model

def variants(word):
    """get all possible variants for a word"""
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    log("Deletes: ", len(set(deletes)))
    log("Transposes: ", len(set(transposes)))
    log("Replaces: ", len(set(replaces)))
    log("Inserts: ", len(set(inserts)))
    s = set(deletes + transposes + replaces + inserts)
    log("Total Variations Tried: ", len(s))
    return s

def double_variants(word):
    """get variants for the variants for a word"""
    return set(s for w in variants(word) for s in variants(w))

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

def norvig_suggestions(word, real_words, short_circuit=True):
    if short_circuit:
        return (  {word.lower()} & real_words or
                        variants(word) & real_words or
                        double_variants(word) & real_words or
                        set(["NO SUGGESTION"]))
    else:
        return ({word.lower()} | variants(word) | double_variants(word)) & real_words or set(["NO SUGGESTION"])  

def suggestions(word, real_words, short_circuit=True):
    """get best spelling suggestion for word
    return on first match if short_circuit is true, otherwise collect all possible suggestions
    """

    # Case (upper/lower) errors:
    #  "inSIDE" => "inside"
    if word != word.lower():
        if word.lower() in real_words:
            return {[word.lower()]}
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

def best_suggestion(inputted_word, suggestions, word_model=None):
    """choose the best suggestion in a list based on lowest hamming distance from original word"""

    if word_model is None:
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
    else:
        log("Scores:", { s:word_model.get(s) for s in suggestions})
        return max(suggestions, key=word_model.get)

if __name__ == "__main__":
    word_file = file('/usr/share/dict/words')
    word_model = train(words(word_file.read()))
    real_words = set(word_model)

    log("Total Word Set: ", len(real_words))

    try:
        while True:
            word = str(raw_input(">"))

            possibilities = suggestions(word, real_words, short_circuit=False)
            n_possibilities = norvig_suggestions(word, real_words, short_circuit=True)

            print "Hamm Best: " + best_suggestion(word, possibilities)
            print "Freq Best: " + best_suggestion(word, possibilities, word_model)
            print "Norvig's Hamm Best: " + best_suggestion(word, n_possibilities)
            print "Norvig's Freq Best: " + best_suggestion(word, n_possibilities, word_model)

    except (EOFError, KeyboardInterrupt):
        exit(0)
