from collections import namedtuple

import networkx


class Link(namedtuple('Link', 'word, word_index, governor, governor_index, dep_type')):
    """
    An object of type link is a tuple with all the dependency information related to a single
    dependency:
    the word and it's index; it's parent (governor) with the parent's index, as well as the
    dependency type itself
    """
    pass


def get_links(unprocessed_links):
    """
    'get_links' will take the stanfordnlp's representation of a dependency tree of a sentence
    and return a list of 'Link' objects representing the same.
    The advantage ot the Link based representation is that it's a named-tuple which is much less error
    prone that a simple tuple where it's possible to get indexing very wrong.

    Parameters
    ----------
    unprocessed_links :
        stanfordnlp's representation of a dependency tree as a list of tuples

    Returns
    -------
        the same dependency tree represented by a list of Link objects

    """

    links = []

    for unprocessed_link in unprocessed_links:
        link = Link(word=unprocessed_link[1],
                    word_index=int(unprocessed_link[0]),
                    governor=unprocessed_link[4],
                    governor_index=int(unprocessed_link[3]),
                    dep_type=unprocessed_link[2])

        links.append(link)

    return links


def get_head(links, nodes):
    """
    'get_head' will receive a dependency tree represented as a list of Link objects as well as a
    list of contiguous node indices and will return the head node among them (i.e. a node which all
    others are decedents of)


    Parameters
    ----------
    links
        representation of dependency tree as list of Link objects
        
    nodes
        list of contiguous node indices

    Returns
    -------
    returns one of the node indices in 'nodes' which is an ancestor of all other.
    Importantly, if no such node exists (i.e. there is no node in 'nodes' which is
    ancestor to all others) the first node in 'nodes' will be returned

    """
    graph = __get_networkx_digraph(links)

    for potential_head in nodes:
        descendants = networkx.descendants(graph, potential_head)
        nodes_without_potential_head = list(filter(lambda x: x != potential_head, nodes))

        found_head = True
        for potential_descendant in nodes_without_potential_head:
            if potential_descendant not in descendants:
                found_head = False
                break

        if found_head:
            return potential_head

    # if we can't find a head, by convention we just return the first node
    return nodes[0]


def __get_networkx_digraph(links):
    """
    internal method that converts a list of Link objects into an instance of 'networkx.DiGraph'
    """
    edges = []
    for link in links:
        edges.append((link.governor_index, link.word_index))

    digraph = networkx.DiGraph(edges)
    return digraph
