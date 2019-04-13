from collections import defaultdict
from collections import namedtuple
from enum import Enum

import pandas

from count_trigger_paths import _utility
from count_trigger_paths._dep_graph import DepGraph

Stat = namedtuple('Stat', 'frequency, path')


class PathDesignation(Enum):

    TRIGGER_TO_ENTITY1 = 'Trigger to Entity 1'
    TRIGGER_TO_ENTITY2 = 'Trigger to Entity 2'
    ENTITY1_TO_ENTITY2 = 'Entity 1 to Entity 2'


class PathStats(object):

    def __init__(self, input_file):

        self.__trigger_to_entity1_histogram = defaultdict(int)
        self.__trigger_to_entity2_histogram = defaultdict(int)
        self.__entity1_to_entity2_histogram = defaultdict(int)

        train_data = pandas.read_csv(input_file, header=0)
        train_data.dropna(subset=['trigger_idx', 'ent1_start', 'ent1_end', 'ent1_end', 'ent2_start'], inplace=True)

        for row in train_data.itertuples():
            dependency_parse = eval(row.dependency_parse)

            links = _utility._get_links(dependency_parse)

            ent1_indexes = [index for index in range(int(row.ent1_start), int(row.ent1_end) + 1)]
            ent1_head = _utility._get_head(links, ent1_indexes)

            ent2_indexes = [index for index in range(int(row.ent2_start), int(row.ent2_end) + 1)]
            ent2_head = _utility._get_head(links, ent2_indexes)

            trigger_index = int(row.trigger_idx)
            graph = DepGraph(links)

            self.__trigger_to_entity1_histogram[graph.get_steps(trigger_index, ent1_head)] += 1
            self.__trigger_to_entity2_histogram[graph.get_steps(trigger_index, ent2_head)] += 1
            self.__entity1_to_entity2_histogram[graph.get_steps(ent1_head, ent2_head)] += 1

    def get_sorted_stats(self, path_designation, reverse=False):

        histogram = None

        if path_designation == PathDesignation.TRIGGER_TO_ENTITY1:
            histogram = self.__trigger_to_entity1_histogram
        elif path_designation == PathDesignation.TRIGGER_TO_ENTITY2:
            histogram = self.__trigger_to_entity2_histogram
        elif path_designation == PathDesignation.ENTITY1_TO_ENTITY2:
            histogram = self.__entity1_to_entity2_histogram

        assert (histogram is not None)

        return sorted([Stat(frequency=frequency, path=path) for (path, frequency) in histogram.items()],
                      reverse=reverse)
