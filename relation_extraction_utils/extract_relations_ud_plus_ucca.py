import argparse
import csv
import sys
from collections import namedtuple
from itertools import product

from relation_extraction_utils.internal.dep_graph import Step, DepGraph
from relation_extraction_utils.internal.link import Link
from relation_extraction_utils.internal.map_csv_column import CsvColumnMapper
from relation_extraction_utils.internal.ucca_types import UccaParsedPassage
from relation_extraction_utils.internal.ud_types import UdRepresentationPlaceholder


class Match(namedtuple('Match', 'path, trigger, trigger_index')):
    """
    An object of type Match is a tuple containing the path and trigger word for
    a relation-extraction match
    """


def __extract_relation_ucca(ucca_entry, ucca_paths, ucca_column_mapper, triggers):
    ucca_parse_serialization = ucca_column_mapper.get_field_value_from_source(ucca_entry, 'ucca_parse')
    if ucca_parse_serialization is None or ucca_parse_serialization == "":
        return None

    ucca_parse = UccaParsedPassage.from_serialization(ucca_parse_serialization)
    links = ucca_parse.get_links()

    ent1_start_token_id = ucca_column_mapper.get_field_value_from_source(ucca_entry, 'ent1_start', as_int=True)
    ent2_start_token_id = ucca_column_mapper.get_field_value_from_source(ucca_entry, 'ent2_start', as_int=True)

    if ent1_start_token_id is None or ent2_start_token_id is None:
        return None

    ent1_start_node_id = ucca_parse.get_node_id_by_token_id(ent1_start_token_id)
    ent1_parent_node_ids = Link.get_parents(links, ent1_start_node_id)
    if len(ent1_parent_node_ids) == 0:
        return None
    ent1_parent_node_id = ent1_parent_node_ids[0]

    ent2_start_node_id = ucca_parse.get_node_id_by_token_id(ent2_start_token_id)
    ent2_parent_node_ids = Link.get_parents(links, ent2_start_node_id)
    if len(ent2_parent_node_ids) == 0:
        return None
    ent2_parent_node_id = ent2_parent_node_ids[0]

    graph = DepGraph(links)

    lemma_with_indices = ucca_column_mapper.get_field_value_from_source(ucca_entry, 'lemmas', evaluate=True)
    lemmas = [lemma for _, lemma in lemma_with_indices]

    words_with_indices = ucca_column_mapper.get_field_value_from_source(ucca_entry, 'words', evaluate=True)
    words = [word for _, word in words_with_indices]

    for trigger_index, (word, lemma) in enumerate(zip(words, lemmas), start=1):

        if word in triggers or lemma in triggers:

            trigger_node_id = ucca_parse.get_node_id_by_token_id(trigger_index)
            trigger_parent_node_id = Link.get_parents(links, trigger_node_id)[0]

            ent1_to_trigger_steps = graph.get_steps(ent1_parent_node_id, trigger_parent_node_id)
            ent1_to_trigger_strings = ucca_parse.get_path_representations(ent1_to_trigger_steps)

            trigger_to_ent2_steps = graph.get_steps(trigger_parent_node_id, ent2_parent_node_id)
            trigger_to_ent2_strings = ucca_parse.get_path_representations(trigger_to_ent2_steps)

            for segment1, segment2 in product(ent1_to_trigger_strings, trigger_to_ent2_strings):

                ent1_to_ent2_via_trigger = '{0} >< {1}'.format(segment1, segment2)

                if ent1_to_ent2_via_trigger in ucca_paths:
                    return Match(path=ent1_to_ent2_via_trigger, trigger=word, trigger_index=trigger_index)


