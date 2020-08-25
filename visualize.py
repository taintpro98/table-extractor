"""
visualize results
"""
import matplotlib.pyplot as plt
import numpy as np
import os

from pandas import DataFrame

def visualize_bar_chart(mode, output_dir):
    filename = os.path.basename(output_dir) + "_bar_chart.png"

    max_mode = max([mode[key] for key in mode.keys()])
    step = max_mode//10 + 1
    max_ytick = step * 11
    yticks_array = np.arange(0, max_ytick, step)

    plt.style.use('ggplot')
    x = [str(i) for i in np.arange(11)/10]
    y = [mode.get(i, 0) for i in x]
    x_pos = [i for i, _ in enumerate(x)]

    plt.bar(x_pos, y, color='green')
    plt.xlabel("TEDS score")
    plt.ylabel("Frequency")
    plt.title("")
    plt.xticks(x_pos, x)
    plt.yticks(yticks_array)
    plt.savefig(os.path.join(output_dir, filename))

def dump_report_excel(summary, output_dir):
    filename = os.path.basename(output_dir) + "_teds_scores.xlsx"
    filepath = os.path.join(output_dir, filename)
    df = DataFrame(summary)
    df.to_excel(filepath, index=False)