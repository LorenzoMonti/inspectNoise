import matplotlib.pyplot as plt
import pandas as pd
import sys
import datetime
import numpy as np
from utils import PLOT_DIR, create_plot_dir
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

def parse_file(file):
    """
        Parse log file passed as param.
    """
    db = []
    timestamps = []
    with open(file, "rt") as f:
        for line in f:
            date, time, val = line.split(" ")
            tmp_date = date + " " +time
            tmp_time = datetime.datetime.strptime(tmp_date, "%Y-%m-%d %H:%M:%S,%f")#.time()
            timestamps.append(tmp_time);
            db.append(float(val))

    return date, db, timestamps

def plot(date, db, timestamps, my_dpi, thr):
    """
        Plot data.
    """
    fig = plt.figure(figsize=(1920/my_dpi, 1080/my_dpi), dpi=my_dpi)
    ax = fig.subplots()
    ax.set_title("Variation of dB {} \nstarted at: {} \nended at: {}".format(date, datetime.datetime.strftime(timestamps[0], "%H:%M:%S"), datetime.datetime.strftime(timestamps[-1], "%H:%M:%S")))
    ax.set_xlabel("Seconds")
    ax.set_ylabel("dB")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    plot1, = plt.plot(timestamps, db)
    if thr > 0:
        thr = [thr] * len(timestamps)
        plot2, = plt.plot(timestamps, thr, lw=2, c="red") # print threshold line.
        ax.legend([plot1, plot2], ["db", "threshold"])
    plt.savefig(PLOT_DIR + "/" + str(datetime.date.today()) + '.png', bbox_inches='tight', dpi=my_dpi)

    plt.clf()

def plot_dist(data, date, db, timestamps, my_dpi, thr):
    """
        Plot distribution of dB.
    """
    fig = plt.figure(figsize=(1920/my_dpi, 1080/my_dpi), dpi=my_dpi)
    bins = np.linspace(30, 130, 100)
    ax = fig.subplots()
    ax.set_title("Distribution of dB {} \nstarted at: {} \nended at: {}".format(date, datetime.datetime.strftime(timestamps[0], "%H:%M:%S"), datetime.datetime.strftime(timestamps[-1], "%H:%M:%S")))
    ax.set_xlabel("dB")
    ax.set_ylabel("Frequency")
    if thr > 0:
         plt.axvline(thr, color='red', linewidth=2)
    plt.hist(db, bins, 50)
    plt.savefig(PLOT_DIR + "/dB_distribution_" + str(datetime.date.today()) + '.png', bbox_inches='tight', dpi=my_dpi)

    plt.clf()

# Call main program.
if __name__ == "__main__":
    """
        Main of program.
    """
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        raise Exception("Usage: python plotter.py inputfile my_dpi [threshold]")

    if len(sys.argv) == 4:
        nome_script, file, my_dpi, thr = sys.argv

    if len(sys.argv) == 3:
        nome_script, file, my_dpi = sys.argv
        thr = 0

    # Create plot dir if it doesn't exist.
    create_plot_dir()

    date, db, timestamps = parse_file(file)

    # Plot data.
    plot(date, db, timestamps, int(my_dpi), float(thr))

    # Pandas series from data.
    series = pd.Series(db)

    # Dist. graph.
    plot_dist(series, date, db, timestamps, int(my_dpi), float(thr))