def __extract_relation_ud(ud_entry, ud_paths, ud_column_mapper, triggers):
    ud_parse = ud_column_mapper.get_field_value_from_source(ud_entry, 'ud_parse', evaluate=True)
    if ud_parse is None:
        return None

    links = UdRepresentationPlaceholder.get_links_from_ud_dep(ud_parse)

    lemma_with_indices = ud_column_mapper.get_field_value_from_source(ud_entry, 'lemmas', evaluate=True)
    lemmas = [lemma for _, lemma in lemma_with_indices]

    words_with_indices = ud_column_mapper.get_field_value_from_source(ud_entry, 'words', evaluate=True)
    words = [word for _, word in words_with_indices]

    ent1_start = ud_column_mapper.get_field_value_from_source(ud_entry, 'ent1_start', as_int=True)
    ent1_end = ud_column_mapper.get_field_value_from_source(ud_entry, 'ent1_end', as_int=True)
    if ent1_start is None or ent1_end is None:
        return None
    ent1_indexes = [idx for idx in range(ent1_start, ent1_end + 1)]
    ent1_head = Link.get_head(links, ent1_indexes)

    ent2_start = ud_column_mapper.get_field_value_from_source(ud_entry, 'ent2_start', as_int=True)
    ent2_end = ud_column_mapper.get_field_value_from_source(ud_entry, 'ent2_end', as_int=True)
    if ent2_start is None or ent2_end is None:
        return None

    ent2_indexes = [idx for idx in range(ent2_start, ent2_end + 1)]
    ent2_head = Link.get_head(links, ent2_indexes)

    graph = DepGraph(links)

    for trigger_index, (word, lemma) in enumerate(zip(words, lemmas), start=1):

        # For some reason we're seeing words with apostrophe s sometimes being parsed into 3 tokens: (1) word itself;
        # (2) the ' sign; (3) 's.
        # The problem is that the lemma of the second token is for some reason 's

        if word in triggers or lemma in triggers:

            trigger_to_ent2 = Step.get_default_representation(graph.get_steps(trigger_index, ent2_head))
            ent1_to_trigger = Step.get_default_representation(graph.get_steps(ent1_head, trigger_index))
            ent1_to_ent2_via_trigger = '{0} >< {1}'.format(ent1_to_trigger, trigger_to_ent2)

            if ent1_to_ent2_via_trigger in ud_paths:
                return Match(path=ent1_to_ent2_via_trigger, trigger=word, trigger_index=trigger_index)


