from collections import namedtuple

import networkx

from relation_extraction_utils.internal.ucca_types import UccaTerminalNode


class Link(namedtuple('Link', 'word, word_index, governor, governor_index, dep_type')):
    """
    An object of type link is a tuple with all the dependency information related to a single
    dependency:
    the word and it's index; it's parent (governor) with the parent's index, as well as the
    dependency type itself
    """

    @staticmethod
    def get_links_from_ud_dep(ud_representation):
        """
        'get_links_from_ud_dep' will take the stanfordnlp's UD representation of a dependency tree
        of a sentence and return a list of 'Link' objects representing the same.
        The advantage ot the Link based representation is that it's a named-tuple which is much less error
        prone that a simple tuple where it's possible to get indexing very wrong.

        Parameters
        ----------
        ud_representation :
            stanfordnlp's representation of a dependency tree as a list of tuples

        Returns
        -------
            the same dependency tree represented by a list of Link objects

        """

        links = []

        for unprocessed_link in ud_representation:
            link = Link(word=unprocessed_link[1],
                        word_index=int(unprocessed_link[0]),
                        governor=unprocessed_link[4],
                        governor_index=int(unprocessed_link[3]),
                        dep_type=unprocessed_link[2])

            links.append(link)

        return links

    @staticmethod
    def get_links_from_ucca_dep(ucca_representation):
        """
        'get_links_from_ucca_dep' will take a UCCA representation of a parse tree coressponding
        to a sentence and return a list of 'Link' objects representing the same.

        Parameters
        ----------
        ucca_representation :
            ucca based representation of a dependency tree as a list of tuples

        Returns
        -------
            the same dependency tree represented by a list of Link objects

        """

        links = []

        for edge in ucca_representation.edges:
            link = Link(word=edge.child.text if isinstance(edge.child, UccaTerminalNode) else None,
                        word_index=edge.child.node_id,
                        governor=None,
                        governor_index=edge.parent.node_id,
                        dep_type=edge.tag)

            links.append(link)

        return links

    @staticmethod
    def get_parents(links, index):
        """
        'get_parents' will receive a dependency tree represented as a list of Link objects as well as a
        a index and will return a list of word_index values representing it's ancestors


        Parameters
        ----------
        links
            representation of dependency tree as list of Link objects

        index
            index of node whose parents we're interested in

        Returns
        -------
        returns a list of all ancestor nodes of the node whose index was requested

        """
        return [link.governor_index for link in links if link.word_index == index]



    @staticmethod
    def get_head(links, indices):
        """
        'get_head' will receive a dependency tree represented as a list of Link objects as well as a
        list of contiguous node indices and will return the head node among them (i.e. a node which all
        others are decedents of)


        Parameters
        ----------
        links
            representation of dependency tree as list of Link objects

        indices
            list of contiguous node indices

        Returns
        -------
        returns one of the node indices in 'nodes' which is an ancestor of all other.
        Importantly, if no such node exists (i.e. there is no node in 'nodes' which is
        ancestor to all others) the first node in 'nodes' will be returned

        """
        graph = Link.__get_networkx_digraph(links)

        for potential_head in indices:
            descendants = networkx.descendants(graph, potential_head)
            nodes_without_potential_head = list(filter(lambda x: x != potential_head, indices))

            found_head = True
            for potential_descendant in nodes_without_potential_head:
                if potential_descendant not in descendants:
                    found_head = False
                    break

            if found_head:
                return potential_head

        # if we can't find a head, by convention we just return the first node
        return indices[0]



    @staticmethod
    def __get_networkx_digraph(links):
        """
        internal method that converts a list of Link objects into an instance of 'networkx.DiGraph'
        """
        edges = []
        for link in links:
            edges.append((link.governor_index, link.word_index))

        digraph = networkx.DiGraph(edges)
        return digraph
