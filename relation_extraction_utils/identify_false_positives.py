import pandas as pd

from relation_extraction_utils.dep_graph import DepGraph
from relation_extraction_utils.link import Link

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


def filter_sen(data, trigger_list):
    """
    drop all rows that doesn't contains any trigger word
    """
    ##    data.drop(without_triggers(data, trigger_list), inplace=True)
    return data


def identify_false_positives(data, triggers, paths):
    indices = []

    for idx, row in data.iterrows():

        trigger = False
        # if 'he founded and directed the National Environmental Trust' in row.sentence:
        #    print('lets debug')

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

                trigger_to_ent2 = graph.get_steps(trigger_index, ent2_head)
                ent1_to_trigger = graph.get_steps(ent1_head, trigger_index)
                ent1_to_ent2_via_trigger = '{0} >< {1}'.format(ent1_to_trigger, trigger_to_ent2)

                if ent1_to_ent2_via_trigger in paths:
                    print('FALSE POSITIVE!!!!')
                    print("sentence: ", row.sentence)
                    print('trigger: {} (lemma: {})'.format(word, lemma))
                    print('ent1: {}'.format(' '.join([links[idx - 1].word for idx in ent1_indexes])))
                    print('ent2: {}'.format(' '.join([links[idx - 1].word for idx in ent2_indexes])))
                    print('path: ', ent1_to_ent2_via_trigger)
                    print()
                    wait_here = True


def main():
    # for creating a new triggers list:
    # print_triggers_oracle(args.relation)
    data = pd.read_csv(r'C:\Users\jyellin\Desktop\no-relation\no_relation5000-0.csv')

    identify_false_positives(data, FOUNDED_BY_TRIGGERS, FOUNDED_BY_FREQUENT_PATHS)

    wait_here = True
    # data.to_csv(args.output, index=False)


if __name__ == "__main__":
    main()
    # arg_parser = argparse.ArgumentParser(description="create list of trigger"
    #                                                 " words for a certain "
    #                                                 "relation")
    # arg_parser.add_argument("input", help="csv file to filter")
    # arg_parser.add_argument("-r", "--relation",
    #                        help="relation csv file for creating an oracle")
    # arg_parser.add_argument("-o", "--output", help="file after filtering")

    # main(arg_parser.parse_args())
