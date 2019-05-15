class SyncTags(object):
    """
    'SyncTags' is designed to

    Attributes
    ----------

    Methods
    -------

    """

    @staticmethod
    def b_lookup_to_a_lookup(list_a, list_b, list_b_lookup):

        list_b_lookup = list_b_lookup.copy()
        list_a_lookup = {}

        index_a = 1
        index_b = 1
        while len(list_b_lookup) > 0 and index_a <= len(list_a) and index_b <= len(list_b):

            # Possibility 1: pointing to same token
            if list_a[index_a - 1] == list_b[index_b - 1]:
                if index_b in list_b_lookup.keys():
                    list_a_lookup[index_a] = list_b_lookup[index_b]
                    del list_b_lookup[index_b]

                index_a += 1
                index_b += 1
                continue

            # Possibility 2: b's token represents multiple different tokens in a
            #
            # note: in this case if b's token has a b-lookup, all corresponding a tokens
            #       will get that lookup

            a_is_substring = False
            word_b = list_b[index_b - 1]
            while list_a[index_a - 1] in word_b:
                a_is_substring = True

                if index_b in list_b_lookup.keys():
                    list_a_lookup[index_a] = list_b_lookup[index_b]

                index_a += 1
                if index_a > len(list_a):
                    break

            if a_is_substring:

                if index_b in list_b_lookup.keys():
                    del list_b_lookup[index_b]

                index_b += 1
                continue

            # Possibility 3: a's token represents multiple different tokens in b
            #
            # note: in this case the a token will be mapped to the last b token
            #       that has a lookup (so if b's tokens correspond to different lookup
            #       values, a will be mapped to the last one only and the others will be
            #       lost)

            b_is_substring = False
            word_a = list_a[index_b - 1]
            while list_b[index_b - 1] in word_a:
                b_is_substring = True

                if index_b in list_b_lookup.keys():
                    list_a_lookup[index_a] = list_b_lookup[index_b]
                    del list_b_lookup[index_b]

                index_b += 1
                if index_b > len(list_b):
                    break

            if b_is_substring:
                index_a += 1
                continue

            # Fallback: increment index of b until a match with a is found
            while index_b < len(list_b):

                tmp = index_a
                found = False
                while tmp < len(list_a):
                    if list_a[tmp - 1] == list_b[index_b - 1]:
                        found = True
                        break
                    tmp += 1

                if found:
                    index_a = tmp
                    break

                index_b += 1

        return list_a_lookup
