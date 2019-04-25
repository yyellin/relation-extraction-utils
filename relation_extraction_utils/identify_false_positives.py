import argparse
import csv

import pandas as pd

from relation_extraction_utils.internal.dep_graph import DepGraph
from relation_extraction_utils.internal.link import Link
from relation_extraction_utils.internal.path_stats import PathStats

FOUNDED_BY_TRIGGERS = {'create',
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

FOUNDED_BY_FREQUENT_PATHS = {'↑nmod:poss ↑case >< ↓case',
                             '↓nmod >< ↓appos',
                             '↓obj >< ↑nsubj',
                             '↓obj >< ↓conj ↑nsubj',
                             '↑appos ↑acl >< ↑obl',
                             '↓compound >< ↓compound',  # four appearences or more above here - three or less below
                             '↓obj >< ↓acl:relcl ↓appos',
                             '↓obj >< ↓acl:relcl',
                             '↓xcomp >< ↓acl',
                             '↓obj >< ↓advcl ↑nsubj',
                             '↓nsubj:pass >< ↑obl',
                             '↓nmod ↑appos >< ↓appos',
                             '↓nmod >< ↑nsubj',
                             '↑nmod:poss ><',
                             '↑appos ↑acl:relcl >< ↑nsubj',
                             '↑acl:relcl >< ↑obl'}


def identify_false_positives(input_files, output_file):
    # See here for guidance on how to get the encoding right (as we need to deal with the '↑' and '↓' characters
    # https://stackoverflow.com/questions/6493876/python-save-csv-file-in-utf-16le

    with open(output_file, 'w', encoding='utf_16', newline='') as f:
        csv_out = csv.writer(f, delimiter='\t')

        csv_out.writerow(['sentence', 'trigger', 'matched-lemma', 'ent1', 'ent2', 'path'])

        for input_file in input_files:
            print('processing ', input_file)
            input_rows = pd.read_csv(input_file)
            __identify_matches(input_rows, csv_out, FOUNDED_BY_TRIGGERS, FOUNDED_BY_FREQUENT_PATHS)


def __identify_matches(input_rows, csv_out, triggers, paths):
    for idx, row in input_rows.iterrows():

        dependency_parse = eval(row['dependency_parse'])
        links = Link.get_links(dependency_parse)

        lemma_indices = eval(row['lemmas'])
        lemmas = [lemma for _, lemma in lemma_indices]

        for link in links:

            trigger_index = link.word_index
            word = link.word
            lemma = lemmas[trigger_index - 1]

            if word in triggers or lemma in triggers:

                ent1_indexes = [idx + 1 for idx in range(int(row.ent1_start), int(row.ent1_end) + 1)]
                ent1_head = Link.get_head(links, ent1_indexes)

                ent2_indexes = [idx + 1 for idx in range(int(row.ent2_start), int(row.ent2_end) + 1)]
                ent2_head = Link.get_head(links, ent2_indexes)

                graph = DepGraph(links)

                trigger_to_ent2 = PathStats.get_steps_as_string(graph.get_steps(trigger_index, ent2_head))
                ent1_to_trigger = PathStats.get_steps_as_string(graph.get_steps(ent1_head, trigger_index))
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

                    csv_out.writerow([row.sentence, trigger, matched_lemma, ent1, ent2, ent1_to_ent2_via_trigger])
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
