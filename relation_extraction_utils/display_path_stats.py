import argparse

import matplotlib.pyplot as plot

from relation_extraction_utils.path_stats import PathStats, PathDesignation


def display_path_stats(csv_file):
    pathstats = PathStats(csv_file)

    full_paths_stats = pathstats.get_sorted_stats(PathDesignation.ENTITY1_TO_ENTITY2_VIA_TRIGGER, reverse=True)

    for frequency, path in full_paths_stats:
        print('{:4d}: {}'.format(frequency, path))

    exit(0)

    for path_designation in PathDesignation:
        stats = pathstats.get_sorted_stats(path_designation)

        plot.figure(figsize=(12, 10))
        plot.title(path_designation.value)
        plot.xlabel('frequency')
        plot.ylabel('path')
        plot.barh([path for _, path in stats], [frequency for frequency, _ in stats])

    plot.show()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="produce histograms representing "
                                                     "between trigger and entities")

    arg_parser.add_argument('csv_file_path',
                            metavar='csv-file-path',
                            help="the path of the csv input file")

    args = arg_parser.parse_args()
    display_path_stats(args.csv_file_path)
