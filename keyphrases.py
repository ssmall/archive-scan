#!/usr/local/bin/python2.7

# based on https://gist.github.com/alexbowe/879414
import argparse

import nltk
from nltk.corpus import stopwords

# Used when tokenizing words
sentence_re = r'''(?x)      # set flag to allow verbose regexps
      ([A-Z])(\.[A-Z])+\.?  # abbreviations, e.g. U.S.A.
    | \w+(-\w+)*            # words with optional internal hyphens
    | \$?\d+(\.\d+)?%?      # currency and percentages, e.g. $12.40, 82%
    | \.\.\.                # ellipsis
    | [][.,;"'?():-_`]      # these are separate tokens
'''

grammar = r"""
    NBAR:
        {<NN.*|JJ>*<NN.*>}  # Nouns and Adjectives, terminated with Nouns

    NP:
        {<NBAR>}
        {<NBAR><IN><NBAR>}  # Above, connected with in/of/etc...
"""

lemmatizer = nltk.WordNetLemmatizer()
stemmer = nltk.stem.porter.PorterStemmer()
chunker = nltk.RegexpParser(grammar)
stopwords = stopwords.words('english')


def leaves(tree):
    """Finds NP (nounphrase) leaf nodes of a chunk tree."""
    for subtree in tree.subtrees(filter=lambda t: t.label() == 'NP'):
        yield subtree.leaves()


def normalise(word):
    """Normalises words to lowercase and stems and lemmatizes it."""
    word = word.lower()
    word = stemmer.stem_word(word)
    word = lemmatizer.lemmatize(word)
    return word


def acceptable_word(word):
    """Checks conditions for acceptable word: length, stopword."""
    accepted = bool(2 <= len(word) <= 40
                    and word.lower() not in stopwords)
    return accepted


def get_terms(tree):
    for leaf in leaves(tree):
        term = [(w, normalise(w)) for w, t in leaf if acceptable_word(w)]
        yield term


def dedupe_and_add(word_or_phrase, collection):
    if word_or_phrase.lower() not in [w.lower() for w in collection]:
        collection.append(word_or_phrase)


def print_keywords(postoks):
    tree = chunker.parse(postoks)
    terms = get_terms(tree)
    term_freq = dict()
    term_to_words = dict()
    for term in terms:
        if len(term) > 0:
            words, stems = zip(*term)
            full_key = " ".join(stems)
            full_term = " ".join(words)
            for word, key in term + [(full_term, full_key)]:
                if key in term_freq:
                    term_freq[key] += 1
                    dedupe_and_add(word, term_to_words[key])
                else:
                    term_freq[key] = 1
                    term_to_words[key] = [word]
    for term_key, freq in sorted(term_freq.iteritems(), key=lambda entry: entry[1], reverse=True):
        print ", ".join(term_to_words[term_key]), freq


def extract_named_entities(postoks):
    named_entities = nltk.chunk.ne_chunk(postoks)
    subtrees = [subtree for subtree in named_entities.subtrees()]
    return set([" ".join([word for word, pos in subtree.leaves()]).lower() for subtree in subtrees[1:]])


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Extract keywords and key phrases from text")
    argparser.add_argument('textfile', type=file)
    args = argparser.parse_args()
    with args.textfile:
        text = "\n".join(map(lambda string: string.decode('utf-8'), args.textfile.readlines()))
        re_toks = nltk.regexp_tokenize(text, sentence_re)
        word_toks = nltk.word_tokenize(text)
    re_postoks = nltk.pos_tag(re_toks)
    word_postoks = nltk.pos_tag(word_toks)

    entities = extract_named_entities(re_postoks).union(extract_named_entities(word_postoks))

    for entity in entities:
        print entity
