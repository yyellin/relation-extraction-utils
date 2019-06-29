import argparse
import csv
import sys

from relation_extraction_utils.internal.map_csv_column import CsvColumnMapper


def filter_relations(input, output, entity_types=None):
    csv_reader = csv.reader(input)
    csv_writer = csv.writer(output)

    required_columns = ['id', 'sentence', 'words', 'lemmas', 'ent1_start', 'ent1_end', 'ent2_start', 'ent2_end', 'path']

    if entity_types is not None:
        required_columns.append('ner')

    column_mapper = CsvColumnMapper(
        source_first_row=next(csv_reader),
        target_columns=[],
        source_required=required_columns)

    csv_writer.writerow(column_mapper.get_new_headers())

    for counter, entry in enumerate(csv_reader, start=1):

        path = column_mapper.get_field_value_from_source(entry, 'path')
        if path is None or path == '':
            continue

        ent1_start = column_mapper.get_field_value_from_source(entry, 'ent1_start', as_int=True)
        ent1_end = column_mapper.get_field_value_from_source(entry, 'ent1_end', as_int=True)
        ent1_indexes = [idx for idx in range(ent1_start, ent1_end + 1)]

        ent2_start = column_mapper.get_field_value_from_source(entry, 'ent2_start', as_int=True)
        ent2_end = column_mapper.get_field_value_from_source(entry, 'ent2_end', as_int=True)
        ent2_indexes = [idx for idx in range(ent2_start, ent2_end + 1)]

        filtered = False

        if entity_types is not None:

            entity1_type = entity_types[0]
            entity2_type = entity_types[1]

            ner_tags = column_mapper.get_field_value_from_source(entry, 'ner', evaluate=True)

            # let's see if any of entity 1's tokens match entity1_type
            entity1_type_match = False
            for ent1_index in ent1_indexes:
                if ent1_index in ner_tags and ner_tags[ent1_index] == entity1_type:
                    entity1_type_match = True
                    break

            entity2_type_match = False
            for ent2_index in ent2_indexes:
                if ent2_index in ner_tags and ner_tags[ent2_index] == entity2_type:
                    entity2_type_match = True
                    break

            filtered = not entity1_type_match or not entity2_type_match

        if not filtered:
            csv_writer.writerow(column_mapper.get_new_row_values(entry, []))

    output.close()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog='filter_relations',
        description="filter out relations that' don't match")

    arg_parser.add_argument(
        '--entity-types',
        nargs=2,
        metavar=('entity1-type', 'entity2-type'),
        help='When used this flag should be followed by two named entity types. When provided, the relation identification '
             'algorithm will filter out relations that are marked differently (unmarked relations will not be filtered out)')

    arg_parser.add_argument(
        '--input',
        action='store',
        metavar='input-file',
        help='When provided input will be read from this file rather than from standard input')

    arg_parser.add_argument(
        '--output',
        action='store',
        metavar='output-file',
        help='The comma-separated field output file (if not provided output will be sent to std output)')

    args = arg_parser.parse_args()

    input = open(args.input, encoding='utf-8') if args.input is not None else sys.stdin
    output = open(args.output, 'w', encoding='utf-8', newline='') if args.output is not None else sys.stdout

    filter_relations(input, output, args.entity_types)
