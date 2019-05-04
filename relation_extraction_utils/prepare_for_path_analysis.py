# https://stackoverflow.com/questions/14207708/ioerror-errno-32-broken-pipe-python
try:
    from signal import signal, SIGPIPE, SIG_DFL

    signal(SIGPIPE, SIG_DFL)
except:
    pass

import argparse
import csv
import sys

import stanfordnlp

from internal.detokenizer import Detokenizer
from internal.map_csv_column import MapCsvColumns
from internal.sync_indices import SyncIndices


def prepare_for_path_analysis(input_file=None, output_file=None, batch_size=None):
    """

     Parameters
     ----------

     Returns
     -------

    """

    input = open(input_file) if input_file is not None else sys.stdin
    cvs_reader = csv.reader(input)

    map_columns = MapCsvColumns(next(cvs_reader))
    detokenizer = Detokenizer()
    nlp = stanfordnlp.Pipeline()

    count = 0
    batch = 0
    output = None

    for entry in cvs_reader:

        original_tokens = eval(map_columns.get_field_value(entry, 'original_tokens'))
        sentence = detokenizer.detokenize(original_tokens)

        parsed_sentence = nlp(sentence)

        # let's ignore sentences who parse into multiple sentences - so as to avoid confusion
        if len(parsed_sentence.sentences) > 1:
            continue

        new_file = False

        # first case: we've just started and need to write to standard output
        if count == 0 and output_file is None:
            output = sys.stdout
            new_file = True

        # second case: we've just started and need to write to file but no batching
        if count == 0 and output_file is not None and batch_size is None:
            output = open(output_file, 'w', newline='')
            new_file = True

        # third case: we've finished a batch (and we are batching
        if count % batch_size == 0 and output_file is not None and batch_size is not None:
            output_file_numbered = '{0}.{1}'.format(output_file, batch)

            if output is not None:
                output.close()

            output = open(output_file_numbered, 'w', newline='')
            batch += 1
            new_file = True

        if new_file:
            fieldnames = ['id', 'sentence', 'ent1', 'ent2', 'ent1_start', 'ent1_end', 'ent2_start', 'ent2_end',
                          'ud_parse', 'words', 'lemmas']

            csv_out = csv.writer(output)
            csv_out.writerow(fieldnames)

        count += 1

        ud_parse = []

        for governor, dep, word in parsed_sentence.sentences[0].dependencies:
            ud_parse.append((word.index, word.text, dep, governor.index, governor.text))

        tokens = []
        lemmas = []

        for token in parsed_sentence.sentences[0].tokens:
            for word in token.words:
                tokens.append((word.index, word.text))
                lemmas.append((word.index, word.lemma))

        ud_parse.sort(key=lambda x: int(x[0]))

        original_entity_lookup = {}
        original_entity_lookup['subj_start'] = entry['subj_start']
        original_entity_lookup['subj_end'] = entry['subj_end']
        original_entity_lookup['obj_start'] = entry['obj_start']
        original_entity_lookup['obj_end'] = entry['obj_end']

        entity_lookup = SyncIndices.b_lookup_to_a_lookup(original_tokens, tokens, original_entity_lookup)

        if len(entity_lookup) != len(original_entity_lookup):
            print('Big problems for sentence: {0}'.format(sentence))
            print('skipping ...')
            continue

        subj_start = entity_lookup['subj_start']
        subj_end = entity_lookup['subj_end']
        subj = ' '.join(tokens[subj_start:subj_end + 1])

        obj_start = entity_lookup['obj_start']
        obj_end = entity_lookup['obj_end']
        obj = ' '.join(tokens[obj_start:obj_end + 1])

        csv_out.writerow(
            [count, sentence, obj, subj, subj_start + 1, subj_end + 1, obj_start + 1, obj_end + 1, ud_parse, tokens,
             lemmas])


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description='prepare each entry in the comma-seperated value input for path analysis. '
                    'each entry will be supplemented with additional columns '
                    'ent1, ent2, ud_parse, tokens, lemmas.')

    arg_parser.add_argument(
        '--input',
        action='store',
        metavar='input-file',
        help='when provided input will be read from this file rather than from standard input')

    arg_parser.add_argument(
        '--output',
        action='store',
        metavar='output-file',
        help='when provided output will be written to this file rather than to standard output')

    arg_parser.add_argument(
        '--batch-size',
        metavar='batch size',
        nargs='?',
        default=None,
        type=int,
        help="it's possible to generate the output file in batches (will be ignored if input is being written to standard output)")

    args = arg_parser.parse_args()

    prepare_for_path_analysis(input_file=args.input, output_file=args.output, batch_size=args.batch_size)

#    convert_tac_to_csv(input, output, args.relation)
