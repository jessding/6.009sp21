# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self, key_type):
        self.value = None
        # directly storing key_type as a type object
        self.key_type = key_type
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        if type(key) != self.key_type:
            raise TypeError('given key is not of the appropriate type')
        # base case: if key is at last step in tree
        if len(key) == 0:
            self.value = value
        # recursive step
        elif key[:1] in self.children:
            self.children[key[:1]].__setitem__(key[1:], value)
        else:
            a = Trie(self.key_type)
            a.__setitem__(key[1:], value)
            self.children[key[:1]] = a

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.

        >>> t = Trie(str)
        >>> t['bat'] = 7
        >>> t['bark'] = ':)'
        >>> t['bark']
        ':)'
        >>> t['apple']
        Traceback (most recent call last):
            ...
        KeyError: 'given key does not exist in trie'
        >>> t['ba']
        Traceback (most recent call last):
            ...
        KeyError: 'no value associated with key'
        >>> t[1]
        Traceback (most recent call last):
            ...
        TypeError: given key is not of the appropriate type
        """
        if type(key) != self.key_type:
            raise TypeError('given key is not of the appropriate type')
        # base case: if key is at last step in tree
        if len(key) == 0:
            if self.value != None:
                return self.value
            else:
                raise KeyError('no value associated with key')
        # recursive step
        elif key[:1] in self.children:
            return self.children[key[:1]].__getitem__(key[1:])
        else:
            raise KeyError('given key does not exist in trie')

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        >>> t = Trie(str)
        >>> t['bat'] = 7
        >>> t['bark'] = ':)'
        >>> del t['bar']
        Traceback (most recent call last):
            ...
        KeyError: 'no value associated with key'
        >>> del t["foo"]
        Traceback (most recent call last):
            ...
        KeyError: 'given key does not exist in trie'
        """
        if type(key) != self.key_type:
            raise TypeError('given key is not of the appropriate type')
        # base case: if key is at last step in tree
        if len(key) == 0:
            if self.value != None:
                self.value = None
            else:
                raise KeyError('no value associated with key')
            return
        # recursive step
        if key[:1] in self.children:
            return self.children[key[:1]].__delitem__(key[1:])
        else:
            raise KeyError('given key does not exist in trie')

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        >>> t = Trie(str)
        >>> t['bat'] = 7
        >>> t['bar'] = 3
        >>> t['bark'] = ':)'
        >>> 'bar' in t
        True
        >>> 'barking' in t
        False
        >>> 'ba' in t
        False
        """
        try: 
            x = self.__getitem__(key)
        except:
            return False
        return x != None

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """
        # yield case: value is not None
        if self.value != None:
            yield (self.key_type(), self.value)
        for c in self.children:
            for pair in self.children[c]:
                yield (c + pair[0], pair[1])


def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    """
    t = Trie(str)
    for sentence in tokenize_sentences(text):
        for word in sentence.split(' '):
            if word in t:
                t[word] += 1
            else:
                t[word] = 1
    return t

def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    t = Trie(tuple)
    sentences = [tuple(s.split()) for s in tokenize_sentences(text)]
    for sentence in sentences:
        if sentence in t:
            t[sentence] += 1
        else:
            t[sentence] = 1
    return t

def get_node(trie, prefix):
    if not prefix:
        return trie
    if prefix[:1] not in trie.children:
        return None
    return get_node(trie.children[prefix[:1]], prefix[1:])

def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.

    >>> t = Trie(str)
    >>> t['ba'] = 3
    >>> t['bar'] = 1
    >>> t['bart'] = 2
    >>> autocomplete(t, 'bar', 2)
    ['bart', 'bar']
    """
    if type(prefix) != trie.key_type:
        raise TypeError
    root = get_node(trie, prefix)
    if not root:
        return []
    sorts = [prefix + x[0] for x in sorted(root, reverse = True, key = lambda n: n[1])]
    return sorts[:max_count] if max_count != None else sorts

