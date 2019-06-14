import argparse
import csv
import sys
from itertools import product

from relation_extraction_utils.internal.dep_graph import DepGraph
from relation_extraction_utils.internal.link import Link
from relation_extraction_utils.internal.map_csv_column import CsvColumnMapper
from relation_extraction_utils.internal.ucca_types import UccaParsedPassage


def identify_ucca_paths(input, output):
    csv_reader = csv.reader(input)
    csv_writer = csv.writer(output)

    column_mapper = CsvColumnMapper(
        next(csv_reader),
        target_columns=['path_id', 'path', 'comment'],
        source_required=['id',
                         'sentence',
                         'ent1_start',
                         'ent1_end',
                         'ent2_start',
                         'ent2_end',
                         'ucca_parse',
                         'trigger_idx'])

    csv_writer.writerow(column_mapper.get_new_headers())

    for counter, entry in enumerate(csv_reader, start=1):

        if 'The Rev. Al Sharpton, who attended a meeting held by the magazine' in column_mapper.get_field_value_from_source(
                entry, 'sentence'):
            wait_here = True

        print('Processing sentence #', column_mapper.get_field_value_from_source(entry, 'id'))

        ucca_parse_serialization = column_mapper.get_field_value_from_source(entry, 'ucca_parse')
        if ucca_parse_serialization is None:
            csv_writer.writerow(column_mapper.get_new_row_values(entry, [None, None, 'ucca_parse missing']))
            continue

        ucca_parse = UccaParsedPassage.from_serialization(ucca_parse_serialization)
        links = ucca_parse.get_links()

        trigger_token_id = column_mapper.get_field_value_from_source(entry, 'trigger_idx', as_int=True)
        ent1_start_token_id = column_mapper.get_field_value_from_source(entry, 'ent1_start', as_int=True)
        ent2_start_token_id = column_mapper.get_field_value_from_source(entry, 'ent2_start', as_int=True)

        if trigger_token_id is None or ent1_start_token_id is None or ent2_start_token_id is None:
            csv_writer.writerow(column_mapper.get_new_row_values(entry, [None, None, 'indices missing']))
            continue

        trigger_node_id = ucca_parse.get_node_id_by_token_id(trigger_token_id)
        trigger_parent_node_id = Link.get_parents(links, trigger_node_id)[0]

        ent1_start_node_id = ucca_parse.get_node_id_by_token_id(ent1_start_token_id)
        ent1_parent_node_id = Link.get_parents(links, ent1_start_node_id)[0]

        ent2_start_node_id = ucca_parse.get_node_id_by_token_id(ent2_start_token_id)
        ent2_parent_node_id = Link.get_parents(links, ent2_start_node_id)[0]

        graph = DepGraph(links)

        ent1_to_trigger_steps = graph.get_steps(ent1_parent_node_id, trigger_parent_node_id)
        ent1_to_trigger_strings = ucca_parse.get_path_representations(ent1_to_trigger_steps)

        trigger_to_ent2_steps = graph.get_steps(trigger_parent_node_id, ent2_parent_node_id)
        trigger_to_ent2_strings = ucca_parse.get_path_representations(trigger_to_ent2_steps)

        sentence_id = column_mapper.get_field_value_from_source(entry, 'id', as_int=True)

        for count, (segment1, segment2) in enumerate(product(ent1_to_trigger_strings, trigger_to_ent2_strings),
                                                     start=1):
            path_id = '{0}_{1}'.format(sentence_id, count)
            path = '{0} >< {1}'.format(segment1, segment2)
            comment = None

            csv_writer.writerow(column_mapper.get_new_row_values(entry, [path_id, path, comment]))



if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog='identify_paths',
        description='for each row in input add path analysis')

    arg_parser.add_argument(
        '--input',
        action='store',
        metavar='input-file',
        help='When provided input will be read from this file rather than from standard input')

    arg_parser.add_argument(
        '--output',
        action='store',
        metavar='output-file',
        help='The comma-separated field output file')

    args = arg_parser.parse_args()

    input = open(args.input, encoding='utf-8') if args.input is not None else sys.stdin
    output = open(args.output, 'w', encoding='utf-8', newline='') if args.output is not None else sys.stdout

    identify_ucca_paths(input, output)

#
#    input_rows = pd.read_csv(sys.stdin if input_file is None else input_file)
#    input_rows.dropna(subset=['ud_parse'], inplace=True)
