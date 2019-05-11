from collections import OrderedDict


class CsvColumnMapper(object):
    """

    Attributes
    ----------
    Methods
    -------

    """

    def __init__(self, source_first_row, target_columns, source_required=None, filter_source_from_result=None):
        """

        Parameters
        ----------
        """
        self.__source_field_lookup = {}

        for i, value in enumerate(source_first_row):
            self.__source_field_lookup[value] = i

        if source_required is not None:
            for field in source_required:
                if field not in self.__source_field_lookup:
                    raise ValueError('missing \'{0}\' column in input'.format(field))

        self.__target_columns = target_columns
        self.__mapping_instructions = []

        target_column_lookup = OrderedDict({target_columns[i]: i for i in range(len(target_columns))})

        for source_index, source_field in enumerate(source_first_row):

            if source_field in target_column_lookup.keys():
                self.__mapping_instructions.append(('T', target_column_lookup[source_field], source_field))
                del target_column_lookup[source_field]
            elif filter_source_from_result is not None or source_field not in filter_source_from_result:
                self.__mapping_instructions.append(('S', source_index, source_field))

        for target_field, target_index in target_column_lookup.items():
            self.__mapping_instructions.append(('T', target_index, target_field))

    def get_field_value_from_source(self, source_row, field, evaluate=False):
        """

        Parameters
        ----------
        """
        value = source_row[self.__source_field_lookup[field]]

        if evaluate:
            if value != '':
                return eval(value)
            else:
                return None

        else:
            return value

    def get_new_headers(self):
        return [instruction[2] for instruction in self.__mapping_instructions]

    def get_new_row_values(self, row_source, new_values):
        """

        Parameters
        ----------
        """

        values = []
        for source_or_target, index, _ in self.__mapping_instructions:
            if source_or_target == 'S':
                values.append(row_source[index])
            else:
                values.append(new_values[index])

        return values
