from collections import namedtuple

import networkx

Step = namedtuple('Step', 'direction, dependency')


class DepGraph(object):
    '''
    '''

    Edge = namedtuple('Edge', 'me, parent')

    def __init__(self, links):
        '''

        '''

        self._edge_to_deptype = {}

        for link in links:
            edge = DepGraph.Edge(me=link.word_index, parent=link.governor_index)
            self._edge_to_deptype[edge] = link.dep_type

        self._graph = networkx.Graph(list(self._edge_to_deptype.keys()))

    def get_steps(self, start, end):

        node_list = networkx.shortest_path(self._graph, source=start, target=end)
        steps = []

        for i in range(0, len(node_list) - 1):

            this = node_list[i]
            next = node_list[i + 1]

            if DepGraph.Edge(this, next) in self._edge_to_deptype:
                edge = DepGraph.Edge(this, next)
                direction = '↑'
            else:
                edge = DepGraph.Edge(next, this)
                direction = '↓'

            dependency = self._edge_to_deptype[edge]

            step = Step(direction=direction, dependency=dependency)

            steps.append(step)

        return ' '.join(['{0}{1}'.format(step.direction, step.dependency) for step in steps])
