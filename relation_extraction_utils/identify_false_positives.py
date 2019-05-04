import argparse
import csv

import pandas as pd

from relation_extraction_utils.internal.dep_graph import DepGraph
from relation_extraction_utils.internal.link import Link
from relation_extraction_utils.internal.path_stats import PathStats

FOUNDED_BY_TRIGGERS = {
    'create',
    'find',
    'launch',
    'found',
    '\'s',
    'build',
    'her',
    'his',
    'co-founder',
    'start',
    'establish',
    'set',
    'founder',
    'set up',
    'form'}

FOUNDED_BY_FREQUENT_PATHS = {
    '↑nmod:poss ↑case >< ↓case',  # 10 appearances
    '↓nmod >< ↓appos',  # 7 appearances
    '↓obj >< ↑nsubj',  # 6 appearances
    '↓obj >< ↓conj ↑nsubj',  # 5 appearances
    '↑appos ↑acl >< ↑obl',
    '↓compound >< ↓compound',  # 4 appearances
    '↓obj >< ↓acl:relcl ↓appos',  # 3 appearances
    '↓obj >< ↓acl:relcl',
    '↓xcomp >< ↓acl',  # 2 appearances
    '↓obj >< ↓advcl ↑nsubj',
    '↓nsubj:pass >< ↑obl',
    '↓nmod ↑appos >< ↓appos',
    '↓nmod >< ↑nsubj',
    '↑nmod:poss ><',
    '↑appos ↑acl:relcl >< ↑nsubj',
    '↑acl:relcl >< ↑obl'}
"""
    
    '↓obl ↓acl:relcl ↑acl >< ↑obl,' # 1 appearance
    '↓obj >< ↓xcomp ↑nsubj,'
    '↓obj >< ↓conj ↓advcl ↑nsubj,'
    '↓obj >< ↓acl:relcl ↑appos,'
    '↓obj >< ↓acl ↓obj ↑nsubj,'
    '↓nsubj:pass ↓acl:relcl >< ↑acl:relcl ↑obl,'
    '↓nsubj:pass ↑advcl >< ↑obl,'
    '↓nsubj:pass >< ↑obl ↑nmod ↑conj ↑nmod,'
    '↓nsubj:pass >< ↑obl ↑acl ↑xcomp,'
    '↓nsubj ↓acl:relcl ↑nmod ↑nmod:poss ><,'
    '↓nsubj ↑obl ↑nmod ↑compound >< ↓compound,'
    '↓nsubj ↑obl >< ↑nmod,'
    '↓nsubj ↑ccomp ↑ccomp ↑obl ↑nmod ↑appos ><,'
    '↓nsubj ↑advcl >< ↑obl ↑flat,'
    '↓nsubj ↑advcl >< ↑obl,'
    '↓nsubj ↑acl >< ↑obl,'
    '↓nsubj >< ↑obl,'
    '↓nmod:poss ↑compound >< ↓compound ↑appos,'
    '↓nmod:poss >< ↓compound,'
    '↓nmod:poss >< ↓appos ↑appos,'
    '↓nmod:poss >< ↓appos,'
    '↓nmod ↓appos ↓nsubj ↑obj ↑nmod ↑compound ↑punct >< ↓punct ↓compound ↓nmod ↓obj ↑nsubj,'
    '↓nmod ↑nmod ↑acl:relcl >< ↓acl:relcl ↓nmod ↓obl ↑nsubj,'
    '↓nmod >< ↓acl:relcl,'
    '↓det ↑acl:relcl >< ↑obl,'
    '↓conj ↑nmod:poss ><,'
    '↓conj ↑conj ↑nmod:poss ><,'
    '↓compound ↓nmod >< ↓conj ↑appos ↑nmod,'
    '↓compound ↓nmod >< ↑nsubj,'
    '↓compound ↓compound ↓nmod >< ↓appos,'
    '↓compound ↓compound ↑nmod:poss ><,'
    '↓compound ↑nmod:poss ↑case >< ↓case,'
    '↓appos ↓nsubj:pass >< ↑obl ↑flat,'
    '↓appos ↑nmod:poss ↑case >< ↓case,'
    '↑nmod:poss ↑case >< ↓case ↓nmod:poss,'
    '↑nmod >< ↓nmod ↓appos,'
    '↑appos ↑acl:relcl >< ↓acl:relcl ↑acl:relcl ↑nsubj,'
    '↑appos ↑acl:relcl >< ↑obl ↑nmod,'
    '↑appos ↑acl >< ↑obl ↑flat,'
    '↑acl >< ↑advmod ↑obl'}
"""

