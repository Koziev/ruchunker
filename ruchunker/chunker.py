import json
import io
import os
import pathlib

import pycrfsuite

import ruword2tags
import rupostagger

from .chunker_crf_params import ChunkerCrfParams
from .sample_vectorization import vectorize_sample


class ChunkToken:
    def __init__(self, index, word, tagset):
        self.index = index
        self.word = word
        self.tagset = tagset

    def __repr__(self):
        s = self.word
        if self.tagset:
            s += '({})'.format('|'.join(self.tagset))
        return s


class Chunk:
    def __init__(self):
        self.tokens = []

    def __repr__(self):
        return ' '.join(map(str, self.tokens))



class Chunker:
    def __init__(self):
        self.word2tags = None
        self.postagger = None
        self.chunker_params = None
        self.crf_tagger = None

    def load(self, model_dir=None):
        if model_dir is None:
            module_folder = str(pathlib.Path(__file__).resolve().parent)
            model_dir = os.path.join(module_folder, '../tmp')
            if not os.path.exists(model_dir):
                model_dir = module_folder

        config_path = os.path.join(model_dir, 'chunker_NP.config')
        self.chunker_params = ChunkerCrfParams.load(config_path)

        if self.chunker_params.use_gren:
            self.word2tags = ruword2tags.RuWord2Tags()
            self.word2tags.load()

        if self.chunker_params.use_postagger:
            self.postagger = rupostagger.RuPosTagger()
            self.postagger.load()

        self.crf_tagger = pycrfsuite.Tagger()
        self.crf_tagger.open(os.path.join(model_dir, self.chunker_params.model_filename))

    def __build_chunks(self, y_pred, tagsets):
        chunks = []

        chunk = None
        for i, (y, tagset) in enumerate(zip(y_pred, tagsets)):
            if y == '0':
                if chunk:
                    chunks.append(chunk)
                    chunk = None
            elif y == '1':
                if chunk:
                    chunks.append(chunk)

                chunk = Chunk()
                chunk.tokens.append(ChunkToken(i, tagset[0], tagset[1]))
            elif y == '2':
                chunk.tokens.append(ChunkToken(i, tagset[0], tagset[1]))
            else:
                raise RuntimeError()

        if chunk:
            chunks.append(chunk)

        return chunks

    def parse(self, tokens):
        features_list, tagsets = vectorize_sample(tokens, self.word2tags, self.postagger, self.chunker_params, with_labels=False)

        y_pred = self.crf_tagger.tag(xseq=features_list)

        #for word, label in zip(tokens, y_pred):
        #    print('{}\t{}'.format(label, word))
        #print('\n')

        chunks = self.__build_chunks(y_pred, zip(tokens, tagsets))
        return chunks
