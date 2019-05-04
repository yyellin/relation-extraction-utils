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

from relation_extraction_utils.internal.detokenizer import Detokenizer
from relation_extraction_utils.internal.map_csv_column import MapCsvColumns
from relation_extraction_utils.internal.sync_indices import SyncIndices


def prepare_for_path_analysis(output_file, input_file=None, batch_size=None):
    """

     Parameters
     ----------

     Returns
     -------

    """
    output_file = output_file[:-len('.csv')] if output_file.endswith('.csv') else output_file
    input = open(input_file) if input_file is not None else sys.stdin
    csv_reader = csv.reader(input)

    map_columns = MapCsvColumns(next(csv_reader))
    detokenizer = Detokenizer()
    nlp = stanfordnlp.Pipeline()

    count = 0
    batch = 0
    output = None

    for entry in csv_reader:

        tac_tokens = eval(map_columns.get_field_value(entry, 'original_tokens'))
        sentence = detokenizer.detokenize(tac_tokens)

        parsed_sentence = nlp(sentence)
        # let's ignore sentences who parse into multiple sentences - so as to avoid confusion
        if len(parsed_sentence.sentences) > 1:
            continue

        # the next few lines of code deal with opening and closing files (depending on the batching argument, etc)
        new_file = False

        # first option: we've just started but no batching
        if count == 0 and batch_size is None:
            output_file_actual = '{0}.csv'.format(output_file)

            output = open(output_file_actual, 'w', newline='')
            new_file = True

        # second case: we've finished a batch (and we are batching..)
        if batch_size is not None and count % batch_size == 0:
            output_file_actual = '{0}-{1}.csv'.format(output_file, batch)

            if output is not None:
                output.close()

            output = open(output_file_actual, 'w', newline='')
            batch += 1
            new_file = True

        # if we did create a new file, let's ensure that the first row consists of column titles
        if new_file:
            fieldnames = ['id', 'sentence', 'ent1', 'ent2', 'ent1_start', 'ent1_end', 'ent2_start', 'ent2_end',
                          'ud_parse', 'words', 'lemmas']

            csv_out = csv.writer(output)
            csv_out.writerow(fieldnames)

        # now that we've finished creating a new file as necessary, we can proceed with the business
        # at hand:

        count += 1

        ud_parse = []
        for governor, dep, word in parsed_sentence.sentences[0].dependencies:
            ud_parse.append((word.index, word.text, dep, governor.index, governor.text))

        tokens = []
        tokens_with_indices = []
        lemmas_with_indices = []
        for token in parsed_sentence.sentences[0].tokens:
            for word in token.words:
                tokens.append(word.text)
                tokens_with_indices.append((word.index, word.text))
                lemmas_with_indices.append((word.index, word.lemma))

        ud_parse.sort(key=lambda x: int(x[0]))

        tac_tokens_lookup = {}
        tac_tokens_lookup['subj_start'] = int(map_columns.get_field_value(entry, 'subj_start'))
        tac_tokens_lookup['subj_end'] = int(map_columns.get_field_value(entry, 'subj_end'))
        tac_tokens_lookup['obj_start'] = int(map_columns.get_field_value(entry, 'obj_start'))
        tac_tokens_lookup['obj_end'] = int(map_columns.get_field_value(entry, 'obj_end'))

        token_lookup = SyncIndices.b_lookup_to_a_lookup(tac_tokens, tokens, tac_tokens_lookup)

        if len(token_lookup) != len(tac_tokens_lookup):
            print('Big problems:')
            print('tac tokens: {0}'.format(tac_tokens))
            print('good tokens: {0}'.format(tokens))
            print('token_lookup {0}'.format(token_lookup))
            print('tac_tokens_reverse_lookup {0}'.format(tac_tokens_lookup))

            print('skipping ...')
            print()
            continue

        ent1_start = token_lookup['subj_start']
        ent1_end = token_lookup['subj_end']
        ent1 = ' '.join(tokens[ent1_start:ent1_end + 1])

        ent2_start = token_lookup['obj_start']
        ent2_end = token_lookup['obj_end']
        ent2 = ' '.join(tokens[ent2_start:ent2_end + 1])

        csv_out.writerow(
            [count, sentence, ent2, ent1, ent1_start + 1, ent1_end + 1, ent2_start + 1, ent2_end + 1, ud_parse,
             tokens_with_indices,
             lemmas_with_indices])


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description='prepare each entry in the comma-seperated value input for path analysis. '
                    'each entry will be supplemented with additional columns '
                    'ent1, ent2, ud_parse, tokens, lemmas.')

    arg_parser.add_argument(
        'output',
        action='store',
        metavar='output-file',
        help='the comma-seperated field output file')

    arg_parser.add_argument(
        '--input',
        action='store',
        metavar='input-file',
        help='when provided input will be read from this file rather than from standard input')

    arg_parser.add_argument(
        '--batch-size',
        metavar='batch size',
        nargs='?',
        default=None,
        type=int,
        help="it's possible to generate the output file in batches (will be ignored if input is being written to standard output)")

    args = arg_parser.parse_args()

    list_a = ['A', 'co-founder', 'of', 'the', 'Nashville', '-', 'based', 'Country', 'Music', 'Association', 'who',
              'spent', 'more', 'than', 'two', 'decades', 'in', 'charge', 'of', 'Capitol', "'s", 'country', 'music',
              'division', ',', 'Nelson', 'produced', 'upward', 'of', '100', 'No']

    list_b = ['A', 'co-founder', 'of', 'the', 'Nashville-based', 'Country', 'Music', 'Association', 'who', 'spent',
              'more', 'than', 'two', 'decades', 'in', 'charge', 'of', 'Capitol', "'s", 'country', 'music', 'division',
              ',', 'Nelson', 'produced', 'upward', 'of', '100', 'No']

    original_entity_lookup = {}
    original_entity_lookup['subj_start'] = 5
    original_entity_lookup['subj_end'] = 7
    original_entity_lookup['obj_start'] = 1
    original_entity_lookup['obj_end'] = 1

    look = SyncIndices.b_lookup_to_a_lookup(list_a, list_b, original_entity_lookup)

    if len(look) != len(original_entity_lookup):
        print('got problem')
    else:
        print('ggod')

    prepare_for_path_analysis(output_file=args.output, input_file=args.input, batch_size=args.batch_size)

#    convert_tac_to_csv(input, output, args.relation)
