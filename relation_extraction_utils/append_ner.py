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
from relation_extraction_utils.internal.mnofc import ManageNewOutputFileCreation
from relation_extraction_utils.internal.sync_tags import SyncTags


def append_ner(input_file=None, output_file=None, batch_size=None):
    """

     Parameters
     ----------

     Returns
     -------

    """
    input = open(input_file, encoding='utf-8') if input_file is not None else sys.stdin
    csv_reader = csv.reader(input)

    column_mapper = CsvColumnMapper(next(csv_reader), ['ner'],
                                    source_required=['sentence', 'words'])

    mnofc = ManageNewOutputFileCreation(output_file, batch_size)

    spacy_pipeline = en_core_web_sm.load()

    for count, entry in enumerate(csv_reader, start=0):

        new_file = mnofc.get_new_file_if_necessary()
        if new_file:
            csv_writer = csv.writer(new_file)
            csv_writer.writerow(column_mapper.get_new_headers())

        # now that we've finished creating a new file as necessary, we can proceed with the business
        # at hand:

        words = column_mapper.get_field_value_from_source(entry, 'words', True)
        if words is None:
            csv_writer.writerow(column_mapper.get_new_row_values(entry, [None]))
            continue

        sentence = column_mapper.get_field_value_from_source(entry, 'sentence')
        spacy_doc = spacy_pipeline(sentence)
        spacy_tokens = [token.text for token in spacy_doc]

        ner_lookup_spacy_tokenization = {}
        for index, token in enumerate(spacy_doc, start=1):
            if token.ent_type != 0:  # in ['PERSON', 'ORG']:
                ner_lookup_spacy_tokenization[index] = token.ent_type_

        ner_lookup = ner_lookup_spacy_tokenization
        tokens = [token for _, token in words]

        if tokens != spacy_tokens and len(ner_lookup_spacy_tokenization) > 0:
            ner_lookup = SyncTags.b_lookup_to_a_lookup(tokens, spacy_tokens, ner_lookup_spacy_tokenization)

        csv_writer.writerow(column_mapper.get_new_row_values(entry, [ner_lookup]))


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog='append_ner',
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

    append_ner(input_file=args.input, output_file=args.output, batch_size=args.batch_size)
