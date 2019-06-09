import json
from itertools import chain


class UccaNode(object):
    def __init__(self, node_id, edge_tags_in):
        self.node_id = node_id
        self.edge_tags_in = [x for i, x in enumerate(edge_tags_in) if edge_tags_in.index(x) == i]


class UccaTerminalNode(UccaNode):
    def __init__(self, node_id, edge_tags_in, token_id, text, lemma):
        super().__init__(node_id, edge_tags_in)

        self.token_id = token_id
        self.text = text
        self.lemma = lemma


class UccaEdge(object):
    def __init__(self, child, parent, tag):
        self.child = child
        self.parent = parent
        self.tag = tag

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.child.node_id == other.child.node_id and self.parent.node_id == other.parent.node_id and self.tag == other.tag
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.child.node_id, self.parent.node_id, self.tag))

    def get_representations(self):
        if len(self.parent.edge_tags_in) == 0:
            return '{}.'.format(self.tag)

        return ['{}{}'.format(self.tag, parent_edge_tag_in) for parent_edge_tag_in in self.parent.edge_tags_in]


class UccaParsedPassage(object):
    class UccaParsedPassageEncoding(json.JSONEncoder):

        def default(self, z):

            if isinstance(z, UccaTerminalNode):
                return (z.node_id, z.token_id, z.text, z.lemma)

            elif isinstance(z, UccaNode):
                return (z.node_id, z.edge_tags_in)

            elif isinstance(z, UccaEdge):
                return (z.child.node_id, z.parent.node_id, z.tag)

            elif isinstance(z, UccaParsedPassage):
                data = {}
                data['terminals'] = z.terminals
                data['non_terminals'] = z.non_terminals
                data['edges'] = z.edges
                return data

            else:
                return super().default(z)

    def serialize(self):
        return json.dumps(self, cls=UccaParsedPassage.UccaParsedPassageEncoding)

    def ucca_node_by_node_id(self, node_id):
        return next(node for node in chain(self.terminals, self.non_terminals) if node.node_id == node_id)

    def node_id_by_token_id(self, token_id):
        return next(terminal.node_id for terminal in self.terminals if terminal.token_id == token_id)

    @staticmethod
    def from_serialization(serialization: str):

        self = UccaParsedPassage()

        representation = eval(serialization)

        self.terminals = []
        self.non_terminals = []
        self.edges = []

        for element in representation['terminals']:
            terminal = UccaTerminalNode(element[0], ['Terminal'], element[1], element[2], element[3])
            self.terminals.append(terminal)

        for element in representation['non_terminals']:
            non_terminal = UccaNode(element[0], element[1])
            self.non_terminals.append(non_terminal)

        for element in representation['edges']:
            child_id = element[0]
            parent_id = element[1]
            edge_tag = element[2]

            child = next(node for node in chain(self.non_terminals, self.terminals) if node.node_id == child_id)
            parent = next(node for node in chain(self.non_terminals, self.terminals) if node.node_id == parent_id)

            self.edges.append(UccaEdge(child, parent, edge_tag))

        return self
