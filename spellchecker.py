# Nick Sweeting 2014
# python spellchecker

import re, collections
from itertools import product, imap

VERBOSE = True
vowels = set("aeiouy")
alphabet = set('abcdefghijklmnopqrstuvwxyz')

### IO

def log(*args):
    if VERBOSE:
        print ''.join([ str(x) for x in args])

def words(text):
    """filter body of text for words"""
    return re.findall('[a-z]+', text.lower()) 

def train(text, model=None):
    """generate or update a word model (dictionary of word:frequency)"""
    if model is None:
        model = collections.defaultdict(lambda: 0.0)
    for word in words(text):
        model[word] += 1
    return model

def train_files(file_list, model=None):
    for f in file_list:
        model = train(file(f).read(), model)
    return model

### UTILITY FUNCTIONS

def numberofdupes(string, idx):
    """return the number of times in a row the letter at index idx is duplicated"""
    # "abccdefgh", 2  returns 1
    initial_idx = idx # 2
    last = string[idx] # c
    while idx+1 < len(string) and string[idx+1] == last:
        idx += 1 # 3
    return idx-initial_idx # 3-2 = 1

def hamming_distance(word1, word2):
    if word1 == word2:
        return 0
    dist = sum(imap(str.__ne__, word1[:len(word2)], word2[:len(word1)]))
    dist = max([word2, word1]) if not dist else dist+abs(len(word2)-len(word1))
    return dist

def frequency(word, word_model):
    if word in word_model:
        return word_model.get(word)
    else:
        return 0

### POSSIBILITIES ANALYSIS

def variants(word):
    """get all possible variants for a word"""
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    s = set(deletes + transposes + replaces + inserts)
    return s

def double_variants(word):
    """get variants for the variants for a word"""
    return set(s for w in variants(word) for s in variants(w))

def reductions(word):
    """return flat option list of all possible variations of the word by removing duplicate letters"""
    word = list(word)
    # ['h','i', 'i', 'i'] becomes ['h', ['i', 'ii', 'iii']]
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
    
    # ['h',['i','ii','iii']] becomes 'hi','hii','hiii'
    for p in product(*word):
        yield ''.join(p)

def vowelswaps(word):
    """return flat option list of all possible variations of the word by swapping vowels"""
    word = list(word)
    # ['h','i'] becomes ['h', ['a', 'e', 'i', 'o', 'u', 'y']]
    for idx, l in enumerate(word):
        if type(l) == list:
            # dont mess with the reductions
            pass
        elif l in vowels:
            # if l is a vowel, replace with all possible vowels
            word[idx] = list(vowels)
    
    # ['h',['i','ii','iii']] becomes 'hi','hii','hiii'
    for p in product(*word):
        yield ''.join(p)

def both(word):
    for reduction in reductions(word):
        for variant in vowelswaps(reduction):
            yield variant

### POSSIBILITY CHOOSING

def suggestions(word, real_words, short_circuit=True):
    """get best spelling suggestion for word
    return on first match if short_circuit is true, otherwise collect all possible suggestions
    """
    word = word.lower()
    if short_circuit:
        return (        {word}                      & real_words or   #  caps     "inSIDE" => "inside"
                        set(reductions(word))       & real_words or   #  repeats  "jjoobbb" => "job"
                        set(vowelswaps(word))       & real_words or   #  vowels   "weke" => "wake"
                        set(both(word))             & real_words or   #  both     "CUNsperrICY" => "conspiracy"
                        set(variants(word))         & real_words or   #  other    "nonster" => "monster"
                        set(double_variants(word))  & real_words or   #  other    "nmnster" => "manster"
                        {"NO SUGGESTION"})
    else:
        return (        {word}                      & real_words or                                                          
                        (set(reductions(word))  | set(vowelswaps(word)) | set(both(word)) | set(variants(word)) | set(double_variants(word))) & real_words or
                        {"NO SUGGESTION"})

def best_suggestion(inputted_word, suggestions, word_model=None):
    """choose the best suggestion in a list based on lowest hamming distance from original word, or based on frequency if word_model is provided"""

    suggestions = list(suggestions)

    def comparehamm(one, two):
        score1 = hamming_distance(inputted_word, one)
        score2 = hamming_distance(inputted_word, two)
        # lower is better
        return cmp(score2, score1)

    def comparefreq(one, two):
        score1 = frequency(one, word_model)
        score2 = frequency(two, word_model)
        # higher is better
        return cmp(score1, score2)

    hamming_sorted = sorted(suggestions, comparehamm)[-10:]
    freq_sorted = sorted(hamming_sorted, comparefreq)[-10:]
    return str(freq_sorted[-1])

if __name__ == "__main__":

    word_model = train(file('/usr/share/dict/words').read())
    #word_model = train(file('sherlockholmes.txt').read())

    real_words = set(word_model)

    texts = [   '/Volumes/HD/Coding/Black Hat/Hash Cracking/Dictionaries/words-english.txt',
                '/Volumes/HD/Coding/Black Hat/Hash Cracking/Dictionaries/common.txt',
                '/Volumes/HD/Coding/Black Hat/Hash Cracking/Dictionaries/websters-dictionary.txt',
                '/Volumes/HD/Coding/Black Hat/Hash Cracking/Dictionaries/allwords.txt',
                '/Volumes/HD/Coding/Black Hat/Hash Cracking/Dictionaries/british.txt',]

    texts = [ 'sherlockholmes.txt' ]

    word_model = train_files(texts, word_model)
    
    log("Total Word Set: ", len(word_model))
    log("Model Precision: %s" % (sum(word_model.values())/len(word_model)))

    try:
        while True:
            word = str(raw_input(">"))

            possibilities = suggestions(word, real_words, short_circuit=False)
            print possibilities
            print best_suggestion(word, possibilities, word_model)

    except (EOFError, KeyboardInterrupt):
        exit(0)
