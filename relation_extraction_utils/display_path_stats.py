import argparse

import matplotlib.pyplot as plot

from relation_extraction_utils.internal.path_stats import PathDesignation, PathStats, PathStatsWithPss


def display_path_stats(csv_file):
    pathstats = PathStatsWithPss(csv_file)

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
