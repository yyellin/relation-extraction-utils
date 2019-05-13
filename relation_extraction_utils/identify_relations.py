import argparse
import csv

from relation_extraction_utils.internal.dep_graph import DepGraph
from relation_extraction_utils.internal.file_type_util import FileTypeUtil
from relation_extraction_utils.internal.link import Link
from relation_extraction_utils.internal.map_csv_column import CsvColumnMapper
from relation_extraction_utils.internal.path_stats import PathStats


def identify_relations(input_file, output_file, trigger_file, path_file, entity_types=None):
    input_encoding = FileTypeUtil.determine_encoding(args.input)
    input = open(input_file, encoding=input_encoding, newline='')
    csv_reader = csv.reader(input, delimiter=',')

    output = open(output_file, 'w', encoding='utf_16', newline='')
    csv_writer = csv.writer(output, delimiter='\t')

    triggers = set([line.rstrip('\n') for line in open(trigger_file)])
    paths = set([line.rstrip('\n') for line in open(path_file, encoding='utf-8')])

    required_columns = ['sentence', 'ud_parse', 'lemmas', 'ent1_start', 'ent1_end', 'ent2_start', 'ent2_end']

    if entity_types is not None:
        required_columns.append('ner')

    column_mapper = CsvColumnMapper(next(csv_reader), ['trigger', 'trigger_idx', 'matched-lemma', 'path'],
                                    source_required=required_columns)

    csv_writer.writerow(column_mapper.get_new_headers())

    for counter, entry in enumerate(csv_reader, start=1):

        print('#{}: {}'.format(counter, column_mapper.get_field_value_from_source(entry, 'sentence')))

        ud_parse = column_mapper.get_field_value_from_source(entry, 'ud_parse', evaluate=True)
        if ud_parse is None:
            continue

        links = Link.get_links(ud_parse)

        lemma_indices = column_mapper.get_field_value_from_source(entry, 'lemmas', evaluate=True)
        lemmas = [lemma for _, lemma in lemma_indices]

        ent1_start = int(column_mapper.get_field_value_from_source(entry, 'ent1_start'))
        ent1_end = int(column_mapper.get_field_value_from_source(entry, 'ent1_end'))
        ent1_indexes = [idx for idx in range(ent1_start, ent1_end + 1)]
        ent1_head = Link.get_head(links, ent1_indexes)

        ent2_start = int(column_mapper.get_field_value_from_source(entry, 'ent2_start'))
        ent2_end = int(column_mapper.get_field_value_from_source(entry, 'ent2_end'))
        ent2_indexes = [idx for idx in range(ent2_start, ent2_end + 1)]
        ent2_head = Link.get_head(links, ent2_indexes)

        graph = DepGraph(links)

        # pss_index_lookup = {tuple[0]: tuple[1] for tuple in eval(row.pss_index_lookup)}
        # pss_positive_lookup = eval(row.pss_parse)
        # pss_tags = SyncPssTags.get_pss_tags_by_index(index_lookup, pss_index_lookup, pss_positive_lookup)
        pss_tags = None  # SyncPssTags.get_pss_tags_by_index(row)

        if entity_types is not None:
            ner_tags = column_mapper.get_field_value_from_source(entry, 'ner', evaluate=True)

            if ent1_head in ner_tags and ner_tags[ent1_head] != entity_types[0]:
                print('amazing (1)!!')
                continue

            if ent2_head in ner_tags and ner_tags[ent2_head] != entity_types[1]:
                print('amazing (2)!!')
                continue

            wait_here = True

        for link in links:

            trigger_index = link.word_index
            word = link.word
            lemma = lemmas[trigger_index - 1]

            # For some reason we're seeing words with apostrophe s sometimes being parsed into 3 tokens: (1) word itself;
            # (2) the ' sign; (3) 's.
            # The problem is that the lemma of the second token is for some reason 's

            if word in triggers or lemma in triggers:

                trigger_to_ent2 = PathStats.get_steps_as_string(graph.get_steps(trigger_index, ent2_head), pss_tags)
                ent1_to_trigger = PathStats.get_steps_as_string(graph.get_steps(ent1_head, trigger_index), pss_tags)
                ent1_to_ent2_via_trigger = '{0} >< {1}'.format(ent1_to_trigger, trigger_to_ent2)

                if ent1_to_ent2_via_trigger in paths:

                    if word in triggers:
                        trigger = word
                        matched_lemma = False
                    else:
                        trigger = lemma
                        matched_lemma = True

                    print('   trigger: {}'.format(trigger))
                    csv_writer.writerow(column_mapper.get_new_row_values(entry, [trigger, trigger_index, matched_lemma,
                                                                                 ent1_to_ent2_via_trigger]))
                    break

    output.close()




if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        prog='identify_relations',
        description="identify relationships that match given paths and trigger words")

    arg_parser.add_argument(
        'output',
        action='store',
        metavar='output-file',
        help='The comma-separated field output file')

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
        '--input',
        action='store',
        metavar='input-file',
        help='When provided input will be read from this file rather than from standard input')

    arg_parser.add_argument(
        '--entity-types',
        nargs=2,
        metavar=('entity1-type', 'entity2-type'),
        help='When used this flag should be followed by two named entity types. When provided, the relation identification '
             'algorithm will filter out relations that are marked differently (unmarked relations will not be filtered out)')


    args = arg_parser.parse_args()

    identify_relations(args.input, args.output, args.triggers, args.paths)  # , args.entity_types )

