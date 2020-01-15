import json


class ChunkerCrfParams:
    def __init__(self):
        self.winspan = None
        self.use_gren = None
        self.use_postagger = None
        self.use_shingles = None
        self.ending_len = None
        self.model_filename = None

    @staticmethod
    def load(config_path):
        chunker_params = ChunkerCrfParams()
        with open(config_path, 'r') as f:
            cfg = json.load(f)

            chunker_params.winspan = cfg['winspan']
            chunker_params.use_gren = cfg['use_gren']
            chunker_params.use_postagger = cfg['use_postagger']
            chunker_params.use_shingles = cfg['use_shingles']
            chunker_params.ending_len = cfg['ending_len']
            chunker_params.model_filename = cfg['model_filename']

        return chunker_params
