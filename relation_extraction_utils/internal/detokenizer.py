from nltk.tokenize.treebank import TreebankWordDetokenizer as Detok


class Detokenizer(object):
    '''
    'Detokenize' is a stateless class that contains a single static method 'detokenize'
    '''

    @staticmethod
    def __switch(tokens, find, replace):
        new_list = []

        iterator = iter(tokens)
        for token in iterator:
            if token == find:
                token = replace

            new_list.append(token)

        return new_list

    @staticmethod
    def __box_forward(tokens, find, replace):
        new_list = []

        iterator = iter(tokens)
        for token in iterator:
            if token == find:
                token = replace + next(iterator)

            new_list.append(token)

        return new_list

    @staticmethod
    def __box_backwards(tokens, find, replace):

        new_list = []

        for token in tokens:
            if token != find:
                new_list.append(token)

            else:

                if len(new_list) > 0:
                    new_list[-1] = new_list[-1] + replace
                # otherwise just ignore - not much to be done ...

        return new_list

    @staticmethod
    def detokenize(tokens):
        '''
        '''
        new_tokens = tokens

        new_tokens = Detokenizer.__box_forward(new_tokens, '-LRB-', '(')
        new_tokens = Detokenizer.__box_forward(new_tokens, '``', '"')

        new_tokens = Detokenizer.__box_backwards(new_tokens, '-RRB-', ')')
        new_tokens = Detokenizer.__box_backwards(new_tokens, '\'\'', '"')

        new_tokens = Detokenizer.__switch(new_tokens, '--', '-')

        detokenizer = Detok()
        return detokenizer.detokenize(new_tokens)
