from collections import namedtuple

import networkx


class Link(namedtuple('Link', 'word, word_index, governor, governor_index, dep_type')):
    """
    An object of type link is a tuple with all the dependency information related to a single
    dependency:
    the word and it's index; it's parent (governor) with the parent's index, as well as the
    dependency type itself
    """



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
