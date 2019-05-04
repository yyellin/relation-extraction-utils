class SyncIndices(object):
    """

    Attributes
    ----------
    Methods
    -------

    """

    @staticmethod
    def b_lookup_to_a_lookup(list_a, list_b, list_b_lookup):

        list_a_lookup = {}

        index_a = 0
        index_b = 0

        matched_total = len(list_b_lookup)
        matched_so_far = 0

        while matched_so_far < matched_total and index_a < len(list_a) and index_b < len(list_b):

            # Possibility 1: pointing to same token
            if list_a[index_a] == list_b[index_b]:

                for k, v in list_b_lookup.items():
                    if v == index_b:
                        list_a_lookup[k] = index_a
                        matched_so_far += 1

                index_a += 1
                index_b += 1
                continue

            # Possibility 2: b's token represent multiple tokens of a
            b_word = list_b[index_b]
            substring = False
            while list_a[index_a] in b_word:

                substring = True

                for k, v in list_b_lookup.items():

                    if v == index_b:

                        if 'start' not in k or k not in list_a_lookup:
                            list_a_lookup[k] = index_a

                    # if not processing_positive_substring and v == index_b and 'start' in k:
                    #     processing_positive_substring = True
                    #     in_end = False
                    #     list_a_lookup[k] = index_a
                    #     matched_so_far += 1
                    #     break
                    #
                    # if processing_positive_substring and v == index_b and 'end' in k:
                    #     in_end = True
                    #     list_a_lookup[k] = index_a
                    #     matched_so_far += 1
                    #     break
                    #

                index_a += 1
                if index_a == len(list_a):
                    break

            if substring:

                index_b += 1
                if index_b == len(list_b):
                    break

                continue

            # Fallback: increment index of b until a match with a is found
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
