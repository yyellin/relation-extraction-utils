# https://stackoverflow.com/questions/14207708/ioerror-errno-32-broken-pipe-python
try:
    from signal import signal, SIGPIPE, SIG_DFL

    signal(SIGPIPE, SIG_DFL)
except:
    pass

import argparse
import csv
import sys
from itertools import zip_longest

import spacy

from relation_extraction_utils.internal.detokenizer import Detokenizer
from relation_extraction_utils.internal.map_csv_column import CsvColumnMapper
from relation_extraction_utils.internal.mnofc import ManageNewOutputFileCreation
from relation_extraction_utils.internal.sync_tac_tags import SyncTacTags
from relation_extraction_utils.internal.tupa_parser2 import TupaParser2

TUPA_BATCH_SIZE = 1000

def parse_ucca(tupa_dir, model_prefix, input_file=None, output_file=None, batch_size=None):
    """

     Parameters
     ----------

     Returns
     -------

    """
    input = open(input_file, encoding='utf-8') if input_file is not None else sys.stdin
    csv_reader = csv.reader(input)

    column_mapper = CsvColumnMapper(
        source_first_row=next(csv_reader),
        target_columns=
        ['id',
         'sentence',
         'ent1',
         'ent2',
         'ent1_start',
         'ent1_end',
         'ent2_start',
         'ent2_end',
         'ucca_parse',
         'words',
         'lemmas',
         'comment'],
        source_required=
        ['tac_tokens',
         'subj_start',
         'subj_end',
         'obj_start',
         'obj_end'],
        filter_source_from_result=
        ['subj_start',
         'subj_end',
         'obj_start',
         'obj_end']
    )

    detokenizer = Detokenizer()
    mnofc = ManageNewOutputFileCreation(output_file, batch_size)

    parser = TupaParser2(tupa_dir, model_prefix)
    nlp = spacy.load('en_core_web_md')

    count = 0
    for next_batch in zip_longest(*([csv_reader] * TUPA_BATCH_SIZE)):
        print('parsing batch')
        sentences = []
        for entry in next_batch:

            if entry is None:
                #we've reached the end of the batch
                break

            tac_tokens = eval(column_mapper.get_field_value_from_source(entry, 'tac_tokens'))
            sentence = detokenizer.detokenize(tac_tokens)
            sentences.append(sentence)

        parsed_sentences = parser.parse_sentences(sentences)
        print(parsed_sentences[0].terminals[0].token_id, parsed_sentences[0].terminals[0].text)

        for sentence, parsed_sentence, entry in zip(sentences, parsed_sentences, next_batch):

            new_file = mnofc.get_new_file_if_necessary()
            if new_file:
                csv_writer = csv.writer(new_file)
                csv_writer.writerow(column_mapper.get_new_headers())

            tokens = []
            tokens_with_indices = []
            lemmas_with_indices = []


            for ucca_terminal in parsed_sentence.terminals:
                tokens.append(ucca_terminal.text)
                tokens_with_indices.append((ucca_terminal.token_id, ucca_terminal.text))

            spacied = nlp(sentence)
            for token_id, word in enumerate(spacied, start=1):
                lemmas_with_indices.append((token_id, word.lemma))


            tac_tokens_lookup = {}
            tac_tokens_lookup['subj_start'] = int(column_mapper.get_field_value_from_source(entry, 'subj_start'))
            tac_tokens_lookup['subj_end'] = int(column_mapper.get_field_value_from_source(entry, 'subj_end'))
            tac_tokens_lookup['obj_start'] = int(column_mapper.get_field_value_from_source(entry, 'obj_start'))
            tac_tokens_lookup['obj_end'] = int(column_mapper.get_field_value_from_source(entry, 'obj_end'))

            token_lookup = SyncTacTags.b_lookup_to_a_lookup(tokens, tac_tokens, tac_tokens_lookup)

            if len(token_lookup) != len(tac_tokens_lookup):
                csv_writer.writerow(column_mapper.get_new_row_values(entry,
                                                                     [count,
                                                                      sentence,
                                                                      None,
                                                                      None,
                                                                      None,
                                                                      None,
                                                                      None,
                                                                      None,
                                                                      None,
                                                                      None,
                                                                      None,
                                                                      'was not able to reconcile TAC and Tupa\'s Spacy based indexing']))
                continue

            ent1_start = token_lookup['subj_start']
            ent1_end = token_lookup['subj_end']
            ent1 = ' '.join(tokens[ent1_start:ent1_end + 1])

            ent2_start = token_lookup['obj_start']
            ent2_end = token_lookup['obj_end']
            ent2 = ' '.join(tokens[ent2_start:ent2_end + 1])

            csv_writer.writerow(column_mapper.get_new_row_values(entry,
                                                                 [count,
                                                                  sentence,
                                                                  ent1,
                                                                  ent2,
                                                                  ent1_start + 1,
                                                                  ent1_end + 1,
                                                                  ent2_start + 1,
                                                                  ent2_end + 1,
                                                                  parsed_sentence.serialize(),
                                                                  tokens_with_indices,
                                                                  lemmas_with_indices,
                                                                  None]))

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog='parse_ucca2',
        description='prepare each sentence represented by an entry in the comma-separated value input '
                    'for ucca based path analysis. '
                    'Each entry will be supplemented with additional columns '
                    'ent1, ent2, ucca_parse, tokens, lemmas. '
                    '(Tokenization is according to ucca and not the input tokens)')

    arg_parser.add_argument(
        'tupa',
        action='store',
        metavar='director-of-tupa-module',
        help='the directory on the local host in which the tupa module is installed')

    arg_parser.add_argument(
        'model',
        action='store',
        metavar='model-path-prefix',
        help='full path and then the prefix of the model as a single string (for example:'
             '(/code/train-founded-by.csv /models/elmo_4_test_sentences_1/elmo_4_test_sentences_1')

    arg_parser.add_argument(
        '--input',
        action='store',
        metavar='input-file',
        help='when provided input will be read from this file rather than from standard input')

    arg_parser.add_argument(
        '--output',
        action='store',
        metavar='output-file',
        help='when provided output will be written to this file rather than standard output')

    arg_parser.add_argument(
        '--batch-size',
        metavar='batch size',
        nargs='?',
        default=None,
        type=int,
        help="it's possible to generate the output file in batches (will be ignored if input is being written to standard output)")

    args = arg_parser.parse_args()

    parse_ucca(args.tupa, args.model, input_file=args.input, output_file=args.output, batch_size=args.batch_size)
