import numpy as NP
from matplotlib import pyplot as PLT
import matplotlib.patches as mpatches

# Import and use this to use python's native graphing capabilities
def draw_matplot_graph(unit_supplies, replay):
    units = sorted(list(unit_supplies.keys()))
    y = NP.row_stack([ unit_supplies[i] for i in units ])
    # this call to 'cumsum' (cumulative sum), passing in your y data, 
    # is necessary to avoid having to manually order the datasets
    x = times
    y_stack = NP.cumsum(y, axis=0)   # a 3x10 array

    fig = PLT.figure()
    ax1 = fig.add_subplot(111)

    patches = []

    ax1.fill_between(x, 0, y_stack[0,:], facecolor="#CC6666", alpha=.7)
    patches.append(mpatches.Patch(color="#CC6666", label=units[0], alpha=.7))

    for index, key in enumerate(units[1:]):
        color = "#" +  hashlib.sha224(bytes(key, 'utf-8')).hexdigest()[:6]

        patches.append(mpatches.Patch(color=color, label=key, alpha=.7))
        ax1.fill_between(x, y_stack[index,:], y_stack[index+1,:], facecolor=color, alpha=.7)

    PLT.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
               ncol=2, mode="expand", borderaxespad=0., handles=patches)
    PLT.show()

