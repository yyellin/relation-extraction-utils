from collections import namedtuple

import networkx


class Step(namedtuple('Step', 'me, next, dep_direction, dependency')):
    """
    'Step' represents a single step in the path between a current node in a dependency tree
    and the next node in the path.
    If the direction corresponds to an edge from a node to it's parent it will be indicated
    with the '↑' character; if it's from the parent of the node to the node itself the direction
    will be indicated with the '↓' symbol
    """


class DepGraph(object):
    """
    'DepGraph' is initialized with a list of Link objects to represent a dependency tree.
    Each edge in the tree is represented by an Edge object.

    Attributes
    ----------
    __edge_to_deptype
        maps each edge in the dependency tree (from a node to its parent) to its dependency type

    __graph
        a networkx.Graph non directed tree which will be used to calculate the shortest path between nodes

    Methods
    -------
    get_steps
        Returns the shortest path between a start and end word represented as a deserialization of a
        list of Step objects

    """

    class Edge(namedtuple('Edge', 'me, parent')):
        """
        As its name suggests the 'Edge' object represents an edge between a node in the dependency tree
        and its parent.
        As Edge is essentially a tuple, it can be used to instantiate networkx.Graph objects
        """

    def __init__(self, links):
        """

        Parameters
        ----------
        links :
           list of 'Link' objects that represent a dependency parse
        """

        self.__edge_to_deptype = {}

        for link in links:
            # convert a link to an edge object that networkx.Graph can be
            # initialized with
            edge = DepGraph.Edge(me=link.word_index, parent=link.governor_index)
            self.__edge_to_deptype[edge] = link.dep_type

        self.__graph = networkx.Graph(list(self.__edge_to_deptype.keys()))

    def get_parents(self, id):
        """

        Parameters
        ----------
        id
            id of node for whose parents we're looking for

        Returns
        -------
        The ids  of all parents of the node whose id was give

        """

        return networkx.ancestors(self.__graph, source=id)


    def get_steps(self, start, end):
        """

        Parameters
        ----------
        start
            first node in path
        end
            last node in path

        Returns
        -------
        The shortest path between 'start and 'end' represented as a deserialization of a
        list of Step objects
        """

        node_list = networkx.shortest_path(self.__graph, source=start, target=end)
        steps = []

        for i in range(0, len(node_list) - 1):

            me = node_list[i]
            next = node_list[i + 1]

            if DepGraph.Edge(me, next) in self.__edge_to_deptype:
                edge = DepGraph.Edge(me, next)
                direction = '!'  # ''↓'
            else:
                # If the edge represented by (this, next) does not exist in the
                # '__edge_to_deptype' map, it means that the actual edge in the
                # dependency parse is from next to this, where this is the parent.
                # Thus we switch the order ...
                edge = DepGraph.Edge(next, me)
                direction = '^'  #'↑'

            dependency = self.__edge_to_deptype[edge]

            step = Step(me=me, next=next, dep_direction=direction, dependency=dependency)

            steps.append(step)
            # ' '.join(['{0}{1}'.format(step.direction, step.dependency) for step in steps])

        return steps
