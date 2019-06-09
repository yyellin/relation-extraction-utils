import argparse
import csv
import sys

from relation_extraction_utils.internal.dep_graph import DepGraph
from relation_extraction_utils.internal.link import Link
from relation_extraction_utils.internal.map_csv_column import CsvColumnMapper
from relation_extraction_utils.internal.ucca_types import UccaParsedPassage


def identify_ucca_paths(input, output):
    csv_reader = csv.reader(input)
    csv_writer = csv.writer(output)

    column_mapper = CsvColumnMapper(
        next(csv_reader),
        target_columns=['path'],
        source_required=['id',
                         'sentence',
                         'ent1_start',
                         'ent1_end',
                         'ent2_start',
                         'ent2_end',
                         'ucca_parse',
                         # 'trigger_idx',
                         'comment'])

    csv_writer.writerow(column_mapper.get_new_headers())

    for counter, entry in enumerate(csv_reader, start=1):

        ucca_parse_serialization = column_mapper.get_field_value_from_source(entry, 'ucca_parse')
        if ucca_parse_serialization is None:
            # TODO!!!
            continue
        ucca_parse = UccaParsedPassage.from_serialization(ucca_parse_serialization)
        links = Link.get_links_from_ucca_dep(ucca_parse)
        graph = DepGraph(links)

        ent1_start_token_id = column_mapper.get_field_value_from_source(entry, 'ent1_start', as_int=True)
        ent1_end_token_id = column_mapper.get_field_value_from_source(entry, 'ent1_end', as_int=True)
        if ent1_start_token_id is None or ent1_end_token_id is None:
            # TODO!!!
            continue

        ent1_start_node_id = ucca_parse.node_id_by_token_id(ent1_start_token_id)
        ent1_parent_node_id = graph.get_parents(ent1_start_node_id)

        ent2_start = column_mapper.get_field_value_from_source(entry, 'ent2_start', as_int=True)
        ent2_end = column_mapper.get_field_value_from_source(entry, 'ent2_end', as_int=True)
        if ent2_start is None or ent2_end is None:
            continue


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
