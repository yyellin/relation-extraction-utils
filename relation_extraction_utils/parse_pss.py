# https://stackoverflow.com/questions/14207708/ioerror-errno-32-broken-pipe-python
try:
    from signal import signal, SIGPIPE, SIG_DFL

    signal(SIGPIPE, SIG_DFL)
except:
    pass

import argparse
import csv
import os
import sys

from nltk.tokenize import word_tokenize

from relation_extraction_utils.internal.map_csv_column import CsvColumnMapper
from relation_extraction_utils.internal.sync_pss_tags import SyncPssTags


def parse_pss(port, model_path, input_file=None, output_file=None, batch_size=None):
    """

     Parameters
     ----------

     Returns
     -------

    """

    input = open(input_file) if input_file is not None else sys.stdin
    csv_reader = csv.reader(input)

    column_mapper = CsvColumnMapper(next(csv_reader), ['pss'],
                                    source_required=['sentence', 'ud_parse', 'words'])

    batch = 0
    output = None
    output_file = output_file[:-len('.csv')] if output_file is not None and output_file.endswith('.csv') \
        else output_file

    print('BEGIN-INIT-PSS')

    from models.supersenses.lstm_mlp_supersenses_model import LstmMlpSupersensesModel
    from models.supersenses.preprocessing import preprocess_sentence
    from models.supersenses.preprocessing.corenlp import CoreNLPServer


    corenlp = CoreNLPServer()
    corenlp.start(port)

    model = LstmMlpSupersensesModel.load(model_path)

    print('END-INIT-PSS')


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

        proper_tokens = word_tokenize(sentence)

        print('BEGIN-PROCESS-PSS')
        preprocessed = preprocess_sentence(' '.join(proper_tokens))
        pss_pred = model.predict(preprocessed.xs, [x.identified_for_pss for x in preprocessed.xs])
        print('END-PROCESS-PSS')

        pss_lookup_nltk_tokens = {}
        for index in range(len(preprocessed.xs)):
            if pss_pred[index].supersense_role:
                pss_lookup_nltk_tokens[index + 1] = (pss_pred[index].supersense_role, pss_pred[index].supersense_func)

        ud_tokens = [token for _, token in eval(column_mapper.get_field_value_from_source(entry, 'words'))]
        pss_lookup = pss_lookup_nltk_tokens

        if ud_tokens != proper_tokens and len(pss_lookup_nltk_tokens) > 0:
            pss_lookup = SyncPssTags.get_pss_tags_by_index(ud_tokens, proper_tokens, pss_lookup_nltk_tokens)

        csv_writer.writerow(column_mapper.get_new_row_values(entry, [pss_lookup]))

    corenlp.stop()

if __name__ == "__main__":

    arg_parser = argparse.ArgumentParser(
        prog='parse_pss',
        description='for each sentence represented by an entry in the comma-separated value input '
                    'add information pertaining to PSS . '
                    'Each entry will be supplemented with additional column '
                    'pss. '
                    'Notes: (1) The module requires two environment parameters to be set: '
                    'CORE_NLP_PORT to indicate which port to run the internal Java server, and '
                    'PSS_MODEL_PATH that should point to the model path (without the file extension'
                    '(2) The module requires a crafted PSS environment in order to run - '
                    'there is a Google colab ipynb file for this')


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


    port = os.environ.get('CORE_NLP_PORT')
    assert (port is not None)

    model_path = os.environ.get('PSS_MODEL_PATH')
    assert (model_path is not None)

    parse_pss(int(port), model_path, input_file=args.input, output_file=args.output, batch_size=args.batch_size)
