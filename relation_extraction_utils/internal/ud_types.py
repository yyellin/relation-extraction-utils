'''
This module is currently more of a placeholder for UD related object model.

Only after (1) implementation of the UCCA side of things, and (2) the analysis of the emerging object model
and relationship between classes (e.g Link, DepGraph, UccaParsedPassage) it became clear that the 'Link' class
should not be aware of specific dependency implementations (e.g. UD or UCCA), and that the static methods
'get_links_from_ud_dep' and 'get_links_from_ucca_dep' should be moved from Link to their corresponding 'homes'.

In the case of UCCA clearly that home would be the 'UccaParsedPassage'; however in the case of UD, at the time
of this writing (14-06-2019), UD dependency graph does not have an object representation per se, and is serialized
and deserialized using standard python to-string-conversion and eval mechanisms. As the UD code is not currently
under development I will not currently implement a UdParsedPassage class, but only move the 'get_links_from_ud_dep'
from the Link object.

Here goes:

'''

from relation_extraction_utils.internal.link import Link


class UdRepresentationPlaceholder(object):

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
