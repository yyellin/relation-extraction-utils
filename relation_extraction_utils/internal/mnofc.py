# mnofc stands for "manager new output file creation"

import sys


class ManageNewOutputFileCreation(object):
    """
    Most of the utilities in relation-extraction-utils package support the option of generating
    batched output files - this can be helpful for long running jobs, where the user will want
    partial output, without waiting for job completion.
    The 'ManageNewOutputFileCreation' class exposes a single method - 'get_new_file_if_necessary'
    that needs to be called before the emission of each new line.


    Attributes
    ----------
    Methods
    -------

    """

    def __init__(self, file_name, batch_size = None):

        """

        Parameters
        ----------
        """
        self.__file_name = file_name[:-len('.csv')] if file_name is not None and file_name.endswith('.csv') else file_name
        self.__current_file = None
        self.__batch_size = batch_size
        self.__batch = 0
        self.__count = 0



    def get_new_file_if_necessary(self):

        current_count = self.__count
        self.__count += 1

        # return 'sys.stdout' the first time 'get_new_file_if_necessary' is called if
        # no file-name was defined in object initialization
        if current_count == 0 and self.__file_name is None:
            return sys.stdout

        # if a file-name is supplied, but a batch-size isn't. then return a new file
        # based on the provided file-name the first time 'get_new_file_if_necessary' is
        # called
        if current_count == 0 and self.__file_name is not None and self.__batch_size is None:
            output_file_actual = '{0}.csv'.format(self.__file_name)

            return open(output_file_actual, 'w', encoding='utf-8', newline='')

        # if a batch-size is supplied with a file-name is supplied, but a batch-size
        # we need to check if we've just completed a batch (or are just beginning to produce
        # output) and return an appropriately opened and named file
        if self.__file_name is not None and self.__batch_size is not None and current_count % self.__batch_size == 0:

            if self.__current_file is not None:
                self.__current_file.close()

            output_file_actual = '{0}-{1}.csv'.format(self.__file_name, self.__batch)

            self.__batch += 1

            self.__current_file = open(output_file_actual, 'w', encoding='utf-8', newline='')
            return self.__current_file

        # None indicates to the calling code that the previously returned file should be used
        return None