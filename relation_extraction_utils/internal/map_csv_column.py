class MapCsvColumns(object):
    """

    Attributes
    ----------
    Methods
    -------

    """

    def __init__(self, first_row):
        """

        Parameters
        ----------
        """
        self.__field_lookup = {}

        for i in range(len(first_row)):
            self.__field_lookup[first_row[i]] = i

    def get_field_value(self, row, field):
        """

        Parameters
        ----------
        """
        return row[self.__field_lookup[field]]
