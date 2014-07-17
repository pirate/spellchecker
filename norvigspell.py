# Nick Sweeting 2014
# python spellchecker based on Peter Norvig's blog post

import re, collections

VERBOSE = True
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
    return set(deletes + transposes + replaces + inserts)

def double_variants(word):
    """get variants for the variants for a word"""
    return set(s for w in variants(word) for s in variants(w))

def suggestions(word, real_words, short_circuit=True):
    if short_circuit:
        return (  {word.lower()} & real_words or
                        variants(word) & real_words or
                        double_variants(word) & real_words or
                        set(["NO SUGGESTION"]))
    else:
        return ({word.lower()} | variants(word) | double_variants(word)) & real_words or set(["NO SUGGESTION"])                       

def best_suggestion(word, word_model, suggestions):
    """choose the best suggestion in a list based on word frequency in a word model"""
    log("Scores:", { s:word_model.get(s) for s in suggestions})
    return max(suggestions, key=word_model.get)

if __name__ == "__main__":
    word_file = open('/usr/share/dict/words', 'r')
    word_model = train(words(word_file.read()))
    real_words = set(word_model)

    log("Total Word Set: ", len(real_words))

    try:
        while True:
            word = str(raw_input(">"))

            possibilities = suggestions(word, real_words, short_circuit=not VERBOSE)

            print(best_suggestion(word, word_model, possibilities))

    except (EOFError, KeyboardInterrupt):
        exit(0)
