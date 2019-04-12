from collections import namedtuple

import networkx

Link = namedtuple('Link', 'word, word_index, governor, governor_index, dep_type')


def get_links(unprocessed_links):
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
    edges = []
    for link in links:
        edges.append((link.governor_index, link.word_index))

    digraph = networkx.DiGraph(edges)
    return digraph
