import re, collections

def words(text):
    """filter body of text for all words"""
    return re.findall('[a-z]+', text.lower()) 

def train(features):
    """generate dicitonary of words:likeleyhood"""
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

NWORDS = train(words(file('/usr/share/dict/words').read()))

alphabet = 'abcdefghijklmnopqrstuvwxyz'

def suggestions(word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def known_suggestions(word):
    return set(e2 for e1 in suggestions(word) for e2 in suggestions(e1) if e2 in NWORDS)

def known(words):
    return set(w for w in words if w in NWORDS)

def correct(word):
    candidates = known([word]) or known(suggestions(word)) or known_suggestions(word) or ["NO SUGGESTION"]
    print candidates
    return max(candidates, key=NWORDS.get)

while True:
    print(correct(raw_input(">")))
