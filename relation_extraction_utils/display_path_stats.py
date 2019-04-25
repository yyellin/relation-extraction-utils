import argparse

import matplotlib.pyplot as plot

from relation_extraction_utils.internal.path_stats import PathStats, PathDesignation


def display_path_histograms(csv_file):
    pathstats = PathStats(csv_file)

    for path_designation in PathDesignation:
        stats = pathstats.get_sorted_stats(path_designation)

        plot.figure(figsize=(14, 12))
        plot.title(path_designation.value)
        plot.xlabel('frequency')
        plot.ylabel('path')
        plot.barh([path for _, path in stats], [frequency for frequency, _ in stats])

    plot.show()


def list_sentences_by_path(csv_file):
    pathstats = PathStats(csv_file)

    paths = pathstats.get_top_n_paths(PathDesignation.ENTITY1_TO_ENTITY2_VIA_TRIGGER, 100)

    for path in paths:
        print('{}:'.format(path))

        for count, sentence in enumerate(
                pathstats.get_path_sentences(PathDesignation.ENTITY1_TO_ENTITY2_VIA_TRIGGER, path), start=1):
            print(' {}:{}'.format(count, sentence))



if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="produce histograms representing "
                                                     "between trigger and entities")

    arg_parser.add_argument('csv_file_path',
                            metavar='csv-file-path',
                            help="the path of the csv input file")

    args = arg_parser.parse_args()
    # list_sentences_by_path(args.csv_file_path)
    display_path_histograms(args.csv_file_path)
