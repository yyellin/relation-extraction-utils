import csv
import json
from itertools import zip_longest

import stanfordnlp

from prepare_for_trigger_identification.detokenizer import Detokenizer


def generate_csv_file(train_data_path, relation_name, cvs_file_path):
    # load the file, which is in json format, into a python data structure 'train'
    relations = []

    with open(train_data_path) as f:
        train = json.load(f)

        for entry in train:
            if entry['relation'] == relation_name:
                relations.append(entry)

    sentences = []
    detokenizer = Detokenizer()
    for relation in relations:
        tokens = relation['token']
        sentences.append(detokenizer.detokenize(tokens))

    parsed_sentences = []
    nlp = stanfordnlp.Pipeline()

    for sentence in sentences:
        parsed_sentence = nlp(sentence)
        parsed_sentences.append(parsed_sentence)

    with open(cvs_file_path, 'w', newline='') as myfile:
        fieldnames = ['counter', 'sentence', 'ent1', 'ent2',
                      'dependency_parse', 'index_lookup',
                      'trigger', 'trigger_idx',
                      'ent1_start', 'ent1_end',
                      'ent2_start', 'ent2_end',
                      'comments']

        csv_out = csv.writer(myfile)

        csv_out.writerow(fieldnames)

        count = 0

        for sentence, relation, parse in zip_longest(sentences, relations, parsed_sentences):

            # let's ignore sentences who parse into multiple sentences - so as to avoid confusion
            if len(parse.sentences) == 1:

                count += 1

                input_tokens = relation['token']

                subj_start = relation['subj_start']
                subj_end = relation['subj_end']
                subj = ' '.join(input_tokens[subj_start:subj_end + 1])

                obj_start = relation['obj_start']
                obj_end = relation['obj_end']
                obj = ' '.join(input_tokens[obj_start:obj_end + 1])

                dependencies = []

                for governor, dep, word in parse.sentences[0].dependencies:
                    dependencies.append((word.index, word.text, dep, governor.index, governor.text))

                dependencies.sort(key=lambda x: int(x[0]))
                index_lookup_str = '\n'.join(['\'{0}\': {1}'.format(dep[1], dep[0]) for dep in dependencies])

                csv_out.writerow([count, sentence, obj, subj, dependencies, index_lookup_str])
