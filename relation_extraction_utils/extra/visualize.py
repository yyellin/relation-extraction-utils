import os
import warnings
from argparse import ArgumentParser
from collections import defaultdict
from operator import attrgetter

import matplotlib
import matplotlib.pyplot as plt

from ucca import layer0, layer1
from ucca.ioutil import get_passages_with_progress_bar

from relation_extraction_utils.internal.ucca_types import UccaParsedPassage, UccaTerminalNode



def from_xml(xml_files):

    passages = get_passages_with_progress_bar(xml_files, desc="Visualizing")

    for passage in passages:

        width = len(passage.layer(layer0.LAYER_ID).all) * 19 / 27
        plt.figure(figsize=(width, width * 10 / 19))
        draw_from_native(passage)

        plt.savefig(os.path.join(args.out_dir, passage.ID + ".png"))
        plt.close()

def draw_from_native(passage):
    import matplotlib.cbook
    import networkx as nx
    warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)
    warnings.filterwarnings("ignore", category=UserWarning)
    g = nx.DiGraph()
    terminals = sorted(passage.layer(layer0.LAYER_ID).all, key=attrgetter("position"))
    g.add_nodes_from([(n.ID, {"label": '{0}\n{1}'.format(n.ID, n.text), "color": "white"}) for n in terminals])
    g.add_nodes_from([(n.ID, {"label": n.ID,
                              "color": "white"}) for n in passage.layer(layer1.LAYER_ID).all])
    g.add_edges_from([(n.ID, e.child.ID, {"label": "|".join(e.tags),
                                          "style": "dashed" if e.attrib.get("remote") else "solid"})
                      for layer in passage.layers for n in layer.all for e in n])
    pos = topological_layout_native(passage)
    nx.draw(g, pos, arrows=False, font_size=10,
            node_color=[d["color"] for _, d in g.nodes(data=True)],
            labels={n: d["label"] for n, d in g.nodes(data=True) if d["label"]},
            style=[d["style"] for _, _, d in g.edges(data=True)])
    nx.draw_networkx_edge_labels(g, pos, font_size=8,
                                 edge_labels={(u, v): d["label"] for u, v, d in g.edges(data=True)})

def topological_layout_native(passage):
    visited = defaultdict(set)
    pos = {}
    implicit_offset = 1 + max((n.position for n in passage.layer(layer0.LAYER_ID).all), default=-1)
    remaining = [n for layer in passage.layers for n in layer.all if not n.parents]
    while remaining:
        node = remaining.pop()
        if node.ID in pos:  # done already
            continue
        if node.children:
            children = [c for c in node.children if c.ID not in pos and c not in visited[node.ID]]
            if children:
                visited[node.ID].update(children)  # to avoid cycles
                remaining += [node] + children
                continue
            xs, ys = zip(*(pos[c.ID] for c in node.children))
            pos[node.ID] = (sum(xs) / len(xs), 1 + max(ys) ** 1.01)  # done with children
        elif node.layer.ID == layer0.LAYER_ID:  # terminal
            pos[node.ID] = (int(node.position), 0)
        else:  # implicit
            pos[node.ID] = (implicit_offset, 0)
            implicit_offset += 1
    return pos




def from_serialized_ucca_parsed_passage(re_representation_files):

    from os.path import splitext


    for re_representation_file in re_representation_files:

        with open(re_representation_file, 'r') as file:
            serialization = file.read().replace('\n', '')
            parsed_passage = UccaParsedPassage.from_serialization(serialization)


        width = len(parsed_passage.terminals) * 19 / 27

        plt.figure(figsize=(width, width * 10 / 19))

        draw_from_re_representation(parsed_passage)

        filename, _ = splitext(re_representation_file)

        plt.savefig(os.path.join(args.out_dir, filename + '.png'))
        plt.close()

def draw_from_re_representation(passage):

    import matplotlib.cbook
    import networkx as nx
    warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)
    warnings.filterwarnings("ignore", category=UserWarning)

    g = nx.DiGraph()

    g.add_nodes_from([(n.node_id, {"label": '{0}\n{1}'.format(n.node_id, n.text), "color": "white"}) for n in passage.terminals])
    g.add_nodes_from([(n.node_id, {"label": n.node_id, "color": "white"}) for n in passage.non_terminals])
    g.add_edges_from([(edge.parent.node_id, edge.child.node_id, {"label": edge.tag}) for edge in passage.edges])

    pos = topological_layout_re(passage)

    nx.draw(g, pos, arrows=False, font_size=10,
            node_color=[d["color"] for _, d in g.nodes(data=True)],
            labels={n: d["label"] for n, d in g.nodes(data=True) if d["label"]})

    nx.draw_networkx_edge_labels(g, pos, font_size=8,
                                 edge_labels={(u, v): d["label"] for u, v, d in g.edges(data=True)})



def topological_layout_re(passage):


    nodes_to_parents = passage.get_ucca_nodes_with_parents()
    nodes_to_children = passage.get_ucca_nodes_with_children()



    visited = defaultdict(set)
    pos = {}
    remaining = [node for node, parents in nodes_to_parents.items() if len(parents) is 0]
    implicit_offset = 1 + max((n.token_id for n in passage.terminals), default=-1)


    while remaining:
        node = remaining.pop()

        if node.node_id in pos:  # done already
            continue


        if len(nodes_to_children[node]) > 0:
            children = [c for c in nodes_to_children[node] if c.node_id not in pos and c not in visited[node.node_id]]
            if len(children) > 0:
                visited[node.node_id].update(children)  # to avoid cycles
                remaining += [node] + children
                continue

            xs, ys = zip(*(pos[c.node_id] for c in nodes_to_children[node]))

            pos[node.node_id] = (sum(xs) / len(xs), 1 + max(ys) ** 1.01)  # done with children

        elif isinstance(node, UccaTerminalNode):  # terminal
            pos[node.node_id] = (node.token_id, 0)

        else:  # implicit
            pos[node.node_id] = (implicit_offset, 0)
            implicit_offset += 1

    return pos










if __name__ == "__main__":
    argparser = ArgumentParser(description="Visualize the given passages as graphs.")

    argparser.add_argument("out_dir", help="directory to save figures in")

    group = argparser.add_mutually_exclusive_group(required=True)
    group.add_argument("-x", "--xml", nargs="+", help="UCCA passages, given as xml/pickle file names")
    group.add_argument("-r", "--re", nargs="+", help="UCCA passages, given as serializations of UccaParsedPassage")



    args = argparser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    matplotlib.use('Agg')

    if args.xml is not None:
        from_xml(args.xml)

    elif args.re is not None:
        from_serialized_ucca_parsed_passage(args.re)
