# Simple Python Spell-Checker

## Quickstart

```bash
git clone https://github.com/pirate/spellchecker
cd spellchecker/
python spellchecker.py

# type interactively to get suggestions
Total Word Set: 285750
Model Precision: 1.62249168854
>manster
[('monster', 2), ('minster', 2)]

# or try some preset mispelled words
python misspeller.py | python spellchecker.py 
```
You can edit `spellchecker.py` and add more files to the training list to increase the word-frequency model precision.

## Background


Peter Norvig wrote an amazing article titled [How to Write a Spelling Corrector](http://norvig.com/spell-correct.html) detailing a basic approach to this deceivingly simple problem.
I had to write a spellchecker as an interview question for [Disqus](https://disqus.com/), and this repo details my efforts.

The core code that I borrow from [Darius Bacon](https://github.com/darius) & Norvig is this beautiful block:
```python
def variants(word):
    """get all possible variants for a word"""
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)
```

Of course that wasn't my only code, I added a lot more on top of Norvig's implementation.

My additions are:
  - short-circuiting options for faster checking
  - hamming distance and word-frequency model based chooser for suggestions
  - double word variants for catching more complex multi-typos
  - vowel-swapping detection
  - a reductions function to efficiently store word variants like `monster: ['m',['o', 'a'], 'n', 's', 't', 'e', 'r']`

## Faster Algorithm

A faster spellchecking algorithm exists, see: https://github.com/wolfgarbe/SymSpell