def make_edits(prefix):
    edits = set()
    # single letter deletions
    edits |= set([prefix[:x] + prefix[x+1:] for x in range(len(prefix))])
    # single letter insertions
    edits |= set([prefix[:x] + chr(c) + prefix[x:] for x in range(len(prefix)) for c in range(97,123)])
    # single letter replacements
    edits |= set([prefix[:x] + chr(c) + prefix[x+1:] for x in range(len(prefix)) for c in range(97,123)])
    # two character transpositions
    edits |= set([prefix[:x] + prefix[x+1] + prefix[x] + prefix[x+2:] for x in range(len(prefix)-1)])
    return edits

def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    >>> t = Trie(str)
    >>> t['ba'] = 3
    >>> t['bar'] = 1
    >>> t['bart'] = 2
    >>> autocorrect(t, 'bar', 5)
    ['bart', 'bar', 'ba']
    """
    if max_count == None:
        max_count = len([x for x in trie])
    completes = autocomplete(trie, prefix, max_count)
    edits = []
    if len(completes) < max_count:
        edits = [(get_node(trie, e).value, e) for e in make_edits(prefix) if e in trie and e not in completes]
        edits = [x[1] for x in sorted(edits, reverse = True)]
    return completes + edits[:max_count - len(completes)]

def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    if not pattern:
        if trie.value:
            return [('', trie.value)]
        else:
            return []
    c = pattern[0]
    # if non-special char, look for child in current node that has key of char
    if c != '?' and c != '*':
        returned = []
        if c in trie.children:
            matches = word_filter(trie.children[c], pattern[1:])
            returned += [(c + m[0], m[1]) for m in matches]
        return list(set(returned))
    # if ?, consider all children of current node
    elif c == '?':
        returned = []
        for edge, child in trie.children.items():
            matches = word_filter(child, pattern[1:])
            returned += [(edge + m[0], m[1]) for m in matches]
        return list(set(returned))
    # if *, consider (1) case of * representing 0, so use same node and drop *, or (2) case of * representing pos num, so use all next children and keep *
    elif c == '*':
        returned = []
        matches = word_filter(trie, pattern[1:])
        returned += [(m[0], m[1]) for m in matches]
        for edge, child in trie.children.items():
            matches = word_filter(child, pattern)
            returned += [(edge + m[0], m[1]) for m in matches]
        return list(set(returned))


# you can include test cases of your own in the block below.
if __name__ == '__main__':
    doctest.testmod()

    # with open("alice.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     t = make_phrase_trie(text)
    #     print(autocomplete(t, tuple(), 6))

    # with open("meta.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     t = make_word_trie(text)
    #     print(autocomplete(t, 'gre', 6))

    # with open("meta.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     t = make_word_trie(text)
    #     print(word_filter(t, 'c*h'))

    # with open("twocities.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     t = make_word_trie(text)
    #     print(word_filter(t, 'r?c*t'))

    # with open("alice.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     t = make_word_trie(text)
    #     print(autocorrect(t, 'hear', 12))

    # with open("pride.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     t = make_word_trie(text)
    #     print(autocorrect(t, 'hear'))

    # with open("dracula.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     t = make_word_trie(text)
    #     i = 0
    #     for x in t:
    #         i += 1
    #     print(i)

    # with open("dracula.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     t = make_word_trie(text)
    #     i = 0
    #     for x in t:
    #         if t[x[0]]:
    #             i += t[x[0]]
    #     print(i)

    # with open("alice.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     t = make_phrase_trie(text)
    #     i = 0
    #     for x in t:
    #         i += 1
    #     print(i)

    # with open("alice.txt", encoding="utf-8") as f:
    #     text = f.read()
    #     t = make_phrase_trie(text)
    #     i = 0
    #     for x in t:
    #         if t[x[0]]:
    #             i += t[x[0]]
    #     print(i)

    