import re

from .chunker_crf_params import ChunkerCrfParams


BEG_TOKEN = '<beg>'
END_TOKEN = '<end>'

token2tag = {BEG_TOKEN: BEG_TOKEN, END_TOKEN: END_TOKEN}


def is_num(token):
    return re.match('^[0-9]+$', token)


def shingles(word0):
    word = '[' + word0 + ']'
    return set(c1+c2+c3 for c1, c2, c3 in zip(word, word[1:], word[2:]))



def get_word_features(word, prefix, word2tags, tags, chunker_params):
    assert(word)
    assert(prefix)

    features = []

    if word in token2tag:
        features.append((u'tag[{}]={}'.format(prefix, token2tag[word]), 1.0))
    elif is_num(word):
        features.append((u'tag[{}]=<num> tag[{}]=<num_{}>'.format(prefix, prefix, word[-1]), 1.0))
    elif len(word) == 1 and word[0] in u'‼≠™®•·[¡+<>`~;.,‚?!-…№”“„{}|‹›/\'"–—_:«»*]()‘’≈':
        features.append((u'tag[{}]=punct_{}'.format(prefix, ord(word[0])), 1.0))
    else:
        first_char = word[0]
        if first_char in u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ':
            features.append((u'word[{}]=<latin>'.format(prefix), 1.0))
        else:
            if first_char in u'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ':
                features.append((u'word[{}]=<upper1>'.format(prefix), 1.0))

            if chunker_params.ending_len > 0:
                ending = '~' + word[-chunker_params.ending_len:] if len(word) > chunker_params.ending_len else word
                features.append((u'ending[{}]={}'.format(prefix, ending), 1.0))

            if chunker_params.use_shingles:
                for shingle in shingles(word):
                    features.append((u'shingle[{}]={}'.format(prefix, shingle), 1.0))

            if chunker_params.use_gren:
                tags0 = set()
                for tagset in word2tags[word]:
                    tags0.update(tagset.split(' '))

                for tag in tags0:
                    features.append((u'tag[{}]={}'.format(prefix, tag), 1.0))

            if chunker_params.use_postagger and tags:
                for tag in tags:
                    features.append((u'tag[{}]={}'.format(prefix, tag), 1.0))

    return features


def vectorize_sample(lines, word2tags, postagger, chunker_params, with_labels):
    lines1 = []
    for line in lines:
        if with_labels:
            word = line[0]
            label = line[1]
        else:
            word = line
            label = -1

        if len(word) == 0:
            print(u'Zero-length word in sample: {}'.format(u'|'.join(x[0] for x in lines)))
            raise ValueError()

        lines1.append((word, label))

    lines2 = []
    nb_words = len(lines1)

    if chunker_params.use_postagger:
        tagsets = [d[1].split('|') for d in postagger.tag([d[0] for d in lines1])]
    else:
        tagsets = [None for _ in lines]

    for iword, data0 in enumerate(lines1):
        label = data0[1]
        word_features = dict()
        for j in range(-chunker_params.winspan, chunker_params.winspan + 1):
            iword2 = iword + j
            if nb_words > iword2 >= 0:
                features = get_word_features(lines1[iword2][0], str(j), word2tags, tagsets[iword2], chunker_params)
                word_features.update(features)
            elif iword2 < 0:
                features = get_word_features(BEG_TOKEN, str(j), word2tags, '', chunker_params)
                word_features.update(features)
            else:
                features = get_word_features(END_TOKEN, str(j), word2tags, '', chunker_params)
                word_features.update(features)

        if with_labels:
            lines2.append((word_features, label))
        else:
            lines2.append(word_features)

    return lines2, tagsets


def print_word_features(features, separator):
    return separator.join(u'{}:{}'.format(f, v) for (f, v) in features.items())

