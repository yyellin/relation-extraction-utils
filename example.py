import matplotlib.pyplot as plot

from count_trigger_paths.path_stats import PathStats, PathDesignation

pathstats = PathStats(r'C:\Users\jyellin\Desktop\per_employee_of.csv')

for path_designation in PathDesignation:
    stats = pathstats.get_sorted_stats(path_designation)

    plot.figure()
    plot.title(path_designation.value)
    plot.xlabel('frequency')
    plot.ylabel('path')
    plot.barh([path for _, path in stats], [frequency for frequency, _ in stats])

plot.show()
