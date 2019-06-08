import json
import sys
from itertools import chain

from tupa.parse import Parser
from ucca.convert import from_text
from ucca.core import Passage
from ucca.layer0 import Layer0
from ucca.layer1 import Layer1
from ucca.textutil import annotate_all


class UccaNode(object):
    def __init__(self, node_id, edge_tags_in):
        self.node_id = node_id
        self.edge_tags_in = [x for i, x in enumerate(edge_tags_in) if edge_tags_in.index(x) == i]


class UccaTerminalNode(UccaNode):
    def __init__(self, node_id, edge_tags_in, token_id, text, lemma ):
        super().__init__(node_id, edge_tags_in)

        self.token_id = token_id
        self.text = text
        self.lemma = lemma



class UccaEdge(object):
    def __init__(self, child, parent, edge_tag):
        self.child = child
        self.parent = parent
        self.edge_tag = edge_tag

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.child.node_id == other.child.node_id and self.parent.node_id == other.parent.node_id and self.edge_tag == other.edge_tag
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.child.node_id, self.parent.node_id, self.edge_tag))

    def get_edge_representations(self):
        if len(self.parent.edge_tags_in) == 0:
            return '{}.'.format(self.edge_tag)

        return ['{}{}'.format(self.edge_tag,parent_edge_tag_in) for parent_edge_tag_in in self.parent.edge_tags_in]


class UccaParsedPassage(object):

    class UccaParsedPassageEncoding(json.JSONEncoder):

        def default(self, z):

            if isinstance(z, UccaTerminalNode):
                return (z.node_id, z.token_id, z.text, z.lemma)

            elif isinstance(z, UccaNode):
                return (z.node_id, z.edge_tags_in)

            elif isinstance(z, UccaEdge):
                return (z.child.node_id, z.parent.node_id, z.edge_tag)

            elif isinstance(z, UccaParsedPassage):
                data = {}
                data['terminals'] = z.terminals
                data['non_terminals'] = z.non_terminals
                data['edges'] = z.edges
                return data

            else:
                return super().default(z)


    def ucca_node_by_id(self, id):
        return self.__ucca_nodelookup.get(id)

    def serialize(self):
        return json.dumps( self, cls= UccaParsedPassage.UccaParsedPassageEncoding)

    @staticmethod
    def from_passage(passage : Passage):

        self = UccaParsedPassage()

        self.terminals = []
        self.non_terminals = []
        self.edges = []
        self.__ucca_nodelookup = {}

        layer0 = next(layer for layer in passage.layers if isinstance(layer, Layer0))
        layer1 = next(layer for layer in passage.layers if isinstance(layer, Layer1))

        for node in layer0.all:
            edge_tags_in = [edge.tag for edge in node.incoming]
            token_id = int(float(node.ID)*10) ## :)
            terminal_node = UccaTerminalNode(node.ID, edge_tags_in, token_id, node.text, node.extra['lemma'])
            self.terminals.append(terminal_node)
            self.__ucca_nodelookup[node.ID] = terminal_node

        for node in layer1.all:
            edge_tags_in = [edge.tag for edge in node.incoming]
            non_terminal_node = UccaNode(node.ID, edge_tags_in)
            self.non_terminals.append(non_terminal_node)
            self.__ucca_nodelookup[node.ID] = non_terminal_node


        # all the edges are from layer1 nodes to their children (which can include layer0
        # nodes)
        for node in layer1.all:
            for edge in node.outgoing:
                child_node = self.__ucca_nodelookup[edge.child.ID]
                parent_node = self.__ucca_nodelookup[edge.parent.ID]

                self.edges.append( UccaEdge(child_node, parent_node, edge.tag) )


        return self

    @staticmethod
    def from_serialization(serialization : str):

        self = UccaParsedPassage()

        representation = eval(serialization)

        self.terminals = []
        self.non_terminals = []
        self.edges = []
        self.__ucca_nodelookup = {}


        for element in representation['terminals']:
            terminal = UccaTerminalNode(element[0], ['Terminal'], element[1], element[2], element[3])
            self.terminals.append(terminal)
            self.__ucca_nodelookup[terminal.node_id] = terminal

        for element in representation['non_terminals']:
            non_terminal = UccaNode(element[0], element[1])
            self.non_terminals.append(non_terminal)
            self.__ucca_nodelookup[non_terminal.node_id] = non_terminal

        for element in representation['edges']:
            child_id = element[0]
            parent_id = element[1]
            edge_tag = element[2]

            child = next(node for node in chain(self.non_terminals, self.terminals) if node.node_id == child_id)
            parent = next(node for node in chain(self.non_terminals, self.terminals) if node.node_id == parent_id)

            self.edges.append(UccaEdge(child, parent, edge_tag))

        return self


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

        parser = Parser(model_files= model_prefix)
        parser.models[0].load()
        parser.trained = True

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
        parsed_passage_and_score = next( self.__parser.parse( [unparsed_passage], evaluate=True) )
        internal_parsed_passage = parsed_passage_and_score[0]
        parsed_passage = UccaParsedPassage.from_passage(internal_parsed_passage)

        return parsed_passage









