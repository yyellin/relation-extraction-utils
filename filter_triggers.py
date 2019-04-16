import pandas as pd
import argparse
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
from itertools import zip_longest


nlp = spacy.load("en_core_web_lg")
lm = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)
print("Done loading.\n")


FOUNDED_BY_TRIGGERS = {'create', 'find', 'launch', 'found', '\'s', 'build',
                       'her', 'his', 'co-founder', 'start', 'establish', 'set',
                       'founder', 'set up', 'form'}


def print_triggers_oracle(file_name):
    """
    create a trigger oracle.
    """
    data = pd.read_csv(file_name)
    data.dropna(inplace=True)
    trigger_words = set()
    for trigger, sen, index in zip_longest(data.trigger, data.sentence,
                                           data.trigger_idx):
        doc = nlp(sen)
        index = min(max(int(index) - 1, 0), len(doc) - 1)
        if doc[index].text == trigger:
            trigger_words.add((doc[index]).lemma_)
        else:  # in case there is a different in the parsing:
            trigger_words.add(lm(trigger, "verb")[0])
    print(trigger_words)
    return trigger_words


def filter_sen(data, trigger_list):
    """
    drop all rows that doesn't contains any trigger word
    """
    data.drop(without_triggers(data, trigger_list),
              inplace=True)
    return data


def without_triggers(data, trigger_list):
    indices = []
    for idx, row in data.iterrows():
        doc = nlp(row["sentence"])
        trigger = False
        for token in doc:
            if (token.lemma_ in trigger_list) or (token.text in trigger_list):
                trigger = True
                break
        if not trigger:
            indices.append(idx)
    return indices


def main(args):
    # for creating a new triggers list:
    # print_triggers_oracle(args.relation)
    data = pd.read_csv(args.input)
    data = filter_sen(data, FOUNDED_BY_TRIGGERS)
    data.to_csv(args.output, index=False)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="create list of trigger"
                                                     " words for a certain "
                                                     "relation")
    arg_parser.add_argument("input", help="csv file to filter")
    arg_parser.add_argument("-r", "--relation",
                            help="relation csv file for creating an oracle")
    arg_parser.add_argument("-o", "--output", help="file after filtering")
    main(arg_parser.parse_args())
