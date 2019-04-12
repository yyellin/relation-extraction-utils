from collections import defaultdict

import pandas

from count_trigger_paths import _utility
from count_trigger_paths._dep_graph import DepGraph


class PathStats(object):
    '''
    '''

    def __init__(self, input_file):
        '''

        '''

        self._trigger_to_entity1_hostogram = defaultdict(int)
        self._trigger_to_entity2_hostogram = defaultdict(int)
        self._entity1_to_entity2_hostogram = defaultdict(int)

        train_data = pandas.read_csv(input_file, header=0)
        train_data.dropna(subset=['trigger_idx', 'ent1_start', 'ent1_end', 'ent1_end', 'ent2_start'], inplace=True)

        for row in train_data.itertuples():
            dependency_parse = eval(row.dependency_parse)

            links = _utility.get_links(dependency_parse)

            ent1_indexes = [index for index in range(int(row.ent1_start), int(row.ent1_end) + 1)]
            ent1_head = _utility.get_head(links, ent1_indexes)

            ent2_indexes = [index for index in range(int(row.ent2_start), int(row.ent2_end) + 1)]
            ent2_head = _utility.get_head(links, ent2_indexes)

            trigger_index = int(row.trigger_idx)
            graph = DepGraph(links)

            self._trigger_to_entity1_hostogram[graph.get_steps(trigger_index, ent1_head)] += 1
            self._trigger_to_entity2_hostogram[graph.get_steps(trigger_index, ent2_head)] += 1
            self._entity1_to_entity2_hostogram[graph.get_steps(ent1_head, ent2_head)] += 1
