import sys

from tupa.config import  Config
from tupa.parse import Parser
from ucca.convert import from_text
from ucca.core import Passage
from ucca.layer0 import Layer0
from ucca.layer1 import Layer1
from ucca.textutil import annotate_all

from relation_extraction_utils.internal.ucca_types import UccaParsedPassage, UccaEdge, UccaNode, UccaTerminalNode


class TupaParser(object):
    """

    Attributes
    ----------
    Methods
    -------

    """

    # the 'from_text' method requires a passage id, however users of this class will not need it.
    # thus, we'll just provide a arbitrary id, in the form of a class level counter that gets
    # incremented after each use
    __passage_counter = 0

    def __init__(self, model_prefix):
        """

        Parameters
        ----------
        """

        # believe it or not, the sys.argv assignment is a necessary hack,
        # without it tupa.parse.Parser will throw exceptions ..
        remember_argv = sys.argv
        sys.argv = ['-m', model_prefix]
        parser = Parser(model_files= model_prefix, config=Config())
        parser.train([],[],[])
        ##parser.trained = True
        ##parser.models[0].load()

        first_sentence = 'Nina Zagat, co-founder of Zagat Survey employs her intimate knowledge of high-end restaurants within a 15-minute drive of any major airport and suggests travelers go and enjoy a pleasant meal instead of hanging around the fast-food joints.'

        ###parser= Parser(model_files=model_prefix, config=Config())
        ######yield from filter(None,
        ######                  p.train(train_passages, dev=dev_passages, test=test_passages, iterations=args.iterations))
        ###unparsed_passage = next( annotate_all( from_text( first_sentence, 0, one_per_line= True) ) )
        ###result = list(parser.train( [], dev=[], test=[unparsed_passage] ))


        self.__parser = parser

        # Since 'parse_sentence' calls 'annotate_all' which lazily instantiated a spacey pipeline,
        # and since we want all the initialization to occur in the __init__ method, we simply call
        # 'parse_sentence' with dummy input
        self.parse_sentence('Hello dummy world')

        # undo hack side effect
        sys.argv = remember_argv

    def parse_sentence(self, sentence):

        TupaParser.__passage_counter =+ 1
        passage_id = TupaParser.__passage_counter =+ 1

        # from_text will convert the sentence into a ucca structure.
        # annotate_all will annotate the structure with information from the Spacy parse.
        # annotate_all returns a generator - one that will yield only one object - hence
        # we call next
        unparsed_passage = next( annotate_all( from_text( sentence, passage_id, one_per_line= True) ) )


        # The 'tupa.parse class's parse method expects a list of unparsed-message. We also need to set
        # the 'evaluate' argument to True, otherwise we get incorrect results. (Ofir Arviv advised as such).
        # The parse method also returns a generator, hence the need to call next.
        # The actual object returned is a tuple of the parsed-passage and an internal score object. We're
        # not interested in the score though, so we just extract the parsed-passage
        parsed_passage_and_score = next( self.__parser.parse( [unparsed_passage], evaluate=False, write=True) )
        internal_parsed_passage = parsed_passage_and_score[0]
        parsed_passage = TupaParser.__get_ucca_parsed_passage_from_passage(internal_parsed_passage)

        return parsed_passage

    @staticmethod
    def __get_ucca_parsed_passage_from_passage(passage: Passage):
        ucca_parsed_passage = UccaParsedPassage()

        ucca_parsed_passage.terminals = []
        ucca_parsed_passage.non_terminals = []
        ucca_parsed_passage.edges = []

        ucca_node_lookup = {}

        layer0 = next(layer for layer in passage.layers if isinstance(layer, Layer0))
        layer1 = next(layer for layer in passage.layers if isinstance(layer, Layer1))

        for node in layer0.all:
            edge_tags_in = [edge.tag for edge in node.incoming]
            token_id = int(node.ID.split('.')[1])  # :)
            terminal_node = UccaTerminalNode(node.ID, edge_tags_in, token_id, node.text, node.extra['lemma'])
            ucca_parsed_passage.terminals.append(terminal_node)
            ucca_node_lookup[node.ID] = terminal_node

        for node in layer1.all:
            edge_tags_in = [edge.tag for edge in node.incoming]
            non_terminal_node = UccaNode(node.ID, edge_tags_in)
            ucca_parsed_passage.non_terminals.append(non_terminal_node)
            ucca_node_lookup[node.ID] = non_terminal_node

        # all the edges are from layer1 nodes to their children (which can include layer0
        # nodes)
        for node in layer1.all:
            for edge in node.outgoing:
                child_node = ucca_node_lookup[edge.child.ID]
                parent_node = ucca_node_lookup[edge.parent.ID]

                ucca_parsed_passage.edges.append(UccaEdge(child_node, parent_node, edge.tag))

        return ucca_parsed_passage
