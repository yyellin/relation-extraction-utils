import argparse
import csv
import json

import stanfordnlp

from relation_extraction_utils.internal.detokenizer import Detokenizer


def generate_csv_file(train_data_path, relation_name, csv_file_path, batch_size=None):
    # load the file, which is in json format, into a python data structure 'train'
    relations = []

    with open(train_data_path) as f:
        train = json.load(f)
        for entry in train:
            if entry['relation'] == relation_name:
                relations.append(entry)

    detokenizer = Detokenizer()

    csv_file_path_without_suffix = csv_file_path[:-len('.csv')] if csv_file_path.endswith('.csv') \
        else csv_file_path

    nlp = stanfordnlp.Pipeline()

    count = 0
    batch = 0
    output_file = None

    for relation in relations:

        tokens = relation['token']
        sentence = detokenizer.detokenize(tokens)
        parsed_sentence = nlp(sentence)

        # let's ignore sentences who parse into multiple sentences - so as to avoid confusion
        if len(parsed_sentence.sentences) > 1:
            continue

        new_file = False
        if batch_size is None and count == 0:
            output_file_name = '{0}.csv'.format(csv_file_path_without_suffix)
            output_file = open(output_file_name, 'w', newline='')
            new_file = True

        if batch_size is not None and count % batch_size == 0:
            output_file_name = '{0}-{1}.csv'.format(csv_file_path_without_suffix, batch)

            if output_file is not None:
                output_file.close()

            output_file = open(output_file_name, 'w', newline='')
            batch += 1
            new_file = True

        if new_file:
            fieldnames = ['counter', 'sentence', 'ent1', 'ent2',
                          'dependency_parse', 'index_lookup', 'lemmas',
                          'trigger', 'trigger_idx',
                          'ent1_start', 'ent1_end',
                          'ent2_start', 'ent2_end',
                          'comments']

            csv_out = csv.writer(output_file)
            csv_out.writerow(fieldnames)

        count += 1

        subj_start = relation['subj_start']
        subj_end = relation['subj_end']
        subj = ' '.join(tokens[subj_start:subj_end + 1])

        obj_start = relation['obj_start']
        obj_end = relation['obj_end']
        obj = ' '.join(tokens[obj_start:obj_end + 1])

        dependencies = []

        for governor, dep, word in parsed_sentence.sentences[0].dependencies:
            dependencies.append((word.index, word.text, dep, governor.index, governor.text))

        texts = []
        lemmas = []

        for token in parsed_sentence.sentences[0].tokens:

            for word in token.words:
                texts.append((word.index, word.text))
                lemmas.append((word.index, word.lemma))

        dependencies.sort(key=lambda x: int(x[0]))

        index_lookup_str = '\n'.join(['{0}: \'{1}\''.format(tuple[0], tuple[1]) for tuple in texts])

        csv_out.writerow([count, sentence, obj, subj,
                          dependencies, index_lookup_str, lemmas,
                          None, None,
                          subj_start + 1, subj_end + 1,
                          obj_start + 1, obj_end + 1,
                          None
                          ])


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="create a csv file for a relationship "
                                                     "with the following columns: "
                                                     "'counter', 'sentence', 'ent1', 'ent2', 'dependency_parse', "
                                                     "'index_lookup', 'lemmas'")

    arg_parser.add_argument('train_data_path',
                            metavar='train-data-path',
                            help="path to TAC's train data json file")

    arg_parser.add_argument('relation_name',
                            metavar='relation-name',
                            help="filters sentences that have been tagged as matching this relation")

    arg_parser.add_argument('csv_file_path',
                            metavar='csv-file-path',
                            help="the path of the csv output file(s)")

    arg_parser.add_argument('batch_size',
                            metavar='batch size',
                            nargs='?',
                            default=None,
                            type=int,
                            help="it's possible to generate the output file in batches")

    args = arg_parser.parse_args()
    generate_csv_file(args.train_data_path, args.relation_name, args.csv_file_path, args.batch_size)
