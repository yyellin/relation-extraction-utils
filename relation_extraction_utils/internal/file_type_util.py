from chardet.universaldetector import UniversalDetector


class FileTypeUtil(object):
    """
    'FileTypeUtil' is designed to ...

    Attributes
    ----------

    Methods
    -------

    """

    @staticmethod
    def determine_encoding(file_path):
        """
        based on https://stackoverflow.com/questions/46037058/using-chardet-to-find-encoding-of-very-large-file

        Parameters
        ----------
        """
        # encoding = 'ascii'
        encoding = 'utf-8'
        detector = UniversalDetector()
        detector.reset()
        with open(file_path, 'rb') as f:

            for count, row in enumerate(f, start=1):
                detector.feed(row)
                if detector.done:
                    encoding = detector.result['encoding']
                    break

                if count == 3:
                    break

        detector.close()

        return encoding
