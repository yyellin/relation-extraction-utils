class SyncPssTags(object):
    """
    'SyncPssTags' is designed to

    Attributes
    ----------

    Methods
    -------

    """

    @staticmethod
    def get_pss_tags_by_index(index_lookup, pss_index_lookup, pss_positive_lookup):

        index_to_pss = {}

        index = 1
        pss_index = 1
        while len(pss_positive_lookup) > 0 and index <= len(index_lookup) and pss_index <= len(pss_index_lookup):

            # Possibility 1: pointing to same token
            if index_lookup[index] == pss_index_lookup[pss_index]:
                if pss_index in pss_positive_lookup.keys():
                    index_to_pss[index] = pss_positive_lookup[pss_index]
                    del pss_positive_lookup[pss_index]

                index += 1
                pss_index += 1
                continue

            # Possibility 2: pss token represents multiple different tokens
            this_is_substring = False
            pss_word = pss_index_lookup[pss_index]
            while index_lookup[index] in pss_word:
                this_is_substring = True
                index += 1
                if index > len(index_lookup):
                    break

            if this_is_substring:
                pss_index += 1
                continue

            # Possibility 3: our token represents multiple different tokens
            pss_is_substring = False
            this_word = index_lookup[index]
            while pss_index_lookup[pss_index] in this_word:
                pss_is_substring = True
                pss_index += 1
                if pss_index > len(pss_index_lookup):
                    break

            if pss_is_substring:
                index += 1
                continue

            # Possibility 4: maybe the current word is represented differently - e.g. " vs ' - let's
            # just try to increment both
            index += 1
            pss_index += 1
            continue

        return index_to_pss
