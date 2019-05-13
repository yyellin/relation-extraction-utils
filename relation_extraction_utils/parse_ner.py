# https://stackoverflow.com/questions/14207708/ioerror-errno-32-broken-pipe-python
try:
    from signal import signal, SIGPIPE, SIG_DFL

    signal(SIGPIPE, SIG_DFL)
except:
    pass

import argparse
import csv
import sys

import en_core_web_sm

from relation_extraction_utils.internal.map_csv_column import CsvColumnMapper
from relation_extraction_utils.internal.sync_tags import SyncTags


def parse_ner(input_file=None, output_file=None, batch_size=None):
    """

     Parameters
     ----------

     Returns
     -------

    """
    input = open(input_file) if input_file is not None else sys.stdin
    csv_reader = csv.reader(input)

    column_mapper = CsvColumnMapper(next(csv_reader), ['ner'],
                                    source_required=['sentence', 'ud_parse', 'words'])

    batch = 0
    output = None
    output_file = output_file[:-len('.csv')] if output_file is not None and output_file.endswith('.csv') \
        else output_file


    spacy_pipeline = en_core_web_sm.load()

    for count, entry in enumerate(csv_reader, start=0):

        # the next few lines of code deal with opening and closing files (depending on the batching argument, etc)
        new_file = False

        # first option: standard output ...
        if count == 0 and output_file is None:
            output = sys.stdout
            new_file = True

        # second option: we've just started, we're writing to a real file, but no batching
        if count == 0 and output_file is not None and batch_size is None:
            output_file_actual = '{0}.csv'.format(output_file)

            output = open(output_file_actual, 'w')
            new_file = True

        # second case: we've finished a batch (and we are batching..)
        if batch_size is not None and count % batch_size == 0:
            output_file_actual = '{0}-{1}.csv'.format(output_file, batch)

            if output is not None:
                output.close()

            output = open(output_file_actual, 'w')
            batch += 1
            new_file = True

        # if we did create a new file, let's ensure that the first row consists of column titles
        if new_file:
            csv_writer = csv.writer(output)
            csv_writer.writerow(column_mapper.get_new_headers())

        # now that we've finished creating a new file as necessary, we can proceed with the business
        # at hand:

        sentence = column_mapper.get_field_value_from_source(entry, 'sentence')
        spacy_doc = spacy_pipeline(sentence)
        spacy_tokens = [token.text for token in spacy_doc]

        ner_lookup_spacy_tokenization = {}
        for index, token in enumerate(spacy_doc, start=1):
            if token.ent_type_ in ['PERSON', 'ORG']:
                ner_lookup_spacy_tokenization[index] = token.ent_type_

        tokens = [token for _, token in eval(column_mapper.get_field_value_from_source(entry, 'words'))]
        ner_lookup = ner_lookup_spacy_tokenization

        if tokens != spacy_tokens and len(ner_lookup_spacy_tokenization) > 0:
            ner_lookup = SyncTags.b_lookup_to_a_lookup(tokens, spacy_tokens, ner_lookup_spacy_tokenization)

        csv_writer.writerow(column_mapper.get_new_row_values(entry, [ner_lookup]))


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog='parse_ner',
        description='for each sentence represented by an entry in the comma-separated value input '
                    'add information pertaining to NER . '
                    'Each entry will be supplemented with additional column '
                    'ner')

    arg_parser.add_argument(
        '--input',
        action='store',
        metavar='input-file',
        help='when provided input will be read from this file rather than from standard input')

    arg_parser.add_argument(
        '--output',
        action='store',
        metavar='output-file',
        help='the comma-separated field output file')

    arg_parser.add_argument(
        '--batch-size',
        metavar='batch size',
        nargs='?',
        default=None,
        type=int,
        help="it's possible to generate the output file in batches (will be ignored if input is being written to standard output)")

    args = arg_parser.parse_args()

    parse_ner(input_file=args.input, output_file=args.output, batch_size=args.batch_size)