def extract_relations(output, ud_input, ud_paths, ucca_input, ucca_paths, triggers):
    def get_output_entry_list(
            id,
            sentence,
            ud_words='',
            ud_lemmas='',
            ud_parse='',
            ucca_words='',
            ucca_lemmas='',
            ucca_parse='',
            ud_trigger='',
            ud_path='',
            ucca_trigger='',
            ucca_path='',
            comment=''):

        return [id,
                sentence,
                ud_words,
                ud_lemmas,
                ud_parse,
                ucca_words,
                ucca_lemmas,
                ucca_parse,
                ud_trigger,
                ud_path,
                ucca_trigger,
                ucca_path,
                comment]

    csv_writer = csv.writer(output)

    csv_writer.writerow([
        'id',
        'sentence',
        'ud_words',
        'ud_lemmas',
        'ud_parse',
        'ucca_words',
        'ucca_lemmas',
        'ucca_parse',
        'ud_trigger',
        'ud_path',
        'ucca_trigger',
        'ucca_path',
        'comment'])

    ud_reader = csv.reader(ud_input)
    ucca_reader = csv.reader(ucca_input)

    ud_column_mapper = CsvColumnMapper(
        source_first_row=next(ud_reader),
        target_columns=['trigger', 'trigger_idx', 'matched-lemma', 'path'],
        source_required=['sentence', 'ud_parse', 'lemmas', 'ent1_start', 'ent1_end', 'ent2_start', 'ent2_end'])

    ucca_column_mapper = CsvColumnMapper(
        source_first_row=next(ucca_reader),
        target_columns=['trigger', 'trigger_idx', 'matched-lemma', 'path'],
        source_required=['sentence', 'ucca_parse', 'lemmas', 'ent1_start', 'ent1_end', 'ent2_start', 'ent2_end']
    )

    ucca_entry_lookup = {}
    for ucca_row in ucca_reader:
        id = ucca_column_mapper.get_field_value_from_source(ucca_row, 'id', as_int=True)
        ucca_entry_lookup[id] = ucca_row

    for ud_row in ud_reader:
        id = ud_column_mapper.get_field_value_from_source(ud_row, 'id', as_int=True)
        sentence = ud_column_mapper.get_field_value_from_source(ud_row, 'sentence')

        ucca_row = ucca_entry_lookup.get(id)
        if ucca_row is None:
            csv_writer.writerow(get_output_entry_list(id, sentence, comment='No matching UCCA row'))
            continue

        ud_words = ud_column_mapper.get_field_value_from_source(ud_row, 'words')
        ud_lemmas = ud_column_mapper.get_field_value_from_source(ud_row, 'lemmas')
        ud_parse = ud_column_mapper.get_field_value_from_source(ud_row, 'ud_parse')
        ud_match = __extract_relation_ud(ud_row, ud_paths, ud_column_mapper, triggers)
        ud_trigger = ud_match.trigger if ud_match is not None else None
        ud_path = ud_match.path if ud_match is not None else None

        ucca_words = ucca_column_mapper.get_field_value_from_source(ucca_row, 'words')
        ucca1_lemmas = ucca_column_mapper.get_field_value_from_source(ucca_row, 'lemmas')
        ucca_parse = ucca_column_mapper.get_field_value_from_source(ucca_row, 'ucca_parse')
        ucca_match = __extract_relation_ucca(ucca_row, ucca_paths, ucca_column_mapper, triggers)
        ucca_trigger = ucca_match.trigger if ucca_match is not None else None
        ucca_path = ucca_match.path if ucca_match is not None else None

        csv_writer.writerow(
            get_output_entry_list(id,
                                  sentence,
                                  ud_words=ud_words,
                                  ud_lemmas=ud_lemmas,
                                  ud_parse=ud_parse,
                                  ucca_words=ucca_words,
                                  ucca_lemmas=ucca1_lemmas,
                                  ucca_parse=ucca_parse,
                                  ud_trigger=ud_trigger,
                                  ud_path=ud_path,
                                  ucca_trigger=ucca_trigger,
                                  ucca_path=ucca_path
                                  ))

        # if ud_match is not None and ucca_match is None:
        #     print('Sentence {} only matched in UD'.format(id))
        #     print('Trigger: {}'.format(ud_match.trigger))
        #     print('UD Path: {}'.format(ud_match.path))
        #     print('\t{}'.format(ud_column_mapper.get_field_value_from_source(ud_row, 'sentence')))
        #     print()
        #
        # elif ud_match is None and ucca_match is not None:
        #     print('Sentence {} only matched in UCCA'.format(id))
        #     print('\tTrigger: {}'.format(ucca_match.trigger))
        #     print('\tUD Path: {}'.format(ucca_match.path))
        #     print('\tSentence: {}'.format(ud_column_mapper.get_field_value_from_source(ud_row, 'sentence')))
        #     print()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog='compare_ud_ucca_extraction',
        description="analyzes differences between UD and UCCA relation extraction success")

    arg_parser.add_argument(
        'ud_input',
        action='store',
        metavar='ud-input-file',
        help='file containing sentences with their UD parse representation')

    arg_parser.add_argument(
        'ud_paths',
        action='store',
        metavar='ud-paths-file',
        help='File containing list of UD paths (each path on separate line)')

    arg_parser.add_argument(
        'ucca_input',
        action='store',
        metavar='ucca-input-file',
        help='file containing sentences with their UCCA parse representation')

    arg_parser.add_argument(
        'ucca_paths',
        action='store',
        metavar='ucca-paths-file',
        help='File containing list of UCCA paths (each path on separate line)')

    arg_parser.add_argument(
        'triggers',
        action='store',
        metavar='triggers-file',
        help='File containing list of trigger words (each trigger word on separate line)')

    arg_parser.add_argument(
        '--output',
        action='store',
        metavar='output-file',
        help='The comma-separated field output file (if not provided output will be sent to std output)')

    args = arg_parser.parse_args()

    ud_input = open(args.ud_input, encoding='utf-8')
    ucca_input = open(args.ucca_input, encoding='utf-8')

    triggers = set([line.rstrip('\n') for line in open(args.triggers)])
    ud_paths = set([line.rstrip('\n') for line in open(args.ud_paths)])
    ucca_paths = set([line.rstrip('\n') for line in open(args.ucca_paths)])

    output = open(args.output, 'w', encoding='utf-8', newline='') if args.output is not None else sys.stdout

    extract_relations(output, ud_input, ud_paths, ucca_input, ucca_paths, triggers)
