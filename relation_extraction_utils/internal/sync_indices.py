class SyncIndices(object):
    """

    Attributes
    ----------
    Methods
    -------

    """

    @staticmethod
    def b_reverselookup_to_a_lookup(list_a, list_b, list_b_lookup):
        list_a_lookup = {}

        index_a = 0
        index_b = 0

        matched_total = len(list_b_lookup)
        matched_so_far = 0

        while matched_so_far < matched_total and index_a < len(list_a) and index_b < len(list_b):

            if list_a[index_a] == list_b[index_b]:
                if index_b in list_b_lookup.keys():
                    list_a_lookup[list_b_lookup[index_b]] = index_a
                    matched_so_far += 1

                index_a += 1
                index_b += 1
                continue

            while index_b < len(list_b):

                tmp = index_a
                found = False
                while tmp < len(list_a):
                    if list_a[tmp] == list_b[index_b]:
                        found = True
                        break
                    tmp += 1

                if found:
                    index_a = tmp
                    break

                index_b += 1

        return list_a_lookup