# FOUNDED_BY_TRIGGERS = {
#     'create',
#     'find',
#     'launch',
#     'found',
#     '\'s',
#     'build',
#     'her',
#     'his',
#     'co-founder',
#     'start',
#     'establish',
#     'set',
#     'founder',
#     'set up',
#     'form'}
#
# FOUNDED_BY_FREQUENT_PATHS = {
#     '↑nmod:poss ↑case >< ↓case',  # 10 appearances
#     '↓nmod >< ↓appos',  # 7 appearances
#     '↓obj >< ↑nsubj',  # 6 appearances
#     '↓obj >< ↓conj ↑nsubj',  # 5 appearances
#     '↑appos ↑acl >< ↑obl',
#     '↓compound >< ↓compound',  # 4 appearances
#     '↓obj >< ↓acl:relcl ↓appos',  # 3 appearances
#     '↓obj >< ↓acl:relcl',
#     '↓xcomp >< ↓acl',  # 2 appearances
#     '↓obj >< ↓advcl ↑nsubj',
#     '↓nsubj:pass >< ↑obl',
#     '↓nmod ↑appos >< ↓appos',
#     '↓nmod >< ↑nsubj',
#     '↑nmod:poss ><',
#     '↑appos ↑acl:relcl >< ↑nsubj',
#     '↑acl:relcl >< ↑obl'}
# """
#
#     '↓obl ↓acl:relcl ↑acl >< ↑obl,' # 1 appearance
#     '↓obj >< ↓xcomp ↑nsubj,'
#     '↓obj >< ↓conj ↓advcl ↑nsubj,'
#     '↓obj >< ↓acl:relcl ↑appos,'
#     '↓obj >< ↓acl ↓obj ↑nsubj,'
#     '↓nsubj:pass ↓acl:relcl >< ↑acl:relcl ↑obl,'
#     '↓nsubj:pass ↑advcl >< ↑obl,'
#     '↓nsubj:pass >< ↑obl ↑nmod ↑conj ↑nmod,'
#     '↓nsubj:pass >< ↑obl ↑acl ↑xcomp,'
#     '↓nsubj ↓acl:relcl ↑nmod ↑nmod:poss ><,'
#     '↓nsubj ↑obl ↑nmod ↑compound >< ↓compound,'
#     '↓nsubj ↑obl >< ↑nmod,'
#     '↓nsubj ↑ccomp ↑ccomp ↑obl ↑nmod ↑appos ><,'
#     '↓nsubj ↑advcl >< ↑obl ↑flat,'
#     '↓nsubj ↑advcl >< ↑obl,'
#     '↓nsubj ↑acl >< ↑obl,'
#     '↓nsubj >< ↑obl,'
#     '↓nmod:poss ↑compound >< ↓compound ↑appos,'
#     '↓nmod:poss >< ↓compound,'
#     '↓nmod:poss >< ↓appos ↑appos,'
#     '↓nmod:poss >< ↓appos,'
#     '↓nmod ↓appos ↓nsubj ↑obj ↑nmod ↑compound ↑punct >< ↓punct ↓compound ↓nmod ↓obj ↑nsubj,'
#     '↓nmod ↑nmod ↑acl:relcl >< ↓acl:relcl ↓nmod ↓obl ↑nsubj,'
#     '↓nmod >< ↓acl:relcl,'
#     '↓det ↑acl:relcl >< ↑obl,'
#     '↓conj ↑nmod:poss ><,'
#     '↓conj ↑conj ↑nmod:poss ><,'
#     '↓compound ↓nmod >< ↓conj ↑appos ↑nmod,'
#     '↓compound ↓nmod >< ↑nsubj,'
#     '↓compound ↓compound ↓nmod >< ↓appos,'
#     '↓compound ↓compound ↑nmod:poss ><,'
#     '↓compound ↑nmod:poss ↑case >< ↓case,'
#     '↓appos ↓nsubj:pass >< ↑obl ↑flat,'
#     '↓appos ↑nmod:poss ↑case >< ↓case,'
#     '↑nmod:poss ↑case >< ↓case ↓nmod:poss,'
#     '↑nmod >< ↓nmod ↓appos,'
#     '↑appos ↑acl:relcl >< ↓acl:relcl ↑acl:relcl ↑nsubj,'
#     '↑appos ↑acl:relcl >< ↑obl ↑nmod,'
#     '↑appos ↑acl >< ↑obl ↑flat,'
#     '↑acl >< ↑advmod ↑obl'}
# """
#
# FOUNDED_BY_FREQUENT_PATHS_WITH_PSS = {
#     '↓nmod >< ↓appos',
#     '↓obj >< ↑nsubj',
#     '↓obj >< ↓conj↑nsubj',
#     '↑appos↑acl >< ↑obl',
#     '↓compound >< ↓compound',
#     '↑nmod:poss↑case >< ↓case(SocialRel/Gestalt)',  # four appearances or more above here - three and two below
#     '↓obj >< ↓acl:relcl↓appos',
#     '↓obj >< ↓acl:relcl',
#     '↑nmod:poss↑case >< ↓case(Agent/Gestalt)',
#     '↓xcomp >< ↓acl',
#     '↓obj >< ↓advcl↑nsubj',
#     '↓nsubj:pass >< ↑obl',
#     '↓nmod↑appos >< ↓appos',
#     '↓nmod >< ↑nsubj',
#     '↑nmod:poss >< ',
#     '↑appos↑acl:relcl >< ↑nsubj',
#     '↑acl:relcl >< ↑obl'}
#
#    input_rows = pd.read_csv(sys.stdin if input_file is None else input_file)
#    input_rows.dropna(subset=['ud_parse'], inplace=True)
