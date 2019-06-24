import argparse
import csv
import sys
from itertools import product

from relation_extraction_utils.internal.dep_graph import DepGraph
from relation_extraction_utils.internal.link import Link
from relation_extraction_utils.internal.map_csv_column import CsvColumnMapper
from relation_extraction_utils.internal.ucca_types import UccaParsedPassage


def extract_relations_ucca(input, output, triggers, paths, entity_types=None):
    csv_reader = csv.reader(input)
    csv_writer = csv.writer(output)

    required_columns = ['sentence', 'ucca_parse', 'lemmas', 'ent1_start', 'ent1_end', 'ent2_start', 'ent2_end']

    if entity_types is not None:
        required_columns.append('ner')

    column_mapper = CsvColumnMapper(next(csv_reader), ['trigger', 'trigger_idx', 'matched-lemma', 'path'],
                                    source_required=required_columns)

    csv_writer.writerow(column_mapper.get_new_headers())

    for counter, entry in enumerate(csv_reader, start=1):

        sentence_id = column_mapper.get_field_value_from_source(entry, 'id', as_int=True)

        ucca_parse_serialization = column_mapper.get_field_value_from_source(entry, 'ucca_parse')
        if ucca_parse_serialization is None or ucca_parse_serialization == "":
            csv_writer.writerow(column_mapper.get_new_row_values(entry, [None, None, 'ucca_parse missing']))
            print('skip')
            continue

        ucca_parse = UccaParsedPassage.from_serialization(ucca_parse_serialization)
        links = ucca_parse.get_links()

        ent1_start_token_id = column_mapper.get_field_value_from_source(entry, 'ent1_start', as_int=True)
        ent2_start_token_id = column_mapper.get_field_value_from_source(entry, 'ent2_start', as_int=True)

        if ent1_start_token_id is None or ent2_start_token_id is None:
            csv_writer.writerow(column_mapper.get_new_row_values(entry, [None, None, 'indices missing']))
            print('skip')
            continue

        ent1_start_node_id = ucca_parse.get_node_id_by_token_id(ent1_start_token_id)
        ent1_parent_node_ids = Link.get_parents(links, ent1_start_node_id)
        if len(ent1_parent_node_ids) == 0:
            csv_writer.writerow(column_mapper.get_new_row_values(entry, [None, None, 'Could not find parent of ent1']))
            print('skip')
            continue
        ent1_parent_node_id = ent1_parent_node_ids[0]

        ent2_start_node_id = ucca_parse.get_node_id_by_token_id(ent2_start_token_id)
        ent2_parent_node_ids = Link.get_parents(links, ent2_start_node_id)
        if len(ent2_parent_node_ids) == 0:
            csv_writer.writerow(column_mapper.get_new_row_values(entry, [None, None, 'Could not find parent of ent2']))
            print('skip')
            continue
        ent2_parent_node_id = ent2_parent_node_ids[0]

        graph = DepGraph(links)

        lemma_with_indices = column_mapper.get_field_value_from_source(entry, 'lemmas', evaluate=True)
        lemmas = [lemma for _, lemma in lemma_with_indices]

        words_with_indices = column_mapper.get_field_value_from_source(entry, 'words', evaluate=True)
        words = [word for _, word in words_with_indices]

        found_trigger = False

        for trigger_index, (word, lemma) in enumerate(zip(words, lemmas), start=1):

            if sentence_id == 7 and trigger_index == 13:
                print('wait here')

            # For some reason we're seeing words with apostrophe s sometimes being parsed into 3 tokens: (1) word itself;
            # (2) the ' sign; (3) 's.
            # The problem is that the lemma of the second token is for some reason 's

            if word in triggers or lemma in triggers:

                found_trigger = True
                trigger_node_id = ucca_parse.get_node_id_by_token_id(trigger_index)
                trigger_parent_node_id = Link.get_parents(links, trigger_node_id)[0]

                ent1_to_trigger_steps = graph.get_steps(ent1_parent_node_id, trigger_parent_node_id)
                ent1_to_trigger_strings = ucca_parse.get_path_representations(ent1_to_trigger_steps)

                trigger_to_ent2_steps = graph.get_steps(trigger_parent_node_id, ent2_parent_node_id)
                trigger_to_ent2_strings = ucca_parse.get_path_representations(trigger_to_ent2_steps)

                for segment1, segment2 in product(ent1_to_trigger_strings, trigger_to_ent2_strings):

                    ent1_to_ent2_via_trigger = '{0} >< {1}'.format(segment1, segment2)

                    if ent1_to_ent2_via_trigger in paths:

                        if word in triggers:
                            trigger = word
                            matched_lemma = False
                        else:
                            trigger = lemma
                            matched_lemma = True

                        csv_writer.writerow(
                            column_mapper.get_new_row_values(entry, [trigger, trigger_index, matched_lemma,
                                                                     ent1_to_ent2_via_trigger]))
                        break

                    # else:
                    #     print('Sentence {}, bad path: {}'.format(sentence_id, ent1_to_ent2_via_trigger))
                    #     print( column_mapper.get_field_value_from_source(entry, 'sentence' ) )
                    #     print()

        if not found_trigger:
            print('no trigger found')

    output.close()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog='extract_relations',
        description="identify relationships that match given UCCA paths and trigger words")

    arg_parser.add_argument(
        'paths',
        action='store',
        metavar='paths-file',
        help='File containing list of paths (each path on separate line)')

    arg_parser.add_argument(
        'triggers',
        action='store',
        metavar='triggers-file',
        help='File containing list of trigger words (each trigger word on separate line)')

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
    triggers = set([line.rstrip('\n') for line in open(args.triggers)])
    paths = set([line.rstrip('\n') for line in open(args.paths)])

    extract_relations_ucca(input, output, triggers, paths)