FOUNDED_BY_FREQUENT_PATHS_WITH_PSS = {
    '↓nmod >< ↓appos',
    '↓obj >< ↑nsubj',
    '↓obj >< ↓conj↑nsubj',
    '↑appos↑acl >< ↑obl',
    '↓compound >< ↓compound',
    '↑nmod:poss↑case >< ↓case(SocialRel/Gestalt)',  # four appearances or more above here - three and two below
    '↓obj >< ↓acl:relcl↓appos',
    '↓obj >< ↓acl:relcl',
    '↑nmod:poss↑case >< ↓case(Agent/Gestalt)',
    '↓xcomp >< ↓acl',
    '↓obj >< ↓advcl↑nsubj',
    '↓nsubj:pass >< ↑obl',
    '↓nmod↑appos >< ↓appos',
    '↓nmod >< ↑nsubj',
    '↑nmod:poss >< ',
    '↑appos↑acl:relcl >< ↑nsubj',
    '↑acl:relcl >< ↑obl'}


def identify_false_positives(input_files, output_file):
    # See here for guidance on how to get the encoding right (as we need to deal with the '↑' and '↓' characters
    # https://stackoverflow.com/questions/6493876/python-save-csv-file-in-utf-16le

    with open(output_file, 'w', encoding='utf_16', newline='') as f:
        csv_out = csv.writer(f, delimiter='\t')

        csv_out.writerow(['sentence', 'trigger', 'matched-lemma', 'ent1', 'ent2', 'path',
                          'trigger_idx', 'ent1_start', 'ent1_end', 'ent2_start', 'ent2_end',
                          'dependency_parse', 'lemmas'])

        for input_file in input_files:
            print('processing ', input_file)
            input_rows = pd.read_csv(input_file)
            __identify_matches(input_rows, csv_out, FOUNDED_BY_TRIGGERS, FOUNDED_BY_FREQUENT_PATHS)


def __identify_matches(input_rows, csv_out, triggers, paths):
    for idx, row in input_rows.iterrows():

        dependency_parse = eval(row['dependency_parse'])
        links = Link.get_links(dependency_parse)

        print(row.sentence)
        if 'Freedom was founded in the 1930s by RC' in row.sentence:
            print('break here')

        lemma_indices = eval(row['lemmas'])
        lemmas = [lemma for _, lemma in lemma_indices]

        for link in links:

            trigger_index = link.word_index
            word = link.word
            lemma = lemmas[trigger_index - 1]

            if word in triggers or lemma in triggers:

                ent1_indexes = [idx for idx in range(int(row.ent1_start), int(row.ent1_end) + 1)]
                ent1_head = Link.get_head(links, ent1_indexes)

                ent2_indexes = [idx for idx in range(int(row.ent2_start), int(row.ent2_end) + 1)]
                ent2_head = Link.get_head(links, ent2_indexes)

                graph = DepGraph(links)
                pss_tags = None  # SyncPssTags.get_pss_tags_by_index(row)

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

                    ent1 = ' '.join([links[idx - 1].word for idx in ent1_indexes])
                    ent2 = ' '.join([links[idx - 1].word for idx in ent2_indexes])

                    csv_out.writerow([row.sentence, trigger, matched_lemma, ent1, ent2, ent1_to_ent2_via_trigger,
                                      trigger_index, row.ent1_start, row.ent1_end, row.ent2_start, row.ent2_end,
                                      row.dependency_parse, row.lemmas])

                    print("sentence: ", row.sentence)
                    print('trigger: {} (lemma: {})'.format(word, lemma))
                    print('ent1: {}'.format(ent1))
                    print('ent2: {}'.format(ent2))
                    print('path: ', ent1_to_ent2_via_trigger)
                    print()



if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="identify relationships in input csv file "
                                                     "that match given paths and trigger words "
                                                     "(and as such can be viewed as false positives) "
                                                     "NOTE: the paths and trigger words are currently "
                                                     "hardcoded in the module")

    arg_parser.add_argument('false_positive_output_file',
                            metavar='false-positive-output-file',
                            help="path of the csv to contain false positives")

    arg_parser.add_argument('relation_input_files',
                            metavar='csv-input-files',
                            nargs='+',
                            help="paths of one or more csv file containing relations to analyze")

    args = arg_parser.parse_args()

    identify_false_positives(args.relation_input_files, args.false_positive_output_file)
