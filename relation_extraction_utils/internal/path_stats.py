from collections import defaultdict
from collections import namedtuple
from enum import Enum

import pandas

from relation_extraction_utils.internal.dep_graph import DepGraph
from relation_extraction_utils.internal.link import Link
from relation_extraction_utils.internal.sync_pss_tags import SyncPssTags


class PathDesignation(Enum):
    """
    PathDesignation is an enum type that contains three members representing
    the three types of paths that we may be interested in.
    Each member is assigned a textual value, that may be useful when iterating
    over all members to represent what they are in natural language
    """

    TRIGGER_TO_ENTITY1 = 'Trigger to Entity 1'
    TRIGGER_TO_ENTITY2 = 'Trigger to Entity 2'
    ENTITY1_TO_ENTITY2_VIA_TRIGGER = 'Entity 1 to Entity 2 via trigger'
    ENTITY1_TO_ENTITY2 = 'Entity 1 to Entity 2 direct'


class Stat(namedtuple('Stat', 'frequency, path')):
    """
    'Stat' is nothing more than a namedtuple representing the frequency and name of a path
    (see https://stackoverflow.com/questions/1606436/adding-docstrings-to-namedtuples)
    """



class PathStats(object):
    """
    'PathStats' is designed to accept a comma delimited file as input and expose histograms representing
    the number of occurrences per path types (enumerated by 'PathDesignation').
    The cvs file must have a row per sentence; each row with the following columns:
       1. trigger_idx
       2. ent1_start
       3. ent1_end
       4. ent2_start
       5. ent2_end
    On initialisation a PathStats object will parse the cvs fail and record the histograms in it's  __histograms
    private property.

    Attributes
    ----------
    __histograms : dictionary of histogram maps
        each histogram map is itself a dictionary mapping a path to the number of its cocurences in the cvs file

    Methods
    -------
    get_sorted_stats
        Returns a list of 'Stat' objects sorted by frequency

    """

    def __init__(self, input_file):
        """
         Parameters
         ----------
         input_file : str
             must contain the path of the comma delimited file - no validation is performed by the code -
             the path must be of a valid file
         """
        self.__histograms = {}
        self.__path_to_sentences = {}

        for path_designation in PathDesignation:
            self.__histograms[path_designation] = defaultdict(int)
            self.__path_to_sentences[path_designation] = {}

        train_data = pandas.read_csv(input_file, header=0)
        train_data.dropna(subset=['trigger_idx', 'ent1_start', 'ent1_end', 'ent1_end', 'ent2_start'], inplace=True)

        for row in train_data.itertuples():

            dependency_parse = eval(row.dependency_parse)

            links = Link.get_links(dependency_parse)
            pss_tags = SyncPssTags.get_pss_tags_by_index(row)


            ent1_indexes = [index for index in range(int(row.ent1_start), int(row.ent1_end) + 1)]
            ent1_head = Link.get_head(links, ent1_indexes)

            ent2_indexes = [index for index in range(int(row.ent2_start), int(row.ent2_end) + 1)]
            ent2_head = Link.get_head(links, ent2_indexes)

            trigger_index = int(row.trigger_idx)
            graph = DepGraph(links)

            trigger_to_ent2 = PathStats.get_steps_as_string(graph.get_steps(trigger_index, ent2_head), pss_tags)
            trigger_to_ent1 = PathStats.get_steps_as_string(graph.get_steps(trigger_index, ent1_head), pss_tags)
            ent1_to_trigger = PathStats.get_steps_as_string(graph.get_steps(ent1_head, trigger_index), pss_tags)
            ent1_to_ent2_via_trigger = '{0} >< {1}'.format(ent1_to_trigger, trigger_to_ent2)
            ent1_to_ent2 = PathStats.get_steps_as_string(graph.get_steps(ent1_head, ent2_head), pss_tags)

            for path_designation, path in zip(PathDesignation, [trigger_to_ent1,
                                                                trigger_to_ent2,
                                                                ent1_to_ent2_via_trigger,
                                                                ent1_to_ent2]):
                path_to_sentences = self.__path_to_sentences[path_designation]
                if path not in path_to_sentences:
                    path_to_sentences[path] = []

                path_to_sentences[path].append(row.sentence)

                self.__histograms[path_designation][path] += 1

    def get_sorted_stats(self, path_designation, reverse=False):
        """
         Parameters
         ----------
         path_designation : PathDesignation
             indicates which path type we're interested in
         reverse : Boolean
             indicates direction of sort of the paths

         Returns
         -------
         a list of 'Stat' objects sorted by frequency

        """

        histogram = self.__histograms[path_designation]
        return sorted([Stat(frequency=frequency, path=path) for (path, frequency) in histogram.items()],
                      reverse=reverse)

    def get_top_n_paths(self, path_designation, n):
        """
         Parameters
         ----------

         Returns
         -------

        """

        histogram = self.__histograms[path_designation]
        top_n_paths = []

        for count, (_, path) in enumerate(
                sorted([Stat(frequency=frequency, path=path) for (path, frequency) in histogram.items()],
                       reverse=True)):

            if count == n:
                break

            top_n_paths.append(path)

        return top_n_paths

    def get_path_sentences(self, path_designation, path):
        """
         Parameters
         ----------

         Returns
         -------

        """

        path_to_sentences = self.__path_to_sentences[path_designation]

        if path not in path_to_sentences.keys():
            return None

        return path_to_sentences[path]

    @staticmethod
    def get_steps_as_string(steps, pss_tags=None):

        if pss_tags is None:
            return ' '.join(['{0}{1}'.format(step.dep_direction, step.dependency) for step in steps])

        str = ''
        for step in steps:
            str = str + '{0}{1}'.format(step.dep_direction, step.dependency)

            if step.me in pss_tags.keys():
                str = str + '({0}/{1})'.format(pss_tags[step.me][1], pss_tags[step.me][2])

        return str

